Feature: Check MolePro

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


    Scenario: Check get compound by id
        Given the Molecular Data Provider
        when we fire "/compound/by_id/CID:387447" query
        then the value of "id" should be "CHEBI:52717"


    Scenario: Check get element by id
        Given the Molecular Data Provider
        when we fire "/element/by_id/CHEBI:52717" query
        then the value of "elements[0].id" should be "CHEBI:52717"


    Scenario: Check get compound by name
        Given the Molecular Data Provider
        when we fire "/compound/by_name/bortezomib" query
        then the length of the collection should be 1
        and the value of "elements[0].id" should be "CHEBI:52717"


    Scenario: Check get element by name
        Given the Molecular Data Provider
        when we fire "/element/by_name/bortezomib" query
        then the length of the collection should be 1
        and the value of "elements[0].id" should be "CHEBI:52717"


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
        then the length of the collection should be 60
        and the value of "element_class" should be "gene"
        and the value of "source" should be "CMAP compound-to-gene transformer"


    Scenario: Check ChEMBL indications transformer
        Given the Molecular Data Provider
        when we call "Pubchem compound-list producer" transformer with the following parameters:
        | compound |
        | aspirin  |
        and we call "ChEMBL indication transformer" transformer with no parameters
        then the length of the collection should be 146
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
        then the length of the collection should be 4
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


    Scenario: Check GeLiNEA
        Given the Molecular Data Provider
        when we call "DrugCentral indications transformer" transformer with the following parameters:
        | disease                 |
        | acute lymphoid leukemia |
        and we call "CMAP compound-to-gene transformer" transformer with the following parameters:
        | score threshold | maximum number |
        | 99              | 0              |
        and we call "Gene-list network enrichment analysis" transformer with the following parameters:
        | network          | gene-set collection    | maximum p-value |
        | STRING-human-700 | H - hallmark gene sets | 0.05            |
        then the length of the collection should be 7
        and the value of "element_class" should be "pathway"
        and the value of "source" should be "Gene-list network enrichment analysis"


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


    Scenario: Check Drug Repurposing Hub targets transformer
        Given the Molecular Data Provider
        when we call "Drug Repurposing Hub compound-list producer" transformer with the following parameters:
        | name     | value                       |
        | compound | aspirin                     |
        | compound | bortezomib                  |
        | compound | GXJABQQUPOEUTA-RDJZCZTQSA-N |
        | compound | allopurinol-riboside        |
        and we call "Drug Repurposing Hub target transformer" transformer with no parameters
        then the length of the collection should be 41
        and the value of "element_class" should be "gene"
        and the value of "source" should be "Drug Repurposing Hub target transformer"


    Scenario: Check Drug Repurposing Hub indications transformer
        Given the Molecular Data Provider
        when we call "Drug Repurposing Hub compound-list producer" transformer with the following parameters:
        | name     | value                       |
        | compound | aspirin                     |
        | compound | bortezomib                  |
        | compound | GXJABQQUPOEUTA-RDJZCZTQSA-N |
        | compound | allopurinol-riboside        |
        and we call "Drug Repurposing Hub indication transformer" transformer with no parameters
        then the length of the collection should be 6
        and the value of "element_class" should be "DiseaseOrPhenotypicFeature"
        and the value of "source" should be "Drug Repurposing Hub indication transformer"


    Scenario: Check transformer chain
        Given the Molecular Data Provider
        when we call transformer chain with the following parameters:
        | transformer                       | parameter            | value                               |
        | MoleProDB node producer           | id                   | MONDO:0005247                       |
        | MoleProDB hierarchy transformer   | name_source          | MolePro                             |
        | MoleProDB hierarchy transformer   | element_attribute    | biolink:description                 |
        | MoleProDB connections transformer | biolink_class        | SmallMolecule                       |
        | MoleProDB connections transformer | name_source          | MolePro                             |
        | MoleProDB connections transformer | element_attribute    | biolink:highest_FDA_approval_status |
        | MoleProDB connections transformer | connection_attribute | biolink:primary_knowledge_source    |
        | MoleProDB connections transformer | connection_attribute | biolink:aggregator_knowledge_source |
        then the length of the collection should be 294


    Scenario: Check union
        Given the Molecular Data Provider
        and a compound list "aspirin;bortezomib;acetaminophen"
        and another compound list "aspirin;bortezomib;ibuprofen"
        when we call aggregator "union"
        then the value of "source" should be "union"
        and the length of the collection should be 4
        and the value of "element_class" should be "compound"


    Scenario: Check intersection
        Given the Molecular Data Provider
        and a compound list "aspirin;bortezomib;acetaminophen"
        and another compound list "aspirin;bortezomib;ibuprofen"
        when we call aggregator "intersection"
        then the value of "source" should be "intersection"
        and the length of the collection should be 2
        and the value of "element_class" should be "compound"


    Scenario: Check difference
        Given the Molecular Data Provider
        and a compound list "aspirin;bortezomib;acetaminophen"
        and another compound list "aspirin;bortezomib;ibuprofen"
        when we call aggregator "difference"
        then the value of "source" should be "difference"
        and the length of the collection should be 1
        and the value of "element_class" should be "compound"


    Scenario: Check symmetric difference
        Given the Molecular Data Provider
        and a compound list "aspirin;bortezomib;acetaminophen"
        and another compound list "aspirin;bortezomib;ibuprofen"
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
        and the int value of "size" should be 5
