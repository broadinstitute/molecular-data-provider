--> data/translator/pharos-tcrd/latest/Pharos.sqlite >>> data/pharos/Pharos-CID.tsv

    select distinct 'CID:'||cmpd_pubchem_cid as id 
    from cmpd_activity 
    where cmpd_pubchem_cid is not null;


--> data/translator/pharos-tcrd/latest/Pharos.sqlite >>> data/pharos/Pharos-ChEMBL_ID.tsv

    select distinct 'ChEMBL:'||cmpd_chemblid as ChEMBL_ID 
    from drug_activity 
    where cmpd_chemblid is not null
    union
    select distinct 'ChEMBL:'||cmpd_id_in_src as ChEMBL_ID 
    from cmpd_activity 
    where cmpd_activity.cmpd_id_in_src like 'CHEMBL%';


--> data/translator/pharos-tcrd/latest/Pharos.sqlite >>> data/pharos/Pharos-ChEMBL_ID-only.tsv

    select distinct 'ChEMBL:'||cmpd_chemblid as ChEMBL_ID 
    from drug_activity 
    where cmpd_chemblid is not null 
    and cmpd_pubchem_cid is null
    union
    select distinct 'ChEMBL:'||cmpd_id_in_src as ChEMBL_ID 
    from cmpd_activity 
    where cmpd_activity.cmpd_id_in_src like 'CHEMBL%' 
    and cmpd_pubchem_cid is null;
