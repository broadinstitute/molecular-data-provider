--> data/MoleProDB.sqlite >>> data/hierarchy/hierarchy-ID.tsv

    select distinct List_Element_Identifier.list_element_id
    from (
        select subject_id as list_element_id from Connection
        union
        select object_id as list_element_id from Connection
    ) as Connection_Element
    join List_Element_Identifier on Connection_Element.list_element_id = List_Element_Identifier.list_element_id
    join Curie_Prefix on Curie_Prefix.prefix_id = List_Element_Identifier.prefix_id
    where field_name in ('mondo','hpo','hp');
