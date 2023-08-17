--> data/translator/pharmgkb/pharmgkb.sqlite >>> data/pharmgkb/PharmGKB-CID.tsv

    select distinct 'CID:' || xref as id
    from chemical
    left join identifier on (identifier.PharmGKB_Accession_Id = chemical.PharmGKB_Accession_Id and identifier.Prefix = 'PubChem Compound')
    where xref is not null;


--> data/translator/pharmgkb/pharmgkb.sqlite >>> data/pharmgkb/PharmGKB-ID-noinchi.tsv

    select chemical.PharmGKB_Accession_ID
    from chemical
    left join identifier on (identifier.PharmGKB_Accession_Id = chemical.PharmGKB_Accession_Id and identifier.Prefix = 'InChI')
    where xref is null;


--> data/translator/pharmgkb/pharmgkb.sqlite >>> data/pharmgkb/PharmGKB-ID.tsv

    select 'PHARMGKB.CHEMICAL:' || chemical.PharmGKB_Accession_ID as id
    from chemical;
