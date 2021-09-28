package org.broadinstitute.translator.parser.drugbank

import java.sql.DriverManager;
import java.sql.Connection
import java.sql.Statement

object DB {

  // Table names
  private val LANGUAGE = "LANGUAGE"
  private val CODER = "CODER"
  private val DRUG = "DRUG"
  private val TAG = "TAG"
  private val RESOURCE = "RESOURCE"
  private val PROPERTY = "PROPERTY"
  private val CATEGORY = "CATEGORY"
  private val PATENT = "PATENT"
  private val COUNTRY = "COUNTRY"
  private val PATHWAY = "PATHWAY" 
  private val POLYPEPTIDE = "POLYPEPTIDE" 
  private val CONNECTION = "CONNECTION" 
  
  
  private var connection: Connection = null

  private var lastDrugId = 0
  private var lastSynonymId = 0
  private var lastTargetId = 0
  private var lastMapId = 0
  private var lastReferenceId = 0
  private var lastPropertyId = 0
  private var lastCategoryId = 0
  private var lastPatentId = 0
  private var lastPathwayId = 0
  private var lastReactionId = 0
  private var lastReactionElementId = 0
  private var lastPolypeptideId = 0
  private var lastPfamId = 0
  private var lastProductPropertyId = 0
  private var lastProductId = 0
  
  private val articleRefTypeId = 1
  private val textbookRefTypeId = 2
  private val linkRefTypeId = 3
  private val attachmentRefTypeId = 4
  
  def createDB(database: String) {
    Class.forName("org.sqlite.JDBC")
    connection = DriverManager.getConnection("jdbc:sqlite:" + database)
    connection.setAutoCommit(false)
    createDrugTable()
    createDictTable(LANGUAGE, LANGUAGE)
    createDictTable(CODER, CODER)
    createSynonymTable()
    createDictTable(TAG, TAG)
    createDrugIdentifierTable()
    createTargetTable()
    createConnectionTable()
    createPolypeptideTable()
    createPolypeptideIdentifierTable()
    createReferenceTypeTable()
    createReferenceTable()
    createDrugReferenceTable()
    createConnectionReferenceTable()
    createPropertyTable()
    createPropertyMapTable(DRUG)
    createPropertyMapTable(POLYPEPTIDE)
    createPropertyMapTable(CONNECTION)
    createDictTable(RESOURCE, RESOURCE)
    createCategoryTable()
    createMapTable(CATEGORY+"_MAP",CATEGORY)
    createSaltTable()
    createPatentTable()
    createDictTable(COUNTRY, COUNTRY)
    createMapTable(PATENT+"_MAP",PATENT)
    createInteractionsTable()
    createPathwayTable()
    createPathwayMemberTable()
    createReactionTable()
    createReactionElementTable()
    createReactionMapTable()
    createMapTable(PATHWAY+"_MAP",PATHWAY)
    createPfamTable()
    createPfamMapTable()
    createSnpEffectTable()
    createProductPropertyTable()
    createProductMapTable()
    createPreLoadIndexes()
    commit()
  }

  private def executeUpdate(sql: String) {
    val stm = connection.createStatement()
    stm.executeUpdate(sql)
    stm.close()
  }

  def createDrugTable() {
    val createTableSQL = """
      CREATE TABLE DRUG(
        DRUG_ID       INTEGER  PRIMARY KEY,
        DRUG_BANK_ID  TEXT  NOT NULL,
        DRUG_TYPE     TEXT  NOT NULL,
        DRUG_NAME          TEXT  NOT NULL
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertDrug(drugbankId: String, drugType: String, name: String): Int = {
    lastDrugId = lastDrugId + 1
    val drugId = lastDrugId

    val insertSQL = s"""
      INSERT INTO DRUG (DRUG_ID, DRUG_BANK_ID, DRUG_TYPE, DRUG_NAME)
      VALUES (${drugId}, ${f(drugbankId)}, ${f(drugType)}, ${f(name)})
      """
    executeUpdate(insertSQL)
    return drugId
  }

  def createSynonymTable() {
    val createTableSQL = """
      CREATE TABLE SYNONYM(
        SYNONYM_ID  INTEGER  PRIMARY KEY,
        DRUG_ID     INT   NOT NULL,
        LANGUAGE_ID INT,
        CODER_ID    INT,
        SYNONYM     TEXT  COLLATE NOCASE NOT NULL,
        FOREIGN KEY(DRUG_ID) REFERENCES DRUG(DRUG_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertSynonym(drugId: Int, synonym: String, language: Option[String], coder: Option[String]): Int = {
    lastSynonymId = lastSynonymId + 1
    val synonymId = lastSynonymId
    val languageId = getId(LANGUAGE, LANGUAGE, language)
    val coderId = getId(CODER, CODER, coder)
    val insertSQL = s"""
      INSERT INTO SYNONYM (SYNONYM_ID, DRUG_ID, LANGUAGE_ID, CODER_ID, SYNONYM)
      VALUES (${synonymId}, ${drugId}, ${fi(languageId)}, ${fi(coderId)}, ${f(synonym)})
      """
    executeUpdate(insertSQL)
    return synonymId
  }

  def createDrugIdentifierTable() {
    val createTableSQL = s"""
      CREATE TABLE DRUG_IDENTIFIER(
        IDENTIFIER_ID  INTEGER  PRIMARY KEY,
        DRUG_ID        INT   NOT NULL,
        TAG_ID         INT   NOT NULL,
        RESOURCE_ID    INT   NOT NULL,
        IDENTIFIER     TEXT  NOT NULL,
        FOREIGN KEY(DRUG_ID) REFERENCES DRUG(DRUG_ID),
        FOREIGN KEY(TAG_ID) REFERENCES TAG(TAG_ID),
        FOREIGN KEY(RESOURCE_ID) REFERENCES RESOURCE(RESOURCE_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertDrugIdentifier(drugId: Int, tag: String, resource: String, identifier: String) = {
    val resource_id = getId(RESOURCE, RESOURCE, resource)
    val tagId = getId(TAG, TAG, tag)
    val insertSQL = s"""
      INSERT INTO DRUG_IDENTIFIER (DRUG_ID, TAG_ID, RESOURCE_ID, IDENTIFIER)
      VALUES (${drugId}, ${tagId}, ${resource_id}, ${f(identifier)})
      """
    executeUpdate(insertSQL)
  }

  def createPolypeptideIdentifierTable() {
    val createTableSQL = s"""
      CREATE TABLE POLYPEPTIDE_IDENTIFIER(
        IDENTIFIER_ID   INTEGER  PRIMARY KEY,
        POLYPEPTIDE_ID  INT   NOT NULL,
        TAG_ID          INT   NOT NULL,
        RESOURCE_ID     INT   NOT NULL,
        IDENTIFIER      TEXT  NOT NULL,
        FOREIGN KEY(POLYPEPTIDE_ID) REFERENCES POLYPEPTIDE(POLYPEPTIDE_ID),
        FOREIGN KEY(TAG_ID) REFERENCES TAG(TAG_ID),
        FOREIGN KEY(RESOURCE_ID) REFERENCES RESOURCE(RESOURCE_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertPolypeptideIdentifier(polypeptideId: Int, tag: String, resource: String, identifier: String) = {
    val resource_id = getId(RESOURCE, RESOURCE, resource)
    val tagId = getId(TAG, TAG, tag)
    val insertSQL = s"""
      INSERT INTO POLYPEPTIDE_IDENTIFIER (POLYPEPTIDE_ID, TAG_ID, RESOURCE_ID, IDENTIFIER)
      VALUES (${polypeptideId}, ${tagId}, ${resource_id}, ${f(identifier)})
      """
    executeUpdate(insertSQL)
  }

  def createTargetTable() {
    val createTableSQL = """
      CREATE TABLE TARGET(
        TARGET_ID          INTEGER  PRIMARY KEY,
        TARGET_IDENTIFIER  TEXT  UNIQUE  NOT NULL,
        NAME               TEXT  NOT NULL,
        ORGANISM           TEXT,
        KNOWN_ACTION       TEXT
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertTarget(targetIdentifier: String, name: String, organism: Option[String], knownAction: Option[String]): Int = {
    lastTargetId = lastTargetId + 1
    val targetId = lastTargetId

    val insertSQL = s"""
      INSERT INTO TARGET (TARGET_ID, TARGET_IDENTIFIER, NAME, ORGANISM, KNOWN_ACTION)
      VALUES (${targetId}, ${f(targetIdentifier)}, ${f(name)}, ${f(organism)}, ${f(knownAction)})
      """
    executeUpdate(insertSQL)
    return targetId
  }

  def createConnectionTable() {
    val createTableSQL = """
      CREATE TABLE CONNECTION(
        CONNECTION_ID     INTEGER  PRIMARY KEY,
        DRUG_ID    INT NOT NULL,
        TAG_ID     INT   NOT NULL,
        TARGET_ID  INT NOT NULL,
        FOREIGN KEY(DRUG_ID) REFERENCES DRUG(DRUG_ID),
        FOREIGN KEY(TAG_ID) REFERENCES TAG(TAG_ID),
        FOREIGN KEY(TARGET_ID) REFERENCES TARGET(TARGET_ID)
      );
    """
    executeUpdate(createTableSQL)
  }
  
  def insertConnection(drugId: Int, tag: String, targetId: Int): Int = {
    lastMapId = lastMapId + 1
    val mapId = lastMapId
    val tagId = getId(TAG, TAG, tag)
    val insertSQL = s"""
      INSERT INTO CONNECTION (CONNECTION_ID, DRUG_ID, TAG_ID, TARGET_ID)
      VALUES (${mapId}, ${drugId}, ${tagId}, ${targetId})
      """
    executeUpdate(insertSQL)
    return mapId
  }

  def createPolypeptideTable(){
    val createTableSQL = """
      CREATE TABLE POLYPEPTIDE (
        POLYPEPTIDE_ID          INTEGER  PRIMARY KEY,
        TARGET_ID               INT   NOT NULL,
        POLYPEPTIDE_NAME        TEXT  NOT NULL,
        POLYPEPTIDE_IDENTIFIER  TEXT  NOT NULL,
        IDENTIFIER_SOURCE       TEXT  NOT NULL,
        FOREIGN KEY(TARGET_ID) REFERENCES TARGET(TARGET_ID)
      );
    """
    executeUpdate(createTableSQL)
  }


  def insertPolypeptide(targetId: Int, polypeptideName: String, polypeptideIdentifier: String, identifierSource: String): Int = {
    lastPolypeptideId = lastPolypeptideId + 1
    val polypeptideId = lastPolypeptideId
    val insertSQL = s"""
      INSERT INTO POLYPEPTIDE (POLYPEPTIDE_ID, TARGET_ID, POLYPEPTIDE_NAME, POLYPEPTIDE_IDENTIFIER, IDENTIFIER_SOURCE)
      VALUES (${polypeptideId}, ${targetId}, ${f(polypeptideName)}, ${f(polypeptideIdentifier)}, ${f(identifierSource)})
      """
    executeUpdate(insertSQL)
    return polypeptideId
  }
  
  def createReferenceTypeTable() {
    val createTableSQL = """
      CREATE TABLE REFERENCE_TYPE(
        REFERENCE_TYPE_ID  INTEGER  PRIMARY KEY,
        REFERENCE_TYPE     TEXT  UNIQUE  NOT NULL
      );
    """
    executeUpdate(createTableSQL)
    insertReferenceType(articleRefTypeId, "article")
    insertReferenceType(textbookRefTypeId, "textbook")
    insertReferenceType(linkRefTypeId, "link")
    insertReferenceType(attachmentRefTypeId, "attachment")
  }

  def insertReferenceType(refTypeId: Int, refType: String) {
    val insertSQL = s"""
      INSERT INTO REFERENCE_TYPE (REFERENCE_TYPE_ID, REFERENCE_TYPE)
      VALUES (${refTypeId}, ${f(refType)})
      """
    executeUpdate(insertSQL)
  }

  def createReferenceTable() {
    val createTableSQL = """
      CREATE TABLE REFERENCE(
        REFERENCE_ID       INTEGER  PRIMARY KEY,
        REFERENCE_TYPE_ID  INT   NOT NULL,
        REF_ID             TEXT  UNIQUE  NOT NULL,
        PUBMED_ID          TEXT,
        ISBN               TEXT,
        CITATION           TEXT,
        TITLE              TEXT,
        URL                TEXT,
        FOREIGN KEY(REFERENCE_TYPE_ID) REFERENCES REFERENCE_TYPE(REFERENCE_TYPE_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertReference(refType: String, refId: String, entry1: String, entry2: String):Int = {
    lastReferenceId = lastReferenceId + 1
    val referenceId = lastReferenceId
    refType match {
      case "article" => insertArticle(referenceId, refId, entry1, entry2)
      case "textbook" => insertTextbook(referenceId ,refId, entry1, entry2)
      case "link" => insertLink(referenceId, refId, entry1, entry2)
      case "attachment" => insertAttachment(referenceId, refId, entry1, entry2)
    }
    return referenceId
  }

  def insertArticle(referenceId: Int, refId: String, pubmedId: String, citation: String) {
    val insertSQL = s"""
      INSERT INTO REFERENCE (REFERENCE_ID, REFERENCE_TYPE_ID, REF_ID, PUBMED_ID, CITATION)
      VALUES (${referenceId}, ${articleRefTypeId}, ${f(refId)}, ${f(pubmedId)}, ${f(citation)})
      """
    executeUpdate(insertSQL)
  }

  def insertTextbook(referenceId: Int, refId: String, isbn: String, citation: String) {
    val insertSQL = s"""
      INSERT INTO REFERENCE (REFERENCE_ID, REFERENCE_TYPE_ID, REF_ID, ISBN, CITATION)
      VALUES (${referenceId}, ${textbookRefTypeId}, ${f(refId)}, ${f(isbn)}, ${f(citation)})
      """
    executeUpdate(insertSQL)
  }

  def insertLink(referenceId: Int, refId: String, title: String, url: String) {
    val insertSQL = s"""
      INSERT INTO REFERENCE (REFERENCE_ID, REFERENCE_TYPE_ID, REF_ID, TITLE, URL)
      VALUES (${referenceId}, ${linkRefTypeId}, ${f(refId)}, ${f(title)}, ${f(url)})
      """
    executeUpdate(insertSQL)
  }

  def insertAttachment(referenceId: Int, refId: String, title: String, url: String) {
    val insertSQL = s"""
      INSERT INTO REFERENCE (REFERENCE_ID, REFERENCE_TYPE_ID, REF_ID, TITLE, URL)
      VALUES (${referenceId}, ${attachmentRefTypeId}, ${f(refId)}, ${f(title)}, ${f(url)})
      """
    executeUpdate(insertSQL)
  }

  def getReferenceId(refId: String): Option[Int] = {
    val query = s"""
        SELECT REFERENCE_ID FROM REFERENCE
        WHERE REF_ID = ${f(refId)}
      """
    var referenceId: Option[Int] = None
    val stm = connection.createStatement()
    val resultSet = stm.executeQuery(query)
    if (resultSet.next()) {
      referenceId = Some(resultSet.getInt("REFERENCE_ID"))
    }
    stm.close()
    return referenceId
  }
  
  def createDrugReferenceTable() {
    val createTableSQL = """
      CREATE TABLE DRUG_REFERENCE(
        DRUG_REFERENCE_ID  INTEGER  PRIMARY KEY,
        DRUG_ID            INT  NOT NULL,
        REFERENCE_ID       INT  NOT NULL,
        FOREIGN KEY(DRUG_ID) REFERENCES DRUG(DRUG_ID),
        FOREIGN KEY(REFERENCE_ID) REFERENCES REFERENCE(REFERENCE_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertDrugReference(drugId: Int, referenceId: Int) {
    val insertSQL = s"""
      INSERT INTO DRUG_REFERENCE (DRUG_ID, REFERENCE_ID)
      VALUES (${drugId}, ${referenceId})
      """
    executeUpdate(insertSQL)
  }

  def createConnectionReferenceTable() {
    val createTableSQL = """
      CREATE TABLE CONNECTION_REFERENCE(
        CONNECTION_REFERENCE_ID  INTEGER  PRIMARY KEY,
        CONNECTION_ID            INT  NOT NULL,
        REFERENCE_ID       INT  NOT NULL,
        FOREIGN KEY(CONNECTION_ID) REFERENCES CONNECTION(CONNECTION_ID),
        FOREIGN KEY(REFERENCE_ID) REFERENCES REFERENCE(REFERENCE_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertConnectionReference(connectionId: Int, referenceId: Int) {
    val insertSQL = s"""
      INSERT INTO CONNECTION_REFERENCE (CONNECTION_ID, REFERENCE_ID)
      VALUES (${connectionId}, ${referenceId})
      """
    executeUpdate(insertSQL)
  }

  def createPropertyTable() {
    val createTableSQL = """
      CREATE TABLE PROPERTY (
        PROPERTY_ID  INTEGER  PRIMARY KEY,
        TAG_ID       INT   NOT NULL,
        KIND         TEXT,
        VALUE        TEXT  NOT NULL,
        SOURCE       TEXT,
        FOREIGN KEY(TAG_ID) REFERENCES TAG(TAG_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def getPropertyId(tag: String, kind: Option[String], value: String, source: Option[String]): Option[Int] = {
    val tagId = getId(TAG, TAG, tag)
    val query = s"""
        SELECT PROPERTY_ID FROM PROPERTY
        WHERE TAG_ID = ${tagId} AND KIND ${is(kind)} AND VALUE = ${f(value)} AND SOURCE ${is(source)}
      """
    return findId(query, "PROPERTY_ID")
  }

  def insertProperty(tag: String, kind: Option[String], value: String, source: Option[String]): Int = {
    lastPropertyId = lastPropertyId + 1
    val propertyId = lastPropertyId
    val tagId = getId(TAG, TAG, tag)
    val insertSQL = s"""
      INSERT INTO PROPERTY (PROPERTY_ID, TAG_ID, KIND, VALUE, SOURCE)
      VALUES (${propertyId}, ${tagId}, ${f(kind)}, ${f(value)}, ${f(source)})
      """
    executeUpdate(insertSQL)
    return propertyId
  }

  def getPropertyId(tag: String, value: String): Option[Int] = getPropertyId(tag, None, value, None)

  def insertProperty(tag: String, value: String): Int = insertProperty(tag, None, value, None)

  def createPropertyMapTable(parentTableName: String) {
    val createTableSQL = s"""
      CREATE TABLE ${parentTableName}_PROPERTY (
        ${parentTableName}_PROPERTY_ID  INTEGER  PRIMARY KEY,
        ${parentTableName}_ID      INT  NOT NULL,
        PROPERTY_ID          INT  NOT NULL,
        FOREIGN KEY(${parentTableName}_ID) REFERENCES ${parentTableName}(${parentTableName}_ID),
        FOREIGN KEY(PROPERTY_ID) REFERENCES PROPERTY(PROPERTY_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertDrugProperty(drugId: Int, propertyId: Int) {
    insertPropertyMapRow(DRUG, drugId, propertyId)
  }

  def insertPolypeptideProperty(polypeptideId: Int, propertyId: Int) {
    insertPropertyMapRow(POLYPEPTIDE, polypeptideId, propertyId)
  }

  def insertConnectionProperty(connectionId: Int, propertyId: Int) {
    insertPropertyMapRow(CONNECTION, connectionId, propertyId)
  }

  def insertPropertyMapRow(parentTableName: String, parentId: Int, propertyId: Int) {
    val insertSQL = s"""
      INSERT INTO ${parentTableName}_PROPERTY (${parentTableName}_ID, PROPERTY_ID)
      VALUES (${parentId}, ${propertyId})
      """
    executeUpdate(insertSQL)
  }


  def createCategoryTable() {
    val createTableSQL = """
      CREATE TABLE CATEGORY (
        CATEGORY_ID    INTEGER  PRIMARY KEY,
        TAG_ID         INT  NOT NULL,
        CATEGORY       TEXT  NOT NULL,
        CATEGORY_XREF  TEXT,
        SOURCE         TEXT,
        FOREIGN KEY(TAG_ID) REFERENCES TAG(TAG_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertCategory(tag: String, category: String, xref: Option[String], source: Option[String]): Int = {
    lastCategoryId = lastCategoryId + 1
    val categoryId = lastCategoryId
    val tagId = getId(TAG, TAG, tag)
    val insertSQL = s"""
      INSERT INTO CATEGORY (CATEGORY_ID, TAG_ID, CATEGORY, CATEGORY_XREF, SOURCE)
      VALUES (${categoryId}, ${tagId}, ${f(category)}, ${f(xref)}, ${f(source)})
      """
    executeUpdate(insertSQL)
    return categoryId
  }

  def getCategory(tag: String, category: String, xref: Option[String], source: Option[String]): Option[Int] = {
    val tagId = getId(TAG, TAG, tag)
    val query = s"""
        SELECT CATEGORY_ID FROM CATEGORY
        WHERE TAG_ID = ${tagId} AND CATEGORY = ${f(category)} AND CATEGORY_XREF ${is(xref)} AND SOURCE ${is(source)}
      """
    return findId(query, "CATEGORY_ID")
  }

  def insertCategoryMap(drugId: Int, category_id: Int) {
    insertMapRow(CATEGORY + "_MAP", CATEGORY, drugId, category_id)
  }

  def createSaltTable() {
    val createTableSQL = """
      CREATE TABLE SALT (
        SALT_ID           INTEGER  PRIMARY KEY,
        DRUG_ID           INT   NOT NULL,  
        SALT_DRUGBANK_ID  TEXT  NOT NULL,
        SALT_NAME         TEXT  NOT NULL,
        UNII              TEXT,
        CAS_NUMBER        TEXT,
        INCHIKEY          TEXT,
        AVERAGE_MASS      REAL,
        MONOISOTOPIC_MASS REAL,
        FOREIGN KEY(DRUG_ID) REFERENCES DRUG(DRUG_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertSalt(drugId: Int, saltDrugbankId: String, saltName: String, unii: Option[String], cas: Option[String], inchikey: Option[String], aveMass: Option[Double], monoMass: Option[Double]) {
    val insertSQL = s"""
      INSERT INTO SALT (DRUG_ID, SALT_DRUGBANK_ID, SALT_NAME, UNII, CAS_NUMBER, INCHIKEY, AVERAGE_MASS, MONOISOTOPIC_MASS)
      VALUES (${drugId}, ${f(saltDrugbankId)}, ${f(saltName)}, ${f(unii)}, ${f(cas)}, ${f(inchikey)}, ${fd(aveMass)}, ${fd(monoMass)})
      """
    executeUpdate(insertSQL)
  }

  def createPatentTable() {
    val createTableSQL = """
      CREATE TABLE PATENT (
        PATENT_ID      INTEGER  PRIMARY KEY,
        PATENT_NUMBER  TEXT  NOT NULL,
        COUNTRY_ID     INT   NOT NULL,
        APPROVED       TEXT,
        EXPIRES        TEXT,
        PEDIATRIC_EXT  INT
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertPatent(patentNumber: String, country: String, approved: Option[String], expires: Option[String], pediatricExt: Boolean): Int = {
    val countryId = getId(COUNTRY, COUNTRY, country)
    lastPatentId = lastPatentId + 1
    val patentId = lastPatentId
    val insertSQL = s"""
      INSERT INTO PATENT (PATENT_ID, PATENT_NUMBER, COUNTRY_ID, APPROVED, EXPIRES, PEDIATRIC_EXT)
      VALUES (${patentId}, ${f(patentNumber)}, ${countryId}, ${f(approved)}, ${f(expires)}, ${f(pediatricExt)})
      """
    executeUpdate(insertSQL)
    return patentId
  }

  def getPatent(patentNumber: String, country: String): Option[Int] = {
    val query = s"""
        SELECT PATENT.PATENT_ID FROM PATENT
        JOIN COUNTRY ON (COUNTRY.COUNTRY_ID = PATENT.COUNTRY_ID)
        WHERE PATENT.PATENT_NUMBER = ${f(patentNumber)} AND COUNTRY.COUNTRY = ${f(country)} 
    """
    return findId(query, "PATENT_ID")
  }

  def insertPatentMap(drugId: Int, category_id: Int) {
    insertMapRow(PATENT + "_MAP", PATENT, drugId, category_id)
  }

  def createInteractionsTable() {
    val createTableSQL = """
      CREATE TABLE INTERACTION (
        INTERACTION_ID    INTEGER  PRIMARY KEY,
        DRUG_ID           INT  NOT NULL,
        TAG_ID            INT  NOT NULL,
        INTERACTOR_ID     TEXT,
        INTERACTION_DESC  TEXT  NOT NULL,
        FOREIGN KEY(DRUG_ID) REFERENCES DRUG(DRUG_ID),
        FOREIGN KEY(TAG_ID) REFERENCES TAG(TAG_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertInteraction(drugId: Int, tag: String, interactorId: Option[String], description: Option[String]) {
    val tagId = getId(TAG, TAG, tag)
    val insertSQL = s"""
      INSERT INTO INTERACTION (DRUG_ID, TAG_ID, INTERACTOR_ID, INTERACTION_DESC)
      VALUES (${drugId}, ${tagId}, ${f(interactorId)}, ${f(description)})
      """
    executeUpdate(insertSQL)
  }

  def createPathwayTable() {
    val createTableSQL = """
      CREATE TABLE PATHWAY (
        PATHWAY_ID        INTEGER  PRIMARY KEY,
        PATHWAY_XREF      TEXT  UNIQUE  NOT NULL,
        PATHWAY_NAME      TEXT,
        PATHWAY_CATEGORY  TEXT
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertPathway(xref: String, name: String, category: Option[String]): Int = {
    lastPathwayId = lastPathwayId + 1
    val pathwayId = lastPathwayId
    val insertSQL = s"""
      INSERT INTO PATHWAY (PATHWAY_ID, PATHWAY_XREF, PATHWAY_NAME, PATHWAY_CATEGORY)
      VALUES (${pathwayId}, ${f(xref)}, ${f(name)}, ${f(category)})
      """
    executeUpdate(insertSQL)
    return pathwayId
  }

  def createPathwayMemberTable() {
    val createTableSQL = """
      CREATE TABLE PATHWAY_MEMBER (
        PATHWAY_MEMBER_ID    INTEGER  PRIMARY KEY,
        PATHWAY_ID           INT   NOT NULL,
        PATHWAY_MEMBER_TYPE  TEXT  NOT NULL,
        PATHWAY_MEMBER_XREF  TEXT  NOT NULL,
        PATHWAY_MEMBER_NAME  TEXT,
        FOREIGN KEY(PATHWAY_ID) REFERENCES PATHWAY(PATHWAY_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertPathwayMember(pathwayId: Int, pathwayType: String, xref: String, name: Option[String]) = {
    val insertSQL = s"""
      INSERT INTO PATHWAY_MEMBER (PATHWAY_ID, PATHWAY_MEMBER_TYPE, PATHWAY_MEMBER_XREF, PATHWAY_MEMBER_NAME)
      VALUES (${pathwayId}, ${f(pathwayType)}, ${f(xref)}, ${f(name)})
      """
    executeUpdate(insertSQL)
  }

  def insertPathwayMap(drugId: Int, pathwayId: Int) {
    insertMapRow(PATHWAY + "_MAP", PATHWAY, drugId, pathwayId)
  }

  def createReactionTable() {
    val createTableSQL = """
      CREATE TABLE REACTION (
        REACTION_ID  INTEGER  PRIMARY KEY,
        DRUG_ID      INT  NOT NULL,
        SEQUENCE     TEXT,
        FOREIGN KEY(DRUG_ID) REFERENCES DRUG(DRUG_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertReaction(drugId: Int, sequence: Option[String]): Int = {
    lastReactionId = lastReactionId + 1
    val reactionId = lastReactionId
    val insertSQL = s"""
      INSERT INTO REACTION (REACTION_ID, DRUG_ID, SEQUENCE)
      VALUES (${reactionId}, ${drugId}, ${f(sequence)})
      """
    executeUpdate(insertSQL)
    return reactionId
  }

  def createReactionElementTable() {
    val createTableSQL = """
      CREATE TABLE REACTION_ELEMENT (
        REACTION_ELEMENT_ID  INTEGER  PRIMARY KEY,
        ELEMENT_DRUGBANK_ID  TEXT  NOT NULL,
        ELEMENT_NAME         TEXT  NOT NULL,
        UNIPROT_ID           TEXT
      );
    """
    executeUpdate(createTableSQL)
  }

  def getReactionElement(drugbankId: String, elementName: String, uniprotId: Option[String]): Option[Int] = {
    val query = s"""
        SELECT REACTION_ELEMENT_ID FROM REACTION_ELEMENT
        WHERE ELEMENT_DRUGBANK_ID = ${f(drugbankId)} AND ELEMENT_NAME = ${f(elementName)} AND UNIPROT_ID ${is(uniprotId)} 
    """
    return findId(query, "REACTION_ELEMENT_ID")
  }

  def insertReactionElement(drugbankId: String, elementName: String, uniprotId: Option[String]): Int = {
    lastReactionElementId = lastReactionElementId + 1
    val reactionElementId = lastReactionElementId
    val insertSQL = s"""
      INSERT INTO REACTION_ELEMENT (REACTION_ELEMENT_ID, ELEMENT_DRUGBANK_ID, ELEMENT_NAME, UNIPROT_ID)
      VALUES (${reactionElementId}, ${f(drugbankId)}, ${f(elementName)}, ${f(uniprotId)})
      """
    executeUpdate(insertSQL)
    return reactionElementId
  }

  def createReactionMapTable() {
    val createTableSQL = """
      CREATE TABLE REACTION_MAP (
        REACTION_MAP_ID      INTEGER  PRIMARY KEY,
        TAG_ID               INT  NOT NULL,
        REACTION_ID          INT  NOT NULL,
        REACTION_ELEMENT_ID  INT  NOT NULL,
        FOREIGN KEY(TAG_ID) REFERENCES TAG(TAG_ID),
        FOREIGN KEY(REACTION_ID) REFERENCES REACTION(REACTION_ID),
        FOREIGN KEY(REACTION_ELEMENT_ID) REFERENCES REACTION_ELEMENT(REACTION_ELEMENT_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertReactionMapRow(tag: String, reactionId: Int, reactionElementId: Int) {
    val tagId = getId(TAG, TAG, tag)
    val insertSQL = s"""
      INSERT INTO REACTION_MAP (TAG_ID, REACTION_ID, REACTION_ELEMENT_ID)
      VALUES (${tagId}, ${reactionId}, ${reactionElementId})
      """
    executeUpdate(insertSQL)
  }

  def createPfamTable() {
    val createTableSQL = """
      CREATE TABLE PFAM (
        PFAM_ID          INTEGER  PRIMARY KEY,
        PFAM_IDENTIFIER  TEXT   NOT NULL,
        PFAM_NAME        TEXT  NOT NULL
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertPfam(identifier: String, name: String): Int = {
    lastPfamId = lastPfamId + 1
    val pfamId = lastPfamId
    val insertSQL = s"""
      INSERT INTO PFAM (PFAM_ID, PFAM_IDENTIFIER, PFAM_NAME)
      VALUES (${pfamId}, ${f(identifier)}, ${f(name)})
      """
    executeUpdate(insertSQL)
    return pfamId
  }

  def getPfam(identifier: String, name: String): Option[Int] = {
    val query = s"""
        SELECT PFAM_ID FROM PFAM
        WHERE PFAM_IDENTIFIER = ${f(identifier)} AND PFAM_NAME = ${f(name)} 
    """
    return findId(query, "PFAM_ID")
  }

  def createPfamMapTable() {
    val createTableSQL = """
      CREATE TABLE PFAM_MAP (
        PFAM_MAP_ID     INTEGER  PRIMARY KEY,
        POLYPEPTIDE_ID  INT  NOT NULL,
        PFAM_ID         INT  NOT NULL,
        FOREIGN KEY(POLYPEPTIDE_ID) REFERENCES POLYPEPTIDE(POLYPEPTIDE_ID),
        FOREIGN KEY(PFAM_ID) REFERENCES PFAM(PFAM_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertPfamMapRow(polypeptideId: Int, pfamId: Int) {
    val insertSQL = s"""
      INSERT INTO PFAM_MAP (POLYPEPTIDE_ID, PFAM_ID)
      VALUES (${polypeptideId}, ${pfamId})
      """
    executeUpdate(insertSQL)
  }

  def createSnpEffectTable() {
    val createTableSQL = """
      CREATE TABLE SNP_EFFECT (
        SNP_EFFECT_ID     INTEGER  PRIMARY KEY,
        DRUG_ID           INT   NOT NULL,
        TAG_ID            INT   NOT NULL,
        PROTEIN_NAME      TEXT  NOT NULL,
        GENE_SYMBOL       TEXT,
        UNIPROT_ID        TEXT,
        RS_ID             TEXT,
        ALLELLE           TEXT,
        DEFINING_CHANGE   TEXT,
        ADVERSE_REACTION  TEXT,
        DESCRIPTION       TEXT,
        PUBMED_ID         TEXT,
        FOREIGN KEY(DRUG_ID) REFERENCES DRUG(DRUG_ID),
        FOREIGN KEY(TAG_ID) REFERENCES TAG(TAG_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertSnpEffect(drugId: Int, tag: String, proteinName: String, geneSymbol: Option[String], uniprotId: Option[String],
                      rsId: Option[String], allele: Option[String], definingChange: Option[String], adverseReaction: Option[String],
                      description: Option[String], pubmedId: Option[String]) {
    val tagId = getId(TAG, TAG, tag)
    val insertSQL = s"""
      INSERT INTO SNP_EFFECT (DRUG_ID, TAG_ID, PROTEIN_NAME, GENE_SYMBOL, UNIPROT_ID, 
        RS_ID, ALLELLE, DEFINING_CHANGE, ADVERSE_REACTION, 
        DESCRIPTION, PUBMED_ID)
      VALUES (${drugId}, ${tagId}, ${f(proteinName)}, ${f(geneSymbol)}, ${f(uniprotId)}, 
        ${f(rsId)}, ${f(allele)}, ${f(definingChange)}, ${f(adverseReaction)}, 
        ${f(description)}, ${f(pubmedId)})
      """
    executeUpdate(insertSQL)
  }

  def createProductPropertyTable() {
    val createTableSQL = """
      CREATE TABLE PRODUCT_PROPERTY (
        PRODUCT_PROPERTY_ID  INTEGER  PRIMARY KEY,
        TAG_ID               INT   NOT NULL,
        VALUE                TEXT  NOT NULL,
        FOREIGN KEY(TAG_ID) REFERENCES TAG(TAG_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def getProductProperty(tag: String, value: String): Option[Int] = {
    val query = s"""
        SELECT PRODUCT_PROPERTY_ID FROM PRODUCT_PROPERTY
        JOIN TAG ON (TAG.TAG_ID = PRODUCT_PROPERTY.TAG_ID)
        WHERE TAG = ${f(tag)} AND VALUE = ${f(value)} 
    """
    return findId(query, "PRODUCT_PROPERTY_ID")
  }

  def insertProductProperty(tag: String, value: String): Int = {
    lastProductPropertyId = lastProductPropertyId + 1
    val productPropertyId = lastProductPropertyId
    val tagId = getId(TAG, TAG, tag)
    val insertSQL = s"""
      INSERT INTO PRODUCT_PROPERTY (PRODUCT_PROPERTY_ID, TAG_ID, VALUE)
      VALUES (${productPropertyId}, ${tagId}, ${f(value)})
      """
    executeUpdate(insertSQL)
    return productPropertyId
  }

  def nextProductId(): Int = {
    lastProductId = lastProductId + 1
    return lastProductId
  }  
  
  def createProductMapTable() {
    val createTableSQL = """
      CREATE TABLE PRODUCT_MAP (
        PRODUCT_MAP_ID       INTEGER  PRIMARY KEY,
        DRUG_ID              INT   NOT NULL,
        PRODUCT_ID           INT   NOT NULL,
        PRODUCT_PROPERTY_ID  INT   NOT NULL,
        FOREIGN KEY(DRUG_ID) REFERENCES DRUG(DRUG_ID),
        FOREIGN KEY(PRODUCT_PROPERTY_ID) REFERENCES PRODUCT_PROPERTY(PRODUCT_PROPERTY_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertProductMapRow(drugId: Int, productId: Int, productPropertyId: Int) {
    val insertSQL = s"""
      INSERT INTO PRODUCT_MAP (DRUG_ID, PRODUCT_ID, PRODUCT_PROPERTY_ID)
      VALUES (${drugId}, ${productId}, ${productPropertyId})
      """
    executeUpdate(insertSQL)
  }
  
  def createMapTable(mapTableName: String, refTableName: String) {
    val createTableSQL = s"""
      CREATE TABLE ${mapTableName} (
        ${mapTableName}_ID  INTEGER  PRIMARY KEY,
        DRUG_ID          INT  NOT NULL,
        ${refTableName}_ID      INT  NOT NULL,
        FOREIGN KEY(DRUG_ID) REFERENCES DRUG(DRUG_ID),
        FOREIGN KEY(${refTableName}_ID) REFERENCES ${refTableName}(${refTableName}_ID)
      );
    """
    executeUpdate(createTableSQL)
  }

  def insertMapRow(matTableName: String, refTableName: String, drugId: Int, propertyId: Int) {
    val insertSQL = s"""
      INSERT INTO ${matTableName} (DRUG_ID, ${refTableName}_ID)
      VALUES (${drugId}, ${propertyId})
      """
    executeUpdate(insertSQL)
  }

  def createDictTable(tableName: String, columnName: String) {
    val createTableSQL = s"""
      CREATE TABLE ${tableName}(
        ${tableName}_ID  INTEGER  PRIMARY KEY,
        ${columnName}  TEXT  UNIQUE  NOT NULL
      );
    """
    executeUpdate(createTableSQL)
  }

  def findId(query: String, idColumn: String): Option[Int] = {
    val stm = connection.createStatement()
    val resultSet = stm.executeQuery(query)
    if (resultSet.next()) {
      val categoryId = resultSet.getInt(idColumn)
      stm.close()
      return Some(categoryId)
    }
    return None
  }

  def getId(tableName: String, columnName: String, value: String): Int = {
    dictTableSelect(tableName, tableName, value) match {
      case Some(id) => id
      case None => insertValue(tableName, tableName, value)
    }
  }

  def getId(tableName: String, columnName: String, value: Option[String]): Option[Int] = value.map(getId(tableName, columnName, _))

  private def dictTableSelect(tableName: String, columnName: String, value: String): Option[Int] = {
    val query = s"""
        SELECT ${tableName}_ID FROM ${tableName}
        WHERE ${columnName} = ${f(value)}
      """
    val stm = connection.createStatement()
    val resultSet = stm.executeQuery(query)
    if (resultSet.next()) {
      val id = Some(resultSet.getInt(tableName + "_ID"))
      stm.close()
      return id
    }
    return None
  }
  
  private def insertValue(tableName: String, columnName: String, value: String): Int = {
    val insertSQL = s"""
      INSERT INTO ${tableName} (${columnName})
      VALUES (${f(value)})
      """
    executeUpdate(insertSQL)
    return dictTableSelect(tableName, tableName, value).get
  }
  
  def createPreLoadIndexes() {
    createIndex("CATEGORY", "CATEGORY")
    createIndex("CODER", "CODER")
    createIndex("COUNTRY", "COUNTRY")
    createIndex("LANGUAGE", "LANGUAGE")
    createIndex("PATENT", "PATENT_NUMBER")
    createIndex("PATHWAY", "PATHWAY_XREF")
    createIndex("PFAM", "PFAM_IDENTIFIER")
    createIndex("PRODUCT_PROPERTY", "VALUE")
    createIndex("PROPERTY", "VALUE")
    createIndex("REFERENCE", "REF_ID")
    createIndex("REACTION_ELEMENT", "ELEMENT_DRUGBANK_ID")
    createIndex("RESOURCE", "RESOURCE")
    createIndex("TAG", "TAG")
  }

  def createIndexes() {
    createIndex("DRUG", "DRUG_ID")
    createIndex("DRUG", "DRUG_BANK_ID")
    createIndex("DRUG", "DRUG_NAME")

    createIndex("SYNONYM", "DRUG_ID")
    createIndex("SYNONYM", "SYNONYM")

    createIndex("DRUG_IDENTIFIER", "DRUG_ID")
    createIndex("DRUG_IDENTIFIER", "IDENTIFIER")

    createIndex("POLYPEPTIDE_IDENTIFIER", "POLYPEPTIDE_ID")
    createIndex("POLYPEPTIDE_IDENTIFIER", "IDENTIFIER")

    createIndex("POLYPEPTIDE_PROPERTY", "POLYPEPTIDE_ID")
    createIndex("POLYPEPTIDE_PROPERTY", "PROPERTY_ID")

    createIndex("POLYPEPTIDE", "TARGET_ID")
    createIndex("POLYPEPTIDE", "POLYPEPTIDE_IDENTIFIER")

    createIndex("TARGET", "TARGET_IDENTIFIER")

    createIndex("INTERACTION", "DRUG_ID")
    createIndex("INTERACTION", "TAG_ID")
    createIndex("INTERACTION", "INTERACTOR_ID")

    createIndex("CONNECTION", "DRUG_ID")
    createIndex("CONNECTION", "TARGET_ID")

    createIndex("CONNECTION_PROPERTY", "CONNECTION_ID")
    createIndex("CONNECTION_PROPERTY", "PROPERTY_ID")

    createIndex("PATENT_MAP", "DRUG_ID")
    createIndex("PATENT_MAP", "PATENT_ID")

    createIndex("PATHWAY_MAP", "DRUG_ID")
    createIndex("PATHWAY_MAP", "PATHWAY_ID")

    createIndex("DRUG_REFERENCE", "DRUG_ID")
    createIndex("DRUG_REFERENCE", "REFERENCE_ID")

    createIndex("CONNECTION_REFERENCE", "CONNECTION_ID")
    createIndex("CONNECTION_REFERENCE", "REFERENCE_ID")

    createIndex("PROPERTY", "TAG_ID")

    createIndex("DRUG_PROPERTY", "DRUG_ID")
    createIndex("DRUG_PROPERTY", "PROPERTY_ID")

    createIndex("CATEGORY", "CATEGORY_XREF")
    createIndex("CATEGORY_MAP", "DRUG_ID")
    createIndex("CATEGORY_MAP", "CATEGORY_ID")

    createIndex("PATHWAY_MEMBER", "PATHWAY_ID")
    createIndex("PATHWAY_MEMBER", "PATHWAY_MEMBER_XREF")

    createIndex("PFAM_MAP", "POLYPEPTIDE_ID")
    createIndex("PFAM_MAP", "PFAM_ID")

    createIndex("REACTION", "DRUG_ID")
    createIndex("REACTION_MAP", "REACTION_ID")
    createIndex("REACTION_MAP", "REACTION_ELEMENT_ID")

    createIndex("PRODUCT_MAP", "PRODUCT_MAP_ID")
    createIndex("PRODUCT_MAP", "PRODUCT_ID")
    createIndex("PRODUCT_MAP", "DRUG_ID")

    createIndex("SALT", "DRUG_ID")

    createIndex("SNP_EFFECT", "DRUG_ID")

    createIndex("REFERENCE", "PUBMED_ID")
  }

  def createIndex(table: String, column: String) {
    val sql = s"CREATE INDEX ${table}__${column}_IDX ON ${table} (${column})"
    executeUpdate(sql)
  }

  def f(str: String) = str match {
    case null => "NULL"
    case _    => "'" + str.replace("'", "''") + "'"
  }

  def f(str: Option[String]) = str match {
    case None      => "NULL"
    case Some("")  => "NULL"
    case Some(str) => "'" + str.replace("'", "''") + "'"
  }

  def is(str: Option[String]) = str match {
    case None      => "IS NULL"
    case Some(str) => "= '" + str.replace("'", "''") + "'"
  }
  
  def fd(opt: Option[Double]) = opt match {
    case None      => "NULL"
    case Some(value) => value.toString
  }
  
  def fi(opt: Option[Int]) = opt match {
    case None      => "NULL"
    case Some(value) => value.toString
  }
  
  def f(value: Boolean): Int = value match {
    case true  => 1
    case false => 0
  }

  def commit() {
    connection.commit()
  }

  def close() = {
    commit()
    connection.close()
  }
}