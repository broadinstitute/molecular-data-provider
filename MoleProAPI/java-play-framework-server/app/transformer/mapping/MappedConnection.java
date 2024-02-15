package transformer.mapping;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import apimodels.Attribute;
import apimodels.Connection;
import apimodels.Element;
import apimodels.Predicate;
import apimodels.Qualifier;

public class MappedConnection extends Connection {

	final static Logger log = LoggerFactory.getLogger("application");

	private static HashMap<String,ArrayList<String>> attributeMap = new HashMap<>();
	private static HashMap<String,MappedPredicate> predicateMap = new HashMap<>();


	private MappedConnection(Connection src) {
		super();
		this.setUuid(mapUUID(src));
		this.setSourceElementId(src.getSourceElementId());
		this.setAttributes(src.getAttributes());
		this.setSource(src.getSource());
		this.setProvidedBy(src.getProvidedBy());
		final MappedPredicate mappedPredicate = mapPredicate(src);
		this.setBiolinkPredicate(mappedPredicate.biolinkPredicate);
		this.setInversePredicate(mappedPredicate.inversePredicate);
		this.setRelation(src.getRelation());
		this.setInverseRelation(src.getInverseRelation());
		this.setQualifiers(MappedQualifier.mapQualifiers(src, mappedPredicate.qualifiers));
	}


	private String mapUUID(Connection src) {
		if (src.getUuid() != null && src.getUuid().length() > 0)
			return src.getUuid();
		for (Attribute attribute : src.getAttributes())
			if ("connection_id".equals(attribute.getOriginalAttributeName())) {
				return attribute.getValue().toString();
			}
		return null;
	}


	private MappedPredicate mapPredicate(Connection src) {
		MappedPredicate mappingBySource = mapPredicate(src, src.getSource());
		MappedPredicate mappingByTransformer = mapPredicate(src, src.getProvidedBy());
		if (mappingBySource.rank < mappingByTransformer.rank)
			return mappingBySource;
		else
			return mappingByTransformer;
	}


	private MappedPredicate mapPredicate(Connection src, final String source) {
		final String predicate = src.getBiolinkPredicate();
		final String relation = src.getRelation();
		MappedPredicate topMapping = null;
		if (relation != null && relation.length() > 0) {
			final String key = key(source, predicate, relation);
			if (predicateMap.containsKey(key)) {
				topMapping = predicateMap.get(key);
			}
		}
		final String aKey = key(source, predicate, "");
		if (attributeMap.containsKey(aKey)) {
			final List<String> attrNames = attributeMap.get(aKey);
			for (Attribute attribute : src.getAttributes())
				if (attrNames.contains(attribute.getOriginalAttributeName())) {
					final String key = key(source, predicate, attribute.getOriginalAttributeName() + ":" + attribute.getValue());
					if (predicateMap.containsKey(key)) {
						final MappedPredicate mapping = predicateMap.get(key);
						if (topMapping == null || mapping.rank < topMapping.rank) {
							topMapping = mapping;
						}
					}
				}
		}
		if (predicateMap.containsKey(aKey)) {
			final MappedPredicate mapping = predicateMap.get(aKey);
			if (topMapping == null || mapping.rank < topMapping.rank) {
				topMapping = mapping;
			}
		}
		if (topMapping == null) {
			topMapping = new MappedPredicate(Integer.MAX_VALUE, predicate, src.getInversePredicate(), new Qualifier[0]);
		}
		return topMapping;
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
			mapFile.readLine(); // ignore header row
			int rank = 0;
			for (String line = mapFile.readLine(); line != null; line = mapFile.readLine()) {
				rank += 1;
				final String[] row = line.split("\t", 9);
				final String source = row[0];
				final String predicate = row[1];
				final String relation = row[2];
				final String attrName = row[3];
				final String attrValue = row[4];
				final String biolinkPredicate = row[5];
				final String inversePredicate = row[6];
				final String qualifiedPredicate = row[7];
				final String[] qualifiers = row[8].split("\t");
				final String aKey = key(source, predicate, "");
				MappedPredicate mappedPredicate = new MappedPredicate(rank, biolinkPredicate, inversePredicate, MappedQualifier.getQualifiers(qualifiedPredicate, qualifiers));
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

		private final int rank;
		private final String biolinkPredicate;
		private final String inversePredicate;
		private final Qualifier[] qualifiers;


		MappedPredicate(final int rank, final String biolinkPredicate, final String inversePredicate, final Qualifier[] qualifiers) {
			super();
			this.rank = rank;
			this.biolinkPredicate = biolinkPredicate;
			this.inversePredicate = inversePredicate;
			this.qualifiers = qualifiers;
		}
	}

}
