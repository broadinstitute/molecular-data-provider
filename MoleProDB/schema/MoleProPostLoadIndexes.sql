CREATE INDEX LE_name_index ON List_Element (primary_name COLLATE NOCASE);
CREATE INDEX LE_biolink_class_index ON List_Element (biolink_class_id);

CREATE INDEX LEH_list_element_index ON List_Element_Hierarchy (list_element_id);
CREATE INDEX LEH_parent_element_index ON List_Element_Hierarchy (parent_element_id);
CREATE INDEX LEH_parent_type_index ON List_Element_Hierarchy (parent_element_id, hierarchy_type);

CREATE INDEX CSA_attribute_type_index ON Chem_Structure_Attribute (attribute_type_id);

CREATE INDEX CA_attribute_type_index ON Connection_Attribute (attribute_type_id);
CREATE INDEX CA_attribute_type_connection_id_index ON Connection_Attribute (connection_id, attribute_type_id);
CREATE INDEX CA_attribute_index ON Connection_Attribute (attribute_id);
CREATE INDEX CA_source_index ON Connection_Attribute (source_id);

CREATE INDEX LEA_attribute_index ON List_Element_Attribute (attribute_id);
CREATE INDEX LEA_source_index ON List_Element_Attribute (source_id);
CREATE INDEX LEA_attribute_type_index ON List_Element_Attribute (attribute_type_id);
CREATE INDEX LEA_attribute_type_list_element_id_index ON List_Element_Attribute (list_element_id, attribute_type_id);

CREATE INDEX PA_source_index ON Parent_Attribute (source_id);
CREATE INDEX PA_source_parent_index ON Parent_Attribute (parent_attribute_id, source_id);

CREATE INDEX C_source_index ON Connection (source_id);
CREATE INDEX C_predicate_index ON Connection (predicate_id);
CREATE INDEX C_qualifier_set_index ON Connection (qualifier_set_id);

CREATE INDEX Q_qualifier_type_index ON Qualifier (qualifier_type);
