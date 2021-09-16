package transformer.mapping;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import apimodels.Element;
import apimodels.Names;

public class MappedName extends Names {

	final static Logger log = LoggerFactory.getLogger("application");

	private static HashMap<String,MappedType> nameTypeMap = new HashMap<>();


	public MappedName(Names src, String transformerName, String transformerLabel) {
		final String source = src.getSource() != null ? src.getSource() : transformerLabel;
		final MappedType mappedType = mapNameType(src.getNameType(), source);
		this.setName(src.getName());
		this.setSynonyms(src.getSynonyms());
		this.setNameType(mappedType.nameType);
		this.setSource(mappedType.nameSource);
		this.setProvidedBy(providedBy(src.getProvidedBy(), transformerName));
		this.setLanguage(language(src.getLanguage(), source));
	}


	private MappedType mapNameType(final String srcNameType, final String srcSource) {
		String nameType = (srcNameType == null) ? "" : srcNameType;
		String source = srcSource;
		if (nameType.length() == 0 && srcSource.indexOf('@') >= 0) {
			// extract name type for MolePro version <= 2.2
			final int lastAt = srcSource.lastIndexOf('@');
			nameType = srcSource.substring(0, lastAt);
			source = srcSource.substring(lastAt + 1);
			if (nameType.indexOf('[') >= 0) {
				nameType = nameType.substring(0, nameType.indexOf('['));
			}
		}
		// map name type
		final String key = key(nameType, source);
		if (nameTypeMap.containsKey(key)) {
			return nameTypeMap.get(key);
		}
		return new MappedType(nameType.length() > 0 ? nameType : null, source);
	}


	private String providedBy(final String srcProvidedBy, final String transformerName) {
		return (srcProvidedBy == null) ? transformerName : srcProvidedBy;
	}


	private String language(String language, String source) {
		if (language != null)
			return language;
		final int start = source.indexOf('[') + 1;
		final int end = source.indexOf(']');
		if (0 <= start && start < end) {
			return source.substring(start, end);
		}
		return null;
	}


	public static void mapNames(Element element, String transformerName, String transformerLabel) {
		List<Names> names = new ArrayList<Names>();
		if (element.getNamesSynonyms() != null)
			for (Names nameSynonyms : element.getNamesSynonyms()) {
				if (nameSynonyms instanceof MappedName) {
					names.add(nameSynonyms);
				}
				else {
					names.add(new MappedName(nameSynonyms, transformerName, transformerLabel));
				}
			}
		element.setNamesSynonyms(names);
	}


	private static String key(final String nameType, final String nameSource) {
		return "(" + nameType.toLowerCase() + "@" + nameSource.toLowerCase() + ")";
	}


	public static void loadMapping() {
		final HashMap<String,MappedType> map = new HashMap<>();
		try {
			final BufferedReader mapFile = new BufferedReader(new FileReader("conf/nameTypeMap.txt"));
			for (String line = mapFile.readLine(); line != null; line = mapFile.readLine()) {
				final String[] row = line.split("\t", 4);
				map.put(key(row[0], row[1]), new MappedType(row[2].length() > 0 ? row[2] : null, row[3]));
			}
			mapFile.close();
			nameTypeMap = map;
		}
		catch (Exception e) {
			log.warn("Failed to load attribute mapping", e);
		}
	}

	static {
		loadMapping();
	}


	private static class MappedType {

		private final String nameType;
		private final String nameSource;


		MappedType(final String nameType, final String nameSource) {
			super();
			this.nameType = nameType;
			this.nameSource = nameSource;
		}

	}
}
