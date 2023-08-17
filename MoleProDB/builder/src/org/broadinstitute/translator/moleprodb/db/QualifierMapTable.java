package org.broadinstitute.translator.moleprodb.db;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.ArrayList;

import apimodels.Qualifier;

public class QualifierMapTable extends MoleProTable {

	private PreparedStatement qualifiersQuery;


	public QualifierMapTable(MoleProDB db) {
		super(db, "Qualifier_Map");
	}


	public void reset() throws SQLException {
		qualifiersQuery = db.prepareStatement(qualifiersQuery());
	}


	private void insert(final long qualifierSetId, final long qualifierId) throws SQLException {
		String sql = "INSERT INTO Qualifier_Map (qualifier_set_id, qualifier_id)\n";
		sql = sql + "VALUES (" + qualifierSetId + "," + qualifierId + ")";
		executeUpdate(sql);
	}


	void insert(final long qualifierSetId, final List<Qualifier> qualifiers) throws SQLException {
		for (Qualifier qualifier : qualifiers) {
			final long qualifierId = db.qualifierTable.getQualifierId(qualifier);
			insert(qualifierSetId, qualifierId);
		}
	}


	public List<Qualifier> getQualifiers(final long qualifierSetId) throws SQLException {
		qualifiersQuery.setLong(1, qualifierSetId);
		final ResultSet results = qualifiersQuery.executeQuery();
		final ArrayList<Qualifier> qualifiers = new ArrayList<>();
		while (results.next()) {
			Qualifier qualifier = new Qualifier();
			qualifier.setQualifierTypeId(results.getString("qualifier_type"));
			qualifier.setQualifierValue(results.getString("qualifier_value"));
			qualifiers.add(qualifier);
		}
		return qualifiers;
	}


	private String qualifiersQuery() {
		String sql = "SELECT qualifier_type, qualifier_value\n";
		sql = sql + "FROM Qualifier\n";
		sql = sql + "JOIN Qualifier_Map ON Qualifier_Map.qualifier_id = Qualifier.qualifier_id\n";
		sql = sql + "WHERE qualifier_set_id = ?";
		return sql;
	}

}
