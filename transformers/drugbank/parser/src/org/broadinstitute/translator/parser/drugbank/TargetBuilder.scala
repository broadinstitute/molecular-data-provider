package org.broadinstitute.translator.parser.drugbank

import scala.language.reflectiveCalls
import scala.language.implicitConversions

import org.broadinstitute.translator.xml._
import collection.mutable.HashMap
import collection.mutable.ArrayBuffer

object TargetBuilder {

  private val targets = new HashMap[String, Int]()

  private def +=(entry: Tuple2[String, Int]): Unit = {
    targets += entry
  }

  def apply(targetId: String) = targets.get(targetId)

  implicit def createTargetBuilder(tag: String): TargetBuilder = new TargetBuilder(tag)
}

class TargetBuilder(val tag: String) extends ParentBuilder with Attributes {

  import PolypeptideBuilder.GOBuilder
  import PolypeptideBuilder.PFamBuilder
  
  val targetIdBuilder = new TextValueBuilder("id") =>: children
  val nameBuilder = new TextValueBuilder("name") =>: children
  val organismBuilder = new TextValueBuilder("organism") =>: children
  val actionsBuilder = new SequenceBuilder[TextValueBuilder]("actions", "action") =>: children
  val referencesBuilder = new ReferencesBuilder("references") =>: children
  val knownActionBuilder = new TextValueBuilder("known-action") =>: children
  val polypeptidesBuilder = new ArrayBuffer[PolypeptideBuilder]()
  val inhibitionStrengthBuilder = new TextValueBuilder("inhibition-strength") =>: children
  val inductionStrengthBuilder = new TextValueBuilder("induction-strength") =>: children

  override def createBuilder(tag: String, attr: Map[String, String]): Option[Builder] = tag match {
    case "polypeptide" => {
      val polypeptideBuilder = new PolypeptideBuilder()
      polypeptidesBuilder += polypeptideBuilder
      Some(polypeptideBuilder)
    }
    case other => super.createBuilder(tag, attr)
  }

  def actions: String = actionsBuilder.elements.map(_.text).mkString(";")

  override def close() {
    val targetIdentifier = targetIdBuilder.text
    if (TargetBuilder(targetIdentifier) == None) {
      val targetId = DB.insertTarget(targetIdentifier, nameBuilder.text, organismBuilder.get, knownActionBuilder.get)
      for (polypeptide <- polypeptidesBuilder) {
        insertPolypeptide(targetId, polypeptide)
      }
      TargetBuilder += targetIdentifier -> targetId
    }
  }

  def insertPolypeptide(targetId: Int, polypeptide: PolypeptideBuilder) = {
    val polypeptideId = DB.insertPolypeptide(targetId, polypeptide.nameBuilder.text, polypeptide.attr("id"), polypeptide.attr("source"))
    insertProperty(polypeptideId, polypeptide.generalFunctionBuilder)
    insertProperty(polypeptideId, polypeptide.specificFunctionBuilder)
    insertProperty(polypeptideId, polypeptide.geneNameBuilder)
    insertProperty(polypeptideId, polypeptide.locusBuilder)
    insertProperty(polypeptideId, polypeptide.cellularLocationBuilder)
    insertProperty(polypeptideId, polypeptide.transmembraneRegionsBuilder)
    insertProperty(polypeptideId, polypeptide.signalRegionsBuilder)
    insertProperty(polypeptideId, polypeptide.theoreticalPiBuilder)
    insertProperty(polypeptideId, polypeptide.molecularWeightBuilder)
    insertProperty(polypeptideId, polypeptide.chromosomeLocationBuilder)
    insertProperty(polypeptideId, polypeptide.organismBuilder)
    for (goBuilder <- polypeptide.goBuilder) {
      insertProperty(polypeptideId, goBuilder)
    }
    for (synonym <- polypeptide.synonymsBuilder){
      insertProperty(polypeptideId, synonym)
    }
    for (id <- polypeptide.idsBuilder)
      for (resource <- id.resourceBuilder.textOption)
        for (identifier <- id.identifierBuilder.textOption) {
          DB.insertPolypeptideIdentifier(polypeptideId, id.tag, resource, identifier)
        }
    for (pfam <- polypeptide.pfamsBuilder){
      insertPfam(polypeptideId, pfam)
    }
  }

  def insertProperty(polypeptideId: Int, property: TextValueBuilder) {
    for (value <- property.textOption) {
      val propertyId = DB.getPropertyId(property.tag, value) match {
        case Some(id) => id
        case None => DB.insertProperty(property.tag, value)
      }
      DB.insertPolypeptideProperty(polypeptideId, propertyId)
    }
  }

  def insertProperty(polypeptideId: Int, goBuilder: GOBuilder) {
    for (description <- goBuilder("description").flatMap(_.textOption)) {
      val category = goBuilder("category").flatMap(_.textOption)
      val propertyId = DB.getPropertyId(goBuilder.tag, category, description, None) match {
        case Some(id) => id
        case None => DB.insertProperty(goBuilder.tag, category, description, None)
      }
      DB.insertPolypeptideProperty(polypeptideId, propertyId)
    }
  }

  def insertPfam(polypeptideId: Int, pfamBuilder: PFamBuilder) {
    for (identifier <- pfamBuilder("identifier").flatMap(_.textOption))
      for (name <- pfamBuilder("name").flatMap(_.textOption)) {
        val pfamId = DB.getPfam(identifier, name) match {
          case Some(id) => id
          case None => DB.insertPfam(identifier, name)
        }
        DB.insertPfamMapRow(polypeptideId, pfamId)
      }
  }

}