--> data/translator/ctd/latest/CTD.sqlite >>> data/nn/CTD-GO.tsv

    select distinct GOTermID as GO
    from chem_go_enriched
    where GOTermID is not null
    union
    select distinct phenotypeid
    from pheno_term_ixns
    where phenotypeid is not null;


--> data/translator/ctd/latest/CTD.sqlite >>> data/nn/CTD-pathways.tsv

    select distinct pathwayID as id
    from chem_pathways_enriched
    where PubChem_CID is null;


--> data/msigdb/MolePro.MSigDB.sqlite >>> data/nn/MSigDB-GO.tsv

    select distinct Curie_Prefix.biolink_prefix || ':' || List_Element_Identifier.xref as id
    from List_Element
    join Biolink_Class on Biolink_Class.biolink_class_id = List_Element.biolink_class_id
    join List_Element_Identifier on List_Element_Identifier.list_element_id = List_Element.list_element_id
    join Curie_Prefix on Curie_Prefix.prefix_id = List_Element_Identifier.prefix_id
    where biolink_class = 'Pathway' and Curie_Prefix.field_name = 'go';



