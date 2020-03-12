package org.broadinstitute.translator.parser.drugbank

import org.broadinstitute.translator.xml._
import collection.mutable.HashMap
import collection.mutable.ArrayBuffer

object TargetBuilder {

  val targets = new HashMap[String, Int]()

  def +=(entry: Tuple2[String, Int]): Unit = {
    targets += entry
  }

  def get(targetId: String) = targets.get(targetId)

  implicit def createTargetBuilder(tag: String): TargetBuilder = new TargetBuilder
}

class TargetBuilder extends ParentBuilder {
  val tag = "target"

  val targetIdBuilder = new TextValueBuilder("id") =>: children
  
  val actionBuilder = new SequenceBuilder[TextValueBuilder]("actions", "action") =>: children
  val polypeptideBuilder = new ArrayBuffer[PolypeptideBuilder]()

  override def createBuilder(tag: String, attr: Map[String, String]): Option[Builder] = tag match {
    case "polypeptide" => Some(new PolypeptideBuilder(attr("id"), attr("source")))
    case other => super.createBuilder(tag, attr)
  }
  
  def actions: String = actionBuilder.elements.map(_.text).mkString(";")

  override def close() {
    println("  " + targetIdBuilder.text + ": " + actions)
  }

  class PolypeptideBuilder(val id: String, val source: String) extends ParentBuilder {

    val tag = "polypeptide"
    
    val nameBuilder = new TextValueBuilder("name") =>: children
    val idsBuilder = new SequenceBuilder[PropertyBuilder]("external-identifiers", "external-identifier")(createIdentifierBuilder) =>: children

    def createIdentifierBuilder(tag: String) = new PropertyBuilder(tag, "resource", "identifier")

    def uniprot = getId("UniProtKB");
    def geneId = getId("HUGO Gene Nomenclature Committee (HGNC)");

    private def getId(key: String): Option[String] = {
      for (id <- idsBuilder) {
        if (id.nameBuilder.text == key) {
          return Some(id.value)
        }
      }
      return None
    }

    override def close() {
      println("    " + id + ": " + source + " | " + uniprot + " | " + geneId)
      polypeptideBuilder += this
    }

  }
}