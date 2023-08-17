--> data/MoleProDB.sqlite >>> data/hierarchy/hierarchy-ID.tsv

    select distinct List_Element_Identifier.list_element_id
    from (
    select subject_id as list_element_id from Connection
    join List_Element on List_Element.list_element_id = Connection.subject_id 
    join Biolink_Class ON List_Element.biolink_class_id = Biolink_Class.biolink_class_id
    where biolink_class in ('Disease','PhenotypicFeature')
    union
    select object_id as list_element_id from Connection
    join List_Element on List_Element.list_element_id = Connection.object_id 
    join Biolink_Class ON List_Element.biolink_class_id = Biolink_Class.biolink_class_id
    where biolink_class in ('Disease','PhenotypicFeature')
    ) as Connection_Element
    join List_Element_Identifier on Connection_Element.list_element_id = List_Element_Identifier.list_element_id
    join Curie_Prefix on Curie_Prefix.prefix_id = List_Element_Identifier.prefix_id
    join List_Element on List_Element.list_element_id = Connection_Element.list_element_id 
    join Biolink_Class ON List_Element.biolink_class_id = Biolink_Class.biolink_class_id;
