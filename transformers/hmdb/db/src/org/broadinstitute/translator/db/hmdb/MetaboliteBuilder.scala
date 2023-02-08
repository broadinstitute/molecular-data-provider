package org.broadinstitute.translator.db.hmdb

import scala.language.reflectiveCalls
import scala.language.implicitConversions

import org.broadinstitute.translator.xml._

class MetaboliteBuilder extends ParentBuilder {

  val tag = "metabolite"

  // builders

  val accessionBuilder = new TextValueBuilder("accession") =>: children
  val accessionsBuilder = new SequenceBuilder[TextValueBuilder]("secondary_accessions", "accession") =>: children
  val nameBuilder = new TextValueBuilder("name") =>: children
  val synonymsBuilder = new SequenceBuilder[TextValueBuilder]("synonyms", "synonym") =>: children
  val iupacBuilder = new TextValueBuilder("iupac_name") =>: children
  val traditionalIupacBuilder = new TextValueBuilder("traditional_iupac") =>: children
  val taxonomyBuilder = new TaxonomyBuilder =>: children
  val ontologiesBuilder = new SequenceBuilder[OntologyBuilder]("ontology", "root") =>: children
  val expPropertiesBuilder = new SequenceBuilder[PropertyBuilder]("experimental_properties", "property") =>: children
  val predPropertiesBuilder = new SequenceBuilder[PropertyBuilder]("predicted_properties", "property") =>: children
  val cellularLocationsBuilder = new SequenceBuilder[TextValueBuilder]("cellular_locations", "cellular") =>: children
  val biospecimenLocationsBuilder = new SequenceBuilder[TextValueBuilder]("biospecimen_locations", "biospecimen") =>: children
  val tissueLocationsBuilder = new SequenceBuilder[TextValueBuilder]("tissue_locations", "tissue") =>: children
  val pathwaysBuilder = new SequenceBuilder[PathwayBuilder]("pathways", "pathway")(pathwayBuilder) =>: children
  val normalConcentrationsBuilder = new SequenceBuilder[NormalConcentrationBuilder]("normal_concentrations", "concentration") =>: children
  val abnormalConcentrationsBuilder = new SequenceBuilder[AbnormalConcentrationBuilder]("abnormal_concentrations", "concentration") =>: children
  val diseasesBuilder = new SequenceBuilder[DiseaseBuilder]("diseases", "disease") =>: children
  val synthesisReferenceBuilder = new TextValueBuilder("synthesis_reference") =>: children
  val referencesBuilder = new SequenceBuilder[ReferenceBuilder]("general_references", "reference")(MetaboliteBuilder.reference) =>: children
  val proteinsBuilder = new SequenceBuilder[ProteinBuilder]("protein_associations", "protein")(proteinBuilder) =>: children

  val propertiesBuilders = {
    val propertyTags = Array(
      "status",
      "description",
      "chemical_formula",
      "average_molecular_weight",
      "monisotopic_molecular_weight",
      "state")
    propertyTags.map { tag =>
      new TextValueBuilder(tag) =>: children
    }
  }

  val identifiersBuilders = {
    val identifiersTags = Array(
      "cas_registry_number",
      "smiles",
      "inchi",
      "inchikey",
      "chemspider_id",
      "drugbank_id",
      "foodb_id",
      "pubchem_compound_id",
      "pdb_id",
      "chebi_id",
      "phenol_explorer_compound_id",
      "knapsack_id",
      "kegg_id",
      "biocyc_id",
      "bigg_id",
      "wikipedia_id",
      "metlin_id",
      "vmh_id",
      "fbonto_id")
    identifiersTags.map { tag =>
      new TextValueBuilder(tag) =>: children
    }
  }

  override def createBuilder(tag: String, attr: Map[String, String]): Option[Builder] = tag match {
    case "biological_properties" => None
    case other => super.createBuilder(tag, attr)
  }

  // metabolite

  override def close() {
    println(accessionBuilder.text + ": " + nameBuilder.text)
    val metaboliteId = DB.insertMetabolite(accessionBuilder.text, nameBuilder.text)
    insertNames(metaboliteId)
    insertIdentifiers(metaboliteId)
    insertProperties(metaboliteId)
    insertTaxonomy(metaboliteId)
    insertOntologies(metaboliteId)
    insertPathways(metaboliteId)
    insertConcentrations(metaboliteId)
    insertDisease(metaboliteId)
    insertReferences(metaboliteId)
    insertProtein(metaboliteId)
  }

  // names

  def insertNames(metaboliteId: Long) {
    insertName(metaboliteId, iupacBuilder)
    insertName(metaboliteId, traditionalIupacBuilder)
    for (synonymBuilder <- synonymsBuilder) {
      for (synonym <- synonymBuilder.textOption) {
        DB.insertName(metaboliteId, synonym, "synonym")
      }
    }
  }

  def insertName(metaboliteId: Long, builder: TextValueBuilder) {
    for (name <- builder.textOption) {
      DB.insertName(metaboliteId, name, builder.tag)
    }
  }

  // identifiers

  def insertIdentifiers(metaboliteId: Long) {
    for (builder <- accessionsBuilder) {
      for (xfer <- builder.textOption) {
        DB.insertIdentifier(metaboliteId, "secondary_accession", xfer)
      }
    }
    for (builder <- identifiersBuilders) {
      for (xfer <- builder.textOption) {
        DB.insertIdentifier(metaboliteId, builder.tag, xfer)
      }
    }
  }

  // properties

  def insertProperties(metaboliteId: Long) {
    for (property <- propertiesBuilders) {
      insertProperty(metaboliteId, property)
    }
    for (property <- expPropertiesBuilder) {
      insertProperty(metaboliteId, expPropertiesBuilder.tag, property)
    }
    for (property <- predPropertiesBuilder) {
      insertProperty(metaboliteId, predPropertiesBuilder.tag, property)
    }
    for (builder <- cellularLocationsBuilder :: biospecimenLocationsBuilder :: tissueLocationsBuilder :: Nil)
      for (propertyBuilder <- builder) {
        for (value <- propertyBuilder.textOption) {
          DB.insertMetaboliteProperty(metaboliteId, builder.tag, Some(propertyBuilder.tag), value, None)
        }
      }
  }

  def insertProperty(metaboliteId: Long, property: TextValueBuilder) = {
    for (value <- property.textOption) {
      DB.insertMetaboliteProperty(metaboliteId, property.tag, None, value, None)
    }
  }

  def insertProperty(metaboliteId: Long, propertyTag: String, property: PropertyBuilder) = {
    for (kind <- property.nameBuilder.textOption) {
      for (value <- property.valueBuilder.textOption) {
        DB.insertMetaboliteProperty(metaboliteId, propertyTag, Some(kind), value, property.sourceBuilder.textOption)
      }
    }
  }

  // taxonomy

  def insertTaxonomy(metaboliteId: Long) {
    val description = taxonomyBuilder.descriptionBuilder.text
    val directParent = taxonomyBuilder.directParentBuilder.text
    val kingdom = taxonomyBuilder.kingdomBuilder.text
    val superclass = taxonomyBuilder.superclassBuilder.text
    val taxonomyClass = taxonomyBuilder.classBuilder.text
    val subclass = taxonomyBuilder.subclassBuilder.textOption
    val molecularFramework = taxonomyBuilder.molecularFrameworkBuilder.textOption
    val taxonomyId = DB.getTaxonomy(description, directParent, kingdom, superclass, taxonomyClass, subclass, molecularFramework)
    DB.insertTaxonomy(metaboliteId, taxonomyId)

    for (builder <- taxonomyBuilder.alternativeParentsBuilder :: taxonomyBuilder.substituentsBuilder :: taxonomyBuilder.externalDescriptorsBuilder :: Nil) {
      for (propertyBuilder <- builder) {
        val propertyId = DB.getProperty(propertyBuilder.tag, None, propertyBuilder.text, None)
        if (DB.findTaxonomyProperty(metaboliteId, propertyId)) {
          println("  Warning: duplicate property, metaboliteId = " + metaboliteId + "\t" + propertyBuilder.tag + " = " + propertyBuilder.text)
        }
        else {
          DB.insertTaxonomyProperty(metaboliteId, propertyId)
        }
      }
    }
  }

  // ontology

  def insertOntologies(metaboliteId: Long) {
    insertOntologies(metaboliteId, ontologiesBuilder, None)
  }

  def insertOntologies(metaboliteId: Long, ontologiesBuilder: SequenceBuilder[OntologyBuilder], parentId: Option[Int]) {
    for (ontologyBuilder <- ontologiesBuilder) {
      val term = ontologyBuilder.termBuilder.text
      val definition = ontologyBuilder.definitionBuilder.textOption
      val ontologyType = ontologyBuilder.typeBuilder.text
      val symonyms = ontologyBuilder.synonymsBuilder.elements.map(_.text)
      val ontologyId = DB.getOntology(parentId, term, definition, ontologyBuilder.xmlParentId, ontologyBuilder.level, ontologyType, symonyms)
      insertOntologies(metaboliteId, ontologyBuilder.descendantsBuilder, Some(ontologyId))
      if (ontologyType == "child" || ontologyBuilder.descendantsBuilder.elements.size == 0) {
        DB.insertOntology(metaboliteId, ontologyId)
      }
    }
  }

  // pathway

  type PathwayBuilder = HomogenParentBuilder[TextValueBuilder]

  def pathwayBuilder(tag: String): ReferenceBuilder = {
    HomogenParentBuilder[TextValueBuilder](tag)("name", "smpdb_id", "kegg_map_id")
  }

  def insertPathways(metaboliteId: Long) {
    for (pathwayBuilder <- pathwaysBuilder) {
      DB.insertPathway(metaboliteId, pathwayBuilder("name"), pathwayBuilder("smpdb_id"), pathwayBuilder("kegg_map_id"))
    }
  }

  //concentration

  def insertConcentrations(metaboliteId: Long) {
    for (concentrationBuilder <- normalConcentrationsBuilder) {
      insertConcentration(metaboliteId, concentrationBuilder, abnormal = false)
    }
    for (concentrationBuilder <- abnormalConcentrationsBuilder) {
      insertConcentration(metaboliteId, concentrationBuilder, abnormal = true)
    }
  }

  def insertConcentration(metaboliteId: Long, concentrationBuilder: ConcentrationBuilder, abnormal: Boolean) {
    val concentrationId = DB.insertConcentration(
      metaboliteId, abnormal, concentrationBuilder.biospecimenBuilder.textOption, concentrationBuilder.concentrationValueBuilder.textOption,
      concentrationBuilder.concentrationUnitsBuilder.textOption, concentrationBuilder.ageBuilder.textOption,
      concentrationBuilder.genderBuilder.textOption, concentrationBuilder.subjectConditionBuilder.textOption,
      concentrationBuilder.patientInformationBuilder.textOption, concentrationBuilder.commentBuilder.textOption)
    for (referenceBuilder <- concentrationBuilder.referencesBuilder) {
      for (referenceTextBuilder <- referenceBuilder("reference_text"); referenceText <- referenceTextBuilder.textOption) {
        val referenceId = DB.getReference(referenceText, referenceBuilder("pubmed_id"))
        DB.insertConcentrationReference(concentrationId, referenceId)
      }
    }
  }

  // disease

  def insertDisease(metaboliteId: Long) {
    for (diseaseBuilder <- diseasesBuilder) {
      for (diseaseName <- diseaseBuilder.nameBuilder.textOption) {
        val diseaseId = DB.getDisease(diseaseName, diseaseBuilder.omimBuilder.textOption.map(_.toInt))
        DB.insertDisease(metaboliteId, diseaseId)
        for (referenceBuilder <- diseaseBuilder.referencesBuilder) {
          for (referenceTextBuilder <- referenceBuilder("reference_text"); referenceText <- referenceTextBuilder.textOption) {
            val referenceId = DB.getReference(referenceText, referenceBuilder("pubmed_id"))
            DB.insertDiseaseReference(metaboliteId, diseaseId, referenceId)
          }
        }
      }
    }
  }

  // references

  type ReferenceBuilder = MetaboliteBuilder.ReferenceBuilder

  def insertReferences(metaboliteId: Long) {
    for (synthesisReference <- synthesisReferenceBuilder.textOption) {
      DB.insertReference(metaboliteId, Some(synthesisReference), None, synthesisReferenceBuilder.tag)
    }
    for (referenceBuider <- referencesBuilder) {
      DB.insertReference(metaboliteId, referenceBuider("reference_text"), referenceBuider("pubmed_id"), referencesBuilder.tag)
    }
  }

  // protein

  type ProteinBuilder = HomogenParentBuilder[TextValueBuilder]

  def proteinBuilder(tag: String): ReferenceBuilder = {
    HomogenParentBuilder[TextValueBuilder](tag)("protein_accession", "name", "uniprot_id", "gene_name", "protein_type")
  }

  def insertProtein(metaboliteId: Long) {
    for (proteinBuilder <- proteinsBuilder) {
      val proteinAccession = proteinBuilder("protein_accession").get.text
      val proteinName = proteinBuilder("name").get.text
      val uniprotId = proteinBuilder("uniprot_id").get.text
      val geneName = proteinBuilder("gene_name").get.text
      val proteinId = DB.getProtein(proteinAccession, proteinName, uniprotId, geneName, proteinBuilder("protein_type"))
      DB.insertProtein(metaboliteId, proteinId)
    }
  }

  implicit def textBuilderToText(builder: Option[TextValueBuilder]): Option[String] = builder.flatMap(_.textOption)
}

object MetaboliteBuilder {

  type ReferenceBuilder = HomogenParentBuilder[TextValueBuilder]

  implicit def reference(tag: String): ReferenceBuilder = {
    HomogenParentBuilder[TextValueBuilder](tag)("reference_text", "pubmed_id")
  }

}
