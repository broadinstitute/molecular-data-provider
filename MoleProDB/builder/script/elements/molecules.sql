--> data/translator/drugbank/ver-5.1.8/DrugBank.sqlite >>> data/nn/DrugBank-molecule-id.tsv

    select distinct 'DrugBank:'|| DRUG_BANK_ID as DRUG_BANK_ID from DRUG;


--> data/translator/chembl/chembl_30/chembl_30.db >>> data/nn/ChEMBL-molecule-id.tsv

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
    );


--> data/translator/chebi/latest/chebi.sqlite >>> data/nn/ChEBI-no-struct-id.tsv

    select distinct chebi_accession
    from compounds
    left join structures on (structures.compound_id = compounds.id and structures.type = 'InChIKey')
    where parent_id is null and structure is null
    and status != 'O' and status != 'D' and status != 'F' ;
