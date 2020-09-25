package transformer.classes;

import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.annotation.JsonProperty;

import apimodels.Attribute;
import apimodels.Element;
import apimodels.GeneInfo;
import apimodels.GeneInfoIdentifiers;
import apimodels.Names;
import transformer.Config;
import transformer.HTTP;
import transformer.JSON;
import transformer.util.Cache;

public class MyGene {

	final static Logger log = LoggerFactory.getLogger("myGene.info");

	private static final String myGeneInfoSearch = Config.config.url().MyGeneInfo().search();
	private static final String myGeneInfoQuery = Config.config.url().MyGeneInfo().query();
	private static final Config.CURIE NCBI_GENE = Config.config.getCuries().getNbcigene();
	private static final Config.CURIE ENSEMBL = Config.config.getCuries().getEnsembl();
	private static final Config.CURIE HGNC = Config.config.getCuries().getHGNC();

	private static String SYMBOL = "Symbol";
	private static String ALIAS = "Alias";
	private static String ENTREZ = "Entrez";
	private static String CURIE = "CURIE";


	static class Info {

		static GeneCache genes = new GeneCache(Config.config.getExpirationTimes().getMyGeneInfo());


		static GeneInfo addInfo(final GeneInfo src) {
			if (getMyGeneInfoId(src) != null) {
				return src;
			}

			final String hgncId = getHgncId(src);
			if (hgncId != null) {
				try {
					final Gene gene = geneByHGNC(hgncId);
					if (gene != null) {
						return gene.addInfo(src);
					}
				} catch (IOException e) {
					e.printStackTrace();
				}
			}

			final String entrezGeneId = getEntrezGeneId(src);
			if (entrezGeneId != null) {
				try {
					final Gene gene = geneByEntrez(entrezGeneId);
					if (gene != null) {
						return gene.addInfo(src);
					}
				} catch (IOException e) {
					e.printStackTrace();
				}
			}

			final String ensemblGeneId = getEnsemblGeneId(src);
			if (ensemblGeneId != null) {
				try {
					final Gene gene = geneByEnsembl(ensemblGeneId);
					if (gene != null) {
						return gene.addInfo(src);
					}
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
			return src;
		}


		private static void addIdentifiers(Map<String,Object> identifiers, GeneInfo geneInfo) {
			if (!identifiers.containsKey("entrez")) {
				identifiers.put("entrez", geneInfo.getIdentifiers().getEntrez());
			}
			if (!identifiers.containsKey("hgnc")) {
				identifiers.put("hgnc", geneInfo.getIdentifiers().getHgnc());
			}
			if (!identifiers.containsKey("mim")) {
				identifiers.put("mim", geneInfo.getIdentifiers().getMim());
			}
			if (!identifiers.containsKey("ensembl")) {
				identifiers.put("ensembl", geneInfo.getIdentifiers().getEnsembl());
			}
			if (!identifiers.containsKey("mygene_info")) {
				identifiers.put("mygene_info", geneInfo.getIdentifiers().getMygeneInfo());
			}
		}


		private static List<Names> namesAndSynonyms(GeneInfo geneInfo) {
			final Names namesAndSynonyms = new Names();
			final HashSet<String> synonyms = new HashSet<>();
			for (Attribute attribute : geneInfo.getAttributes()) {
				if ("gene_name".equals(attribute.getName())) {
					synonyms.add(attribute.getValue());
					namesAndSynonyms.setName(attribute.getValue());
					namesAndSynonyms.setSource(attribute.getSource());
				}
				if ("gene_symbol".equals(attribute.getName())) {
					if (!synonyms.contains(attribute.getValue())) {
						synonyms.add(attribute.getValue());
						namesAndSynonyms.addSynonymsItem(attribute.getValue());
					}
					if (namesAndSynonyms.getSource() == null) {
						namesAndSynonyms.setSource(attribute.getSource());
					}
				}
				if ("synonyms".equals(attribute.getName())) {
					for (String synonym : attribute.getValue().split(";"))
						if (!synonyms.contains(synonym)) {
							synonyms.add(synonym);
							namesAndSynonyms.addSynonymsItem(synonym);
						}
					if (namesAndSynonyms.getSource() == null) {
						namesAndSynonyms.setSource(attribute.getSource());
					}
				}
			}
			final List<Names> namesAndSynonymsList = new ArrayList<>();
			namesAndSynonymsList.add(namesAndSynonyms);
			return namesAndSynonymsList;
		}

		static void addInfo(final Element src) {
			if (src.getIdentifiers() != null && src.getIdentifiers().containsKey("mygene_info")) {
				return;
			}
			GeneInfo geneInfo = addInfo(new GeneInfo().geneId(src.getId()));
			src.setId(geneInfo.getGeneId());
			if (src.getIdentifiers() == null) {
				src.setIdentifiers(new HashMap<String,Object>());
			}
			addIdentifiers(src.getIdentifiers(), geneInfo);
			for (Attribute attribute : geneInfo.getAttributes()) {
				src.addAttributesItem(attribute);
			}
			for (Names names : namesAndSynonyms(geneInfo)) {
				src.addNamesSynonymsItem(names);
			}
		}


		static GeneInfo findGeneBySymbol(final String symbol, final String source) throws IOException {
			Gene gene = getGeneBySymbol(symbol);
			if (gene == null) {
				Search search = query(symbol);
				gene = geneBySymbol(symbol, search);
				if (gene == null) {
					gene = geneByAlias(symbol, search);
				}
			}
			if (gene == null) {
				GeneInfo unknownGene = new GeneInfo().geneId(symbol);
				unknownGene.addAttributesItem(new Attribute().name("name").value("unknown gene").source("myGene.info"));
				unknownGene.addAttributesItem(new Attribute().name("gene_symbol").value(symbol).source(source));
				return unknownGene;
			}
			return gene.addInfo(new GeneInfo());
		}

		
		static GeneInfo findGeneById(final String geneId, final String source) throws IOException {
			Gene gene = getGeneById(geneId);
			if (gene == null) {
				if (NCBI_GENE.isPrefixOf(geneId)) {
					gene = geneByEntrez(geneId);
				}
				else if (HGNC.isPrefixOf(geneId)) {
					gene = geneByHGNC(geneId);
				}
				else if (ENSEMBL.isPrefixOf(geneId)) {
					gene = geneByEnsembl(geneId);
				}
			}
			if (gene == null) {
				GeneInfo unknownGene = new GeneInfo().geneId(geneId);
				unknownGene.addAttributesItem(new Attribute().name("name").value("unknown gene").source("myGene.info"));
				unknownGene.addAttributesItem(new Attribute().name("gene_id").value(geneId).source(source));
				return unknownGene;
			}
			return gene.addInfo(new GeneInfo());
		}

		private static Gene geneBySymbol(String symbol, Search searchResults) throws IOException {
			for (Hit hit : searchResults.getHits()) {
				if (symbol.equals(hit.getSymbol())) {
					return geneByEntrez(hit.getId());
				}
			}
			return null;
		}


		private static Gene geneByAlias(String symbol, Search searchResults) throws IOException {
			for (Hit hit : searchResults.getHits()) {
				Gene gene = geneByEntrez(hit.getId());
				if (gene.getAlias() != null) {
					for (String alias : gene.getAlias()) {
						if (alias.equals(symbol)) {
							return gene;
						}
					}
				}
			}
			return null;
		}


		private static String getMyGeneInfoId(final GeneInfo src) {
			if (src.getIdentifiers() != null) {
				return src.getIdentifiers().getMygeneInfo();
			} else {
				return null;
			}
		}


		private static String getHgncId(final GeneInfo src) {
			String hgncId = null;
			if (src.getIdentifiers() != null) {
				hgncId = src.getIdentifiers().getHgnc();
			}
			if (hgncId == null && src.getGeneId() != null && src.getGeneId().toUpperCase().startsWith("HGNC:")) {
				hgncId = src.getGeneId().toUpperCase();
			}
			return hgncId;
		}


		private static Gene geneByHGNC(final String hgncId) throws IOException {
			Gene gene = getGeneByHGNC(hgncId);
			if (gene != null) {
				return gene;
			}
			for (Hit hit : query(hgncId).getHits()) {
				gene = geneByEntrez(hit.getId());
				if (hgncId.equals(gene.getHGNC())) {
					genes.save(gene);
					return gene;
				}
			}
			return null;
		}


		private static Search query(final String id) throws IOException {
			final URL url = new URL(String.format(myGeneInfoSearch, id));
			final String json = HTTP.get(url);
			return JSON.mapper.readValue(json, Search.class);
		}


		private static String getEntrezGeneId(final GeneInfo src) {
			String entrezGeneId = null;
			if (src.getIdentifiers() != null) {
				entrezGeneId = src.getIdentifiers().getEntrez();
			}
			if (entrezGeneId == null && src.getGeneId() != null && NCBI_GENE.isPrefixOf(src.getGeneId())){
				entrezGeneId = src.getGeneId().toUpperCase();
			}
			return entrezGeneId;
		}


		private static Gene geneByEntrez(String entrezGeneId) throws IOException {
			entrezGeneId = NCBI_GENE.removePrefix(entrezGeneId);
			Gene gene = getGeneByEntrez(entrezGeneId);
			if (gene == null) {
				URL url = new URL(String.format(myGeneInfoQuery, entrezGeneId));
				gene = JSON.mapper.readValue(HTTP.get(url), Gene.class);
				genes.save(gene);
			}
			return gene;
		}


		private static Gene geneByEnsembl(String ensemblGeneId) throws IOException {
			ensemblGeneId = ENSEMBL.removePrefix(ensemblGeneId);
			Gene gene = getGeneByEnsembl(ensemblGeneId);
			if (gene == null) {
				URL url = new URL(String.format(myGeneInfoQuery, ensemblGeneId));
				gene = JSON.mapper.readValue(HTTP.get(url), Gene.class);
				genes.save(gene);
			}
			return gene;
		}


		private static String getEnsemblGeneId(final GeneInfo src) {
			if (src.getGeneId() != null && ENSEMBL.isPrefixOf(src.getGeneId())) {
				return src.getGeneId();
			}
			if (src.getIdentifiers() != null) {
				if (src.getIdentifiers().getEnsembl() != null && src.getIdentifiers().getEnsembl().size() > 0) {
					return src.getIdentifiers().getEnsembl().get(0);
				}
			}
			return null;
		}


		private synchronized static Gene getGeneBySymbol(final String symbol) {
			Gene gene = genes.get(SYMBOL, symbol);
			if (gene == null) {
				gene = genes.get(ALIAS, symbol);
			}
			return gene;
		}


		private synchronized static Gene getGeneByEntrez(String entrezgene) {
			return genes.get(ENTREZ, entrezgene);
		}


		private synchronized static Gene getGeneByHGNC(String hgncId) {
			return genes.get(HGNC.getPrefix(), hgncId);
		}


		private synchronized static Gene getGeneByEnsembl(String ensemblGeneId) {
			return genes.get(ENSEMBL.getPrefix(), ensemblGeneId);
		}


		private synchronized static Gene getGeneById(String geneId) {
			return genes.get(CURIE, geneId);
		}
	}


	static class Search {

		private Hit[] hits;


		public Hit[] getHits() {
			return hits;
		}


		public void setHits(Hit[] hits) {
			this.hits = hits;
		}
	}


	static class Hit {

		private String id;
		private String symbol;
		private String entrezgene;


		public String getId() {
			return id;
		}


		@JsonProperty("_id")
		public void setId(String id) {
			this.id = id;
		}


		public String getSymbol() {
			return symbol;
		}


		public void setSymbol(String symbol) {
			this.symbol = symbol;
		}


		public String getEntrezgene() {
			return entrezgene;
		}


		public void setEntrezgene(String entrezgene) {
			this.entrezgene = entrezgene;
		}
	}


	static class Gene {

		private String id;
		private String hgnc;
		private String mim;
		private Object alias;
		private String[] ensembl;
		private String entrezgene;
		private String name;
		private String symbol;


		public String getId() {
			return id;
		}


		@JsonProperty("_id")
		public void setId(String id) {
			this.id = id;
		}


		public String getHGNC() {
			return (hgnc == null) ? null : "HGNC:" + hgnc;
		}


		@JsonProperty("HGNC")
		public void setHGNC(String hgnc) {
			this.hgnc = hgnc;
		}


		public String getMIM() {
			return mim;
		}


		@JsonProperty("MIM")
		public void setMIM(String mim) {
			this.mim = mim;
		}


		@SuppressWarnings("unchecked")
		public String[] getAlias() {
			if (alias == null) {
				return null;
			}
			if (alias instanceof String)
				return new String[] { alias.toString() };
			if (alias instanceof ArrayList) {
				return ((ArrayList<String>) alias).toArray(new String[0]);
			}
			log.warn("did not convert alias " + alias.getClass().getName());
			return null;
		}


		public void setAlias(Object alias) {
			this.alias = alias;
		}


		public String[] getEnsembl() {
			return ensembl;
		}


		@SuppressWarnings("rawtypes")
		public void setEnsembl(Object ensembl) {
			if (ensembl instanceof Map) {
				String gene = getEnsemblGene((Map) ensembl);
				if (gene != null) {
					this.ensembl = new String[] { gene };
				}
			}
			else if (ensembl instanceof ArrayList) {
				ArrayList<String> genes = new ArrayList<String>();
				for (Object entry : (ArrayList) ensembl) {
					if (entry instanceof Map) {
						String gene = getEnsemblGene((Map) entry);
						if (gene != null) {
							genes.add(gene);
						}
					}
				}
				this.ensembl = genes.toArray(new String[genes.size()]);
			}
			else {
				log.warn("did not convert ensembl " + ensembl.getClass().getName());
			}
		}


		@SuppressWarnings("rawtypes")
		private String getEnsemblGene(Map map) {
			return map.get("gene").toString();
		}


		public String getEntrezgene() {
			return entrezgene;
		}


		public void setEntrezgene(String entrezgene) {
			this.entrezgene = entrezgene;
		}


		public String getName() {
			return name;
		}


		public void setName(String name) {
			this.name = name;
		}


		public String getSymbol() {
			return symbol;
		}


		public void setSymbol(String symbol) {
			this.symbol = symbol;
		}


		private void addIdentifiers(GeneInfoIdentifiers identifiers) {
			if (identifiers.getMygeneInfo() == null && getId() != null) {
				identifiers.setMygeneInfo(getId());
			}
			if (identifiers.getEntrez() == null && getEntrezgene() != null) {
				identifiers.setEntrez(NCBI_GENE.addPrefix(getEntrezgene()));
			}
			if (identifiers.getHgnc() == null && getHGNC() != null) {
				identifiers.setHgnc(getHGNC());
			}
			if (identifiers.getMim() == null && getMIM() != null) {
				identifiers.setMim("MIM:" + getMIM());
			}
			if (identifiers.getEnsembl() == null && getEnsembl() != null && getEnsembl().length > 0) {
				ArrayList<String> ensembl = new ArrayList<>();
				for (String ensemblGeneId : getEnsembl()) {
					ensembl.add(ENSEMBL.addPrefix(ensemblGeneId));
				}
				identifiers.setEnsembl(ensembl);
			}
		}


		GeneInfo addInfo(GeneInfo src) {
			if (getHGNC() != null) {
				src.setGeneId(getHGNC());
			}
			else if (getEntrezgene() != null) {
				src.setGeneId(NCBI_GENE.addPrefix(getEntrezgene()));
			}
			else if (getEnsembl() != null && getEnsembl().length > 0) {
				src.setGeneId(getEnsembl()[0]);
			}
			else {
				src.setGeneId(getSymbol());
			}
			if (getSymbol() != null) {
				src.addAttributesItem(new Attribute().name("gene_symbol").value(getSymbol()).source("myGene.info"));
			}
			if (getAlias() != null && getAlias().length > 0) {
				src.addAttributesItem(new Attribute().name("synonyms").value(String.join(";", getAlias())).source("myGene.info"));
			}
			if (getName() != null) {
				src.addAttributesItem(new Attribute().name("gene_name").value(getName()).source("myGene.info"));
			}
			if (src.getIdentifiers() == null) {
				src.setIdentifiers(new GeneInfoIdentifiers());
			}
			addIdentifiers(src.getIdentifiers());
			return src;
		}
	}


	static class GeneCache extends Cache<String,String,Gene> {

		public GeneCache(long expirationTime) {
			super(expirationTime);
			addKeySet(SYMBOL);
			addKeySet(ALIAS);
			addKeySet(ENTREZ);
			addKeySet(HGNC.getPrefix());
			addKeySet(CURIE);
			addKeySet(ENSEMBL.getPrefix());
		}


		@Override
		protected List<KeyPair<String,String>> getKeys(Gene gene) {
			List<KeyPair<String,String>> keys = new ArrayList<KeyPair<String,String>>();
			keys.add(new KeyPair<String,String>(SYMBOL, gene.getSymbol()));
			if (gene.getAlias() != null) {
				for (String alias : gene.getAlias()) {
					keys.add(new KeyPair<String,String>(ALIAS, alias));
				}
			}
			keys.add(new KeyPair<String,String>(ENTREZ, gene.getEntrezgene()));
			if (gene.getEntrezgene() != null) {
				keys.add(new KeyPair<String,String>(CURIE, NCBI_GENE.addPrefix(gene.getEntrezgene())));
			}
			keys.add(new KeyPair<String,String>(HGNC.getPrefix(), gene.getHGNC()));
			keys.add(new KeyPair<String,String>(CURIE, gene.getHGNC()));
			if (gene.getEnsembl() != null) {
				for (String ensembl : gene.getEnsembl()) {
					keys.add(new KeyPair<String,String>(ENSEMBL.getPrefix(), ensembl));
					keys.add(new KeyPair<String,String>(CURIE, ENSEMBL.addPrefix(ensembl)));
				}
			}
			return keys;
		}
	}

}
