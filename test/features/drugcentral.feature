Feature: Check DrugCentral transformer

    Background: Specify transformer API
        Given a transformer at "http://localhost:8260/drugcentral"


    Scenario: Check transformer info
        Given the transformer
        when we fire "/indications/transformer_info" query
        then the value of "name" should be "DrugCentral indications transformer"
        and the value of "knowledge_map.input_class" should be "disease"
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
            | source                                 |
            | DrugCentral indications transformer |
        and the response only contains the following entries in "source"
            | source                                 |
            | DrugCentral indications transformer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | DrugCentral |
        and the response contains the following entries in "source" of "attributes" array
            | source                                 |
            | DrugCentral indications transformer |
        and the response only contains the following entries in "source" of "attributes" array
            | source                                 |
            | DrugCentral indications transformer |


