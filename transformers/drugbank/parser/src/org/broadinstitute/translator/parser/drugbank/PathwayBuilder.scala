package org.broadinstitute.translator.parser.drugbank

import scala.language.reflectiveCalls
import scala.language.implicitConversions

import org.broadinstitute.translator.xml._
import scala.collection.mutable.HashMap

object PathwayBuilder {

  private val pathways = new HashMap[String, Int]()

  implicit def createBuilder(tag: String) = new PathwayBuilder(tag)

  def pathwayId(smpdbId: String): Int = pathways(smpdbId)

}

class PathwayBuilder(val tag: String) extends ParentBuilder {
  val smpdbIdBuilder = new TextValueBuilder("smpdb-id") =>: children
  val nameBuilder = new TextValueBuilder("name") =>: children
  val categoryBuilder = new TextValueBuilder("category") =>: children
  val drugsBuilder = new SequenceBuilder[MemberDrug]("drugs", "drug") =>: children
  val enzymesBuilder = new SequenceBuilder[TextValueBuilder]("enzymes", "uniprot-id") =>: children

  type MemberDrug = HomogenParentBuilder[TextValueBuilder]

  implicit def memberDrug(tag: String): MemberDrug = HomogenParentBuilder[TextValueBuilder](tag)(
    "drugbank-id",
    "name")

  override def close() {
    for (xref <- smpdbIdBuilder.get) {
      if (PathwayBuilder.pathways.contains(xref)) {
        return
      }
      for (name <- nameBuilder.get) {
        val pathwayId = DB.insertPathway(xref, name, categoryBuilder.get)
        PathwayBuilder.pathways(xref) = pathwayId
        for (drugBuilder <- drugsBuilder){
          DB.insertPathwayMember(pathwayId, drugBuilder.tag, drugBuilder("drugbank-id").get.text, drugBuilder("name").flatMap(_.get))
        }
        for (enzymeBuilder <- enzymesBuilder){
          DB.insertPathwayMember(pathwayId, "enzyme", enzymeBuilder.text, None)
        }
      }
    }
  }
}

