package transformer.mapping;

import java.io.BufferedReader;
import java.io.FileReader;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MappedQualifier {

	final static Logger log = LoggerFactory.getLogger("application");


	public MappedQualifier() {
	}

	static {
		loadMapping();
	}


	public static void loadMapping() {
		try {
			final BufferedReader mapFile = new BufferedReader(new FileReader("conf/qualifierMap.txt"));
		}
		catch (Exception e) {
			log.warn("Failed to load attribute mapping", e);
		}
	}
}
