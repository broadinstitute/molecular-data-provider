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

public class MappedConnection extends Connection {

	final static Logger log = LoggerFactory.getLogger("application");

	private static HashMap<String,ArrayList<String>> attributeMap = new HashMap<>();
	private static HashMap<String,MappedPredicate> predicateMap = new HashMap<>();


	private MappedConnection(Connection src) {
		super();
		this.setSourceElementId(src.getSourceElementId());
		this.setEvidenceType(src.getEvidenceType());
		this.setAttributes(src.getAttributes());
		this.setSource(src.getSource());
		this.setProvidedBy(src.getProvidedBy());
		final MappedPredicate mappedPredicate = mapPredicate(src.getSource(), src.getType(), src.getRelation(), src.getAttributes());
		this.setType(mappedPredicate.biolinkPredicate);
		this.setRelation(mappedPredicate.relation);
	}


	private MappedPredicate mapPredicate(final String source, final String type, final String relation, final List<Attribute> attributes) {
		if (relation != null && relation.length() > 0) {
			final String key = key(source, type, relation);
			if (predicateMap.containsKey(key)) {
				return predicateMap.get(key);
			}
		}
		final String aKey = key(source, type, "");
		if (attributeMap.containsKey(aKey)) {
			final List<String> attrNames = attributeMap.get(aKey);
			for (Attribute attribute : attributes)
				if (attrNames.contains(attribute.getName())) {
					final String key = key(source, type, attribute.getName() + ":" + attribute.getValue());
					if (predicateMap.containsKey(key)) {
						return predicateMap.get(key);
					}
				}
		}
		if (predicateMap.containsKey(aKey)) {
			return predicateMap.get(aKey);
		}
		return new MappedPredicate(type, relation);
	}


	private static String key(final String source, final String name, final String type) {
		return "(" + source.toLowerCase() + ";" + name.toLowerCase() + ";" + type.toLowerCase() + ")";
	}


	private static List<Connection> map(List<Connection> srcConnections) {
		final List<Connection> connections = new ArrayList<>();
		if (srcConnections != null) {
			for (Connection connection : srcConnections) {
				if (connection instanceof MappedConnection) {
					connections.add(connection);
				}
				else {
					connections.add(new MappedConnection(connection));
				}
			}
		}
		return connections;
	}


	public static void mapConnections(Element element) {
		element.setConnections(map(element.getConnections()));
	}


	public static void mapPredicates(String source, List<Predicate> predicates) {
		if (predicates == null)
			return;
		for (Predicate predicate : predicates) {
			final String aKey = key(source, predicate.getPredicate(), "");
			if (predicateMap.containsKey(aKey)) {
				predicate.setPredicate(predicateMap.get(aKey).biolinkPredicate);
			}
		}
	}


	public static void loadMapping() {
		final HashMap<String,ArrayList<String>> aMap = new HashMap<>();
		final HashMap<String,MappedPredicate> pMap = new HashMap<>();
		try {
			final BufferedReader mapFile = new BufferedReader(new FileReader("conf/predicateMap.txt"));
			for (String line = mapFile.readLine(); line != null; line = mapFile.readLine()) {
				final String[] row = line.split("\t");
				final String source = row[0];
				final String type = row[1];
				final String relation = row[2];
				final String attrName = row[3];
				final String attrValue = row[4];
				final String biolinkPredicate = row[5];
				final String mappedRelation = row[6];
				final String aKey = key(source, type, "");
				MappedPredicate mappedPredicate = new MappedPredicate(biolinkPredicate, mappedRelation);
				if (relation.length() > 0) {
					pMap.put(key(source, type, relation), mappedPredicate);
				}
				if (attrName.length() > 0 && attrValue.length() > 0) {
					if (!aMap.containsKey(aKey)) {
						aMap.put(aKey, new ArrayList<String>(1));
					}
					aMap.get(aKey).add(attrName);
					pMap.put(key(source, type, attrName + ":" + attrValue), mappedPredicate);
				}
				if (relation.length() == 0 && attrName.length() == 0) {
					pMap.put(aKey, mappedPredicate);
				}
			}

			mapFile.close();
			attributeMap = aMap;
			predicateMap = pMap;
		} catch (Exception e) {
			log.warn("Failed to load predicate mapping", e);
		}
	}

	static {
		loadMapping();
	}


	private static class MappedPredicate {

		private final String biolinkPredicate;
		private final String relation;


		MappedPredicate(String biolinkPredicate, String relation) {
			super();
			this.biolinkPredicate = biolinkPredicate;
			this.relation = relation;
		}

	}
}
