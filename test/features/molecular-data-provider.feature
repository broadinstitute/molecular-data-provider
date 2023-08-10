Feature: Check MolePro

    Background: Specify Molecular Data Provider API
        Given a Molecular Data Provider at "https://molepro.ci.transltr.io/molecular_data_provider"


    Scenario: Check transformers
        Given the Molecular Data Provider
        when we fire "/transformers" query
        then the response contains the following entries in "status":
            | status |
            | online |
        and the response only contains the following entries in "status":
            | status |
            | online |


    Scenario: Check get compound by id
        Given the Molecular Data Provider
        when we fire "/compound/by_id/CHEBI:52717" query
        then the value of "id" should be "CID:387447"


    Scenario: Check get element by id
        Given the Molecular Data Provider
        when we fire "/element/by_id/CHEBI:52717" query
        then the value of "elements[0].id" should be "CID:387447"


    Scenario: Check get compound by name
        Given the Molecular Data Provider
        when we fire "/compound/by_name/bortezomib" query
        then the length of the collection should be 1
        and the value of "elements[0].id" should be "CID:387447"


    Scenario: Check get element by name
        Given the Molecular Data Provider
        when we fire "/element/by_name/bortezomib" query
        then the length of the collection should be 1
        and the value of "elements[0].id" should be "CID:387447"


    Scenario: Check HGNC producer
        Given the Molecular Data Provider
        when we call "HGNC gene-list producer" transformer with the following parameters:
        | name | value                   |
        | gene | GPX4                    |
        | gene | NCBIgene:6790           |
        | gene | HGNC:2243               |
        | gene | ENSEMBL:ENSG00000183044 |
        then the length of the collection should be 4
        and the value of "element_class" should be "gene"
        and the value of "source" should be "HGNC gene-list producer"
        and the value of "elements[0].id" should be "NCBIGene:2879"
        and the value of "elements[1].id" should be "NCBIGene:6790"
        and the value of "elements[2].id" should be "NCBIGene:22818"
        and the value of "elements[3].id" should be "NCBIGene:18"


    Scenario: Check MoleProDB name producer
        Given the Molecular Data Provider
        when we call "MoleProDB name producer" transformer with the following parameters:
        | name | value                   |
        | name | GPX4                    |
        then the length of the collection should be 1
        and the value of "element_class" should be "any"
        and the value of "source" should be "MoleProDB name producer"
        and the value of "elements[0].id" should be "NCBIGene:2879"



    Scenario: Check MoleProDB node producer
        Given the Molecular Data Provider
        when we call "MoleProDB node producer" transformer with the following parameters:
        | name | value                   |
        | id   | NCBIgene:6790           |
        | id   | HGNC:2243               |
        | id   | ENSEMBL:ENSG00000183044 |
        then the length of the collection should be 3
        and the value of "element_class" should be "any"
        and the value of "source" should be "MoleProDB node producer"
        and the value of "elements[0].id" should be "NCBIGene:6790"
        and the value of "elements[1].id" should be "NCBIGene:22818"
        and the value of "elements[2].id" should be "NCBIGene:18"


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
        when we call "MoleProDB name producer" transformer with the following parameters:
        | name  |
        | FGFR1 |
        and we call "DGIdb inhibitor transformer" transformer with no parameters
        and we call "CMAP compound-to-gene transformer" transformer with the following parameters:
        | score threshold | maximum number |
        | 99.0            | 2              |
        then the length of the collection should be 20
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


    Scenario: Check batch compound list by id
        Given the Molecular Data Provider
        when we fire "/compound/by_id" query with the following body:
        """
            ["DrugBank:DB01050","CID:2244","ChEMBL:25"]
        """
        then the size of "attributes" should be 1
        and the int value of "size" should be 2


    Scenario: Check batch compound list by name
        Given the Molecular Data Provider
        when we fire "/compound/by_name" query with the following body:
        """
            ["aspirin","bortezomib","Velcade","ibuprofen"]
        """
        then the size of "attributes" should be 4
        and the int value of "size" should be 4


    Scenario: Check batch element list by id
        Given the Molecular Data Provider
        when we fire "/element/by_id" query with the following body:
        """
            ["DrugBank:DB01050","CID:2244","ChEMBL:25"]
        """
        then the size of "attributes" should be 1
        and the int value of "size" should be 2


    Scenario: Check batch element list by name
        Given the Molecular Data Provider
        when we fire "/element/by_name" query with the following body:
        """
            ["aspirin","bortezomib","Velcade","ibuprofen"]
        """
        then the size of "attributes" should be 0
        and the int value of "size" should be 7
