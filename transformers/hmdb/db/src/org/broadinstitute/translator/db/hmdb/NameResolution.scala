package org.broadinstitute.translator.db.hmdb

import java.io.PrintWriter
import java.io.FileWriter

import java.sql.DriverManager
import java.sql.Connection
import java.sql.ResultSet

import java.net.URLEncoder
import java.net.URL
import java.util.LinkedHashMap

import scala.collection.JavaConverters._

object NameResolution {

  private val TAB = "\t"

  private var connection: Connection = null

  def connectToDB(database: String) {
    Class.forName("org.sqlite.JDBC")
    connection = DriverManager.getConnection("jdbc:sqlite:" + database)
  }

  def locationQuery(tag: String) =
    s"""
      select VALUE as TERM
      from PROPERTY 
      join TAG on TAG.TAG_ID = PROPERTY.TAG_ID
      where TAG = '${tag}'
    """

  val ontologyQuery =
    """
      select ONTOLOGY_TERM as TERM
      from ONTOLOGY
      where ONTOLOGY_TYPE = 'child'
    """

  val diseaseQuery =
    """
      select DISEASE as TERM
      from DISEASE
      order by DISEASE_ID
    """

  def queryDB(query: String) = {
    val stm = connection.createStatement()
    stm.executeQuery(query)
  }

  def nameResolverLookup(tag: String, query: String, output: PrintWriter): Unit = {
    val resultSet = queryDB(query)
    while (resultSet.next()) {
      val term = resultSet.getString("TERM")
      println(term)
      for (resolvedTerm <- nameResolverLookup(term)) {
        if (confirmTerm(resolvedTerm, term))
          output.println(tag + TAB + term + TAB + resolvedTerm.primaryId + TAB + resolvedTerm.primaryName)
      }
      output.flush()
    }
  }

  def confirmTerm(resolvedTerm: NameResolver, term: String): Boolean = {
    val url = new URL("https://nodenormalization-sri.renci.org/get_normalized_nodes?curie=" + resolvedTerm.primaryId)
    val json = HTTP.get(url)
    val response: LinkedHashMap[String, Entry] = JSON.mapper.readValue[LinkedHashMap[String, Entry]](json)
    if (response.get(resolvedTerm.primaryId) != null) {
      val entry = response.get(resolvedTerm.primaryId)
      if (confirmTerm(entry.id, term)) {
        return true
      }
      for (id <- entry.equivalent_identifiers) {
        if (confirmTerm(id, term)) {
          return true
        }
      }
    }
    false
  }

  def confirmTerm(id: Entry.ID, term: String): Boolean = {
    id.label != null && term.toLowerCase == id.label.toLowerCase
  }

  def nameResolverLookup(term: String): Set[NameResolver] = {
    try {
      var list: Set[NameResolver] = Set()
      val url = new URL("https://name-resolution-sri.renci.org/lookup?string=" + URLEncoder.encode(term, "UTF-8"))
      val json = HTTP.post(url)
      val response = JSON.mapper.readValue[LinkedHashMap[String, Array[String]]](json)
      for ((key, items) <- response.asScala) {
        for (item <- items) {
          if (term.toLowerCase == item.toLowerCase) {
            list += NameResolver(key, items(0))
          }
        }
      }
      return list
    }
    catch {
      case e: Exception => e.printStackTrace()
    }
    return Set()
  }

  def main(args: Array[String]) {
    connectToDB(args(0))
    val output = new PrintWriter(new FileWriter(args(1)))
    nameResolverLookup("biospecimen", locationQuery("biospecimen_locations"), output)
    nameResolverLookup("cellular", locationQuery("cellular_locations"), output)
    nameResolverLookup("tissue", locationQuery("tissue_locations"), output)
    nameResolverLookup("ontology", ontologyQuery, output)
    nameResolverLookup("disease", diseaseQuery, output)
    output.close()
    connection.close()
  }

}

case class NameResolver(primaryId: String, primaryName: String)
