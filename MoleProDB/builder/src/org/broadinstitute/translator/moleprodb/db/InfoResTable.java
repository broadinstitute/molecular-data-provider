package org.broadinstitute.translator.moleprodb.db;

import java.sql.SQLException;
import transformer.mapping.MappedInfoRes;

public class InfoResTable extends MoleProTable {

	public InfoResTable(MoleProDB moleProDB) {
		super(moleProDB, "Infores");
	}


	private void insert(String infores) throws SQLException {
		String sql = "INSERT INTO Infores(resource) VALUES (" + f(infores) + ")";
		executeUpdate(sql);
	}


	public Long InfoResId(String transformerName) throws SQLException {
		String infores = MappedInfoRes.map(transformerName);
		if (infores.startsWith("infores:")) {
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
