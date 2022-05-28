Feature: Check CTD transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-ctd-transformer.transltr.io/ctdbase"


    Scenario: Check CTD producer info
        Given the transformer
        when we fire "/chemicals/transformer_info" query
        then the value of "name" should be "CTD compound-list producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the size of "knowledge_map" should be 4
        and the size of "parameters" should be 1


    Scenario: Check CTD gene-interactions transformer info
        Given the transformer
        when we fire "/gene-interactions/transformer_info" query
        then the value of "name" should be "CTD gene interactions transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the size of "knowledge_map" should be 4
        and the size of "parameters" should be 0


    Scenario: Check CTD disease associations transformer info
        Given the transformer
        when we fire "/disease-associations/transformer_info" query
        then the value of "name" should be "CTD disease associations transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "disease"
        and the size of "knowledge_map" should be 4
        and the size of "parameters" should be 0


    Scenario: Check CTD pathway associations transformer info
        Given the transformer
        when we fire "/pathway-associations/transformer_info" query
        then the value of "name" should be "CTD pathway associations transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "pathway"
        and the size of "knowledge_map" should be 4
        and the size of "parameters" should be 1


    Scenario: Check CTD go associations transformer info
        Given the transformer
        when we fire "/go-associations/transformer_info" query
        then the value of "name" should be "CTD go associations transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "BiologicalEntity"
        and the size of "knowledge_map" should be 4
        and the size of "parameters" should be 1


    Scenario: Check CTD phenotype interactions transformer info
        Given the transformer
        when we fire "/phenotype-interactions/transformer_info" query
        then the value of "name" should be "CTD phenotype interactions transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "BiologicalProcess"
        and the size of "knowledge_map" should be 4
        and the size of "parameters" should be 0


    Scenario: Check CTD compound-list producer
        Given the transformer
        when we fire "/chemicals/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compound",
                    "value": "aspirin"
                },
                {
                    "name": "compound",
                    "value": "CID:387447"
                },
                {
                    "name": "compound",
                    "value": "MESH:D001241"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "id"
            | id         |
            | CID:2244   |
            | CID:387447 |
        and the response only contains the following entries in "id"
            | id         |
            | CID:2244   |
            | CID:387447 |
        and the response contains the following entries in "provided_by"
            | provided_by                |
            | CTD compound-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                |
            | CTD compound-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | CTD    |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name       |
            | Aspirin    |
            | Bortezomib |
        and the response only contains the following entries in "name" of "names_synonyms" array
            | name       |
            | Aspirin    |
            | Bortezomib |
        and the response contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | CTD              |
        and the response only contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | CTD              |


    Scenario: Check CTD gene-interactions transformer
        Given the transformer
        when we fire "/gene-interactions/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "CID:2836600",
                    "biolink_class": "ChemicalSUbstance",
                    "identifiers": {
                        "pubchem": "CID:2836600"
                    },
                    "source": "MolePro test",
                    "provided_by": "MolePro test"
                }
            ]
        }
        """
        then the size of the response is 6
        and the response contains the following entries in "provided_by"
            | provided_by                       |
            | CTD gene interactions transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                       |
            | CTD gene interactions transformer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | CTD    |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | CTD    |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | CTD    |


    Scenario: Check CTD disease associations transformer
        Given the transformer
        when we fire "/disease-associations/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "CID:114709",
                    "biolink_class": "ChemicalSUbstance",
                    "identifiers": {
                        "pubchem": "CID:114709"
                    },
                    "source": "MolePro test",
                    "provided_by": "MolePro test"
                }
            ]
        }
        """
        then the size of the response is 48
        and the response contains the following entries in "provided_by"
            | provided_by                          |
            | CTD disease associations transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                          |
            | CTD disease associations transformer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | CTD    |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | CTD    |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | CTD    |


    Scenario: Check CTD pathway associations transformer
        Given the transformer
        when we fire "/pathway-associations/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name":"limit",
                    "value" : "99"
                }
            ],
            "collection": [
                {
                    "id": "CID:14805",
                    "biolink_class": "ChemicalSUbstance",
                    "identifiers": {
                        "pubchem": "CID:14805"
                    },
                    "source": "MolePro test",
                    "provided_by": "MolePro test"
                }
            ]
        }
        """
        then the size of the response is 99
        and the response contains the following entries in "provided_by"
            | provided_by                          |
            | CTD pathway associations transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                          |
            | CTD pathway associations transformer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | CTD    |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | CTD    |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | CTD    |


    Scenario: Check CTD go associations transformer
        Given the transformer
        when we fire "/go-associations/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "CID:2836600",
                    "biolink_class": "ChemicalSUbstance",
                    "identifiers": {
                        "pubchem": "CID:2836600"
                    },
                    "source": "MolePro test",
                    "provided_by": "MolePro test"
                }
            ]
        }
        """
        then the size of the response is 8
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | CTD go associations transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | CTD go associations transformer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | CTD    |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | CTD    |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | CTD    |
        and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by                     |
            | CTD go associations transformer |
        and the response only contains the following entries in "provided_by" of "attributes" array
            | provided_by                     |
            | CTD go associations transformer |


    Scenario: Check CTD go associations transformer
        Given the transformer
        when we fire "/phenotype-interactions/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "CID:2836600",
                    "biolink_class": "ChemicalSUbstance",
                    "identifiers": {
                        "pubchem": "CID:2836600"
                    },
                    "source": "MolePro test",
                    "provided_by": "MolePro test"
                }
            ]
        }
        """
        then the size of the response is 4
        and the response contains the following entries in "provided_by"
            | provided_by                            |
            | CTD phenotype interactions transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                            |
            | CTD phenotype interactions transformer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | CTD    |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | CTD    |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | CTD    |
        and the response contains the following entries in "provided_by" of "connections" array
            | provided_by                            |
            | CTD phenotype interactions transformer |
        and the response only contains the following entries in "provided_by" of "connections" array
            | provided_by                            |
            | CTD phenotype interactions transformer |

