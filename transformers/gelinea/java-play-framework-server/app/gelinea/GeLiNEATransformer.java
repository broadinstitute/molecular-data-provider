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
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.broadinstitute.cbts.gelinea.GeLiNEA;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.annotation.JsonInclude.Include;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;

import apimodels.Attribute;
import apimodels.Element;
import apimodels.GeneInfo;
import apimodels.Property;
import apimodels.TransformerInfo;
import apimodels.TransformerQuery;

public class GeLiNEATransformer {

	final static Logger log = LoggerFactory.getLogger(GeLiNEATransformer.class);

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
			String configJson = new String(Files.readAllBytes(Paths.get("conf/config.json")));
			this.config = mapper.readValue(configJson, Config.class);
		} catch (IOException e) {
			log.error("unable to load transformer info", e);
		}
	}


	public TransformerInfo getInfo() {
		return info;
	}


	public List<Element> transform(TransformerQuery query) throws Exception {
		if (query.getGenes() == null) {
			return new ArrayList<Element>();
		}
		File inputFile = null;
		File outputFile = File.createTempFile("gelinea_out", ".txt");
		try {
			Map<String,String> controls = controlMap(query.getControls());
			Network network = config.networks.get(controls.get("network"));
			inputFile = mapGeneList(network, query.getGenes());
			final String geneSetsFile = config.getGeneSetFile(controls.get("gene-set collection"), info);
			gelinea(network, geneSetsFile, inputFile, outputFile);
			return readOutput(outputFile, Double.valueOf(controls.get("maximum p-value")));
		} finally {
			if (inputFile != null && inputFile.exists()) {
				inputFile.delete();
			}
			if (outputFile != null && outputFile.exists()) {
				outputFile.delete();
			}
		}
	}


	private File mapGeneList(Network network, List<GeneInfo> genes) throws Exception {
		Map<String,String> geneMap = readGeneIdMap(network);
		File inputFile = File.createTempFile("gelinea_in", ".txt");
		PrintWriter input = new PrintWriter(new FileWriter(inputFile));
		input.println("protein_id");
		for (GeneInfo gene : genes) {
			if (gene.getIdentifiers() != null && gene.getIdentifiers().getEntrez() != null) {
				String geneId = gene.getIdentifiers().getEntrez();
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


	private static Map<String,String> controlMap(List<Property> controls) {
		Map<String,String> map = new HashMap<String,String>();
		for (Property property : controls) {
			map.put(property.getName(), property.getValue());
		}
		return map;
	}


	private void gelinea(Network network, String geneSetsFile, File input, File output) {
		GeLiNEA.apply(network.filename, geneSetsFile, input.getAbsolutePath(), output.getAbsolutePath(), true, 50);
	}


	private List<Element> readOutput(File outputFile, double threshold) throws IOException {
		ArrayList<Element> pathways = new ArrayList<Element>();
		BufferedReader output = new BufferedReader(new FileReader(outputFile));
		String header = output.readLine();
		if (!"geneSet\toverlap\tnConnections\tpValue".equals(header)) {
			log.warn("Wrong GeLiNEA output file format");
		}
		for (String line = output.readLine(); line != null; line = output.readLine()) {
			String[] row = line.split("\t");
			if (row.length == 4) {
				String geneSet = "MSigDB:" + row[0];
				String url = String.format(config.urlPrefix, row[0]);
				String overlap = row[1];
				String nConnections = row[2];
				double pValue = Double.parseDouble(row[3]);
				if (pValue < threshold) {
					Element element = new Element();
					element.setId(geneSet);
					element.setBiolinkClass("pathway");
					element.putIdentifiersItem("MSigDB", geneSet);
					element.addAttributesItem(new Attribute().name("gene-list overlap").value(overlap).source(this.info.getName()).url(url));
					element.addAttributesItem(new Attribute().name("gene-list connections").value(nConnections).source(this.info.getName()).url(url));
					element.addAttributesItem(new Attribute().name("GeLiNEA p-value").value(String.valueOf(pValue)).source(this.info.getName()).url(url));
					element.setSource(this.info.getName());
					pathways.add(element);
				}
			}
		}
		output.close();
		return pathways;
	}


	static class Config {

		private Map<String,String> geneSetFiles;
		private String urlPrefix;
		private HashMap<String,Network> networks;


		public void setGeneSetFiles(Map<String,String> geneSetFiles) {
			this.geneSetFiles = geneSetFiles;
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
}
