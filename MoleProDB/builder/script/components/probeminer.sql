--> data/translator/probeminer/latest/probeminer.sqlite >>> data/probeminer/probe-miner-id.tsv

    select distinct inchi_key
    from chemicals
    where inchi_key is not null;


--> data/translator/probeminer/latest/probeminer.sqlite >>> data/probeminer/probe-miner-uniprot-id.tsv

    select distinct 'UniProtKB:'||UNIPROT_ACCESSION as id 
    from proteins;

