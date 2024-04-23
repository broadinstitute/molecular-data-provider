package transformer.collection;

import java.util.ArrayList;
import java.util.List;

import apimodels.Collection;
import apimodels.CollectionInfo;
import apimodels.Element;
import transformer.elements.CollectionElement;

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
		return new CollectionsEntry(collectionInfo, elementArray);
	}


	private static CollectionElement[] elements(Element[] sourceElements) {
		ArrayList<CollectionElement> elements = new ArrayList<>(sourceElements.length);
		for (Element sourceElement : sourceElements) {
			if (sourceElement != null && sourceElement.getId() != null) {
				elements.add(new CollectionElement(sourceElement));
			}
		}
		return elements.toArray(new CollectionElement[0]);
	}



}
