package org.broadinstitute.translator.moleprodb.builder;

import java.util.Arrays;
import java.util.HashSet;

import org.broadinstitute.translator.moleprodb.db.MoleProDB;

public class MoleProDBBuilder {

	public static void main(String[] args) throws Exception {
		final String dbLocation = args[0];
		final String command = args[1];
		final MoleProDB db = new MoleProDB(dbLocation);
		if ("load-transformers".equals(command)) {
			new TransformerLoader(db).loadTransformers();
		}
		if ("load-prefixes".equals(command)) {
			db.curiePrefixTable.loadPrefixes();
		}
		if ("exec".equals(command)) {
			final String script = args[2];
			db.executeScript(script);
		}
		if ("load-structures".equals(command)) {
			final String[] transformers = args[2].split(";");
			final String compounds = args[3];
			new StructureLoader(db).loadStructures(transformers, compounds);
		}
		if ("load-compounds".equals(command)) {
			new SubstanceLoader(db).loadCompounds();
		}
		if ("load-elements".equals(command)) {
			final String transformer = args[2];
			final String elements = args[3];
			HashSet<String> mergeFields = null;
			if (args.length > 4) {
				final String[] mergeFieldsArg = args[4].split(",");
				mergeFields = new HashSet<String>(Arrays.asList(mergeFieldsArg));
			}
			new ListElementLoader(db).loadElements(transformer, elements, mergeFields);
		}
		if ("load-connections".equals(command)) {
			final String field = args[2];
			final String compounds = args[3];
			final String transformer = args[4];
			new ConnectionLoader(db).loadConnections(field, compounds, transformer);
		}
		if ("merge-structures".equals(command)) {
			final String transformer = args[2];
			final MoleProDB srcDB = new MoleProDB(args[3]);
			new MoleProDBMerger(db).mergeStructures(transformer, srcDB);
		}
		if ("merge-elements".equals(command)) {
			final String transformer = args[2];
			final MoleProDB srcDB = new MoleProDB(args[3]);
			HashSet<String> mergeFields = null;
			if (args.length > 4) {
				final String[] mergeFieldsArg = args[4].split(",");
				mergeFields = new HashSet<String>(Arrays.asList(mergeFieldsArg));
			}
			new MoleProDBMerger(db).mergeElements(transformer, srcDB, mergeFields);
		}
		if ("merge-connections".equals(command)) {
			final String field = args[2];
			final String transformer = args[3];
			final MoleProDB srcDB = new MoleProDB(args[4]);
			String idField = null;
			if (args.length > 5) {
				idField = args[5];
			}
			new MoleProDBMerger(db).mergeConnections(transformer, field, srcDB, idField);
		}
		if ("load-hierarchy".equals(command)) {
			final String hierarchyFile = args[2];
			new HierarchyLoader(db).loadHierarchy(hierarchyFile);
		}
		db.close();
		Loader.profileReport();
		System.out.println(String.join(" ", args));
	}

}
