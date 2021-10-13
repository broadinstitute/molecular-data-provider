package org.broadinstitute.translator.moleprodb.db;

public class ListElementNameTable extends NameMapTable {

	public ListElementNameTable(MoleProDB db) {
		super(db, "List_Element_Name", "list_element_id");
	}
}
