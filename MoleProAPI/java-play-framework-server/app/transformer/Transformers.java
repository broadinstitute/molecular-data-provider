package transformer;

import java.util.List;
import java.util.Map;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;

import apimodels.TransformerInfo;
import transformer.collection.Collections;
import transformer.InternalTransformer.InternalTransformerInfo;
import transformer.classes.MyChem;
import transformer.classes.MyGene;
import transformer.classes.PubChem;
import transformer.exception.NotFoundException;
import transformer.mapping.MappedAttribute;
import transformer.mapping.MappedBiolinkClass;
import transformer.mapping.MappedConnection;
import transformer.util.HTTP;
import transformer.util.JSON;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Transformers {

	private static final TransformerInfo.StatusEnum ONLINE = TransformerInfo.StatusEnum.ONLINE;
	private static final TransformerInfo.StatusEnum OFFLINE = TransformerInfo.StatusEnum.OFFLINE;

	/**
	 * Logger
	 */
	final static Logger log = LoggerFactory.getLogger(Transformers.class);

	/**
	 * Maps transformer's URL to TransformerInfo object
	 */
	private static Map<String,Transformer> transformers;

	/**
	 * Maps transformer's name to transformer's URL
	 */
	private static Map<String,String> urls = new HashMap<>();

	private static Map<String,Transformer> internalTransformers = loadInternalTransformers();


	private static Map<String,Transformer> loadInternalTransformers() {
		final Map<String,Transformer> map = new HashMap<>();
		try {
			final String json = new String(Files.readAllBytes(Paths.get("conf/transformerInfo.json")));
			final InternalTransformerInfo[] transformers = JSON.mapper.readValue(json, InternalTransformerInfo[].class);
			for (InternalTransformerInfo info : transformers) {
				Transformer transformer = InternalTransformer.createFrom(info);
				map.put(transformer.info.getName(), transformer);
			}
		} catch (IOException e) {
			log.error("Unable to load internal transformers", e);
		}
		log.debug("Loaded " + map.size() + " internal transformers");
		return map;
	}


	/**
	 * Implement /transformers API endpoint
	 * 
	 * @return List of known transformers
	 */
	public static List<TransformerInfo> getTransformers() {
		final ArrayList<Transformer> transformers = new ArrayList<Transformer>();
		try {
			final BufferedReader transformerFile = new BufferedReader(new FileReader("conf/transformers.txt"));
			for (String baseURL = transformerFile.readLine(); baseURL != null; baseURL = transformerFile.readLine()) {
				if (baseURL.startsWith("=")) {
					String internalName = baseURL.substring(1);
					transformers.add(internalTransformers.get(internalName));
				}
				else if (baseURL.trim().length() > 0 && !baseURL.trim().startsWith("#")) {
					final TransformerInfo info = getTransformeInfo(baseURL);
					if (info != null) {
						transformers.add(RemoteTransformer.createFrom(info));
					}
				}
			}
			transformerFile.close();
		} catch (IOException e) {
			log.error("Unable to load external transformers", e);
		}
		updateTransformerMap(transformers);
		log.debug("Obtained " + transformers.size() + " transformers");
		MappedAttribute.loadMapping();
		MappedConnection.loadMapping();
		MappedBiolinkClass.loadMapping();
		for (Transformer transformer : transformers) {
			MappedBiolinkClass.map(transformer.info.getKnowledgeMap().getEdges());
			MappedConnection.mapPredicates(transformer.info.getLabel(), transformer.info.getKnowledgeMap().getEdges());
		}
		return getInfo(transformers);
	}


	/**
	 * Load transformer info for a given base URL, return cached info for offline
	 * transformers
	 * 
	 * @param baseURL
	 * @return transformer info
	 */
	private static TransformerInfo getTransformeInfo(final String baseURL) {
		TransformerInfo info = null;
		try {
			final URL url = new URL(baseURL + "/transformer_info");
			info = JSON.mapper.readValue(HTTP.get(url), TransformerInfo.class);
			if (info.getUrl() == null) {
				info.setUrl(baseURL);
			}
			info.setStatus(ONLINE);
		} catch (Exception e) {
			log.warn("Transformer offline: " + baseURL);
			// transformer offline - use cached info
		}
		if (info == null && transformers != null && transformers.containsKey(baseURL)) {
			info = transformers.get(baseURL).info;
			if (info != null) {
				info.setStatus(OFFLINE);
			}
		}
		return info;
	}


	private synchronized static void updateTransformerMap(final ArrayList<Transformer> transformers) {
		final Map<String,Transformer> transformerMap = new HashMap<String,Transformer>();
		final Map<String,String> urlMap = new HashMap<String,String>();
		for (Transformer transformer : transformers) {
			String url = transformer.info.getUrl();
			if (url == null || url.length() == 0) {
				url = transformer.info.getName();
			}
			transformerMap.put(url, transformer);
			urlMap.put(transformer.info.getName(), url);
		}
		Transformers.transformers = transformerMap;
		Transformers.urls = urlMap;
	}


	private static List<TransformerInfo> getInfo(final ArrayList<Transformer> transformers) {
		final ArrayList<TransformerInfo> transformerInfo = new ArrayList<TransformerInfo>();
		for (Transformer transformer : transformers) {
			transformerInfo.add(transformer.info);
		}
		return transformerInfo;
	}


	public synchronized static Transformer getTransformer(final String transformerName) throws NotFoundException {
		log.trace("Transformers.getTransformer(\"" + transformerName + "\")");
		if (urls.containsKey(transformerName)) {
			final String baseURL = urls.get(transformerName);
			return transformers.get(baseURL);
		}
		else {
			log.debug("Transformer '" + transformerName + "' not found");
			throw new NotFoundException("Transformer '" + transformerName + "' not found");
		}
	}
	
	public static void status() {
		StringBuilder status = new StringBuilder();
		status.append("transformers:"+transformers.size()+", ");
		status.append("collections:"+Collections.size()+", ");
		status.append("genes:"+MyGene.size()+", ");
		status.append("compounds:"+MyChem.size()+", ");
		status.append("pubchem:"+PubChem.size()+", ");
		status.append("free memory:"+Runtime.getRuntime().freeMemory()/1000000);
		status.append("/"+Runtime.getRuntime().totalMemory()/1000000);
		System.out.println(status.toString());
	}
}
