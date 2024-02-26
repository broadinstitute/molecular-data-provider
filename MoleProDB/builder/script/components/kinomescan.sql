--> data/translator/kinomescan/2018-01-18/KinomeScan.sqlite >>> data/kinomescan/KinomeScan-inchikey.tsv

    select distinct INCHI_KEY as id 
    from SMALL_MOLECULE 
    where INCHI_KEY is not null;


