package org.broadinstitute.translator.moleprodb.db;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HashSet;

public class ElementHierarchyTable extends MoleProTable {

	public ElementHierarchyTable(MoleProDB db) {
		super(db, "List_Element_Hierarchy");
	}


	private void insert(final long listElementId, final long parentElementId, final String hierarchyType, final long connectionId) throws SQLException {
		String sql = "INSERT INTO " + tableName + " (list_element_id, parent_element_id, connection_id, hierarchy_type)\n";
		sql = sql + "VALUES (" + listElementId + "," + parentElementId + "," + connectionId + "," + f(hierarchyType) + ")";
		executeUpdate(sql);
	}


	private boolean find(final long listElementId, final long parentElementId, final String hierarchyType) {
		final String where = "WHERE list_element_id = " + listElementId + " AND parent_element_id = " + parentElementId + " AND hierarchy_type " + is(hierarchyType);
		final long elementHierarchyId = findId("element_hierarchy_id", where);
		return elementHierarchyId > 0;
	}


	public void saveHierarchy(final long listElementId, final long parentElementId, final String hierarchyType) throws SQLException {
		if (!find(listElementId, parentElementId, hierarchyType)) {
			insert(listElementId, parentElementId, hierarchyType, 0);
		}
	}


	public HashSet<Long> hierarchyDone() throws SQLException {
		String sql = "SELECT DISTINCT list_element_id FROM List_Element_Hierarchy";
		HashSet<Long> ids = new HashSet<>();
		ResultSet results = this.executeQuery(sql);
		while (results.next()) {
			ids.add(results.getLong("list_element_id"));
		}
		return ids;
	}

}
