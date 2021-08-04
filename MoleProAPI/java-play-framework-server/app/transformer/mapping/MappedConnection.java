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
		this.setAttributes(src.getAttributes());
		this.setSource(src.getSource());
		this.setProvidedBy(src.getProvidedBy());
		final MappedPredicate mappedPredicate = mapPredicate(src);
		this.setBiolinkPredicate(mappedPredicate.biolinkPredicate);
		this.setInversePredicate(mappedPredicate.inversePredicate);
		this.setRelation(mappedPredicate.relation);
		this.setInverseRelation(mappedPredicate.inverseRelation);
	}


	private MappedPredicate mapPredicate(Connection src) {
		final String source = src.getSource();
		final String predicate = src.getBiolinkPredicate();
		final String relation = src.getRelation();
		if (relation != null && relation.length() > 0) {
			final String key = key(source, predicate, relation);
			if (predicateMap.containsKey(key)) {
				return predicateMap.get(key);
			}
		}
		final String aKey = key(source, predicate, "");
		if (attributeMap.containsKey(aKey)) {
			final List<String> attrNames = attributeMap.get(aKey);
			for (Attribute attribute : src.getAttributes())
				if (attrNames.contains(attribute.getOriginalAttributeName())) {
					final String key = key(source, predicate, attribute.getOriginalAttributeName() + ":" + attribute.getValue());
					if (predicateMap.containsKey(key)) {
						return predicateMap.get(key);
					}
				}
		}
		if (predicateMap.containsKey(aKey)) {
			return predicateMap.get(aKey);
		}
		return new MappedPredicate(predicate, src.getInversePredicate(), relation, src.getInverseRelation());
	}


	private static String key(final String source, final String predicate, final String relation) {
		return "(" + source.toLowerCase() + ";" + predicate.toLowerCase() + ";" + relation.toLowerCase() + ")";
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
				predicate.setInversePredicate(predicateMap.get(aKey).inversePredicate);
			}
		}
	}


	public static void loadMapping() {
		final HashMap<String,ArrayList<String>> aMap = new HashMap<>();
		final HashMap<String,MappedPredicate> pMap = new HashMap<>();
		try {
			final BufferedReader mapFile = new BufferedReader(new FileReader("conf/predicateMap.txt"));
			for (String line = mapFile.readLine(); line != null; line = mapFile.readLine()) {
				final String[] row = line.split("\t", 9);
				final String source = row[0];
				final String predicate = row[1];
				final String relation = row[2];
				final String attrName = row[3];
				final String attrValue = row[4];
				final String biolinkPredicate = row[5];
				final String inversePredicate = row[6];
				final String mappedRelation = row[7];
				final String inverseRelation = row[8];
				final String aKey = key(source, predicate, "");
				MappedPredicate mappedPredicate = new MappedPredicate(biolinkPredicate, inversePredicate, mappedRelation, inverseRelation);
				if (relation.length() > 0) {
					pMap.put(key(source, predicate, relation), mappedPredicate);
				}
				if (attrName.length() > 0 && attrValue.length() > 0) {
					if (!aMap.containsKey(aKey)) {
						aMap.put(aKey, new ArrayList<String>(1));
					}
					aMap.get(aKey).add(attrName);
					pMap.put(key(source, predicate, attrName + ":" + attrValue), mappedPredicate);
				}
				if (relation.length() == 0 && attrName.length() == 0) {
					pMap.put(aKey, mappedPredicate);
				}
			}

			mapFile.close();
			attributeMap = aMap;
			predicateMap = pMap;
		}
		catch (Exception e) {
			log.warn("Failed to load predicate mapping", e);
		}
	}

	static {
		loadMapping();
	}


	private static class MappedPredicate {

		private final String biolinkPredicate;
		private final String inversePredicate;
		private final String relation;
		private final String inverseRelation;


		MappedPredicate(final String biolinkPredicate, final String inversePredicate, final String relation, final String inverseRelation) {
			super();
			this.biolinkPredicate = biolinkPredicate;
			this.inversePredicate = inversePredicate;
			this.relation = emptyToNull(relation);
			this.inverseRelation = emptyToNull(inverseRelation);
		}


		private String emptyToNull(String relation) {
			if (relation == null)
				return null;
			if (relation.length() == 0)
				return null;
			return relation;

		}
	}
}
