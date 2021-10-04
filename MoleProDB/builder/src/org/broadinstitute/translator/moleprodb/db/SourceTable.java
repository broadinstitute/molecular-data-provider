package org.broadinstitute.translator.moleprodb.db;

import java.sql.ResultSet;
import java.sql.SQLException;

public class SourceTable extends MoleProTable {

	private long lastSourceId = -1;


	SourceTable(MoleProDB moleProDB) {
		super(moleProDB, "Source");
	}


	/************************************************************************************************
	 * Insert any new MolePro Transformers into the Source table, indexed by Transformer name to 
	 * ensure unique entry.
	 * 
	 * The Transformers were created for the corresponding Sources such as:
	 * BigGIM, CMAP, CTRP, ChEBI, ChEMBL, ChemBank, DGIdb, DepMap, DrugBank, DrugCentral, GeLiNEA, 
	 * GtoPdb, etc ...
	 * 
	 * @param id
	 * @param name
	 * @param url
	 * @param transformer
	 * @param transformerURL
	 * @throws SQLException
	 */
	private void insert(long id, String name, String url, String sourceVersion, String transformer, String transformerURL, String transformerVersion, Long inforesId) throws SQLException {
		String sql = "INSERT INTO Source (source_id, source_name, source_url, source_version, transformer, transformer_url, transformer_version, infores_id)\n";
		sql = sql + "VALUES (" + id + "," + f(name) + "," + f(url) + "," + f(sourceVersion) + ",";
		sql = sql + f(transformer) + "," + f(transformerURL) + "," + f(transformerVersion) + "," + f(inforesId) + ")";
		executeUpdate(sql);
	}


	public void insert(String name, String url, String sourceVersion, String transformer, String transformerURL, String transformerVersion) throws SQLException {
		if (lastSourceId < 0) {
			lastSourceId = lastId("source_id");
		}
		lastSourceId = lastSourceId + 1;
		final Long inforesId = db.inforesTable.InfoResId(transformer);
		insert(lastSourceId, name, url, sourceVersion, transformer, transformerURL, transformerVersion, inforesId);
	}


	public int sourceId(String transformer) {
		int sourceId = 0;
		String query = "SELECT source_id from Source WHERE transformer = " + f(transformer) + ";";
		try {
			ResultSet results = this.executeQuery(query);
			if (results.next()) {
				sourceId = results.getInt(1);
			}
			results.close();
		}
		catch (SQLException e) {
			System.err.println("Failed to obtain source_id for " + transformer + ": " + e.getMessage());
		}
		return sourceId;
	}
}
