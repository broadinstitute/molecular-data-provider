--> data/translator/rephub/latest/RepurposingHub.sqlite >>> data/rephub/RepHub-inchikey.tsv

    select distinct INCHIKEY from SAMPLE;


--> data/translator/rephub/latest/RepurposingHub.sqlite >>> data/rephub/RepHub-disease-id.tsv

    select FEATURE_XREF
    from feature 
    where feature_type = 'indication';

