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
	private long insert(String uuid, long subjectId, long objectId, long predicateId, int sourceId) throws SQLException {
		if (lastConnectionId < 0) {
			lastConnectionId = lastId("connection_id");
		}
		lastConnectionId = lastConnectionId + 1;
		final long connectionId = lastConnectionId;
		String sql = "INSERT INTO Connection(connection_id, uuid, subject_id, object_id, predicate_id, source_id)\n";
		sql = sql + "VALUES (" + connectionId + "," + f(uuid) + "," + subjectId + "," + objectId + "," + predicateId + "," + sourceId + ")";
		executeUpdate(sql);
		return lastConnectionId;
	}


	public long connectionId(String uuid, long subjectId, long objectId, long predicateId, int sourceId) throws SQLException {
		final long connectionId = findConnectionId(subjectId, objectId, predicateId, sourceId);
		if (connectionId > 0) {
			return connectionId;
		}
		return insert(uuid, subjectId, objectId, predicateId, sourceId);
	}


	private long findConnectionId(final long subjectId, final long objectId, final long predicateId, final int sourceId) {
		final String where = "WHERE subject_id = " + subjectId + " AND object_id = " + objectId + " AND predicate_id = " + predicateId + " AND source_id = " + sourceId;
		return findId("connection_id", where);
	}


	public long lastConnectionId() throws SQLException {
		reset();
		return lastId("connection_id");
	}


	public String connectionQuery() {
		String sql = "SELECT connection_id, subject_id, object_id, source_id, biolink_predicate, inverse_predicate, relation, inverse_relation ";
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
