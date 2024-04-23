package org.broadinstitute.translator.parser.drugcentral

import java.sql.DriverManager;
import java.sql.Connection
import java.sql.Statement

object DB {

  private var connection: Connection = null

  var lastDiseaseId = 0
  var lastIndicationId = 0

  def createDB(database: String) {
    Class.forName("org.sqlite.JDBC")
    connection = DriverManager.getConnection("jdbc:sqlite:" + database)
    connection.setAutoCommit(false)
    createDrugTable()
    createDiseaseTable()
    createIndicationTable()
  }

  private def executeUpdate(sql: String) {
    val stm = connection.createStatement()
    stm.executeUpdate(sql)
    stm.close()
  }

  def createDrugTable() {
    val createTableSQL = """
      CREATE TABLE DRUG(
        DRUG_CENTRAL_ID  INT   PRIMARY KEY NOT NULL,
        DRUG_NAME        TEXT  COLLATE NOCASE NOT NULL,
        CAS_RN           TEXT  NOT NULL,
        SMILES           TEXT  NOT NULL,
        INCHI            TEXT  NOT NULL,
        INCHI_KEY        TEXT  NOT NULL
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertDrug(drugId: Int, name: String, cas: String, smiles: String, inchi: String, inchikey: String): Int = {

    val insertSQL = s"""
      INSERT INTO DRUG (DRUG_CENTRAL_ID, DRUG_NAME, CAS_RN, SMILES, INCHI, INCHI_KEY)
      VALUES (${drugId}, ${f(name)}, ${f(cas)}, ${f(smiles)}, ${f(inchi)}, ${f(inchikey)})
      """
    executeUpdate(insertSQL)
    return drugId
  }

  def createDiseaseTable() {
    val createTableSQL = """
      CREATE TABLE DISEASE(
        DISEASE_ID    INT  PRIMARY KEY NOT NULL,
        DISEASE_NAME  TEXT COLLATE NOCASE NOT NULL,
        MONDO_ID      TEXT COLLATE NOCASE,
        UMLS_CUI      TEXT COLLATE NOCASE,
        SNOMEDCT_CUI  TEXT COLLATE NOCASE,
        DOID          TEXT COLLATE NOCASE
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertDisease(name: String, mondoId: Option[String], umlsCode: Option[String], snomedCtId: Option[String], doid: Option[String]): Int = {
    lastDiseaseId = lastDiseaseId + 1
    val diseaseId = lastDiseaseId

    val insertSQL = s"""
      INSERT INTO DISEASE (DISEASE_ID, DISEASE_NAME, MONDO_ID, UMLS_CUI, SNOMEDCT_CUI, DOID)
      VALUES (${diseaseId}, ${f(name)}, ${f(mondoId)}, ${f(umlsCode)}, ${f(snomedCtId)}, ${f(doid)})
      """
    executeUpdate(insertSQL)
    return diseaseId
  }

  def createIndicationTable() {
    val createTableSQL = """
      CREATE TABLE INDICATION (
        INDICATION_ID    INT PRIMARY KEY NOT NULL,
        DRUG_CENTRAL_ID  INT NOT NULL,
        DISEASE_ID       INT NOT NULL,
        FOREIGN KEY(DRUG_CENTRAL_ID) REFERENCES DRUG(DRUG_CENTRAL_ID),
        FOREIGN KEY(DISEASE_ID) REFERENCES DISEASE(DISEASE_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertIndication(drugId: Int, diseaseId: Int): Int = {
    lastIndicationId = lastIndicationId + 1
    val mapId = lastIndicationId

    val insertSQL = s"""
      INSERT INTO INDICATION (INDICATION_ID, DRUG_CENTRAL_ID, DISEASE_ID)
      VALUES (${mapId}, ${drugId}, ${diseaseId})
      """
    executeUpdate(insertSQL)
    return mapId
  }

  def createIndexes() {
    createIndex("DRUG", "DRUG_CENTRAL_ID")
    createIndex("DRUG", "DRUG_NAME")
    createIndex("DRUG", "INCHI")

    createIndex("DISEASE", "DISEASE_ID")
    createIndex("DISEASE", "DISEASE_NAME")
    createIndex("DISEASE", "MONDO_ID")
    createIndex("DISEASE", "UMLS_CUI")
    createIndex("DISEASE", "SNOMEDCT_CUI")
    createIndex("DISEASE", "DOID")

    createIndex("INDICATION", "DISEASE_ID")
    createIndex("INDICATION", "DRUG_CENTRAL_ID")
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
