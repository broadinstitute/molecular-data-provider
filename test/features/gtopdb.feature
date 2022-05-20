Feature: Check GtoPdb transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-gtopdb-transformer.transltr.io/gtopdb"
        
    Scenario: Check transformer info
        Given the transformer
        when we fire "/molecules/transformer_info" query
        then the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"

    Scenario: Check GtoPdb compound-list producer with name
        Given the transformer
        when we fire "/molecules/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compounds",
                    "value": "aspirin"
                }
            ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "id"
            | id       |
            | GTOPDB:4139 |
        and the response only contains the following entries in "id"
            | id       |
            | GTOPDB:4139 |


    Scenario: Check GtoPdb compound-list producer with CID
        Given the transformer
        when we fire "/molecules/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compounds",
                    "value": "CID:2244"
                }
            ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "id"
            | id       |
            | GTOPDB:4139 |
        and the response only contains the following entries in "id"
            | id       |
            | GTOPDB:4139 |


    Scenario: Check GtoPdb compound-list producer with ligand id
        Given the transformer
        when we fire "/molecules/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compounds",
                    "value": "GtoPdb:4829"
                }
            ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "id"
            | id       |
            | GTOPDB:4829 |
        and the response only contains the following entries in "id"
            | id       |
            | GTOPDB:4829 |


    Scenario: Check GtoPdb compound-list producer with two names
        Given the transformer
        when we fire "/molecules/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compounds",
                    "value": "bortezomib; aspirin"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "id"
            | id          |
            | GTOPDB:6391 |
            | GTOPDB:4139 |
        and the response only contains the following entries in "id"
            | id          |
            | GTOPDB:6391 |
            | GTOPDB:4139 |
        and the value of "[0].names_synonyms[0].name" should be "bortezomib"
        and the value of "[1].names_synonyms[0].name" should be "aspirin"



    Scenario: Check GtoPdb multi-compound-list producer
        Given the transformer
        when we fire "/molecules/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compounds",
                    "value": "bortezomib; CID:2244; GTOPDB:4050"
                }
            ]
        }
        """
        then the size of the response is 3
        and the response contains the following entries in "id"
            | id          |
            | GTOPDB:4050 |
            | GTOPDB:6391 |
            | GTOPDB:4139 |
        and the response only contains the following entries in "id"
            | id          |
            | GTOPDB:6391 |
            | GTOPDB:4139 |
            | GTOPDB:4050 |


    Scenario: Check GtoPdb targets transformer
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "CID:2244",
                    "identifiers": {
                        "drugbank": "DrugBank:DB00945",
                        "pubchem": "CID:2244"
                    }
                }
            ]
        }
        """
        then the size of the response is 3
        and the response contains the following entries in "id"
            | id        |
            | HGNC:101  |
            | HGNC:9604 |
            | HGNC:9605 |
        and the response only contains the following entries in "id"
            | id        |
            | HGNC:101  |
            | HGNC:9604 |
            | HGNC:9605 |


    Scenario: Check GtoPdb targets transformer
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "DrugBank:DB00945",
                    "identifiers": {
                        "drugbank": "DrugBank:DB00945",
                        "chembl": "ChEMBL:CHEMBL25"
                    }
                }
            ]
        }
        """
        then the size of the response is 0


    Scenario: Check GtoPdb inhibitors transformer
        Given the transformer
        when we fire "/inhibitors/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "HGNC:3538",
                    "identifiers": {
                        "hgnc": "HGNC:3538"
                    }
                }
            ]
        }
        """
        then the size of the response is 19
