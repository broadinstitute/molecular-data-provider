package org.broadinstitute.translator.parser.drugbank

import scala.language.reflectiveCalls
import scala.language.implicitConversions

import org.broadinstitute.translator.xml._

object ReferenceBuilder {
  implicit def reference(tag: String) = tag match {
    case "article" => new ReferenceBuilder(tag, "pubmed-id", "citation")
    case "textbook" => new ReferenceBuilder(tag, "isbn", "citation")
    case "link" => new ReferenceBuilder(tag, "title", "url")
    case "attachment" => new ReferenceBuilder(tag, "title", "url")

  }
}

class ReferenceBuilder(val tag: String, entry1Tag: String, entry2Tag: String) extends ParentBuilder {

  val refIdBuilder = new TextValueBuilder("ref-id") =>: children
  val entry1Builder = new TextValueBuilder(entry1Tag) =>: children
  val entry2Builder = new TextValueBuilder(entry2Tag) =>: children

}