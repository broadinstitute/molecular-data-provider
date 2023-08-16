--> data/translator/chembl/chembl_30/chembl_30.db >>> data/chembl/ChEMBL-ID.tsv

    select distinct 'ChEMBL:'||chembl_id as id from (
    select distinct molecule_dictionary.chembl_id, molecule_dictionary.pref_name 
    from molecule_dictionary 
    join compound_records on compound_records.molregno = molecule_dictionary.molregno 
    join metabolism on metabolism.drug_record_id = compound_records.record_id 
    union 
    select distinct molecule_dictionary.chembl_id, molecule_dictionary.pref_name 
    from molecule_dictionary 
    join compound_records on compound_records.molregno = molecule_dictionary.molregno 
    join metabolism on metabolism.substrate_record_id = compound_records.record_id 
    union 
    select distinct molecule_dictionary.chembl_id, molecule_dictionary.pref_name 
    from molecule_dictionary 
    join compound_records on compound_records.molregno = molecule_dictionary.molregno 
    join metabolism on metabolism.metabolite_record_id = compound_records.record_id 
    union 
    select distinct molecule_dictionary.chembl_id, molecule_dictionary.pref_name 
    from molecule_dictionary 
    join drug_mechanism on drug_mechanism.molregno = molecule_dictionary.molregno 
    union 
    select distinct molecule_dictionary.chembl_id, molecule_dictionary.pref_name 
    from molecule_dictionary 
    JOIN drug_warning ON molecule_dictionary.molregno = drug_warning.molregno 
    union 
    select distinct molecule_dictionary.chembl_id, molecule_dictionary.pref_name 
    from molecule_dictionary 
    JOIN molecule_atc_classification ON molecule_atc_classification.molregno=molecule_dictionary.molregno 
    union 
    select distinct molecule_dictionary.chembl_id, molecule_dictionary.pref_name 
    from molecule_dictionary 
    JOIN drug_indication ON drug_indication.molregno=molecule_dictionary.molregno
)
;


--> data/translator/pharos-tcrd/latest/Pharos.sqlite >>> data/chembl/Pharos-ChEMBL_ID.tsv

    select distinct 'ChEMBL:'||cmpd_chemblid as id 
    from drug_activity where cmpd_chemblid is not null
    union
    select distinct 'ChEMBL:'||cmpd_id_in_src as id 
    from cmpd_activity where cmpd_activity.cmpd_id_in_src like 'CHEMBL%';


--> data/translator/chembl/chembl_30/chembl_30.db >>> data/chembl/ChEMBL-disease-id.tsv

    select distinct 'MESH:'||mesh_id as id from drug_indication;


--> data/translator/chembl/chembl_30/ChEMBL.target.xref.sqlite >>> data/chembl/ChEMBL-gene-id.tsv

    select 'ENSEMBL:' || xref_id as id
    from component_xref 
    where xref_src_db = 'EnsemblGene';


--> data/translator/chebi/latest/ChEBI.sqlite >>> data/chembl/ChEBI-inchikey.tsv

    select distinct structure as inchikey from structures where structures.type = 'InChIKey';


--> data/translator/chembank/ChemBank.sqlite >>> data/chembl/ChemBank-inchikey.tsv

    select distinct INCHI_KEY as inchikey from COMPOUND;

--> data/translator/drugbank/ver-5.1.8/DrugBank.sqlite >>> data/chembl/DrugBank-inchikey.tsv

    select distinct identifier as inchikey from drug_identifier
    join resource on (resource.RESOURCE_ID = drug_identifier.RESOURCE_ID)
    where resource = 'InChIKey';


--> data/translator/drugcentral/latest/DrugCentral.sqlite >>> data/chembl/DrugCentral-inchikey.tsv

    select INCHI_KEY as inchikey from DRUG;


--> data/translator/gtopdb/GtoPdb.db >>> data/chembl/GtoPdb-inchikey.tsv

    select distinct inchikey from ligand where inchikey != '';


--> data/translator/hmdb/latest/HMDB.sqlite >>> data/chembl/HMDB-inchikey.tsv

    select XREF as inchikey 
    from IDENTIFIER join TAG on TAG.TAG_ID = IDENTIFIER.TAG_ID 
    where TAG = 'inchikey';


--> data/translator/probeminer/latest/probeminer.sqlite >>> data/chembl/ProbeMiner-inchikey.tsv

    select distinct inchi_key as inchikey
    from chemicals
    where inchi_key is not null;


--> data/translator/pubchem/latest/PubChem.sqlite >>> data/chembl/PubChem-inchikey.tsv

    select distinct STANDARD_INCHIKEY as inchikey
    from COMPOUND
    where STANDARD_INCHIKEY is not null;


--> data/translator/rephub/latest/RepurposingHub.sqlite >>> data/chembl/RepHub-inchikey.tsv

    select INCHIKEY as inchikey from SAMPLE;


--> data/translator/rxnorm/latest/rxnorm.sqlite >>> data/chembl/UNII-inchikey.tsv

    select distinct INCHIKEY as inchikey from UNII where INCHIKEY != '';
