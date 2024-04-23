package org.broadinstitute.translator.moleprodb.db;

import java.io.BufferedReader;
import java.io.FileReader;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;

import apimodels.Names;

public class NameMapTable extends MoleProTable {

	private final String parentIdColumn;


	public NameMapTable(final MoleProDB db, final String tableName, final String parentIdColumn) {
		super(db, tableName);
		this.parentIdColumn = parentIdColumn;
	}


	private void insert(final long parentId, final long sourceId, final long nameId, final long nameTypeId, final long nameSourceId, final String language) throws SQLException {
		String sql = "INSERT INTO " + tableName + " (" + parentIdColumn + ", name_id, name_type_id, name_source_id, source_id, language)\n";
		sql = sql + "VALUES (" + parentId + "," + nameId + "," + nameTypeId + "," + nameSourceId + "," + sourceId + "," + f(language) + ")";
		executeUpdate(sql);
	}


	/************************************************
	 * 
	 * 
	 * @param db
	 * @param structureId
	 * @param sourceId
	 * @param namesSynonyms
	 * @throws SQLException
	 */
	public void saveNames(final long parentId, final int sourceId, final Names namesSynonyms) throws SQLException {
		final String language = mapLanguage(namesSynonyms.getLanguage());
		final long nameSourceId = db.nameSourceTable.nameSourceId(namesSynonyms.getSource());
		if (namesSynonyms != null && namesSynonyms.getName() != null && namesSynonyms.getName().length() > 0) {
			final long nameId = db.nameTable.nameId(namesSynonyms.getName());
			final long nameTypeId = db.nameTypeTable.nameTypeId(namesSynonyms.getNameType());
			saveName(parentId, sourceId, nameId, nameTypeId, nameSourceId, language);
		}
		if (namesSynonyms != null && namesSynonyms.getSynonyms() != null) {
			for (String synonym : namesSynonyms.getSynonyms())
				if (synonym != null && synonym.length() > 0) {
					final long synonymId = db.nameTable.nameId(synonym);
					final long synonymTypeId = db.nameTypeTable.synonymTypeId(namesSynonyms.getNameType());
					saveName(parentId, sourceId, synonymId, synonymTypeId, nameSourceId, language);
				}
		}
	}


	public void saveName(final long parentId, final int sourceId, final long nameId, final long nameTypeId, final long nameSourceId, final String language) throws SQLException {
		if (parentNameId(parentId, sourceId, nameId, nameTypeId, nameSourceId, language) <= 0) {
			insert(parentId, sourceId, nameId, nameTypeId, nameSourceId, language);
		}
	}


	private long parentNameId(final long parentId, final long sourceId, final long nameId, final long nameTypeId, final long nameSourceId, final String language) {
		String where = "WHERE " + parentIdColumn + " = " + parentId + " AND name_id = " + nameId + " AND name_type_id = " + nameTypeId;
		where = where + " AND name_source_id = " + nameSourceId + " AND source_id = " + sourceId + " AND language " + is(language);
		return super.findId(parentIdColumn, where);
	}


	public ArrayList<Names> getNames(final long parentId, final long sourceId) throws SQLException {
		Date start = new Date();
		String query = "SELECT name, name_type, name_source, transformer, language \n";
		query = query + "FROM " + tableName + "\n";
		query = query + "JOIN Name_Type ON Name_Type.name_type_id = " + tableName + ".name_type_id\n";
		query = query + "JOIN Name_Source ON Name_Source.name_source_id = " + tableName + ".name_source_id\n";
		query = query + "JOIN Name ON Name.name_id = " + tableName + ".name_id\n";
		query = query + "JOIN Source ON Source.source_id = " + tableName + ".source_id\n";
		query = query + "WHERE " + parentIdColumn + " = " + parentId;
		query = query + " AND Source.source_id = " + sourceId;
		final ResultSet results = this.executeQuery(query);
		final ArrayList<Names> nameList = new ArrayList<>();
		final HashMap<String,Names> names = new HashMap<>();
		while (results.next()) {
			final String name = results.getString("name");
			boolean synonym = false;
			String nameType = results.getString("name_type");
			if ("primary name".equals(nameType)) {
				nameType = "";
			}
			if ("synonym".equals(nameType)) {
				nameType = "";
				synonym = true;
			}
			if (nameType.endsWith(" synonym")) {
				nameType = nameType.substring(0, nameType.length() - 8);
				synonym = true;
			}
			final String nameSource = results.getString("name_source");
			final String transformer = results.getString("transformer");
			final String language = results.getString("language");
			final String key = nameType + "[" + language + "]@" + nameSource;
			if (!names.containsKey(key)) {
				Names namesSynonyms = new Names().synonyms(new ArrayList<String>());
				if (synonym) {
					namesSynonyms.getSynonyms().add(name);
				}
				else {
					namesSynonyms.setName(name);
				}
				namesSynonyms.setNameType(nameType);
				namesSynonyms.setSource(nameSource);
				namesSynonyms.setProvidedBy(transformer);
				namesSynonyms.setLanguage(language);
				names.put(key, namesSynonyms);
				nameList.add(namesSynonyms);
			}
			else {
				Names namesSynonyms = names.get(key);
				if (synonym) {
					namesSynonyms.getSynonyms().add(name);
				}
				else if (namesSynonyms.getName() == null) {
					namesSynonyms.setName(name);
				}
				else {
					namesSynonyms.getSynonyms().add(name);
				}
			}
		}
		for (Names namesSynonyms : nameList) {
			if ("".equals(namesSynonyms.getName())) {
				namesSynonyms.setName(null);
			}
		}
		profile("- get structure - getNames", start);
		return nameList;
	}

	// STATIC

	private static final HashMap<String,String> languageMap = loadLanguageMap();


	private static HashMap<String,String> loadLanguageMap() {
		HashMap<String,String> languageMap = new HashMap<>();
		try {
			final BufferedReader mapFile = new BufferedReader(new FileReader("conf/languageMap.txt"));
			for (String line = mapFile.readLine(); line != null; line = mapFile.readLine()) {
				final String[] row = line.split("\t", 2);
				languageMap.put(row[0], row[1]);
			}
			mapFile.close();
		}
		catch (Exception e) {
			System.err.println("Failed to load language mapping" + e);
		}
		return languageMap;
	}


	private String mapLanguage(String language) {
		if (language == null)
			return null;
		return languageMap.getOrDefault(language, language);
	}

}
