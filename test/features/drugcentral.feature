Feature: Check DrugCentral transformer

    Background: Specify transformer API
        Given a transformer at "https://translator.broadinstitute.org/drugcentral"


    Scenario: Check transformer info
        Given the transformer
        when we fire "/indications/transformer_info" query
        then the value of "name" should be "DrugCentral indications transformer"
        and the value of "knowledge_map.input_class" should be "disease"
        and the value of "knowledge_map.output_class" should be "compound"


    Scenario: Check transformer info for disease producer
        Given the transformer
        when we fire "/diseases/transformer_info" query
        then the value of "name" should be "DrugCentral disease producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "disease"


    Scenario: Check transformer info for compounds producer
        Given the transformer
        when we fire "/compounds/transformer_info" query
        then the value of "name" should be "DrugCentral compounds producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"


    Scenario: Check DrugCentral transformer
        Given the transformer
        when we fire "/indications/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "disease",
                    "value": "pain"
                }
            ]
        }
        """
        then the size of the response is 47
        and the response contains the following entries in "source"
            | source      |
            | DrugCentral |
        and the response only contains the following entries in "source"
            | source      |
            | DrugCentral |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source      |
            | DrugCentral |


    Scenario: Check DrugCentral disease producer
        Given the transformer
        when we fire "/diseases/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "disease",
                    "value": "MONDO:0006805"
                }
            ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "source"
            | source      |
            | DrugCentral |
        and the response only contains the following entries in "source"
            | source      |
            | DrugCentral |
        and the response contains the following entries in "id"
            | id                 |
            | SNOMEDCT:194828000 |
        and the response only contains the following entries in "id"
            | id                 |
            | SNOMEDCT:194828000 |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source      |
            | DrugCentral |


    Scenario: Check DrugCentral disease producer with multiple diseases
        Given the transformer
        when we fire "/diseases/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "disease",
                    "value": "MONDO:0006805"
                },
                {
                    "name": "disease",
                    "value": "SNOMEDCT:89362005"
                },
                {
                    "name": "disease",
                    "value": "UMLS:C0002962"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "source"
            | source      |
            | DrugCentral |
        and the response only contains the following entries in "source"
            | source      |
            | DrugCentral |
        and the response contains the following entries in "id"
            | id                 |
            | SNOMEDCT:194828000 |
            | SNOMEDCT:89362005  |
        and the response only contains the following entries in "id"
            | id                 |
            | SNOMEDCT:194828000 |
            | SNOMEDCT:89362005  |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source      |
            | DrugCentral |


    Scenario: Check DrugCentral compounds producer
        Given the transformer
        when we fire "/compounds/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compound",
                    "value": "levdobutamine"
                },
                {
                    "name": "compound",
                    "value": "DrugCentral:24"
                },
                {
                    "name": "compound",
                    "value": "JRWZLRBJNMZMFE-ZDUSSCGKSA-N"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "source"
            | source      |
            | DrugCentral |
        and the response only contains the following entries in "source"
            | source      |
            | DrugCentral |
        and the response contains the following entries in "id"
            | id             |
            | DrugCentral:13 |
            | DrugCentral:24 |
        and the response only contains the following entries in "id"
            | id             |
            | DrugCentral:13 |
            | DrugCentral:24 |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source      |
            | DrugCentral |
