package org.broadinstitute.translator.parser.drugbank

import scala.language.reflectiveCalls
import scala.language.implicitConversions

import org.broadinstitute.translator.xml._

object IdentifierBuilder {

  implicit def createPropertyBuilder(tag: String) = new IdentifierBuilder(tag)

}

class IdentifierBuilder(val tag: String = "property", resourceTag: String = "resource", identifierTag: String = "identifier") extends ParentBuilder {

  val resourceBuilder = new TextValueBuilder(resourceTag) =>: children
  val identifierBuilder = new TextValueBuilder(identifierTag) =>: children
}

