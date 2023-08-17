--> data/translator/hmdb/latest/HMDB.sqlite >>> data/nn/HMDB-OMIM.tsv

    select 'OMIM:' || OMIM_ID as id
    from DISEASE
    where OMIM_ID is not null
    order by OMIM_ID;


--> data/translator/drugcentral/latest/DrugCentral.sqlite >>> data/nn/DrugCentral-SNOMED.tsv

    select distinct 'SNOMEDCT:'||SNOMEDCT_CUI as id 
    from disease where SNOMEDCT_CUI is not null;


--> data/translator/chembl/chembl_30/chembl_30.db >>> data/nn/ChEMBL-disease-id.tsv

    select distinct 'MESH:'||mesh_id as id from drug_indication;


--> data/translator/ctd/latest/CTD.sqlite >>> data/nn/CTD-disease-id.tsv

    select distinct DiseaseID as id
    from chemicals_diseases
    where DiseaseID != 'OMIM:603855' and DiseaseID != 'MESH:C565865';


--> data/translator/rephub/latest/RepurposingHub.sqlite >>> data/nn/RepHub-disease-id.tsv

    select distinct FEATURE_XREF as id
    from FEATURE 
    where FEATURE_TYPE = 'indication' and FEATURE_XREF is not null;


--> data/translator/sider/4.1/sider.sqlite >>> data/nn/SIDER-UMLS.tsv

    select 'UMLS:' || umls_id as id from umls;

