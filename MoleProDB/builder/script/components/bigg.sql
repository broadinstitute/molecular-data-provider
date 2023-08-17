--> data/translator/BiGG_model/latest/BiGG.sqlite >>> data/bigg/BiGG-metabolite_id.tsv

    SELECT DISTINCT 'BIGG.METABOLITE:'|| metabolite_bigg_id AS id
    FROM metabolite;

--> data/translator/BiGG_model/latest/BiGG.sqlite >>> data/bigg/BiGG-inchikey.tsv

    SELECT DISTINCT db_id AS id
    FROM metabolite_db 
    WHERE metabolite_db."database" = 'InChI Key';

--> data/translator/BiGG_model/latest/BiGG.sqlite >>> data/bigg/BiGG-entrez.tsv

    SELECT DISTINCT db_id AS id
    FROM gene_db 
    WHERE gene_db."database" = 'NCBI Entrez Gene';
