--> data/translator/BiGG_model/ver-1.6.0/BiGG.sqlite >>> data/nn/BiGG-entrez.tsv

    select distinct db_id as gene_id
    from gene_db
    where gene_db."database" = 'NCBI Entrez Gene';


--> data/translator/chembl/chembl_30/ChEMBL.target.xref.sqlite >>> data/nn/ChEMBL-gene-id.tsv

    select distinct 'ENSEMBL:' || xref_id as gene_id
    from component_xref
    where component_xref.xref_src_db = 'EnsemblGene';


--> data/cmap/MolePro.CMAP.sqlite >>> data/nn/CMAP-NCBIGeneId.tsv

    select distinct Curie_Prefix.biolink_prefix || ':' || List_Element_Identifier.xref as gene_id
    from List_Element
    join Biolink_Class on Biolink_Class.biolink_class_id = List_Element.biolink_class_id
    join List_Element_Identifier on List_Element_Identifier.list_element_id = List_Element.list_element_id
    join Curie_Prefix on Curie_Prefix.prefix_id = List_Element_Identifier.prefix_id
    where biolink_class = 'Gene' and Curie_Prefix.field_name = 'entrez';


--> data/translator/ctd/2021-03/CTD_07_21.sqlite >>> data/nn/CTD-geneID.tsv

    select distinct 'NCBIGene:'||GeneID as gene_id
    from chem_gene_ixns
    union
    select distinct 'NCBIGene:'||GeneID as GeneID
    from chem_gene_ixns_w_axn_info;


--> data/dgidb/MolePro.DGIdb.sqlite >>> data/nn/DGIdb-gene-id.tsv

    select distinct Curie_Prefix.biolink_prefix || ':' || List_Element_Identifier.xref as gene_id
    from List_Element
    join Biolink_Class on Biolink_Class.biolink_class_id = List_Element.biolink_class_id
    join List_Element_Identifier on List_Element_Identifier.list_element_id = List_Element.list_element_id
    join Curie_Prefix on Curie_Prefix.prefix_id = List_Element_Identifier.prefix_id
    where biolink_class = 'Gene' and Curie_Prefix.field_name = 'entrez';


--> data/drugbank/MolePro.DrugBank.sqlite >>> data/nn/DrugBank-gene-id.tsv

    select distinct Curie_Prefix.biolink_prefix || ':' || List_Element_Identifier.xref as gene_id
    from List_Element
    join Biolink_Class on Biolink_Class.biolink_class_id = List_Element.biolink_class_id
    join List_Element_Identifier on List_Element_Identifier.list_element_id = List_Element.list_element_id
    join Curie_Prefix on Curie_Prefix.prefix_id = List_Element_Identifier.prefix_id
    where biolink_class = 'Gene';


--> data/gtopdb/MolePro.GtoPdb.sqlite >>> data/nn/GtoPdb-gene-id.tsv

    select distinct Curie_Prefix.biolink_prefix || ':' || List_Element_Identifier.xref as gene_id
    from List_Element
    join Biolink_Class on Biolink_Class.biolink_class_id = List_Element.biolink_class_id
    join List_Element_Identifier on List_Element_Identifier.list_element_id = List_Element.list_element_id
    join Curie_Prefix on Curie_Prefix.prefix_id = List_Element_Identifier.prefix_id
    where biolink_class = 'Gene';


--> data/translator/msigdb/ver-7.4/MSigDB.sqlite >>> data/nn/MSigDB-gene-id.tsv

    select distinct 'NCBIGene:' || MEMBERS_3 as id
    from MEMBER
    where MEMBERS_3 is not null;


--> data/pharos/MolePro.Pharos.sqlite >>> data/nn/Pharos-gene-id.tsv

    select distinct Curie_Prefix.biolink_prefix || ':' || List_Element_Identifier.xref as gene_id
    from List_Element
    join Biolink_Class on Biolink_Class.biolink_class_id = List_Element.biolink_class_id
    join List_Element_Identifier on List_Element_Identifier.list_element_id = List_Element.list_element_id
    join Curie_Prefix on Curie_Prefix.prefix_id = List_Element_Identifier.prefix_id
    where biolink_class = 'Gene';


--> data/translator/rephub/latest/RepurposingHub.sqlite >>> data/nn/RepHub-gene-id.tsv

    select feature_xref from feature as gene_id
    where feature_type = 'target' and feature_xref like 'HGNC%';

