package org.broadinstitute.translator.parser.ctrp

import java.io.IOException
import java.io.OutputStreamWriter
import java.net.URL
import java.net.URLConnection
import java.net.URLEncoder
import java.nio.file.{ Paths, Files }

import scala.collection.mutable.Set
import scala.io.Source

import com.fasterxml.jackson.annotation.JsonInclude.Include
import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.scala.DefaultScalaModule
import java.io.PrintWriter

object CTRPparser {

  val mapper = new ObjectMapper()
  mapper.setSerializationInclusion(Include.NON_NULL);
  mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
  mapper.registerModule(DefaultScalaModule)

  def main(args: Array[String]) {
    val root = args(0)
    val moleProURL = args(1)
    val input = root + "/CTRP_AUCv3xAUCv3_compound_metadata.txt"
    val compoundFile = root + "/CTRP_AUCv3xAUCv3_compound_metadata_ids.txt"
    if (!Files.exists(Paths.get(compoundFile))) {
      findCompounds(root + "/CTRP_AUCv3xAUCv3_compound_metadata.txt", moleProURL, compoundFile)
    }

    DB.createDB("CTRP.sqlite")
    val compounds = loadCompounds(compoundFile)
    loadContext(root + "/CTRP_AUCv3xAUCv3_context_metadata.txt")
    loadCorrelations(root + "/CTRP_AUCv3xAUCv3_correlation_with_fdr.csv", compounds)
    DB.createIndexes()
    DB.commit()
    DB.close()
  }

  private def findCompounds(inputFile: String, baseURL: String, outputFile: String): Unit = {
    val input = Source.fromFile(inputFile).getLines
    val output = new PrintWriter(outputFile)
    output.println("cpdId\tname\tbroadCpdId\tcid\tsmiles\tinchi\tinchikey")
    val headerLine = input.take(1).next
    if (headerLine != "master_cpd_id\tcpd_name\tbroad_cpd_id\ttop_test_conc_umol\tcpd_status\tinclusion_rationale\tgene_symbol_of_protein_target\ttarget_or_activity_of_compound\tsource_name\tsource_catalog_id\tcpd_smiles") {
      throw new IOException("Wrong file format: " + inputFile)
    }
    for (line <- input) {
      val row = line.split("\t")
      val cpdId = row(0).toInt
      val name = row(1)
      val broadCpdId = row(2)
      val smiles = row(10)
      println(name + "(" + cpdId + "): " + smiles)
      try {
        httpPost(baseURL + "/by_structure", smiles) match {
          case Some(json) => {
            val response = mapper.readValue(json, classOf[Map[String, Any]])
            val cid = response("identifiers").asInstanceOf[Map[String, String]]("pubchem")
            if (response("structure") != null) {
              val inchi = response("structure").asInstanceOf[Map[String, String]].getOrElse("inchi", null)
              val inchikey = response("structure").asInstanceOf[Map[String, String]].getOrElse("inchikey", null)
              output.println(cpdId + "\t" + name + '\t' + broadCpdId + '\t' + cid + '\t' + smiles + '\t' + inchi + '\t' + inchikey)
            } else {
              output.println(cpdId + "\t" + name + '\t' + broadCpdId + '\t' + cid + '\t' + smiles + '\t' + '\t')
            }
          }
          case None => output.println(cpdId + "\t" + name + '\t' + broadCpdId + '\t' + '\t' + smiles + '\t' + '\t')
        }
      } catch {
        case e: Exception => println(e); DB.insertCompound(cpdId, name, broadCpdId, null, smiles, null, null)
      }
    }
    output.close()
    println("compounds loaded")
  }

  private def loadCompounds(compoundFile: String): Set[Int] = {
    val cpdIds = Set[Int]()
    val input = Source.fromFile(compoundFile).getLines
    val headerLine = input.take(1).next
    if (headerLine != "cpdId\tname\tbroadCpdId\tcid\tsmiles\tinchi\tinchikey") {
      throw new IOException("Wrong file format: " + compoundFile)
    }
    for (line <- input) {
      val row = line.split("\t")
      if (row.length == 7) {
        val cpdId = row(0).toInt
        val name = row(1)
        val broadCpdId = row(2)
        val cid = row(3)
        val smiles = row(4)
        val inchi = row(5)
        val inchikey = row(6)
        if (cid.length > 0 && inchi.length > 0 && inchikey.length > 0) {
          cpdIds.add(cpdId)
          DB.insertCompound(cpdId, name, broadCpdId, cid, smiles, inchi, inchikey)
        } 
      } 
    }
    DB.commit()
    println(cpdIds.size + "compounds loaded")
    return cpdIds
  }

  private def loadContext(filename: String) {
    val src = Source.fromFile(filename).getLines
    val headerLine = src.take(1).next
    if (headerLine != "context_id\tcontext_type\tcontext_name") {
      throw new IOException("Wrong file format: " + filename)
    }
    for (line <- src) {
      val row = line.split("\t")
      val context_id = row(0).toInt
      val context_name = row(2)
      DB.insertContext(context_id, context_name)
    }
    println("context loaded")
  }

  private def loadCorrelations(inputFile: String, compounds: Set[Int]) {
    val input = Source.fromFile(inputFile).getLines
    val headerLine = input.take(1).next
    if (headerLine != "fisher_ztr,pearson_cor,num_samples,robust_z_fdr,slope,intercept,rmse,row_cpd_id,col_cpd_id,context_id,method_id") {
      throw new IOException("Wrong file format: " + inputFile)
    }
    for (line <- input) {
      val row = line.split(",")
      val fisherZ = row(0).toDouble
      val corr = row(1).toDouble
      val nSamples = row(2).toInt
      val fdr = row(3).toDouble
      val compoundId1 = row(7).toInt
      val compoundId2 = row(8).toInt
      val contextId = row(9).toInt
      if (compounds.contains(compoundId1) && compounds.contains(compoundId2)){
        DB.insertTargetMap(compoundId1, compoundId2, contextId, nSamples, corr, fisherZ, fdr)
      }
    }
    DB.commit()
  }

  private def httpPost(url: String, smiles: String): Option[String] = {
    try {
      val connection: URLConnection = new URL(url).openConnection()
      connection.setDoOutput(true);
      connection.setRequestProperty("Content-Type", "application/json")
      val out = new OutputStreamWriter(connection.getOutputStream())
      out.write('"' + URLEncoder.encode(smiles) + '"')
      out.close
      Some(Source.fromInputStream(connection.getInputStream()).mkString)
    } catch {
      case e: Exception => println(e); None
    }
  }
}
