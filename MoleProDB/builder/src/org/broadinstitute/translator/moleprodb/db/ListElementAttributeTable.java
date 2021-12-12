package org.broadinstitute.translator.moleprodb.db;

public class ListElementAttributeTable extends AttributeMapTable {

	public ListElementAttributeTable(MoleProDB db) {
		super(db, "List_Element_Attribute", "list_element_id");
	}

}
