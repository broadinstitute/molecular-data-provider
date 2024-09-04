package transformer;

import java.util.ArrayList;
import java.util.List;

import apimodels.Element;
import apimodels.MoleProQuery;
import apimodels.Property;
import transformer.collection.Collections;
import transformer.collection.CollectionsEntry;
import transformer.elements.CollectionElement;
import transformer.exception.NotFoundException;

public class TransformerQuery {

	private final List<Property> controls;

	final ArrayList<Element> collection = new ArrayList<Element>();


	public TransformerQuery(final MoleProQuery query, String cache, final boolean hasInput) throws NotFoundException {
		controls = query.getControls();
		if (hasInput) {
			final String collectionId = query.getCollectionId();
			final CollectionsEntry collection = Collections.getCollection(collectionId, cache);
			getElements(collection);
		}
	}


	public TransformerQuery(final List<Property> controls, CollectionsEntry collection) {
		this.controls = controls;
		if (collection != null) {
			getElements(collection);
		}
	}


	public TransformerQuery(final List<Property> controls, ArrayList<Element> collection) {
		this(controls);
		if (collection != null) {
			for (Element element : collection) {
				this.collection.add(element);
			}
		}
	}


	private void getElements(final CollectionsEntry collection) {
		for (CollectionElement srcElement : collection.getElements()) {
			Element element = new Element();
			element.id(srcElement.getElement().getId());
			element.biolinkClass(srcElement.getElement().getBiolinkClass());
			element.identifiers(srcElement.getElement().getIdentifiers());
			element.source(srcElement.getElement().getSource());
			element.providedBy(srcElement.getElement().getProvidedBy());
			this.collection.add(element);
		}
	}


	public TransformerQuery(final List<Property> controls) {
		this.controls = controls;
	}


	public List<Property> getControls() {
		return controls;
	}


	public List<Element> getCollection() {
		return collection;
	}


	public List<String> getPropertyValue(String name) {
		List<String> values = new ArrayList<String>();
		for (Property property : controls) {
			if (name.equals(property.getName())) {
				values.add(property.getValue());
			}
		}
		return values;
	}


	public TransformerQuery query(final List<Property> controls) {
		return new TransformerQuery(controls);
	}
}
