package org.broadinstitute.translator.moleprodb.db;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Date;

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
	 * Format java string for SQL WHERE clause
	 * 
	 * @return formated string
	 */
	protected String is(Long longValue) {
		if (longValue == null) {
			return "IS NULL";
		}
		else {
			return "= " + f(longValue);
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
	protected String f(boolean value) {
		return value ? "1" : "0";
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


	/**
	 * Return long value, distinguishing null result. 
	 *  
	 */
	protected Long getLong(final ResultSet result, final String column) throws SQLException {
		final long value = result.getLong(column);
		if (result.wasNull()) {
			return null;
		}
		return value;
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
		final String query = "SELECT DISTINCT " + idColumn + " FROM " + tableName + " " + where + ";";
		return findId(query);
	}


	protected long findId(final String query) {
		long id = -1;
		try {
			final ResultSet results = this.executeQuery(query);
			if (results.next()) {
				id = results.getLong(1);
			}
			if (results.next()) {
				System.err.println("WARN: Found multiple ids in " + query);
			}
			results.close();
		}
		catch (SQLException e) {
			System.err.println("WARN: Failed to obtain " + query + ": " + e.getMessage());
		}
		return id;
	}


	protected static void profile(final String transformerName, final Date start) {
		MoleProDB.profile(transformerName, start);
	}
}
