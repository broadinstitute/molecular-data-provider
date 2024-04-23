package org.broadinstitute.translator.moleprodb.db;

import java.sql.SQLException;

public class NameTable extends MoleProTable {

	private long lastNameId = -1;


	public NameTable(MoleProDB db) {
		super(db, "Name");
	}


	private void insert(long id, String name) throws SQLException {
		String sql = "INSERT INTO Name (name_id, name)\n";
		sql = sql + "VALUES (" + id + "," + f(name) + ")";
		executeUpdate(sql);
	}


	private long insert(String name) throws SQLException {
		if (lastNameId < 0) {
			lastNameId = lastId("name_id");
		}
		lastNameId = lastNameId + 1;
		insert(lastNameId, name);
		return lastNameId;
	}


	public long nameId(final String name) throws SQLException {
		long nameId = findNameId(name);
		if (nameId <= 0) {
			nameId = insert(name);
		}
		return nameId;
	}


	private long findNameId(String name) {
		return findId("name_id", "name", name);
	}

}
