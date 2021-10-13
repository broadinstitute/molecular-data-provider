package org.broadinstitute.translator.moleprodb.db;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;

import transformer.mapping.MappedBiolinkClass;
import transformer.util.JSON;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.annotation.JsonProperty;

public class CuriePrefixTable extends MoleProTable {

	private long lastPrefixId = -1;

	private HashMap<String,Long> curiePrefixMap = new HashMap<>();


	public CuriePrefixTable(MoleProDB db) {
		super(db, "Curie_Prefix");
	}


	private void insert(long id, long biolinkClassId, String moleProPrefix, String biolinkPrefix, String fieldName, Long inforesId, String uri) throws SQLException {
		String sql = "INSERT INTO Curie_Prefix (prefix_id, biolink_class_id, mole_pro_prefix, biolink_prefix, field_name, infores_id, uri)\n";
		sql = sql + "VALUES (" + id + "," + biolinkClassId + "," + f(moleProPrefix) + "," + f(biolinkPrefix) + "," + f(fieldName) + "," + f(inforesId) + "," + f(uri) + ")";
		executeUpdate(sql);
		curiePrefixMap.put(fieldName + ":" + moleProPrefix + "@" + biolinkClassId, id);
	}


	private long insert(long biolinkClassId, String moleProPrefix, String biolinkPrefix, String fieldName, String uri) throws SQLException {
		if (lastPrefixId < 0) {
			lastPrefixId = lastId("prefix_id");
		}
		lastPrefixId = lastPrefixId + 1;
		final Long inforesId = db.inforesTable.InfoResId(fieldName);
		insert(lastPrefixId, biolinkClassId, moleProPrefix, biolinkPrefix, fieldName, inforesId, uri);
		return lastPrefixId;
	}


	private long findPrefixId(long biolinkClassId, String moleProPrefix, String fieldName) {
		String key = fieldName + ":" + moleProPrefix + "@" + biolinkClassId;
		if (curiePrefixMap.containsKey(key)) {
			return curiePrefixMap.get(key);
		}
		long id = -1;
		String query = "SELECT prefix_id FROM Curie_Prefix ";
		query = query + "WHERE biolink_class_id = " + biolinkClassId + " AND mole_pro_prefix = " + f(moleProPrefix) + " AND field_name = " + f(fieldName) + ";";
		try {
			ResultSet results = this.executeQuery(query);
			if (results.next()) {
				id = results.getLong(1);
				curiePrefixMap.put(key, id);
			}
			results.close();
		}
		catch (SQLException e) {
			System.err.println("Failed to obtain prefix_id for " + moleProPrefix + "/" + fieldName + ": " + e.getMessage());
		}
		return id;
	}


	/******************************************************************
	 * 
	 * Look up the prefix_id in the Curie_Prefix Table given values for -
	 * biolink_class_id - mole_pro_prefix - field_name
	 * 
	 * 
	 * @param biolinkClassId
	 * @param moleProPrefix
	 * @param fieldName
	 * @return
	 * @throws SQLException
	 */
	public long prefixId(final long biolinkClassId, final String moleProPrefix, final String fieldName) throws SQLException {
		return prefixId(biolinkClassId, moleProPrefix, moleProPrefix, fieldName);
	}


	private long prefixId(final long biolinkClassId, final String moleProPrefix, final String biolinkPrefix, final String fieldName) throws SQLException {
		if (biolinkClassId <= 0) {
			return 0;
		}
		long prefixId = findPrefixId(biolinkClassId, moleProPrefix, fieldName);
		if (prefixId <= 0 && biolinkPrefix != moleProPrefix) {
			prefixId = findPrefixId(biolinkClassId, biolinkPrefix, fieldName);
		}
		if (prefixId > 0) {
			return prefixId;
		}
		return insert(biolinkClassId, moleProPrefix, biolinkPrefix, fieldName, null);
	}


	public void loadPrefixes() throws Exception {
		String json = new String(Files.readAllBytes(Paths.get("conf/prefixMap.json")));
		final TypeReference<Map<String,Map<String,PrefixMap>>> typeReference = new TypeReference<Map<String,Map<String,PrefixMap>>>() {
		};
		final Map<String,Map<String,PrefixMap>> prefixMap = JSON.mapper.readValue(json, typeReference);
		for (String biolinkClass : prefixMap.keySet()) {
			final long biolinkClassId = db.biolinkClassTable.biolinkClassId(MappedBiolinkClass.map(biolinkClass));
			for (String fieldName : prefixMap.get(biolinkClass).keySet()) {
				PrefixMap prefixes = prefixMap.get(biolinkClass).get(fieldName);
				System.out.println(biolinkClass);
				System.out.println(fieldName + ": " + prefixes);
				String moleproPrefix = prefixes.moleproPrefix;
				if (moleproPrefix.endsWith(":")) {
					moleproPrefix = moleproPrefix.substring(0, moleproPrefix.length() - 1);
				}
				prefixId(biolinkClassId, moleproPrefix, prefixes.biolinkPrefix, fieldName);
			}
		}
		db.commit();
	}


	static class PrefixMap {

		String biolinkPrefix;
		String moleproPrefix;


		@JsonProperty("biolink_prefix")
		public void setBiolinkPrefix(String biolinkPrefix) {
			this.biolinkPrefix = biolinkPrefix;
		}


		@JsonProperty("molepro_prefix")
		public void setMoleproPrefix(String moleproPrefix) {
			this.moleproPrefix = moleproPrefix;
		}


		public String toString() {
			return "{biolink:" + biolinkPrefix + ",molepro:" + moleproPrefix + "}";
		}
	}
}
