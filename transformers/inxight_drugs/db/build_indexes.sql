CREATE INDEX index_components_on_mixture_id ON components (
    mixture_id
);

CREATE INDEX index_components_on_refuuid ON components (
    refuuid
);

CREATE INDEX index_entity_references_entity_id ON entity_references (
    entity_id
);

CREATE INDEX index_entity_references_reference_id ON entity_references (
    reference_id
);

CREATE INDEX index_names_on_name_nc ON names (
    name COLLATE NOCASE
);

CREATE INDEX index_nucleic_acid_sequences_on_nucleic_acid_id ON nucleic_acid_sequences (
    nucleic_acid_id
);

CREATE INDEX index_nucleic_acids_on_substance_id ON nucleic_acids (
    substance_id
);

CREATE INDEX index_polymers_on_substance_id ON polymers (
    substance_id
);

CREATE INDEX index_protein_sequences_on_protein_id ON protein_sequences (
    protein_id
);

CREATE INDEX index_proteins_on_substance_id ON proteins (
    substance_id
);

CREATE INDEX index_relationships_on_substance_id ON relationships (
    substance_id
);

CREATE INDEX index_relationships_on_related_substance_id ON relationships (
    relatedSubstance_id
);

CREATE INDEX index_structurally_diverse_on_substance_id ON structurallyDiverse (
    substance_id
);

CREATE INDEX index_structures_on_pubchem_nc ON structures (
    pubChem COLLATE NOCASE
);

CREATE INDEX index_structures_on_inchikey_nc ON structures (
    InChIKey COLLATE NOCASE
);

CREATE INDEX index_substance_attributes_on_substance_id ON substance_attributes (
    substance_id
);

CREATE INDEX index_substance_codes_on_substance_id ON substance_codes (
    substance_id
);

CREATE INDEX index_substance_codes_on_code_id ON substance_codes (
    code_id
);

CREATE INDEX index_substance_names_on_substance_id ON substance_names (
    substance_id
);

CREATE INDEX index_substance_names_on_name_id ON substance_names (
    name_id
);

CREATE INDEX index_substance_on_structure_id ON substances (
    structure_id
);

CREATE INDEX index_substances_on_unii ON substances (
    UNII
);

CREATE INDEX index_substances_on_unii_nc ON substances (
    UNII COLLATE NOCASE
);

CREATE INDEX index_substance_on_name_nc ON substances (
    _name COLLATE NOCASE
);

CREATE INDEX index_substances_on_mixture ON substances (
    mixture
);

CREATE INDEX index_unii_lookup_on_rxcui_nc ON unii_lookup (
    RXCUI COLLATE NOCASE
);

CREATE INDEX index_unii_lookup_on_rxcui ON unii_lookup (
    RXCUI
);
