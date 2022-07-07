package org.broadinstitute.translator.parser.pubchem

import scala.collection.mutable.ArrayBuffer
import scala.io.Source

import org.broadinstitute.translator.parser.pubchem.retired.PreferredCidDB
import org.broadinstitute.translator.parser.pubchem.similar.PubChemSimilarityDB
import org.broadinstitute.translator.parser.pubchem.synonym.PubChemSynonyms
import org.broadinstitute.translator.parser.pubchem.synonym.SynonymDB
import org.broadinstitute.translator.parser.pubchem.title.TitleDB
import org.broadinstitute.translator.xml.Builder
import org.broadinstitute.translator.xml.Parser

object PubChem {

  val SYN_DB = "data/db/PubChem.syn.sqlite"

  def createDB(dbFile: String) {
    val db = DB(dbFile).createDB()
    uploadSynonymTypes(db)
    db.createIndex("COMPOUND", "STANDARD_INCHIKEY")
    db.createIndex("SYNONYM_TYPE", "SYNONYM_TYPE")
    DB().commit()
    DB().close()
  }

  def loadStructures(dbFile: String, src: String) {
    DB(dbFile)
    val source = Source.fromFile(src)(io.Codec("UTF-8"))
    Parser.parse(source, new RootBuilder)
    DB().commit()
    DB().close()
    println("Structures loaded")
  }

  class RootBuilder extends Builder {
    val tag = ""
    override def getBuilder(tag: String, attr: Map[String, String]): Option[Builder] = tag match {
      case "PC-Compound" => Some(new CompoundBuilder())
      case _ => None
    }
  }

  def getCidsFromName(src: String) {
    val source = Source.fromFile(src)(io.Codec("UTF-8"))
    val inchikeys = new ArrayBuffer[String]()
    println("CID\tname")
    for (line <- source.getLines().drop(1)) {
      val name = line.stripPrefix("\"").stripSuffix("\"")
      for (cid <- PubChemPUG.findCID(name)) {
        println(cid + "\t" + name)
      }
    }
  }

  def synGetCidsFromName(src: String) {
    val synDB = DB(SYN_DB)
    val source = Source.fromFile(src)(io.Codec("UTF-8"))
    val inchikeys = new ArrayBuffer[String]()
    println("CID\tname")
    for (line <- source.getLines().drop(1)) {
      val name = line.stripPrefix("\"").stripSuffix("\"")
      for (cid <- synDB.findCID(name)) {
        println(cid + "\t" + name)
      }
    }
  }

  // LOAD SYNONYMS

  def loadSynonymTypes(db: DB): Map[String, Int] = {
    var map = Map[String, Int]()
    for (result <- db.getSynonymTypes()) {
      val synonymTypeId = result.getInt("SYNONYM_TYPE_ID")
      val synonymType = result.getString("SYNONYM_TYPE")
      map += synonymType -> synonymTypeId
    }
    return map
  }

  def loadSynonyms(dbFile: String) {
    val db = DB(dbFile).createDB()
    try {
      val types = uploadSynonymTypes(db)
      var n = 0
      val allSynonyms = SynonymDB.allSynonyms()
      println("got synonyms")
      while (allSynonyms.next()) {
        val synonymId = allSynonyms.getString(1)
        val cid = allSynonyms.getLong(2)
        loadSynonyms(synonymId, cid, types)
        n = n + 1
        if (n % 100000 == 0) {
          db.commit()
          println(n + "\tmax: " + Runtime.getRuntime.maxMemory() + ", free:" + Runtime.getRuntime.freeMemory() + ", total: " + Runtime.getRuntime.totalMemory())
        }
      }
      db.commit()
      println("" + n + " synonyms loaded")
    }
    finally {
      db.close()
    }
  }

  def uploadSynonymTypes(db: DB): Map[String, Int] = {
    val descriptions = loadSynonymTypeDescriptions("data/synonym_types.txt")
    var maxSynonymTypeId = -1
    var map = Map[String, Int]()
    for (result <- SynonymDB.getSynonymTypes()) {
      val synonymTypeId = result.getInt("SYNONYM_TYPE_ID")
      val synonymType = result.getString("SYNONYM_TYPE")
      map += synonymType -> synonymTypeId
      println(synonymTypeId, synonymType, descriptions.get(synonymType))
      db.insertSynonymType(synonymTypeId, synonymType, descriptions.get(synonymType))
      maxSynonymTypeId = scala.math.max(maxSynonymTypeId, synonymTypeId)
    }
    for ((synonymType, description) <- descriptions) {
      if (!(map contains synonymType)) {
        maxSynonymTypeId = maxSynonymTypeId + 1
        val synonymTypeId = maxSynonymTypeId
        map += synonymType -> synonymTypeId
        println(synonymTypeId, synonymType, description)
        db.insertSynonymType(synonymTypeId, synonymType, Some(description))
      }
    }
    return map
  }

  def loadSynonymTypeDescriptions(filename: String): Map[String, String] = {
    var map = Map[String, String]()
    val source = Source.fromFile(filename)
    for (line <- source.getLines().drop(1)) {
      val row = line.split("\t")
      if (row.length >= 3) {
        map += row(1) -> row(2)
      }
    }
    return map
  }

  def loadSynonyms(synonymId: String, cid: Long, types: Map[String, Int]) {
    for (synonymType <- SynonymDB.synonymType(synonymId)) {
      for (synonymValue <- SynonymDB.synonymValue(synonymId)) {
        DB().insertSynonym(cid, types(synonymType), synonymValue)
      }
    }
  }

  // GET RETIRED CIDs

  def getPreferredCIDs(dbFile: String, preferredDBFile: String) {
    val db = DB(dbFile)
    println(loadSynonymTypes(db))
    val retiredPubChemTypeId = loadSynonymTypes(db)("pubchem-retired")
    val preferredDB = new PreferredCidDB(preferredDBFile)
    for (i <- 0 to 163) {
      val cids = db.getAllCompounds(i)
      println(i + ":\t" + cids.length)
      for (preferredCID <- cids) {
        for (retiredCIDresults <- preferredDB.retiredCids(preferredCID)) {
          val retiredCID = retiredCIDresults.getLong("RETIRED_CID")
          if (!db.hasPreferredCid(retiredCID)) {
            db.insertPreferredCid(retiredCID, Some(preferredCID))
            db.insertSynonym(preferredCID, retiredPubChemTypeId, retiredCID.toString)
          }
        }
      }
      db.commit()
      db.reconnect()
    }
  }

  def main(args: Array[String]): Unit = {
    System.setProperty("java.io.tmpdir", "tmp");
    args(0) match {
      case "create-db" => createDB(args(1))
      case "load-compounds-inchikey" => PubChemLoader.loadCompoundsByInchikey(args(1), args(2))
      case "load-compounds-cid" => PubChemLoader.loadCompoundsByCid(args(1), args(2))
      case "load-compounds-name" => PubChemLoader.loadCompoundsByName(args(1), args(2))
      case "get-cid-from-name" => getCidsFromName(args(1))
      case "syn-get-cid-from-name" => synGetCidsFromName(args(1))
      case "load-structures" => loadStructures(args(1), args(2))
      case "syn-create-db" => SynonymDB.createDB()
      case "syn-load-ids" => PubChemSynonyms.loadIds(args(1))
      case "syn-load-types" => PubChemSynonyms.loadTypes(args(1))
      case "syn-load-values" => PubChemSynonyms.loadValues(args(1))
      case "syn-build-indexes" => SynonymDB.buildIndexes()
      case "load-synonyms" => loadSynonyms(args(1))
      case "build-indexes" => DB(args(1)).buildIndexes()
      case "load-titles" => TitleDB.loadTitles(args(1), args(2))
      case "sim-create-db" => PubChemSimilarityDB.createDB(args(1))
      case "sim-load-neighbors" => PubChemSimilarityDB.loadNeighbors(args(1), args(2))
      case "sim-build-indexes" => PubChemSimilarityDB.buildIndex(args(1))
      case "load-neighbors" => PubChemLoader.loadNeighbors(args(1))
      case "add-neighbors" => PubChemLoader.addNeighbors(args(1))
      case "load-preferred-cids" => PreferredCidDB.loadPreferredCIDs(args(1), args(2))
      case "get-preferred-cids" => getPreferredCIDs(args(1), args(2))
    }
    println("\nDone")
  }
}
