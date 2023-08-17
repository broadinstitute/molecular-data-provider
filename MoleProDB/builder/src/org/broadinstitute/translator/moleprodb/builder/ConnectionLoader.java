package org.broadinstitute.translator.moleprodb.builder;

import java.io.BufferedReader;
import java.io.FileReader;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.UUID;

import org.broadinstitute.translator.moleprodb.db.MoleProDB;

import apimodels.Attribute;
import apimodels.Connection;
import apimodels.Element;
import apimodels.Property;
import apimodels.TransformerInfo;
import transformer.TransformerQuery;
import transformer.Transformers;

public class ConnectionLoader extends Loader {

	private static final int BATCH_SIZE = 5;

	private final ListElementLoader elementLoader;


	public ConnectionLoader(MoleProDB db) {
		super(db);
		elementLoader = new ListElementLoader(db);
	}


	/********************************************************
	 * 
	 * Load collections
	 * 
	 * @param db
	 * @param transformers
	 * @param compounds
	 * @throws Exception
	 */
	public void loadConnections(final String fieldName, final String compoundFile, final String transformerName, final String[] matchFields) throws Exception {
		Transformers.getTransformers();
		final TransformerRun transformer = new TransformerRun(transformerName);
		if (transformer.info.getFunction() == TransformerInfo.FunctionEnum.PRODUCER) {
			loadProducerConnections(fieldName, compoundFile, transformer, true, matchFields);
		}
		else {
			loadTransformerConnections(fieldName, compoundFile, transformer, true, matchFields);
		}
	}


	public void addConnections(final String fieldName, final String compoundFile, final String transformerName, final String[] matchFields) throws Exception {
		Transformers.getTransformers();
		final TransformerRun transformer = new TransformerRun(transformerName);
		if (transformer.info.getFunction() == TransformerInfo.FunctionEnum.PRODUCER) {
			loadProducerConnections(fieldName, compoundFile, transformer, false, matchFields);
		}
		else {
			loadTransformerConnections(fieldName, compoundFile, transformer, false, matchFields);
		}
	}


	private void loadTransformerConnections(final String fieldName, final String compoundFile, final TransformerRun transformer, final boolean createObject, final String[] matchFields) throws Exception {
		ArrayList<Element> queryElements = new ArrayList<Element>();

		// Loop through all given compound names
		final BufferedReader input = new BufferedReader(new FileReader(compoundFile));
		input.readLine(); // header line
		int i = 0;
		for (String id = input.readLine(); id != null; id = input.readLine()) {
			/****************************************************************************
			 * Build a query element with each ChemicalSubstance (i.e., biolink_class_id =
			 * 1) in the List_Element, List_Element_Identifier & Curie_Prefix Tables
			 */
			long listElementId = db.listElementIdentifierTable.findParentId(fieldName, id);
			if (listElementId > 0) {
				queryElements.add(elementLoader.element(listElementId));
				if (queryElements.size() >= BATCH_SIZE) {
					loadConnections(transformer, queryElements, createObject, matchFields);
					queryElements = new ArrayList<Element>();
					db.commit();
				}
			}
			else {
				System.out.println("WARN: element not found: " + id);
			}
			i = i + 1;
			if (i % 100 == 0) {
				printMemoryStatus(i + "\n");
			}
			if (i % 100 == 0) {
				db.reconnect();
			}
			if (i % 10000 == 0) {
				Loader.profileReport();
			}
		}
		if (queryElements.size() > 0) {
			loadConnections(transformer, queryElements, createObject, matchFields);
			db.commit();
		}
		input.close();
	}


	private void loadProducerConnections(final String fieldName, final String compoundFile, final TransformerRun transformer, final boolean createObject, final String[] matchFields) throws Exception {
		final int sourceId = db.sourceTable.sourceId(transformer.info.getName());
		final List<Property> controls = new ArrayList<>();
		final Property control = new Property().name(transformer.info.getParameters().get(0).getName());
		controls.add(control);
		final BufferedReader input = new BufferedReader(new FileReader(compoundFile));
		input.readLine(); // header line
		int i = 0;
		for (String id = input.readLine(); id != null; id = input.readLine()) {
			final long subjectElementId = db.listElementIdentifierTable.findParentId(fieldName, id);
			if (subjectElementId > 0) {
				control.setValue(id);
				try {
					TransformerQuery query = new TransformerQuery(controls, new ArrayList<Element>());
					Element[] elements = super.transform(transformer.transformer, query);
					saveConnections(elements, sourceId, subjectElementId, createObject, matchFields);
				}
				catch (Exception e) {
					System.out.println(e.toString());
					System.out.print(id);
				}
				i = i + 1;
				if (i % 10 == 0) {
					db.commit();
					if (i % 100 == 0) {
						printMemoryStatus(i + "\n");
					}
					if (i % 1000 == 0) {
						db.reconnect();
					}
				}
				if (i % 10000 == 0) {
					Loader.profileReport();
				}
			}
			else {
				System.out.println("WARN: element not found: " + id);
			}
		}
		input.close();
	}


	private void loadConnections(TransformerRun transformer, ArrayList<Element> queryElements, final boolean createObject, final String[] matchFields) {
		final int sourceId = db.sourceTable.sourceId(transformer.info.getName());
		try {
			// Run a transformer on the query element to obtain list of object elements
			Element[] elements = transform(transformer, queryElements);
			// Iterate through responses from the transformer and then
			// save all the object elements to the database
			saveConnections(elements, sourceId, -1, createObject, matchFields);
		}
		catch (Exception e) {
			System.out.println(e.toString());
			for (Element element : queryElements) {
				System.out.print(element.getId() + "; ");
			}
			System.out.println();
		}
	}


	/*****************************************************************************
	 * 
	 * 
	 * @param transformer
	 * @param element
	 * @return
	 * @throws Exception
	 */
	private Element[] transform(TransformerRun transformer, ArrayList<Element> elements) throws Exception {
		TransformerQuery query = new TransformerQuery(transformer.controls(), elements);
		return super.transform(transformer.transformer, query);
	}


	private void saveConnections(final Element[] elements, final int sourceId, final long subjectElementId, final boolean createObject, final String[] matchFields) throws SQLException {
		for (Element objectElement : elements) {
			final long objectElementId = objectElementId(objectElement, sourceId, createObject, matchFields);
			if (objectElementId > 0) {
				saveConnections(null, objectElement, objectElementId, sourceId, subjectElementId);
			}
		}
	}


	private long objectElementId(final Element objectElement, final int sourceId, final boolean createObject, final String[] matchFields) throws SQLException {
		if (createObject) {
			return elementLoader.getCreateListElementId(objectElement, sourceId, matchFields);
		}
		else {
			return elementLoader.getListElementId(objectElement, sourceId, matchFields);
		}
	}


	/*************************************************************************
	 * 
	 * Called by loadConnections() method to save each object element provided by
	 * transformers. The following tables are populated. - Name Table -
	 * List_Element_Name Table - List_Element_Identifier Table -
	 * List_Element_Attribute Table - Attribute Table - Predicate Table
	 * 
	 * @param db
	 * @param objectElement
	 * @param sourceId
	 * @throws SQLException
	 */
	public void saveConnections(final String srcUUID, final Element objectElement, final long objectId, final int sourceId, final long srcSubjectId) throws SQLException {
		for (Connection connection : objectElement.getConnections()) {
			// Save to the Predicate Table and get ID

			Date start = new Date();
			final String predicate = connection.getBiolinkPredicate();
			final String inversePredicate = connection.getInversePredicate();
			String relation = connection.getRelation();
			if (relation == null) {
				relation = predicate;
			}
			String inverseRelation = connection.getInverseRelation();
			if (inverseRelation == null) {
				inverseRelation = inversePredicate;
			}
			final long predicateId = db.predicateTable.predicateId(predicate, inversePredicate, relation, inverseRelation);
			profile("find predicate", start);

			long subjectId = srcSubjectId;
			if (subjectId <= 0 && connection.getSourceElementId().startsWith(ListElementLoader.MOLE_PRO_PREFIX)) {
				subjectId = Long.parseLong(connection.getSourceElementId().substring(ListElementLoader.MOLE_PRO_PREFIX.length()));
			}
			if (subjectId > 0) {
				String uuid = (srcUUID == null) ? UUID.randomUUID().toString() : srcUUID;
				// Save to the Connection Table
				start = new Date();
				final Long qualifierSetId = db.qualifierSetTable.getQualifierSetId(connection.getQualifiers());
				profile("qualifiers", start);
				start = new Date();
				final long connectionId = db.connectionTable.connectionId(uuid, subjectId, objectId, predicateId, qualifierSetId, sourceId);
				profile("save connection", start);

				// Save to the Connection_Attribute Table
				start = new Date();
				saveConnectionAttributes(db, connectionId, connection, sourceId);
				profile("save connection attributes", start);
			}
		}
	}


	/****************************************************************************
	 * Save Connection Attributes
	 * 
	 * 
	 * @param db
	 * @param connectionId
	 * @param attributes
	 * @param sourceId
	 * @throws SQLException
	 */
	private static void saveConnectionAttributes(final MoleProDB db, final long connectionId, final Connection connection, final int sourceId) throws SQLException {
		for (Attribute attribute : connection.getAttributes()) {
			db.connectionAttributeTable.insert(connectionId, attribute, sourceId);
		}
	}

}
