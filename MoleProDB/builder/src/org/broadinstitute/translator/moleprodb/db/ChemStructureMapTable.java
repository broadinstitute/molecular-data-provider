package org.broadinstitute.translator.moleprodb.db;

import java.sql.SQLException;

public class ChemStructureMapTable extends MoleProTable {

	public ChemStructureMapTable(MoleProDB db) {
		super(db, "Chem_Structure_Map");
	}


	public void insert(final long substanceId, final long structureId, final boolean isCorrect) throws SQLException {
		final int correct = isCorrect ? 1 : 0;
		String sql = "INSERT INTO " + tableName + " (substance_id, structure_id, correct)\n";
		sql = sql + "VALUES (" + substanceId + "," + structureId + "," + correct + ")";
		executeUpdate(sql);
	}
}
