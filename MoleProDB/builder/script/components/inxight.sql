--> data/translator/inxight-drugs/latest/Inxight_Drugs.sqlite >>> data/inxight/InxightDrugs-UNII-chem.tsv

    select distinct 'UNII:' || substances.UNII AS id 
    from substances
    join unii_lookup ON substances.UNII = unii_lookup.UNII
    where INCHIKEY is not null and INCHIKEY != '';


--> data/translator/inxight-drugs/latest/Inxight_Drugs.sqlite >>> data/inxight/InxightDrugs-UNII.tsv

    select distinct 'UNII:' || substances.UNII AS id 
    from substances
    join unii_lookup ON substances.UNII = unii_lookup.UNII
    where INCHIKEY is null or INCHIKEY = '';

