package transformer.classes;

import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.annotation.JsonProperty;

import apimodels.CompoundInfo;
import apimodels.CompoundInfoIdentifiers;
import apimodels.CompoundInfoStructure;
import apimodels.Names;
import transformer.Config;
import transformer.Config.CURIE;
import transformer.util.Cache;
import transformer.HTTP;
import transformer.JSON;

public class MyChem {

	final static Logger log = LoggerFactory.getLogger("myChem.info");

	private static final String myChemInfoQuery = Config.config.url().MyChemInfo().query();

	public static final CURIE PUBCHEM_CURIE = Config.config.getCuries().getPubchem();
	public static final CURIE CHEMBL_CURIE = Config.config.getCuries().getChembl();
	public static final CURIE CHEBI_CURIE = Config.config.getCuries().getChebi();
	public static final CURIE HMDB_CURIE = Config.config.getCuries().getHmdb();
	public static final CURIE KEGG_CURIE = Config.config.getCuries().getKegg();
	public static final CURIE DRUGCENTRAL_CURIE = Config.config.getCuries().getDrugcentral();
	public static final CURIE CAS_CURIE = Config.config.getCuries().getCas();
	public static final CURIE DRUGBANK_CURIE = Config.config.getCuries().getDrugbank();
	private static final String INCHIKEY = "InChIKey";


	static class Info {

		private static MyChemCache compounds = new MyChemCache(Config.config.getExpirationTimes().getMyChemInfo());


		static void addInfo(CompoundInfo src) {
			if (src.getIdentifiers() == null || src.getIdentifiers().getMychemInfo() != null) {
				return;
			}

			String pubchemCID = src.getIdentifiers().getPubchem();
			if (pubchemCID != null) {
				try {
					Compound compound = getCompoundByCID(pubchemCID);
					compound.addInfo(src);
					return;
				} catch (IOException e) {
					compounds.put(PUBCHEM_CURIE.getPrefix(), pubchemCID, new Compound());
					log.warn("Failed to obtain compound info from myChem.info for " + pubchemCID+"; "+e.getMessage());
				}
			}

			String chemblId = CHEMBL_CURIE.removePrefix(src.getIdentifiers().getChembl());
			if (chemblId != null) {
				try {
					Compound compound = getCompoundByChemblID(chemblId);
					compound.addInfo(src);
					return;
				} catch (IOException e) {
					compounds.put(CHEMBL_CURIE.getPrefix(), chemblId, new Compound());
					log.warn("Failed to obtain compound info from myChem.info for " + chemblId+"; "+e.getMessage());
				}
			}

			if (src.getStructure() != null) {
				String inchikey = src.getStructure().getInchikey();
				if (inchikey != null) {
					try {
						Compound compound = getCompoundByInChIKey(inchikey);
						compound.addInfo(src);
						return;
					} catch (IOException e) {
						compounds.put(INCHIKEY, inchikey, new Compound());
						log.warn("Failed to obtain compound info from myChem.info for " + inchikey+"; "+e.getMessage());
					}
				}
			}
		}


		private static Compound getCompoundByCID(String pubchemCID) throws IOException {
			Compound compound = compounds.get(PUBCHEM_CURIE.getPrefix(), pubchemCID);
			if (compound != null) {
				return compound;
			}
			return myChemInfoQuery(pubchemCID);
		}


		private static Compound getCompoundByChemblID(String chemblId) throws IOException {
			Compound compound = compounds.get(CHEMBL_CURIE.getPrefix(), chemblId);
			if (compound != null) {
				return compound;
			}
			return myChemInfoQuery(chemblId);
		}


		private static Compound getCompoundByInChIKey(final String inchikey) throws IOException {
			Compound compound = compounds.get(INCHIKEY, inchikey);
			if (compound != null) {
				return compound;
			}

			return myChemInfoQuery(inchikey);
		}


		static Compound myChemInfoQuery(final String chemid) throws IOException {
			final URL url = new URL(String.format(myChemInfoQuery, chemid));
			final String json = HTTP.get(url);
			Compound compound = JSON.mapper.readValue(json, Compound.class);
			compounds.save(compound);
			return compound;
		}


		static CompoundInfo findCompoundById(final String compoundId) {
			try {
				final URL url = new URL(String.format(myChemInfoQuery, compoundId));
				final String json = HTTP.get(url);
				final Compound compound = JSON.mapper.readValue(json, Compound.class);
				compounds.save(compound);
				return compound.addInfo(new CompoundInfo());
			} 
			catch (Exception e) {
				return null;
			}
		}
	}


	static interface NameSource {

		String getSource();


		String getName();


		List<String> getSynonyms();


		String getURL();
	}


	static abstract class StructureSource {

		abstract String getInchi();


		abstract String getInchi_key();


		abstract String getSmiles();


		void updateStructure(CompoundInfoStructure structure) {
			if (structure.getSmiles() == null) {
				structure.setSmiles(this.getSmiles());
			}
			if (structure.getInchi() == null) {
				structure.setInchi(this.getInchi());
			}
			if (structure.getInchikey() == null) {
				structure.setInchikey(this.getInchi_key());
			}
		}
	}


	static class Compound {

		private String id;
		private Chebi chebi;
		private ChEMBL chembl;
		private DrugBank drugbank;
		private PubChem pubchem;


		public String getId() {
			return id;
		}


		@JsonProperty("_id")
		public void setId(String id) {
			this.id = id;
		}


		public Chebi getChebi() {
			return chebi;
		}


		@SuppressWarnings({ "unchecked", "rawtypes" })
		public void setChebi(Object chebi) {
			if (chebi instanceof Chebi)
				this.chebi = (Chebi) chebi;
			if (chebi instanceof HashMap)
				this.chebi = new Chebi((HashMap)chebi);
			if (chebi instanceof ArrayList) {
				ArrayList chebiList = (ArrayList) chebi;
				if (chebiList.size() > 0 && chebiList.get(0) instanceof HashMap) {
					this.chebi = new Chebi((HashMap)chebiList.get(0));
				}
			}
		}


		public DrugBank getDrugbank() {
			return drugbank;
		}


		public void setDrugbank(DrugBank drugbank) {
			this.drugbank = drugbank;
		}


		public ChEMBL getChembl() {
			return chembl;
		}


		public void setChembl(ChEMBL chembl) {
			this.chembl = chembl;
		}


		public PubChem getPubchem() {
			return pubchem;
		}


		public void setPubchem(PubChem pubchem) {
			this.pubchem = pubchem;
		}


		static class Chebi implements NameSource {

			private String id;
			private String name;
			private List<String> synonyms = new ArrayList<String>();
			private String hmdb;
			private String kegg;
			private String drugcentral;
			private String cas;


			Chebi(Map<String, Object> map){
				this.id = map.get("id").toString();
				this.name = map.get("name").toString();
				this.setSynonyms(map.get("synonyms"));
				this.setXrefs(map.get("xrefs"));
			}
			
			@Override
			public String getSource() {
				return "ChEBI";
			}


			@Override
			public String getURL() {
				return String.format(CHEBI_CURIE.getUri(), id);
			}


			public String getId() {
				return id;
			}


			public void setId(String id) {
				this.id = id;
			}


			@Override
			public String getName() {
				return name;
			}


			public void setName(String name) {
				this.name = name;
			}


			@Override
			public List<String> getSynonyms() {
				return synonyms;
			}


			@SuppressWarnings({ "rawtypes", "unchecked" })
			public void setSynonyms(Object synonyms) {
				if (synonyms == null) {
					return;
				}
				if (synonyms instanceof String) {
					this.synonyms.add(synonyms.toString());
					return;
				}
				if (synonyms instanceof ArrayList) {
					this.synonyms = (ArrayList) synonyms;
					return;
				}
				log.warn("Unable to convert myChem/chebi synonyms: " + synonyms.getClass() + " @ " + this.id);
			}


			public String getHmdb() {
				return hmdb;
			}


			public String getKegg() {
				return kegg;
			}


			public String getDrugcentral() {
				return drugcentral;
			}


			public String getCas() {
				return cas;
			}


			@SuppressWarnings("rawtypes")
			@JsonProperty("xrefs")
			public void setXrefs(Object obj) {
				if (obj instanceof Map) {
					Map xrefs = (Map) obj;
					if (xrefs.containsKey("hmdb")) {
						hmdb = xrefs.get("hmdb").toString();
					}
					if (xrefs.containsKey("kegg_compound")) {
						kegg = xrefs.get("kegg_compound").toString();
					}
					if (xrefs.containsKey("drug_central")) {
						drugcentral = xrefs.get("drug_central").toString();
					}
					if (xrefs.containsKey("cas")) {
						cas = xrefs.get("cas").toString();
					}
				}
			}

		}


		static class DrugBank implements NameSource {

			private String id;
			private String name;
			private List<String> synonyms = new ArrayList<String>();


			@Override
			public String getSource() {
				return "DrugBank";
			}


			@Override
			public String getURL() {
				String id = this.id;
				if (this.id.startsWith(DRUGBANK_CURIE.getPrefix())) {
					id = this.id.substring(DRUGBANK_CURIE.getPrefix().length());
				}
				return String.format(DRUGBANK_CURIE.getUri(), id);
			}


			public String getId() {
				return id;
			}


			public void setId(String id) {
				this.id = id;
			}


			@Override
			public String getName() {
				return name;
			}


			public void setName(String name) {
				this.name = name;
			}


			@Override
			public List<String> getSynonyms() {
				return synonyms;
			}


			@SuppressWarnings({ "rawtypes", "unchecked" })
			public void setSynonyms(Object synonyms) {
				if (synonyms == null) {
					return;
				}
				if (synonyms instanceof String) {
					this.synonyms.add(synonyms.toString());
					return;
				}
				if (synonyms instanceof ArrayList) {
					this.synonyms = (ArrayList) synonyms;
					return;
				}
				log.warn("Unable to convert myChem/drugbank synonyms: " + synonyms.getClass() + " @ " + this.id);
			}
		}


		static class ChEMBL extends StructureSource implements NameSource {

			private String id;
			private String name;
			private String inchi;
			private List<String> synonyms = new ArrayList<String>();
			private String inchi_key;
			private String smiles;


			@Override
			public String getSource() {
				return "ChEMBL";
			}


			@Override
			public String getURL() {
				return String.format(CHEMBL_CURIE.getUri(), CHEMBL_CURIE.removePrefix(id));
			}


			public String getId() {
				return id;
			}


			@JsonProperty("molecule_chembl_id")
			public void setId(String id) {
				this.id = id;
			}


			@Override
			public String getName() {
				return name;
			}


			@JsonProperty("pref_name")
			public void setName(String name) {
				this.name = name;
			}


			@Override
			public String getInchi() {
				return inchi;
			}


			public void setInchi(String inchi) {
				this.inchi = inchi;
			}


			@Override
			public List<String> getSynonyms() {
				return synonyms;
			}


			@SuppressWarnings("rawtypes")
			@JsonProperty("molecule_synonyms")
			public void setSynonyms(Object synonyms) {
				if (synonyms == null) {
					return;
				}
				if (synonyms instanceof Synonym) {
					this.synonyms.add(((Synonym) synonyms).getSynonym());
					return;
				}
				if (synonyms instanceof Map) {
					Map map = (Map)synonyms;
					if (map.containsKey("molecule_synonym")) {
						this.synonyms.add(map.get("molecule_synonym").toString());
						return;
					}
				}
				if (synonyms instanceof ArrayList) {
					LinkedHashSet<String> synonymSet = new LinkedHashSet<String>();
					for (Object synonym : (ArrayList) synonyms) {
						if (synonym instanceof Synonym) {
							synonymSet.add(((Synonym) synonyms).getSynonym());
						}
					}
					this.synonyms = new ArrayList<String>();
					for (String synonym : synonymSet) {
						this.synonyms.add(synonym);
					}
					return;
				}
				log.warn("Unable to convert myChem/CheMBL synonyms: " + synonyms.getClass() + " @ " + this.id);
			}


			@Override
			public String getInchi_key() {
				return inchi_key;
			}


			public void setInchi_key(String inchi_key) {
				this.inchi_key = inchi_key;
			}


			@Override
			public String getSmiles() {
				return smiles;
			}


			public void setSmiles(String smiles) {
				this.smiles = smiles;
			}


			static class Synonym {
				private String synonym;


				public String getSynonym() {
					return synonym;
				}


				@JsonProperty("molecule_synonym")
				public void setSynonym(String synonym) {
					this.synonym = synonym;
				}

			}
		}


		static class PubChem extends StructureSource {

			private String cid;
			private String inchi;
			private String inchi_key;
			private Smiles smiles;


			public String getCid() {
				return cid;
			}


			public void setCid(String cid) {
				this.cid = cid;
			}


			public String getInchi() {
				return inchi;
			}


			public void setInchi(String inchi) {
				this.inchi = inchi;
			}


			public String getInchi_key() {
				return inchi_key;
			}


			public void setInchi_key(String inchi_key) {
				this.inchi_key = inchi_key;
			}


			public String getSmiles() {
				if (smiles == null) {
					return null;
				}
				return smiles.isomeric;
			}


			public void setSmiles(Smiles smiles) {
				this.smiles = smiles;
			}


			static class Smiles {
				private String isomeric;


				public String getIsomeric() {
					return isomeric;
				}


				public void setIsomeric(String isomeric) {
					this.isomeric = isomeric;
				}

			}

		}


		private void updateIdentifiers(CompoundInfoIdentifiers identifiers) {
			if (identifiers.getChebi() == null && chebi != null && chebi.id != null) {
				identifiers.setChebi(chebi.id);
			}
			if (identifiers.getChembl() == null && chembl != null && chembl.id != null) {
				identifiers.setChembl(CHEMBL_CURIE.getPrefix() + chembl.id);
			}
			if (identifiers.getHmdb() == null && chebi != null && chebi.hmdb != null) {
				identifiers.setHmdb(HMDB_CURIE.getPrefix() + chebi.hmdb);
			}
			if (identifiers.getKegg() == null && chebi != null && chebi.kegg != null) {
				identifiers.setKegg(KEGG_CURIE.getPrefix() + chebi.kegg);
			}
			if (identifiers.getDrugcentral() == null && chebi != null && chebi.drugcentral != null) {
				identifiers.setDrugcentral(DRUGCENTRAL_CURIE.getPrefix() + chebi.drugcentral);
			}
			if (identifiers.getCas() == null && chebi != null && chebi.cas != null) {
				identifiers.setCas(CAS_CURIE.getPrefix() + chebi.cas);
			}
			if (identifiers.getDrugbank() == null && drugbank != null && drugbank.id != null) {
				identifiers.setDrugbank(DRUGBANK_CURIE.getPrefix() + drugbank.id);
			}
			if (identifiers.getPubchem() == null && pubchem != null && pubchem.cid != null) {
				identifiers.setPubchem(PUBCHEM_CURIE.getPrefix() + pubchem.cid);
			}
			if (id != null) {
				identifiers.setMychemInfo(id);
			}
		}


		private void updateNames(NameSource source, List<Names> names, Set<String> set) {
			if (source != null && !set.contains(source.getSource())) {
				if (source.getName() != null) {
					Names compoundName = new Names();
					compoundName.setSource(source.getSource());
					compoundName.setName(source.getName());
					compoundName.setSynonyms(source.getSynonyms());
					compoundName.setUrl(source.getURL());
					names.add(compoundName);
				}
			}
		}


		private void updateNames(List<Names> names) {
			HashMap<String,Names> map = new HashMap<String,Names>();
			for (Names name : names) {
				map.put(name.getSource(), name);
			}
			updateNames(this.drugbank, names, map.keySet());
			updateNames(this.chebi, names, map.keySet());
			updateNames(this.chembl, names, map.keySet());
		}


		private void updateStructure(CompoundInfoStructure structure) {
			if (this.pubchem != null) {
				pubchem.updateStructure(structure);
				structure.setSource("PubChem@myChem.info");
			}
			else if (this.chembl != null) {
				chembl.updateStructure(structure);
				structure.setSource("ChEMBL@myChem.info");
			}
		}


		CompoundInfo addInfo(CompoundInfo src) {
			if (src.getIdentifiers() == null) {
				src.setIdentifiers(new CompoundInfoIdentifiers());
			}
			updateIdentifiers(src.getIdentifiers());

			if (src.getNamesSynonyms() == null) {
				src.setNamesSynonyms(new ArrayList<Names>());
			}
			updateNames(src.getNamesSynonyms());

			if (src.getStructure() == null) {
				src.setStructure(new CompoundInfoStructure());
			}
			if (src.getStructure().getSource() == null) {
				updateStructure(src.getStructure());
			}
			return src;
		}
	}


	private static class MyChemCache extends Cache<String,String,Compound> {

		public MyChemCache(long expirationTime) {
			super(expirationTime);
			addKeySet(PUBCHEM_CURIE.getPrefix());
			addKeySet(CHEMBL_CURIE.getPrefix());
			addKeySet(INCHIKEY);
		}


		@Override
		protected List<KeyPair<String,String>> getKeys(Compound compound) {
			List<KeyPair<String,String>> keys = new ArrayList<KeyPair<String,String>>();
			if (compound.getPubchem() != null) {
				if (compound.getPubchem().getCid() != null) {
					keys.add(new KeyPair<String,String>(PUBCHEM_CURIE.getPrefix(), compound.getPubchem().getCid()));
				}
				if (compound.getPubchem().getInchi_key() != null) {
					keys.add(new KeyPair<String,String>(INCHIKEY, compound.getPubchem().getInchi_key()));
				}
			}
			if (compound.getChembl() != null) {
				if (compound.getChembl().getId() != null) {
					keys.add(new KeyPair<String,String>(CHEMBL_CURIE.getPrefix(), compound.getChembl().getId()));
				}
				if (compound.getChembl().getInchi_key() != null) {
					keys.add(new KeyPair<String,String>(INCHIKEY, compound.getChembl().getInchi_key()));
				}
			}
			return keys;
		}
	}
}
