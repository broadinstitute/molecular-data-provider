package org.broadinstitute.translator.moleprodb.db;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class ConnectionTable extends MoleProTable {

	private long lastConnectionId = -1;

	private PreparedStatement connectionQuery;


	public ConnectionTable(MoleProDB db) {
		super(db, "Connection");
	}


	public void reset() throws SQLException {
		connectionQuery = db.prepareStatement(connectionQuery());
	}


	/*************************************************************
	 * 
	 * 
	 * @param subjectId
	 * @param objectId
	 * @param predicate_id
	 * @param source_id
	 * @throws SQLException
	 */
	private long insert(final String uuid, final long subjectId, final long objectId, final long predicateId, final Long qualifierSetId, final int sourceId) throws SQLException {
		if (lastConnectionId < 0) {
			lastConnectionId = lastId("connection_id");
		}
		lastConnectionId = lastConnectionId + 1;
		final long connectionId = lastConnectionId;
		String sql = "INSERT INTO Connection(connection_id, uuid, subject_id, object_id, predicate_id, qualifier_set_id, source_id)\n";
		sql = sql + "VALUES (" + connectionId + "," + f(uuid) + "," + subjectId + "," + objectId + "," + predicateId + "," + f(qualifierSetId) + "," + sourceId + ")";
		executeUpdate(sql);
		return lastConnectionId;
	}


	public long connectionId(final String uuid, final long subjectId, final long objectId, final long predicateId, final Long qualifierSetId, final int sourceId) throws SQLException {
		final long connectionId = findConnectionId(subjectId, objectId, predicateId, qualifierSetId, sourceId);
		if (connectionId > 0) {
			return connectionId;
		}
		return insert(uuid, subjectId, objectId, predicateId, qualifierSetId, sourceId);
	}


	private long findConnectionId(final long subjectId, final long objectId, final long predicateId, final Long qualifierSetId, final int sourceId) {
		final String where = "WHERE subject_id = " + subjectId + 
				" AND object_id = " + objectId + 
				" AND predicate_id = " + predicateId + 
				" AND qualifier_set_id " + is(qualifierSetId) + 
				" AND source_id = " + sourceId;
		return findId("connection_id", where);
	}


	public long lastConnectionId() throws SQLException {
		reset();
		return lastId("connection_id");
	}


	private boolean hasUUID() {
		try {
			final ResultSet results = this.executeQuery("pragma main.table_info('Connection');");
			while (results.next()) {
				if ("uuid".equals(results.getString("name"))) {
					return true;
				}
			}
		}
		catch (SQLException e) {
			System.out.println(e);
		}
		return false;
	}


	public String connectionQuery() {
		final String nullUUID = hasUUID() ? "" : "NULL AS ";
		String sql = "SELECT connection_id, " + nullUUID + "uuid, subject_id, object_id, source_id, biolink_predicate, inverse_predicate, relation, inverse_relation, qualifier_set_id ";
		sql = sql + " FROM " + tableName + "\n";
		sql = sql + " JOIN Predicate ON Predicate.predicate_id = " + tableName + ".predicate_id\n";
		sql = sql + " WHERE connection_id = ? AND source_id = ?";
		return sql;
	}


	public ResultSet getConnection(long connectionId, int inputSourceId) throws SQLException {
		connectionQuery.setLong(1, connectionId);
		connectionQuery.setLong(2, inputSourceId);
		return connectionQuery.executeQuery();
	}
}
