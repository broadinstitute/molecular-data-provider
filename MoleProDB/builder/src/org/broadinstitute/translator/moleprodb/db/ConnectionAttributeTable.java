package org.broadinstitute.translator.moleprodb.db;

public class ConnectionAttributeTable extends AttributeMapTable {

	public ConnectionAttributeTable(MoleProDB db) {
		super(db, "Connection_Attribute", "connection_id");
	}

}
