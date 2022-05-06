Feature: Check HMDB transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-gtopdb-transformer.test.transltr.io/hmdb"


    Scenario: Check HMDB producer info
        Given the transformer
        when we fire "/metabolites/transformer_info" query
        then the value of "name" should be "HMDB metabolite producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the size of "parameters" should be 1


    Scenario: Check HMDB producer info
        Given the transformer
        when we fire "/targets/transformer_info" query
        then the value of "name" should be "HMDB target transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the size of "parameters" should be 0


    Scenario: Check HMDB producer
        Given the transformer
        when we fire "/metabolites/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compounds",
                    "value": "Velcade; Aspirin; HMDB:HMDB0000012;HMDB:HMDB0100630"
                }
            ]
        }
        """
        then the size of the response is 4
        and the response contains the following entries in "biolink_class"
            | biolink_class     |
            | ChemicalSubstance |
        and the response only contains the following entries in "biolink_class"
            | biolink_class     |
            | ChemicalSubstance |
        and the response contains the following entries in "source" of "attributes" array
            | source |
            | HMDB   |
        and the response only contains the following entries in "source" of "attributes" array
            | source |
            | HMDB   |


    Scenario: Check HMDB aspirin targets
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "CID:2244",
                    "identifiers": {
                        "drugbank": "DrugBank:DB00945"
                    }
                }
            ]
        }
        """
        then the size of the response is 9
        and the response contains the following entries in "id"
            | id             |
            | NCBIGene:1645  |
            | NCBIGene:5743  |
            | NCBIGene:5742  |
            | NCBIGene:1559  |
            | NCBIGene:1557  |
            | NCBIGene:1558  |
            | NCBIGene:5243  |
            | NCBIGene:9356  |
            | NCBIGene:10864 |
        and the response only contains the following entries in "id"
            | id             |
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
            | source |
            | HMDB   |
        and the response only contains the following entries in "source" of "attributes" array
            | source |
            | HMDB   |

    Scenario: Check HMDB target producer
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "CID:28694",
                    "identifiers": {
                        "drugbank": "DrugBank:DB09130"
                    }
                }
            ]
        }
        """
        then the size of the response is 49
        and the response contains the following entries in "source" of "attributes" array
            | source |
            | HMDB   |
        and the response only contains the following entries in "source" of "attributes" array
            | source |
            | HMDB   |


    Scenario: Check HMDB disorder producer
        Given the transformer
        when we fire "/disorders/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "HMDB:HMDB0000012",
                    "identifiers": {
                        "hmdb": "HMDB:HMDB0000012"
                    }
                }
            ]
        }
        """
        then the size of the response is 5
        and the response contains the following entries in "biolink_class"
            | biolink_class |
            | Disease       |
        and the response only contains the following entries in "biolink_class"
            | biolink_class |
            | Disease       |
        and the response contains the following entries in "relation" of "connections" array
            | relation   |
            | related_to |
        and the response only contains the following entries in "relation" of "connections" array
            | relation   |
            | related_to |
