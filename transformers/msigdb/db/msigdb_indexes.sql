CREATE INDEX gene_symbol_index ON gene_set_gene_symbol (
    gene_symbol_id
);

CREATE INDEX gene_set_index ON gene_set_gene_symbol (
    gene_set_id
);

CREATE INDEX version_name_index ON MSigDB (
    version_name
);

CREATE INDEX publication_id_index ON publication_author (
    publication_id
);
