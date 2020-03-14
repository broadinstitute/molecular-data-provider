package org.broadinstitute.translator.parser.chembank

import java.sql.DriverManager;
import java.sql.Connection
import java.sql.Statement

object DB {

  private var connection: Connection = null

  var lastNameId = 0

  def createDB(database: String) {
    Class.forName("org.sqlite.JDBC")
    connection = DriverManager.getConnection("jdbc:sqlite:" + database)
    connection.setAutoCommit(false)
    createCompoundTable()
    createCompoundNameTable()
    createCompoundNameTypeTable()
  }

  def createCompoundTable() {
    val createTableSQL = """
      CREATE TABLE COMPOUND (
        CHEMBANK_ID  INT   PRIMARY KEY NOT NULL UNIQUE,
        SMILES       TEXT  NOT NULL,
        INCHI        TEXT  NOT NULL UNIQUE,
        INCHI_KEY    TEXT  NOT NULL
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertCompound(chembankId: Int, smiles: String, inchi: String, inchikey: String): Int = {

    val insertSQL = s"""
      INSERT INTO COMPOUND (CHEMBANK_ID, SMILES, INCHI, INCHI_KEY)
      VALUES (${chembankId}, ${f(smiles)}, ${f(inchi)}, ${f(inchikey)})
      """
    executeUpdate(insertSQL)
    return chembankId
  }

  def createCompoundNameTable() {
    val createTableSQL = """
      CREATE TABLE COMPOUND_NAME (
        CPD_NAME_ID      INT   PRIMARY KEY NOT NULL UNIQUE,
        CHEMBANK_ID      INT   NOT NULL,
        CPD_NAME         TEXT  NOT NULL  COLLATE NOCASE,
        CPD_NAME_TYPE_ID INT   NOT NULL,
        FOREIGN KEY(CHEMBANK_ID) REFERENCES COMPOUND(CHEMBANK_ID),
        FOREIGN KEY(CPD_NAME_TYPE_ID) REFERENCES COMPOUND_NAME_TYPE(CPD_NAME_TYPE_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertName(chembankId: Int, name: String, nameType: Int): Int = {
    lastNameId = lastNameId + 1
    val diseaseId = lastNameId
    val insertSQL = s"""
      INSERT INTO COMPOUND_NAME (CPD_NAME_ID, CHEMBANK_ID, CPD_NAME, CPD_NAME_TYPE_ID)
      VALUES (${lastNameId}, ${chembankId}, ${f(name)}, ${nameType})
      """
    executeUpdate(insertSQL)
    return lastNameId
  }

  def createCompoundNameTypeTable() {
    val createTableSQL = """
      CREATE TABLE COMPOUND_NAME_TYPE (
        CPD_NAME_TYPE_ID        INT   PRIMARY KEY NOT NULL UNIQUE,
        CPD_NAME_TYPE           TEXT  NOT NULL UNIQUE,
        CPD_NAME_TYPE_PRIORITY  INT   NOT NULL
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertType(nameType: Int, name: String, priority: Int): Int = {
    val insertSQL = s"""
      INSERT INTO COMPOUND_NAME_TYPE (CPD_NAME_TYPE_ID, CPD_NAME_TYPE, CPD_NAME_TYPE_PRIORITY)
      VALUES (${nameType}, ${f(name)}, ${priority})
      """
    executeUpdate(insertSQL)
    return nameType
  }

  private def executeUpdate(sql: String) {
    val stm = connection.createStatement()
    stm.executeUpdate(sql)
    stm.close()
  }

  def createIndexes() {
    createIndex("CPD_ID","COMPOUND", "CHEMBANK_ID", true)
    createIndex("CPD_INCHI","COMPOUND", "INCHI", true)
    createIndex("CPD_INCHI_KEY","COMPOUND", "INCHI_KEY")

    createIndex("NAME_ID","COMPOUND_NAME", "CPD_NAME_ID", true)
    createIndex("NAME_CPD_ID","COMPOUND_NAME", "CHEMBANK_ID")
    createIndex("NAME","COMPOUND_NAME", "CPD_NAME")
    createIndex("NAME_TYPE_ID","COMPOUND_NAME", "CPD_NAME_TYPE_ID")

    createIndex("TYPE_ID","COMPOUND_NAME_TYPE", "CPD_NAME_TYPE_ID", true)
    createIndex("TYPE","COMPOUND_NAME_TYPE", "CPD_NAME_TYPE", true)
    createIndex("TYPE_PRIORITY", "COMPOUND_NAME_TYPE", "CPD_NAME_TYPE_PRIORITY", true)
  }

  def createIndex(name: String, table: String, column: String, unique: Boolean = false) {
    val sql = unique match {
      case false => s"CREATE INDEX ${name}_IDX ON ${table} (${column})"
      case true  => s"CREATE UNIQUE INDEX ${name}_IDX ON ${table} (${column})"
    }
    executeUpdate(sql)
  }

  def f(str: String) = str match {
    case null => "NULL"
    case _    => "'" + str.replace("'", "''") + "'"
  }

  def f(str: Option[String]) = str match {
    case None      => "NULL"
    case Some(str) => "'" + str.replace("'", "''") + "'"
  }

  def commit() {
    connection.commit()
  }

  def close() = {
    commit()
    connection.close()
  }

}
