package transformer.classes;

import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.annotation.JsonProperty;

import apimodels.CompoundInfo;
import apimodels.CompoundInfoIdentifiers;
import apimodels.Element;
import apimodels.Names;
import transformer.Config;
import transformer.classes.PubChem.Response.InformationList.Information;
import transformer.util.Cache;
import transformer.util.HTTP;
import transformer.util.JSON;
import transformer.Config.CURIE;

public class PubChem {

	final static Logger log = LoggerFactory.getLogger(PubChem.class);

	private static PubChemCache compoundNames = new PubChemCache(Config.config.getExpirationTimes().getPubchem());
	private static PubChemCache compoundSynonyms = new PubChemCache(Config.config.getExpirationTimes().getPubchem());

	private static final String PUBCHEM = "PubChem";
	private static final CURIE PUBCHEM_CURIE = Config.config.getCuries().getPubchem();
	private static final String PUBCHEM_DESCRIPTION = Config.config.url().PubChem().description();
	private static final String PUBCHEM_SYNONYMS = Config.config.url().PubChem().synonyms();
	private static final String PUBCHEM_BY_SMILES = Config.config.url().PubChem().smiles();
	private static final String PUBCHEM_BY_INCHI = Config.config.url().PubChem().inchi();


	static CompoundInfo findCompoundById(final String compoundId) {
		final Long cid = getPubChemCID(compoundId);
		if (cid == null) {
			return null;
		}
		final Names names = getNameAndSynonyms(cid);
		if (names.getName() == null) {
			return null;
		}
		CompoundInfo compound = new CompoundInfo();
		compound.setCompoundId(PUBCHEM_CURIE.getPrefix() + cid);
		compound.setIdentifiers(new CompoundInfoIdentifiers().pubchem(compound.getCompoundId()));
		compound.addNamesSynonymsItem(names);
		compound.setSource(PUBCHEM);
		return compound;
	}


	static CompoundInfo findCompoundBySmiles(final String structure) {
		return findCompoundByStructure(PUBCHEM_BY_SMILES, "smiles", structure);
	}


	static CompoundInfo findCompoundByInChI(final String structure) {
		return findCompoundByStructure(PUBCHEM_BY_INCHI, "inchi", structure);
	}


	private static CompoundInfo findCompoundByStructure(final String url, final String key, final String structure) {
		try {
			String json = HTTP.post(new URL(url), key, structure);
			Thread.sleep(200); // PubChem only allows 5 requests per second
			Response response = JSON.mapper.readValue(json, Response.class);
			if (response != null && response.getIdentifierList() != null) {
				if (response.getIdentifierList().getCids() != null
						&& response.getIdentifierList().getCids().length > 0) {
					String cid = response.getIdentifierList().getCids()[0];
					return findCompoundById(PUBCHEM_CURIE.getPrefix() + cid);
				}
			}
			return null;
		} catch (Exception e) {
			return null;
		}
	}


	static void addInfo(final Element src) {
		if (hasPubChemNames(src)) {
			return;
		}
		final Long cid = getPubChemCID(src);
		if (cid != null) {
			final Names names = getNameAndSynonyms(cid);
			src.addNamesSynonymsItem(names);
		}
	}


	private static Boolean hasPubChemNames(final Element src) {
		if (src.getNamesSynonyms() == null) {
			return false;
		}
		for (Names names : src.getNamesSynonyms())
			if (PUBCHEM.equals(names.getSource())) {
				return true;
			}

		return false;
	}


	private static Long getPubChemCID(final Element src) {
		if (src.getIdentifiers() != null && src.getIdentifiers().get("pubchem") != null) {
			return getPubChemCID(src.getIdentifiers().get("pubchem").toString());
		}
		return null;
	}


	static void addInfo(final CompoundInfo src) {
		if (hasPubChemNames(src)) {
			return;
		}
		final Long cid = getPubChemCID(src);
		if (cid != null) {
			addNameAndSynonyms(cid, src);
		}
	}


	private static Boolean hasPubChemNames(final CompoundInfo src) {
		if (src.getNamesSynonyms() == null) {
			return false;
		}
		for (Names names : src.getNamesSynonyms())
			if (PUBCHEM.equals(names.getSource())) {
				return true;
			}

		return false;
	}


	private static Long getPubChemCID(final CompoundInfo src) {
		if (src.getIdentifiers() != null) {
			return getPubChemCID(src.getIdentifiers().getPubchem());
		}
		return null;
	}


	private static void addNameAndSynonyms(long cid, CompoundInfo src) {
		final Names names = getNameAndSynonyms(cid);
		src.addNamesSynonymsItem(names);
	}


	static Long getPubChemCID(String pubchemCID) {
		if (pubchemCID == null) {
			return null;
		}
		if (pubchemCID.startsWith(PUBCHEM_CURIE.getPrefix())) {
			pubchemCID = pubchemCID.substring(PUBCHEM_CURIE.getPrefix().length());
		}
		try {
			return Long.parseLong(pubchemCID);
		} catch (NumberFormatException e) {
			return null;
		}
	}


	static Names getNameAndSynonyms(final long cid) {
		final Names names = new Names();
		names.setName(getName(cid));
		names.setSynonyms(getSynonyms(cid));
		names.setSource(PUBCHEM);
		names.setUrl(String.format(PUBCHEM_CURIE.getUri(), cid));
		return names;
	}


	private static String getName(final long cid) {
		try {
			Response response = compoundNames.get(PUBCHEM, String.valueOf(cid));
			if (response == null) {
				URL url = new URL(String.format(PUBCHEM_DESCRIPTION, cid));
				String json = HTTP.get(url);
				Thread.sleep(200); // PubChem only allows 5 requests per second
				response = JSON.mapper.readValue(json, Response.class);
				compoundNames.save(response);
			}
			Information information = response.getInformation();
			if (information != null) {
				return information.getTitle();
			}
		} catch (IOException e) {
			compoundNames.put(PUBCHEM, String.valueOf(cid), new Response());
			log.warn("Unable to obtain PubChem name for CID:"+cid+"; "+e.getMessage());
		} catch (InterruptedException e) {
		}
		return null;
	}


	private static List<String> getSynonyms(final long cid) {
		try {
			Response response = compoundSynonyms.get(PUBCHEM, String.valueOf(cid));
			if (response == null) {
				URL url = new URL(String.format(PUBCHEM_SYNONYMS, cid));
				String json = HTTP.get(url);
				Thread.sleep(200); // PubChem only allows 5 requests per second
				response = JSON.mapper.readValue(json, Response.class);
				compoundSynonyms.save(response);
			}
			Information information = response.getInformation();
			if (information != null) {
				return information.getSynonyms();
			}
		} catch (IOException e) {
			compoundSynonyms.put(PUBCHEM, String.valueOf(cid), new Response());
			log.warn("Unable to obtain PubChem synonyms for CID:"+cid+"; "+e.getMessage());
		} catch (InterruptedException e) {
		}
		return null;
	}


	static class Response {

		private InformationList informationList;

		private IdentifierList identifierList;


		public InformationList getInformationList() {
			return informationList;
		}


		@JsonProperty("InformationList")
		public void setInformationList(InformationList informationList) {
			this.informationList = informationList;
		}


		Information getInformation() {
			if (this.getInformationList() != null) {
				Information[] information = this.getInformationList().getInformation();
				if (information != null && information.length > 0) {
					return information[0];
				}
			}
			return null;
		}


		static class InformationList {

			private Information[] information;


			public Information[] getInformation() {
				return information;
			}


			@JsonProperty("Information")
			public void setInformation(Information[] information) {
				this.information = information;
			}


			static class Information {

				private String cid;
				private String title;
				private List<String> synonyms;


				public String getCid() {
					return cid;
				}


				@JsonProperty("CID")
				public void setCid(String cid) {
					this.cid = cid;
				}


				public String getTitle() {
					return title;
				}


				@JsonProperty("Title")
				public void setTitle(String title) {
					this.title = title;
				}


				public List<String> getSynonyms() {
					return synonyms;
				}


				@JsonProperty("Synonym")
				public void setSynonyms(List<String> synonyms) {
					this.synonyms = synonyms;
				}

			}
		}


		public IdentifierList getIdentifierList() {
			return identifierList;
		}


		@JsonProperty("IdentifierList")
		public void setIdentifierList(IdentifierList identifierList) {
			this.identifierList = identifierList;
		}


		static class IdentifierList {

			private String[] cids;


			public String[] getCids() {
				return cids;
			}


			@JsonProperty("CID")
			public void setCids(String[] cids) {
				this.cids = cids;
			}
		}
	}


	private static class PubChemCache extends Cache<String,String,Response> {

		public PubChemCache(long expirationTime) {
			super(expirationTime);
			addKeySet(PUBCHEM);
		}


		@Override
		protected List<KeyPair<String,String>> getKeys(Response compound) {
			List<KeyPair<String,String>> keys = new ArrayList<KeyPair<String,String>>();
			Information information = compound.getInformation();
			if (information != null) {
				keys.add(new KeyPair<String,String>(PUBCHEM, information.getCid()));
			}
			return keys;
		}
	}
}
