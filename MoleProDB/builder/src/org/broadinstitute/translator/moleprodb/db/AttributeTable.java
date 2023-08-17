package org.broadinstitute.translator.moleprodb.db;

import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashSet;
import java.util.List;

import com.fasterxml.jackson.core.JsonProcessingException;

import apimodels.Attribute;
import transformer.util.JSON;

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
	private void insert(final long attributeId, final String attributeValue, final boolean isJSON, final String url, final String description, final Long subAttributeId) throws SQLException {
		String sql = "INSERT INTO Attribute (attribute_id, attribute_value, is_json, url, description, subattribute_id)\n";
		sql = sql + "VALUES (" + attributeId + "," + f(attributeValue) + "," + f(isJSON) + "," + f(url) + "," + f(description) + "," + f(subAttributeId) + ")";
		executeUpdate(sql);
	}


	long getAttributeId(final Attribute attribute, final long sourceId) throws SQLException {
		if (attribute.getValue() == null) {
			return -1;
		}
		String attributeValue = null;
		boolean isJSON = false;
		if (attribute.getValue() instanceof String) {
			attributeValue = (String)attribute.getValue();
		}
		else {
			try {
				attributeValue = JSON.mapper.writeValueAsString(attribute.getValue());
				isJSON = true;
			}
			catch (JsonProcessingException e) {
				attributeValue = attribute.getValue().toString();
				System.out.print("failed to map to JSON: (" + attribute.getOriginalAttributeName() + ")" + attributeValue);
			}
		}
		Date start = new Date();
		final List<Attribute> subAttributes = removeDuplicates(attribute.getAttributes());
		final long[] subAttributeIds = findSubAttributes(subAttributes, sourceId);
		profile("**get subattributes", start);
		start = new Date();
		final long[] subAttributeTypes = findSubAttributeTypes(subAttributes, sourceId);
		profile("**get subattribute types", start);
		start = new Date();
		final long attributeId = findAttributeId(attributeValue, isJSON, attribute.getValueUrl(), attribute.getDescription(), subAttributeIds, subAttributeTypes, sourceId);
		profile("**get attribute id", start);
		if (attributeId > 0) {
			return attributeId;
		}
		if (lastAttributeId < 0) {
			lastAttributeId = lastId("attribute_id");
		}
		lastAttributeId = lastAttributeId + 1;
		final Long subAttributeId = (subAttributeIds == null) ? null : lastAttributeId;
		start = new Date();
		if (subAttributeIds != null)
			for (int i = 0; i < subAttributeIds.length; i++) {
				db.parentAttributeTable.insert(lastAttributeId, subAttributeTypes[i], subAttributeIds[i], sourceId);
			}
		profile("**insert subattributes", start);
		start = new Date();
		insert(lastAttributeId, attributeValue, isJSON, attribute.getValueUrl(), attribute.getDescription(), subAttributeId);
		profile("**insert attribute", start);
		return lastAttributeId;
	}


	private List<Attribute> removeDuplicates(List<Attribute> attributes) {
		if (attributes == null)
			return attributes;
		final List<Attribute> subAttributes = new ArrayList<>();
		final HashSet<String> subAttributeSet = new HashSet<>();
		for (Attribute attribute : attributes) {
			final String key = attribute.getAttributeTypeId()+"#"+attribute.getValue();
			if (!subAttributeSet.contains(key)) {
				subAttributes.add(attribute);
				subAttributeSet.add(key);
			}
		}
		return subAttributes;
	}


	private long[] findSubAttributes(final List<Attribute> attributes, final long sourceId) throws SQLException {
		if (attributes == null || attributes.size() == 0)
			return null;
		final long[] attributeIds = new long[attributes.size()];
		for (int i = 0; i < attributeIds.length; i++) {
			attributeIds[i] = getAttributeId(attributes.get(i), sourceId);
		}
		return attributeIds;
	}


	private long[] findSubAttributeTypes(final List<Attribute> attributes, final long sourceId) throws SQLException {
		if (attributes == null || attributes.size() == 0)
			return null;
		final long[] attributeIds = new long[attributes.size()];
		for (int i = 0; i < attributeIds.length; i++) {
			attributeIds[i] = db.attributeTypeTable.getAttrTypeId(attributes.get(i), sourceId);
		}
		return attributeIds;
	}


	private long findAttributeId(final String attributeValue, final boolean isJSON, final String url, final String description) {
		String where = "WHERE attribute_value = " + f(attributeValue);
		where = where + " AND is_json = " + f(isJSON);
		where = where + " AND url " + is(url);
		where = where + " AND description " + is(description);
		where = where + " AND subattribute_id IS NULL;\n";
		return findId("Attribute.attribute_id", where);
	}


	private long findAttributeId(final String attributeValue, final boolean isJSON, final String url, final String description, final long[] subAttributes, final long[] subAttributeTypes, final long sourceId) {
		if (subAttributes == null || subAttributes.length == 0) {
			return findAttributeId(attributeValue, isJSON, url, description);
		}

		String select = "SELECT parent_attribute_id, count(attribute_id) AS count\n";
		select = select + "FROM Parent_Attribute\n";
		select = select + "WHERE  parent_attribute_id IN (\n";
		select = select + " SELECT Attribute.attribute_id\n";
		select = select + " FROM Attribute\n";

		String where = " WHERE attribute_value = " + f(attributeValue);
		where = where + "  AND is_json = " + f(isJSON);
		where = where + "  AND url " + is(url);
		where = where + "  AND description " + is(description) + "\n";

		String join = "";
		for (int i = 0; i < subAttributes.length; i++) {
			join = join + " JOIN Parent_Attribute AS Parent_Attribute_" + i + " ON Parent_Attribute_" + i + ".parent_attribute_id = Attribute.subattribute_id\n";
			where = where + "  AND Parent_Attribute_" + i + ".attribute_id = " + subAttributes[i];
			where = where + "  AND Parent_Attribute_" + i + ".attribute_type_id = " + subAttributeTypes[i];
			where = where + "  AND Parent_Attribute_" + i + ".source_id = " + sourceId + "\n";
		}
		where = where + ")";

		String group = "GROUP BY parent_attribute_id\n";
		group = group + "HAVING count = " + subAttributes.length + "\n";

		return findId(select + join + where + group);
	}

}
