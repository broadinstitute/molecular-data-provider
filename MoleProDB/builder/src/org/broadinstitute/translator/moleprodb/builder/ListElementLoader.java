package org.broadinstitute.translator.moleprodb.builder;

import java.io.BufferedReader;
import java.io.FileReader;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;

import org.broadinstitute.translator.moleprodb.db.IdentifierTable;
import org.broadinstitute.translator.moleprodb.db.MoleProDB;

import apimodels.Attribute;
import apimodels.Element;
import apimodels.Names;
import apimodels.Parameter;
import apimodels.Property;
import transformer.TransformerQuery;
import transformer.Transformers;

public class ListElementLoader extends Loader {

	static final String MOLE_PRO_PREFIX = "MolePro:";

	private static final int BATCH_SIZE = 100;


	public ListElementLoader(MoleProDB db) {
		super(db);
	}


	public void loadElements(final String transformerName, final String compoundFile, final String[] matchFields) throws Exception {
		Transformers.getTransformers();
		final TransformerRun transformer = new TransformerRun(transformerName);
		ArrayList<String> batch = new ArrayList<>();
		int i = 0;
		final BufferedReader input = new BufferedReader(new FileReader(compoundFile));
		try {
			input.readLine(); // header line
			for (String element = input.readLine(); element != null; element = input.readLine()) {

				batch.add(element);
				i = i + 1;
				if (i % BATCH_SIZE == 0) {
					System.out.println(element + "\t@" + i);
					loadElements(transformer, batch, matchFields);
					db.commit();
					System.out.println();
					batch = new ArrayList<>();
				}
				if (i % (10 * BATCH_SIZE) == 0) {
					System.out.println("db.reconnect");
					db.reconnect();
				}
				if (i % (100 * BATCH_SIZE) == 0) {
					Loader.profileReport();
				}
			}
			if (batch.size() > 0) {
				loadElements(transformer, batch, matchFields);
				db.commit();
			}
		}
		finally {
			db.rollback();
			input.close();
		}
	}


	HashSet<Long> loadElements(final TransformerRun transformer, final ArrayList<String> batch, final String[] matchFields) {
		final int sourceId = db.sourceTable.sourceId(transformer.info.getName());
		HashSet<Long> elementIds = new HashSet<>();
		try {
			final List<Property> controls = new ArrayList<>();
			final Parameter parameter = transformer.info.getParameters().get(0);
			if (parameter.getMultivalued() != null && parameter.getMultivalued()) {
				for (String value : batch) {
					if (value != null)
						controls.add(new Property().name(parameter.getName()).value(value));
				}
			}
			else {
				controls.add(new Property().name(parameter.getName()).value(String.join(";", batch)));
			}
			for (Property property : transformer.controls()) {
				controls.add(property);
			}
			final TransformerQuery query = new TransformerQuery(controls);
			final Element[] elements = transform(transformer.transformer, query);
			final HashSet<String> foundIds = new HashSet<>();
			for (Element element : elements) {
				if (element != null) {
					final long elementId = getCreateListElementId(element, sourceId, matchFields);
					if (elementId > 0) {
						elementIds.add(elementId);
						for (String queryId : queryNames(element)) {
							foundIds.add(queryId);
						}
					}
				}
			}
			for (String id : batch) {
				if (!foundIds.contains(id)) {
					System.out.println("WARN: id not found " + id);
				}
			}
		}
		catch (Exception e) {
			if (batch.size() > 1) {
				System.err.println("INFO: batch load failed, trying single elements");
				elementIds = new HashSet<>();
				final ArrayList<String> singleton = new ArrayList<String>(1);
				singleton.add(null);
				for (String element : batch) {
					singleton.set(0, element);
					final HashSet<Long> singleId = loadElements(transformer, singleton, matchFields);
					for (long elementId : singleId) {
						if (elementId > 0) {
							elementIds.add(elementId);
						}
					}
				}

			}
			else {
				System.err.println("WARNING: " + transformer.info.getName() + " failed to load " + batch.get(0) + ": " + e);
			}
		}
		if (batch.size() > 1) {
			System.out.print(".");
			printMemoryStatus();
		}
		return elementIds;
	}


	private List<String> queryNames(Element element) {
		List<String> queryNames = new ArrayList<>();
		for (Attribute attribute : element.getAttributes()) {
			if ("query name".equals(attribute.getOriginalAttributeName()))
				if ("".equals(attribute.getAttributeTypeId()) || "query name".equals(attribute.getAttributeTypeId())) {
					queryNames.add(attribute.getValue().toString());
				}
		}
		return queryNames;
	}


	public long getCreateListElementId(final Element element, final int sourceId, final String[] matchFields) throws SQLException {
		return getListElementId(element, sourceId, matchFields, true);
	}


	public long getListElementId(final Element element, final int sourceId, final String[] matchFields) throws SQLException {
		return getListElementId(element, sourceId, matchFields, false);
	}


	private long getListElementId(final Element element, final int sourceId, final String[] matchFields, final boolean create) throws SQLException {
		long listElementId = findListElementId(element, sourceId, matchFields);
		if (listElementId > 0) {
			saveElement(listElementId, element, sourceId);
			return listElementId;
		}
		if (create) {
			if (listElementId < 0 && element.getIdentifiers() != null && element.getIdentifiers().size() > 0) {
				listElementId = createListElement(element);
				if (listElementId > 0) {
					saveElement(listElementId, element, sourceId);
					return listElementId;
				}
			}
		}
		if (listElementId <= 0) {
			System.out.println("WARN: Not matched by identifiers: " + element.getId());
		}
		return -1;
	}


	public long findListElementId(final Element element, final int sourceId, final String[] matchFields) throws SQLException {
		final Date start = new Date();
		long listElementId = -1;
		if (matchFields == null || matchFields.length == 0 || (matchFields[0].equals("id"))) {
			final String fieldName = idFieldName(element);
			listElementId = db.listElementIdentifierTable.findParentId(fieldName, element.getId(), sourceId);
			if (listElementId <= 0) {
				listElementId = db.listElementIdentifierTable.findParentId(fieldName, element.getId());
			}
		}
		if (listElementId <= 0) {
			listElementId = findListElementId(element.getIdentifiers(), matchFields);
		}
		profile("find element", start);
		return listElementId;
	}


	private long createListElement(final Element element) throws SQLException {
		Date start = new Date();
		final long biolinkClassId = biolinkClassId(element.getBiolinkClass());
		profile("get biolink class id", start);
		long listElementId;
		String primaryName = element.getId();
		if (element.getNamesSynonyms() != null && element.getNamesSynonyms().size() > 0) {
			if (element.getNamesSynonyms().get(0).getName() != null) {
				primaryName = element.getNamesSynonyms().get(0).getName();
			}
			for (Names names : element.getNamesSynonyms()) {
				if ("primary name".equals(names.getNameType()) && names.getName() != null) {
					primaryName = names.getName();
				}
			}
		}
		listElementId = db.listElementTable.insert(primaryName, biolinkClassId);
		profile("save element", start);
		return listElementId;
	}


	private static String idFieldName(final Element element) {
		for (Map.Entry<String,Object> entry : element.getIdentifiers().entrySet())
			if (entry.getValue() != null) {
				for (String value : IdentifierTable.identifiers(entry.getValue()))
					if (element.getId().equals(value)) {
						return entry.getKey();
					}
			}
		System.err.println("WARN: Id not found among element identifiers: " + element.getId());
		System.err.println("  #connections: " + element.getConnections().size());
		for (apimodels.Connection connection : element.getConnections()) {
			System.err.println("  " + connection);
		}
		return null;
	}


	long findListElementId(Element element, String fieldName) throws SQLException {
		if (fieldName != null && element.getIdentifiers().containsKey(fieldName)) {
			for (String curie : IdentifierTable.identifiers(element.getIdentifiers().get(fieldName))) {
				long listElementId = db.listElementIdentifierTable.findParentId(fieldName, curie);
				if (listElementId > 0) {
					return listElementId;
				}
			}
			System.out.println("Not found " + fieldName + ": " + element.getIdentifiers().get(fieldName));
		}
		System.out.println("Check all identifiers " + element.getIdentifiers());
		return findListElementId(element.getIdentifiers(), null);
	}


	private long findListElementId(final Map<String,Object> identifiers, String[] matchFields) throws SQLException {
		long listElementId = -1;
		if (matchFields == null) {
			matchFields = identifiers.keySet().toArray(new String[0]);
		}
		for (String fieldName : matchFields) {
			for (String curie : IdentifierTable.identifiers(identifiers.get(fieldName))) {
				long newListElementId = db.listElementIdentifierTable.findParentId(fieldName, curie);
				listElementId = listElementId(listElementId, newListElementId, curie);
			}
		}
		return listElementId;
	}


	private static long listElementId(long listElementId, long newListElementId, String id) {
		if (listElementId == -1) {
			return newListElementId;
		}
		if (newListElementId == -1) {
			return listElementId;
		}
		if (listElementId != newListElementId) {
			System.err.println("WARN: Multiple list element matches " + id);
		}
		return listElementId;
	}


	private void saveElement(final long listElementId, final Element element, final int sourceId) throws SQLException {
		Date start = new Date();
		final long biolinkClassId = biolinkClassId(element.getBiolinkClass());
		profile("get biolink class id", start);
		db.listElementIdentifierTable.saveIdentifiers(listElementId, biolinkClassId, element, sourceId);
		profile("save element identifiers", start);
		start = new Date();
		if (element.getNamesSynonyms() != null) {
			for (Names names : element.getNamesSynonyms()) {
				db.listElementNameTable.saveNames(listElementId, sourceId, names);
			}
		}
		profile("save element names", start);
		start = new Date();
		if (element.getAttributes() != null) {
			// Save to the List_Element_Attribute Table, the cross reference between
			// List_Element and Attribute Tables.
			for (Attribute attribute : element.getAttributes()) {
				db.listElementAttributeTable.insert(listElementId, attribute, sourceId, true);
			}
		}
		profile("save element attributes", start);
	}


	/************************************************************************************
	 * Make an Element from an elementId
	 * 
	 * @return Element
	 * @throws SQLException
	 */
	Element element(long listElementId) throws SQLException {
		String id = MOLE_PRO_PREFIX + listElementId;
		HashMap<String,Object> identifiers = db.listElementIdentifierTable.getListElementIdentiers(listElementId);
		Element element = new Element();
		element.setId(id);
		element.setIdentifiers(identifiers);
		element.setBiolinkClass(db.listElementTable.getBiolinkClass(listElementId));
		element.setSource("MolePro");
		element.setProvidedBy("MolePro");
		return element;
	}

}
