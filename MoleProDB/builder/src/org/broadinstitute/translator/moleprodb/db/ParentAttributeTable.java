package org.broadinstitute.translator.moleprodb.db;

public class ParentAttributeTable extends AttributeMapTable {

	public ParentAttributeTable(MoleProDB db) {
		super(db, "Parent_Attribute", "parent_attribute_id");
	}

}
