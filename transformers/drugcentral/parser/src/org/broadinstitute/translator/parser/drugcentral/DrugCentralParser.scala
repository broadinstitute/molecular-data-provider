package org.broadinstitute.translator.parser.drugcentral

import scala.io.Source
import java.io.IOException

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.annotation.JsonInclude.Include
import com.fasterxml.jackson.module.scala.DefaultScalaModule
import scala.beans.BeanProperty

object DrugCentralParser {

  val mapper = new ObjectMapper()
  mapper.setSerializationInclusion(Include.NON_NULL);
  mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
  mapper.registerModule(DefaultScalaModule)

  def main(args: Array[String]) {
    DB.createDB("DrugCentral.sqlite")
    val root = args(0)
    parseStructures(root + "/structures.smiles.tsv")
    parseIndications(root + "/drug_indications_10122018.tsv")
    DB.createIndexes()
    DB.close()
  }

  def parseStructures(filename: String) = {
    val src = Source.fromFile(filename).getLines
    val headerLine = src.take(1).next
    if (headerLine != "SMILES\tInChI\tInChIKey\tID\tINN\tCAS_RN") {
      throw new IOException("Wrong file format: " + filename)
    }
    for (line <- src) {
      val row = line.split("\t")
      println(row(3).toInt + " => " + row(4))
      DB.insertDrug(row(3).toInt, row(4), row(5), row(0), row(1), row(2))
    }
    DB.commit()
  }

  def findDisease(umlsCode: String): Option[String] = {
    try {
      val curie = "UMLS:" + umlsCode
      val url = "https://nodenormalization-sri.renci.org/get?key=" + curie
      val json = Source.fromURL(url).mkString
      if (json != null) {
        val response = mapper.readValue(json, classOf[Map[String, Map[String, Any]]])
        val identifier = response.get(curie).get("id")
        if (identifier.isInstanceOf[Map[_, _]]) {
          return identifier.asInstanceOf[Map[String, String]].get("identifier")
        }
        println(response)
      }
    } catch {
      case e: Exception => 
    }
    return None
  }

  def parseIndications(filename: String) {
    val src = Source.fromFile(filename).getLines
    val headerLine = src.take(1).next
    if (headerLine != "DRUG_ID\tDRUG_NAME\tINDICATION_FDB\tUMLS_CUI\tSNOMEDCT_CUI\tDOID") {
      throw new IOException("Wrong file format: " + filename)
    }
    var diseases = Map[String, Int]()
    for (line <- src; row = line.split("\t")) {
      val drugCentralId = row(0).toInt
      val diseaseName = row(2)
      val umlsCode = if (row.length > 3) Some(row(3)) else None
      val mondoId = umlsCode.flatMap(findDisease)
      val snomedCtId = if (row.length > 4) Some(row(4)) else None
      val doid = if (row.length > 5) Some(row(5)) else None
      println(drugCentralId + "\t" + diseaseName + "\t" + umlsCode + "\t" + mondoId + "\t" + snomedCtId + "\t" + doid)
      val diseaseId = diseases.get(diseaseName) match {
        case None => {
          val diseaseId = DB.insertDisease(diseaseName, mondoId, umlsCode, snomedCtId, doid)
          diseases += diseaseName -> diseaseId
          diseaseId
        }
        case Some(id) => id
      }
      DB.insertIndication(drugCentralId, diseaseId)
    }
  }

}
