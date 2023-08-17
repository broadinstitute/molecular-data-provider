--> data/translator/rxnorm/latest/rxnorm.sqlite >>> data/moleprodb/rxnorm/RxNorm-UNII.tsv

    select distinct 'UNII:' || UNII AS id from UNII;


--> data/translator/rxnorm/latest/rxnorm.sqlite >>> data/moleprodb/rxnorm/RxNorm-RXCUI.tsv

    select distinct 'RXCUI:' || RXNCONSO.RXCUI as id
    from RXNCONSO
    left join DRUG_MAP on DRUG_MAP.RXCUI = RXNCONSO.RXCUI
    where PRIMARY_RXCUI is null;


--> data/translator/rxnorm/latest/rxnorm.sqlite >>> data/moleprodb/rxnorm/RxNorm-CID.tsv

    select distinct 'CID:' || PUBCHEM AS id
    from UNII
    where PUBCHEM is not null and PUBCHEM != '';
