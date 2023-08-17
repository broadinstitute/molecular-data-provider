CREATE INDEX LE_name_index ON List_Element (primary_name COLLATE NOCASE);

CREATE INDEX LEH_list_element_id_index ON Element_Hierarchy (list_element_id);
CREATE INDEX LEH_parent_element_id_index ON Element_Hierarchy (parent_element_id);
CREATE INDEX LEH_parent_id_type_index ON Element_Hierarchy (parent_element_id, hierarchy_type);

CREATE INDEX A_attribute_type_id_index ON Attribute (attribute_type_id);
CREATE INDEX CA_attribute_id_index ON Connection_Attribute (attribute_id);
CREATE INDEX CA_source_id_index ON Connection_Attribute (source_id);

CREATE INDEX LEA_attribute_id_index ON List_Element_Attribute (attribute_id);
CREATE INDEX LEA_source_id_index ON List_Element_Attribute (source_id);

CREATE INDEX C_source_id_index ON Connection (source_id);
CREATE INDEX C_predicate_id_index ON Connection (predicate_id);
