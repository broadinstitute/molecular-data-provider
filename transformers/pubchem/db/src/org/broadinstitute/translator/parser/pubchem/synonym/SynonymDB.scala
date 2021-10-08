package org.broadinstitute.translator.parser.pubchem.synonym

import org.broadinstitute.translator.parser.pubchem.db.SQLite

object SynonymDB extends SQLite("data/PubChemSynonyms.sqlite") {

  def createDB() {
    try {
      createSynIdTable()
      createSynTypeTable()
      createSynTypeDictTable()
      createSynValueTable()
      commit()
    }
    finally {
      close()
    }
  }

  def createSynIdTable() {
    val createTableSQL = """
      CREATE TABLE SYNONYM_ID (
        SYNONYM_MD5_ID  TEXT  NOT NULL,
        CID             INT   NOT NULL
      );
    """
    executeUpdate(createTableSQL)
    println("SYNONYM_ID table created")
  }

  def createSynTypeTable() {
    val createTableSQL = """
      CREATE TABLE SYNONYM_TYPE (
        SYNONYM_MD5_ID  TEXT  NOT NULL,
        SYNONYM_TYPE    TEXT  NOT NULL
      );
    """
    executeUpdate(createTableSQL)
    println("SYNONYM_TYPE table created")
  }

  private var synonymTypeId = 0

  private var synonymTypes = Set[String]()

  def createSynTypeDictTable() {
    val createTableSQL = """
      CREATE TABLE SYNONYM_TYPE_DICT (
        SYNONYM_TYPE_ID  INT PRIMARY KEY  NOT NULL,
        SYNONYM_TYPE     TEXT  NOT NULL
      );
    """
    executeUpdate(createTableSQL)
    println("SYNONYM_TYPE_DICT table created")
  }

  def createSynValueTable() {
    val createTableSQL = """
      CREATE TABLE SYNONYM_VALUE (
        SYNONYM_MD5_ID  TEXT  NOT NULL,
        VALUE           TEXT  NOT NULL,
        LANGUAGE        TEXT
      );
    """
    executeUpdate(createTableSQL)
    println("SYNONYM_VALUE table created")
  }

  def insertId(synId: String, cid: Int) {
    val insertSQL = s"""
      INSERT INTO SYNONYM_ID (SYNONYM_MD5_ID, CID)
      VALUES (${f(synId)}, ${cid})
      """
    executeUpdate(insertSQL)
  }

  def insertType(synId: String, synType: String) {
    val insertSQL = s"""
      INSERT INTO SYNONYM_TYPE (SYNONYM_MD5_ID, SYNONYM_TYPE)
      VALUES (${f(synId)}, ${f(synType)})
      """
    executeUpdate(insertSQL)
    if (synonymTypeId == 0) {
      loadSynTypes()
    }
    if (!synonymTypes.contains(synType)) {
      addSynType(synType)
    }
  }

  private def loadSynTypes() {
    for (result <- SynonymDB.getSynonymTypes()) {
      synonymTypes +=  result.getString("SYNONYM_TYPE") 
      synonymTypeId = math.max(synonymTypeId, result.getInt("SYNONYM_TYPE_ID"))
    }
    println("loaded " + synonymTypeId + " synonym types")
  }

  private def addSynType(synType: String) {
    synonymTypeId += 1
    synonymTypes += synType
    val insertSQL = s"""
      INSERT INTO SYNONYM_TYPE_DICT (SYNONYM_TYPE_ID, SYNONYM_TYPE)
      VALUES (${synonymTypeId}, ${f(synType)})
      """
    executeUpdate(insertSQL)
  }

  def insertValue(synId: String, synValue: String, synLang: String) {
    val insertSQL = s"""
      INSERT INTO SYNONYM_VALUE (SYNONYM_MD5_ID, VALUE, LANGUAGE)
      VALUES (${f(synId)}, ${f(synValue)}, ${f(synLang)})
      """
    executeUpdate(insertSQL)
  }

  def buildIndexes() = {
    try {
      createIndex("SYNONYM_ID", "SYNONYM_MD5_ID")
      commit()
      println("Created index SYNONYM_ID[SYNONYM_MD5_ID]")
      createIndex("SYNONYM_TYPE", "SYNONYM_MD5_ID")
      commit()
      println("Created index SYNONYM_TYPE[SYNONYM_MD5_ID]")
      createIndex("SYNONYM_VALUE", "SYNONYM_MD5_ID")
      commit()
      println("Created index SYNONYM_VALUE[SYNONYM_MD5_ID]")
    }
    finally {
      close()
    }
  }

  def allSynonyms() = executeQuery("SELECT SYNONYM_MD5_ID, CID FROM SYNONYM_ID")

  def synonymCount(synonymId: String, cid: Long): Int = {
    val sql = s"SELECT SYNONYM_MD5_ID, CID FROM SYNONYM_ID WHERE SYNONYM_MD5_ID = ${f(synonymId)} AND CID = ${cid}"
    var count = 0
    for (result <- queryResults(sql)) {
      count += 1
    }
    return count
  }
  
  def synonymType(synonymId: String) = queryResults(s"SELECT DISTINCT SYNONYM_TYPE FROM SYNONYM_TYPE WHERE SYNONYM_MD5_ID = '${synonymId}'").map(_.getString(1))

  def synonymValue(synonymId: String) = queryResults(s"SELECT DISTINCT VALUE FROM SYNONYM_VALUE WHERE SYNONYM_MD5_ID = '${synonymId}'").map(_.getString(1))
  
  def getSynonymTypes() = queryResults("SELECT SYNONYM_TYPE_ID, SYNONYM_TYPE FROM SYNONYM_TYPE_DICT")
}