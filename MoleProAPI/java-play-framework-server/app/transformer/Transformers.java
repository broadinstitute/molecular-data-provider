package transformer;

import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;

import apimodels.ChainQuery;
import apimodels.Parameter;
import apimodels.TransformerInfo;
import apimodels.TransformerInfoProperties;
import transformer.collection.Collections;
import transformer.InternalTransformer.InternalTransformerInfo;
import transformer.exception.NotFoundException;
import transformer.mapping.MappedAttribute;
import transformer.mapping.MappedBiolinkClass;
import transformer.mapping.MappedConnection;
import transformer.mapping.MappedInfoRes;
import transformer.mapping.MappedName;
import transformer.util.HTTP;
import transformer.util.JSON;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Transformers {

	private static final TransformerInfo.StatusEnum ONLINE = TransformerInfo.StatusEnum.ONLINE;
	private static final TransformerInfo.StatusEnum OFFLINE = TransformerInfo.StatusEnum.OFFLINE;

	private static final String PATTERN = "[(]\\d{4}[-]\\d\\d[-]\\d\\d[)]$";
	private static final Pattern DATE_PATTERN = Pattern.compile(PATTERN);

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

	static {
		getTransformers();
	}


	private static Map<String,Transformer> loadInternalTransformers() {
		final Map<String,Transformer> map = new HashMap<>();
		try {
			final String json = new String(Files.readAllBytes(Paths.get("conf/transformerInfo.json")));
			final InternalTransformerInfo[] transformers = JSON.mapper.readValue(json, InternalTransformerInfo[].class);
			for (InternalTransformerInfo info : transformers) {
				Transformer transformer = InternalTransformer.createFrom(info);
				map.put(transformer.info.getName(), transformer);
			}
		}
		catch (IOException e) {
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
			final String transformerfFileName = Config.config.transformersFileName();
			final BufferedReader transformerFile = new BufferedReader(new FileReader(transformerfFileName));
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
		}
		catch (IOException e) {
			log.error("Unable to load external transformers", e);
		}
		updateTransformerMap(transformers);
		log.debug("Obtained " + transformers.size() + " transformers");
		MappedAttribute.loadMapping();
		MappedConnection.loadMapping();
		MappedBiolinkClass.loadMapping();
		MappedName.loadMapping();
		MappedInfoRes.loadMapping();
		for (Transformer transformer : transformers) {
			final TransformerInfo info = transformer.info;
			MappedBiolinkClass.map(info.getKnowledgeMap().getEdges());
			MappedConnection.mapPredicates(info.getLabel(), info.getKnowledgeMap().getEdges());
			if (info.getInfores() == null) {
				info.setInfores(MappedInfoRes.map(info.getLabel()));
			}
		}
		MappedAttribute.loadKnowledgeTypeMapping();
		return getInfo(transformers);
	}


	/**
	 * 
	 */
	public static ChainTransformer getChainTransformer(List<ChainQuery> chainQuery) {
		return new ChainTransformer(chainQuery);
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
			final int timeout = Config.config.getTimeouts().getTransformerInfoTimeout();
			info = JSON.mapper.readValue(HTTP.get(url, timeout), TransformerInfo.class);
			if (info.getUrl() == null) {
				info.setUrl(baseURL);
			}
			info.setStatus(ONLINE);
			for (Parameter parameter : info.getParameters()) {
				if (parameter.getRequired() == null) {
					parameter.setRequired(true);
				}
				if (parameter.getMultivalued() == null) {
					parameter.setMultivalued(false);
				}
			}
			final TransformerInfoProperties properties = info.getProperties();
			if (properties.getSourceDate() == null && properties.getSourceVersion() != null) {
				Matcher matcher = DATE_PATTERN.matcher(properties.getSourceVersion());
				if (matcher.find()) {
					properties.setSourceDate(matcher.group().substring(1, 11));
					properties.setSourceVersion(properties.getSourceVersion().split(PATTERN)[0].trim());
				}
			}
		}
		catch (Exception e) {
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


	private static List<TransformerInfo> getInfo(final java.util.Collection<Transformer> transformers) {
		final ArrayList<TransformerInfo> transformerInfo = new ArrayList<TransformerInfo>();
		for (Transformer transformer : transformers) {
			transformerInfo.add(transformer.info);
		}
		return transformerInfo;
	}


	public static java.util.Collection<TransformerInfo> getInfo() {
		return getInfo(transformers.values());
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
		status.append("transformers:" + transformers.size() + ", ");
		status.append("collections:" + Collections.size() + ", ");
		status.append("elements:" + MoleProDB.size() + ", ");
		status.append("free memory:" + Runtime.getRuntime().freeMemory() / 1000000);
		status.append("/" + Runtime.getRuntime().totalMemory() / 1000000);
		System.out.println(status.toString());
	}
}
