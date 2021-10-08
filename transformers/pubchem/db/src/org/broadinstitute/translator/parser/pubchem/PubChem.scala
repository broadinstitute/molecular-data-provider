package org.broadinstitute.translator.parser.pubchem

import scala.io.Source
import org.broadinstitute.translator.xml.Builder
import org.broadinstitute.translator.xml.Parser
import java.io.File
import java.io.FileReader

import scala.util.parsing.combinator.RegexParsers
import org.broadinstitute.translator.parser.pubchem.rdf.TTLparser
import org.broadinstitute.translator.parser.pubchem.synonym.SynonymDB
import org.broadinstitute.translator.parser.pubchem.synonym.PubChemSynonyms
import scala.collection.mutable.ArrayBuffer
import org.broadinstitute.translator.parser.pubchem.title.TitleDB

object PubChem {

  def createDB(dbFile: String) {
    DB(dbFile).createDB()
    val db = DB(dbFile)
    uploadSynonymTypes(db)
    db.createIndex("COMPOUND", "STANDARD_INCHIKEY")
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

  def loadCompoundsByInchikey(dbFile: String, src: String) {
    val synDB = DB("data/PubChem.syn.sqlite")
    val titleDB = new TitleDB("data/PubChem.title.sqlite")
    val db = DB(dbFile)
    val source = Source.fromFile(src)(io.Codec("UTF-8"))
    val inchikeys = new ArrayBuffer[String]()
    for (line <- source.getLines().drop(1)) {
      if (db.getCompoundByInchikey(line).isEmpty) {
        inchikeys += line
      }
    }
    println(inchikeys.size + " compounds to load")
    val structuresDir = "data/structures"
    for (file <- new File(structuresDir).list; if file.startsWith("PubChem_") && file.endsWith(".sqlite")) {
      loadCompounds(db, inchikeys, structuresDir + "/" + file, synDB, titleDB)
    }
    db.commit()
    db.close()

  }

  def loadCompounds(db: DB, compounds: ArrayBuffer[String], srcDBname: String, synDB: DB, titleDB: TitleDB) {
    println(srcDBname)
    val srcDB = new DB(srcDBname)
    for (inchikey <- compounds) {
      for ((cid, properties) <- srcDB.getCompoundByInchikey(inchikey)) {
        insertCompound(db: DB, cid, properties, synDB, titleDB)
      }
    }
    srcDB.close()
    db.commit()
  }

  def insertCompound(db: DB, cid: Long, properties: Map[String, String], synDB: DB, titleDB: TitleDB) {
    val title = titleDB.getTitle(cid)
    db.insertCompound(cid, title, properties)
    for (result <- synDB.getSynonyms(cid)) {
      val synonymTypeId = result.getInt("SYNONYM_TYPE_ID")
      val synonym = result.getString("SYNONYM")
      db.insertSynonym(cid, synonymTypeId, synonym)
    }
  }

  def insertCompound(db: DB, cid: Long, synDB: DB, titleDB: TitleDB) {
    if (db.getCompoundByCid(cid).isEmpty) {
      val srcDB = getStructureDB(cid)
      for ((cid, properties) <- srcDB.getCompoundByCid(cid)) {
        insertCompound(db: DB, cid, properties, synDB, titleDB)
      }
      srcDB.close()
    }
  }

  def loadCompoundsByCid(dbFile: String, src: String) {
    val synDB = new DB("data/PubChem.syn.sqlite")
    val titleDB = new TitleDB("data/PubChem.title.sqlite")
    val db = DB(dbFile)
    val source = Source.fromFile(src)(io.Codec("UTF-8"))
    var count = 0
    for (line <- source.getLines().drop(1)) {
      val cid = line.toLong
      insertCompound(db: DB, cid, synDB, titleDB)
      count += 1
      if (count % 1000 == 0) {
        println(count)
        db.commit()
      }
    }
    db.commit()
    db.close()
    synDB.close()
  }

  def loadCompoundsByName(dbFile: String, src: String) {
    val synDB = new DB("data/PubChem.syn.sqlite")
    val titleDB = new TitleDB("data/PubChem.title.sqlite")
    val db = DB(dbFile)
    val source = Source.fromFile(src)(io.Codec.ISO8859)
    var count = 0
    for (line <- source.getLines().drop(1)) {
      val name = line.stripPrefix("\"").stripSuffix("\"")
      for (cid <- titleDB.findCID(name)) {
        insertCompound(db: DB, cid, synDB, titleDB)
      }
      for (cid <- synDB.findCID(name)) {
        insertCompound(db: DB, cid, synDB, titleDB)
      }
      count += 1
      if (count % 1000 == 0) {
        println(count)
        db.commit()
      }
    }
    db.commit()
    db.close()
    titleDB.close()
    synDB.close()
  }

  private def getStructureDB(cid: Long): DB = {
    val index = (cid - 1) / 1000000
    val dbName = "data/structures/PubChem_" + f"${index}%03d" + ".sqlite"
    return new DB(dbName)
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
    val synDB = DB("data/PubChem.syn.sqlite")
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
    val db = DB(dbFile)
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
    var map = Map[String, Int]()
    for (result <- SynonymDB.getSynonymTypes()) {
      val synonymTypeId = result.getInt("SYNONYM_TYPE_ID")
      val synonymType = result.getString("SYNONYM_TYPE")
      map += synonymType -> synonymTypeId
      db.insertSynonymType(synonymTypeId, synonymType, descriptions.get(synonymType))
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

  def main(args: Array[String]): Unit = args(0) match {
    case "create-db" => createDB(args(1))
    case "load-compounds-inchikey" => loadCompoundsByInchikey(args(1), args(2))
    case "load-compounds-cid" => loadCompoundsByCid(args(1), args(2))
    case "load-compounds-name" => loadCompoundsByName(args(1), args(2))
    case "get-cid-from-name" => getCidsFromName(args(1))
    case "syn-get-cid-from-name" => synGetCidsFromName(args(1))
    case "load-structures" => loadStructures(args(1), args(2))
    case "load-compounds" => loadStructures(args(1), args(2))
    case "syn-create-db" => SynonymDB.createDB()
    case "syn-load-ids" => PubChemSynonyms.loadIds(args(1))
    case "syn-load-types" => PubChemSynonyms.loadTypes(args(1))
    case "syn-load-values" => PubChemSynonyms.loadValues(args(1))
    case "syn-build-indexes" => SynonymDB.buildIndexes()
    case "load-synonyms" => loadSynonyms(args(1))
    case "build-indexes" => DB(args(1)).buildIndexes()
    case "load-titles" => TitleDB.loadTitles(args(1), args(2))
  }

}
