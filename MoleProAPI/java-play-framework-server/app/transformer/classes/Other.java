package transformer.classes;

import java.util.ArrayList;
import java.util.List;

import apimodels.CollectionInfo;
import apimodels.Connection;
import apimodels.Element;
import apimodels.Property;
import apimodels.TransformerInfo;
import apimodels.MoleProQuery;
import transformer.Config;
import transformer.MoleProDB;
import transformer.Transformer.Query;
import transformer.collection.CollectionsEntry;
import transformer.mapping.MappedAttribute;
import transformer.mapping.MappedBiolinkClass;
import transformer.mapping.MappedConnection;
import transformer.mapping.MappedName;
import transformer.util.JSON;

public class Other extends TransformerClass {

	private final String elementClass;


	public Other(String elementClass) {
		super();
		this.elementClass = elementClass;
	}


	@Override
	public Query getQuery(MoleProQuery query, String cache) {
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
			mapElement(info, element);
		}
		return new CollectionsEntry(collectionInfo, elements);
	}


	public static void mapElement(TransformerInfo info, Element element) {
		if (element.getConnections() != null) {
			for (Connection connection : element.getConnections()) {
				if (connection.getSource() == null)
					connection.setSource(info.getLabel());
				if (connection.getProvidedBy() == null)
					connection.setProvidedBy(info.getName());
			}
		}
		if (element.getProvidedBy() == null) {
			element.setProvidedBy(info.getName());
			element.setSource(info.getLabel());
		}
		MappedConnection.mapConnections(element);
		MappedAttribute.mapAttributes(element);
		MappedBiolinkClass.map(element);
		MappedName.mapNames(element, info.getName(), info.getLabel());
		element.setId(bestId(element));
	}


	@SuppressWarnings("unchecked")
	public static String bestId(Element element) {
		for (String key : Config.getConfig().getIdentifierPriority()) {
			if (element.getIdentifiers().containsKey(key)) {
				Object value = element.getIdentifiers().get(key);
				if (value instanceof String) {
					return value.toString();
				}
				if (value instanceof String[] && ((String[])value).length > 0) {
					return ((String[])value)[0];
				}
				if (value instanceof ArrayList && ((ArrayList<Object>)value).size() > 0) {
					return ((ArrayList<Object>)value).get(0).toString();
				}
			}
		}
		if (element.getId() == null) {
			for (Object value : element.getIdentifiers().values()) {
				if (value instanceof String) {
					return value.toString();
				}
				if (value instanceof String[] && ((String[])value).length > 0) {
					return ((String[])value)[0];
				}
				if (value instanceof ArrayList && ((ArrayList<Object>)value).size() > 0) {
					return ((ArrayList<Object>)value).get(0).toString();
				}
			}
		}
		return element.getId();
	}


	private static Element[] getElementCollection(String elementClass, final CollectionInfo collectionInfo, final String response) throws Exception {
		final Element[] elements = JSON.mapper.readValue(response, Element[].class);
		collectionInfo.setElementClass(elementClass);
		collectionInfo.setUrl(Config.config.url().getBaseURL() + "/collection/");
		for (Element element : elements) {
			if (!MoleProDB.addInfo(element)) {
				if (Gene.CLASS.equals(elementClass) || Gene.CLASS.equals(element.getBiolinkClass())) {
					MyGene.Info.addInfo(element);
				}
				if (Compound.CLASS.equals(elementClass) || Compound.CLASS.equals(element.getBiolinkClass())) {
					Compound.updateCompound(element);
				}
			}
		}
		return elements;
	}

}
