package org.broadinstitute.translator.parser.pubchem

import java.io.File

import scala.collection.mutable.ArrayBuffer
import scala.io.Source

import org.broadinstitute.translator.parser.pubchem.similar.PubChemSimilarityDB
import org.broadinstitute.translator.parser.pubchem.title.TitleDB
import org.broadinstitute.translator.parser.pubchem.retired.PreferredCidDB

object PubChemLoader {

  val SYN_DB = "data/db/PubChem.syn.sqlite"
  val TITLE_DB = "data/db/PubChem.title.sqlite"
  val PREF_DB = "data/db/PubChemPreferredCID.sqlite"
  val STRUCTURE_DIR = "data/structures"
  val SIMILARITY_DIR = "data/db/similarity"

  val synDB = DB(SYN_DB)
  val titleDB = new TitleDB(TITLE_DB)
  val prefDB = new PreferredCidDB(PREF_DB)

  def loadCompoundsByInchikey(dbFile: String, src: String) {
    val db = DB(dbFile)
    val source = Source.fromFile(src)(io.Codec("UTF-8"))
    val inchikeys = new ArrayBuffer[String]()
    for (line <- source.getLines().drop(1)) {
      if (db.getCompoundByInchikey(line).isEmpty) {
        inchikeys += line
      }
    }
    println(inchikeys.size + " compounds to load")
    for (file <- new File(STRUCTURE_DIR).list.sorted; if file.startsWith("PubChem_") && file.endsWith(".sqlite")) {
      loadCompoundsByInchikey(db, inchikeys, STRUCTURE_DIR + "/" + file)
    }
    db.commit()
    db.close()
    titleDB.close()
    synDB.close()
    prefDB.close()
  }

  def loadCompoundsByInchikey(db: DB, compounds: ArrayBuffer[String], srcDBname: String) {
    println(srcDBname)
    val srcDB = new DB(srcDBname)
    for (inchikey <- compounds) {
      for ((cid, properties) <- srcDB.getCompoundByInchikey(inchikey)) {
        insertCompound(db: DB, cid, properties)
      }
    }
    srcDB.close()
    db.commit()
    db.reconnect()
  }

  def loadCompoundsByCid(dbFile: String, src: String) {
    val db = DB(dbFile)
    val source = Source.fromFile(src)(io.Codec("UTF-8"))
    var count = 0
    for (line <- source.getLines().drop(1)) {
      val cid = line.toLong
      loadCompound(db: DB, cid)
      count += 1
      if (count % 1000 == 0) {
        println(count)
        db.commit()
        if (count % 10000 == 0) {
          db.reconnect()
        }
      }
    }
    db.commit()
    db.close()
    titleDB.close()
    synDB.close()
    prefDB.close()
  }

  def loadCompoundsByName(dbFile: String, src: String) {
    val db = DB(dbFile)
    val source = Source.fromFile(src)(io.Codec.ISO8859)
    var count = 0
    for (line <- source.getLines().drop(1)) {
      val name = line.stripPrefix("\"").stripSuffix("\"")
      for (cid <- titleDB.findCID(name)) {
        loadCompound(db: DB, cid)
      }
      for (cid <- synDB.findCID(name)) {
        loadCompound(db: DB, cid)
      }
      count += 1
      if (count % 1000 == 0) {
        println(count)
        db.commit()
        if (count % 10000 == 0) {
          db.reconnect()
        }
      }
    }
    db.commit()
    db.close()
    titleDB.close()
    synDB.close()
    prefDB.close()
  }

  def loadCompound(db: DB, srcCid: Long) {
    if (db.getCompoundByCid(srcCid).isEmpty && !db.hasPreferredCid(srcCid)) {
      getStructureDB(srcCid) match {
        case Some(srcDB) => {
          for ((cid, properties) <- getCompound(db, srcDB, srcCid)) {
            if (db.getCompoundByCid(cid).isEmpty) {
              insertCompound(db: DB, cid, properties)
            }
            else {
              println("INFO: preferred CID=" + cid + " allready stored")
            }
          }
          srcDB.close()
        }
        case None => println("WARN: cid=" + srcCid + " is outside of the range")
      }
    }
  }

  def getCompound(db: DB, srcDB: DB, cid: Long): Seq[(Long, Map[String, String])] = {
    val compound = srcDB.getCompoundByCid(cid)
    if (compound.isEmpty) {
      prefDB.getPreferredCid(cid) match {
        case Some(prefCid) => {
          db.insertPreferredCid(cid, Some(prefCid))
          val retiredPubChemTypeId = db.getSynonymTypeId("pubchem-retired")
          db.insertSynonym(prefCid, retiredPubChemTypeId, cid.toString)
          return srcDB.getCompoundByCid(prefCid)
        }
        case None => {
          db.insertPreferredCid(cid, None)
          return new ArrayBuffer[(Long, Map[String, String])]()
        }
      }
    }
    else {
      return compound
    }
  }

  private def getStructureDB(cid: Long): Option[DB] = {
    val index = (cid - 1) / 1000000
    val dbName = STRUCTURE_DIR + "/PubChem_" + f"${index}%03d" + ".sqlite"
    new File(dbName).exists() match {
      case false => None
      case true => Some(new DB(dbName))
    }
  }

  // LOAD NEIGHBORS

  def loadNeighbors(dbFile: String) {
    addNeighbors(dbFile, load = true)
  }

  def addNeighbors(dbFile: String, load: Boolean = false) {
    val db = DB(dbFile)
    val cids: Seq[Array[Long]] = (0 to 163).map(db.getAllCompounds(_))
    db.reconnect()
    for (i <- 0 to 163) {
      println(i+": "+cids(i).length)
      val simDB = new PubChemSimilarityDB(SIMILARITY_DIR + f"/PubChemSimilarity_$i%03d.sqlite")
      val synDB = new DB(SYN_DB)
      var n: Int = 0
      for (cid1 <- cids(i)) {
        for (neighbor <- simDB.getNeighbors(cid1)) {
          val cid2 = neighbor.getLong("CID2")
          if (load) {
            db.insertNeighbor(cid1, cid2)
            loadCompound(db, cid2)
          }
          else if (!db.getCompoundByCid(cid2).isEmpty) {
            db.insertNeighbor(cid1, cid2)
          }
        }
        n = n + 1
        if (n % 10 == 0) {
          db.commit()
          print(".")
          if (n % 100 == 0) {
            db.reconnect()
            simDB.reconnect()
          }
        }
      }
      println("loaded neighbors for " + n + " cids @ " + i)
      db.commit()
      db.reconnect()
      simDB.close()
      synDB.close()
    }
    db.close()
    titleDB.close()
  }

  // INSERT COPOUND

  def insertCompound(db: DB, cid: Long, properties: Map[String, String]) {
    val title = titleDB.getTitle(cid)
    db.insertCompound(cid, title, properties)
    for (result <- synDB.getSynonyms(cid)) {
      val synonymTypeId = result.getInt("SYNONYM_TYPE_ID")
      val synonym = result.getString("SYNONYM")
      db.insertSynonym(cid, synonymTypeId, synonym)
    }
  }

}