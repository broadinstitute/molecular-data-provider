package transformer.mapping;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.HashMap;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import apimodels.Attribute;

public class MappedInfoRes {

	final static Logger log = LoggerFactory.getLogger("application");

	private static HashMap<String,MappedInfoRes> inforesMap = new HashMap<>();

	final public String infores;

	final public String knowledgeSourceSlot;


	public MappedInfoRes(String infores, String knowledgeSourceSlot) {
		super();
		this.infores = infores;
		this.knowledgeSourceSlot = knowledgeSourceSlot;
	}

	static {
		loadMapping();
	}


	public static void loadMapping() {
		final HashMap<String,MappedInfoRes> map = new HashMap<>();
		try {
			final BufferedReader mapFile = new BufferedReader(new FileReader("conf/inforesMap.txt"));
			for (String line = mapFile.readLine(); line != null; line = mapFile.readLine()) {
				final String[] row = line.split("\t", 4);
				final MappedInfoRes mappedInfoRes = new MappedInfoRes(row[2], row[3]);
				map.put(row[0], mappedInfoRes);
				map.put(row[1], mappedInfoRes);
			}
			mapFile.close();
			inforesMap = map;
		}
		catch (Exception e) {
			log.warn("Failed to load attribute mapping", e);
		}
	}


	public static Attribute knowledgeSourceAttribute(String providedBy) {
		if (inforesMap.containsKey(providedBy)) {
			MappedInfoRes infores = inforesMap.get(providedBy);
			Attribute attribute = new Attribute();
			attribute.originalAttributeName(infores.knowledgeSourceSlot);
			attribute.attributeTypeId(infores.knowledgeSourceSlot);
			attribute.value(infores.infores);
			attribute.valueTypeId("biolink:InformationResource");
			attribute.attributeSource(map("MolePro"));
			if ("MolePro".equals(providedBy))
				attribute.description("Molecular Data Provider");
			else
				attribute.description("MolePro's " + providedBy);
			return attribute;
		}
		return null;
	}


	public static String map(String providedBy) {
		if (providedBy == null)
			return null;
		if (inforesMap.containsKey(providedBy))
			return inforesMap.get(providedBy).infores;
		return providedBy;
	}

}
