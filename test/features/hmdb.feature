Feature: Check HMDB transformer

    Background: Specify transformer API
        Given a transformer at "https://translator.broadinstitute.org/hmdb"


    Scenario: Check HMDB producer info
        Given the transformer
        when we fire "/targets/transformer_info" query
        then the value of "name" should be "HMDB target transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the size of "parameters" should be 0


    Scenario: Check HMDB aspirin targets
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "compounds": [
                {
                    "compound_id": "CID:2244",
                    "identifiers": {
                        "drugbank": "DrugBank:DB00945"
                    }
                }
            ]
        }
        """
        then the size of the response is 9
        and the response contains the following entries in "gene_id"
            | gene_id        |
            | NCBIGene:1645  |
            | NCBIGene:5743  |
            | NCBIGene:5742  |
            | NCBIGene:1559  |
            | NCBIGene:1557  |
            | NCBIGene:1558  |
            | NCBIGene:5243  |
            | NCBIGene:9356  |
            | NCBIGene:10864 |
        and the response only contains the following entries in "gene_id"
            | gene_id                         |
            | NCBIGene:1645  |
            | NCBIGene:5743  |
            | NCBIGene:5742  |
            | NCBIGene:1559  |
            | NCBIGene:1557  |
            | NCBIGene:1558  |
            | NCBIGene:5243  |
            | NCBIGene:9356  |
            | NCBIGene:10864 |
        and the response contains the following entries in "source" of "attributes" array
            | source                  |
            | HMDB target transformer |
        and the response only contains the following entries in "source" of "attributes" array
            | source                  |
            | HMDB target transformer |


    Scenario: Check HMDB target producer
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "compounds": [
                {
                    "compound_id": "CID:28694",
                    "identifiers": {
                        "drugbank": "DrugBank:DB09130"
                    }
                }
            ]
        }
        """
        then the size of the response is 49
        and the response contains the following entries in "source" of "attributes" array
            | source                  |
            | HMDB target transformer |
        and the response only contains the following entries in "source" of "attributes" array
            | source                  |
            | HMDB target transformer |
