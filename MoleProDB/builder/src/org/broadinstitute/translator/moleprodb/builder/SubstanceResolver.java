package org.broadinstitute.translator.moleprodb.builder;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;

import org.broadinstitute.translator.moleprodb.db.MoleProDB;

public class SubstanceResolver extends Loader {

	private final int[] PRIORITY_LEVELS = { 10, 100, 200, 300 };

	private final static HashMap<String,Integer> sourcePriority = loadSourcePriority();

	private PreparedStatement resolvedQuery;

	private PreparedStatement structuresQuery;

	private PreparedStatement substanceIdQuery;

	private PreparedStatement substanceNameQuery;

	private PreparedStatement bestNameQuery;

	private PreparedStatement namesQuery;

	private PreparedStatement indentifiersQuery;

	private PreparedStatement inchiQuery;

	private PreparedStatement structureMapQuery;


	SubstanceResolver(MoleProDB db) throws Exception {
		super(db);
		resolvedQuery = db.prepareStatement(resolvedQuery());
		structuresQuery = db.prepareStatement(structuresQuery());
		substanceIdQuery = db.prepareStatement(substanceIdQuery());
		substanceNameQuery = db.prepareStatement(substanceNameQuery());
		bestNameQuery = db.prepareStatement(bestNameQuery(PRIORITY_LEVELS[1]));
		namesQuery = db.prepareStatement(namesQuery());
		indentifiersQuery = db.prepareStatement(indentifiersQuery());
		inchiQuery = db.prepareStatement(inchiQuery());
		structureMapQuery = db.prepareStatement(structureMapQuery());
	}


	protected void reconnect() throws SQLException {
		db.reconnect();
		resolvedQuery = db.prepareStatement(resolvedQuery());
		structuresQuery = db.prepareStatement(structuresQuery());
		substanceIdQuery = db.prepareStatement(substanceIdQuery());
		substanceNameQuery = db.prepareStatement(substanceNameQuery());
		bestNameQuery = db.prepareStatement(bestNameQuery(PRIORITY_LEVELS[1]));
		namesQuery = db.prepareStatement(namesQuery());
		indentifiersQuery = db.prepareStatement(indentifiersQuery());
		inchiQuery = db.prepareStatement(inchiQuery());
		structureMapQuery = db.prepareStatement(structureMapQuery());
	}


	private static HashMap<String,Integer> loadSourcePriority() {
		HashMap<String,Integer> sourcePriority = new HashMap<>();
		try {
			final BufferedReader sourceFile = new BufferedReader(new FileReader("conf/sourcePriority.txt"));
			int i = 0;
			for (String line = sourceFile.readLine(); line != null; line = sourceFile.readLine()) {
				if (i > 0) {
					sourcePriority.put(line, i);
				}
				i = i + 1;
			}
			sourceFile.close();
		}
		catch (IOException e) {
			e.printStackTrace();
			System.exit(1);
		}
		System.out.println(sourcePriority.size() + " source priorities loaded");
		return sourcePriority;
	}


	private String resolvedQuery() {
		String sql = "SELECT element_name_id\n";
		sql = sql + "FROM List_Element_Name\n";
		sql = sql + "JOIN Chem_Structure_Map ON (Chem_Structure_Map.substance_id = List_Element_Name.list_element_id)\n";
		sql = sql + "WHERE structure_id = ? AND name_id = ? AND name_type_id = ? AND source_id=?\n";
		return sql;
	}


	private boolean resolvedName(final StructureName structureName) throws SQLException {
		Boolean resolved = false;
		resolvedQuery.setLong(1, structureName.structureId);
		resolvedQuery.setLong(2, structureName.nameId);
		resolvedQuery.setLong(3, structureName.nameTypeId);
		resolvedQuery.setLong(4, structureName.sourceId);
		final ResultSet results = resolvedQuery.executeQuery();
		while (results.next()) {
			resolved = true;
		}
		results.close();
		return resolved;
	}


	private String structuresQuery() {
		String sql = "SELECT structure_id, Name.name_id, Chem_Structure_Name.name_type_id, name_priority, name_source_id, Source.source_id, source_name, language\n";
		sql = sql + "FROM Chem_Structure_Name\n";
		sql = sql + "JOIN Name ON (Name.name_id = Chem_Structure_Name.name_id)\n";
		sql = sql + "JOIN Name_Type ON (Name_Type.name_type_id = Chem_Structure_Name.name_type_id)\n";
		sql = sql + "JOIN Source on Source.source_id = Chem_Structure_Name.source_id\n";
		sql = sql + "WHERE Name.name = ? COLLATE NOCASE\n";
		sql = sql + "ORDER BY name_priority ASC";
		return sql;
	}


	private ResultSet getStructures(String name) throws SQLException {
		structuresQuery.setString(1, name);
		return structuresQuery.executeQuery();
	}


	private String namesQuery() {
		String sql = "SELECT structure_id, name, Name.name_id, Chem_Structure_Name.name_type_id, name_priority, name_source_id, Source.source_id, source_name, language\n";
		sql = sql + "FROM Chem_Structure_Name\n";
		sql = sql + "JOIN Name ON (Name.name_id = Chem_Structure_Name.name_id)\n";
		sql = sql + "JOIN Name_Type ON (Name_Type.name_type_id = Chem_Structure_Name.name_type_id)\n";
		sql = sql + "JOIN Source on Source.source_id = Chem_Structure_Name.source_id\n";
		sql = sql + "WHERE Chem_Structure_Name.structure_id = ?\n";
		sql = sql + "ORDER BY name_priority ASC";
		return sql;
	}


	private ResultSet getNames(long structureId) throws SQLException {
		structuresQuery.setLong(1, structureId);
		return structuresQuery.executeQuery();
	}


	private String substanceIdQuery() {
		String sql = "SELECT DISTINCT substance_id\n";
		sql = sql + "FROM Chem_Structure_Map\n";
		sql = sql + "WHERE correct = 1 and structure_id = ? \n";
		return sql;
	}


	private long getSubstanceId(final long bestStructureId) throws SQLException {
		substanceIdQuery.setLong(1, bestStructureId);
		final ResultSet results = substanceIdQuery.executeQuery();
		long substanceId = -1;
		while (results.next()) {
			if (substanceId < 0) {
				substanceId = results.getLong("substance_id");
			}
			else {
				throw new SQLException("Duplicate substance_id for structure_id = " + bestStructureId);
			}
		}
		return substanceId;
	}


	private String substanceNameQuery() {
		String sql = "SELECT DISTINCT list_element_id\n";
		sql = sql + "FROM List_Element\n";
		sql = sql + "WHERE primary_name = ? COLLATE NOCASE\n";
		return sql;
	}


	private long getSubstanceId(final String primaryName) throws SQLException {
		substanceNameQuery.setString(1, primaryName);
		ResultSet results = substanceNameQuery.executeQuery();
		long substanceId = -1;
		while (results.next()) {
			if (substanceId < 0) {
				substanceId = results.getLong("list_element_id");
			}
			else {
				throw new SQLException("Duplicate substance_id for primary_name = " + primaryName);
			}
		}
		return substanceId;
	}


	private String bestNameQuery(int level) {
		String sql = "SELECT distinct name, source_name, name_priority\n";
		sql = sql + "FROM Chem_Structure_Name\n";
		sql = sql + "JOIN Name ON (Name.name_id = Chem_Structure_Name.name_id)\n";
		sql = sql + "JOIN Name_Type ON (Name_Type.name_type_id = Chem_Structure_Name.name_type_id)\n";
		sql = sql + "JOIN Source on Source.source_id = Chem_Structure_Name.source_id\n";
		sql = sql + "WHERE name_priority <= " + level + " and structure_id = ? \n";
		return sql;
	}


	private String indentifiersQuery() {
		String sql = "SELECT xref, prefix_id, source_id\n";
		sql = sql + "FROM Chem_Structure_Identifier\n";
		sql = sql + "WHERE structure_id = ?\n";
		return sql;
	}


	protected ResultSet indentifiers(final long structureId) throws SQLException {
		indentifiersQuery.setLong(1, structureId);
		return indentifiersQuery.executeQuery();
	}


	private String inchiQuery() {
		String sql = "SELECT inchi, inchikey\n";
		sql = sql + "FROM Chem_Structure\n";
		sql = sql + "WHERE structure_id = ?\n";
		return sql;
	}


	private ResultSet inchi(final long structureId) throws SQLException {
		inchiQuery.setLong(1, structureId);
		return inchiQuery.executeQuery();
	}


	private String structureMapQuery() {
		String sql = "SELECT structure_id\n";
		sql = sql + "FROM Chem_Structure_Map\n";
		sql = sql + "WHERE substance_id = ?\n";
		return sql;
	}


	private HashSet<Long> structures(long substanceId) throws SQLException {
		structureMapQuery.setLong(1, substanceId);
		final HashSet<Long> structures = new HashSet<>();
		ResultSet results = structureMapQuery.executeQuery();
		while (results.next()) {
			structures.add(results.getLong("structure_id"));
		}
		return structures;
	}


	private int countNames(final HashMap<String,NameCount> nameCounters) {
		int count = 0;
		for (NameCount counter : nameCounters.values()) {
			count = count + counter.count;
		}
		return count;
	}


	public String findBestName(final long bestStructureId) throws SQLException {
		// collect names
		bestNameQuery.setLong(1, bestStructureId);
		ResultSet results = bestNameQuery.executeQuery();
		final HashMap<String,HashMap<String,NameCount>> counts = new HashMap<>();
		while (results.next()) {
			String name = results.getString("name");
			String lowerCaseName = name.toLowerCase();
			HashMap<String,NameCount> nameCounts = counts.get(lowerCaseName);
			if (nameCounts == null) {
				nameCounts = new HashMap<String,NameCount>();
				counts.put(lowerCaseName, nameCounts);
			}
			NameCount counter = nameCounts.get(name);
			if (counter == null) {
				counter = new NameCount(name);
				nameCounts.put(name, counter);
			}
			counter.inc(results.getString("source_name"), results.getInt("name_priority"));
		}
		// find most frequent name
		int bestCount = 0;
		int minSourcePriority = Integer.MAX_VALUE;
		int minTypePriority = Integer.MAX_VALUE;
		String bestName = null;
		for (Map.Entry<String,HashMap<String,NameCount>> entry : counts.entrySet()) {
			int count = countNames(entry.getValue());
			// System.out.println(" " + entry.getKey() + ": " + count);
			int typePriority = minTypePriority(entry.getValue());
			if (bestCount < count || (bestCount == count && typePriority < minTypePriority) || (bestCount == count && typePriority == minTypePriority && minPriority(entry.getValue()) < minSourcePriority)) {
				bestCount = count;
				minSourcePriority = minPriority(entry.getValue());
				minTypePriority = minTypePriority(entry.getValue());
				bestName = entry.getValue().containsKey(entry.getKey()) ? entry.getKey() : mostFrequentName(entry.getValue());
			}
		}
		// System.out.println(" best name:" + bestName);
		return bestName;
	}


	private int minPriority(HashMap<String,NameCount> nameCounters) {
		int minSourcePriority = Integer.MAX_VALUE;
		for (NameCount counter : nameCounters.values()) {
			if (counter.minSourcePriority < minSourcePriority) {
				minSourcePriority = counter.minSourcePriority;
			}
		}
		return minSourcePriority;
	}


	private int minTypePriority(HashMap<String,NameCount> nameCounters) {
		int minTypePriority = Integer.MAX_VALUE;
		for (NameCount counter : nameCounters.values()) {
			if (counter.minTypePriority < minTypePriority) {
				minTypePriority = counter.minTypePriority;
			}
		}
		return minTypePriority;
	}


	private String mostFrequentName(final HashMap<String,NameCount> nameCounters) {
		int bestCount = 0;
		String bestName = null;
		for (NameCount counter : nameCounters.values()) {
			if (bestCount < counter.count) {
				bestCount = counter.count;
				bestName = counter.name;
			}
		}
		return bestName;
	}


	public String findAnyName(final long structureId) throws SQLException {
		namesQuery.setLong(1, structureId);
		final ResultSet results = namesQuery.executeQuery();
		String name = null;
		while (results.next()) {
			if (name == null)
				name = results.getString("name");
		}
		return name;
	}


	private long createSubstance(final long bestStructureId, final String queryName) throws SQLException {
		String bestName = findBestName(bestStructureId);
		if (bestName == null) {
			bestName = queryName;
		}
		else if (!bestName.toLowerCase().equals(queryName.toLowerCase())) {
			System.out.println("query name '" + queryName + "' != best name '" + bestName + "'");
			return getSubstanceId(bestName);
		}
		final long biolinkClassId = biolinkClassId(BiolinkClass.ChemicalEntity);
		final long substanceId = db.listElementTable.insert(bestName, biolinkClassId);
		db.chemStructureMapTable.insert(substanceId, bestStructureId, true);
		insertIdentifiers(substanceId, biolinkClassId, bestStructureId);
		return substanceId;
	}


	private void insertIdentifiers(long substanceId, long biolinkClassId, long bestStructureId) throws SQLException {
		final ResultSet identifiers = indentifiers(bestStructureId);
		final HashSet<String> ids = new HashSet<>();
		long firstSourceId = -1;
		while (identifiers.next()) {
			final String xref = identifiers.getString("xref");
			final long prefixId = identifiers.getLong("prefix_id");
			final long sourceId = identifiers.getLong("source_id");
			if (firstSourceId < 0) {
				firstSourceId = sourceId;
			}
			String key = "" + prefixId + ":" + xref;
			if (!ids.contains(key)) {
				db.listElementIdentifierTable.saveIdentifier(substanceId, xref, prefixId, sourceId);
				ids.add(key);
			}
		}
		identifiers.close();
		String inchi = null;
		String inchikey = null;
		final ResultSet inchiQueryResult = inchi(bestStructureId);
		while (inchiQueryResult.next()) {
			inchi = inchiQueryResult.getString("inchi");
			inchikey = inchiQueryResult.getString("inchikey");
		}
		long inchiPrefixId = db.curiePrefixTable.prefixId(biolinkClassId, "", "inchi");
		db.listElementIdentifierTable.saveIdentifier(substanceId, inchi, inchiPrefixId, firstSourceId);
		long inchikeyPrefixId = db.curiePrefixTable.prefixId(biolinkClassId, "", "inchikey");
		db.listElementIdentifierTable.saveIdentifier(substanceId, inchikey, inchikeyPrefixId, firstSourceId);
	}


	private void addNamesToSubstance(final long substanceId, final long bestStructureId, final ArrayList<StructureName> structures) throws SQLException {
		final HashSet<Long> structureIds = structures(substanceId);
		structureIds.add(bestStructureId);
		for (StructureName structureName : structures) {
			if (!structureIds.contains(structureName.structureId)) {
				db.chemStructureMapTable.insert(substanceId, structureName.structureId, false);
				structureIds.add(structureName.structureId);
			}
			db.listElementNameTable.saveName(substanceId, structureName.sourceId, structureName.nameId, structureName.nameTypeId, structureName.nameSourceId, structureName.language);
		}
	}


	private long findCorrectSubstanceId(ArrayList<StructureName> structures) throws SQLException {
		for (StructureName structureName : structures) {
			final long substanceId = getSubstanceId(structureName.structureId);
			if (substanceId > 0) {
				return substanceId;
			}
		}
		return -1;
	}


	/**
	 * Find best structure associated with the name.
	 * 
	 * @param name
	 * @return primary name for the best structure
	 * @throws SQLException
	 */
	private String resolve(String name) throws SQLException {
		ResultSet results = getStructures(name);
		ArrayList<StructureName> structures = new ArrayList<>();
		// count: source -> count
		final HashMap<String,SourceCount> counts = new HashMap<>();
		// sources: structure -> count
		final HashMap<Long,HashMap<String,SourceCount>> sources = new HashMap<>();
		long bestStructureId = -1;
		int level = 0;
		while (results.next()) {
			StructureName structure = new StructureName(results);
			if (resolvedName(structure)) {
				results.close();
				return name;
			}
			structures.add(structure);
			System.out.println("  " + structure);
			if (PRIORITY_LEVELS[level] < structure.priotity && bestStructureId < 0) {
				System.out.print("    Evaluate: @" + PRIORITY_LEVELS[level]);
				bestStructureId = evaluate(sources, false);
				System.out.println("    Evaluate: @" + PRIORITY_LEVELS[level] + "\t= " + bestStructureId);
			}
			while (level < PRIORITY_LEVELS.length && PRIORITY_LEVELS[level] < structure.priotity) {
				level = level + 1;
			}
			if (!sources.containsKey(structure.structureId)) {
				sources.put(structure.structureId, new HashMap<String,SourceCount>());
			}
			if (!sources.get(structure.structureId).containsKey(structure.sourceName)) {
				sources.get(structure.structureId).put(structure.sourceName, getSource(counts, structure.sourceName));
			}
		}
		if (bestStructureId < 0) {
			System.out.print("    Evaluate: @" + PRIORITY_LEVELS[level]);
			bestStructureId = evaluate(sources, true);
		}
		System.out.println("    Evaluate: @ end\t= " + bestStructureId);
		long substanceId = getSubstanceId(bestStructureId);
		if (substanceId < 0) {
			substanceId = createSubstance(bestStructureId, name);
		}
		if (substanceId < 0) {
			substanceId = findCorrectSubstanceId(structures);
		}
		if (substanceId > 0) {
			System.out.println(name + " saved");
			addNamesToSubstance(substanceId, bestStructureId, structures);
			return name;
		}
		return findBestName(bestStructureId);
	}


	private long evaluate(final HashMap<Long,HashMap<String,SourceCount>> sources, boolean allowTies) {
		if (sources.size() == 0) {
			return -1;
		}
		double bestCount = -1;
		int bestSourcePriority = -1;
		long bestStructureId = -1;
		boolean tie = false;
		for (Map.Entry<Long,HashMap<String,SourceCount>> entry : sources.entrySet()) {
			final double count = count(entry.getValue());
			System.out.print("\t" + count + " " + entry);
			if (bestCount < count) {
				bestCount = count;
				bestSourcePriority = minSourcePriority(entry.getValue());
				bestStructureId = entry.getKey();
				tie = false;
			}
			else if (bestCount == count) {
				tie = true;
				final int minSource = minSourcePriority(entry.getValue());
				if (minSource < bestSourcePriority) {
					bestSourcePriority = minSource;
					bestStructureId = entry.getKey();
				}
			}
		}
		System.out.println("\t= " + bestStructureId);
		if (tie && !allowTies) {
			return -1;
		}
		// do not make decision on a single source
		if (bestCount == 1.0 && !allowTies) {
			return -1;
		}
		return bestStructureId;
	}


	private SourceCount getSource(HashMap<String,SourceCount> counts, String sourceName) {
		SourceCount count = null;
		if (counts.containsKey(sourceName)) {
			count = counts.get(sourceName);
		}
		else {
			count = new SourceCount(sourceName);
			counts.put(sourceName, count);
		}
		count.inc();
		return count;
	}


	private double count(HashMap<String,SourceCount> counts) {
		double count = 0;
		for (SourceCount sourceCount : counts.values()) {
			count = count + sourceCount.count();
		}
		return count;
	}


	private int minSourcePriority(HashMap<String,SourceCount> counts) {
		int minPriority = Integer.MAX_VALUE;
		for (SourceCount sourceCount : counts.values()) {
			if (sourceCount.priority < minPriority) {
				minPriority = sourceCount.priority;
			}
		}
		return minPriority;
	}


	public void resolveStructures() throws SQLException {
		final ResultSet results = null;// allStructures();
		ArrayList<Long> mismatches = new ArrayList<>();
		while (results.next()) {
			final long structureId = results.getLong("structure_id");
			// long structureId = 256;
			String name = findBestName(structureId);
			System.out.println(name + " @ " + structureId);
			if (name != null) {
				String bestName = resolve(name);
				if (!bestName.equals(name)) {
					mismatches.add(structureId);
					System.out.println("WARNING - name mismatch @ " + structureId);
				}
				else {

				}
			}
		}
		for (long structId : mismatches) {
			System.out.println("revisit name mismatch @ " + structId);
			String name = findBestName(structId);
			resolve(name);
		}
		db.commit();
		db.close();
	}


	public static void main(String[] args) throws Exception {
		MoleProDB db = new MoleProDB(args[0]);
		SubstanceResolver resolver = new SubstanceResolver(db);
		resolver.resolveStructures();
	}


	private static class SourceCount {

		final String sourceName;
		final int priority;
		int count = 0;


		SourceCount(String sourceName) {
			super();
			this.sourceName = sourceName;
			this.priority = sourcePriority.get(sourceName);
		}


		public double count() {
			return 1.0 / count;
		}


		void inc() {
			count = count + 1;
		}


		@Override
		public String toString() {
			return count + "(" + sourceName + ")";
		}
	}


	private static class NameCount {

		final String name;
		int minSourcePriority = Integer.MAX_VALUE;
		int minTypePriority = Integer.MAX_VALUE;
		int count = 0;


		NameCount(String name) {
			super();
			this.name = name;
		}


		void inc(String sourceName, int typePriority) {
			count = count + 1;
			if (!sourcePriority.containsKey(sourceName)) {
				System.out.println("WARNING: No source priority for " + sourceName);
			}
			int priority = sourcePriority.getOrDefault(sourceName, Integer.MAX_VALUE);
			if (priority < minSourcePriority) {
				minSourcePriority = priority;
			}
			if (typePriority < minTypePriority) {
				minTypePriority = typePriority;
			}
		}


		@Override
		public String toString() {
			return count + "(" + name + ")";
		}
	}


	private static class StructureName {
		final long structureId;
		final long nameId;
		final long nameTypeId;
		final int sourceId;
		final String sourceName;
		final int nameSourceId;
		final int priotity;
		final String language;


		StructureName(ResultSet result) throws SQLException {
			structureId = result.getLong("structure_id");
			nameId = result.getLong("name_id");
			nameTypeId = result.getLong("name_type_id");
			sourceId = result.getInt("source_id");
			sourceName = result.getString("source_name");
			nameSourceId = result.getInt("name_source_id");
			priotity = result.getInt("name_priority");
			language = result.getString("language");
		}


		public String toString() {
			return "" + structureId + "\t" + sourceName + "\t" + priotity;
		}
	}
}
