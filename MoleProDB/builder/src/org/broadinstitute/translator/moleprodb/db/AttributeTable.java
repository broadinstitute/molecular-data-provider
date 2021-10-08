package org.broadinstitute.translator.moleprodb.db;

import java.sql.SQLException;

import apimodels.Attribute;

public class AttributeTable extends MoleProTable {

	private long lastAttributeId = -1;


	public AttributeTable(MoleProDB db) {
		super(db, "Attribute");
	}


	/*************************************
	 * Insert row in Attribute table
	 * 
	 * @param attributes
	 * @throws SQLException
	 */
	private void insert(final long attributeId, final long attrTypeId, final String attributeValue, final String url, final String description) throws SQLException {
		String sql = "INSERT INTO Attribute (attribute_id, attribute_type_id, attribute_value, url, description)\n";
		sql = sql + "VALUES (" + attributeId + "," + attrTypeId + "," + f(attributeValue) + "," + f(url) + "," + f(description) + ")";
		executeUpdate(sql);
	}


	long getAttributeId(final Attribute attribute) throws SQLException {
		final long attrTypeId = db.attributeTypeTable.getAttrTypeId(attribute.getOriginalAttributeName(), attribute.getAttributeTypeId(), attribute.getValueTypeId());
		if (attrTypeId < 0 || attribute.getValue() == null) {
			return -1;
		}
		final long attributeId = findAttributeId(attrTypeId, attribute.getValue().toString(), attribute.getValueUrl(), attribute.getDescription());
		if (attributeId > 0) {
			return attributeId;
		}
		if (lastAttributeId < 0) {
			lastAttributeId = lastId("attribute_id");
		}
		lastAttributeId = lastAttributeId + 1;
		insert(lastAttributeId, attrTypeId, attribute.getValue().toString(), attribute.getValueUrl(), attribute.getDescription());
		return lastAttributeId;
	}


	private long findAttributeId(final long attrTypeId, final String attributeValue, final String url, final String description) {
		String where = "WHERE attribute_type_id = " + attrTypeId 
				+ " AND attribute_value = " + f(attributeValue) 
				+ " AND url " + is(url)
				+ " AND description " + is(description) + ";";
		return findId("attribute_id", where);
	}

}
