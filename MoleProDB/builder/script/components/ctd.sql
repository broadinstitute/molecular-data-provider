--> data/translator/ctd/latest/CTD.sqlite >>> data/ctd/CTD-chem-CID.tsv

    select distinct PubChem_CID as id
    from chemicals_w_PubchemCID
    where PubChem_CID is not null;

--> data/translator/ctd/latest/CTD.sqlite >>> data/ctd/CTD-chem-MeSH-ID.tsv

    select distinct 'MESH:' || ChemicalID as id
    from chem_gene_ixns_w_axn_info
    union
    select distinct 'MESH:' || ChemicalID as id
    from chem_go_enriched
    union
    select distinct 'MESH:' || ChemicalID as id
    from chem_pathways_enriched
    union
    select distinct 'MESH:' || ChemicalID as id
    from chemicals_diseases
    union
    select distinct 'MESH:' || ChemicalID as id
    from pheno_term_ixns;


--> data/translator/ctd/latest/CTD.sqlite >>> data/ctd/CTD-gene-int-ID.tsv

    select 'MESH:' || ChemicalID as id from (
    select ChemicalID , count(distinct GeneId) as count from chem_gene_ixns_w_axn_info
    group by ChemicalID
    having count <= 500
    order by count desc
    );

--> data/translator/ctd/latest/CTD.sqlite >>> data/ctd/CTD-gene-ID.tsv

    select distinct 'NCBIGene:'||GeneID as GeneID
    from chem_gene_ixns_w_axn_info;

--> data/translator/ctd/latest/CTD.sqlite >>> data/ctd/CTD-disease-ID.tsv

    select distinct DiseaseID
    from chemicals_diseases
    where DiseaseID != 'OMIM:603855' and DiseaseID != 'MESH:C565865';
