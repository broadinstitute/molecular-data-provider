package org.broadinstitute.translator.db.hmdb

import scala.language.reflectiveCalls
import scala.language.implicitConversions

import org.broadinstitute.translator.xml._

object DiseaseBuilder {

  implicit def createDiseaseBuilder(tag: String) = new DiseaseBuilder

}

class DiseaseBuilder extends ParentBuilder {

  type ReferenceBuilder = MetaboliteBuilder.ReferenceBuilder

  val tag = "disease"

  val nameBuilder = new TextValueBuilder("name") =>: children
  val omimBuilder = new TextValueBuilder("omim_id") =>: children
  val referencesBuilder = new SequenceBuilder[ReferenceBuilder]("references", "reference")(MetaboliteBuilder.reference) =>: children

}
