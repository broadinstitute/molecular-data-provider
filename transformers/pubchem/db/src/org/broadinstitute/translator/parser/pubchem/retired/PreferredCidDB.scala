package org.broadinstitute.translator.parser.pubchem.retired

import org.broadinstitute.translator.parser.pubchem.db.SQLite
import scala.io.Source
import java.sql.ResultSet

object PreferredCidDB {

  def createDB(dbName: String): PreferredCidDB = {
    val db = new PreferredCidDB(dbName)
    db.createPreferredTable()
    db.commit()
    return db
  }

  def loadPreferredCIDs(dbName: String, filename: String) {
    val db = createDB(dbName)
    var i = 0
    val titles = Source.fromFile(filename)
    for (line <- titles.getLines) {
      val row = line.split("\t")
      val oldCid = row(0).toLong
      val preferredCid = row(1).toLong
      db.insertPreferredCid(oldCid, preferredCid)
      i = i + 1
      if (i % 10000 == 0) {
        db.commit()
        if (i % 100000 == 0) {
          println(i)
        }
      }
    }
    db.commit()
    db.createIndex("PREFERRED", "PREFERRED_CID")
    db.commit()
    db.close()

  }
}

class PreferredCidDB(filename: String) extends SQLite(filename) {

  def createPreferredTable() {
    val createTableSQL = """
      CREATE TABLE PREFERRED (
        RETIRED_CID  INTEGER   PRIMARY KEY NOT NULL,
        PREFERRED_CID  INT  NULL
      );
    """
    executeUpdate(createTableSQL)
    println("PREFERRED table created")
  }

  def insertPreferredCid(retiredCid: Long, preferredCid: Long) {
    val insertSQL = s"""
        INSERT INTO PREFERRED (RETIRED_CID, PREFERRED_CID)
        VALUES (${retiredCid}, ${preferredCid})
      """
    executeUpdate(insertSQL)
  }

  def retiredCids(preferredCID: Long): Iterable[ResultSet] = {
    val query = s"""
      SELECT RETIRED_CID FROM PREFERRED
      WHERE  PREFERRED_CID = $preferredCID
    """
    return queryResults(query)
  }

  def getPreferredCid(retiredCid: Long): Option[Long] = {
    val query = s"""
      SELECT PREFERRED_CID FROM PREFERRED
      WHERE  RETIRED_CID = $retiredCid
    """
    var preferredCid: Option[Long] = None
    for (result <- queryResults(query)) {
      preferredCid = Some(result.getLong("PREFERRED_CID"))
    }
    return preferredCid
  }

}
