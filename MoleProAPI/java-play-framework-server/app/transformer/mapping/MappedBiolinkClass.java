package transformer.mapping;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.HashMap;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import apimodels.Element;
import apimodels.Predicate;

public class MappedBiolinkClass {

	final static Logger log = LoggerFactory.getLogger("application");

	private static HashMap<String,String> biolinkClassMap = new HashMap<>();


	public static void map(Element element) {
		element.setBiolinkClass(biolinkClassMap.getOrDefault(element.getBiolinkClass(), element.getBiolinkClass()));
	}


	public static void map(List<Predicate> predicates) {
		if (predicates == null)
			return;
		for (Predicate predicate : predicates) {
			predicate.setSubject(biolinkClassMap.getOrDefault(predicate.getSubject(), predicate.getSubject()));
			predicate.setObject(biolinkClassMap.getOrDefault(predicate.getObject(), predicate.getObject()));
		}
	}


	public static void loadMapping() {
		final HashMap<String,String> map = new HashMap<>();
		try {
			final BufferedReader mapFile = new BufferedReader(new FileReader("conf/biolinkClassMap.txt"));
			for (String line = mapFile.readLine(); line != null; line = mapFile.readLine()) {
				final String[] row = line.split("\t");
				map.put(row[0], row[1]);
			}
			mapFile.close();
			biolinkClassMap = map;
		} catch (Exception e) {
			log.warn("Failed to load Biolink class mapping", e);
		}
	}

	static {
		loadMapping();
	}

}
