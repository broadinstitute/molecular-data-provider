package org.broadinstitute.translator.moleprodb.db;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HashSet;

public class ElementHierarchyTable extends MoleProTable {

	public ElementHierarchyTable(MoleProDB db) {
		super(db, "Element_Hierarchy");
	}


	private void insert(final long listElementId, final long parentElementId) throws SQLException {
		String sql = "INSERT INTO " + tableName + " (list_element_id, parent_element_id)\n";
		sql = sql + "VALUES (" + listElementId + "," + parentElementId + ")";
		executeUpdate(sql);
	}


	private boolean find(final long listElementId, final long parentElementId) {
		final String where = "WHERE list_element_id = " + listElementId + " AND parent_element_id = " + parentElementId;
		final long elementHierarchyId = findId("element_hierarchy_id", where);
		return elementHierarchyId > 0;
	}


	public void saveHierarchy(final long listElementId, final long parentElementId) throws SQLException {
		if (!find(listElementId, parentElementId)) {
			insert(listElementId, parentElementId);
		}
	}


	public HashSet<Long> hierarchyDone() throws SQLException {
		String sql = "SELECT DISTINCT list_element_id FROM Element_Hierarchy";
		HashSet<Long> ids = new HashSet<>();
		ResultSet results = this.executeQuery(sql);
		while (results.next()) {
			ids.add(results.getLong("list_element_id"));
		}
		return ids;
	}

}
