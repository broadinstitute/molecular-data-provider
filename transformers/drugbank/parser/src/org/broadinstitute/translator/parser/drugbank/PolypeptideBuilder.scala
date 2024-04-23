package org.broadinstitute.translator.parser.drugbank

import scala.language.reflectiveCalls
import scala.language.implicitConversions

import org.broadinstitute.translator.xml._

object PolypeptideBuilder {

  type PFamBuilder = HomogenParentBuilder[TextValueBuilder]

  type GOBuilder = HomogenParentBuilder[TextValueBuilder]
}

class PolypeptideBuilder() extends ParentBuilder with Attributes {

  import PolypeptideBuilder.PFamBuilder
  import PolypeptideBuilder.GOBuilder

  val tag = "polypeptide"

  val nameBuilder = new TextValueBuilder("name") =>: children
  val generalFunctionBuilder = new TextValueBuilder("general-function") =>: children
  val specificFunctionBuilder = new TextValueBuilder("specific-function") =>: children
  val geneNameBuilder = new TextValueBuilder("gene-name") =>: children
  val locusBuilder = new TextValueBuilder("locus") =>: children
  val cellularLocationBuilder = new TextValueBuilder("cellular-location") =>: children
  val transmembraneRegionsBuilder = new TextValueBuilder("transmembrane-regions") =>: children
  val signalRegionsBuilder = new TextValueBuilder("signal-regions") =>: children
  val theoreticalPiBuilder = new TextValueBuilder("theoretical-pi") =>: children
  val molecularWeightBuilder = new TextValueBuilder("molecular-weight") =>: children
  val chromosomeLocationBuilder = new TextValueBuilder("chromosome-location") =>: children
  val organismBuilder = new TextValueBuilder("organism") with Attributes =>: children
  val idsBuilder = new SequenceBuilder[IdentifierBuilder]("external-identifiers", "external-identifier") =>: children
  val synonymsBuilder = new SequenceBuilder[TextValueBuilder]("synonyms", "synonym") =>: children
  val pfamsBuilder = new SequenceBuilder[PFamBuilder]("pfams", "pfam")(pfamBuilder) =>: children
  val goBuilder = new SequenceBuilder[GOBuilder]("go-classifiers", "go-classifier")(goClassifiers) =>: children

  private def pfamBuilder(tag: String): PFamBuilder = HomogenParentBuilder[TextValueBuilder](tag)("identifier", "name")

  private def goClassifiers(tag: String): GOBuilder = HomogenParentBuilder[TextValueBuilder](tag)("category", "description")
}