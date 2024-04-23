package org.broadinstitute.translator.parser.pubchem
import scala.language.implicitConversions
import scala.language.reflectiveCalls

import org.broadinstitute.translator.xml._

object PropertyBuilder {

  def apply(tag: String) = new PropertyBuilder(tag)

  implicit def createBuilder(tag: String) = PropertyBuilder(tag)

}

class PropertyBuilder(override val tag: String) extends ParentBuilder {

  val labelBuilder = new TextValueBuilder("PC-Urn_label") =>: children
  val nameBuilder = new TextValueBuilder("PC-Urn_name") =>: children
  val typeBuilder = new TextValueBuilder("PC-UrnDataType") =>: children
  val implementationBuilder = new TextValueBuilder("PC-Urn_implementation") =>: children
  val versionBuilder = new TextValueBuilder("PC-Urn_version") =>: children
  val softwareBuilder = new TextValueBuilder("PC-Urn_software") =>: children
  val sourceBuilder = new TextValueBuilder("PC-Urn_source") =>: children
  val releaseBuilder = new TextValueBuilder("PC-Urn_release") =>: children
  val iValueBuilder = new TextValueBuilder("PC-InfoData_value_ival") =>: children
  val sValueBuilder = new TextValueBuilder("PC-InfoData_value_sval") =>: children
  val fValueBuilder = new TextValueBuilder("PC-InfoData_value_fval") =>: children

  val typeMap = Map[Option[String], TextValueBuilder](Some("1") -> sValueBuilder, Some("5") -> iValueBuilder, Some("7") -> fValueBuilder)

  override def createBuilder(tag: String, attr: Map[String, String]) = None

  override def close() {
  }

  def isDefined = typeMap.get(typeBuilder.get).isDefined

  def label = labelBuilder.text

  def value = typeMap.get(typeBuilder.get).get.text

}