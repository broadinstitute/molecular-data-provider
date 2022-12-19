package transformer;

import java.util.ArrayList;
import java.util.List;

import apimodels.Element;
import apimodels.MoleProQuery;
import apimodels.Property;
import transformer.Transformer.Query;
import transformer.collection.CollectionElement;
import transformer.collection.Collections;
import transformer.collection.CollectionsEntry;
import transformer.exception.NotFoundException;

public class TransformerQuery extends Query {

	final ArrayList<Element> collection = new ArrayList<Element>();


	public TransformerQuery(final MoleProQuery query, String cache, final boolean hasInput) throws NotFoundException {
		super(query);
		if (hasInput) {
			final String collectionId = query.getCollectionId();
			final CollectionsEntry collection = Collections.getCollection(collectionId, cache);
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
	}


	public TransformerQuery(final List<Property> controls, ArrayList<Element> collection) {
		super(controls);
		if (collection != null) {
			for (Element element : collection) {
				this.collection.add(element);
			}
		}
	}


	public TransformerQuery(final List<Property> controls) {
		super(controls);
	}


	public List<Element> getCollection() {
		return collection;
	}

}
