package org.broadinstitute.translator.moleprodb.db;

import java.sql.SQLException;
import java.util.List;

import apimodels.Qualifier;

public class QualifierSetTable extends MoleProTable {

	private long lastQualifierSetId = -1;


	public QualifierSetTable(MoleProDB db) {
		super(db, "Qualifier_Set");
	}


	private void insert(final long qualifierSetId) throws SQLException {
		String sql = "INSERT INTO Qualifier_Set (qualifier_set_id)\n";
		sql = sql + "VALUES (" + qualifierSetId + ")";
		executeUpdate(sql);
	}


	private long insert(final List<Qualifier> qualifiers) throws SQLException {
		if (lastQualifierSetId < 0) {
			lastQualifierSetId = lastId("qualifier_set_id");
		}
		lastQualifierSetId = lastQualifierSetId + 1;
		insert(lastQualifierSetId);
		db.qualifierMapTable.insert(lastQualifierSetId, qualifiers);
		return lastQualifierSetId;
	}


	public Long getQualifierSetId(final List<Qualifier> qualifiers) throws SQLException {
		if (qualifiers == null || qualifiers.size() == 0)
			return null;
		final long qualifierSetId = findQualifierSetId(qualifiers);
		if (qualifierSetId > 0) {
			return qualifierSetId;
		}
		return insert(qualifiers);
	}


	long findQualifierSetId(final List<Qualifier> qualifiers) {
		final String NL = "\n";
		String join = "";
		join += "JOIN (" + NL;
		join += "  SELECT qualifier_set_id, count(qualifier_id) AS count" + NL;
		join += "  FROM Qualifier_Map" + NL;
		join += "  GROUP BY qualifier_set_id" + NL;
		join += ") AS Qualifier_Count" + NL;
		join += "ON Qualifier_Count.qualifier_set_id = Qualifier_Set.qualifier_set_id" + NL;
		String where = "WHERE count = " + qualifiers.size() + NL;
		for (int i = 0; i < qualifiers.size(); i++) {
			Qualifier qualifier = qualifiers.get(i);
			join += "JOIN Qualifier_Map AS Qualifier_Map_" + i + " ON Qualifier_Map_" + i + ".qualifier_set_id = Qualifier_Set.qualifier_set_id" + NL;
			join += "JOIN Qualifier AS Qualifier_" + i + " ON Qualifier_" + i + ".qualifier_id = Qualifier_Map_" + i + ".qualifier_id" + NL;
			where += "AND Qualifier_" + i + ".qualifier_type = " + f(qualifier.getQualifierTypeId()) + NL;
			where += "AND Qualifier_" + i + ".qualifier_value = " + f(qualifier.getQualifierValue()) + NL;
		}
		return findId("Qualifier_Set.qualifier_set_id", join + where);
	}

}
