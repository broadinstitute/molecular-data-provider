--> data/translator/gtopdb/GtoPdb.db >>> data/gtopdb/GtoPdb-id.tsv

    select 'GTOPDB:'||LIGAND_ID from LIGAND where INCHIKEY != '';
