--> data/translator/chembl/chembl_30/chembl_30.db >>> data/nn/ChEMBL-protein-id.tsv

    select distinct 'UniProtKB:' || accession as id
    from component_sequences
    where component_type = 'PROTEIN';


--> data/translator/drugbank/ver-5.1.8/DrugBank.sqlite >>> data/nn/DrugBank-protein-id.tsv

    select distinct 'UniProtKB:' || POLYPEPTIDE_IDENTIFIER as id
    from POLYPEPTIDE;


--> data/translator/hmdb/latest/HMDB.sqlite >>> data/nn/HMDB-uniprot-id.tsv

    select distinct 'UniProtKB:' || UNIPROT_ID as id 
    from PROTEIN;


--> data/translator/stitch/STITCH.sqlite >>> data/nn/STITCH-ensembl.tsv

    select distinct 'ENSEMBL:' || substr(protein, 6) as  protein 
    from protein_chemical_links_transfer;


--> data/translator/probeminer/latest/probeminer.sqlite >>> data/nn/probe-miner-uniprot-id.tsv

    select distinct 'UniProtKB:' || UNIPROT_ACCESSION as id 
    from proteins;



