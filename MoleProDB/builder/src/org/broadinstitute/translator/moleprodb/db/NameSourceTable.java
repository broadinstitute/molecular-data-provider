package org.broadinstitute.translator.moleprodb.db;

import java.sql.SQLException;

public class NameSourceTable extends MoleProTable {

	private long lastNameSourceId = -1;


	public NameSourceTable(MoleProDB db) {
		super(db, "Name_Source");
	}


	private void insert(final long id, final String nameSource) throws SQLException {
		String sql = "INSERT INTO Name_Source (name_source_id, name_source)\n";
		sql = sql + "VALUES (" + id + "," + f(nameSource) + ")";
		executeUpdate(sql);
	}


	private long insert(final String nameSource) throws SQLException {
		if (lastNameSourceId < 0) {
			lastNameSourceId = lastId("name_source_id");
		}
		lastNameSourceId = lastNameSourceId + 1;
		insert(lastNameSourceId, nameSource);
		return lastNameSourceId;
	}


	public long nameSourceId(final String nameSource) throws SQLException {
		long nameSourceId = findNameSourceId(nameSource);
		if (nameSourceId <= 0) {
			nameSourceId = insert(nameSource);
		}
		return nameSourceId;
	}


	private long findNameSourceId(final String nameSource) {
		return findId("name_source_id", "name_source", nameSource);
	}

}
