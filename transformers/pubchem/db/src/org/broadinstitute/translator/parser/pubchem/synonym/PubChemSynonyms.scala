package org.broadinstitute.translator.parser.pubchem.synonym

import org.broadinstitute.translator.parser.pubchem.rdf.TTLparser

object PubChemSynonyms {

  def loadIds(filename: String) {

    val parser = TTLparser(filename)
    var count = 0
    try {
      parser.parse { triples =>
        for (triple <- triples) {
          if (triple.predicate == "sio:is-attribute-of") {
            if (triple.obj.startsWith("compound:CID")) {
              val cid = triple.obj.substring(12).toInt
              SynonymDB.insertId(triple.sub, cid)
            }
            else {
              println("WARNING: unexpected compound " + triple.obj)
            }
            count += 1
          }
          else {
            println("WARNING: unexpected predicate " + triple.predicate)
          }
        }
      }
      SynonymDB.commit()
    }
    finally {
      SynonymDB.close()
    }
    println("Loaded " + count + " synonym ids")
  }

  def loadTypes(filename: String) {

    val parser = TTLparser(filename)
    var count = 0
    try {
      parser.parse { triples =>
        for (triple <- triples) {
          if (triple.predicate == "rdf:type") {
            SynonymDB.insertType(triple.sub, triple.obj)
            count += 1
          }
          else {
            println("WARNING: unexpected predicate " + triple.predicate)
          }
        }
      }
      SynonymDB.commit()
    }
    finally {
      SynonymDB.close()
    }
    println("Loaded " + count + " synonym types")
  }

  def loadValues(filename: String) {

    val parser = TTLparser(filename)
    var count = 0
    try {
      parser.parse { triples =>
        for (triple <- triples) {
          if (triple.predicate == "sio:has-value") {
            val valLang = triple.obj.split("@")
            if (valLang.length == 2) {
              var value = valLang(0)
              val lang = valLang(1)
              if (value.startsWith("\""))
                value = value.substring(1)
              if (value.endsWith("\""))
                value = value.substring(0, value.length() - 1)
              SynonymDB.insertValue(triple.sub, value, lang)
            }
            count += 1
          }
          else {
            println("WARNING: unexpected predicate " + triple.predicate)
          }
        }
      }
      SynonymDB.commit()
    }
    finally {
      SynonymDB.close()
    }
    println("Loaded " + count + " synonym values")
  }
}