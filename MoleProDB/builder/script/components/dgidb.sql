--> data/translator/dgidb/DGIdb.db >>> data/dgidb/DGIdb-chembl-id.tsv

    select distinct 'ChEMBL:'||chembl_id as id from drugs;


--> data/translator/dgidb/DGIdb.db >>> data/dgidb/DGIdb-name.tsv

    select distinct name from drugs;
