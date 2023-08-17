--> data/translator/drugcentral/latest/DrugCentral.sqlite >>> data/drugcentral/DrugCentral-ID.tsv

    select 'DrugCentral:'||DRUG_CENTRAL_ID as id from DRUG;

--> data/translator/drugcentral/latest/DrugCentral.sqlite >>> data/drugcentral/DrugCentral-SNOMED.tsv

    select distinct 'SNOMEDCT:'||SNOMEDCT_CUI as id 
    from disease 
    where SNOMEDCT_CUI is not null;
