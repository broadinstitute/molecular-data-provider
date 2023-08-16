CREATE INDEX CS_inchi_index ON Chem_Structure (inchi);
CREATE INDEX CS_inchikey_index ON Chem_Structure (inchikey);
CREATE INDEX N_name_index ON Name (name COLLATE NOCASE);
CREATE INDEX S_transformer_index ON Source (transformer);

CREATE INDEX CSI_structure_index ON Chem_Structure_Identifier (structure_id);
CREATE INDEX CSI_xref_index ON Chem_Structure_Identifier (xref);
CREATE INDEX CSN_structure_index ON Chem_Structure_Name (structure_id);
CREATE INDEX CSA_structure_index ON Chem_Structure_Attribute (structure_id);

CREATE INDEX LEI_element_index ON List_Element_Identifier (list_element_id);
CREATE INDEX LEI_xref_index    ON List_Element_Identifier (xref);
CREATE INDEX LEN_element_index ON List_Element_Name (list_element_id);
CREATE INDEX LEN_name_index    ON List_Element_Name (name_id);
CREATE INDEX LEA_element_index ON List_Element_Attribute (list_element_id);

CREATE INDEX CA_connection_index ON Connection_Attribute (connection_id);
CREATE INDEX C_subject_index     ON Connection (subject_id);
CREATE INDEX C_object_index      ON Connection (object_id);

CREATE INDEX A_value_index ON Attribute (attribute_value);
CREATE INDEX P_biolink_predicate_index ON Predicate (biolink_predicate);
CREATE INDEX P_inverse_predicate_index ON Predicate (inverse_predicate);

CREATE INDEX PA_parent_index ON Parent_Attribute (parent_attribute_id);
