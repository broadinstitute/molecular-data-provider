package org.broadinstitute.translator.db.hmdb

import scala.language.reflectiveCalls
import scala.language.implicitConversions

import org.broadinstitute.translator.xml._

object ConcentrationBuilder {

  implicit def createNormalConcentrationBuilder(tag: String) = new NormalConcentrationBuilder

  implicit def createAbnormalConcentrationBuilder(tag: String) = new AbnormalConcentrationBuilder
}

abstract class ConcentrationBuilder extends ParentBuilder {

  type ReferenceBuilder = MetaboliteBuilder.ReferenceBuilder

  val tag = "concentration"

  val biospecimenBuilder = new TextValueBuilder("biospecimen") =>: children
  val concentrationValueBuilder = new TextValueBuilder("concentration_value") =>: children
  val concentrationUnitsBuilder = new TextValueBuilder("concentration_units") =>: children
  val ageBuilder: TextValueBuilder
  val genderBuilder: TextValueBuilder
  val subjectConditionBuilder = new TextValueBuilder("subject_condition") =>: children
  val patientInformationBuilder = new TextValueBuilder("patient_information") =>: children
  val commentBuilder = new TextValueBuilder("comment") =>: children
  val referencesBuilder = new SequenceBuilder[ReferenceBuilder]("references", "reference")(MetaboliteBuilder.reference) =>: children
}

class NormalConcentrationBuilder extends ConcentrationBuilder {

  val ageBuilder = new TextValueBuilder("subject_age") =>: children
  val genderBuilder = new TextValueBuilder("subject_sex") =>: children
}

class AbnormalConcentrationBuilder extends ConcentrationBuilder {

  val ageBuilder = new TextValueBuilder("patient_age") =>: children
  val genderBuilder = new TextValueBuilder("patient_sex") =>: children
}
