package org.broadinstitute.translator.moleprodb.db;

import java.io.BufferedReader;
import java.io.FileReader;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

public class MoleProDB {

	private Connection connection;
	private final String location;

	public final BiolinkClassTable biolinkClassTable;
	public final ChemStructureIdentifierTable chemStructureIdentifierTable;
	public final ChemStructureNameTable chemStructureNameTable;
	public final ChemStructureTable chemStructureTable;
	public final CuriePrefixTable curiePrefixTable;
	public final ListElementIdentifierTable listElementIdentifierTable;
	public final ListElementTable listElementTable;
	public final NameTable nameTable;
	public final NameTypeTable nameTypeTable;
	public final NameSourceTable nameSourceTable;
	public final SourceTable sourceTable;
	public final InfoResTable inforesTable;
	public final AttributeTypeTable attributeTypeTable;
	public final AttributeTable attributeTable;
	public final ListElementAttributeTable listElementAttributeTable;
	public final ChemStructureAttributeTable chemStructureAttributeTable;
	public final ParentAttributeTable parentAttributeTable;
	public final ElementHierarchyTable elementHierarchyTable;
	public final PredicateTable predicateTable;
	public final ConnectionTable connectionTable;
	public final ListElementNameTable listElementNameTable;
	public final ConnectionAttributeTable connectionAttributeTable;
	public final ChemStructureMapTable chemStructureMapTable;
	public final QualifierTable qualifierTable;
	public final QualifierMapTable qualifierMapTable;
	public final QualifierSetTable qualifierSetTable;

	public static final HashMap<String,Long> profile = new HashMap<>();


	public MoleProDB(final String location) throws Exception {
		this.location = location;
		Class.forName("org.sqlite.JDBC");
		connection = DriverManager.getConnection("jdbc:sqlite:" + location);
		connection.setAutoCommit(false);

		biolinkClassTable = new BiolinkClassTable(this);
		chemStructureIdentifierTable = new ChemStructureIdentifierTable(this);
		chemStructureNameTable = new ChemStructureNameTable(this);
		chemStructureTable = new ChemStructureTable(this);
		curiePrefixTable = new CuriePrefixTable(this);
		listElementIdentifierTable = new ListElementIdentifierTable(this);
		listElementTable = new ListElementTable(this);
		nameTable = new NameTable(this);
		nameTypeTable = new NameTypeTable(this);
		nameSourceTable = new NameSourceTable(this);
		sourceTable = new SourceTable(this);
		inforesTable = new InfoResTable(this);
		attributeTypeTable = new AttributeTypeTable(this);
		attributeTable = new AttributeTable(this);
		listElementAttributeTable = new ListElementAttributeTable(this);
		chemStructureAttributeTable = new ChemStructureAttributeTable(this);
		parentAttributeTable = new ParentAttributeTable(this);
		elementHierarchyTable = new ElementHierarchyTable(this);
		predicateTable = new PredicateTable(this);
		connectionTable = new ConnectionTable(this);
		listElementNameTable = new ListElementNameTable(this);
		connectionAttributeTable = new ConnectionAttributeTable(this);
		chemStructureMapTable = new ChemStructureMapTable(this);
		qualifierTable = new QualifierTable(this);
		qualifierMapTable = new QualifierMapTable(this);
		qualifierSetTable = new QualifierSetTable(this);
	}


	void executeUpdate(final String sql) throws SQLException {
		final Statement stm = connection.createStatement();
		stm.executeUpdate(sql);
		stm.close();
	}


	public ResultSet executeQuery(final String sql) throws SQLException {
		final Statement stm = connection.createStatement();
		return stm.executeQuery(sql);
	}


	public PreparedStatement prepareStatement(String sql) throws SQLException {
		return connection.prepareStatement(sql);
	}


	public void executeScript(final String filename) throws Exception {
		StringBuilder sb = new StringBuilder();
		final BufferedReader input = new BufferedReader(new FileReader(filename));
		int i = 0;
		try {
			for (String line = input.readLine(); line != null; line = input.readLine()) {
				sb.append(line);
				if (line.trim().endsWith(";")) {
					i = i + 1;
					System.out.println("execute # " + i);
					executeUpdate(sb.toString());
					sb = new StringBuilder();
				}
			}
			commit();
		}
		catch (Exception e) {
			System.out.println(e);
		}
		finally {
			connection.rollback();
			input.close();
		}
	}


	public void rollback() throws SQLException {
		connection.rollback();
	}


	public void commit() throws SQLException {
		connection.commit();
	}


	public void close() throws SQLException {
		connection.close();
	}


	public void reconnect() throws SQLException {
		connection.close();
		connection = null;
		connection = DriverManager.getConnection("jdbc:sqlite:" + location);
		connection.setAutoCommit(false);
	}


	public static void profile(String transformerName, Date start) {
		final long responseTime = (new Date()).getTime() - start.getTime();
		long sumTime = profile.getOrDefault(transformerName, 0L);
		profile.put(transformerName, sumTime + responseTime);
	}


	public static void profileReport() {
		System.out.println();
		for (Map.Entry<String,Long> entry : profile.entrySet()) {
			final String transformer = entry.getKey();
			final long responseTime = entry.getValue();
			System.out.println(transformer + "\t" + responseTime);
		}
	}
}
