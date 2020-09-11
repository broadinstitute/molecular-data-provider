Feature: Check ChEMBL transformer

    Background: Specify transformer API
        Given a transformer at "https://translator.broadinstitute.org/chembl"


    Scenario: Check ChEMBL producer info
        Given the transformer
        when we fire "/molecules/transformer_info" query
        then the value of "name" should be "ChEMBL compound-list producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the size of "parameters" should be 1


    Scenario: Check ChEMBL target transformer info
        Given the transformer
        when we fire "/targets/transformer_info" query
        then the value of "name" should be "ChEMBL target transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the size of "parameters" should be 0


    Scenario: Check ChEMBL compound-list producer
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
            | id |
            | ChEMBL:CHEMBL25    |
        and the response only contains the following entries in "id"
            | id |
            | ChEMBL:CHEMBL25    |
        and the response contains the following entries in "source"
            | source                          |
            | ChEMBL compound-list producer |
        and the response only contains the following entries in "source"
            | source                          |
            | ChEMBL compound-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | ChEMBL |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                 |
            | Acetylsalicylic Acid |
        and the response contains the following entries in "source" of "attributes" array
            | source                        |
            | ChEMBL compound-list producer |
        and the response only contains the following entries in "source" of "attributes" array
            | source                        |
            | ChEMBL compound-list producer |
        and the response contains the following entries in "value" of "attributes" array
            | value  |
            | aspirin |
            | ChEMBL  |
        and the response only contains the following entries in "value" of "attributes" array
            | value  |
            | aspirin |
            | ChEMBL  |
        and the response contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
        and the response only contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |


    Scenario: Check ChEMBL targets transformer on ID input
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "CID:2244",
                    "identifiers": {
                        "chembl": "ChEMBL:CHEMBL25"
                    }
                }
            ]
        }
        """
        then the size of the response is 2


    Scenario: Check ChEMBL targets transformer on structure input
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "CID:2244",
                    "identifiers": {
                        "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                    }
                }
            ]
        }
        """
        then the size of the response is 2


    Scenario: Check ChEMBL indications transformer on structure input
        Given the transformer
        when we fire "/indications/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "CID:2244",
                    "identifiers": {
                        "chembl": "ChEMBL:CHEMBL25"
                    },
                    "structure": {
                        "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                    }
                }
            ]
        }
        """
        then the size of the response is 108
        and the response contains the following entries in "biolink_class"
            | biolink_class |
            | Disease       |
        and the response only contains the following entries in "biolink_class"
            | biolink_class |
            | Disease       |
        and the response contains the following entries in "source"
            | source                         |
            | ChEMBL indication transformer |
        and the response only contains the following entries in "source"
            | source                         |
            | ChEMBL indication transformer |


