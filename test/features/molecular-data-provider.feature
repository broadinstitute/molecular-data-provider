Feature: Check CMAP transformer

    Background: Specify Molecular Data Provider API
        Given a Molecular Data Provider at "https://translator.broadinstitute.org/molecular_data_provider"


    Scenario: Check transformers
        Given the Molecular Data Provider
        when we fire "/transformers" query
        then the response contains the following entries in "status":
            | status |
            | online |
        and the response only contains the following entries in "status":
            | status |
            | online |


    Scenario: Check HGNC producer
        Given the Molecular Data Provider
        when we call "HGNC gene-list producer" transformer with the following parameters:
        | genes                 |
        | GPX4;NCBIgene:6790;HGNC:2243;ENSEMBL:ENSG00000183044 |
        then the length of the collection should be 4
        and the value of "element_class" should be "gene"
        and the value of "source" should be "HGNC gene-list producer"
        and the value of "elements[0].gene_id" should be "HGNC:4556"
        and the value of "elements[1].gene_id" should be "HGNC:11393"
        and the value of "elements[2].identifiers.entrez" should be "NCBIGene:22818"
        and the value of "elements[3].gene_id" should be "HGNC:23"

    Scenario: Check PubChem producer
        Given the Molecular Data Provider
        when we call "Pubchem compound-list producer" transformer with the following parameters:
        | compounds                 |
        | aspirin; ibuprofen; ML210 |
        then the length of the collection should be 3
        and the value of "element_class" should be "compound"
        and the value of "source" should be "Pubchem compound-list producer"


    Scenario: Check CMAP compound-to-gene transformer
        Given the Molecular Data Provider
        when we call "Pubchem compound-list producer" transformer with the following parameters:
        | compounds                 |
        | aspirin; ibuprofen; ML210 |
        and we call "CMAP compound-to-gene transformer" transformer with the following parameters:
        | score threshold | maximum number |
        | 99.5            | 0              |
        then the length of the collection should be 86
        and the value of "element_class" should be "gene"
        and the value of "source" should be "CMAP compound-to-gene transformer"


    Scenario: Check ChEMBL indications transformer
        Given the Molecular Data Provider
        when we call "Pubchem compound-list producer" transformer with the following parameters:
        | compounds |
        | aspirin   |
        and we call "ChEMBL indication transformer" transformer with no parameters
        then the length of the collection should be 108
        and the value of "element_class" should be "disease"
        and the value of "source" should be "ChEMBL indication transformer"


    Scenario: Check ChEMBL compound-list producer
        Given the Molecular Data Provider
        when we call "ChEMBL compound-list producer" transformer with the following parameters:
        | compounds |
        | aspirin   |
        and we call "CMAP compound-to-gene transformer" transformer with the following parameters:
        | score threshold | maximum number |
        | 99.5            | 0              |
        then the length of the collection should be 11
        and the value of "element_class" should be "gene"
        and the value of "source" should be "CMAP compound-to-gene transformer"


    Scenario: Check ChEMBL targets transformer
        Given the Molecular Data Provider
        when we call "ChEMBL compound-list producer" transformer with the following parameters:
        | compounds |
        | aspirin   |
        and we call "ChEMBL target transformer" transformer with no parameters
        and we call "CMAP gene-to-gene expander" transformer with the following parameters:
        | score threshold | maximum number |
        | 99.0            | 2              |
        then the length of the collection should be 3
        and the value of "element_class" should be "gene"
        and the value of "source" should be "CMAP gene-to-gene expander"

        @wip
    Scenario: Check DGIdb inhibitors transformer
        Given the Molecular Data Provider
        when we call "HGNC gene-list producer" transformer with the following parameters:
        | genes |
        | FGFR1 |
        and we call "DGIdb inhibitor transformer" transformer with no parameters
        and we call "CMAP compound-to-gene transformer" transformer with the following parameters:
        | score threshold | maximum number |
        | 99.0            | 2              |
        then the length of the collection should be 23
        and the value of "element_class" should be "gene"
        and the value of "source" should be "CMAP compound-to-gene transformer"


    Scenario: Check CMAP compound-to-compound transformer
        Given the Molecular Data Provider
        when we call "Pubchem compound-list producer" transformer with the following parameters:
        | compounds                 |
        | aspirin; ibuprofen; ML210 |
        and we call "CMAP compound-to-compound expander" transformer with the following parameters:
        | score threshold | maximum number |
        | 99.5            | 0              |
        then the length of the collection should be 60
        and the value of "element_class" should be "compound"
        and the value of "source" should be "CMAP compound-to-compound expander"


    Scenario: Check union
        Given the Molecular Data Provider
        and a compound list "aspirin;ibuprofen;acetaminophen"
        and another compound list "aspirin;ibuprofen;naproxen"
        when we call aggregator "union"
        then the value of "source" should be "union"
        and the length of the collection should be 4
        and the value of "element_class" should be "compound"


    Scenario: Check intersection
        Given the Molecular Data Provider
        and a compound list "aspirin;ibuprofen;acetaminophen"
        and another compound list "aspirin;ibuprofen;naproxen"
        when we call aggregator "intersection"
        then the value of "source" should be "intersection"
        and the length of the collection should be 2
        and the value of "element_class" should be "compound"


    Scenario: Check difference
        Given the Molecular Data Provider
        and a compound list "aspirin;ibuprofen;acetaminophen"
        and another compound list "aspirin;ibuprofen;naproxen"
        when we call aggregator "difference"
        then the value of "source" should be "difference"
        and the length of the collection should be 1
        and the value of "element_class" should be "compound"


    Scenario: Check symmetric difference
        Given the Molecular Data Provider
        and a compound list "aspirin;ibuprofen;acetaminophen"
        and another compound list "aspirin;ibuprofen;naproxen"
        when we call aggregator "symmetric difference"
        then the value of "source" should be "symmetric difference"
        and the length of the collection should be 2
        and the value of "element_class" should be "compound"

