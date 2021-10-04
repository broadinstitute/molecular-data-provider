package org.broadinstitute.translator.moleprodb.builder;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.broadinstitute.translator.moleprodb.db.MoleProDB;

import apimodels.Attribute;
import apimodels.Connection;
import apimodels.Element;
import apimodels.Names;
import apimodels.TransformerInfo;
import transformer.Transformers;
import transformer.classes.Other;

public class MoleProDBMerger extends Loader {

	public MoleProDBMerger(MoleProDB db) {
		super(db);
	}


	public void mergeStructures(final String transformer, final MoleProDB srcDB) throws Exception {
		Transformers.getTransformers();
		final TransformerInfo transformerInfo = Transformers.getTransformer(transformer).info;
		final StructureLoader loader = new StructureLoader(db);
		final int sourceId = srcDB.sourceTable.sourceId(transformer);
		final long lastStructureId = srcDB.chemStructureTable.lastStructureId();
		for (long structureId = 1; structureId <= lastStructureId; structureId++) {
			final Element structure = getStructure(srcDB, structureId, sourceId);
			if (structure != null) {
				Other.mapElement(transformerInfo, structure);
				loader.save(sourceId, structure);
			}
			if (structureId % 100 == 0) {
				db.commit();
				db.reconnect();
				srcDB.reconnect();
				printMemoryStatus();
			}
		}
		db.commit();
	}


	private Element getStructure(final MoleProDB srcDB, final long structureId, final long sourceId) throws SQLException {
		final Date start = new Date();
		final Element element = new Element();
		final String biolinkClass = srcDB.chemStructureIdentifierTable.getBiolinkClass(structureId, sourceId);
		element.setBiolinkClass(biolinkClass);
		final Map<String,Object> identifiers = srcDB.chemStructureIdentifierTable.getIdentifiers(structureId, sourceId);
		if (biolinkClass == null || identifiers.size() == 0) {
			profile("get structure", start);
			return null;
		}
		element.setIdentifiers(identifiers);
		final List<Names> names = srcDB.chemStructureNameTable.getNames(structureId, sourceId);
		element.setNamesSynonyms(names);
		final List<Attribute> attributes = srcDB.chemStructureAttributeTable.getAttributes(structureId, sourceId);
		element.setAttributes(attributes);
		profile("get structure", start);
		return element;
	}


	public void mergeElements(String transformer, MoleProDB srcDB, final Set<String> matchFields) throws Exception {
		Transformers.getTransformers();
		final TransformerInfo transformerInfo = Transformers.getTransformer(transformer).info;
		final ListElementLoader loader = new ListElementLoader(db);
		final int sourceId = srcDB.sourceTable.sourceId(transformer);
		final long lastElementId = srcDB.listElementTable.lastElementId();
		long count = 0;
		for (long elementId = 1; elementId < lastElementId; elementId++) {
			final Date start = new Date();
			final Element element = getElement(srcDB, elementId, sourceId);
			profile("get element", start);
			if (element != null) {
				Other.mapElement(transformerInfo, element);
				loader.listElementId(element, sourceId, matchFields);
				count++;
				if (count % 100 == 0) {
					db.commit();
					db.reconnect();
					srcDB.reconnect();
					printMemoryStatus();
				}
			}
		}
		System.out.println("Merged " + count + " elements");
		db.commit();
	}


	private Element getElement(final MoleProDB srcDB, final long elementId, final long sourceId) throws SQLException {
		final Element element = createElement(srcDB, elementId, sourceId, null);
		if (element != null) {
			final List<Names> names = srcDB.listElementNameTable.getNames(elementId, sourceId);
			element.setNamesSynonyms(names);
			final List<Attribute> attributes = srcDB.listElementAttributeTable.getAttributes(elementId, sourceId);
			element.setAttributes(attributes);
		}
		return element;
	}


	private Element createElement(final MoleProDB srcDB, final long elementId, final long sourceId, final String field) throws SQLException {
		if (elementId <= 0) {
			return null;
		}
		final Map<String,Object> identifiers = srcDB.listElementIdentifierTable.getIdentifiers(elementId, sourceId, field);
		if (identifiers.size() == 0) {
			return null;
		}
		final Element element = new Element();
		element.setIdentifiers(identifiers);
		final String biolinkClass = srcDB.listElementTable.getBiolinkClass(elementId);
		element.setBiolinkClass(biolinkClass);
		return element;
	}


	public void mergeConnections(final String transformer, final String field, final MoleProDB srcDB, final String idField) throws Exception {
		Transformers.getTransformers();
		final TransformerInfo transformerInfo = Transformers.getTransformer(transformer).info;

		final long lastConnectionId = srcDB.connectionTable.lastConnectionId();
		final ListElementLoader elementLoader = new ListElementLoader(db);
		final ConnectionLoader connectionLoader = new ConnectionLoader(db);
		final int outputSourceId = db.sourceTable.sourceId(transformer);
		long count = 0;
		for (long connectionId = 1; connectionId < lastConnectionId; connectionId++) {
			final Date start = new Date();
			final Triple triple = getTriple(srcDB, connectionId, field, transformerInfo, idField);
			profile("get connection", start);
			if (triple != null) {
				final long subjectElementId = elementLoader.findListElementId(triple.subjectElement, field);
				final long objectElementId = elementLoader.findListElementId(triple.objectElement, idField);
				Other.mapElement(transformerInfo, triple.objectElement);
				if (objectElementId > 0 && subjectElementId > 0) {
					connectionLoader.saveConnections(triple.objectElement, objectElementId, outputSourceId, subjectElementId);
					count++;
				}
				else {
					System.out.println("Connection not matched: " + connectionId);
					System.out.println(triple.subjectElement.getIdentifiers() + " => " + subjectElementId);
					System.out.println(triple.connection.getBiolinkPredicate());
					System.out.println(triple.objectElement.getIdentifiers() + " => " + objectElementId);
				}
				if (count % 100 == 0) {
					db.commit();
					db.reconnect();
					srcDB.reconnect();
					srcDB.connectionTable.reset();
					printMemoryStatus(connectionId + ": ");
				}
			}
		}
		db.commit();
		System.out.println("Merged " + count + " connections");
	}


	private Triple getTriple(final MoleProDB srcDB, final long connectionId, final String field, final TransformerInfo transformerInfo, final String idField) throws SQLException {
		final int inputSourceId = srcDB.sourceTable.sourceId(transformerInfo.getName());
		final ResultSet results = srcDB.connectionTable.getConnection(connectionId, inputSourceId);
		Triple triple = null;
		while (results.next()) {
			final Element subjectElement = createElement(srcDB, results.getLong("subject_id"), -1, field);
			final Connection connection = createConnection(srcDB, results, inputSourceId, transformerInfo);
			final Element objectElement = createElement(srcDB, results.getLong("object_id"), inputSourceId, null);
			if (idField != null && objectElement != null && objectElement.getIdentifiers() != null) {
				if (objectElement.getIdentifiers().containsKey(idField))
					objectElement.setId(objectElement.getIdentifiers().get(idField).toString());
			}

			if (subjectElement != null && connection != null && objectElement != null) {
				triple = new Triple(subjectElement, connection, objectElement);
				triple.objectElement.setConnections(triple.connections());
			}
			else {
				System.out.println("Connection not loaded: " + connectionId);
				System.out.println(subjectElement);
				System.out.println(connection.getBiolinkPredicate());
				System.out.println(objectElement);
			}
		}
		return triple;
	}


	private Connection createConnection(final MoleProDB srcDB, final ResultSet result, final int inputSourceId, final TransformerInfo transformerInfo) throws SQLException {
		final Connection connection = new Connection();
		connection.setBiolinkPredicate(result.getString("biolink_predicate"));
		connection.setInversePredicate(result.getString("inverse_predicate"));
		connection.setRelation(result.getString("relation"));
		connection.setInverseRelation(result.getString("inverse_relation"));
		connection.setProvidedBy(transformerInfo.getName());
		connection.setSource(transformerInfo.getLabel());
		final List<Attribute> attributes = srcDB.connectionAttributeTable.getAttributes(result.getLong("connection_id"), inputSourceId);
		connection.setAttributes(attributes);
		return connection;
	}


	private static class Triple {

		final Element subjectElement;
		final Connection connection;
		final Element objectElement;


		Triple(Element subjectElement, Connection connection, Element objectElement) {
			super();
			this.subjectElement = subjectElement;
			this.connection = connection;
			this.objectElement = objectElement;
		}


		ArrayList<Connection> connections() {
			ArrayList<Connection> connections = new ArrayList<>();
			connections.add(connection);
			return connections;
		}
	}

}
