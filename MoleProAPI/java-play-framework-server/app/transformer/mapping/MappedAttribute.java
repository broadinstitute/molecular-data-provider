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
import apimodels.Predicate;
import apimodels.TransformerInfo;
import transformer.Config;
import transformer.Transformers;

public class MappedAttribute extends Attribute {

	final static Logger log = LoggerFactory.getLogger("application");

	private static final String UNSPECIFIED = "unspecified";

	private static HashMap<String,MappedType> attributeMap = new HashMap<>();

	private static HashMap<String,String> attributeValueMap = new HashMap<>();

	private static HashMap<String,KnowledgeType> knowledgeTypeMap = new HashMap<>();


	public MappedAttribute(final Attribute src) {
		super();
		MappedType mappedType = mappedType(src.getAttributeSource(), src.getOriginalAttributeName(), src.getAttributeTypeId(), src.getValueTypeId());
		this.setAttributeTypeId(mappedType.attributeType);
		this.setOriginalAttributeName(src.getOriginalAttributeName());
		this.setValue(mappedValue(src));
		this.setValueTypeId(mappedType.valueType);
		this.setAttributeSource(MappedInfoRes.map(src.getAttributeSource()));
		this.setValueUrl(src.getValueUrl());
		this.setDescription(src.getDescription());
		this.setProvidedBy(src.getProvidedBy());
		this.setAttributes(map(src.getAttributes()));
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


	private Object mappedValue(final Attribute src) {
		final String key = key(src.getAttributeSource(), src.getOriginalAttributeName(), src.getValue().toString());
		if (attributeValueMap.containsKey(key)) {
			return attributeValueMap.get(key);
		}
		return src.getValue();
	}


	private static String key(final String source, final String name, final String type) {
		return "(" + toLowerCase(source) + ";" + toLowerCase(name) + ";" + toLowerCase(type) + ")";
	}


	private static String toLowerCase(final String str) {
		return (str == null) ? "" : str.toLowerCase();
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
		String upstreamResourceId = null;
		if (element.getConnections() != null) {
			for (Connection connection : element.getConnections()) {
				connection.setAttributes(map(connection.getAttributes()));
				boolean hasSourceProvenance = false;
				boolean hasKnowledgeLevel = false;
				boolean hasAgentType = false;
				for (Attribute attribute : connection.getAttributes()) {
					if (has(attribute, "primary source")) {
						hasSourceProvenance = true;
						if (upstreamResourceId == null && attribute.getValue() != null) {
							upstreamResourceId = attribute.getValue().toString();
						}
					}
					if (has(attribute, "aggregator source")) {
						if (attribute.getValue() != null) {
							upstreamResourceId = attribute.getValue().toString();
						}
					}
					if (has(attribute, "knowledge level")) {
						hasKnowledgeLevel = true;
					}
					if (has(attribute, "agent type")) {
						hasAgentType = true;
					}
				}
				if (!hasSourceProvenance) {
					addKnowledgeSourceAttribute(connection);
				}
				if (!hasKnowledgeLevel) {
					addKnowledgeLevelAttribute(connection, element.getBiolinkClass());
				}
				if (!hasAgentType) {
					addAgentTypeAttribute(connection, element.getBiolinkClass());
				}
				connection.addAttributesItem(MappedInfoRes.knowledgeSourceAttribute("MolePro", upstreamResourceId));
			}
		}
	}


	private static boolean has(Attribute attribute, String attributeName) {
		if (attribute.getAttributeTypeId() == null) {
			return false;
		}
		return attribute.getAttributeTypeId().equals(Config.config.biolinkAttribute(attributeName));
	}


	private static void addKnowledgeSourceAttribute(Connection connection) {
		final Attribute ksAttribute = MappedInfoRes.knowledgeSourceAttribute(connection.getProvidedBy(), null);
		if (ksAttribute != null) {
			connection.addAttributesItem(ksAttribute);
		}
	}


	private static void addKnowledgeLevelAttribute(final Connection connection, final String biolinkClass) {
		final KnowledgeType knowledgeType = getKnowledgeType(connection, biolinkClass);
		final String attributeType = Config.config.biolinkAttribute("knowledge level");
		final String knowledgeLevel = (knowledgeType == null) ? UNSPECIFIED : knowledgeType.knowledgeLevel;
		connection.addAttributesItem(knowledgeTypeAttribute(attributeType, knowledgeLevel));
	}


	private static void addAgentTypeAttribute(Connection connection, final String biolinkClass) {
		final KnowledgeType knowledgeType = getKnowledgeType(connection, biolinkClass);
		final String attributeType = Config.config.biolinkAttribute("agent type");
		final String agentType = (knowledgeType == null) ? UNSPECIFIED : knowledgeType.agentType;
		connection.addAttributesItem(knowledgeTypeAttribute(attributeType, agentType));
	}


	private static KnowledgeType getKnowledgeType(final Connection connection, final String biolinkClass) {
		final String key = key(connection.getProvidedBy(), connection.getBiolinkPredicate(), biolinkClass);
		KnowledgeType knowledgeType = knowledgeTypeMap.get(key);
		if (knowledgeType == null)
			knowledgeType = knowledgeTypeMap.get(connection.getProvidedBy());
		return knowledgeType;
	}


	private static Attribute knowledgeTypeAttribute(final String attributeType, final String value) {
		Attribute attribute = new Attribute();
		attribute.originalAttributeName(attributeType);
		attribute.attributeTypeId(attributeType);
		attribute.value((value == null) ? UNSPECIFIED : value);
		attribute.valueTypeId("string");
		attribute.attributeSource(MappedInfoRes.map("MolePro"));
		return attribute;
	}


	private static void loadAttributeTypeMapping() {
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


	private static void loadAttributeValueMapping() {
		final HashMap<String,String> map = new HashMap<>();
		try {
			final BufferedReader mapFile = new BufferedReader(new FileReader("conf/attributeValueMap.txt"));
			for (String line = mapFile.readLine(); line != null; line = mapFile.readLine()) {
				final String[] row = line.split("\t", 5);
				map.put(key(row[0], row[1], row[2]), row[3]);
			}
			mapFile.close();
			attributeValueMap = map;
		}
		catch (Exception e) {
			log.warn("Failed to load attribute value mapping", e);
		}
	}


	public static void loadKnowledgeTypeMapping() {
		final HashMap<String,KnowledgeType> map = new HashMap<>();
		for (TransformerInfo transformer : Transformers.getInfo()) {
			if (!"MolePro".equals(transformer.getLabel()) && transformer.getKnowledgeMap().getEdges() != null) {
				for (Predicate predicate : transformer.getKnowledgeMap().getEdges()) {
					final String knowledgeLevel = predicate.getKnowledgeLevel();
					final String agentType = predicate.getAgentType();
					if (knowledgeLevel != null || agentType != null) {
						final String biolinkClass = predicate.getObject();
						final String key = key(transformer.getName(), predicate.getPredicate(), biolinkClass);
						map.put(key, new KnowledgeType(knowledgeLevel, agentType));
					}
				}
			}
		}
		try {
			final BufferedReader mapFile = new BufferedReader(new FileReader("conf/knowledgeTypeMap.txt"));
			mapFile.readLine(); // skip header
			for (String line = mapFile.readLine(); line != null; line = mapFile.readLine()) {
				final String[] row = line.split("\t", 3);
				map.put(row[0], new KnowledgeType(row[1], row[2]));
			}
			mapFile.close();
			knowledgeTypeMap = map;
		}
		catch (Exception e) {
			log.warn("Failed to load knowledge type mapping", e);
		}

	}


	public static void loadMapping() {
		loadAttributeTypeMapping();
		loadAttributeValueMapping();
		loadKnowledgeTypeMapping();
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


	private static class KnowledgeType {

		private final String knowledgeLevel;
		private final String agentType;


		KnowledgeType(final String knowledgeLevel, final String agentType) {
			super();
			this.knowledgeLevel = knowledgeLevel;
			this.agentType = agentType;
		}


		@Override
		public String toString() {
			return "KnowledgeType[knowledgeLevel=" + knowledgeLevel + ";agentType=" + agentType + "]";
		}
	}
}
