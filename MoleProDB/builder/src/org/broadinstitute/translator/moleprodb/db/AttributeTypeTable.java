package org.broadinstitute.translator.moleprodb.db;

import java.sql.SQLException;
import java.util.HashMap;

import apimodels.Attribute;
import apimodels.KmAttribute;
import apimodels.Node;
import apimodels.Predicate;
import transformer.Transformer;
import transformer.Transformers;
import transformer.exception.NotFoundException;

public class AttributeTypeTable extends MoleProTable {

	private static HashMap<String,String> attributeDescriptions = new HashMap<>();

	private long lastAttrTypeId = -1;


	public AttributeTypeTable(MoleProDB db) {
		super(db, "Attribute_Type");
	}


	private void insert(final long id, final String attrName, final String attrType, final String valueType, final String description) throws SQLException {
		String sql = "INSERT INTO Attribute_Type (attribute_type_id, attribute_name, attribute_type, value_type, description)\n";
		sql = sql + "VALUES (" + id + "," + f(attrName) + "," + f(attrType) + "," + f(valueType) + "," + f(description) + ")";
		executeUpdate(sql);
	}


	public long getAttrTypeId(final Attribute attribute, final long sourceId) throws SQLException {
		final String attrName = attribute.getOriginalAttributeName();
		final String attrType = attribute.getAttributeTypeId();
		final String valueType = attribute.getValueTypeId();
		final String attributeDescription = getattributeDescription(attribute, sourceId);
		if (attrName == null) {
			return -1;
		}
		long attrTypeId = findAttrTypeId(attrName, (attrType == null) ? "" : attrType, valueType, attributeDescription);
		if (attrTypeId > 0) {
			return attrTypeId;
		}
		if (lastAttrTypeId < 0) {
			lastAttrTypeId = lastId("attribute_type_id");
		}
		lastAttrTypeId = lastAttrTypeId + 1;
		insert(lastAttrTypeId, attrName, (attrType == null) ? "" : attrType, valueType, attributeDescription);
		return lastAttrTypeId;
	}


	private long findAttrTypeId(final String attrName, final String attrType, final String valueType, final String description) {
		String where = "WHERE attribute_name = " + f(attrName) + " AND attribute_type " + is(attrType) + " AND value_type " + is(valueType) + " AND description " + is(description) + ";";
		return findId("attribute_type_id", where);
	}


	private String getattributeDescription(Attribute attribute, final long sourceId) {
		final String key = key(attribute.getOriginalAttributeName(), sourceId);
		if (!attributeDescriptions.containsKey(key)) {
			attributeDescriptions.put(key, null);
			loadAttributeDescriptions(sourceId);
		}
		return attributeDescriptions.get(key);
	}


	private void loadAttributeDescriptions(final long sourceId) {
		final String transformerName = db.sourceTable.getTransformerName(sourceId);
		try {
			Transformer transformer = Transformers.getTransformer(transformerName);
			if (transformer.info.getKnowledgeMap().getNodes() != null)
				for (Node node : transformer.info.getKnowledgeMap().getNodes().values()) {
					if (node.getAttributes() != null)
						for (KmAttribute attribute : node.getAttributes()) {
							loadAttributeDescriptions(sourceId, attribute);
						}
				}
			if (transformer.info.getKnowledgeMap().getEdges() != null)
				for (Predicate predicate : transformer.info.getKnowledgeMap().getEdges()) {
					if (predicate.getAttributes() != null)
						for (KmAttribute attribute : predicate.getAttributes()) {
							loadAttributeDescriptions(sourceId, attribute);
						}
				}
		}
		catch (NotFoundException e) {
			System.err.println("WARN: Failed to obtain transformer for " + transformerName);
		}
		catch (Exception e) {
			e.printStackTrace();
		}
	}


	private void loadAttributeDescriptions(long sourceId, KmAttribute attribute) {
		final String typeKey = key(attribute.getAttributeTypeId(), sourceId);
		attributeDescriptions.put(typeKey, attribute.getDescription());
		if (attribute.getNames() != null)
			for (String attributeName : attribute.getNames()) {
				final String nameKey = key(attributeName, sourceId);
				attributeDescriptions.put(nameKey, attribute.getDescription());
			}
	}


	private String key(final String attributeName, final long sourceId) {
		return attributeName + " # " + sourceId;
	}
}
