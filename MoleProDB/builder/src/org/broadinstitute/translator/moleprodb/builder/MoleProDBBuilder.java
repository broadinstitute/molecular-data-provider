package org.broadinstitute.translator.moleprodb.builder;

import org.broadinstitute.translator.moleprodb.db.MoleProDB;

public class MoleProDBBuilder {

	public static void main(String[] args) throws Exception {
		System.setProperty("java.io.tmpdir", "tmp");
		final String dbLocation = args[0];
		final String command = args[1];
		final MoleProDB db = new MoleProDB(dbLocation);

		if ("load-transformers".equals(command)) {
			new TransformerLoader(db).loadTransformers();
		}

		else if ("load-prefixes".equals(command)) {
			db.curiePrefixTable.loadPrefixes();
		}

		else if ("exec".equals(command)) {
			final String script = args[2];
			db.executeScript(script);
		}

		else if ("load-structures".equals(command)) {
			final String[] transformers = args[2].split(";");
			final String compounds = args[3];
			new StructureLoader(db).loadStructures(transformers, compounds);
		}

		else if ("load-compounds".equals(command)) {
			new SubstanceLoader(db).loadCompounds();
		}

		else if ("load-elements".equals(command)) {
			final String transformer = args[2];
			final String elements = args[3];
			final String[] mergeFields = mergeFields(args, 4);
			new ListElementLoader(db).loadElements(transformer, elements, mergeFields);
		}

		else if ("add-connections".equals(command)) {
			final String field = args[2];
			final String compounds = args[3];
			final String transformer = args[4];
			final String[] mergeFields = mergeFields(args, 5);
			final boolean noSubAttributes = args.length > 6 && "-noSubAttributes".equals(args[6]);
			new ConnectionLoader(db, !noSubAttributes).addConnections(field, compounds, transformer, mergeFields);
		}

		else if ("load-connections".equals(command)) {
			final String field = args[2];
			final String compounds = args[3];
			final String transformer = args[4];
			final String[] mergeFields = mergeFields(args, 5);
			final boolean noSubAttributes = args.length > 6 && "-noSubAttributes".equals(args[6]);
			new ConnectionLoader(db, !noSubAttributes).loadConnections(field, compounds, transformer, mergeFields);
		}

		else if ("merge-structures".equals(command)) {
			final String transformer = args[2];
			final MoleProDB srcDB = new MoleProDB(args[3]);
			new MoleProDBMerger(db).mergeStructures(transformer, srcDB);
		}

		else if ("merge-elements".equals(command)) {
			final String transformer = args[2];
			final MoleProDB srcDB = new MoleProDB(args[3]);
			final String[] mergeFields = mergeFields(args, 4);
			new MoleProDBMerger(db).mergeElements(transformer, srcDB, mergeFields);
		}

		else if ("merge-connections".equals(command)) {
			final String field = args[2];
			final String transformer = args[3];
			final MoleProDB srcDB = new MoleProDB(args[4]);
			String idField = null;
			if (args.length > 5) {
				idField = args[5];
			}
			new MoleProDBMerger(db).mergeConnections(transformer, field, srcDB, idField);
		}

		else if ("load-hierarchy".equals(command)) {
			final String hierarchyFile = args[2];
			new HierarchyLoader(db).loadHierarchy(hierarchyFile);
		}

		else {
			System.out.println("ERROR - unknown command " + command);
		}

		db.close();
		Loader.profileReport();
		System.out.println(String.join(" ", args));
	}


	private static String[] mergeFields(String[] args, int index) {
		if (args.length > index) {
			return args[index].split(",");
		}
		return null;
	}

}
