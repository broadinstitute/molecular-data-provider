package org.broadinstitute.translator.moleprodb.db;

import java.sql.SQLException;

public class AttributeTypeTable extends MoleProTable {

	private long lastAttrTypeId = -1;


	public AttributeTypeTable(MoleProDB db) {
		super(db, "Attribute_Type");
	}


	private void insert(final long id, final String attrName, final String attrType, final String valueType) throws SQLException {
		String sql = "INSERT INTO Attribute_Type (attribute_type_id, attribute_name, attribute_type, value_type)\n";
		sql = sql + "VALUES (" + id + "," + f(attrName) + "," + f(attrType) + "," + f(valueType) + ")";
		executeUpdate(sql);
	}


	public long getAttrTypeId(final String attrName, final String attrType, final String valueType) throws SQLException {
		if (attrName == null) {
			return -1;
		}
		long attrTypeId = findAttrTypeId(attrName, (attrType == null) ? "" : attrType, valueType);
		if (attrTypeId > 0) {
			return attrTypeId;
		}
		if (lastAttrTypeId < 0) {
			lastAttrTypeId = lastId("attribute_type_id");
		}
		lastAttrTypeId = lastAttrTypeId + 1;
		insert(lastAttrTypeId, attrName, (attrType == null) ? "" : attrType, valueType);
		return lastAttrTypeId;
	}


	private long findAttrTypeId(final String attrName, final String attrType, final String valueType) {
		String where = "WHERE attribute_name = " + f(attrName) + "AND attribute_type " + is(attrType) + ";";
		return findId("attribute_type_id", where);
	}

}
