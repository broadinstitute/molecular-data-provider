package org.broadinstitute.translator.moleprodb.db;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import apimodels.Element;

public abstract class IdentifierTable extends MoleProTable {

	protected final String primaryKeyColumn;
	protected final String parentIdColumn;

	private long lastIdentifierId = -1;


	public IdentifierTable(final MoleProDB db, final String tableName, final String primaryKey, final String parentId) {
		super(db, tableName);
		this.primaryKeyColumn = primaryKey;
		this.parentIdColumn = parentId;
	}


	private void insert(final long id, final long parentId, final String xref, final long prefixId, final long sourceId) throws SQLException {
		String sql = "INSERT INTO " + tableName + " (" + primaryKeyColumn + ", " + parentIdColumn + ", xref, prefix_id, source_id)\n";
		sql = sql + "VALUES (" + id + "," + parentId + "," + f(xref) + "," + prefixId + "," + sourceId + ")";
		executeUpdate(sql);
	}


	private long insert(final long parentId, final String xref, final long prefixId, final long sourceId) throws SQLException {
		if (lastIdentifierId < 0) {
			lastIdentifierId = lastId(primaryKeyColumn);
		}
		lastIdentifierId = lastIdentifierId + 1;
		insert(lastIdentifierId, parentId, xref, prefixId, sourceId);
		return lastIdentifierId;
	}


	public void saveIdentifiers(final long listElementId, final long biolinkClassId, final Element element, final int sourceId) throws SQLException {
		for (Map.Entry<String,Object> entry : element.getIdentifiers().entrySet()) {
			final String fieldName = entry.getKey();
			for (String curie : identifiers(entry.getValue())) {
				final IdentifierTable.ParsedCurie parsedCurie = parseCurie(fieldName, curie);
				if (parsedCurie != null) {
					final long prefixId = db.curiePrefixTable.prefixId(biolinkClassId, parsedCurie.prefix, fieldName);
					saveIdentifier(listElementId, parsedCurie.xref, prefixId, sourceId);
				}
			}
		}
	}


	@SuppressWarnings("unchecked")
	public static Iterable<String> identifiers(Object entry) {
		if (entry != null) {
			if (entry instanceof String) {
				return Collections.singletonList((String)entry);

			}
			else if (entry instanceof String[]) {
				return Arrays.asList((String[])entry);

			}
			else if (entry instanceof ArrayList) {
				return (ArrayList<String>)entry;

			}
			else {
				System.err.println("WARN: unexpected identifier type: " + entry.getClass());
				return new ArrayList<String>();
			}
		}
		return new ArrayList<String>();
	}


	public void saveIdentifier(final long parentId, final String xref, final long prefixId, final long sourceId) throws SQLException {
		if (findIdentifierId(parentId, xref, prefixId, sourceId) <= 0) {
			insert(parentId, xref, prefixId, sourceId);
		}
	}


	private long findIdentifierId(final long parentId, final String xref, final long prefixId, final long sourceId) {
		final String where = "WHERE  " + parentIdColumn + "  = " + parentId + " AND xref = " + f(xref) + " AND prefix_id = " + prefixId + " AND source_id = " + sourceId + ";";
		return findId(primaryKeyColumn, where);
	}


	public long findParentId(final String fieldName, final String curie, final int sourceId) throws SQLException {
		final ParsedCurie parsedCurie = parseCurie(fieldName, curie);
		if (parsedCurie != null) {
			final String joinPrefix = " JOIN Curie_Prefix ON Curie_Prefix.prefix_id = " + tableName + ".prefix_id";
			final String where = " WHERE xref = " + f(parsedCurie.xref) + " AND mole_pro_prefix = " + f(parsedCurie.prefix) + " AND source_id = " + sourceId + ";";
			return findId(parentIdColumn, joinPrefix + where);
		}
		return -1;
	}


	public ArrayList<Long> findParentIds(final String curie, final long sourceId) throws SQLException {
		String[] prefixXref = curie.split(":");
		ArrayList<Long> ids = new ArrayList<>();
		if (prefixXref.length == 2) {
			final String prefix = prefixXref[0];
			final String xref = prefixXref[1];
			final String where = " WHERE xref = " + f(xref) + " AND biolink_prefix = " + f(prefix) + " AND source_id = " + sourceId + ";";
			final String join = " JOIN Curie_Prefix ON Curie_Prefix.prefix_id = " + tableName + ".prefix_id";
			final String query = "SELECT DISTINCT " + parentIdColumn + " FROM " + tableName + " " + join + " " + where + ";";
			final ResultSet results = this.executeQuery(query);
			while (results.next()) {
				ids.add(results.getLong(1));
			}
		}
		return ids;
	}


	public long findParentId(final String fieldName, final String curie) throws SQLException {
		final String joinPrefix = " JOIN Curie_Prefix ON Curie_Prefix.prefix_id = " + tableName + ".prefix_id";
		final String joinSource = " JOIN Source ON Source.source_id = " + tableName + ".source_id";
		final ParsedCurie parsedCurie = parseCurie(fieldName, curie);
		if (parsedCurie != null) {
			final String where = " WHERE xref = " + f(parsedCurie.xref) + " AND mole_pro_prefix = " + f(parsedCurie.prefix);
			final String whereInfores = " AND Source.infores_id = Curie_Prefix.infores_id";
			final long parentId = findId(parentIdColumn, joinPrefix + joinSource + where + whereInfores);
			if (parentId > 0) {
				return parentId;
			}
			return findId(parentIdColumn, joinPrefix + where);
		}
		return -1;
	}


	private ParsedCurie parseCurie(final String fieldName, final String curie) throws SQLException {
		if (curie == null || fieldName == null) {
			return null;
		}
		String xref = null;
		String moleProPrefix = "";
		if ("smiles".equals(fieldName) || "inchi".equals(fieldName) || "inchikey".equals(fieldName)) {
			xref = curie;
		}
		final String[] splitCurie = curie.split(":");
		if (splitCurie.length == 2) {
			moleProPrefix = splitCurie[0];
			xref = splitCurie[1];
		}
		if (xref != null) {
			return new ParsedCurie(moleProPrefix, xref);
		}
		return null;
	}


	public static class ParsedCurie {

		public final String prefix;

		public final String xref;


		private ParsedCurie(final String prefix, final String xref) {
			super();
			this.prefix = prefix;
			this.xref = xref;
		}
	}


	public Map<String,Object> getIdentifiers(final long parentId, final long sourceId, final String field) throws SQLException {

		String query = "SELECT DISTINCT field_name, mole_pro_prefix, xref\n";
		query = query + "FROM " + tableName + "\n";
		query = query + "JOIN Curie_Prefix ON Curie_Prefix.prefix_id = " + tableName + ".prefix_id\n";
		query = query + "JOIN Source ON Source.source_id = " + tableName + ".source_id\n";
		query = query + "WHERE " + parentIdColumn + " = " + parentId;
		if (field != null) {
			query = query + " AND Curie_Prefix.field_name = " + f(field);
		}
		if (sourceId >= 0) {
			query = query + " AND Source.source_id = " + sourceId;
		}
		return getIdentifiers(query);
	}


	@SuppressWarnings("unchecked")
	protected Map<String,Object> getIdentifiers(String query) throws SQLException {
		final ResultSet results = this.executeQuery(query);
		final HashMap<String,Object> identifiers = new HashMap<>();
		while (results.next()) {
			final String fieldName = results.getString("field_name");
			final String prefix = results.getString("mole_pro_prefix");
			final String xref = results.getString("xref");
			final String curie = (prefix.length() == 0) ? xref : prefix + ":" + xref;
			if (identifiers.containsKey(fieldName)) {
				if (identifiers.get(fieldName) instanceof String) {
					ArrayList<Object> ids = new ArrayList<Object>();
					ids.add(identifiers.get(fieldName));
					identifiers.put(fieldName, ids);
				}
				ArrayList<Object> ids = (ArrayList<Object>)identifiers.get(fieldName);
				ids.add(curie);
			}
			else {
				identifiers.put(fieldName, curie);
			}
		}
		return identifiers;
	}
}
