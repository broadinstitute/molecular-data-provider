package org.broadinstitute.translator.parser.pubchem

import scala.io.Source
import scalaj.http.Http
import org.broadinstitute.translator.xml._

object PubChemPUG {

  var lastQuryTime: Long = (new java.util.Date).getTime

  def getDescriptions(cid: String) = {

    val url = s"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/${cid}/description/XML"
    val now = (new java.util.Date).getTime
    Thread.sleep(math.max(0, 500 - (now - lastQuryTime)))
    val source = Source.fromURL(url)(io.Codec("UTF-8"))
    val rootBuilder = new InformationList
    Parser.parse(source, rootBuilder)
    lastQuryTime = (new java.util.Date).getTime
    rootBuilder.informationList.elements
  }

  class InformationList extends Builder {
    val informationList = new SequenceBuilder[InformationBuilder]("InformationList", "Information")
    val tag = ""
    override def getBuilder(tag: String, attr: Map[String, String]): Option[Builder] = tag match {
      case "InformationList" => Some(informationList)
      case _                 => None
    }
  }

  class InformationBuilder(val tag: String) extends ParentBuilder {
    val cidBuilder = new TextValueBuilder("CID") =>: children
    val titleBuilder = new TextValueBuilder("Title") =>: children
    val descBuilder = new TextValueBuilder("Description") =>: children
    val sourceBuilder = new TextValueBuilder("DescriptionSourceName") =>: children
    val urlBuilder = new TextValueBuilder("DescriptionURL") =>: children
  }

  implicit def createBuilder(tag: String): InformationBuilder = new InformationBuilder(tag)

  def findCID(name: String) = {
    val url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/cids/XML"
    val now = (new java.util.Date).getTime
    Thread.sleep(math.max(0, 500 - (now - lastQuryTime)))
    val result = Http(url).postData("name=" + name)
    val source = Source.fromString(result.asString.body)
    val rootBuilder = new IdentifierList
    Parser.parse(source, rootBuilder)
    lastQuryTime = (new java.util.Date).getTime
    rootBuilder.informationList.elements.map(_.text.toLong)
  }

  class IdentifierList extends Builder {
    val informationList = new SequenceBuilder[TextValueBuilder]("IdentifierList", "CID")
    val tag = ""
    override def getBuilder(tag: String, attr: Map[String, String]): Option[Builder] = tag match {
      case "IdentifierList" => Some(informationList)
      case _                => None
    }
  }

  def main(args: Array[String]): Unit = {
    for (cid <- findCID("dacarbazine")) {
      println("cid: " + cid)
    }
  }
}
