package transformer.collection;

import java.util.ArrayList;
import java.util.List;

import apimodels.Collection;
import apimodels.CollectionInfo;
import apimodels.CompoundInfo;
import apimodels.Element;
import apimodels.GeneInfo;
import transformer.classes.Compound;
import transformer.classes.Gene;

public class CollectionsEntry {

	private final CollectionInfo collectionInfo;

	private final CollectionElement[] elements;


	public CollectionsEntry(CollectionInfo collectionInfo, CollectionElement[] elements) {
		super();
		this.collectionInfo = collectionInfo;
		this.elements = elements;
		collectionInfo.setSize(elements.length);
	}


	public CollectionsEntry(CollectionInfo collectionInfo, Element[] elements) {
		this(collectionInfo, elements(elements));
	}


	public String getId() {
		return collectionInfo.getId();
	}


	public CollectionInfo getInfo() {
		return collectionInfo;
	}


	public CollectionElement[] getElements() {
		return elements;
	}


	public Collection asCollection() {
		final Collection collection = new Collection();
		collection.setId(this.getInfo().getId());
		collection.setElementClass(this.getInfo().getElementClass());
		collection.setSize(this.getInfo().getSize());
		collection.setSource(this.getInfo().getSource());
		collection.setUrl(this.getInfo().getUrl());
		collection.setAttributes(this.getInfo().getAttributes());
		collection.setElements(new ArrayList<Element>());
		for (CollectionElement element : this.getElements()) {
			collection.addElementsItem(element.getElement());
		}
		return collection;
	}


	static CollectionsEntry create(CollectionInfo collectionInfo, List<CollectionElement> elements) {
		CollectionElement[] elementArray = elements.toArray(new CollectionElement[elements.size()]);
		if (Gene.CLASS.equals(collectionInfo.getElementClass())) {
			return new GeneCollection(collectionInfo, elementArray);
		}
		if (Compound.CLASS.equals(collectionInfo.getElementClass())) {
			return new CompoundCollection(collectionInfo, elementArray);
		}
		return new CollectionsEntry(collectionInfo, elementArray);
	}


	private static CollectionElement[] elements(Element[] sourceElements) {
		CollectionElement[] elements = new CollectionElement[sourceElements.length];
		for (int i = 0; i < sourceElements.length; i++) {
			elements[i] = new CollectionElement.ElementElement(sourceElements[i]);
		}
		return elements;
	}


	public static final class GeneCollection extends CollectionsEntry {

		public GeneCollection(CollectionInfo collectionInfo, CollectionElement[] elements) {
			super(collectionInfo, elements);
		}


		public GeneCollection(CollectionInfo collectionInfo, GeneInfo[] genes) {
			this(collectionInfo, elements(genes));
		}


		public GeneInfo[] getGenes() {
			CollectionElement[] elements = getElements();
			GeneInfo[] genes = new GeneInfo[elements.length];
			for (int i = 0; i < elements.length; i++) {
				genes[i] = elements[i].getGeneInfo();
			}
			return genes;
		}


		private static CollectionElement[] elements(GeneInfo[] genes) {
			CollectionElement[] elements = new CollectionElement[genes.length];
			for (int i = 0; i < genes.length; i++) {
				elements[i] = new CollectionElement.GeneElement(genes[i]);
			}
			return elements;
		}
	}


	public static final class CompoundCollection extends CollectionsEntry {

		public CompoundCollection(CollectionInfo collectionInfo, CollectionElement[] compounds) {
			super(collectionInfo, compounds);
		}


		public CompoundCollection(CollectionInfo collectionInfo, CompoundInfo[] compounds) {
			this(collectionInfo, elements(compounds));
		}


		public CompoundInfo[] getCompounds() {
			CollectionElement[] elements = getElements();
			CompoundInfo[] compounds = new CompoundInfo[elements.length];
			for (int i = 0; i < elements.length; i++) {
				compounds[i] = elements[i].getCompoundInfo();
			}
			return compounds;
		}


		private static CollectionElement[] elements(CompoundInfo[] compounds) {
			CollectionElement[] elements = new CollectionElement[compounds.length];
			for (int i = 0; i < compounds.length; i++) {
				elements[i] = new CollectionElement.CompoundElement(compounds[i]);
			}
			return elements;
		}
	}
}
