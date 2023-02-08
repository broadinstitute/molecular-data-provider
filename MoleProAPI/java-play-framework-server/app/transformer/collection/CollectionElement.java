package transformer.collection;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;

import apimodels.Attribute;
import apimodels.CompoundInfo;
import apimodels.CompoundInfoIdentifiers;
import apimodels.CompoundInfoStructure;
import apimodels.Connection;
import apimodels.Element;
import apimodels.GeneInfo;
import apimodels.GeneInfoIdentifiers;
import apimodels.Names;
import transformer.classes.Compound;
import transformer.classes.Gene;

public abstract class CollectionElement {

	public abstract String getId();

	public abstract CollectionElement duplicate();
	
	public abstract void merge(CollectionElement other);
	
	public abstract Element getElement();
	
	public abstract GeneInfo getGeneInfo();
	
	public abstract CompoundInfo getCompoundInfo();

	protected abstract List<Attribute> getAttributes();


	protected void mergeAttributes(final List<Attribute> srcAttributes) {
		if (srcAttributes == null) {
			return;
		}
		final HashMap<String,HashMap<String,Object>> attributes = new HashMap<>();
		if (this.getAttributes() != null && this.getAttributes().size() > 0) {
			for (Attribute attribute : this.getAttributes()) {
				if (!attributes.containsKey(attribute.getAttributeSource())) {
					attributes.put(attribute.getAttributeSource(), new HashMap<String,Object>());
				}
				attributes.get(attribute.getAttributeSource()).put(attribute.getOriginalAttributeName(), attribute.getValue());
			}
		}
		for (Attribute attribute : srcAttributes) {
			if (!attributes.containsKey(attribute.getAttributeSource())
					|| !attributes.get(attribute.getAttributeSource()).containsKey(attribute.getOriginalAttributeName())) {
				this.getAttributes().add(attribute);
			}
		}
	}


	protected void mergeNames(final List<Names> thisNames, final List<Names> otherNames) {
		if (otherNames == null) {
			return;
		}
		final HashSet<String> thisSources = new HashSet<>();
		for (Names name : thisNames) {
			thisSources.add(name.getSource());
		}
		for (Names name : otherNames) {
			if (!thisSources.contains(name.getSource())) {
				thisNames.add(name);
			}
		}
	}


	static class GeneElement extends CollectionElement {

		private final GeneInfo geneInfo;


		protected GeneElement(final GeneInfo geneInfo) {
			super();
			this.geneInfo = geneInfo;
		}


		@Override
		public GeneInfo getGeneInfo() {
			return geneInfo;
		}

		@Override
		public CompoundInfo getCompoundInfo() {
			throw new ClassCastException("GeneElement cannot be cast to CompoundInfo");
		}
		
		
		private HashMap<String,Object> identifiers() {
			final HashMap<String,Object> identifiers = new HashMap<>();
			if (geneInfo.getIdentifiers() != null) {
				identifiers.put("entrez", geneInfo.getIdentifiers().getEntrez());
				identifiers.put("hgnc", geneInfo.getIdentifiers().getHgnc());
				identifiers.put("mim", geneInfo.getIdentifiers().getMim());
				identifiers.put("ensembl", geneInfo.getIdentifiers().getEnsembl());
				identifiers.put("mygene_info", geneInfo.getIdentifiers().getMygeneInfo());
			}
			return identifiers;
		}


		private List<Names> namesAndSynonyms() {
			final Names namesAndSynonyms = new Names();
			final HashSet<String> synonyms = new HashSet<>();
			for (Attribute attribute : geneInfo.getAttributes()) {
				if ("gene_name".equals(attribute.getOriginalAttributeName())) {
					synonyms.add(attribute.getValue().toString());
					namesAndSynonyms.setName(attribute.getValue().toString());
					namesAndSynonyms.setSource(attribute.getAttributeSource());
					namesAndSynonyms.setProvidedBy(attribute.getProvidedBy());
				}
				if ("gene_symbol".equals(attribute.getOriginalAttributeName())) {
					if (!synonyms.contains(attribute.getValue())) {
						synonyms.add(attribute.getValue().toString());
						namesAndSynonyms.addSynonymsItem(attribute.getValue().toString());
					}
					if (namesAndSynonyms.getSource() == null) {
						namesAndSynonyms.setSource(attribute.getAttributeSource());
						namesAndSynonyms.setProvidedBy(attribute.getProvidedBy());
					}
				}
				if ("synonyms".equals(attribute.getOriginalAttributeName())) {
					for (String synonym : attribute.getValue().toString().split(";"))
						if (!synonyms.contains(synonym)) {
							synonyms.add(synonym);
							namesAndSynonyms.addSynonymsItem(synonym);
						}
					if (namesAndSynonyms.getSource() == null) {
						namesAndSynonyms.setSource(attribute.getAttributeSource());
						namesAndSynonyms.setProvidedBy(attribute.getProvidedBy());
					}
				}
			}
			final List<Names> namesAndSynonymsList = new ArrayList<>();
			namesAndSynonymsList.add(namesAndSynonyms);
			return namesAndSynonymsList;
		}


		@Override
		public String getId() {
			return geneInfo.getGeneId();
		}


		@Override
		public CollectionElement duplicate() {
			return new GeneElement(
				new GeneInfo()
					.geneId(geneInfo.getGeneId())
					.identifiers(geneInfo.getIdentifiers())
					.attributes(new ArrayList<Attribute>())
					.source(geneInfo.getSource())
				);
		}


		@Override
		public void merge(final CollectionElement src) {
			if (!(src instanceof GeneElement)) {
				return;
			}
			final GeneElement other = (GeneElement) src;
			if (this.geneInfo.getIdentifiers() == null) {
				this.geneInfo.setIdentifiers(other.geneInfo.getIdentifiers());
			}
			else {
				mergeIdentifiers(other.geneInfo.getIdentifiers());
			}

			mergeAttributes(other.getAttributes());
		}


		private void mergeIdentifiers(final GeneInfoIdentifiers identifiers) {
			if (identifiers == null) {
				return;
			}
			if (this.geneInfo.getIdentifiers().getEntrez() == null) {
				this.geneInfo.getIdentifiers().setEntrez(identifiers.getEntrez());
			}
			if (this.geneInfo.getIdentifiers().getHgnc() == null) {
				this.geneInfo.getIdentifiers().setHgnc(identifiers.getHgnc());
			}
			if (this.geneInfo.getIdentifiers().getMim() == null) {
				this.geneInfo.getIdentifiers().setMim(identifiers.getMim());
			}
			if (this.geneInfo.getIdentifiers().getEnsembl() == null) {
				this.geneInfo.getIdentifiers().setEnsembl(identifiers.getEnsembl());
			}
			if (this.geneInfo.getIdentifiers().getMygeneInfo() == null) {
				this.geneInfo.getIdentifiers().setMygeneInfo(identifiers.getMygeneInfo());
			}
		}


		@Override
		public Element getElement() {
			return new Element()
					.id(this.getId())
					.biolinkClass(Gene.BIOLINK_CLASS)
					.identifiers(identifiers())
					.namesSynonyms(namesAndSynonyms())
					.attributes(geneInfo.getAttributes())
					.source(geneInfo.getSource())
					.providedBy(geneInfo.getSource());
		}


		@Override
		protected List<Attribute> getAttributes() {
			return geneInfo.getAttributes();
		}

	}
	

	public static class CompoundElement extends CollectionElement {

		private final CompoundInfo compoundInfo;


		public CompoundElement(final CompoundInfo compoundInfo) {
			super();
			this.compoundInfo = compoundInfo;
		}


		@Override
		public CompoundInfo getCompoundInfo() {
			return compoundInfo;
		}


		@Override
		public GeneInfo getGeneInfo() {
			throw new ClassCastException("CompoundElement cannot be cast to GeneInfo");
		}


		private HashMap<String,Object> identifiers() {
			final HashMap<String,Object> identifiers = new HashMap<>();
			if (compoundInfo.getIdentifiers() != null) {
				identifiers.put("pubchem", compoundInfo.getIdentifiers().getPubchem());
				identifiers.put("drugbank", compoundInfo.getIdentifiers().getDrugbank());
				identifiers.put("chembl", compoundInfo.getIdentifiers().getChembl());
				identifiers.put("chebi", compoundInfo.getIdentifiers().getChebi());
				identifiers.put("hmdb", compoundInfo.getIdentifiers().getHmdb());
				identifiers.put("mychem_info", compoundInfo.getIdentifiers().getMychemInfo());
			}
			if (compoundInfo.getStructure() != null) {
				identifiers.put("inchikey", compoundInfo.getStructure().getInchikey());
				identifiers.put("inchi", compoundInfo.getStructure().getInchi());
				identifiers.put("smiles", compoundInfo.getStructure().getSmiles());
			}
			return identifiers;
		}


		@Override
		public String getId() {
			if (compoundInfo.getStructure() != null && compoundInfo.getStructure().getInchikey() != null) {
				return compoundInfo.getStructure().getInchikey();
			}
			if (compoundInfo.getIdentifiers() != null && compoundInfo.getIdentifiers().getMychemInfo() != null) {
				compoundInfo.getIdentifiers().getMychemInfo();
			}
			return compoundInfo.getCompoundId();
		}


		@Override
		public CollectionElement duplicate() {
			return new CompoundElement(
				new CompoundInfo()
					.compoundId(compoundInfo.getCompoundId())
					.identifiers(compoundInfo.getIdentifiers())
					.namesSynonyms(compoundInfo.getNamesSynonyms())
					.structure(compoundInfo.getStructure())
					.attributes(new ArrayList<Attribute>())
					.source(compoundInfo.getSource())
			);
		}


		@Override
		public void merge(final CollectionElement src) {
			if (!(src instanceof CompoundElement)) {
				return;
			}
			final CompoundElement other = (CompoundElement) src;
			if (this.compoundInfo.getIdentifiers() == null) {
				this.compoundInfo.setIdentifiers(other.compoundInfo.getIdentifiers());
			}
			else {
				mergeIdentifiers(other.compoundInfo.getIdentifiers());
			}
			if (this.compoundInfo.getNamesSynonyms() == null) {
				this.compoundInfo.setNamesSynonyms(other.compoundInfo.getNamesSynonyms());
			}
			else {
				mergeNames(this.compoundInfo.getNamesSynonyms(), other.compoundInfo.getNamesSynonyms());
			}
			mergeAttributes(other.getAttributes());
		}


		private void mergeIdentifiers(final CompoundInfoIdentifiers identifiers) {
			if (identifiers == null) {
				return;
			}
			if (this.compoundInfo.getIdentifiers().getChebi() == null) {
				this.compoundInfo.getIdentifiers().setChebi(identifiers.getChebi());
			}
			if (this.compoundInfo.getIdentifiers().getChembl() == null) {
				this.compoundInfo.getIdentifiers().setChembl(identifiers.getChembl());
			}
			if (this.compoundInfo.getIdentifiers().getDrugbank() == null) {
				this.compoundInfo.getIdentifiers().setDrugbank(identifiers.getDrugbank());
			}
			if (this.compoundInfo.getIdentifiers().getPubchem() == null) {
				this.compoundInfo.getIdentifiers().setPubchem(identifiers.getPubchem());
			}
			if (this.compoundInfo.getIdentifiers().getMesh() == null) {
				this.compoundInfo.getIdentifiers().setMesh(identifiers.getMesh());
			}
			if (this.compoundInfo.getIdentifiers().getHmdb() == null) {
				this.compoundInfo.getIdentifiers().setHmdb(identifiers.getHmdb());
			}
			if (this.compoundInfo.getIdentifiers().getUnii() == null) {
				this.compoundInfo.getIdentifiers().setUnii(identifiers.getUnii());
			}
			if (this.compoundInfo.getIdentifiers().getKegg() == null) {
				this.compoundInfo.getIdentifiers().setKegg(identifiers.getKegg());
			}
			if (this.compoundInfo.getIdentifiers().getGtopdb() == null) {
				this.compoundInfo.getIdentifiers().setGtopdb(identifiers.getGtopdb());
			}
			if (this.compoundInfo.getIdentifiers().getChembank() == null) {
				this.compoundInfo.getIdentifiers().setChembank(identifiers.getChembank());
			}
			if (this.compoundInfo.getIdentifiers().getDrugcentral() == null) {
				this.compoundInfo.getIdentifiers().setDrugcentral(identifiers.getDrugcentral());
			}
			if (this.compoundInfo.getIdentifiers().getCas() == null) {
				this.compoundInfo.getIdentifiers().setCas(identifiers.getCas());
			}
			if (this.compoundInfo.getIdentifiers().getMychemInfo() == null) {
				this.compoundInfo.getIdentifiers().setMychemInfo(identifiers.getMychemInfo());
			}
		}


		@Override
		public Element getElement() {
			return new Element()
					.id(compoundInfo.getCompoundId())
					.biolinkClass(Compound.BIOLINK_CLASS)
					.identifiers(identifiers())
					.namesSynonyms(compoundInfo.getNamesSynonyms())
					.attributes(compoundInfo.getAttributes())
					.source(compoundInfo.getSource())
					.providedBy(compoundInfo.getSource());
		}


		@Override
		protected List<Attribute> getAttributes() {
			return compoundInfo.getAttributes();
		}
	}
	

	public static class ElementElement extends CollectionElement {

		private final Element element;


		public ElementElement(final Element element) {
			super();
			this.element = element;
		}


		@Override
		public Element getElement() {
			return element;
		}


		@Override
		public CompoundInfo getCompoundInfo() {
			return getCompoundInfo(getElement());
		}


		static CompoundInfo getCompoundInfo(final Element element) {
			if (!Compound.BIOLINK_CLASS.equals(element.getBiolinkClass())) {
				throw new ClassCastException("Element("+element.getBiolinkClass()+") cannot be cast to "+Compound.BIOLINK_CLASS);
			}
			final CompoundInfo compoundInfo = new CompoundInfo();
			compoundInfo.setCompoundId(element.getId());
			final CompoundInfoIdentifiers identifiers = compoundIdentifiers(element);
			compoundInfo.setIdentifiers(identifiers);
			if (element.getNamesSynonyms() != null) {
				for (Names name : element.getNamesSynonyms()) {
					compoundInfo.addNamesSynonymsItem(name);
				}
			}
			final CompoundInfoStructure structure = new CompoundInfoStructure();
			if (element.getIdentifiers().containsKey("smiles") && element.getIdentifiers().get("smiles") != null) {
				structure.setSmiles(element.getIdentifiers().get("smiles").toString());
			}
			if (element.getIdentifiers().containsKey("inchi") && element.getIdentifiers().get("inchi") != null) {
				structure.setInchi(element.getIdentifiers().get("inchi").toString());
			}
			if (element.getIdentifiers().containsKey("inchikey") && element.getIdentifiers().get("inchikey") != null) {
				structure.setInchikey(element.getIdentifiers().get("inchikey").toString());
			}
			compoundInfo.setStructure(structure);
			for (Attribute attribute : element.getAttributes()) {
				if ("structure source".equals(attribute.getOriginalAttributeName())) {
					structure.setSource(attribute.getValue().toString());
				}
				else {
					compoundInfo.addAttributesItem(attribute);
				}
			}
			compoundInfo.setSource(element.getSource());
			return compoundInfo;
		}


		private static CompoundInfoIdentifiers compoundIdentifiers(final Element element) {
			final CompoundInfoIdentifiers identifiers = new CompoundInfoIdentifiers();
			if (element.getIdentifiers().containsKey("chebi") && element.getIdentifiers().get("chebi") != null) {
				identifiers.setChebi(element.getIdentifiers().get("chebi").toString());
			}
			if (element.getIdentifiers().containsKey("chembl") && element.getIdentifiers().get("chembl") != null) {
				identifiers.setChembl(element.getIdentifiers().get("chembl").toString());
			}
			if (element.getIdentifiers().containsKey("drugbank") && element.getIdentifiers().get("drugbank") != null) {
				identifiers.setDrugbank(element.getIdentifiers().get("drugbank").toString());
			}
			if (element.getIdentifiers().containsKey("pubchem") && element.getIdentifiers().get("pubchem") != null) {
				identifiers.setPubchem(element.getIdentifiers().get("pubchem").toString());
			}
			if (element.getIdentifiers().containsKey("mesh") && element.getIdentifiers().get("mesh") != null) {
				identifiers.setMesh(element.getIdentifiers().get("mesh").toString());
			}
			if (element.getIdentifiers().containsKey("hmdb") && element.getIdentifiers().get("hmdb") != null) {
				identifiers.setHmdb(element.getIdentifiers().get("hmdb").toString());
			}
			if (element.getIdentifiers().containsKey("unii") && element.getIdentifiers().get("unii") != null) {
				identifiers.setUnii(element.getIdentifiers().get("unii").toString());
			}
			if (element.getIdentifiers().containsKey("kegg") && element.getIdentifiers().get("kegg") != null) {
				identifiers.setKegg(element.getIdentifiers().get("kegg").toString());
			}
			if (element.getIdentifiers().containsKey("gtopdb") && element.getIdentifiers().get("gtopdb") != null) {
				identifiers.setGtopdb(element.getIdentifiers().get("gtopdb").toString());
			}
			if (element.getIdentifiers().containsKey("chembank") && element.getIdentifiers().get("chembank") != null) {
				identifiers.setChembank(element.getIdentifiers().get("chembank").toString());
			}
			if (element.getIdentifiers().containsKey("drugcentral") && element.getIdentifiers().get("drugcentral") != null) {
				identifiers.setDrugcentral(element.getIdentifiers().get("drugcentral").toString());
			}
			if (element.getIdentifiers().containsKey("cas") && element.getIdentifiers().get("cas") != null) {
				identifiers.setCas(element.getIdentifiers().get("cas").toString());
			}
			if (element.getIdentifiers().containsKey("mychem_info") && element.getIdentifiers().get("mychem_info") != null) {
				identifiers.setMychemInfo(element.getIdentifiers().get("mychem_info").toString());
			}
			return identifiers;
		}


		@Override
		public GeneInfo getGeneInfo() {
			return getGeneInfo(getElement());
		}


		public GeneInfo getGeneInfo(final Element element) {
			if (!Gene.BIOLINK_CLASS.equals(element.getBiolinkClass())) {
				throw new ClassCastException("Element(" + element.getBiolinkClass() + ") cannot be cast to GeneInfo");
			}
			final GeneInfo geneInfo = new GeneInfo();
			geneInfo.setGeneId(element.getId());
			final GeneInfoIdentifiers identifiers = geneIdentifiers(element);
			geneInfo.setIdentifiers(identifiers);
			for (Attribute attribute : element.getAttributes()) {
				geneInfo.addAttributesItem(attribute);
			}
			geneInfo.setSource(element.getSource());
			return geneInfo;
		}


		private GeneInfoIdentifiers geneIdentifiers(final Element element) {
			final GeneInfoIdentifiers identifiers = new GeneInfoIdentifiers();
			if (element.getIdentifiers().containsKey("entrez") && element.getIdentifiers().get("entrez") != null) {
				identifiers.setEntrez(element.getIdentifiers().get("entrez").toString());
			}			
			if (element.getIdentifiers().containsKey("hgnc") && element.getIdentifiers().get("hgnc") != null) {
				identifiers.setHgnc(element.getIdentifiers().get("hgnc").toString());
			}			
			if (element.getIdentifiers().containsKey("mim") && element.getIdentifiers().get("mim") != null) {
				identifiers.setMim(element.getIdentifiers().get("mim").toString());
			}			
			if (element.getIdentifiers().containsKey("ensembl") && element.getIdentifiers().get("ensembl") != null) {
				final List<String> ensembl = new ArrayList<>();
				if (element.getIdentifiers().get("ensembl") instanceof String[]) {
					final String[] ensemblSrc = (String[])element.getIdentifiers().get("ensembl");
					for (String id : ensemblSrc) {
						ensembl.add(id);
					}
				}
				else {
					ensembl.add(element.getIdentifiers().get("ensembl").toString());
				}
				identifiers.setEnsembl(ensembl);
			}			
			if (element.getIdentifiers().containsKey("mygene_info") && element.getIdentifiers().get("mygene_info") != null) {
				identifiers.setMygeneInfo(element.getIdentifiers().get("mygene_info").toString());
			}
			return identifiers;
		}


		@Override
		public String getId() {
			if (Compound.BIOLINK_CLASS.equals(element.getBiolinkClass())) {
				if (element.getIdentifiers() != null && element.getIdentifiers().get("inchikey") != null)
					return element.getIdentifiers().get("inchikey").toString();
			}
			return element.getId();
		}


		@Override
		public CollectionElement duplicate() {
			return new ElementElement(
				new Element()
					.id(element.getId())
					.biolinkClass(element.getBiolinkClass())
					.identifiers(element.getIdentifiers())
					.namesSynonyms(element.getNamesSynonyms())
					.attributes(new ArrayList<Attribute>())
					.connections(new ArrayList<Connection>())
					.source(element.getSource())
					.providedBy(element.getProvidedBy())
			);
		}


		@Override
		public void merge(final CollectionElement src) {
			if (!(src instanceof ElementElement)) {
				return;
			}
			final ElementElement other = (ElementElement) src;
			if (this.element.getIdentifiers() == null) {
				this.element.setIdentifiers(other.element.getIdentifiers());
			}
			else {
				mergeIdentifiers(other.element.getIdentifiers());
			}
			if (this.element.getNamesSynonyms() == null) {
				this.element.setNamesSynonyms(other.element.getNamesSynonyms());
			}
			else {
				mergeNames(this.element.getNamesSynonyms(), other.element.getNamesSynonyms());
			}
			mergeAttributes(other.getAttributes());
			mergeConnections(other.element.getConnections());
		}


		private void mergeIdentifiers(final Map<String,Object> identifiers) {
			if (identifiers == null) {
				return;
			}
			for (String key : identifiers.keySet()) {
				if (!this.element.getIdentifiers().containsKey(key)) {
					this.element.getIdentifiers().put(key, identifiers.get(key));
				}
			}
		}


		private void mergeConnections(final List<Connection> connections) {
			if (connections == null || connections.size() == 0) {
				return;
			}
			if (this.element.getConnections() == null || this.element.getConnections().size() == 0) {
				this.element.setConnections(connections);
				return;
			}
			HashMap<String,Connection> connectionMap = new HashMap<>();
			for (Connection connection : this.element.getConnections()) {
				String key = connection.getSourceElementId() + " # " + connection.getProvidedBy();
				connectionMap.put(key, connection);
			}
			for (Connection connection : connections) {
				String key = connection.getSourceElementId() + " # " + connection.getProvidedBy();
				if (!connectionMap.containsKey(key)) {
					this.element.addConnectionsItem(connection);
				}
			}
		}

		
		@Override
		protected List<Attribute> getAttributes() {
			return element.getAttributes();
		}

	}

}
