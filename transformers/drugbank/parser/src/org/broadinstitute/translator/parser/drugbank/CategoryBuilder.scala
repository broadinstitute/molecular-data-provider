package org.broadinstitute.translator.parser.drugbank

import scala.language.reflectiveCalls
import scala.language.implicitConversions

import org.broadinstitute.translator.xml._

object CategoryBuilder {

  implicit def createBuilder(tag: String) = new CategoryBuilder(tag)

}

class CategoryBuilder(val tag: String) extends ParentBuilder {
  val categoryBuilder = new TextValueBuilder("category") =>: children
  val meshIdBuilder = new TextValueBuilder("mesh-id") =>: children
  
  def meshId = meshIdBuilder.textOption.map("MESH:"+_)
}
