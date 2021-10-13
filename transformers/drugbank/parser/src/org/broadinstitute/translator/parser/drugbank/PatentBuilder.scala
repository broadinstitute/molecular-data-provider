package org.broadinstitute.translator.parser.drugbank

import scala.language.reflectiveCalls
import scala.language.implicitConversions

import org.broadinstitute.translator.xml._

object PatentBuilder {

  implicit def createBuilder(tag: String) = new PatentBuilder(tag)

}

class PatentBuilder(val tag: String) extends ParentBuilder {

  val numberBuilder = new TextValueBuilder("number") =>: children
  val countryBuilder = new TextValueBuilder("country") =>: children
  val approvedBuilder = new TextValueBuilder("approved") =>: children
  val expiresBuilder = new TextValueBuilder("expires") =>: children
  val pediatricBuilder = new TextValueBuilder("pediatric-extension") =>: children

}
