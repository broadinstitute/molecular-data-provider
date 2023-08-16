--> data/translator/sider/4.1/sider.sqlite >>> data/sider/SIDER-CID.tsv

select 'CID:' || CAST(substr(cid_stereo,4) as integer) as id from drug;


--> data/translator/sider/4.1/sider.sqlite >>> data/sider/SIDER-UMLS.tsv

select 'UMLS:' || umls_id as id from umls;
