package gelinea;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import org.broadinstitute.cbts.gelinea.GeLiNEA;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.annotation.JsonInclude.Include;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;

import apimodels.Attribute;
import apimodels.Connection;
import apimodels.Element;
import apimodels.Names;
import apimodels.Property;
import apimodels.TransformerInfo;
import apimodels.TransformerQuery;

public class GeLiNEATransformer {

	private static final String GELINEA_P_VALUE = "GeLiNEA p-value";

	final static Logger log = LoggerFactory.getLogger("gelinea");

	private static ObjectMapper mapper = new ObjectMapper();

	static {
		mapper.setSerializationInclusion(Include.NON_NULL);
		mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
	}

	private TransformerInfo info = null;
	private Config config = null;


	public GeLiNEATransformer() {
		super();
		try {
			String json = new String(Files.readAllBytes(Paths.get("conf/transformer_info.json")));
			this.info = mapper.readValue(json, TransformerInfo.class);
			Controls.PVALUE_THRESHOLD = info.getParameters().get(0).getName();
			Controls.DEFAULT_PVALUE_THRESHOLD = Double.valueOf(info.getParameters().get(0).getDefault());
			Controls.NETWORK = info.getParameters().get(1).getName();
			Controls.DEFAULT_NETWORK = info.getParameters().get(1).getDefault();
			Controls.GENE_SETS = info.getParameters().get(2).getName();
			Controls.DEFAULT_GENE_SET = info.getParameters().get(2).getDefault();
			String configJson = new String(Files.readAllBytes(Paths.get("conf/config.json")));
			this.config = mapper.readValue(configJson, Config.class);
		}
		catch (IOException e) {
			log.error("unable to load transformer info", e);
		}
	}


	public TransformerInfo getInfo() {
		return info;
	}


	public List<Element> transform(TransformerQuery query) throws Exception {
		final List<Element> collection = query.getCollection();
		if (collection == null || collection.size() == 0) {
			return new ArrayList<Element>();
		}
		File inputFile = null;
		File outputFile = File.createTempFile("gelinea_out", ".txt");
		try {
			log.info("GeLiNEA: gene list size:" + collection.size());
			final List<Element> pathways = new ArrayList<Element>();
			final Controls controls = new Controls(query.getControls());
			final Network network = config.networks.get(controls.network);
			inputFile = mapGeneList(network, collection);
			int geneSetSize = 0;
			for (String geneSet : controls.genesets) {
				geneSetSize = geneSetSize + config.geneSetSizes.getOrDefault(geneSet, 0);
			}
			for (String geneSet : controls.genesets) {
				final String geneSetsFile = config.getGeneSetFile(geneSet, info);
				gelinea(network, geneSetsFile, inputFile, outputFile);
				final String sourceElementId = collection.get(0).getId();
				pathways.addAll(readOutput(outputFile, Double.valueOf(controls.minimum_p_value), geneSetSize, sourceElementId));
			}
			pathways.sort(pathwayComparator);
			log.info("GeLiNEA: enriched pathways:" + pathways.size());
			return pathways;
		}
		finally {
			if (inputFile != null && inputFile.exists()) {
				inputFile.delete();
			}
			if (outputFile != null && outputFile.exists()) {
				outputFile.delete();
			}
		}
	}

	private static Comparator<Element> pathwayComparator = new Comparator<Element>() {

		@Override
		public int compare(Element element1, Element element2) {
			Double pValue1 = pValue(element1);
			Double pValue2 = pValue(element2);
			return Double.compare(pValue1, pValue2);
		}

	};


	private static double pValue(Element element) {
		Double minPvalue = 1.0;
		for (Attribute attr : element.getConnections().get(0).getAttributes()) {
			if (GELINEA_P_VALUE.equals(attr.getOriginalAttributeName())) {
				final double pValue = Double.valueOf(attr.getValue().toString());
				if (pValue < minPvalue) {
					minPvalue = pValue;
				}
			}
		}
		return minPvalue;
	}


	private File mapGeneList(final Network network, final List<Element> genes) throws Exception {
		Map<String,String> geneMap = readGeneIdMap(network);
		File inputFile = File.createTempFile("gelinea_in", ".txt");
		PrintWriter input = new PrintWriter(new FileWriter(inputFile));
		input.println("protein_id");
		for (Element gene : genes) {
			if (gene.getIdentifiers() != null && gene.getIdentifiers().containsKey("entrez") && gene.getIdentifiers().get("entrez") instanceof String) {
				String geneId = gene.getIdentifiers().get("entrez").toString();
				if (geneId.toUpperCase().startsWith("NCBIGENE:")) {
					geneId = geneId.substring(9);
				}
				if (geneMap.containsKey(geneId)) {
					String nodeId = geneMap.get(geneId);
					input.println(nodeId);
				}
			}
		}
		input.close();
		return inputFile;
	}


	private static Map<String,String> readGeneIdMap(Network network) throws IOException {
		Map<String,String> map = new HashMap<>();
		BufferedReader input = new BufferedReader(new FileReader(network.mappingFile));
		String header = input.readLine();
		if (!"protein_id\tGeneID".equals(header)) {
			log.warn("Wrong format '" + network.mappingFile + "'");
		}
		for (String line = input.readLine(); line != null; line = input.readLine()) {
			String[] row = line.split("\t");
			if (row.length == 2) {
				map.put(row[1], row[0]);
			}
		}
		input.close();
		return map;
	}


	private void gelinea(Network network, String geneSetsFile, File input, File output) {
		GeLiNEA.apply(network.filename, geneSetsFile, input.getAbsolutePath(), output.getAbsolutePath(), true, 50);
	}


	private List<Element> readOutput(final File outputFile, final double threshold, final int geneSetSize, final String sourceElementId) throws IOException {
		ArrayList<Element> pathways = new ArrayList<Element>();
		BufferedReader output = new BufferedReader(new FileReader(outputFile));
		String header = output.readLine();
		if (!"geneSet\toverlap\tnConnections\tpValue".equals(header)) {
			log.warn("Wrong GeLiNEA output file format");
		}
		for (String line = output.readLine(); line != null; line = output.readLine()) {
			String[] row = line.split("\t");
			if (row.length == 4) {
				String name = row[0];
				String geneSet = "MSigDB:" + name;
				String url = String.format(config.urlPrefix, row[0]);
				String overlap = row[1];
				String nConnections = row[2];
				final double pValue = Double.parseDouble(row[3]);
				final double adjPValue = Math.min(geneSetSize * pValue, 1.0);
				if (pValue < threshold) {

					Element element = new Element();
					element.setId(geneSet);
					element.setBiolinkClass("Pathway");
					element.putIdentifiersItem("msigdb", geneSet);
					element.setSource(this.info.getLabel());
					element.providedBy(this.info.getName());
					element.addAttributesItem(attribute("url", "url", url, url));
					pathways.add(element);

					Connection connection = new Connection();
					connection.addAttributesItem(attribute("gene-list overlap", "GELINEA:gene_list_overlap", overlap));
					connection.addAttributesItem(attribute("gene-list connections", "GELINEA:gene_list_connections", nConnections));
					connection.addAttributesItem(attribute(GELINEA_P_VALUE, "biolink:p_value", String.valueOf(pValue)));
					connection.addAttributesItem(attribute("GeLiNEA adjusted p-value ", "biolink:adjusted_p_value", String.valueOf(adjPValue)));
					connection.providedBy(this.info.getName());
					connection.source(this.info.getLabel());
					connection.sourceElementId(sourceElementId);
					connection.biolinkPredicate(this.info.getKnowledgeMap().getEdges().get(0).getPredicate());
					connection.inversePredicate(this.info.getKnowledgeMap().getEdges().get(0).getInversePredicate());
					element.addConnectionsItem(connection);

					Names names = new Names();
					names.setName(name);
					names.source(this.info.getLabel());
					element.addNamesSynonymsItem(names);
				}
			}
		}
		output.close();
		return pathways;
	}


	private Attribute attribute(String name, String type, String value) {
		return attribute(name, type, value, null);
	}


	private Attribute attribute(String name, String type, String value, String url) {
		final Attribute attribute = new Attribute();
		attribute.setOriginalAttributeName(name);
		attribute.setAttributeTypeId(type);
		attribute.setValue(value);
		attribute.setValueUrl(url);
		attribute.setAttributeSource(this.info.getLabel());
		attribute.setProvidedBy(this.info.getName());
		return attribute;
	}


	static class Config {

		private Map<String,String> geneSetFiles;
		private Map<String,Integer> geneSetSizes = new HashMap<>();
		private String urlPrefix;
		private HashMap<String,Network> networks;


		public void setGeneSetFiles(Map<String,String> geneSetFiles) {
			this.geneSetFiles = geneSetFiles;

			for (String geneSet : geneSetFiles.keySet()) {
				try {
					final BufferedReader geneSetFile = new BufferedReader(new FileReader(geneSetFiles.get(geneSet)));
					int count = 0;
					for (String line = geneSetFile.readLine(); line != null; line = geneSetFile.readLine()) {
						count = count + 1;
					}
					geneSetSizes.put(geneSet, count);
					geneSetFile.close();
					log.info("Loaded " + count + " gene sets from " + geneSet);
				}
				catch (IOException e) {
					e.printStackTrace();
				}
			}

		}


		public String getGeneSetFile(String collectionName, TransformerInfo info) {
			if (geneSetFiles.containsKey(collectionName))
				return geneSetFiles.get(collectionName);
			else
				return geneSetFiles.get(info.getParameters().get(2).getDefault());
		}


		public void setUrlPrefix(String urlPrefix) {
			this.urlPrefix = urlPrefix;
		}


		public void setNetworks(List<Network> networks) {
			this.networks = new HashMap<String,Network>();
			for (Network network : networks) {
				this.networks.put(network.network, network);
			}
		}
	}


	static class Network {
		private String network;
		private String filename;
		private String mappingFile;


		public void setNetwork(String network) {
			this.network = network;
		}


		public void setFilename(String filename) {
			this.filename = filename;
		}


		public void setMappingFile(String mappingFile) {
			this.mappingFile = mappingFile;
		}


		@Override
		public String toString() {
			return "Network['" + network + "':'" + filename + "':'" + mappingFile + "']";
		}
	}


	private static class Controls {

		private static String PVALUE_THRESHOLD = "maximum p-value";
		private static String NETWORK = "network";
		private static String GENE_SETS = "gene-set collection";

		private static double DEFAULT_PVALUE_THRESHOLD = 1e-05;
		private static String DEFAULT_NETWORK = "STRING-human-700";
		private static String DEFAULT_GENE_SET = "H - hallmark gene sets";

		private double minimum_p_value = DEFAULT_PVALUE_THRESHOLD;
		private String network = DEFAULT_NETWORK;
		private List<String> genesets = new LinkedList<>();


		Controls(List<Property> controls) {
			for (Property property : controls) {
				if (PVALUE_THRESHOLD.equals(property.getName())) {
					minimum_p_value = Double.valueOf(property.getValue());
				}
				if (NETWORK.equals(property.getName())) {
					network = property.getValue();
				}
				if (GENE_SETS.equals(property.getName())) {
					genesets.add(property.getValue());
				}
			}
			if (genesets.isEmpty()) {
				genesets.add(DEFAULT_GENE_SET);
			}
		}
	}
}
