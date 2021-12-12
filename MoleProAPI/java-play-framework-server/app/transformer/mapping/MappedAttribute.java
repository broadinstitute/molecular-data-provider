package transformer.mapping;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import apimodels.Attribute;
import apimodels.Connection;
import apimodels.Element;

public class MappedAttribute extends Attribute {

	final static Logger log = LoggerFactory.getLogger("application");

	private static HashMap<String,MappedType> attributeMap = new HashMap<>();


	public MappedAttribute(final Attribute src) {
		super();
		MappedType mappedType = mappedType(src.getAttributeSource(), src.getOriginalAttributeName(), src.getAttributeTypeId(), src.getValueTypeId());
		this.setAttributeTypeId(mappedType.attributeType);
		this.setOriginalAttributeName(src.getOriginalAttributeName());
		this.setValue(src.getValue());
		this.setValueTypeId(mappedType.valueType);
		this.setAttributeSource(src.getAttributeSource());
		this.setValueUrl(src.getValueUrl());
		this.setDescription(src.getDescription());
		this.setProvidedBy(src.getProvidedBy());
	}


	private MappedType mappedType(final String source, final String name, final String type, final String valueType) {
		if (type != null) {
			String key = key(source, name, type);
			if (attributeMap.containsKey(key)) {
				return attributeMap.get(key);
			}
		}
		return new MappedType(type, valueType);
	}


	private static String key(final String source, final String name, final String type) {
		return "(" + source.toLowerCase() + ";" + name.toLowerCase() + ";" + type.toLowerCase() + ")";
	}


	private static List<Attribute> map(List<Attribute> srcAttributes) {
		List<Attribute> attributes = new ArrayList<Attribute>();
		if (srcAttributes != null) {
			for (Attribute attribute : srcAttributes) {
				if (attribute instanceof MappedAttribute) {
					attributes.add(attribute);
				}
				else {
					attributes.add(new MappedAttribute(attribute));
				}
			}
		}
		return attributes;
	}


	public static void mapAttributes(Element element) {
		element.setAttributes(map(element.getAttributes()));
		if (element.getConnections() != null) {
			for (Connection connection : element.getConnections()) {
				connection.setAttributes(map(connection.getAttributes()));
			}
		}
	}


	public static void loadMapping() {
		final HashMap<String,MappedType> map = new HashMap<>();
		try {
			final BufferedReader mapFile = new BufferedReader(new FileReader("conf/attributeMap.txt"));
			for (String line = mapFile.readLine(); line != null; line = mapFile.readLine()) {
				final String[] row = line.split("\t", 5);
				map.put(key(row[0], row[1], row[2]), new MappedType(row[3], row[4]));
			}
			mapFile.close();
			attributeMap = map;
		}
		catch (Exception e) {
			log.warn("Failed to load attribute mapping", e);
		}
	}

	static {
		loadMapping();
	}


	private static class MappedType {

		private final String attributeType;
		private final String valueType;


		MappedType(String attributeType, String valueType) {
			super();
			this.attributeType = attributeType;
			this.valueType = valueType;
		}

	}
}
