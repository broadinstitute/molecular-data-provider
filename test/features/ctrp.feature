Feature: Check CTRP transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-ctrp-transformer.ci.transltr.io/ctrp"


    Scenario: Check transformer info
        Given the transformer
        when we fire "/transformer_info" query
        then the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "compound"


    Scenario: Check transformation
        Given the transformer
        when we fire "/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "maximum FDR",
                    "value": "0.005"
                },
                {
                    "name": "disease context",
                    "value": "pan-cancer (all lines)"
                },
                {
                    "name": "maximum number",
                    "value": "0"
                }
            ],
            "collection": [
                {
                    "id": "CID:49793307",
                    "identifiers": {
                        "pubchem": "CID:49793307"
                    }
                }
            ]
        }
        """
        then the size of the response is 14


    Scenario: Check transformation
        Given the transformer
        when we fire "/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "maximum FDR",
                    "value": "0.005"
                },
                {
                    "name": "disease context",
                    "value": "pan-cancer (all lines)"
                },
                {
                    "name": "maximum number",
                    "value": "5"
                }
            ],
            "collection": [
                {
                    "id": "CID:49793307",
                    "identifiers": {
                        "pubchem": "CID:49793307"
                    }
                }
            ]
        }
        """
        then the size of the response is 5

