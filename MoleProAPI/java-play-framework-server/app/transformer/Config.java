package transformer;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.annotation.JsonProperty;

import transformer.exception.InternalServerError;
import transformer.util.JSON;

public class Config {

	final static Logger log = LoggerFactory.getLogger(Config.class);

	public static final Config config = loadConfig();


	private static Config loadConfig() {
		try {
			String json = new String(Files.readAllBytes(Paths.get("conf/transformerConfig.json")));
			Config config = JSON.mapper.readValue(json, Config.class);
			log.info("Loaded config from conf/transformerConfig.json");
			config.transformersFileName = "conf/transformers.txt";
			if (System.getenv().containsKey("MOLEPRO_TRANSFORMERS")) {
				config.transformersFileName = System.getenv().get("MOLEPRO_TRANSFORMERS");
			}
			return config;
		}
		catch (IOException e) {
			log.error("Unable to load configuration file", e);
			throw new InternalServerError("Unable to load configuration file");
		}
	}


	public String transformersFileName() {
		return transformersFileName;
	}


	public static Config getConfig() {
		return config;
	}

	private URL url;
	private CURIES curies;
	private Map<String,String> curiePrefixMap;
	private Timeouts timeouts;
	private ExpirationTimes expirationTimes;
	private String[] compoundSearchProducers;
	private Map<String,Integer> compoundNamePriority;
	private Map<String,String> biolinkAttributes;
	private String[] identifierPriority;
	private String transformersFileName;


	public URL url() {
		return url;
	}


	public void setUrl(URL url) {
		this.url = url;
	}


	public CURIES getCuries() {
		return curies;
	}


	public void setCuries(Map<String,CURIE> curies) {
		this.curies = new CURIES(curies);
	}


	public String mapCuriePrefix(String curie) {
		for (String prefix : curiePrefixMap.keySet()) {
			if (curie.toUpperCase().startsWith(prefix.toUpperCase())) {
				return curiePrefixMap.get(prefix) + curie.substring(prefix.length());
			}
		}
		return curie;
	}


	@JsonProperty("curie prefix map")
	public void setCuriePrefixMap(Map<String,String> curiePrefixMap) {
		this.curiePrefixMap = curiePrefixMap;
	}


	public Timeouts getTimeouts() {
		return timeouts;
	}


	@JsonProperty("timeouts")
	public void setTimeouts(Timeouts timeouts) {
		this.timeouts = timeouts;
	}


	public ExpirationTimes getExpirationTimes() {
		return expirationTimes;
	}


	@JsonProperty("expirationTimes")
	public void setExpirationTimes(ExpirationTimes expirationTimes) {
		this.expirationTimes = expirationTimes;
	}


	public String[] getCompoundSearchProducers() {
		return compoundSearchProducers;
	}


	@JsonProperty("compound-search producers")
	public void setCompoundSearchProducers(String[] compoundSearchProducers) {
		this.compoundSearchProducers = compoundSearchProducers;
	}


	public int getCompoundNamePriority(String nameSource) {
		if (compoundNamePriority.containsKey(nameSource)) {
			return compoundNamePriority.get(nameSource);
		}
		String[] secondarySource = nameSource.split("@");
		if (secondarySource.length == 2) {
			if (compoundNamePriority.containsKey("*" + secondarySource[1])) {
				return compoundNamePriority.get("*" + secondarySource[1]);
			}
			if (compoundNamePriority.containsKey(secondarySource[0] + "*")) {
				return compoundNamePriority.get(secondarySource[0] + "*");
			}
		}
		return compoundNamePriority.size();
	}


	@JsonProperty("compound-name priority")
	public void setCompoundNamePriorityOrder(String[] compoundNamePriority) {
		this.compoundNamePriority = new HashMap<>();
		for (int i = 0; i < compoundNamePriority.length; i++) {
			this.compoundNamePriority.put(compoundNamePriority[i], i);
		}
	}


	public String biolinkAttribute(final String attributeName) {
		return biolinkAttributes.get(attributeName);
	}


	@JsonProperty("biolink attributes")
	public void setSourceProvenanceSlots(Map<String,String> biolinkAttributes) {
		this.biolinkAttributes = biolinkAttributes;
	}


	public String[] getIdentifierPriority() {
		return identifierPriority;
	}


	@JsonProperty("identifier priority")
	public void setIdentifierPriority(String[] identifierPriority) {
		this.identifierPriority = identifierPriority;
	}


	public static final class URL {

		private String baseURL;
		private MyGeneInfo myGeneInfo;
		private MyChemInfo myChemInfo;
		private PubChem pubchem;
		private String automatHierarchyURL;


		public String getBaseURL() {
			return baseURL;
		}


		@JsonProperty("base")
		public void setBaseURL(String baseURL) {
			this.baseURL = baseURL;
			if (baseURL.contains("localhost") && System.getenv().containsKey("MOLEPRO_HOST")) {
				this.baseURL = System.getenv().get("MOLEPRO_HOST");
			}
			else if (baseURL.contains("localhost") && System.getenv().containsKey("HOST")) {
				this.baseURL = System.getenv().get("HOST");
			}
		}


		public MyGeneInfo MyGeneInfo() {
			return myGeneInfo;
		}


		@JsonProperty("myGene.info")
		public void setMyGeneInfo(MyGeneInfo myGeneInfo) {
			this.myGeneInfo = myGeneInfo;
		}


		public MyChemInfo MyChemInfo() {
			return myChemInfo;
		}


		@JsonProperty("myChem.info")
		public void setMyChemInfo(MyChemInfo myChemInfo) {
			this.myChemInfo = myChemInfo;
		}


		public PubChem PubChem() {
			return pubchem;
		}


		@JsonProperty("PubChem")
		public void setPubchem(PubChem pubchem) {
			this.pubchem = pubchem;
		}


		public String getAutomatHierarchyURL() {
			return automatHierarchyURL;
		}


		@JsonProperty("automat.hierarchy")
		public void setAutomatHierarchyURL(String automatHierarchyURL) {
			this.automatHierarchyURL = automatHierarchyURL;
		}


		public static class MyGeneInfo {

			private String search;
			private String query;


			public String search() {
				return search;
			}


			@JsonProperty("search")
			public void setSearch(String search) {
				this.search = search;
			}


			public String query() {
				return query;
			}


			@JsonProperty("query")
			public void setQuery(String query) {
				this.query = query;
			}

		}


		public static class MyChemInfo {
			private String query;


			public String query() {
				return query;
			}


			@JsonProperty("query")
			public void setQuery(String query) {
				this.query = query;
			}

		}


		public static class PubChem {

			private String description;
			private String synonyms;
			private String smiles;
			private String inchi;


			public String description() {
				return description;
			}


			@JsonProperty("description")
			public void setDescription(String description) {
				this.description = description;
			}


			public String synonyms() {
				return synonyms;
			}


			@JsonProperty("synonyms")
			public void setSynonyms(String synonyms) {
				this.synonyms = synonyms;
			}


			public String smiles() {
				return smiles;
			}


			@JsonProperty("smiles")
			public void setSmiles(String smiles) {
				this.smiles = smiles;
			}


			public String inchi() {
				return inchi;
			}


			@JsonProperty("inchi")
			public void setInchi(String inchi) {
				this.inchi = inchi;
			}

		}
	}


	public static class CURIES {

		private final Map<String,CURIE> curies;


		public CURIES(Map<String,CURIE> curies) {
			this.curies = curies;
		}


		public CURIE getNbcigene() {
			return curies.get("nbcigene");
		}


		public CURIE getHGNC() {
			return curies.get("hgnc");
		}


		public CURIE getEnsembl() {
			return curies.get("ensembl");
		}


		public CURIE getPubchem() {
			return curies.get("pubchem");
		}


		public CURIE getDrugbank() {
			return curies.get("drugbank");
		}


		public CURIE getChembl() {
			return curies.get("chembl");
		}


		public CURIE getHmdb() {
			return curies.get("hmdb");
		}


		public CURIE getChebi() {
			return curies.get("chebi");
		}


		public CURIE getKegg() {
			return curies.get("kegg");
		}


		public CURIE getDrugcentral() {
			return curies.get("drugcentral");
		}


		public CURIE getCas() {
			return curies.get("cas");
		}


		public Collection<CURIE> getAllCuries() {
			return curies.values();
		}
	}


	public static class CURIE {

		private String prefix;
		private String uri;
		private String producer;


		public String getPrefix() {
			return prefix;
		}


		public void setPrefix(String prefix) {
			this.prefix = prefix;
		}


		public String getUri() {
			return uri;
		}


		public void setUri(String uri) {
			this.uri = uri;
		}


		public String getProducer() {
			return producer;
		}


		public void setProducer(String producer) {
			this.producer = producer;
		}


		public boolean isPrefixOf(String curie) {
			return curie.toUpperCase().startsWith(this.prefix.toUpperCase());
		}


		public String addPrefix(String id) {
			if (id == null || id.startsWith(this.prefix)) {
				return id;
			}
			return this.prefix + id;
		}


		public String removePrefix(String curie) {
			if (curie == null) {
				return curie;
			}
			if (this.isPrefixOf(curie)) {
				return curie.substring(this.prefix.length());
			}
			return curie;
		}
	}


	public static class Timeouts {

		private int transformerInfo;


		public int getTransformerInfoTimeout() {
			return transformerInfo;
		}


		@JsonProperty("transformer_info")
		public void setTransformerInfo(int transformerInfo) {
			this.transformerInfo = transformerInfo;
		}

	}


	public static class ExpirationTimes {

		private long collections;
		private long myGeneInfo;
		private long myChemInfo;
		private long pubchem;


		public long getCollections() {
			return collections;
		}


		public void setCollections(String collections) {
			this.collections = parseTime(collections);
		}


		public long getMyGeneInfo() {
			return myGeneInfo;
		}


		@JsonProperty("myGene.info cache")
		public void setMyGeneInfo(String myGeneInfo) {
			this.myGeneInfo = parseTime(myGeneInfo);
		}


		public long getMyChemInfo() {
			return myChemInfo;
		}


		@JsonProperty("myChem.info cache")
		public void setMyChemInfo(String myChemInfo) {
			this.myChemInfo = parseTime(myChemInfo);
		}


		public long getPubchem() {
			return pubchem;
		}


		@JsonProperty("PubChem cache")
		public void setPubchem(String pubchem) {
			this.pubchem = parseTime(pubchem);
		}


		static long parseTime(String timeStr) {
			String[] strings = timeStr.split(" ");
			long time = 0;

			long sec = 1000;
			time = time + sec * getValue(strings, "s");

			long min = sec * 60;
			time = time + min * getValue(strings, "m");

			long hours = min * 60;
			time = time + hours * getValue(strings, "h");

			long days = hours * 24;
			time = time + days * getValue(strings, "d");

			long weeks = days * 7;
			time = time + weeks * getValue(strings, "w");

			long months = 365 * days / 12;
			time = time + months * getValue(strings, "mo");

			long years = months * 12;
			time = time + years * getValue(strings, "y");

			return time;
		}


		private static long getValue(String[] strings, String suffix) {
			for (String str : strings) {
				if (str.endsWith(suffix)) {
					return Long.parseLong(str.substring(0, str.length() - suffix.length()));
				}
			}
			return 0;
		}
	}

}
