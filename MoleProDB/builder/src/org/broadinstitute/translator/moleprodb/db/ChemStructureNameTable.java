package org.broadinstitute.translator.moleprodb.db;

public class ChemStructureNameTable extends NameMapTable {

	public ChemStructureNameTable(MoleProDB db) {
		super(db, "Chem_Structure_Name", "structure_id");
	}

}
