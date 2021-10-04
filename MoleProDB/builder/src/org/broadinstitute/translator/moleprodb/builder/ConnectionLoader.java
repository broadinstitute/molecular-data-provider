package org.broadinstitute.translator.moleprodb.builder;

import java.io.BufferedReader;
import java.io.FileReader;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;

import org.broadinstitute.translator.moleprodb.db.MoleProDB;

import apimodels.Attribute;
import apimodels.Connection;
import apimodels.Element;
import apimodels.Property;
import apimodels.TransformerInfo;
import transformer.Transformer;
import transformer.TransformerQuery;
import transformer.Transformers;

public class ConnectionLoader extends Loader {

	private static final String MOLE_PRO_PREFIX = "MolePro:";

	private static final int BATCH_SIZE = 10;

	private final ListElementLoader elementLoader;


	public ConnectionLoader(MoleProDB db) {
		super(db);
		elementLoader = new ListElementLoader(db);
	}


	/********************************************************
	 * 
	 * called by loadConnections(db, transformers, compounds)
	 * 
	 * @param db
	 * @param transformers
	 * @param compounds
	 * @throws Exception
	 */
	public void loadConnections(final String fieldName, final String compoundFile, final String transformerName) throws Exception {
		Transformers.getTransformers();
		final Transformer transformer = Transformers.getTransformer(transformerName);
		if (transformer.info.getFunction() == TransformerInfo.FunctionEnum.PRODUCER) {
			loadProducerConnections(fieldName, compoundFile, transformer);
		}
		else {
			loadTransformerConnections(fieldName, compoundFile, transformer);
		}
	}


	private void loadTransformerConnections(final String fieldName, final String compoundFile, final Transformer transformer) throws Exception {
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
				queryElements.add(queryElement(listElementId));
				if (queryElements.size() >= BATCH_SIZE) {
					loadConnections(transformer, queryElements);
					queryElements = new ArrayList<Element>();
					db.commit();
				}
			}
			else {
				System.out.println("WARN: element not found: " + id);
			}
			i = i + 1;
			if (i % 1000 == 0) {
				reconnect();
			}
		}
		if (queryElements.size() > 0) {
			loadConnections(transformer, queryElements);
			db.commit();
		}
		input.close();
	}


	private void reconnect() throws SQLException {
		db.reconnect();
		StringBuilder status = new StringBuilder();
		status.append("free memory:" + Runtime.getRuntime().freeMemory() / 1000000);
		status.append("/" + Runtime.getRuntime().totalMemory() / 1000000);
		System.out.println(status.toString());
	}


	private void loadProducerConnections(final String fieldName, final String compoundFile, final Transformer transformer) throws Exception {
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
					Element[] elements = super.transform(transformer, query);
					for (Element objectElement : elements) {
						final long objectElementId = elementLoader.listElementId(objectElement, sourceId, new HashSet<String>());
						saveConnections(objectElement, objectElementId, sourceId, subjectElementId);
					}
				}
				catch (Exception e) {
					System.out.println(e.toString());
					System.out.print(id);
				}
				i = i + 1;
				if (i % 10 == 0) {
					db.commit();
					if (i % 1000 == 0) {
						reconnect();
					}
				}
			}
			else {
				System.out.println("WARN: element not found: " + id);
			}
		}
		input.close();
	}


	private void loadConnections(Transformer transformer, ArrayList<Element> queryElements) {
		final int sourceId = db.sourceTable.sourceId(transformer.info.getName());
		try {
			// Run a transformer on the query element to obtain list of object elements
			Element[] elements = transform(transformer, queryElements);
			// Iterate through responses from the transformer and then
			// save all the object elements to the database
			for (Element objectElement : elements) {
				final long listElementId = elementLoader.listElementId(objectElement, sourceId, new HashSet<String>());
				if (listElementId > 0) {
					saveConnections(objectElement, listElementId, sourceId, -1);
				}
			}
		}
		catch (Exception e) {
			System.out.println(e.toString());
			for (Element element : queryElements) {
				System.out.print(element.getId() + "; ");
			}
			System.out.println();
		}
	}


	/************************************************************************************
	 * Make an ELEMENT FOR THE transform(Transformer, Element) method
	 * 
	 * @return
	 * @throws SQLException
	 */
	// query elements will be loaded from the database during production after
	// deployment
	private Element queryElement(long listElementId) throws SQLException {
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


	/*****************************************************************************
	 * 
	 * 
	 * @param transformer
	 * @param element
	 * @return
	 * @throws Exception
	 */
	private Element[] transform(Transformer transformer, ArrayList<Element> elements) throws Exception {

		List<Property> controls = new ArrayList<>();
		// ArrayList<Element> elements = new ArrayList<>();
		// elements.add(element);
		Property score = new Property(); // For Stitch Only
		score.setName("score_threshold"); // For Stitch Only
		score.setValue("150"); // For Stitch Only
		controls.add(score); // For Stitch Only
		Property limit = new Property(); // For Stitch Only
		limit.setName("limit"); // For Stitch Only
		limit.setValue("5"); // For Stitch Only
		controls.add(limit); // For Stitch Only

		TransformerQuery query = new TransformerQuery(controls, elements);
		return super.transform(transformer, query);

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
	public void saveConnections(final Element objectElement, final long objectId, final int sourceId, final long srcSubjectId) throws SQLException {
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
			if (subjectId <= 0 && connection.getSourceElementId().startsWith(MOLE_PRO_PREFIX)) {
				subjectId = Long.parseLong(connection.getSourceElementId().substring(MOLE_PRO_PREFIX.length()));
			}
			if (subjectId > 0) {
				// Save to the Connection Table
				start = new Date();
				long connectionId = db.connectionTable.connectionId(subjectId, objectId, predicateId, sourceId);
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
