package org.broadinstitute.translator.parser.pubchem.title

import org.broadinstitute.translator.parser.pubchem.db.SQLite
import scala.io.Source

object TitleDB {
  def loadTitles(dbName: String, filename: String) {
    val db = new TitleDB(dbName)
    db.createTitleTable()
    val titles = Source.fromFile(filename)(io.Codec.ISO8859)
    for (line <- titles.getLines) {
      val row = line.split("\t")
      val cid = row(0).toLong
      val title = row(1)
      db.insertTitle(cid, title)
      if (cid % 10000 == 0) {
        db.commit()
        if (cid % 1000000 == 0) {
          println(cid)
        }
      }
    }
    db.commit()
    db.createIndex("TITLE", "TITLE")
    db.close()
  }
}

class TitleDB(filename: String) extends SQLite(filename) {

  def createTitleTable() {
    val createTableSQL = s"""
      CREATE TABLE TITLE (
        CID    INTEGER   PRIMARY KEY NOT NULL,
        TITLE  TEXT COLLATE NOCASE
      );
    """
    executeUpdate(createTableSQL)
    println("TITLE table created")
  }

  def insertTitle(cid: Long, title: String) = {
    val insertSQL = s"""
        INSERT INTO TITLE (CID, TITLE)
        VALUES (${cid}, ${f(title)})
      """
    executeUpdate(insertSQL)
  }

  def getTitle(cid: Long): Option[String] = {
    val query = "SELECT TITLE FROM TITLE WHERE CID = " + cid
    var title: Option[String] = None
    for (result <- queryResults(query)) {
      title = Some(result.getString("TITLE"))
    }
    return title
  }

  def findCID(title: String): Seq[Long] = {
    val query = s"SELECT CID FROM TITLE WHERE TITLE = ${f(title)} COLLATE NOCASE"
    return queryResults(query).map(_.getLong("CID")).toSeq
  }
}
