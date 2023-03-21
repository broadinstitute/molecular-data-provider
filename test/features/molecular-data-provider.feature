Feature: Check MolePro

    Background: Specify Molecular Data Provider API
        Given a Molecular Data Provider at "https://molepro.test.transltr.io/molecular_data_provider"


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
        | name  | value                   |
        | genes | GPX4                    |
        | genes | NCBIgene:6790           |
        | genes | HGNC:2243               |
        | genes | ENSEMBL:ENSG00000183044 |
        then the length of the collection should be 4
        and the value of "element_class" should be "gene"
        and the value of "source" should be "HGNC gene-list producer"
        and the value of "elements[0].id" should be "HGNC:4556"
        and the value of "elements[1].id" should be "HGNC:11393"
        and the value of "elements[2].identifiers.entrez" should be "NCBIGene:22818"
        and the value of "elements[3].id" should be "HGNC:23"


    Scenario: Check PubChem producer
        Given the Molecular Data Provider
        when we call "Pubchem compound-list producer" transformer with the following parameters:
        | name     | value     |
        | compound | aspirin   |
        | compound | ibuprofen |
        | compound | ML210     |
        then the length of the collection should be 3
        and the value of "element_class" should be "compound"
        and the value of "source" should be "Pubchem compound-list producer"


    Scenario: Check CMAP compound-to-gene transformer
        Given the Molecular Data Provider
        when we call "Pubchem compound-list producer" transformer with the following parameters:
        | name     | value     |
        | compound | aspirin   |
        | compound | ibuprofen |
        | compound | ML210     |
        and we call "CMAP compound-to-gene transformer" transformer with the following parameters:
        | score threshold | maximum number |
        | 99.5            | 0              |
        then the length of the collection should be 86
        and the value of "element_class" should be "gene"
        and the value of "source" should be "CMAP compound-to-gene transformer"


    Scenario: Check ChEMBL indications transformer
        Given the Molecular Data Provider
        when we call "Pubchem compound-list producer" transformer with the following parameters:
        | compound |
        | aspirin  |
        and we call "ChEMBL indication transformer" transformer with no parameters
        then the length of the collection should be 142
        and the value of "element_class" should be "disease"
        and the value of "source" should be "ChEMBL indication transformer"


    Scenario: Check ChEMBL compound-list producer
        Given the Molecular Data Provider
        when we call "ChEMBL compound-list producer" transformer with the following parameters:
        | compound |
        | aspirin  |
        and we call "CMAP compound-to-gene transformer" transformer with the following parameters:
        | score threshold | maximum number |
        | 99.5            | 0              |
        then the length of the collection should be 11
        and the value of "element_class" should be "gene"
        and the value of "source" should be "CMAP compound-to-gene transformer"


    Scenario: Check ChEMBL targets transformer
        Given the Molecular Data Provider
        when we call "ChEMBL compound-list producer" transformer with the following parameters:
        | compound |
        | aspirin  |
        and we call "ChEMBL gene target transformer" transformer with no parameters
        and we call "CMAP gene-to-gene expander" transformer with the following parameters:
        | score threshold | maximum number |
        | 99.0            | 2              |
        then the length of the collection should be 3
        and the value of "element_class" should be "gene"
        and the value of "source" should be "CMAP gene-to-gene expander"


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
        | name     | value     |
        | compound | aspirin   |
        | compound | ibuprofen |
        | compound | ML210     |
        and we call "CMAP compound-to-compound expander" transformer with the following parameters:
        | score threshold | maximum number |
        | 99.5            | 0              |
        then the length of the collection should be 60
        and the value of "element_class" should be "compound"
        and the value of "source" should be "CMAP compound-to-compound expander"


    Scenario: Check STITCH transformer
        Given the Molecular Data Provider
        when we call "STITCH compound-list producer" transformer with the following parameters:
        | compounds          |
        | bortezomib;aspirin |
        and we call "STITCH link transformer" transformer with the following parameters:
        | score_threshold | limit |
        | 700             | 10    |
        then the length of the collection should be 19
        and the value of "element_class" should be "protein"
        and the value of "source" should be "STITCH link transformer"


    Scenario: Check Repurposing Hub targets transformer
        Given the Molecular Data Provider
        when we call "Repurposing Hub compound-list producer" transformer with the following parameters:
        | compounds                                                             |
        | aspirin; bortezomib;GXJABQQUPOEUTA-RDJZCZTQSA-N; allopurinol-riboside |
        and we call "Repurposing Hub target transformer" transformer with no parameters
        then the length of the collection should be 41
        and the value of "element_class" should be "gene"
        and the value of "source" should be "Repurposing Hub target transformer"


    Scenario: Check Repurposing Hub indications transformer
        Given the Molecular Data Provider
        when we call "Repurposing Hub compound-list producer" transformer with the following parameters:
        | compounds                                                             |
        | aspirin; bortezomib;GXJABQQUPOEUTA-RDJZCZTQSA-N; allopurinol-riboside |
        and we call "Repurposing Hub indication transformer" transformer with no parameters
        then the length of the collection should be 6
        and the value of "element_class" should be "DiseaseOrPhenotypicFeature"
        and the value of "source" should be "Repurposing Hub indication transformer"


    Scenario: Check union
        Given the Molecular Data Provider
        and a compound list "aspirin;ibuprofen;acetaminophen"
        and another compound list "aspirin;ibuprofen;naproxen"
        when we call aggregator "union"
        then the value of "source" should be "union"
        and the length of the collection should be 8
        and the value of "element_class" should be "compound"


    Scenario: Check intersection
        Given the Molecular Data Provider
        and a compound list "aspirin;ibuprofen;acetaminophen"
        and another compound list "aspirin;ibuprofen;naproxen"
        when we call aggregator "intersection"
        then the value of "source" should be "intersection"
        and the length of the collection should be 4
        and the value of "element_class" should be "compound"


    Scenario: Check difference
        Given the Molecular Data Provider
        and a compound list "aspirin;ibuprofen;acetaminophen"
        and another compound list "aspirin;ibuprofen;naproxen"
        when we call aggregator "difference"
        then the value of "source" should be "difference"
        and the length of the collection should be 2
        and the value of "element_class" should be "compound"


    Scenario: Check symmetric difference
        Given the Molecular Data Provider
        and a compound list "aspirin;ibuprofen;acetaminophen"
        and another compound list "aspirin;ibuprofen;naproxen"
        when we call aggregator "symmetric difference"
        then the value of "source" should be "symmetric difference"
        and the length of the collection should be 4
        and the value of "element_class" should be "compound"


    Scenario: Check batch compound list by id
        Given the Molecular Data Provider
        when we fire "/compound/by_id" query with the following body:
        """
            ["DrugBank:DB01050","CID:2244","ChEMBL:25"]
        """
        then the size of "attributes" should be 1
        and the int value of "size" should be 2
