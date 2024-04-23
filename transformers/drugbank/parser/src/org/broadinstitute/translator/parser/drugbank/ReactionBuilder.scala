package org.broadinstitute.translator.parser.drugbank

import scala.language.reflectiveCalls
import scala.language.implicitConversions

import org.broadinstitute.translator.xml._

object ReactionBuilder {

  implicit def enzymeBuilder(tag: String): ReactionBuilder = new ReactionBuilder(tag)
}

class ReactionBuilder(val tag: String) extends ParentBuilder {

  type EnzymeBuilder = HomogenParentBuilder[TextValueBuilder]

  val sequenceBuilder = new TextValueBuilder("sequence") =>: children
  val leftElementBuilder = elementBuilder("left-element") =>: children
  val rightElementBuilder = elementBuilder("right-element") =>: children
  val enzymesBuilder = new SequenceBuilder[EnzymeBuilder]("enzymes", "enzyme") =>: children

  private def elementBuilder(tag: String) = HomogenParentBuilder[TextValueBuilder](tag)("drugbank-id", "name")

  implicit def enzymeBuilder(tag: String): EnzymeBuilder = HomogenParentBuilder[TextValueBuilder](tag)("drugbank-id", "name", "uniprot-id")
}
