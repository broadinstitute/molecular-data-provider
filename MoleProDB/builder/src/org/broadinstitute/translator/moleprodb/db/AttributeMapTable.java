package org.broadinstitute.translator.moleprodb.db;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Date;

import org.broadinstitute.translator.moleprodb.builder.Loader;
import apimodels.Attribute;

public abstract class AttributeMapTable extends MoleProTable {

	private final String parentIdColumn;


	public AttributeMapTable(final MoleProDB db, final String tableName, final String parentIdColumn) {
		super(db, tableName);
		this.parentIdColumn = parentIdColumn;
	}


	private void insert(final long parentId, final long attributeId, final long sourceId) throws SQLException {
		String sql = "INSERT INTO " + tableName + " (" + parentIdColumn + ", attribute_id, source_id)\n";
		sql = sql + "VALUES (" + parentId + "," + attributeId + "," + sourceId + ")";
		executeUpdate(sql);
	}


	private boolean find(final long parentId, final long attributeId, final long sourceId) throws SQLException {
		Date start = new Date();
		boolean found = false;
		if (attributeId > 0) {
			String query = "SELECT * FROM " + tableName + "\n";
			query = query + "WHERE " + parentIdColumn + " = " + parentId;
			query = query + " AND attribute_id = " + attributeId;
			query = query + " AND source_id = " + sourceId;
			final ResultSet results = this.executeQuery(query);
			if (results.next()) {
				found = true;
			}
			results.close();
		}
		Loader.profile("save attributes - find", start);
		return found;
	}


	public void insert(final long parentId, final Attribute attribute, final long sourceId) throws SQLException {
		final long attributeId = db.attributeTable.getAttributeId(attribute);
		saveAttribute(parentId, sourceId, attributeId);
	}


	public void saveAttribute(final long parentId, final long sourceId, final long attributeId) throws SQLException {
		if (!find(parentId, attributeId, sourceId)) {
			insert(parentId, attributeId, sourceId);
		}
	}


	public ArrayList<Attribute> getAttributes(final long parentId, final long sourceId) throws SQLException {
		String query = "SELECT attribute_type, attribute_name, attribute_value, value_type, \n";
		query = query + " source_name, url, description, transformer \n";
		query = query + "FROM " + tableName + "\n";
		query = query + "JOIN Attribute ON Attribute.attribute_id = " + tableName + ".attribute_id\n";
		query = query + "JOIN Attribute_Type ON Attribute_Type.attribute_type_id = Attribute.attribute_type_id\n";
		query = query + "JOIN Source ON Source.source_id = " + tableName + ".source_id\n";
		query = query + "WHERE " + parentIdColumn + " = " + parentId;
		query = query + " AND Source.source_id = " + sourceId;
		final ResultSet results = this.executeQuery(query);
		final ArrayList<Attribute> attributes = new ArrayList<Attribute>();
		while (results.next()) {
			Attribute attribute = new Attribute();
			attribute.setAttributeTypeId(results.getString("attribute_type"));
			attribute.setOriginalAttributeName(results.getString("attribute_name"));
			attribute.setValue(results.getString("attribute_value"));
			attribute.setValueTypeId(results.getString("value_type"));
			attribute.setAttributeSource(results.getString("source_name"));
			attribute.setValueUrl(results.getString("url"));
			attribute.setDescription(results.getString("description"));
			attribute.setProvidedBy(results.getString("transformer"));
			attributes.add(attribute);
		}
		results.close();
		return attributes;
	}
}
