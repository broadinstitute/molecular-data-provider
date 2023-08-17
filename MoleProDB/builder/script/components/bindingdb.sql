--> data/translator/bindingdb/latest/BindingDB.sqlite >>> data/bindingdb/BindingDB-ID-inchikey.tsv

    select 'BINDINGDB:' || Ligand_ID || X'09' || InChi_Key 
    from LIGAND 
    where InChi_Key is not null;
