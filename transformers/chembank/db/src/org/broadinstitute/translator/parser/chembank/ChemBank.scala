package org.broadinstitute.translator.parser.chembank

import scala.io.Source
import java.io.IOException

object ChemBank {

  def main(args: Array[String]) {
    DB.createDB("ChemBank.sqlite")
    val root = args(0)
    loadTypes(root + "/NAME_TYPE.txt")
    loadCompounds(root + "/COMPOUND.txt")
    loadNames(root + "/COMPOUND_NAME.txt")
    DB.createIndexes()
    DB.commit()
    DB.close()
  }

  def loadTypes(filename: String) {
    val src = Source.fromFile(filename).getLines
    val headerLine = src.take(1).next
    if (headerLine != "CPD_NAME_TYPE_ID\tCPD_NAME_TYPE\tCPD_NAME_TYPE_PRIORITY") {
      throw new IOException("Wrong file format: " + filename)
    }
    for (line <- src) {
      val row = line.split("\t")
      DB.insertType(row(0).toInt, row(1), row(2).toInt)
    }
    println("name types loaded")
    DB.commit()
  }

  def loadCompounds(filename: String) {
    val src = Source.fromFile(filename).getLines
    val headerLine = src.take(1).next
    if (headerLine != "ChemBankId\tCHEMBANK_ID\tCBP_SMILES\tInChI\tInChIKey") {
      throw new IOException("Wrong file format: " + filename)
    }
    for (line <- src) {
      val row = line.split("\t")
      DB.insertCompound(row(1).toInt, row(2), row(3), row(4))
    }
    println("compounds loaded")
    DB.commit()
  }

  def loadNames(filename: String) {
    val src = Source.fromFile(filename).getLines
    val headerLine = src.take(1).next
    if (headerLine != "﻿CHEMBANK_ID\tCPD_NAME\tCPD_NAME_TYPE_ID") {
      throw new IOException("Wrong file format: " + filename)
    }
    for (line <- src) {
      val row = line.split("\t")
      DB.insertName(row(0).toInt, row(1), row(2).toInt)
    }
    println("compound names loaded")
    DB.commit()
  }
}
