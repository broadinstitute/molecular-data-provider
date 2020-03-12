package org.broadinstitute.translator.parser.drugbank

import org.broadinstitute.translator.xml._

class DrugBuilder(val drugType: String) extends ParentBuilder {

  val tag = "drug"

  val idBuilder = new TextValueBuilder("drugbank-id")
  val nameBuilder = new TextValueBuilder("name") =>: children
  val synonymsBuilder = new SequenceBuilder[TextValueBuilder]("synonyms", "synonym") =>: children
  val casNumberBuilder = new TextValueBuilder("cas-number") =>: children
  val idsBuilder = new SequenceBuilder[PropertyBuilder]("external-identifiers", "external-identifier")(createIdentifierBuilder) =>: children
  val calcPropertiesBuilder = new SequenceBuilder[PropertyBuilder]("calculated-properties","property")(createPropertyBuilder) =>: children
  val targetsBuilder = new SequenceBuilder[TargetBuilder]("targets","target")  =>: children
  
  override def createBuilder(tag: String, attr: Map[String, String]): Option[Builder] = tag match {
    case "drugbank-id" if attr.get("primary") == Some("true") => Some(idBuilder)
    case other => super.createBuilder(tag, attr)
  }

  override def close() {
    println(idBuilder.text + ": " + nameBuilder.text)
    val drugId = DB.insertDrug(idBuilder.text, drugType, nameBuilder.text)
    for (casNumber <- casNumberBuilder.get) {
      //println("  CAS: " + casNumber)
      DB.insertIdentifier(drugId, casNumber, "CAS")
    }
    for (synonym <- synonymsBuilder) {
      //println("  " + synonym.text)
      DB.insertSynonym(drugId, synonym.text)
    }
    for (id <- idsBuilder) {
      //println("  "+id.nameBuilder.text+": "+id.valueBuilder.text)
      DB.insertIdentifier(drugId, id.valueBuilder.text, id.nameBuilder.text)
    }
    for (property <- calcPropertiesBuilder) {
      if (property.nameBuilder.text == "SMILES" || property.nameBuilder.text == "InChI" || property.nameBuilder.text == "InChIKey") {
        DB.insertIdentifier(drugId, property.valueBuilder.text, property.nameBuilder.text)
      }
    }
    for (target <- targetsBuilder) {

      println("  " + target.targetIdBuilder.text)
      for (polypeptide <- target.polypeptideBuilder) {
        val targetId = TargetBuilder.get(polypeptide.id) match {
          case Some(targetId) => targetId
          case None => {
            val targetId = DB.insertTarget(polypeptide.id, polypeptide.uniprot, polypeptide.geneId, polypeptide.nameBuilder.text)
            TargetBuilder += polypeptide.id -> targetId
            targetId
          }
        }
        DB.insertTargetMap(drugId, targetId, target.actions)
      }
    }
  }

  def createIdentifierBuilder(tag: String) = new PropertyBuilder(tag, "resource", "identifier")

  def createPropertyBuilder(tag: String) = new PropertyBuilder(tag, nameTag = "kind")

}
