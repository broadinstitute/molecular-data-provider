package org.broadinstitute.translator.parser.drugbank

import scala.language.reflectiveCalls
import scala.language.implicitConversions

import org.broadinstitute.translator.xml._

object PropertyBuilder {

  implicit def createPropertyBuilder(tag: String) = new PropertyBuilder(tag)

}

class PropertyBuilder(val tag: String = "property", nameTag: String = "kind", valueTag: String = "value", sourceTag: String = "source") extends ParentBuilder {

  val nameBuilder = new TextValueBuilder(nameTag) =>: children
  val valueBuilder = new TextValueBuilder(valueTag) =>: children
  val sourceBuilder = new TextValueBuilder(sourceTag) =>: children

  def name = nameBuilder.text
  def value = valueBuilder.text
}