package org.broadinstitute.translator.parser.pubchem

import java.sql.DriverManager
import java.sql.Connection
import java.sql.Statement
import org.broadinstitute.translator.parser.pubchem.db.SQLite
import scala.collection.mutable.ArrayBuffer

object DB {

  private var db: Option[DB] = None

  def apply(dbFile: String): DB = {
    db = Some(new DB(dbFile))
    return db.get
  }

  def apply(): DB = db.get

}

class DB(dbFile: String) extends SQLite(dbFile) {

  def createDB(): DB = {
    createCompoundTable()
    createSynonymTypeTable()
    createSynonymTable()
    createNeighborTable()
    createPreferredTable()
    commit()
    return this
  }

  //COMPOUND TABLE

  private val compoundColumns = Array[(String, (String, String))](
    "Hydrogen Bond Acceptor Count" -> ("HBA_COUNT", "INT"),
    "Hydrogen Bond Donor Count" -> ("HBD_COUNT", "INT"),
    "Rotatable Bond Count" -> ("ROTATABLE_BOND_COUNT", "INT"),
    "Polar Surface Area Topological" -> ("PSA", "REAL"),
    "MonoIsotopic Weight" -> ("MONOISOTOPIC_WEIGHT", "REAL"),
    " Molecular Weight" -> ("MOLECULAR_WEIGHT", "REAL"),
    " Molecular Formula" -> ("MOLECULAR_FORMULA", "TEXT"),
    "Preferred IUPAC Name" -> ("PREFERRED_IUPAC_NAME", "TEXT"),
    "Standard InChI" -> ("STANDARD_INCHI", "TEXT"),
    "Standard InChIKey" -> ("STANDARD_INCHIKEY", "TEXT"),
    "Isomeric SMILES" -> ("ISOMERIC_SMILES", "TEXT")
  )

  val compoundColumnMap = compoundColumns.toMap.mapValues(_._1)

  def createCompoundTable() {
    val createTableSQL = s"""
      CREATE TABLE COMPOUND (
        CID     INTEGER   PRIMARY KEY NOT NULL,
        TITLE   TEXT COLLATE NOCASE,
        ${compoundColumns.map(_._2).map(c => c._1 + " " + c._2).mkString(",\n")}
      );
    """
    executeUpdate(createTableSQL)
    println("COMPOUND table created")
  }

  def insertCompound(cid: Long, title: Option[String], properties: Map[String, String]) {
    val columns = compoundColumns.filter(properties contains _._2._1).map(_._2)
    val values = columns.map(mapValue(cid, properties))
    val insertSQL = s"""
        INSERT INTO COMPOUND (CID, TITLE, ${columns.map(_._1).mkString(",")})
        VALUES (${cid}, ${f(title)}, ${values.mkString(",")})
      """
    executeUpdate(insertSQL)
  }

  def mapValue(cid: Long, properties: Map[String, String])(column: (String, String)): String = {
    val (columnName, columnType) = column
    properties.get(columnName) match {
      case None => "NULL"
      case Some(value) => columnType match {
        case "TEXT" => f(value)
        case "INT" => intValueString(cid, columnType, value)
        case "REAL" => realValueString(cid, columnType, value)
      }
    }
  }

  private def intValueString(cid: Long, columnType: String, value: String): String = {
    try {
      value.toLong
      value
    }
    catch {
      case e: NumberFormatException => warning(cid, columnType, value); "NULL"
    }
  }

  private def realValueString(cid: Long, columnType: String, value: String): String = {
    try {
      value.toDouble
      value
    }
    catch {
      case e: NumberFormatException => warning(cid, columnType, value); "NULL"
    }
  }

  private def warning(cid: Long, columnType: String, value: String) {
    Console.err.println(s"WARNING: wrong format (${columnType}) '${value}'@cid:${cid}");
  }

  def getCompoundByInchikey(inchikey: String): Seq[(Long, Map[String, String])] = {
    val query = s"""
      SELECT * FROM COMPOUND WHERE STANDARD_INCHIKEY = '${inchikey}'
    """
    return getCompound(query)
  }

  def getCompoundByCid(cid: Long): Seq[(Long, Map[String, String])] = {
    val query = s"""
      SELECT * FROM COMPOUND WHERE CID = ${cid}
    """
    return getCompound(query)
  }

  private def getCompound(query: String): Seq[(Long, Map[String, String])] = {

    val results = new ArrayBuffer[(Long, Map[String, String])]()
    for (result <- queryResults(query)) {
      val cid = result.getLong("CID")
      val map = compoundColumns.map(_._2).map(pair => (pair._1, result.getString(pair._1))).toMap
      results.append((cid, map))
    }
    return results
  }

  def getAllCompounds(index: Int): Array[Long] = {
    val cids = ArrayBuffer[Long]()
    val startCID: Long = 1000000 * index
    val endCID: Long = 1000000 * (index + 1)
    val query = s"""
      SELECT CID FROM COMPOUND
      WHERE $startCID < CID AND CID <= $endCID
    """
    for (result <- queryResults(query)) {
      val cid = result.getLong("CID")
      cids.append(cid)
    }
    return cids.toArray
  }

  // SYNONYM TYPE TABLE

  private def createSynonymTypeTable() {
    val createTableSQL = """
      CREATE TABLE SYNONYM_TYPE (
        SYNONYM_TYPE_ID    INTEGER PRIMARY KEY  NOT NULL,
        SYNONYM_TYPE       TEXT  NOT NULL,
        SYNONYM_TYPE_DESC  TEXT
      );
    """
    executeUpdate(createTableSQL)
    println("SYNONYM_TYPE table created")
  }

  def insertSynonymType(synonymTypeId: Int, synonymType: String, synonymTypeDesc: Option[String]) {
    val insertSQL = s"""
      INSERT INTO SYNONYM_TYPE (SYNONYM_TYPE_ID, SYNONYM_TYPE, SYNONYM_TYPE_DESC)
      VALUES (${synonymTypeId}, ${f(synonymType)}, ${f(synonymTypeDesc)})
      """
    executeUpdate(insertSQL)
  }

  def getSynonymTypes() = queryResults("SELECT SYNONYM_TYPE_ID, SYNONYM_TYPE FROM SYNONYM_TYPE")

  def getSynonymTypeId(synonymType: String): Int = {
    val query = s"SELECT SYNONYM_TYPE_ID FROM SYNONYM_TYPE WHERE SYNONYM_TYPE = '$synonymType'"
    var synonymTypeId = -1
    for (result <- queryResults(query)) {
      synonymTypeId = result.getInt("SYNONYM_TYPE_ID")
    }
    if (synonymTypeId < 0) {
      throw new RuntimeException("Not found $synonymType = '" + synonymType + "'")
    }
    return synonymTypeId
  }

  // SYNONYM TABLE

  private def createSynonymTable() {
    val createTableSQL = """
      CREATE TABLE SYNONYM (
        SYNONYM_ID       INTEGER   PRIMARY KEY NOT NULL,
        CID              INT   NOT NULL,
        SYNONYM_TYPE_ID  INT  NOT NULL,
        SYNONYM          TEXT  NOT NULL  COLLATE NOCASE
      );
    """
    executeUpdate(createTableSQL)
    println("SYNONYM table created")
  }

  def findCID(synonym: String): ArrayBuffer[Long] = {
    val cids = ArrayBuffer[Long]()
    val query = s"""
      SELECT DISTINCT CID
      FROM SYNONYM
      WHERE SYNONYM = ${f(synonym)} COLLATE NOCASE
    """
    for (result <- queryResults(query)) {
      val cid = result.getLong("CID")
      cids.append(cid)
    }
    return cids
  }

  private var synonymId: Long = -1

  def lastSynonymId(): Long = {
    for (result <- queryResults("SELECT MAX(SYNONYM_ID) AS MAX_SYN_ID FROM SYNONYM")) {
      return result.getLong("MAX_SYN_ID")
    }
    return 0
  }

  def insertSynonym(cid: Long, synonymTypeId: Int, synonym: String) {
    if (synonymId < 0) {
      synonymId = lastSynonymId()
    }
    synonymId = synonymId + 1
    val insertSQL = s"""
      INSERT INTO SYNONYM (SYNONYM_ID, CID, SYNONYM_TYPE_ID, SYNONYM)
      VALUES (${synonymId}, ${cid}, ${synonymTypeId}, ${f(synonym)})
      """
    executeUpdate(insertSQL)
  }

  def getSynonyms(cid: Long) = queryResults("SELECT SYNONYM_TYPE_ID, SYNONYM FROM SYNONYM WHERE CID = " + cid)

  // NEIGHBOR TABLE

  def createNeighborTable() {
    val createTableSQL = """
      CREATE TABLE NEIGHBOR (
        CID1  INT  NULL,
        CID2  INT  NULL
      );
    """
    executeUpdate(createTableSQL)
    println("NEIGHBOR table created")
  }

  def insertNeighbor(cid1: Long, cid2: Long) = {
    val insertSQL = s"""
        INSERT INTO NEIGHBOR (CID1, CID2)
        VALUES (${cid1}, ${cid2})
      """
    executeUpdate(insertSQL)
  }

  // PREFERRED TABLE

  def createPreferredTable() {
    val createTableSQL = """
      CREATE TABLE PREFERRED (
        RETIRED_CID  INTEGER   PRIMARY KEY NOT NULL,
        PREFERRED_CID  INT
      );
    """
    executeUpdate(createTableSQL)
    println("PREFERRED table created")
  }

  def insertPreferredCid(retiredCid: Long, preferredCid: Option[Long]) {
    val insertSQL = s"""
        INSERT INTO PREFERRED (RETIRED_CID, PREFERRED_CID)
        VALUES (${retiredCid}, ${fl(preferredCid)})
      """
    executeUpdate(insertSQL)
  }

  def hasPreferredCid(retiredCid: Long): Boolean = {
    val query = s"""
      SELECT PREFERRED_CID FROM PREFERRED
      WHERE  RETIRED_CID = $retiredCid
    """
    var hasPreferredCid = false
    for (result <- queryResults(query)) {
      hasPreferredCid = true
    }
    return hasPreferredCid
  }

  // DESCRIPTION TABLE

  private def createDescriptionTable() {
    val createTableSQL = """
      CREATE TABLE DESCRIPTION (
        DESCRIPTION_ID      INTEGER   PRIMARY KEY NOT NULL,
        CID                 INT   NOT NULL,
        DESCRIPTION         TEXT  NOT NULL,
        DESCRIPTION_SOURCE  TEXT,
        DESCRIPTION_URL     TEXT
      );
    """
    executeUpdate(createTableSQL)
    println("DESCRIPTION table created")
  }

  def insertDescription(cid: Long, description: String, descriptionSourceName: Option[String], descriptionURL: Option[String]) {
    val insertSQL = s"""
      INSERT INTO DESCRIPTION (CID, DESCRIPTION, DESCRIPTION_SOURCE, DESCRIPTION_URL)
      VALUES (${cid}, ${f(description)}, ${f(descriptionSourceName)}, ${f(descriptionURL)})
      """
    executeUpdate(insertSQL)
  }

  // INDEXES

  def buildIndexes() = {
    try {
      createIndex("COMPOUND", "TITLE", nocase = true)
      commit()
      println("Created index COMPOUND[TITLE]")

      createIndex("COMPOUND", "STANDARD_INCHI")
      commit()
      println("Created index COMPOUND[STANDARD_INCHI]")

      createIndex("SYNONYM", "CID")
      commit()
      println("Created index SYNONYM[CID]")

      createIndex("SYNONYM", "SYNONYM", nocase = true)
      commit()
      println("Created index SYNONYM[SYNONYM]")

      createIndex("NEIGHBOR", "CID1")
      commit()
      println("Created index NEIGHBOR[CID1]")

      createIndex("PREFERRED", "PREFERRED_CID")
      commit()
      println("Created index PREFERRED[PREFERRED_CID]")
    }
    finally {
      close()
    }
  }

}
