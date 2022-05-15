Feature: Check ChemBank transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-chembank-transformer.transltr.io/chembank"


    Scenario: Check transformer info
        Given the transformer
        when we fire "/compounds/transformer_info" query
        then the size of "parameters" should be 1
        and the value of "label" should be "ChemBank"


    Scenario: Check ChemBank producer - single name
        Given the transformer
        when we fire "/compounds/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compounds",
                    "value": "ChemBank:1472;aspirin; bortezomib"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "id"
            | id            |
            | ChemBank:1472 |
            | ChemBank:1171 |
        and the response only contains the following entries in "id"
            | id            |
            | ChemBank:1472 |
            | ChemBank:1171 |
        and the response contains the following entries in "source"
            | source   |
            | ChemBank |
        and the response only contains the following entries in "source"
            | source   |
            | ChemBank |


    Scenario: Check ChemBank producer - multi name
        Given the transformer
        when we fire "/compounds/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compounds",
                    "value": "ChemBank:1472"
                },
                {
                    "name": "compounds",
                    "value": "aspirin"
                },
                {
                    "name": "compounds",
                    "value": "HEFNNWSXXWATRW-JTQLQIEISA-N"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "id"
            | id            |
            | ChemBank:1472 |
            | ChemBank:1171 |
        and the response only contains the following entries in "id"
            | id            |
            | ChemBank:1472 |
            | ChemBank:1171 |
        and the response contains the following entries in "source"
            | source   |
            | ChemBank |
        and the response only contains the following entries in "source"
            | source   |
            | ChemBank |
