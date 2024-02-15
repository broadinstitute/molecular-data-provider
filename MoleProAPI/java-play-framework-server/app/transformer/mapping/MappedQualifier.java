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
import apimodels.Qualifier;

public class MappedQualifier extends Qualifier {

	final static Logger log = LoggerFactory.getLogger("application");

	static final String QUALIFIED_PREDICATE = "qualified_predicate";
	static final String QUALIFIER_PREFIX = "qualifier:";

	private static HashMap<String,MappedQualifier> qualifierMap = new HashMap<>();

	static {
		loadMapping();
	}


	public MappedQualifier(final String qualifierType, final String qualifierValue) {
		super();
		this.setQualifierTypeId(qualifierType);
		this.setQualifierValue(qualifierValue);
	}


	public MappedQualifier(Qualifier qualifier) {
		super();
		this.setQualifierTypeId(qualifier.getQualifierTypeId());
		this.setQualifierValue(qualifier.getQualifierValue());
	}


	private String key() {
		return getQualifierTypeId() + ":" + getQualifierValue();
	}


	private String key(final String source) {
		return source + ":" + key();
	}


	private String noValueKey(final String source) {
		return source + ":" + getQualifierTypeId() + ":";
	}


	public static void loadMapping() {
		try {
			final HashMap<String,MappedQualifier> map = new HashMap<>();
			final BufferedReader mapFile = new BufferedReader(new FileReader("conf/qualifierMap.txt"));
			for (String line = mapFile.readLine(); line != null; line = mapFile.readLine()) {
				final String[] row = line.split("\t", 5);
				final String transformer = row[0];
				final String qualifierType = row[1];
				final String qualifierValue = row[2];
				final String mappedQualifierType = row[3];
				final String mappedQualifierValue = row[4];
				final MappedQualifier qualifier = new MappedQualifier(qualifierType, qualifierValue);
				final MappedQualifier mappedQualifier = new MappedQualifier(mappedQualifierType, mappedQualifierValue);
				map.put(qualifier.key(transformer), mappedQualifier);
			}
			mapFile.close();
			qualifierMap = map;
		}
		catch (Exception e) {
			log.warn("Failed to load qualifier mapping", e);
		}
	}


	static Qualifier[] getQualifiers(String qualifiedPredicate, String[] qualifierStrings) {
		final Qualifier[] qualifiers = new Qualifier[qualifierStrings.length + 1];
		for (int i = 0; i < qualifierStrings.length; i++) {
			final String[] qualifier = qualifierStrings[i].split(":", 2);
			if (qualifier.length >= 2)
				qualifiers[i + 1] = new MappedQualifier(qualifier[0], qualifier[1].trim());
		}
		qualifiers[0] = new MappedQualifier(QUALIFIED_PREDICATE, qualifiedPredicate);
		return qualifiers;
	}


	private static void addMappedQualifier(final HashMap<String,Qualifier> mappedQualifiers, final String source, final MappedQualifier qualifier) {
		MappedQualifier mappedQualifier = qualifier;
		if (qualifierMap.containsKey(qualifier.key(source))) {
			mappedQualifier = new MappedQualifier(qualifierMap.get(qualifier.key(source)));
		}
		else if (qualifierMap.containsKey(qualifier.noValueKey(source))) {
			mappedQualifier = new MappedQualifier(qualifierMap.get(qualifier.noValueKey(source)).getQualifierTypeId(), qualifier.getQualifierValue());
		}
		mappedQualifiers.put(mappedQualifier.key(), mappedQualifier);
	}


	private static void addMappedQualifier(final HashMap<String,Qualifier> mappedQualifiers, final String source, final Attribute attribute) {
		final String qualifierType = attribute.getAttributeTypeId().substring(QUALIFIER_PREFIX.length());
		final String qualifierValue = attribute.getValue().toString();
		addMappedQualifier(mappedQualifiers, source, new MappedQualifier(qualifierType, qualifierValue));
	}


	static List<Qualifier> mapQualifiers(final Connection src, final Qualifier[] predicateQualifiers) {
		final HashMap<String,Qualifier> mappedQualifiers = new HashMap<>();
		final String source = src.getProvidedBy();
		if (src.getQualifiers() != null) {
			for (Qualifier qualifier : src.getQualifiers()) {
				addMappedQualifier(mappedQualifiers, source, new MappedQualifier(qualifier));
			}
		}
		if (src.getAttributes() != null) {
			for (Attribute attribute : src.getAttributes())
				if (attribute.getAttributeTypeId().startsWith(QUALIFIER_PREFIX)) {
					addMappedQualifier(mappedQualifiers, source, attribute);
				}
		}
		for (Qualifier qualifier : predicateQualifiers)
			if (qualifier != null && !mappedQualifiers.containsKey(qualifier.getQualifierTypeId()) && qualifier.getQualifierValue().length() > 0) {
				addMappedQualifier(mappedQualifiers, source, new MappedQualifier(qualifier));
			}
		return new ArrayList<Qualifier>(mappedQualifiers.values());
	}
}
