package org.broadinstitute.translator.moleprodb.builder;

import java.io.BufferedReader;
import java.io.FileReader;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.broadinstitute.translator.moleprodb.db.MoleProDB;

import apimodels.Attribute;
import apimodels.Element;
import apimodels.Names;
import apimodels.Parameter;
import apimodels.Property;
import transformer.Transformer;
import transformer.TransformerQuery;
import transformer.Transformers;

public class ListElementLoader extends Loader {

	private static final int BATCH_SIZE = 100;


	public ListElementLoader(MoleProDB db) {
		super(db);
	}


	public void loadElements(final String transformerName, final String compoundFile, final Set<String> matchFields) throws Exception {
		Transformers.getTransformers();
		Transformer transformer = Transformers.getTransformer(transformerName);
		ArrayList<String> batch = new ArrayList<>();
		int i = 0;
		final BufferedReader input = new BufferedReader(new FileReader(compoundFile));
		try {
			input.readLine(); // header line
			for (String element = input.readLine(); element != null; element = input.readLine()) {

				batch.add(element);
				i = i + 1;
				if (i % BATCH_SIZE == 0) {
					System.out.println(element);
					loadElements(transformer, batch, matchFields);
					db.commit();
					System.out.println();
					batch = new ArrayList<>();
				}
				if (i % (10 * BATCH_SIZE) == 0) {
					System.out.println("db.reconnect");
					db.reconnect();
				}
			}
			loadElements(transformer, batch, matchFields);
			db.commit();
		}
		finally {
			db.rollback();
			input.close();
		}

	}


	private void loadElements(final Transformer transformer, final ArrayList<String> batch, final Set<String> matchFields) {
		final int sourceId = db.sourceTable.sourceId(transformer.info.getName());
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
			final TransformerQuery query = new TransformerQuery(controls);
			final Element[] elements = transform(transformer, query);
			for (Element element : elements) {
				if (element != null) {
					listElementId(element, sourceId, matchFields);
				}
			}
		}
		catch (Exception e) {
			if (batch.size() > 1) {
				System.err.println("INFO: batch load failed, trying single elements");
				final ArrayList<String> singleton = new ArrayList<String>(1);
				singleton.add(null);
				for (String element : batch) {
					singleton.set(0, element);
					loadElements(transformer, singleton, matchFields);
				}
			}
			else {
				System.err.println("WARNING: " + transformer.info.getName() + " failed to load " + batch.get(0) + ": " + e);
			}
		}
		if (batch.size() > 1) {
			System.out.print(".");

			StringBuilder status = new StringBuilder();
			status.append("free memory:" + Runtime.getRuntime().freeMemory() / 1000000);
			status.append("/" + Runtime.getRuntime().totalMemory() / 1000000);
			System.out.print(status.toString());
		}
	}


	public long listElementId(final Element element, final int sourceId, final Set<String> matchFields) throws SQLException {
		final long biolinkClassId = biolinkClassId(element.getBiolinkClass());
		Date start = new Date();
		long listElementId = db.listElementIdentifierTable.findParentId(biolinkClassId, idFieldName(element), element.getId(), sourceId);
		if (listElementId > 0) {
			profile("find element", start);
			return listElementId;
		}
		listElementId = db.listElementIdentifierTable.findParentId(biolinkClassId, idFieldName(element), element.getId());
		if (listElementId < 0) {
			listElementId = listElementId(biolinkClassId, element.getIdentifiers(), matchFields);
			if (listElementId < 0) {
				System.out.println("Not matched by identifiers: "+element.getId());
			}
		}
		profile("find element", start);

		if (listElementId > 0) {
			saveElement(listElementId, biolinkClassId, element, sourceId);
			return listElementId;
		}

		if (listElementId < 0 && element.getIdentifiers() != null && element.getIdentifiers().size() > 0) {
			listElementId = createListElement(element, biolinkClassId);
		}
		if (listElementId > 0) {
			saveElement(listElementId, biolinkClassId, element, sourceId);
			return listElementId;
		}

		return -1;
	}


	public long createListElement(final Element element, final long biolinkClassId) throws SQLException {
		long listElementId;
		String primaryName = element.getId();
		if (element.getNamesSynonyms() != null && element.getNamesSynonyms().size() > 0) {
			if (element.getNamesSynonyms().get(0).getName() != null) {
				primaryName = element.getNamesSynonyms().get(0).getName();
			}
		}
		listElementId = db.listElementTable.insert(primaryName, biolinkClassId);
		return listElementId;
	}


	@SuppressWarnings("rawtypes")
	private static String idFieldName(final Element element) {
		for (Map.Entry<String,Object> entry : element.getIdentifiers().entrySet())
			if (entry.getValue() != null) {
				if (entry.getValue() instanceof String) {
					if (element.getId().equals(entry.getValue())) {
						return entry.getKey();
					}
				}
				else if (entry.getValue() instanceof String[]) {
					for (String value : (String[])entry.getValue())
						if (element.getId().equals(value)) {
							return entry.getKey();
						}
				}
				else if (entry.getValue() instanceof ArrayList) {
					for (Object value : (ArrayList)entry.getValue())
						if (element.getId().equals(value)) {
							return entry.getKey();
						}
				}
				else {
					System.err.println("" + entry.getValue().getClass());
				}
			}
		System.err.println("WARN: Id not found among element identifiers: " + element.getId());
		return null;
	}


	long findListElementId(Element element, String fieldName) throws SQLException {
		if (fieldName != null && element.getIdentifiers().containsKey(fieldName)) {
			if (element.getIdentifiers().get(fieldName) instanceof String) {
				String curie = (String)element.getIdentifiers().get(fieldName);
				long listElementId =  db.listElementIdentifierTable.findParentId(fieldName, curie);
				if (listElementId > 0) {
					return listElementId;
				}
				else {
					System.out.println("Not found "+fieldName+": "+curie);
				}
			}
		}
		System.out.println("Check all identifiers "+element.getIdentifiers());
		return listElementId(0, element.getIdentifiers(), null);
	}


	@SuppressWarnings("rawtypes")
	private long listElementId(final long biolinkClassId, final Map<String,Object> identifiers, final Set<String> matchFields) throws SQLException {
		long listElementId = -1;
		for (Map.Entry<String,Object> entry : identifiers.entrySet())
			if (entry.getValue() != null) {
				final String fieldName = entry.getKey();
				if (matchFields == null || matchFields.contains(fieldName)) {
					if (entry.getValue() instanceof String) {
						final String curie = (String)entry.getValue();
						long newListElementId = db.listElementIdentifierTable.findParentId(biolinkClassId, fieldName, curie);
						listElementId = listElementId(listElementId, newListElementId, curie);
					}
					else if (entry.getValue() instanceof String[]) {
						for (String curie : (String[])entry.getValue()) {
							long newListElementId = db.listElementIdentifierTable.findParentId(biolinkClassId, fieldName, curie);
							listElementId = listElementId(listElementId, newListElementId, curie);
						}

					}
					else if (entry.getValue() instanceof ArrayList) {
						for (Object curie : (ArrayList)entry.getValue())
							if (curie != null) {
								if (curie instanceof String) {
									long newListElementId = db.listElementIdentifierTable.findParentId(biolinkClassId, fieldName, (String)curie);
									listElementId = listElementId(listElementId, newListElementId, (String)curie);
								}
								else {
									System.err.println("WARN: unexpected identifier type:" + curie.getClass());
								}
							}
					}
					else {
						System.err.println("WARN: unexpected identifier type:" + entry.getValue());
					}
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


	private void saveElement(final long listElementId, final long biolinkClassId, final Element element, final int sourceId) throws SQLException {
		Date start = new Date();
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
				db.listElementAttributeTable.insert(listElementId, attribute, sourceId);
			}
		}
		profile("save element attributes", start);
	}

}
