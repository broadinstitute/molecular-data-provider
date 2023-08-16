package org.broadinstitute.translator.moleprodb.db;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Map;

public class ChemStructureIdentifierTable extends IdentifierTable {

	public ChemStructureIdentifierTable(MoleProDB db) {
		super(db, "Chem_Structure_Identifier", "structure_identifier_id", "structure_id");
	}


	public long structureId(final Map<String,Object> identifiers) throws SQLException {
		for (Map.Entry<String,Object> entry : identifiers.entrySet())
			if (entry.getValue() != null) {
				final String fieldName = entry.getKey();
				if (entry.getValue() instanceof String) {
					final String curie = (String) entry.getValue();
					final long structureId = findParentId(fieldName, curie);
					if (structureId > 0) {
						return structureId;
					}
				}
			}
		return -1;
	}


	public Map<String,Object> getIdentifiers(final long parentId, final long sourceId) throws SQLException {
		String query = "SELECT field_name, mole_pro_prefix, xref\n";
		query = query + "FROM " + tableName + "\n";
		query = query + "JOIN Curie_Prefix ON Curie_Prefix.prefix_id = " + tableName + ".prefix_id\n";
		query = query + "JOIN Source ON Source.source_id = " + tableName + ".source_id\n";
		query = query + "WHERE " + parentIdColumn + " = " + parentId;
		query = query + " AND Source.source_id = " + sourceId + "\n";
		query = query + " AND Curie_Prefix.field_name not in ('inchi','inchikey')";
		query = query + "UNION\n";
		query = query + "SELECT\n";
		query = query + "  'inchi' AS field_name,\n";
		query = query + "  '' AS mole_pro_prefix,\n";
		query = query + "  inchi AS xref\n";
		query = query + "FROM Chem_Structure\n";
		query = query + "WHERE " + parentIdColumn + " = " + parentId + "\n";
		query = query + "UNION\n";
		query = query + "SELECT\n";
		query = query + "  'inchikey' AS field_name,\n";
		query = query + "  '' AS mole_pro_prefix,\n";
		query = query + "  inchikey AS xref\n";
		query = query + "FROM Chem_Structure\n";
		query = query + "WHERE " + parentIdColumn + " = " + parentId + "\n";
		return getIdentifiers(query);
	}


	public String getBiolinkClass(final long parentId, final long sourceId) throws SQLException {
		String query = "SELECT DISTINCT biolink_class\n";
		query = query + "FROM " + tableName + "\n";
		query = query + "JOIN Curie_Prefix ON Curie_Prefix.prefix_id = " + tableName + ".prefix_id\n";
		query = query + "JOIN Biolink_Class ON Biolink_Class.biolink_class_id = Curie_Prefix.biolink_class_id\n";
		query = query + "WHERE " + parentIdColumn + " = " + parentId;
		query = query + " AND Chem_Structure_Identifier.source_id = " + sourceId + "\n";
		final ResultSet results = this.executeQuery(query);
		while (results.next()) {
			String biolinkClass = results.getString("biolink_class");
			results.close();
			return biolinkClass;
		}
		return null;
	}
}
