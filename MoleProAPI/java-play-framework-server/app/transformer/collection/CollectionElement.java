package transformer.collection;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;

import apimodels.Attribute;
import apimodels.CompoundInfo;
import apimodels.CompoundInfoIdentifiers;
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

	protected abstract List<Attribute> getAttributes();


	protected void mergeAttributes(final List<Attribute> srcAttributes) {
		if (srcAttributes == null) {
			return;
		}
		final HashMap<String,HashMap<String,String>> attributes = new HashMap<>();
		if (this.getAttributes() != null && this.getAttributes().size() > 0) {
			for (Attribute attribute : this.getAttributes()) {
				if (!attributes.containsKey(attribute.getSource())) {
					attributes.put(attribute.getSource(), new HashMap<String,String>());
				}
				attributes.get(attribute.getSource()).put(attribute.getName(), attribute.getValue());
			}
		}
		for (Attribute attribute : srcAttributes) {
			if (!attributes.containsKey(attribute.getSource())
					|| !attributes.get(attribute.getSource()).containsKey(attribute.getName())) {
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


		public GeneInfo getGeneInfo() {
			return geneInfo;
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
					.source(geneInfo.getSource());
		}


		@Override
		protected List<Attribute> getAttributes() {
			return geneInfo.getAttributes();
		}

	}
	

	static class CompoundElement extends CollectionElement {

		private final CompoundInfo compoundInfo;


		protected CompoundElement(final CompoundInfo compoundInfo) {
			super();
			this.compoundInfo = compoundInfo;
		}


		public CompoundInfo getCompoundInfo() {
			return compoundInfo;
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
					.id(this.getId())
					.biolinkClass(Compound.BIOLINK_CLASS)
					.identifiers(identifiers())
					.namesSynonyms(compoundInfo.getNamesSynonyms())
					.attributes(compoundInfo.getAttributes())
					.source(compoundInfo.getSource());
		}


		@Override
		protected List<Attribute> getAttributes() {
			return compoundInfo.getAttributes();
		}
	}
	

	static class ElementElement extends CollectionElement {

		private final Element element;


		protected ElementElement(final Element element) {
			super();
			this.element = element;
		}


		@Override
		public Element getElement() {
			return element;
		}


		@Override
		public String getId() {
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
					.source(element.getSource())
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


		@Override
		protected List<Attribute> getAttributes() {
			return element.getAttributes();
		}

	}
}
