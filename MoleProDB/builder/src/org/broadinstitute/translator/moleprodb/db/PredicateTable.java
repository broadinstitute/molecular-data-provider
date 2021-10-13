package org.broadinstitute.translator.moleprodb.db;

import java.sql.ResultSet;
import java.sql.SQLException;

public class PredicateTable extends MoleProTable {

	long lastPredicateId = -1;


	public PredicateTable(MoleProDB db) {
		super(db, "Predicate");
	}


	private void insert(final long predicateId, final String biolinkPredicate, final String inversePredicate, final String relation, final String inverseRelation) throws SQLException {
		String sql = "INSERT INTO Predicate(predicate_id, biolink_predicate, inverse_predicate, relation, inverse_relation)\n";
		sql = sql + "VALUES (" + predicateId + "," + f(biolinkPredicate) + "," + f(inversePredicate) + "," + f(relation) + "," + f(inverseRelation) + ")";
		executeUpdate(sql);
	}


	/***************************
	 * 
	 * 
	 * @param element
	 * @param biolinkPredicate
	 * @param relation
	 * @return
	 * @throws SQLException
	 */
	private long insert(final String biolinkPredicate, final String inversePredicate, final String relation, final String inverseRelation) throws SQLException {
		if (lastPredicateId < 0) {
			lastPredicateId = lastId("predicate_id");
		}
		lastPredicateId = lastPredicateId + 1;
		insert(lastPredicateId, biolinkPredicate, inversePredicate, relation, inverseRelation);
		return lastPredicateId;
	}


	public long predicateId(final String biolinkPredicate, final String inversePredicate, final String relation, final String inverseRelation) throws SQLException {
		long predicateId = findPredicateId(biolinkPredicate, relation);
		if (predicateId > 0) {
			return predicateId;
		}
		return insert(biolinkPredicate, inversePredicate, relation, inverseRelation);
	}


	/****************************
	 * 
	 * 
	 * @param relation
	 * @return
	 * @throws SQLException
	 */
	private long findPredicateId(final String biolinkPredicate, final String relation) {
		final String where = "WHERE relation = " + f(relation);
		final String query = "SELECT DISTINCT predicate_id, biolink_predicate FROM " + tableName + " " + where + ";";
		final String idColumn = "predicate_id";
		long id = -1;
		try {
			final ResultSet results = this.executeQuery(query);
			if (results.next()) {
				id = results.getLong("predicate_id");
				if (!results.getString("biolink_predicate").equals(biolinkPredicate)) {
					System.err.println("WARN: Different biolink predicate " + biolinkPredicate + " " + where);
				}
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
