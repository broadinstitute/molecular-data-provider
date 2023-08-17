--> data/translator/stitch/STITCH.sqlite >>> data/stitch/STITCH-CID.tsv

    select distinct 'CID:'||cast(substr(chemical, 5) AS INTEGER) as CID 
    from protein_chemical_links_transfer;


--> data/translator/stitch/STITCH.sqlite >>> data/stitch/STITCH-ensembl.tsv

    select distinct 'ENSEMBL:' || substr(protein, 6) as  id 
    from protein_chemical_links_transfer;
