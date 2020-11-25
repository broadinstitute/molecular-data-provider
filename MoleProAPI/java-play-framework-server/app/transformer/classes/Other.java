package transformer.classes;

import java.util.List;

import apimodels.CollectionInfo;
import apimodels.Connection;
import apimodels.Element;
import apimodels.Property;
import apimodels.TransformerInfo;
import apimodels.MoleProQuery;
import transformer.Config;
import transformer.Transformer.Query;
import transformer.collection.CollectionsEntry;
import transformer.mapping.MappedAttribute;
import transformer.mapping.MappedBiolinkClass;
import transformer.mapping.MappedConnection;
import transformer.util.JSON;

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
		Element[] elements = getElementCollection(elementClass, collectionInfo, response);
		for (Element element : elements) {
			MappedAttribute.mapAttributes(element);
		}
		return new CollectionsEntry(collectionInfo, elements);
	}


	public static CollectionsEntry getElementCollection(TransformerInfo info, final CollectionInfo collectionInfo, final String response) throws Exception {
		Element[] elements = getElementCollection(info.getKnowledgeMap().getOutputClass(), collectionInfo, response);
		for (Element element : elements) {
			if (element.getConnections() != null) {
				for (Connection connection : element.getConnections()) {
					if (connection.getSource() == null)
						connection.setSource(info.getLabel());
					if (connection.getProvidedBy() == null)
						connection.setProvidedBy(info.getName());
				}
			}
			MappedConnection.mapConnections(element);
			MappedAttribute.mapAttributes(element);
			MappedBiolinkClass.map(element);
		}
		return new CollectionsEntry(collectionInfo, elements);
	}


	private static Element[] getElementCollection(String elementClass, final CollectionInfo collectionInfo, final String response) throws Exception {
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
				Compound.updateCompound(element);
			}
		}
		return elements;
	}

}
