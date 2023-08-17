--> data/translator/hmdb/latest/HMDB.sqlite >>> data/hmdb/HMDB-id.tsv

    select 'HMDB:' || ACCESSION as id
    from METABOLITE
    order by METABOLITE_ID;


--> data/translator/hmdb/latest/HMDB.sqlite >>> data/hmdb/HMDB-OMIM.tsv

    select 'OMIM:' || OMIM_ID as id
    from DISEASE
    where OMIM_ID is not null
    order by OMIM_ID;
