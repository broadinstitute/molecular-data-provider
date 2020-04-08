Feature: Check CMAP transformer

    Background: Specify transformer API
        Given a transformer at "https://translator.broadinstitute.org/cmap"
        
    Scenario: Check transformer info
        Given the transformer
        when we fire "/gene/gene/transformer_info" query
        then the value of "knowledge_map.input_class" should be "gene"
        and the value of "knowledge_map.output_class" should be "gene"

    Scenario: Check transformer info
        Given the transformer
        when we fire "/gene/compound/transformer_info" query
        then the value of "knowledge_map.input_class" should be "gene"
        and the value of "knowledge_map.output_class" should be "compound"

    Scenario: Check transformer info
        Given the transformer
        when we fire "/compound/gene/transformer_info" query
        then the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"

    Scenario: Check transformer info
        Given the transformer
        when we fire "/compound/compound/transformer_info" query
        then the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "compound"

    Scenario: Check transformation
        Given the transformer
        when we fire "/compound/compound/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "score threshold",
                    "value": "99.5"
                },
                {
                    "name": "maximum number",
                    "value": "0"
                }
            ],
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
        then the size of the response is 13


    Scenario: Check transformation with limit
        Given the transformer
        when we fire "/compound/compound/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "score threshold",
                    "value": "99.5"
                },
                {
                    "name": "maximum number",
                    "value": "2"
                }
            ],
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
