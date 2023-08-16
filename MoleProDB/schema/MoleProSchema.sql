CREATE TABLE "Attribute" (
  "attribute_id" INTEGER NOT NULL,
  "attribute_type_id" INT NOT NULL REFERENCES "Attribute_Type"("attribute_type_id"),
  "attribute_value" TEXT NOT NULL,
  "url" TEXT,
  "description" TEXT,
  PRIMARY KEY ("attribute_id"),
  UNIQUE ("attribute_type_id", "attribute_value", "url", "description")
);

CREATE TABLE "Attribute_Type" (
  "attribute_type_id" INTEGER NOT NULL,
  "attribute_name" TEXT NOT NULL,
  "attribute_type" TEXT NOT NULL,
  "value_type" TEXT,
  PRIMARY KEY ("attribute_type_id"),
  UNIQUE ("attribute_type", "attribute_name")
);

CREATE TABLE "Biolink_Class" (
  "biolink_class_id" INTEGER NOT NULL,
  "biolink_class" TEXT UNIQUE NOT NULL,
  PRIMARY KEY ("biolink_class_id")
);

CREATE TABLE "Chem_Structure" (
  "structure_id" INTEGER NOT NULL,
  "inchi" TEXT,
  "inchikey" TEXT NOT NULL,
  PRIMARY KEY ("structure_id")
);

CREATE TABLE "Chem_Structure_Attribute" (
  "structure_attribute_id" INTEGER NOT NULL,
  "structure_id" INT NOT NULL REFERENCES "Chem_Structure"("structure_id"),
  "attribute_id" INT NOT NULL REFERENCES "Attribute"("attribute_id"),
  "source_id" INT NOT NULL REFERENCES "Source"("source_id"),
  PRIMARY KEY ("structure_attribute_id"),
  UNIQUE ("structure_id", "attribute_id", "source_id")
);

CREATE TABLE "Chem_Structure_Identifier" (
  "structure_identifier_id" INTEGER NOT NULL,
  "structure_id" INT NOT NULL REFERENCES "Chem_Structure"("structure_id"),
  "xref" TEXT NOT NULL,
  "prefix_id" INT NOT NULL REFERENCES "Curie_Prefix"("prefix_id"),
  "source_id" INT NOT NULL REFERENCES "Source"("source_id"),
  PRIMARY KEY ("structure_identifier_id"),
  UNIQUE ("structure_id", "xref", "prefix_id", "source_id")
);

CREATE TABLE "Chem_Structure_Map" (
  "structure_map_id" INTEGER NOT NULL,
  "substance_id" INT NOT NULL REFERENCES "List_Element"("list_element_id"),
  "structure_id" INT NOT NULL REFERENCES "Chem_Structure"("structure_id"),
  "correct" BOOLEAN,
  PRIMARY KEY ("structure_map_id"),
  UNIQUE ("structure_id", "substance_id")
);

CREATE TABLE "Chem_Structure_Name" (
  "structure_name_id" INTEGER NOT NULL,
  "structure_id" INT NOT NULL REFERENCES "Chem_Structure"("structure_id"),
  "name_id" INT NOT NULL REFERENCES "Name"("name_id"),
  "name_type_id" INT NOT NULL REFERENCES "Name_Type"("name_type_id"),
  "name_source_id" INT NOT NULL REFERENCES "Name_Source"("name_source_id"),
  "source_id" INT NOT NULL REFERENCES "Source"("source_id"),
  "language" TEXT,
  PRIMARY KEY ("structure_name_id")
);

CREATE TABLE "Chem_Structure_Source" (
  "structure_source_id" INTEGER NOT NULL,
  "structure_map_id" INT NOT NULL REFERENCES "Chem_Structure_Map"("structure_map_id"),
  "source_id" INT NOT NULL REFERENCES "Source"("source_id"),
  PRIMARY KEY ("structure_source_id")
);

CREATE TABLE "Connection" (
  "connection_id" INTEGER NOT NULL,
  "uuid" TEXT UNIQUE,
  "subject_id" INT NOT NULL REFERENCES "List_Element"("list_element_id"),
  "object_id" INT NOT NULL REFERENCES "List_Element"("list_element_id"),
  "predicate_id" INT NOT NULL REFERENCES "Predicate"("predicate_id"),
  "source_id" INT NOT NULL REFERENCES "Source"("source_id"),
  PRIMARY KEY ("connection_id"),
  UNIQUE ("subject_id", "object_id", "predicate_id", "source_id")
);

CREATE TABLE "Connection_Attribute" (
  "connection_attribute_id" INTEGER NOT NULL,
  "connection_id" INT NOT NULL REFERENCES "Connection"("connection_id"),
  "attribute_id" INT NOT NULL REFERENCES "Attribute"("attribute_id"),
  "source_id" INT NOT NULL REFERENCES "Source"("source_id"),
  PRIMARY KEY ("connection_attribute_id"),
  UNIQUE ("connection_id", "attribute_id", "source_id")
);

CREATE TABLE "Curie_Prefix" (
  "prefix_id" INTEGER NOT NULL,
  "biolink_class_id" INT NOT NULL REFERENCES "Biolink_Class"("biolink_class_id"),
  "mole_pro_prefix" TEXT NOT NULL,
  "biolink_prefix" TEXT NOT NULL,
  "field_name" TEXT NOT NULL,
  "infores_id" INT REFERENCES "Infores"("infores_id"),
  "uri" TEXT,
  PRIMARY KEY ("prefix_id"),
  UNIQUE ("biolink_class_id", "mole_pro_prefix", "field_name", "infores_id")
);

CREATE TABLE "Element_Hierarchy" (
  "element_hierarchy_id" INTEGER NOT NULL,
  "list_element_id" INT NOT NULL REFERENCES "List_Element"("list_element_id"),
  "parent_element_id" INT NOT NULL REFERENCES "List_Element"("list_element_id"),
  "hierarchy_type" TEXT NOT NULL,
  PRIMARY KEY ("element_hierarchy_id"),
  UNIQUE ("list_element_id", "parent_element_id", "hierarchy_type")
);

CREATE TABLE "Infores" (
  "infores_id" INTEGER NOT NULL,
  "resource" TEXT UNIQUE NOT NULL,
  PRIMARY KEY ("infores_id")
);

CREATE TABLE "List_Element" (
  "list_element_id" INTEGER NOT NULL,
  "primary_name" TEXT,
  "biolink_class_id" INT NOT NULL REFERENCES "Biolink_Class"("biolink_class_id"),
  PRIMARY KEY ("list_element_id")
);

CREATE TABLE "List_Element_Attribute" (
  "element_attribute_id" INTEGER NOT NULL,
  "list_element_id" INT NOT NULL REFERENCES "List_Element"("list_element_id"),
  "attribute_id" INT NOT NULL REFERENCES "Attribute"("attribute_id"),
  "source_id" INT NOT NULL REFERENCES "Source"("source_id"),
  PRIMARY KEY ("element_attribute_id"),
  UNIQUE ("list_element_id", "attribute_id", "source_id")
);

CREATE TABLE "List_Element_Identifier" (
  "element_identifier_id" INTEGER NOT NULL,
  "list_element_id" INT NOT NULL REFERENCES "List_Element"("list_element_id"),
  "xref" TEXT NOT NULL,
  "prefix_id" INT NOT NULL REFERENCES "Curie_Prefix"("prefix_id"),
  "source_id" INT NOT NULL REFERENCES "Source"("source_id"),
  PRIMARY KEY ("element_identifier_id"),
  UNIQUE ("list_element_id", "xref", "prefix_id", "source_id")
);

CREATE TABLE "List_Element_Name" (
  "element_name_id" INTEGER NOT NULL,
  "list_element_id" INT NOT NULL REFERENCES "List_Element"("list_element_id"),
  "name_id" INT NOT NULL REFERENCES "Name"("name_id"),
  "name_type_id" INT NOT NULL REFERENCES "Name_Type"("name_type_id"),
  "name_source_id" INT NOT NULL REFERENCES "Name_Source"("name_source_id"),
  "source_id" INT NOT NULL REFERENCES "Source"("source_id"),
  "language" TEXT,
  PRIMARY KEY ("element_name_id")
);

CREATE TABLE "Name" (
  "name_id" INTEGER NOT NULL,
  "name" TEXT UNIQUE NOT NULL,
  PRIMARY KEY ("name_id")
);

CREATE TABLE "Name_Source" (
  "name_source_id" INTEGER NOT NULL,
  "name_source" TEXT UNIQUE NOT NULL,
  PRIMARY KEY ("name_source_id")
);

CREATE TABLE "Name_Type" (
  "name_type_id" INTEGER NOT NULL,
  "name_type" TEXT UNIQUE NOT NULL,
  "name_priority" INT NOT NULL,
  PRIMARY KEY ("name_type_id")
);

CREATE TABLE "Parent_Attribute" (
  "attribute_id" INTEGER NOT NULL,
  "parent_attribute_id" INT NOT NULL REFERENCES "Attribute"("attribute_id"),
  "source_id" INT NOT NULL REFERENCES "Source"("source_id"),
  PRIMARY KEY ("attribute_id")
);

CREATE TABLE "Predicate" (
  "predicate_id" INTEGER NOT NULL,
  "biolink_predicate" TEXT NOT NULL,
  "inverse_predicate" TEXT NOT NULL,
  "canonical" TEXT,
  "relation" TEXT UNIQUE NOT NULL,
  "inverse_relation" TEXT,
  PRIMARY KEY ("predicate_id")
);

CREATE TABLE "Source" (
  "source_id" INTEGER NOT NULL,
  "source_name" TEXT NOT NULL,
  "infores_id" INT REFERENCES "Infores"("infores_id"),
  "source_url" TEXT,
  "transformer" TEXT UNIQUE NOT NULL,
  "transformer_url" TEXT,
  "transformer_version" TEXT,
  "source_version" TEXT,
  PRIMARY KEY ("source_id")
);

