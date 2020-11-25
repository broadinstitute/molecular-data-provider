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

	private static HashMap<String,String> attributeMap = new HashMap<>();


	public MappedAttribute(final Attribute src) {
		super();
		this.setName(src.getName());
		this.setProvidedBy(src.getProvidedBy());
		this.setSource(src.getSource());
		this.setType(mappedType(src.getSource(), src.getName(), src.getType()));
		this.setUrl(src.getUrl());
		this.setValue(src.getValue());
	}


	private String mappedType(final String source, final String name, final String type) {
		if (type == null) {
			return null;
		}
		return attributeMap.getOrDefault(key(source, name, type), type);
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
				} else {
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
		final HashMap<String,String> map = new HashMap<>();
		try {
			final BufferedReader mapFile = new BufferedReader(new FileReader("conf/attributeMap.txt"));
			for (String line = mapFile.readLine(); line != null; line = mapFile.readLine()) {
				final String[] row = line.split("\t");
				map.put(key(row[0], row[1], row[2]), row[3]);
			}
			mapFile.close();
			attributeMap = map;
		} catch (Exception e) {
			log.warn("Failed to load attribute mapping", e);
		}
	}

	static {
		loadMapping();
	}
}
