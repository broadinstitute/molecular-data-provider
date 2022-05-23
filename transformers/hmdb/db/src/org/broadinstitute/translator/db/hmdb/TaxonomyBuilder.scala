package org.broadinstitute.translator.db.hmdb

import scala.language.reflectiveCalls
import scala.language.implicitConversions

import org.broadinstitute.translator.xml._

class TaxonomyBuilder extends ParentBuilder {

  val tag = "taxonomy"

  val descriptionBuilder = new TextValueBuilder("description") =>: children
  val directParentBuilder = new TextValueBuilder("direct_parent") =>: children
  val kingdomBuilder = new TextValueBuilder("kingdom") =>: children
  val superclassBuilder = new TextValueBuilder("super_class") =>: children
  val classBuilder = new TextValueBuilder("class") =>: children
  val subclassBuilder = new TextValueBuilder("sub_class") =>: children
  val molecularFrameworkBuilder = new TextValueBuilder("molecular_framework") =>: children

  val alternativeParentsBuilder = new SequenceBuilder[TextValueBuilder]("alternative_parents", "alternative_parent") =>: children
  val substituentsBuilder = new SequenceBuilder[TextValueBuilder]("substituents", "substituent") =>: children
  val externalDescriptorsBuilder = new SequenceBuilder[TextValueBuilder]("external_descriptors", "external_descriptor") =>: children
}
