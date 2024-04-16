package transformer.elements;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;

import apimodels.Attribute;
import apimodels.Connection;
import apimodels.Element;
import apimodels.Names;
import apimodels.TransformerInfo;
import transformer.Config;
import transformer.mapping.MappedAttribute;
import transformer.mapping.MappedBiolinkClass;
import transformer.mapping.MappedConnection;
import transformer.mapping.MappedName;

public class CollectionElement {

	private final Element element;


	public CollectionElement(final Element element) {
		super();
		this.element = element;
	}


	public Element getElement() {
		return element;
	}


	public String getId() {
		if (element.getIdentifiers() != null && element.getIdentifiers().get("inchikey") != null)
			return element.getIdentifiers().get("inchikey").toString();
		return element.getId();
	}


	public CollectionElement duplicate() {
		final Element duplicate = new Element();
		duplicate.setId(element.getId());
		duplicate.setBiolinkClass(element.getBiolinkClass());
		duplicate.setIdentifiers(element.getIdentifiers());
		duplicate.setNamesSynonyms(element.getNamesSynonyms());
		duplicate.setAttributes(new ArrayList<Attribute>());
		duplicate.setConnections(new ArrayList<Connection>());
		duplicate.setSource(element.getSource());
		duplicate.setProvidedBy(element.getProvidedBy());
		return new CollectionElement(duplicate);
	}


	public void merge(final CollectionElement other) {
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
		mergeAttributes(other.element.getAttributes());
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


	private void mergeNames(final List<Names> thisNames, final List<Names> otherNames) {
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


	private void mergeAttributes(final List<Attribute> srcAttributes) {
		if (srcAttributes == null) {
			return;
		}
		final HashMap<String,HashMap<String,Object>> attributes = new HashMap<>();
		if (this.element.getAttributes() != null && this.element.getAttributes().size() > 0) {
			for (Attribute attribute : this.element.getAttributes()) {
				if (!attributes.containsKey(attribute.getAttributeSource())) {
					attributes.put(attribute.getAttributeSource(), new HashMap<String,Object>());
				}
				attributes.get(attribute.getAttributeSource()).put(attribute.getOriginalAttributeName(), attribute.getValue());
			}
		}
		for (Attribute attribute : srcAttributes) {
			if (!attributes.containsKey(attribute.getAttributeSource()) || !attributes.get(attribute.getAttributeSource()).containsKey(attribute.getOriginalAttributeName())) {
				this.element.getAttributes().add(attribute);
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
		for (String key : Config.getConfig().getIdentifierPriority(element.getBiolinkClass())) {
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



}
