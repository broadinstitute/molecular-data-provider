package org.broadinstitute.translator.moleprodb.db;

import java.sql.SQLException;
import java.util.HashMap;

public class NameTypeTable extends MoleProTable {

	private static boolean dbHasPrimaryName = false;
	
	private long lastNameTypeId = -1;

	private HashMap<String,Long> nameTypeMap = new HashMap<>();


	public NameTypeTable(MoleProDB db) throws SQLException {
		super(db, "Name_Type");
	}


	private void insert(long id, String nameType, int namePriority) throws SQLException {
		String sql = "INSERT INTO Name_Type (name_type_id, name_type, name_priority)\n";
		sql = sql + "VALUES (" + id + "," + f(nameType) + "," + namePriority + ")";
		executeUpdate(sql);
	}


	private long insert(String nameType, int namePriority) throws SQLException {
		if (lastNameTypeId < 0) {
			lastNameTypeId = lastId("name_type_id");
		}
		lastNameTypeId = lastNameTypeId + 1;
		insert(lastNameTypeId, nameType, namePriority);
		nameTypeMap.put(nameType, lastNameTypeId);
		return lastNameTypeId;
	}


	private long findNameTypeId(String nameType) {
		if (nameTypeMap.containsKey(nameType)) {
			return nameTypeMap.get(nameType);
		}
		long id = findId("name_type_id", "name_type", nameType);
		nameTypeMap.put(nameType, id);
		return id;
	}

	private void checkPrimaryName() throws SQLException {
		if (dbHasPrimaryName) {
			return;
		}
		if (findNameTypeId("primary name") <= 0) {
			insert("primary name", 10);
		}
		if (findNameTypeId("synonym") <= 0) {
			insert("synonym", 200);
		}
		dbHasPrimaryName = true;
	}

	public long nameTypeId(String nameType) throws SQLException {
		checkPrimaryName();
		if (nameType == null || nameType.length() == 0) {
			nameType = "primary name";
		}
		long nameTypeId = findNameTypeId(nameType);
		if (nameTypeId <= 0) {
			nameTypeId = insert(nameType, 100);
		}
		return nameTypeId;
	}


	public long synonymTypeId(String nameType) throws SQLException {
		checkPrimaryName();
		if (nameType == null || nameType.length() == 0) {
			nameType = "synonym";
		}
		else {
			nameType = nameType + " synonym";
		}
		long nameTypeId = findNameTypeId(nameType);
		if (nameTypeId <= 0) {
			nameTypeId = insert(nameType, 300);
		}
		return nameTypeId;
	}

}
