package org.broadinstitute.translator.db.hmdb

import scala.language.reflectiveCalls
import scala.language.implicitConversions

import org.broadinstitute.translator.xml._
import scala.collection.mutable.ArrayBuffer

object OntologyBuilder {

  implicit def createBuilder(tag: String) = new OntologyBuilder(tag)

}

class OntologyBuilder(val tag: String) extends ParentBuilder {

  val termBuilder = new TextValueBuilder("term") =>: children
  val definitionBuilder = new TextValueBuilder("definition") =>: children
  private val parent_idBuilder = new TextValueBuilder("parent_id") =>: children
  private val levelBuilder = new TextValueBuilder("level") =>: children
  val typeBuilder = new TextValueBuilder("type") =>: children

  val synonymsBuilder = new SequenceBuilder[TextValueBuilder]("synonyms", "synonym") =>: children
  val descendantsBuilder = new SequenceBuilder[OntologyBuilder]("descendants", "descendant") =>: children

  def level: Int = levelBuilder.text.toInt
  def xmlParentId: Option[Int] = parent_idBuilder.textOption.map(_.toInt)

  override def toString(): String = {
    var str = term
    for (descendantBuilder <- descendantsBuilder) {
      str = str + descendantBuilder
    }
    return str
  }

  private def term: String = {
    var str = ""
    for (i <- 0 until level) {
      str = str + "  "
    }
    return str + "(" + level + ")" + termBuilder.text + "\n"
  }
}
