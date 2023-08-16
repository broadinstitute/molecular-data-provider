CREATE INDEX LE_name_index ON List_Element (primary_name COLLATE NOCASE);

CREATE INDEX LEH_list_element_id_index ON Element_Hierarchy (list_element_id);
CREATE INDEX LEH_parent_element_id_index ON Element_Hierarchy (parent_element_id);
CREATE INDEX LEH_parent_id_type_index ON Element_Hierarchy (parent_element_id, hierarchy_type);
