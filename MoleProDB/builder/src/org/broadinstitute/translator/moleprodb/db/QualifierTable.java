package org.broadinstitute.translator.moleprodb.db;

import java.sql.SQLException;

import apimodels.Qualifier;

public class QualifierTable extends MoleProTable {

	private final String PRIMARY_KEY = "qualifier_id";

	private long lastQualifierId = -1;


	public QualifierTable(MoleProDB db) {
		super(db, "Qualifier");
	}


	private void insert(final long id, final String qualifierType, final String qualifierValue) throws SQLException {
		String sql = "INSERT INTO Qualifier (qualifier_id, qualifier_type, qualifier_value)\n";
		sql = sql + "VALUES (" + id + "," + f(qualifierType) + "," + f(qualifierValue) + ")";
		executeUpdate(sql);
	}


	private long insert(final Qualifier qualifier) throws SQLException {
		if (lastQualifierId < 0) {
			lastQualifierId = lastId(PRIMARY_KEY);
		}
		lastQualifierId = lastQualifierId + 1;
		insert(lastQualifierId, qualifier.getQualifierTypeId(), qualifier.getQualifierValue());
		return lastQualifierId;
	}


	public long getQualifierId(final Qualifier qualifier) throws SQLException {
		final long qualifierId = findQualifierId(qualifier);
		if (qualifierId > 0) {
			return qualifierId;
		}
		return insert(qualifier);
	}


	private long findQualifierId(final Qualifier qualifier) {
		final String where = "WHERE qualifier_type = " + f(qualifier.getQualifierTypeId());
		final String and = " AND qualifier_value = " + f(qualifier.getQualifierValue());
		return findId(PRIMARY_KEY, where + and);
	}
}
