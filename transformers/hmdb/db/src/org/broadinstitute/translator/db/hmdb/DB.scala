package org.broadinstitute.translator.db.hmdb

import java.sql.DriverManager;
import java.sql.Connection
import java.sql.Statement

import scala.io.Source
import scala.collection.mutable.ArrayBuffer

object DB {

  private val METABOLITE = "METABOLITE";
  private val TAG = "TAG"

  private var lastPropertyId = 0
  private var lastReferenceId = 0
  private var lastDiseaseId = 0
  private var lastPathwayId = 0
  private var lastProteinId = 0
  private var lastConcentrationId = 0
  private var lastTaxonomyId = 0
  private var lastOntologyId = 0

  private var connection: Connection = null
  private var database: String = null;
  
  def createDB(database: String) {
    this.database = database
    Class.forName("org.sqlite.JDBC")
    connection = DriverManager.getConnection("jdbc:sqlite:" + database)
    connection.setAutoCommit(false)
    exec("schema/HMDB.sql");
  }

  // metabolite

  def insertMetabolite(accession: String, name: String): Long = {
    val metaboliteId = accession.substring(4).toLong
    val insertSQL = s"""
      INSERT INTO METABOLITE (METABOLITE_ID, ACCESSION, NAME)
      VALUES (${metaboliteId}, ${f(accession)}, ${f(name)})
      """
    executeUpdate(insertSQL)
    return metaboliteId
  }

  // name

  def findName(metaboliteId: Long, name: String, nameType: String): Boolean = {
    val query = s"""
        SELECT NAME_ID FROM NAME
        WHERE METABOLITE_ID = ${metaboliteId} AND NAME = ${f(name)} AND NAME_TYPE = ${f(nameType)}
      """
    return findId(query, "NAME_ID").isDefined
  }

  def insertName(metaboliteId: Long, name: String, nameType: String): Unit = {
    if (findName(metaboliteId, name, nameType)) return
    val insertSQL = s"""
      INSERT INTO NAME (METABOLITE_ID, NAME, NAME_TYPE)
      VALUES (${metaboliteId},  ${f(name)}, ${f(nameType)})
      """
    executeUpdate(insertSQL)
  }

  // identifier

  def insertIdentifier(metaboliteId: Long, tag: String, xref: String) = {
    val tagId = getId(TAG, TAG, tag)
    val insertSQL = s"""
      INSERT INTO IDENTIFIER (METABOLITE_ID, TAG_ID, XREF)
      VALUES (${metaboliteId}, ${tagId}, ${f(xref)})
      """
    executeUpdate(insertSQL)
  }

  // property

  def insertMetaboliteProperty(metaboliteId: Long, propertyId: Int) {
    insertPropertyMapRow(METABOLITE, metaboliteId, propertyId)
  }

  def insertPropertyMapRow(parentTableName: String, parentId: Long, propertyId: Int) {
    val insertSQL = s"""
      INSERT INTO ${parentTableName}_PROPERTY (${parentTableName}_ID, PROPERTY_ID)
      VALUES (${parentId}, ${propertyId})
      """
    executeUpdate(insertSQL)
  }

  def insertMetaboliteProperty(metaboliteId: Long, tag: String, kind: Option[String], value: String, source: Option[String]) {
    val propertyId = getProperty(tag, kind, value, source)
    insertMetaboliteProperty(metaboliteId, propertyId)
  }

  def findPropertyId(tag: String, kind: Option[String], value: String, source: Option[String]): Option[Int] = {
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

  def getProperty(tag: String, kind: Option[String], value: String, source: Option[String]): Int = {
    findPropertyId(tag, kind, value, source) match {
      case Some(id) => id
      case None => insertProperty(tag, kind, value, source)
    }
  }

  // taxonomy

  def findTaxonomy(description: String, directParent: String, kingdom: String, superclass: String,
                   taxonomyClass: String, subclass: Option[String], molecularFramework: Option[String]): Option[Int] = {
    val query = s"""
      SELECT TAXONOMY_ID FROM TAXONOMY
      WHERE DESCRIPTION = ${f(description)} AND DIRECT_PARENT = ${f(directParent)} AND KINGDOM = ${f(kingdom)} AND SUPERCLASS = ${f(superclass)} 
        AND TAXONOMY_CLASS = ${f(taxonomyClass)} AND SUBCLASS ${is(subclass)} AND MOLECULAR_FRAMEWORK ${is(molecularFramework)}
      """
    return findId(query, "TAXONOMY_ID")
  }

  def insertTaxonomy(description: String, directParent: String, kingdom: String, superclass: String,
                     taxonomyClass: String, subclass: Option[String], molecularFramework: Option[String]): Int = {
    lastTaxonomyId = lastTaxonomyId + 1
    val taxonomyId = lastTaxonomyId
    val insertSQL = s"""
      INSERT INTO TAXONOMY (
        TAXONOMY_ID, DESCRIPTION, DIRECT_PARENT, KINGDOM,  
        SUPERCLASS, TAXONOMY_CLASS, SUBCLASS, MOLECULAR_FRAMEWORK)
      VALUES (${taxonomyId}, ${f(description)}, ${f(directParent)}, ${f(kingdom)},
        ${f(superclass)}, ${f(taxonomyClass)}, ${f(subclass)}, ${f(molecularFramework)})
      """
    executeUpdate(insertSQL)
    return taxonomyId
  }

  def getTaxonomy(description: String, directParent: String, kingdom: String, superclass: String,
                  taxonomyClass: String, subclass: Option[String], molecularFramework: Option[String]): Int = {
    findTaxonomy(description, directParent, kingdom, superclass, taxonomyClass, subclass, molecularFramework) match {
      case Some(id) => id
      case None => insertTaxonomy(description, directParent, kingdom, superclass, taxonomyClass, subclass, molecularFramework)
    }
  }

  def insertTaxonomy(metaboliteId: Long, taxonomyId: Int) {
    val insertSQL = s"""
      INSERT INTO TAXONOMY_MAP (METABOLITE_ID, TAXONOMY_ID)
      VALUES (${metaboliteId}, ${taxonomyId})
      """
    executeUpdate(insertSQL)
  }

  def findTaxonomyProperty(metaboliteId: Long, propertyId: Int): Boolean = {
    val query = s"""
      SELECT TAXONOMY_PROPERTY_ID FROM TAXONOMY_PROPERTY
      WHERE METABOLITE_ID = ${metaboliteId} AND PROPERTY_ID = ${propertyId}
      """
    return findId(query, "TAXONOMY_PROPERTY_ID").isDefined
  }

  def insertTaxonomyProperty(metaboliteId: Long, propertyId: Int) {
    val insertSQL = s"""
      INSERT INTO TAXONOMY_PROPERTY (METABOLITE_ID, PROPERTY_ID)
      VALUES (${metaboliteId}, ${propertyId})
      """
    executeUpdate(insertSQL)
  }

  // ontology

  def findOntology(term: String, definition: Option[String], level: Int): Option[Int] = {
    val query = s"""
      SELECT ONTOLOGY_ID FROM ONTOLOGY
      WHERE ONTOLOGY_TERM = ${f(term)} AND DEFINITION ${is(definition)} AND ONTOLOGY_LEVEL = ${level}
      """
    return findId(query, "ONTOLOGY_ID")
  }

  def insertOntology(parentId: Option[Int], term: String, definition: Option[String], xmlParentId: Option[Int], level: Int, ontologyType: String): Int = {
    lastOntologyId = lastOntologyId + 1
    val ontologyId = lastOntologyId
    val insertSQL = s"""
      INSERT INTO ONTOLOGY 
        (ONTOLOGY_ID, ONTOLOGY_PARENT_ID, ONTOLOGY_TERM, DEFINITION, XML_PARENT_ID, ONTOLOGY_LEVEL, ONTOLOGY_TYPE)
      VALUES (${ontologyId}, ${fi(parentId)}, ${f(term)}, ${f(definition)}, ${fi(xmlParentId)}, ${level}, ${f(ontologyType)})
      """
    executeUpdate(insertSQL)
    return ontologyId
  }

  def getOntology(parentId: Option[Int], term: String, definition: Option[String], xmlParentId: Option[Int], level: Int,
                  ontologyType: String, synonyms: ArrayBuffer[String]): Int = {
    findOntology(term, definition, level) match {
      case Some(id) => id
      case None => {
        val ontologyId = insertOntology(parentId, term, definition, xmlParentId, level, ontologyType)
        for (synonym <- synonyms) {
          DB.insertOntologySynonym(ontologyId, synonym)
        }
        ontologyId
      }
    }
  }

  def insertOntology(metaboliteId: Long, parentId: Int) {
    val insertSQL = s"""
      INSERT INTO ONTOLOGY_MAP (METABOLITE_ID, ONTOLOGY_ID)
      VALUES (${metaboliteId}, ${parentId})
      """
    executeUpdate(insertSQL)
  }

  def insertOntologySynonym(parentId: Int, synonym: String) {
    val insertSQL = s"""
      INSERT INTO ONTOLOGY_SYNONYM (ONTOLOGY_ID, ONTOLOGY_SYNONYM)
      VALUES (${parentId}, ${f(synonym)})
      """
    executeUpdate(insertSQL)
  }

  // pathway

  def findPathway(pathwayName: String, smpdbId: Option[String], keggMapId: Option[String]): Option[Int] = {
    val query = s"""
      SELECT PATHWAY_ID FROM PATHWAY
      WHERE PATHWAY_NAME = ${f(pathwayName)} AND SMPDB_ID ${is(smpdbId)} AND KEGG_MAP_ID ${is(keggMapId)}
      """
    return findId(query, "PATHWAY_ID")
  }

  def insertPathway(pathwayName: String, smpdbId: Option[String], keggMapId: Option[String]): Int = {
    lastPathwayId = lastPathwayId + 1
    val pathwayId = lastPathwayId
    val insertSQL = s"""
      INSERT INTO PATHWAY (PATHWAY_ID, PATHWAY_NAME, SMPDB_ID, KEGG_MAP_ID)
      VALUES (${pathwayId}, ${f(pathwayName)}, ${f(smpdbId)}, ${f(keggMapId)})
      """
    executeUpdate(insertSQL)
    pathwayId
  }

  def findPathway(metaboliteId: Long, pathwayId: Int): Boolean = {
    val query = s"""
      SELECT PATHWAY_MAP_ID FROM PATHWAY_MAP
      WHERE METABOLITE_ID = ${metaboliteId} AND PATHWAY_ID = ${pathwayId}
      """
    return findId(query, "PATHWAY_MAP_ID").isDefined
  }

  def insertPathway(metaboliteId: Long, pathwayId: Int) {
    val insertSQL = s"""
      INSERT INTO PATHWAY_MAP (METABOLITE_ID, PATHWAY_ID)
      VALUES (${metaboliteId}, ${pathwayId})
      """
    executeUpdate(insertSQL)
  }

  def insertPathway(metaboliteId: Long, pathwayName: Option[String], smpdbId: Option[String], keggMapId: Option[String]) {
    if (pathwayName.isDefined) {
      val pathwayId = findPathway(pathwayName.get, smpdbId, keggMapId) match {
        case Some(id) => id
        case None => insertPathway(pathwayName.get, smpdbId, keggMapId)
      }
      if (findPathway(metaboliteId, pathwayId)) {
        println("  Warning: duplicate pathway, metaboliteId = " + metaboliteId + "\tpathwayId = " + pathwayId)
      }
      else {
        insertPathway(metaboliteId, pathwayId)
      }
    }
  }

  //concentration

  def insertConcentration(metaboliteId: Long, abnormal: Boolean, biospecimen: Option[String], concentrationValue: Option[String],
                          concentrationUnits: Option[String], age: Option[String], gender: Option[String],
                          subjectCondition: Option[String], patientInformation: Option[String], comment: Option[String]): Int = {
    lastConcentrationId = lastConcentrationId + 1
    val concentrationId = lastConcentrationId
    val insertSQL = s"""
      INSERT INTO CONCENTRATION (
        CONCENTRATION_ID, METABOLITE_ID, ABNORMAL_CONCENTRATION, BIOSPECIMEN, CONCENTRATION_VALUE, 
        CONCENTRATION_UNITS, AGE, GENDER, SUBJECT_CONDITION, PATIENT_INFORMATION, COMMENT)
      VALUES (${concentrationId}, ${metaboliteId}, ${f(abnormal)}, ${f(biospecimen)}, ${f(concentrationValue)},
        ${f(concentrationUnits)}, ${f(age)}, ${f(gender)}, ${f(subjectCondition)}, ${f(patientInformation)}, ${f(comment)})
      """
    executeUpdate(insertSQL)
    return concentrationId
  }

  def insertConcentrationReference(concentrationId: Long, referenceId: Int) {
    val insertSQL = s"""
      INSERT INTO CONCENTRATION_REFERENCE_MAP (CONCENTRATION_ID, REFERENCE_ID)
      VALUES (${concentrationId}, ${referenceId})
      """
    executeUpdate(insertSQL)
  }

  // disease

  def getDisease(disease: String, omimId: Option[Int]): Int = {
    findDisease(disease) match {
      case Some(id) => id
      case None => insertDisease(disease, omimId)
    }
  }

  def findDisease(disease: String): Option[Int] = {
    val query = s"""
      SELECT DISEASE_ID FROM DISEASE
      WHERE DISEASE = ${f(disease)}
      """
    return findId(query, "DISEASE_ID")
  }

  def insertDisease(disease: String, omimId: Option[Int]): Int = {
    lastDiseaseId = lastDiseaseId + 1
    val diseaseId = lastDiseaseId
    val insertSQL = s"""
      INSERT INTO DISEASE (DISEASE_ID, DISEASE, OMIM_ID)
      VALUES (${diseaseId}, ${f(disease)}, ${fi(omimId)})
      """
    executeUpdate(insertSQL)
    return diseaseId
  }

  def insertDisease(metaboliteId: Long, diseaseId: Int) {
    val insertSQL = s"""
      INSERT INTO DISEASE_MAP (METABOLITE_ID, DISEASE_ID)
      VALUES (${metaboliteId}, ${diseaseId})
      """
    executeUpdate(insertSQL)
  }

  def insertDiseaseReference(metaboliteId: Long, diseaseId: Int, referenceId: Int) {
    val insertSQL = s"""
      INSERT INTO DISEASE_REFERENCE_MAP (METABOLITE_ID, DISEASE_ID, REFERENCE_ID)
      VALUES (${metaboliteId}, ${diseaseId}, ${referenceId})
      """
    executeUpdate(insertSQL)
  }

  //reference

  def getReference(referenceText: String, pubmedId: Option[String]) = {
    findReference(referenceText, pubmedId) match {
      case Some(id) => id
      case None => insertReference(referenceText, pubmedId.map(_.toLong))
    }
  }

  def insertReference(metaboliteId: Long, reference: Option[String], pubmedId: Option[String], tag: String) {
    for (referenceText <- reference) {
      val referenceId = getReference(referenceText, pubmedId)
      insertReference(metaboliteId, referenceId, tag)
    }
  }

  def findReference(referenceText: String, pubmedId: Option[String]): Option[Int] = {
    val query = s"""
        SELECT REFERENCE_ID, PUBMED_ID FROM REFERENCE
        WHERE REFERENCE = ${f(referenceText)}
      """
    val stm = connection.createStatement()
    val resultSet = stm.executeQuery(query)
    if (resultSet.next()) {
      val referenceId = resultSet.getInt("REFERENCE_ID")
      val dbPubmedId = resultSet.getLong("PUBMED_ID")
      if (resultSet.wasNull() && pubmedId.isDefined) {
        updatePubmedId(referenceId, pubmedId.get.toLong)
      }
      stm.close()
      return Some(referenceId)
    }
    return None
  }

  def insertReference(reference: String, pubmedId: Option[Long]): Int = {
    lastReferenceId = lastReferenceId + 1
    val referenceId = lastReferenceId
    val insertSQL = s"""
      INSERT INTO REFERENCE (REFERENCE_ID, REFERENCE, PUBMED_ID)
      VALUES (${referenceId}, ${f(reference)}, ${fl(pubmedId)})
      """
    executeUpdate(insertSQL)
    return referenceId
  }

  def updatePubmedId(referenceId: Int, pubmedId: Long) {
    val updateSQL = s"""
      UPDATE REFERENCE SET PUBMED_ID = ${pubmedId}
      WHERE REFERENCE_ID = ${referenceId}
      """
    print("update reference " + referenceId)
    executeUpdate(updateSQL)
  }

  def insertReference(metaboliteId: Long, referenceId: Int, tag: String) {
    val tagId = getId(TAG, TAG, tag)
    val insertSQL = s"""
      INSERT INTO REFERENCE_MAP (METABOLITE_ID, REFERENCE_ID, TAG_ID)
      VALUES (${metaboliteId}, ${referenceId}, ${tagId})
      """
    executeUpdate(insertSQL)
  }

  // protein

  def findProtein(proteinAccession: String): Option[Int] = {
    val query = s"""
      SELECT PROTEIN_ID FROM PROTEIN
      WHERE PROTEIN_ACCESSION = ${f(proteinAccession)}
      """
    return findId(query, "PROTEIN_ID")
  }

  def insertProtein(proteinAccession: String, proteinName: String, uniprotId: String, geneName: String, proteinType: Option[String]): Int = {
    lastProteinId = lastProteinId + 1
    val proteinId = lastProteinId
    val insertSQL = s"""
      INSERT INTO PROTEIN (PROTEIN_ID, PROTEIN_ACCESSION, PROTEIN_NAME, UNIPROT_ID, GENE_NAME, PROTEIN_TYPE)
      VALUES (${proteinId}, ${f(proteinAccession)}, ${f(proteinName)}, ${f(uniprotId)}, ${f(geneName)}, ${f(proteinType)})
      """
    executeUpdate(insertSQL)
    return proteinId
  }

  def getProtein(proteinAccession: String, proteinName: String, uniprotId: String, geneName: String, proteinType: Option[String]): Int = {
    findProtein(proteinAccession) match {
      case Some(id) => id
      case None => insertProtein(proteinAccession, proteinName, uniprotId, geneName, proteinType)
    }
  }

  def insertProtein(metaboliteId: Long, proteinId: Int) {
    val insertSQL = s"""
      INSERT INTO PROTEIN_MAP (METABOLITE_ID, PROTEIN_ID)
      VALUES (${metaboliteId}, ${proteinId})
      """
    executeUpdate(insertSQL)
  }

  // query utils

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

  // DB utils

  private def exec(sqlFile: String) {
    val source = Source.fromFile(sqlFile)(io.Codec("UTF-8"))
    for (statement <- source.mkString("").split(";")) {
      executeUpdate(statement)
    }
    commit()
  }

  def createIndexes() {
    println("building indexes")
    createIndex("NAME", "METABOLITE_ID")
    createIndex("NAME", "NAME")
    createIndex("IDENTIFIER", "METABOLITE_ID")
    createIndex("IDENTIFIER", "TAG_ID", "XREF")
    createIndex("TAXONOMY", "DIRECT_PARENT")
    createIndex("TAXONOMY", "KINGDOM")
    createIndex("TAXONOMY", "SUPERCLASS")
    createIndex("TAXONOMY", "TAXONOMY_CLASS")
    createIndex("TAXONOMY", "SUBCLASS")
    createIndex("TAXONOMY_MAP", "METABOLITE_ID")
    createIndex("TAXONOMY_MAP", "TAXONOMY_ID")
    createIndex("TAXONOMY_PROPERTY", "METABOLITE_ID")
    createIndex("ONTOLOGY", "ONTOLOGY_TERM")
    createIndex("ONTOLOGY", "ONTOLOGY_PARENT_ID")
    createIndex("ONTOLOGY_MAP", "METABOLITE_ID")
    createIndex("ONTOLOGY_MAP", "ONTOLOGY_ID")
    createIndex("ONTOLOGY_SYNONYM", "ONTOLOGY_ID")
    createIndex("ONTOLOGY_SYNONYM", "ONTOLOGY_SYNONYM")
    createIndex("PATHWAY", "SMPDB_ID")
    createIndex("PATHWAY_MAP", "METABOLITE_ID")
    createIndex("PATHWAY_MAP", "PATHWAY_ID")
    createIndex("CONCENTRATION", "METABOLITE_ID")
    createIndex("CONCENTRATION", "BIOSPECIMEN")
    createIndex("CONCENTRATION_REFERENCE_MAP", "CONCENTRATION_ID")
    createIndex("DISEASE_MAP", "METABOLITE_ID")
    createIndex("DISEASE_MAP", "DISEASE_ID")
    createIndex("DISEASE_REFERENCE_MAP", "METABOLITE_ID")
    createIndex("DISEASE_REFERENCE_MAP", "DISEASE_ID")
    createIndex("DISEASE_REFERENCE_MAP", "METABOLITE_ID", "DISEASE_ID")
    createIndex("REFERENCE_MAP", "METABOLITE_ID")
    createIndex("PROTEIN", "UNIPROT_ID")
    createIndex("PROTEIN_MAP", "METABOLITE_ID")
    createIndex("PROTEIN_MAP", "PROTEIN_ID")
    createIndex("METABOLITE_PROPERTY", "METABOLITE_ID")
    createIndex("METABOLITE_PROPERTY", "PROPERTY_ID")
    createIndex("PROPERTY", "TAG_ID")
  }

  def createIndex(table: String, column: String) {
    val sql = s"CREATE INDEX ${table}__${column}_IDX ON ${table} (${column})"
    executeUpdate(sql)
  }

  def createIndex(table: String, column1: String, column2: String) {
    val sql = s"CREATE INDEX ${table}__${column1}__${column2}_IDX ON ${table} (${column1}, ${column2})"
    executeUpdate(sql)
  }

  private def executeUpdate(sql: String) {
    val stm = connection.createStatement()
    stm.executeUpdate(sql)
    stm.close()
  }

  def commit() {
    connection.commit()
  }

  def reconnect() {
    connection.close()
    connection = null
    connection = DriverManager.getConnection("jdbc:sqlite:" + database)
    connection.setAutoCommit(false)

  }

  def close() = {
    commit()
    connection.close()
  }

  // format SQL

  def f(str: String) = str match {
    case null => "NULL"
    case _ => "'" + str.replace("'", "''") + "'"
  }

  def f(str: Option[String]) = str match {
    case None => "NULL"
    case Some("") => "NULL"
    case Some(str) => "'" + str.replace("'", "''") + "'"
  }

  def f(value: Boolean): Int = value match {
    case true => 1
    case false => 0
  }

  def fl(opt: Option[Long]) = opt match {
    case None => "NULL"
    case Some(value) => value.toString
  }

  def fi(opt: Option[Int]) = opt match {
    case None => "NULL"
    case Some(value) => value.toString
  }

  def is(str: Option[String]) = str match {
    case None => "IS NULL"
    case Some(str) => "= '" + str.replace("'", "''") + "'"
  }
}
