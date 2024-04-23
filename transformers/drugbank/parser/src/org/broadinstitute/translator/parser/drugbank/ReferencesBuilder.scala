package org.broadinstitute.translator.parser.drugbank

import scala.language.reflectiveCalls

import org.broadinstitute.translator.xml._

class ReferencesBuilder(val tag: String) extends ParentBuilder {

  val articlesBuilder = new SequenceBuilder[ReferenceBuilder]("articles", "article") =>: children
  val textbooksBuilder = new SequenceBuilder[ReferenceBuilder]("textbooks", "textbook") =>: children
  val linksBuilder = new SequenceBuilder[ReferenceBuilder]("links", "link") =>: children
  val attachmentsBuilder = new SequenceBuilder[ReferenceBuilder]("attachments", "attachment") =>: children

  val references = articlesBuilder :: textbooksBuilder :: linksBuilder :: attachmentsBuilder :: Nil

}
