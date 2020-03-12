package org.broadinstitute.translator.parser.ctrp

object DB extends DbBuilder {

  var lastCorrId = 0

  override def createDB(database: String) {
    super.createDB(database)
    createCompoundTable()
    createContextTable()
    createCorrelationTable()
  }

  def createCompoundTable() {
    val createTableSQL = """
      CREATE TABLE COMPOUND (
        CPD_ID        INT   PRIMARY KEY NOT NULL UNIQUE,
        COMPOUND_NAME TEXT  NOT NULL COLLATE NOCASE UNIQUE,
        BROAD_CPD_ID  TEXT  NOT NULL COLLATE NOCASE UNIQUE,
        PUBCHEM_CID   TEXT  NOT NULL,
        SMILES        TEXT  NOT NULL,
        INCHI         TEXT  UNIQUE,
        INCHI_KEY     TEXT  
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertCompound(cpdId: Int, name: String, broadCpdId: String, cid: String, smiles: String, inchi: String, inchikey: String): Int = {

    val insertSQL = s"""
      INSERT INTO COMPOUND (CPD_ID, COMPOUND_NAME, BROAD_CPD_ID, PUBCHEM_CID, SMILES, INCHI, INCHI_KEY)
      VALUES (${cpdId}, ${f(name)}, ${f(broadCpdId)}, ${f(cid)}, ${f(smiles)}, ${f(inchi)}, ${f(inchikey)})
      """
    executeUpdate(insertSQL)
    return cpdId
  }

  def createContextTable() {
    val createTableSQL = """
      CREATE TABLE CONTEXT (
        CONTEXT_ID    INT   PRIMARY KEY  NOT NULL  UNIQUE,
        CONTEXT_NAME  TEXT  NOT NULL  UNIQUE  COLLATE NOCASE
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertContext(contextId: Int, contextName: String): Int = {

    val insertSQL = s"""
      INSERT INTO CONTEXT (CONTEXT_ID, CONTEXT_NAME)
      VALUES (${contextId}, ${f(contextName)})
      """
    executeUpdate(insertSQL)
    return contextId
  }

  def createCorrelationTable() {
    val createTableSQL = """
      CREATE TABLE CORRELATION (
        CORRELATION_ID     INT  PRIMARY KEY NOT NULL,
        CPD_ID_1           INT  NOT NULL,
        CPD_ID_2           INT  NOT NULL,
        CONTEXT_ID         INT  NOT NULL,
        N_SAMPLES          INT  NOT NULL,
        CORRELATION_VALUE  REAL NOT NULL,
        FISHER_Z           REAL NOT NULL,
        FDR                REAL NOT NULL,
        FOREIGN KEY(CPD_ID_1) REFERENCES COMPOUND(CPD_ID),
        FOREIGN KEY(CPD_ID_2) REFERENCES COMPOUND(CPD_ID),
        FOREIGN KEY(CONTEXT_ID) REFERENCES CONTEXT(CONTEXT_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertTargetMap(compoundId1: Int, compoundId2: Int, contextId: Int, nSamples: Int, correlation: Double, fisherZ: Double, fdr: Double): Int = {
    lastCorrId = lastCorrId + 1
    val mapId = lastCorrId

    val insertSQL = s"""
      INSERT INTO CORRELATION (CORRELATION_ID, CPD_ID_1, CPD_ID_2, CONTEXT_ID, N_SAMPLES, CORRELATION_VALUE, FISHER_Z, FDR)
      VALUES (${lastCorrId}, ${compoundId1}, ${compoundId2}, ${contextId}, ${nSamples}, ${correlation}, ${fisherZ}, ${fdr})
      """
    executeUpdate(insertSQL)
    return lastCorrId
  }

  def createIndexes() {
    createIndex("COMPOUND", "CPD_ID", UNIQUE)
    createIndex("COMPOUND", "INCHI", UNIQUE)
    createIndex("COMPOUND", "INCHI_KEY")

    createIndex("CONTEXT", "CONTEXT_ID", UNIQUE)
    createIndex("CONTEXT", "CONTEXT_NAME", UNIQUE)

    createIndex("CORRELATION", "CPD_ID_1")
    createIndex("CORRELATION", "CONTEXT_ID")
  }
}
