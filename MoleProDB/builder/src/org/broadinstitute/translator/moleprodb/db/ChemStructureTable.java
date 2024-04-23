package org.broadinstitute.translator.moleprodb.db;

import java.sql.ResultSet;
import java.sql.SQLException;

public class ChemStructureTable extends MoleProTable {

	private long lastStructureId = -1;


	public ChemStructureTable(MoleProDB db) {
		super(db, "Chem_Structure");
	}


	private void insert(final long id, final String inchi, final String inchikey) throws SQLException {
		String sql = "INSERT INTO Chem_Structure (structure_id, inchi, inchikey)\n";
		sql = sql + "VALUES (" + id + "," + f(inchi) + "," + f(inchikey) + ")";
		executeUpdate(sql);
	}


	private long insert(final String inchi, final String inchikey) throws SQLException {
		if (lastStructureId < 0) {
			lastStructureId = lastStructureId();
		}
		lastStructureId = lastStructureId + 1;
		insert(lastStructureId, inchi, inchikey);
		return lastStructureId;
	}


	private long structureIdInchi(final String inchi) {
		return findId("structure_id", "inchi", inchi);
	}


	private long structureIdInchikey(final String inchikey, final String inchi) throws SQLException {
		final String select = "SELECT structure_id, inchi FROM " + tableName;
		final String where = " WHERE inchikey = " + f(inchikey);
		long structureId = -1;
		String inchiDB = null;

		final ResultSet results = this.executeQuery(select + where);
		if (results.next()) {
			structureId = results.getLong("structure_id");
			inchiDB = results.getString("inchi");
		}
		if (results.next()) {
			System.err.println("WARN: Found multiple ids in structure_id " + where);
		}
		results.close();

		if (structureId > 0) {
			if (inchi != null) {
				if (inchiDB == null) {
					// update InChI in the database
					updateInChI(structureId, inchikey, inchi);
				}
				else {
					// compare InChI for differences
					if (!inchi.equals(inchiDB)) {
						System.err.println("WARN: Found multiple inchi vules for " + inchikey);
					}
				}
			}
		}
		return structureId;
	}


	private void updateInChI(final long structureId, final String inchikey, final String inchi) throws SQLException {
		final String update = "UPDATE " + tableName + " SET inchi = " + f(inchi);
		final String where = " WHERE structure_id = " + structureId + " AND inchikey = " + f(inchikey);
		try {
			executeUpdate(update + where);
		}
		catch (SQLException e) {
			System.err.println("WARN: Failed to update InChI " + where + ": " + e.getMessage());
		}
	}


	public long lastStructureId() {
		return lastId("structure_id");
	}


	public long getStructureId(final String inchi, String inchikey) throws SQLException {
		if (inchikey == null) {
			return -1;
		}
		if (inchikey.toUpperCase().startsWith("INCHIKEY:")) {
			inchikey = inchikey.substring(9);
		}
		long structureId = db.chemStructureTable.structureIdInchi(inchi);
		if (structureId <= 0) {
			structureId = db.chemStructureTable.structureIdInchikey(inchikey, inchi);
		}
		if (structureId <= 0 && inchikey != null) {
			structureId = db.chemStructureTable.insert(inchi, inchikey);
		}
		return structureId;
	}
}
