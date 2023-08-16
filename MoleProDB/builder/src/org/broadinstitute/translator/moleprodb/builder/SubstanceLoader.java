package org.broadinstitute.translator.moleprodb.builder;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Date;

import org.broadinstitute.translator.moleprodb.db.MoleProDB;

public class SubstanceLoader extends SubstanceResolver {

	private PreparedStatement namesQuery;
	private PreparedStatement attributesQuery;


	public SubstanceLoader(MoleProDB db) throws Exception {
		super(db);
		namesQuery = db.prepareStatement(namesQuery());
		attributesQuery = db.prepareStatement(attributesQuery());
	}


	protected void reconnect() throws SQLException {
		super.reconnect();
		namesQuery = db.prepareStatement(namesQuery());
		attributesQuery = db.prepareStatement(attributesQuery());
	}


	private long getFirstStructureId() throws SQLException {
		String sql = "SELECT max(structure_id) as last_structure_id FROM Chem_Structure_Map";
		ResultSet results = db.executeQuery(sql);
		results.next();
		return results.getLong("last_structure_id") + 1;
	}


	private ResultSet getStructure(final long structureId) throws SQLException {
		String sql = "SELECT inchi, inchikey FROM Chem_Structure\n";
		sql = sql + "WHERE structure_id = " + structureId;
		return db.executeQuery(sql);
	}


	private void createSubstance(long structureId, String inchi, String inchikey) throws SQLException {
		Date start = new Date();
		String name = findBestName(structureId);
		profile("get best name", start);
		if (name == null)
			name = findAnyName(structureId);
		if (name == null)
			name = inchikey;
		start = new Date();
		final long biolinkClassId = biolinkClassId(detectMixture(inchi));
		long elementId = db.listElementTable.insert(name, biolinkClassId);
		db.chemStructureMapTable.insert(elementId, structureId, true);
		profile("save element", start);
		saveIdentifiers(elementId, structureId, inchi, inchikey, biolinkClassId);
		saveNames(elementId, structureId);
		saveAttributes(elementId, structureId);
	}


	static String detectMixture(String inchi) {
		if (inchi == null) {
			return BiolinkClass.ChemicalEntity;
		}
		final String[] inchiParts = inchi.split("/");
		if (inchiParts.length >= 2) {
			return (inchiParts[1].contains(".")) ? BiolinkClass.MolecularMixture : BiolinkClass.SmallMolecule;
		}
		return BiolinkClass.SmallMolecule;
	}


	private void saveIdentifiers(long elementId, long structureId, String inchi, String inchikey, final long biolinkClassId) throws SQLException {
		Date start = new Date();
		long fisrtSourceId = -1;
		ResultSet identifiers = indentifiers(structureId);
		profile("get identifiers", start);
		start = new Date();
		while (identifiers.next()) {
			String xref = identifiers.getString("xref");
			long prefixId = identifiers.getLong("prefix_id");
			long sourceId = identifiers.getLong("source_id");
			if (fisrtSourceId < 0) {
				fisrtSourceId = sourceId;
			}
			db.listElementIdentifierTable.saveIdentifier(elementId, xref, prefixId, sourceId);
		}
		identifiers.close();
		long inchiPrefixId = db.curiePrefixTable.prefixId(biolinkClassId, "", "inchi");
		if (inchi != null) {
			db.listElementIdentifierTable.saveIdentifier(elementId, inchi, inchiPrefixId, fisrtSourceId);
		}
		long inchikeyPrefixId = db.curiePrefixTable.prefixId(biolinkClassId, "", "inchikey");
		db.listElementIdentifierTable.saveIdentifier(elementId, inchikey, inchikeyPrefixId, fisrtSourceId);
		profile("save identifiers", start);
	}


	private String namesQuery() {
		String sql = "SELECT name_id, name_type_id, name_source_id, source_id, language\n";
		sql = sql + "FROM Chem_Structure_Name\n";
		sql = sql + "WHERE structure_id = ?";
		return sql;
	}


	private void saveNames(long elementId, long structureId) throws SQLException {
		Date start = new Date();
		namesQuery.setLong(1, structureId);
		ResultSet names = namesQuery.executeQuery();
		profile("get names", start);
		start = new Date();
		while (names.next()) {
			long nameId = names.getLong("name_id");
			long nameTypeId = names.getLong("name_type_id");
			long nameSourceId = names.getLong("name_source_id");
			int sourceId = names.getInt("source_id");
			String language = names.getString("language");
			db.listElementNameTable.saveName(elementId, sourceId, nameId, nameTypeId, nameSourceId, language);
		}
		names.close();
		profile("save names", start);
	}


	private String attributesQuery() {
		String sql = "SELECT attribute_id, source_id\n";
		sql = sql + "FROM Chem_Structure_Attribute\n";
		sql = sql + "WHERE structure_id = ?";
		return sql;
	}


	private void saveAttributes(long elementId, long structureId) throws SQLException {
		Date start = new Date();
		attributesQuery.setLong(1, structureId);
		ResultSet attributes = attributesQuery.executeQuery();
		profile("get attributes", start);
		start = new Date();
		while (attributes.next()) {
			int sourceId = attributes.getInt("source_id");
			long attributeId = attributes.getLong("attribute_id");
			db.listElementAttributeTable.saveAttribute(elementId, sourceId, attributeId);
		}
		attributes.close();
		profile("save attributes", start);
	}


	public void loadCompounds() throws Exception {
		final long firstStructureId = getFirstStructureId();
		final long lastStructureId = db.chemStructureTable.lastStructureId();
		for (long structureId = firstStructureId; structureId <= lastStructureId; structureId++) {
			ResultSet results = getStructure(structureId);
			while (results.next()) {
				String inchi = results.getString("inchi");
				String inchikey = results.getString("inchikey");
				if (inchikey != null)
					createSubstance(structureId, inchi, inchikey);
			}
			results.close();
			if (structureId % 100 == 0) {
				System.out.print(".");
				db.commit();
				if (structureId % 1000 == 0) {
					reconnect();
					printMemoryStatus(" @" + structureId + ": ");
				}
			}
		}
		db.commit();
	}

}
