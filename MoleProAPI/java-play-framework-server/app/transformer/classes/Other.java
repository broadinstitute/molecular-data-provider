package transformer.classes;

import java.util.List;

import apimodels.CollectionInfo;
import apimodels.Element;
import apimodels.Property;
import apimodels.MoleProQuery;
import transformer.Config;
import transformer.JSON;
import transformer.Transformer.Query;
import transformer.collection.CollectionsEntry;

public class Other extends TransformerClass {

	private final String elementClass;


	public Other(String elementClass) {
		super();
		this.elementClass = elementClass;
	}


	@Override
	public Query getQuery(MoleProQuery query) {
		return new Query(query);
	}


	@Override
	public Query getQuery(final List<Property> controls, CollectionsEntry entry) {
		return new Query(controls);
	}


	@Override
	public CollectionsEntry getCollection(final CollectionInfo collectionInfo, final String response) throws Exception {
		return getElementCollection(elementClass, collectionInfo, response);
	}


	public static CollectionsEntry getElementCollection(String elementClass, final CollectionInfo collectionInfo, final String response) throws Exception {
		final Element[] elements = JSON.mapper.readValue(response, Element[].class);
		collectionInfo.setElementClass(elementClass);
		collectionInfo.setUrl(Config.config.url().getBaseURL() + "/collection/");
		if (Gene.CLASS.equals(elementClass)) {
			for (Element element : elements) {
				MyGene.Info.addInfo(element);
			}
		}
		if (Compound.CLASS.equals(elementClass)) {
			for (Element element : elements) {
				MyChem.Info.addInfo(element);
			}
		}
		return new CollectionsEntry(collectionInfo, elements);
	}

}
