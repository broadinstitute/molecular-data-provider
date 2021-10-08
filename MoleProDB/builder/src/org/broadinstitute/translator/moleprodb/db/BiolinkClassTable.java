package org.broadinstitute.translator.moleprodb.db;

import java.sql.SQLException;
import java.util.HashMap;

public class BiolinkClassTable extends MoleProTable {

	private long lastBiolinkClassId = -1;

	private final HashMap<String,Long> biolinkClassMap = new HashMap<>();


	public BiolinkClassTable(final MoleProDB db) {
		super(db, "Biolink_Class");
	}


	private void insert(final long id, final String biolinkClass) throws SQLException {
		String sql = "INSERT INTO Biolink_Class (biolink_class_id, biolink_class)\n";
		sql = sql + "VALUES (" + id + "," + f(biolinkClass) + ")";
		executeUpdate(sql);
		biolinkClassMap.put(biolinkClass, id);
	}


	private long insert(final String biolinkClass) throws SQLException {
		if (lastBiolinkClassId < 0) {
			lastBiolinkClassId = lastId("biolink_class_id");
		}
		lastBiolinkClassId = lastBiolinkClassId + 1;
		insert(lastBiolinkClassId, biolinkClass);
		return lastBiolinkClassId;
	}


	private long findBiolinkClassId(final String biolinkClass) {
		if (biolinkClassMap.containsKey(biolinkClass)) {
			return biolinkClassMap.get(biolinkClass);
		}
		long id = findId("biolink_class_id", "biolink_class", biolinkClass);
		biolinkClassMap.put(biolinkClass, id);
		return id;
	}
	
	public long biolinkClassId(final String biolinkClass) throws SQLException {
		final long biolinkClassId = findBiolinkClassId(biolinkClass);
		if (biolinkClassId > 0) {
			return biolinkClassId;
		}
		return insert(biolinkClass);
	}
}
