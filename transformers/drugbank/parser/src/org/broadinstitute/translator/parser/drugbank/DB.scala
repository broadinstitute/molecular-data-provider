package org.broadinstitute.translator.parser.drugbank

import java.sql.DriverManager;
import java.sql.Connection
import java.sql.Statement

object DB {

  private var connection: Connection = null

  private var lastDrugId = 0
  private var lastSynonymId = 0
  private var lastIdentifierId = 0
  private var lastTargetId = 0
  private var lastMapId = 0

  def createDB(database: String) {
    Class.forName("org.sqlite.JDBC")
    connection = DriverManager.getConnection("jdbc:sqlite:" + database)
    connection.setAutoCommit(false)
    createDrugTable()
    createSynonymTable()
    createIdentifierTable()
    createTargetTable()
    createTargetMapTable()
    commit()
  }

  private def executeUpdate(sql: String) {
    val stm = connection.createStatement()
    stm.executeUpdate(sql)
    stm.close()
  }

  def createDrugTable() {
    val createTableSQL = """
      CREATE TABLE DRUG(
        DRUG_ID       INT   PRIMARY KEY NOT NULL,
        DRUG_BANK_ID  TEXT  NOT NULL,
        DRUG_TYPE     TEXT  NOT NULL,
        DRUG_NAME          TEXT  NOT NULL
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertDrug(drugbankId: String, drugType: String, name: String): Int = {
    lastDrugId = lastDrugId + 1
    val drugId = lastDrugId

    val insertSQL = s"""
      INSERT INTO DRUG (DRUG_ID, DRUG_BANK_ID, DRUG_TYPE, DRUG_NAME)
      VALUES (${drugId}, ${f(drugbankId)}, ${f(drugType)}, ${f(name)})
      """
    executeUpdate(insertSQL)
    return drugId
  }

  def createSynonymTable() {
    val createTableSQL = """
      CREATE TABLE SYNONYM(
        SYNONYM_ID  INT   PRIMARY KEY NOT NULL,
        DRUG_ID     INT   NOT NULL,
        SYNONYM     TEXT  COLLATE NOCASE NOT NULL,
        FOREIGN KEY(DRUG_ID) REFERENCES DRUG(DRUG_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertSynonym(drugId: Int, synonym: String): Int = {
    lastSynonymId = lastSynonymId + 1
    val nameId = lastSynonymId

    val insertSQL = s"""
      INSERT INTO SYNONYM (SYNONYM_ID, DRUG_ID, SYNONYM)
      VALUES (${lastSynonymId}, ${drugId}, ${f(synonym)})
      """
    executeUpdate(insertSQL)
    return nameId
  }

  def createIdentifierTable() {
    val createTableSQL = """
      CREATE TABLE IDENTIFIER(
        IDENTIFIER_ID  INT   PRIMARY KEY NOT NULL,
        DRUG_ID        INT   NOT NULL,
        IDENTIFIER     TEXT  NOT NULL,
        SOURCE         TEXT  NOT NULL,
        FOREIGN KEY(DRUG_ID) REFERENCES DRUG(DRUG_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertIdentifier(drugId: Int, identifier: String, source: String): Int = {
    lastIdentifierId = lastIdentifierId + 1
    val identifierId = lastIdentifierId

    val insertSQL = s"""
      INSERT INTO IDENTIFIER (IDENTIFIER_ID, DRUG_ID, IDENTIFIER, SOURCE)
      VALUES (${identifierId}, ${drugId}, ${f(identifier)}, ${f(source)})
      """
    executeUpdate(insertSQL)
    return identifierId
  }

  def createTargetTable() {
    val createTableSQL = """
      CREATE TABLE TARGET(
        TARGET_ID            INT   PRIMARY KEY NOT NULL,
        DRUG_BANK_TARGET_ID  TEXT  NOT NULL,
        UNIPROT              TEXT,
        GENE_ID              TEXT,
        NAME                 TEXT  NOT NULL
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertTarget(drugBankTargetId: String, uniprot: Option[String], geneId: Option[String], name: String): Int = {
    lastTargetId = lastTargetId + 1
    val targetId = lastTargetId

    val insertSQL = s"""
      INSERT INTO TARGET (TARGET_ID, DRUG_BANK_TARGET_ID, UNIPROT, GENE_ID, NAME)
      VALUES (${targetId}, ${f(drugBankTargetId)}, ${f(uniprot)}, ${f(geneId)}, ${f(name)})
      """
    executeUpdate(insertSQL)
    return targetId
  }

  def createTargetMapTable() {
    val createTableSQL = """
      CREATE TABLE TARGET_MAP(
        MAP_ID     INT PRIMARY KEY NOT NULL,
        DRUG_ID    INT NOT NULL,
        TARGET_ID  INT NOT NULL,
        ACTIONS    TEXT,
        FOREIGN KEY(DRUG_ID) REFERENCES DRUG(DRUG_ID),
        FOREIGN KEY(TARGET_ID) REFERENCES TARGET(TARGET_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertTargetMap(drugId: Int, targetId: Int, actions: String): Int = {
    lastMapId = lastMapId + 1
    val mapId = lastMapId

    val insertSQL = s"""
      INSERT INTO TARGET_MAP (MAP_ID, DRUG_ID, TARGET_ID, ACTIONS)
      VALUES (${mapId}, ${drugId}, ${targetId}, ${f(actions)})
      """
    executeUpdate(insertSQL)
    return mapId
  }

  def createIndexes() {
    createIndex("DRUG", "DRUG_ID")
    createIndex("DRUG", "DRUG_BANK_ID")
    createIndex("DRUG", "DRUG_NAME")

    createIndex("SYNONYM", "DRUG_ID")
    createIndex("SYNONYM", "SYNONYM")

    createIndex("IDENTIFIER", "DRUG_ID")
    createIndex("IDENTIFIER", "IDENTIFIER")

    createIndex("TARGET", "TARGET_ID")
    createIndex("TARGET", "UNIPROT")
    createIndex("TARGET", "GENE_ID")

    createIndex("TARGET_MAP", "DRUG_ID")
    createIndex("TARGET_MAP", "TARGET_ID")

  }

  def createIndex(table: String, column: String) {
    val sql = s"CREATE INDEX ${table}_${column}_IDX ON ${table} (${column})"
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