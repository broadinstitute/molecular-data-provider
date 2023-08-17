package org.broadinstitute.translator.moleprodb.db;

import java.sql.SQLException;

public class InfoResTable extends MoleProTable {

	public InfoResTable(MoleProDB moleProDB) {
		super(moleProDB, "Infores");
	}


	private void insert(String infores) throws SQLException {
		String sql = "INSERT INTO Infores(resource) VALUES (" + f(infores) + ")";
		executeUpdate(sql);
	}


	public Long infoResId(String infores) throws SQLException {
		if (infores != null && infores.startsWith("infores:")) {
			final long inforesId = findInfoRes(infores);
			if (inforesId > 0) {
				return inforesId;
			}
			insert(infores);
			return findInfoRes(infores);
		}
		else {
			return null;
		}
	}


	private long findInfoRes(String infores) {
		return super.findId("infores_id", "resource", infores);
	}
}
