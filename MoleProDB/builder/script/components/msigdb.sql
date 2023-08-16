--> data/translator/msigdb/ver-7.4/MSigDB.sqlite >>> data/msigdb/MSigDB-gene-id.tsv

    select distinct 'NCBIGene:' || MEMBERS_3 as id
    from MEMBER
    where MEMBERS_3 is not null;

