package org.broadinstitute.translator.moleprodb.db;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import apimodels.Attribute;

public abstract class AttributeMapTable extends MoleProTable {

	private final String parentIdColumn;


	public AttributeMapTable(final MoleProDB db, final String tableName, final String parentIdColumn) {
		super(db, tableName);
		this.parentIdColumn = parentIdColumn;
	}


	protected void insert(final long parentId, final long attrTypeId, final long attributeId, final long sourceId) throws SQLException {
		String sql = "INSERT INTO " + tableName + " (" + parentIdColumn + ", attribute_type_id, attribute_id, source_id)\n";
		sql = sql + "VALUES (" + parentId + "," + attrTypeId + "," + attributeId + "," + sourceId + ")";
		executeUpdate(sql);
	}


	private boolean find(final long parentId, final long attrTypeId, final long attributeId, final long sourceId) throws SQLException {
		Date start = new Date();
		boolean found = false;
		if (attributeId > 0) {
			String query = "SELECT * FROM " + tableName + "\n";
			query = query + "WHERE " + parentIdColumn + " = " + parentId;
			query = query + " AND attribute_type_id = " + attrTypeId;
			query = query + " AND attribute_id = " + attributeId;
			query = query + " AND source_id = " + sourceId;
			final ResultSet results = this.executeQuery(query);
			if (results.next()) {
				found = true;
			}
			results.close();
		}
		profile("*save attributes - find", start);
		return found;
	}


	public void insert(final long parentId, final Attribute attribute, final long sourceId, boolean saveSubAttributes) throws SQLException {
		if ("biolink:aggregator_knowledge_source".equals(attribute.getAttributeTypeId())) {
			if ("infores:molepro".equals(attribute.getValue()))
				return;
			else
				saveSubAttributes = true;
		}
		Date start = new Date();
		final long attrTypeId = db.attributeTypeTable.getAttrTypeId(attribute, sourceId);
		profile("*get attribute type", start);
		start = new Date();
		final long attributeId = db.attributeTable.getAttributeId(attribute, sourceId, saveSubAttributes);
		profile("*get attribute id", start);
		saveAttribute(parentId, attrTypeId, attributeId, sourceId);
	}


	public void saveAttribute(final long parentId, final long attrTypeId, final long attributeId, final long sourceId) throws SQLException {
		if (!find(parentId, attrTypeId, attributeId, sourceId)) {
			Date start = new Date();
			insert(parentId, attrTypeId, attributeId, sourceId);
			profile("*save attribute - insert", start);
		}
	}


	public ArrayList<Attribute> getAttributes(final long parentId, final long sourceId) throws SQLException {
		Date start = new Date();
		String query = "SELECT attribute_type, attribute_name, attribute_value, value_type, \n";
		query = query + " source_name, url, Attribute.description, transformer, subattribute_id \n";
		query = query + "FROM " + tableName + "\n";
		query = query + "JOIN Attribute ON Attribute.attribute_id = " + tableName + ".attribute_id\n";
		query = query + "JOIN Attribute_Type ON Attribute_Type.attribute_type_id = " + tableName + ".attribute_type_id\n";
		query = query + "JOIN Source ON Source.source_id = " + tableName + ".source_id\n";
		query = query + "WHERE " + parentIdColumn + " = " + parentId;
		query = query + " AND Source.source_id = " + sourceId;
		final ResultSet results = this.executeQuery(query);
		final ArrayList<Attribute> attributes = new ArrayList<Attribute>();
		profile("* get attributes " + tableName, start);
		while (getNext(results)) {
			start = new Date();
			Attribute attribute = new Attribute();
			attribute.setAttributeTypeId(results.getString("attribute_type"));
			attribute.setOriginalAttributeName(results.getString("attribute_name"));
			attribute.setValue(results.getString("attribute_value"));
			attribute.setValueTypeId(results.getString("value_type"));
			attribute.setAttributeSource(results.getString("source_name"));
			attribute.setValueUrl(results.getString("url"));
			attribute.setDescription(results.getString("description"));
			attribute.setProvidedBy(results.getString("transformer"));
			profile("* get attributes " + tableName, start);
			List<Attribute> subattributes = getSubAttributes(getLong(results, "subattribute_id"), sourceId);
			attribute.setAttributes(subattributes);
			attributes.add(attribute);
		}
		results.close();
		return attributes;
	}


	private boolean getNext(final ResultSet results) throws SQLException {
		Date start = new Date();
		boolean next = results.next();
		profile("* get next attributes " + tableName, start);
		return next;
	}


	private List<Attribute> getSubAttributes(final Long parentId, final long sourceId) throws SQLException {
		if (parentId == null) {
			return null;
		}
		return db.parentAttributeTable.getAttributes(parentId, sourceId);
	}
}
