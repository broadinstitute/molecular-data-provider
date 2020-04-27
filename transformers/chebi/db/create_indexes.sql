create index compounds_chebi_idx on compounds(chebi_accession);
create index compounds_name_idx on compounds(name);
create index chemical_data_compound_id_idx on chemical_data(compound_id);
create index comments_compound_id_idx on comments(compound_id);
create index database_accession_compound_id_idx on database_accession(compound_id);
create index names_compound_id_idx on names(compound_id);
create index names_name_idx on names(name);
create index reference_compound_id_idx on reference(compound_id);
create index relation_init_id_idx on relation(init_id);
create index relation_final_id_idx on relation(final_id);
create index structures_compound_id_idx on structures(compound_id);
create index structures_structure_idx on structures(structure);
create index compound_origins_id_idx on compound_origins(compound_id);

