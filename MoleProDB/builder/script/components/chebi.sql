--> data/translator/chebi/latest/chebi.sqlite >>> data/chebi/ChEBI-inchikey.tsv

    select distinct structure 
    from compounds
    join structures on (structures.compound_id = compounds.id and structures.type = 'InChIKey')
    where status != 'O' and status != 'D' and status != 'F' ;

--> data/translator/chebi/latest/chebi.sqlite >>> data/chebi/ChEBI-no-struct-id.tsv

    select distinct chebi_accession
    from compounds
    left join structures on (structures.compound_id = compounds.id and structures.type = 'InChIKey')
    where parent_id is null and structure is null
    and status != 'O' and status != 'D' and status != 'F' ;
