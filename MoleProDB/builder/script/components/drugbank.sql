--> data/translator/drugbank/latest/DrugBank.sqlite >>> data/drugbank/DrugBank-compound-id.tsv

    select distinct 'DrugBank:'|| DRUG_BANK_ID as id
    from DRUG
    where DRUG_TYPE = 'small molecule';

--> data/translator/drugbank/latest/DrugBank.sqlite >>> data/drugbank/DrugBank-id.tsv

    select distinct 'DrugBank:'|| DRUG_BANK_ID as id
    from DRUG;

