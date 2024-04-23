package org.broadinstitute.translator.moleprodb.db;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HashMap;

public class ListElementIdentifierTable extends IdentifierTable {

	public ListElementIdentifierTable(MoleProDB db) {
		super(db, "List_Element_Identifier", "element_identifier_id", "list_element_id");
	}


	/********************************************************
	 * 
	 * Obtain the list_element_id searched by primary name
	 * 
	 * @param primaryName
	 * @return
	 * @throws SQLException
	 */
	public HashMap<String,Object> getListElementIdentiers(Long listElementId) throws SQLException {

		String sql = "SELECT DISTINCT xref, mole_pro_prefix, field_name  FROM List_Element_Identifier ";
		sql = sql + "JOIN Curie_Prefix ON List_Element_Identifier.prefix_id = Curie_Prefix.prefix_id ";
		sql = sql + "WHERE list_element_id = '" + listElementId.toString() + "'";

		ResultSet results = this.executeQuery(sql);
		HashMap<String,Object> queryIdentifiers = new HashMap<String,Object>();
		while (results.next()) {
			final String fieldName = results.getString("field_name");
			String prefix = results.getString("mole_pro_prefix");
			String value = "";
			if (prefix != null && prefix.trim().length() > 0) {
				value = prefix + ":" + results.getString("xref");
			}
			else {
				value = results.getString("xref");
			}
			if (queryIdentifiers.get(fieldName) == null) {
				queryIdentifiers.put(fieldName, value);
			}
			//else {
			//	System.err.println("WARN: Multiple " + fieldName + " ids for " + listElementId);
			//}
		}
		return queryIdentifiers;
	}

}
