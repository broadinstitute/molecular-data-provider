package org.broadinstitute.translator.moleprodb.db;

public class ChemStructureAttributeTable extends AttributeMapTable {

	public ChemStructureAttributeTable(MoleProDB db) {
		super(db, "Chem_Structure_Attribute", "structure_id");
	}

}
