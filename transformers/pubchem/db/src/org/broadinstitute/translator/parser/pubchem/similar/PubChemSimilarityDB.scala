package org.broadinstitute.translator.parser.pubchem.similar

import org.broadinstitute.translator.parser.pubchem.db.SQLite
import org.broadinstitute.translator.parser.pubchem.rdf.TTLparser
import java.sql.ResultSet

object PubChemSimilarityDB {
  def createDB(dbName: String) = {
    val db = new PubChemSimilarityDB(dbName)
    db.createNeighborTable()
    db.commit()
    db.close()
  }

  def loadNeighbors(dbName: String, filename: String) = {
    val db = new PubChemSimilarityDB(dbName)
    val parser = TTLparser(filename, sep = " ")
    var count = 0
    try {
      parser.parse { triples =>
        for (triple <- triples) {
          if (triple.sub.startsWith("compound:CID") && triple.predicate == "sio:CHEMINF_000482" && triple.obj.startsWith("compound:CID")) {
            val cid1 = triple.sub.substring(12).toInt
            val cid2 = triple.obj.substring(12).toInt
            db.insertNeighbor(cid1, cid2)
            count += 1
            if (count % 100000 == 0) {
              db.commit()
              if (count % 100000 == 0) {
                db.reconnect()
              }
              if (count % 1000000 == 0) {
                println(count)
              }
            }
          }
        }
      }
      db.commit()
    }
    finally {
      db.close()
    }
    println("Loaded " + count + " neighbors")
  }

  def buildIndex(filename: String) = {
    val db = new PubChemSimilarityDB(filename)
    db.buildIndex()
  }
}

class PubChemSimilarityDB(filename: String) extends SQLite(filename) {

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

  def getNeighbors(cid: Long): Iterable[ResultSet] = {
    val query = s"""
      SELECT CID2 FROM NEIGHBOR
      WHERE  CID1 = $cid
    """
    return queryResults(query)

  }

  def buildIndex() = {
    createIndex("NEIGHBOR", "CID1")
    commit()
  }
}
