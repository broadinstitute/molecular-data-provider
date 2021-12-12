package org.broadinstitute.translator.moleprodb.db;

import java.sql.ResultSet;
import java.sql.SQLException;

public abstract class MoleProTable {

	protected final MoleProDB db;

	protected final String tableName;


	protected MoleProTable(MoleProDB db, String tableName) {
		this.db = db;
		this.tableName = tableName;
	}


	protected void executeUpdate(String sql) throws SQLException {
		db.executeUpdate(sql);
	}


	protected ResultSet executeQuery(String sql) throws SQLException {
		return db.executeQuery(sql);
	}


	/**
	 * Format java string for SQL WHERE clause
	 * 
	 * @return formated string
	 */
	protected String is(String str) {
		if (str == null) {
			return "IS NULL";
		}
		else {
			return "= " + f(str);
		}
	}


	/**
	 * Format java string for SQL
	 * 
	 * @return formated string
	 */
	protected String f(String str) {
		if (str == null) {
			return "NULL";
		}
		else {
			return "'" + str.replace("'", "''") + "'";
		}
	}


	/**
	 * Format java string for SQL
	 * 
	 * @return formated string
	 */
	protected String f(Long longValue) {
		if (longValue == null) {
			return "NULL";
		}
		else {
			return Long.toString(longValue);
		}
	}


	protected long lastId(String idColumn) {
		long lastSourceId = 0;
		String query = "SELECT max(" + idColumn + ") from " + this.tableName + ";";
		try {
			ResultSet results = this.executeQuery(query);
			if (results.next()) {
				lastSourceId = results.getLong(1);
			}
			results.close();
		}
		catch (SQLException e) {
			System.err.println("Failed to obtain max " + idColumn + ": " + e.getMessage());
		}
		return lastSourceId;
	}


	/**
	 * Find primary key for a given value.
	 * 
	 * @param idColumn
	 *            name of the primary key column
	 * @param valueColumn
	 *            name of the column
	 * @param value
	 * @return primary key
	 */
	protected long findId(String idColumn, String valueColumn, String value) {
		if (value == null) {
			return -1;
		}
		String where = " WHERE " + valueColumn + " = " + f(value) + ";";
		return findId(idColumn, where);
	}


	protected long findId(final String idColumn, final String where) {
		long id = -1;
		final String query = "SELECT DISTINCT " + idColumn + " FROM " + tableName + " " + where + ";";
		try {
			final ResultSet results = this.executeQuery(query);
			if (results.next()) {
				id = results.getLong(1);
			}
			if (results.next()) {
				System.err.println("WARN: Found multiple ids in " + idColumn + " " + where);
			}
			results.close();
		}
		catch (SQLException e) {
			System.err.println("WARN: Failed to obtain " + idColumn + " " + where + ": " + e.getMessage());
		}
		return id;
	}

}
