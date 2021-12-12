package org.broadinstitute.translator.moleprodb.db;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class ListElementTable extends MoleProTable {

	private long lastElementId = -1;


	public ListElementTable(MoleProDB db) {
		super(db, "List_Element");
	}


	/**************************************************
	 * 
	 * 
	 * @param id
	 * @param primaryName
	 * @param biolinkClassId
	 * @throws SQLException
	 */
	private void insert(long id, String primaryName, long biolinkClassId) throws SQLException {
		String sql = "INSERT INTO List_Element (list_element_id, primary_name, biolink_class_id)\n";
		sql = sql + "VALUES (" + id + "," + f(primaryName) + "," + biolinkClassId + ")";
		executeUpdate(sql);
	}


	/**************************************************
	 * 
	 * 
	 * @param primaryName
	 * @param biolinkClassId
	 * @return
	 * @throws SQLException
	 */
	public long insert(String primaryName, long biolinkClassId) throws SQLException {
		if (lastElementId < 0) {
			lastElementId = lastId("list_element_id");
		}
		lastElementId = lastElementId + 1;
		insert(lastElementId, primaryName, biolinkClassId);
		return lastElementId;
	}


	/***************************************************************
	 * 
	 * Get all the list-element ids of compounds (ChemicalSubstance)
	 * 
	 * @return
	 * @throws SQLException
	 */
	public ArrayList<Long> selectAll() throws SQLException {
		String sql = "SELECT list_element_id FROM List_Element";
		sql = sql + " JOIN Biolink_Class ON Biolink_Class.biolink_class_id = List_Element.biolink_class_id";
		sql = sql + " WHERE biolink_class = 'ChemicalSubstance';";
		ArrayList<Long> ids = new ArrayList<Long>();
		ResultSet results = this.executeQuery(sql);
		while (results.next()) {
			ids.add(results.getLong("list_element_id"));
		}
		return ids;
	}


	/********************************************************
	 * 
	 * Obtain all the list_element_ids searched by primary name
	 * 
	 * @param primaryName
	 * @return
	 */
	public List<Long> getListElementID(String primaryName) {
		List<Long> listElementIds = new ArrayList<Long>();
		String sql = "SELECT list_element_id FROM List_Element WHERE primary_name = '" + primaryName + "' ";
		try {
			ResultSet results = this.executeQuery(sql);
			while (results.next()) {
				listElementIds.add(results.getLong("list_element_id"));
			}
		}
		catch (SQLException e) {
			e.printStackTrace();
		}
		return listElementIds;
	}


	public String getBiolinkClass(final long elementId) throws SQLException {
		String biolinkClass = null;
		String sql = "SELECT biolink_class FROM List_Element\n";
		sql = sql + "JOIN Biolink_Class ON Biolink_Class.biolink_class_id = List_Element.biolink_class_id\n";
		sql = sql + "WHERE list_element_id = " + elementId + "; ";
		ResultSet results = this.executeQuery(sql);
		while (results.next()) {
			biolinkClass = results.getString("biolink_class");
		}
		results.close();
		return biolinkClass;
	}


	public long lastElementId() {
		return lastId("list_element_id");
	}
}
