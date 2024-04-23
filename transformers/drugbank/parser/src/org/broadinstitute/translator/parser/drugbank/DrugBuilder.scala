package org.broadinstitute.translator.parser.drugbank

import scala.language.reflectiveCalls
import scala.language.implicitConversions

import org.broadinstitute.translator.xml._

class DrugBuilder(val drugType: String) extends ParentBuilder {

  val tag = "drug"

  val idBuilder = new TextValueBuilder("drugbank-id")
  val nameBuilder = new TextValueBuilder("name") =>: children
  val casNumberBuilder = new TextValueBuilder("cas-number") =>: children
  val uniiBuilder = new TextValueBuilder("unii") =>: children
  val groupsBuilder = new SequenceBuilder[TextValueBuilder]("groups","group") =>: children
  val referencesBuilder = new ReferencesBuilder("general-references") =>: children
  val classificationBuilder = new ClassificationBuilder("classification") =>: children
  val saltsBuilder = new SequenceBuilder[SaltBuilder]("salts", "salt")(saltBuilder) =>: children
  val synonymsBuilder = new SequenceBuilder[SynonymBuilder]("synonyms", "synonym") =>: children
  val productsBuilder = new SequenceBuilder[ProductBuilder]("products", "product")(product) =>: children
  val internationalBrandsBuilder = new SequenceBuilder[InternationalBrand]("international-brands", "international-brand")(internationalBrand) =>: children
  val categoriesBuilder = new SequenceBuilder[CategoryBuilder]("categories", "category") =>: children
  val organismsBuilder = new SequenceBuilder[TextValueBuilder]("affected-organisms", "affected-organism") =>: children
  val atcCodesBuilder = new ATCcodeBuilder("atc-codes") =>: children
  val pdbEntriesBuilder = new SequenceBuilder[TextValueBuilder]("pdb-entries","pdb-entry") =>: children
  val patentsBuilder = new SequenceBuilder[PatentBuilder]("patents","patent") =>: children
  val foodInteractionsBuilder = new SequenceBuilder[TextValueBuilder]("food-interactions", "food-interaction") =>: children
  val drugInteractionsBuilder = new SequenceBuilder[DrugInteraction]("drug-interactions", "drug-interaction")(drugInteraction) =>: children
  val calcPropertiesBuilder = new SequenceBuilder[PropertyBuilder]("calculated-properties","property") =>: children
  val expPropertiesBuilder = new SequenceBuilder[PropertyBuilder]("experimental-properties","property") =>: children
  val idsBuilder = new SequenceBuilder[IdentifierBuilder]("external-identifiers", "external-identifier") =>: children
  val linksBuilder = new SequenceBuilder[ExternalLink]("external-links", "external-link")(externalLink) =>: children
  val pathwaysBuilder = new SequenceBuilder[PathwayBuilder]("pathways","pathway") =>: children
  val reactionsBuilder = new SequenceBuilder[ReactionBuilder]("reactions","reaction") =>: children
  val snpEffectBuilder = new SequenceBuilder[SnpEffect]("snp-effects", "effect")(snpEffect) =>: children
  val snpReactionBuilder = new SequenceBuilder[SnpEffect]("snp-adverse-drug-reactions", "reaction")(snpEffect) =>: children
  val targetsBuilder = new SequenceBuilder[TargetBuilder]("targets","target")  =>: children
  val enzymesBuilder = new SequenceBuilder[TargetBuilder]("enzymes","enzyme")  =>: children
  val carriersBuilder = new SequenceBuilder[TargetBuilder]("carriers","carrier")  =>: children
  val transportersBuilder = new SequenceBuilder[TargetBuilder]("transporters","transporter")  =>: children

  val propertiesBuilders = {
    val propertyTags = Array(
      "description",
      "average-mass",
      "monoisotopic-mass",
      "state",
      "synthesis-reference",
      "indication",
      "pharmacodynamics",
      "mechanism-of-action",
      "toxicity",
      "metabolism",
      "absorption",
      "half-life",
      "protein-binding",
      "route-of-elimination",
      "volume-of-distribution",
      "clearance",
      "fda-label",
      "msds")
    propertyTags.map { tag =>
      new TextValueBuilder(tag) =>: children
    }
  }
    
  override def createBuilder(tag: String, attr: Map[String, String]): Option[Builder] = tag match {
    case "drugbank-id" if attr.get("primary") == Some("true") => Some(idBuilder)
    case other => super.createBuilder(tag, attr)
  }

  override def close() {
    println(idBuilder.text + ": " + nameBuilder.text)
    val drugId = DB.insertDrug(idBuilder.text, drugType, nameBuilder.text)
    insertIdentifiers(drugId)
    insertSynonyms(drugId)
    insertConnections(drugId)
    insertReferences(drugId)
    insertProperties(drugId)
    insertCategories(drugId)
    insertSalts(drugId)
    insertPatents(drugId)
    insertInteractions(drugId)
    insertPathways(drugId)
    insertReactions(drugId)
    insertSnpEffects(drugId)
    insertProducts(drugId)
  }

  def insertIdentifiers(drugId: Int) {
    for (casNumber <- casNumberBuilder.textOption) {
      DB.insertDrugIdentifier(drugId, casNumberBuilder.tag, "CAS", casNumber)
    }
    for (unii <- uniiBuilder.textOption) {
      DB.insertDrugIdentifier(drugId, uniiBuilder.tag, "UNII", unii)
    }
    for (id <- idsBuilder) 
      for (resource <- id.resourceBuilder.textOption)
        for (identifier <- id.identifierBuilder.textOption) {
      DB.insertDrugIdentifier(drugId, id.tag, resource, identifier)
    }
    for (property <- calcPropertiesBuilder) {
      if (property.nameBuilder.text == "SMILES" || property.nameBuilder.text == "InChI" || property.nameBuilder.text == "InChIKey") {
        DB.insertDrugIdentifier(drugId, calcPropertiesBuilder.tag, property.nameBuilder.text, property.valueBuilder.text)
      }
    }
  }

  type SynonymBuilder = TextValueBuilder with Attributes

  def insertSynonyms(drugId: Int) {
    for (synonym <- synonymsBuilder) {
      DB.insertSynonym(drugId, synonym.text, synonym.attr.get("language"), synonym.attr.get("coder"))
    }
    for (internationalBrandBuilder <- internationalBrandsBuilder) {
      for (brandNameBuilder <- internationalBrandBuilder("name")) {
        for (brandName <- brandNameBuilder.textOption) {
          DB.insertSynonym(drugId, brandName, None, Some(internationalBrandBuilder.tag))
        }
      }
    }
  }

  type ProductBuilder = HomogenParentBuilder[TextValueBuilder]

  def product(tag: String): ProductBuilder = {
    HomogenParentBuilder[TextValueBuilder](tag)(
      "name",
      "labeller",
      "ndc-id",
      "ndc-product-code",
      "dpd-id",
      "ema-product-code",
      "ema-ma-number",
      "started-marketing-on",
      "ended-marketing-on",
      "dosage-form",
      "strength",
      "route",
      "fda-application-number",
      "generic",
      "over-the-counter",
      "approved",
      "country",
      "source")
  }

  def insertProducts(drugId: Int) {
    for (productBuilder <- productsBuilder) {
      insertProduct(drugId, DB.nextProductId(), productBuilder)
    }
  }

  def insertProduct(drugId: Int, productId: Int, productBuilder: ProductBuilder) {
    for (propertyBuilder <- productBuilder) {
      for (value <- propertyBuilder.textOption) {
        val propertyId = DB.getProductProperty(propertyBuilder.tag, value) match {
          case Some(propertyId) => propertyId
          case None => DB.insertProductProperty(propertyBuilder.tag, value)
        }
        DB.insertProductMapRow(drugId, productId, propertyId)
      }
    }
  }

  type InternationalBrand = HomogenParentBuilder[TextValueBuilder]

  def internationalBrand(tag: String): InternationalBrand = {
    HomogenParentBuilder[TextValueBuilder](tag)("name", "company")
  }
  
  def insertConnections(drugId: Int) {
    for (builder <- targetsBuilder :: enzymesBuilder :: carriersBuilder :: transportersBuilder :: Nil)
      for (target <- builder) {
        insertConnection(drugId, target)
      }
  }

  def insertConnection(drugId: Int, target: TargetBuilder) {
    val targetId = TargetBuilder(target.targetIdBuilder.text).get
    val connectionId = DB.insertConnection(drugId, target.tag, targetId)
    if (target.actions.length > 0) {
      insertActions(connectionId, target.actions)
    }
    insertConnectionProperty(connectionId, target.inhibitionStrengthBuilder)
    insertConnectionProperty(connectionId, target.inductionStrengthBuilder)
    for (references <- target.referencesBuilder.references) {
      for (reference <- references) {
        insertConnectionReference(connectionId, reference)
      }
    }
  }

  def insertConnectionReference(drugId: Int, reference: ReferenceBuilder) {
    insertReference(drugId, reference, DB.insertConnectionReference)
  }


  def insertActions(connectionId: Int, actions: String) {
    val propertyId = DB.getPropertyId("actions", actions) match {
      case Some(id) => id
      case None => DB.insertProperty("actions", actions)
    }
    DB.insertConnectionProperty(connectionId, propertyId)
  }

  def insertConnectionProperty(connectionId: Int, builder: TextValueBuilder) {
    for (property <- builder.textOption) {
      val propertyId = DB.getPropertyId(builder.tag, property) match {
        case Some(id) => id
        case None => DB.insertProperty(builder.tag, property)
      }
      DB.insertConnectionProperty(connectionId, propertyId)
    }
  }

  def insertReferences(drugId: Int) {
    for (references <- referencesBuilder.references) {
      for (reference <- references) {
        insertDrugReference(drugId, reference)
      }
    }
  }

  def insertDrugReference(drugId: Int, reference: ReferenceBuilder) {
    insertReference(drugId, reference, DB.insertDrugReference)
  }

  private def insertReference(id: Int, reference: ReferenceBuilder, dbInsert: (Int, Int) => Unit) {
    for (refId <- reference.refIdBuilder.textOption) {
      val referenceId = DB.getReferenceId(refId) match {
        case Some(id) => id
        case None => DB.insertReference(reference.tag, refId, reference.entry1Builder.text, reference.entry2Builder.text)
      }
      dbInsert(id, referenceId)
    }
  }

  def insertProperties(drugId: Int) {
    for (group <- groupsBuilder){
      insertProperty(drugId, group)
    }
    for (organism <- organismsBuilder){
      insertProperty(drugId, organism)
    }
    for (entry <- pdbEntriesBuilder){
      insertProperty(drugId, entry)
    }
    for (property <- propertiesBuilders) {
      insertProperty(drugId, property)
    }
    for (property <- calcPropertiesBuilder) {
      insertProperty(drugId, calcPropertiesBuilder.tag, property)
    }
    for (property <- expPropertiesBuilder) {
      insertProperty(drugId, expPropertiesBuilder.tag, property)
    }
    for (link <- linksBuilder){
      insertProperty(drugId, link)
    }
  }

  def insertProperty(drugId: Int, propertyTag: String, property: PropertyBuilder) = {
    for (kind <- property.nameBuilder.textOption) {
      for (value <- property.valueBuilder.textOption) {
        val propertyId = DB.getPropertyId(propertyTag, Some(kind), value, property.sourceBuilder.textOption) match {
          case Some(id) => id
          case None => DB.insertProperty(propertyTag, Some(kind), value, property.sourceBuilder.textOption)
        }
        DB.insertDrugProperty(drugId, propertyId)
      }
    }
  }

  def insertProperty(drugId: Int, property: TextValueBuilder) = {
    for (value <- property.textOption) {
      val propertyId = DB.getPropertyId(property.tag, value) match {
        case Some(id) => id
        case None => DB.insertProperty(property.tag, value)
      }
      DB.insertDrugProperty(drugId, propertyId)
    }
  }

  type ExternalLink = HomogenParentBuilder[TextValueBuilder]
  
  def insertProperty(drugId: Int, link: ExternalLink) = {
    for (url <- link("url"); value <- url.textOption) {
      val propertyId = DB.getPropertyId(link.tag, None, value, link("resource")) match {
        case Some(id) => id
        case None => DB.insertProperty(link.tag, None, value, link("resource"))
      }
      DB.insertDrugProperty(drugId, propertyId)
    }
  }

  def externalLink(tag: String): DrugInteraction = {
    HomogenParentBuilder[TextValueBuilder](tag)("resource", "url")
  }

  def insertCategories(drugId: Int) {
    for (builder <- classificationBuilder) {
      insertCategory(drugId, builder, Some("Classyfire"))
    }
    for (category <- categoriesBuilder) {
      insertCategory(drugId, category)
    }
    for (atcCode <- atcCodesBuilder.levels){
      insertAtcCode(drugId, atcCode)
      for (level <- atcCode.levels){
        insertCategory(drugId, level)
      }
    }
  }

  def insertCategory(drugId: Int, builder: TextValueBuilder, source: Option[String]) {
    for (category <- builder.textOption) {
      val category_id = DB.getCategory(builder.tag, category, None, source) match {
        case Some(category_id) => category_id
        case None => DB.insertCategory(builder.tag, category, None, source)
      }
      DB.insertCategoryMap(drugId, category_id)
    }
  }

  def insertCategory(drugId: Int, builder: CategoryBuilder) {
    for (category <- builder.categoryBuilder.textOption) {
      val category_id = DB.getCategory(builder.tag, category, builder.meshId, None) match {
        case Some(category_id) => category_id
        case None => DB.insertCategory(builder.tag, category, builder.meshId, None)
      }
      DB.insertCategoryMap(drugId, category_id)
    }
  }
  
  def insertCategory(drugId: Int, builder: ATCcodeBuilder) {
    val code = builder.code.map("ATC:" + _)
    for (level <- builder.textOption) {
      val category_id = DB.getCategory(builder.tag, level, code, Some("ATC")) match {
        case Some(category_id) => category_id
        case None => DB.insertCategory(builder.tag, level, code, Some("ATC"))
      }
      DB.insertCategoryMap(drugId, category_id)
    }
  }

  def insertAtcCode(drugId: Int, builder: ATCcodeBuilder) {
    for (code <- builder.code) {
      val category_id = DB.getCategory(builder.tag, code, Some("ATC:" + code), Some("ATC")) match {
        case Some(category_id) => category_id
        case None => DB.insertCategory(builder.tag, code, Some("ATC:" + code), Some("ATC"))
      }
      DB.insertCategoryMap(drugId, category_id)
    }
  }

  type SaltBuilder = HomogenParentBuilder[TextValueBuilder with Attributes]

  def saltBuilder(tag: String): SaltBuilder = {
    HomogenParentBuilder[TextValueBuilder with Attributes](tag)(
      "drugbank-id",
      "name",
      "unii",
      "cas-number",
      "inchikey",
      "average-mass",
      "monoisotopic-mass")
  }

  implicit def textAttrBuilder(tag: String): TextValueBuilder with Attributes = new TextValueBuilder(tag) with Attributes

  def insertSalts(drugId: Int) {
    for (builder <- saltsBuilder) {
      insertSalt(drugId, builder)
    }
  }

  def insertSalt(drugId: Int, builder: SaltBuilder) {
    for (saltDrugBankId <- builder("drugbank-id") if saltDrugBankId.attr.get("primary") == Some("true")) {
      for (name <- builder("name")) {
        val aveMass: Option[Double] = builder("average-mass").flatMap(_.textOption).map(_.toDouble)
        val monoMass: Option[Double] = builder("monoisotopic-mass").flatMap(_.textOption).map(_.toDouble)
        DB.insertSalt(drugId, saltDrugBankId.text, name.text, builder("unii"), builder("cas-number"), builder("inchikey"), aveMass, monoMass)
      }
    }
  }

  def insertPatents(drugId: Int) {
    for (builder <- patentsBuilder) {
      insertPatent(drugId, builder)
    }
  }

  def insertPatent(drugId: Int, patent: PatentBuilder) {
    val patentNumber = patent.numberBuilder.text
    val country = patent.countryBuilder.text
    val patent_id = DB.getPatent(patentNumber, country) match {
      case Some(category_id) => category_id
      case None => DB.insertPatent(patentNumber, country, patent.approvedBuilder.textOption, patent.expiresBuilder.textOption, patent.pediatricBuilder.text == "true")
    }
    DB.insertPatentMap(drugId, patent_id)
  }

  type DrugInteraction = HomogenParentBuilder[TextValueBuilder]

  def insertInteractions(drugId: Int) {
    for (builder <- foodInteractionsBuilder) {
      insertFoodInteraction(drugId, builder)
    }
    for (builder <- drugInteractionsBuilder) {
      insertDrugInteraction(drugId, builder)
    }
  }

  def insertFoodInteraction(drugId: Int, builder: TextValueBuilder) {
    DB.insertInteraction(drugId, builder.tag, None, builder.textOption)
  }

  def insertDrugInteraction(drugId: Int, builder: DrugInteraction) {
    DB.insertInteraction(drugId, builder.tag, builder("drugbank-id"), builder("description"))
  }

  implicit def drugInteraction(tag: String): DrugInteraction = {
    HomogenParentBuilder[TextValueBuilder](tag)("drugbank-id", "name", "description")
  }

  def insertPathways(drugId: Int) {
    for (builder <- pathwaysBuilder) {
      for (smpdbId <- builder.smpdbIdBuilder.textOption) {
        val pathwayId = PathwayBuilder.pathwayId(smpdbId)
        DB.insertPathwayMap(drugId, pathwayId)
      }
    }
  }

  def insertReactions(drugId: Int) {
    for (builder <- reactionsBuilder) {
      val reactionId = DB.insertReaction(drugId, builder.sequenceBuilder.textOption)
      insertReactionElement(reactionId, builder.leftElementBuilder)
      insertReactionElement(reactionId, builder.rightElementBuilder)
      for (enzymeBuilder <- builder.enzymesBuilder) {
        insertReactionElement(reactionId, enzymeBuilder)
      }
    }
  }

  def insertReactionElement(reactionId: Int, builder: HomogenParentBuilder[TextValueBuilder]) {
    for (drugbankId <- builder("drugbank-id").get.textOption)
      for (elementName <- builder("name").get.textOption) {
        val uniprotId = builder("uniprot-id")
        val reactionElementId = DB.getReactionElement(drugbankId, elementName, uniprotId) match {
          case Some(id) => id
          case None => DB.insertReactionElement(drugbankId, elementName, uniprotId)
        }
        DB.insertReactionMapRow(builder.tag, reactionId, reactionElementId)
      }
  }

  type SnpEffect = HomogenParentBuilder[TextValueBuilder]

  implicit def snpEffect(tag: String): SnpEffect = {
    HomogenParentBuilder[TextValueBuilder](tag)(
      "protein-name",
      "gene-symbol",
      "uniprot-id",
      "rs-id",
      "allele",
      "defining-change",
      "adverse-reaction",
      "description",
      "pubmed-id")
  }

  def insertSnpEffects(drugId: Int) {
    for (builder <- snpEffectBuilder) {
      insertSnpEffect(drugId, builder)
    }
    for (builder <- snpReactionBuilder) {
      insertSnpEffect(drugId, builder)
    }
  }

  def insertSnpEffect(drugId: Int, builder: SnpEffect) {
    for (proteinName <- builder("protein-name").get.textOption) {
      DB.insertSnpEffect(drugId, builder.tag, proteinName, builder("gene-symbol"), builder("uniprot-id"),
        builder("rs-id"), builder("allele"), builder("defining-change"), builder("adverse-reaction"),
        builder("description"), builder("pubmed-id"))
    }
  }
  
  implicit def textBuilderToText(builder: Option[TextValueBuilder]): Option[String] = builder match {
    case Some(builder) => builder.textOption
    case None => None
  }
}
