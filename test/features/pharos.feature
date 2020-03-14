Feature: Check Pharos transformer

    Background: Specify transformer API
        Given a transformer at "https://translator.broadinstitute.org/pharos"


    Scenario: Check Pharos producer info
        Given the transformer
        when we fire "/transformer_info" query
        then the value of "name" should be "Pharos transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the size of "parameters" should be 0


    Scenario: Check Pharos compound-list producer
        Given the transformer
        when we fire "/transform" query with the following body:
        """
        {
            "controls": [],
            "compounds": [
                {
                    "compound_id": "CID:2244",
                    "identifiers": {
                        "pubchem": "CID:2244"
                    }
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "gene_id"
            | gene_id        |
            | NCBIGene:5743  |
            | NCBIGene:5742  |
        and the response only contains the following entries in "gene_id"
            | gene_id                         |
            | NCBIGene:5743  |
            | NCBIGene:5742  |
        and the response contains the following entries in "source" of "attributes" array
            | source             |
            | Pharos transformer |
        and the response only contains the following entries in "source" of "attributes" array
            | source             |
            | Pharos transformer |
