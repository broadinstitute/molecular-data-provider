package org.broadinstitute.translator.parser.drugbank

import org.broadinstitute.translator.xml._

class PropertyBuilder(val tag: String = "property", nameTag: String = "name", valueTag: String = "value") extends ParentBuilder {

  val nameBuilder = new TextValueBuilder(nameTag) =>: children
  val valueBuilder = new TextValueBuilder(valueTag) =>: children

  def name = nameBuilder.text
  def value = valueBuilder.text
}