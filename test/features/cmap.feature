Feature: Check CMAP transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-cmap-transformer.test.transltr.io/cmap"
        
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
            "collection": [
                {
                    "id": "CID:2244",
                    "identifiers": {
                        "pubchem": "CID:2244"
                    },
                    "source": "test input"
                }
            ]
        }
        """
        then the size of the response is 13
        and the response contains the following entries in "source"
            | source                             |
            | test input                         |
            | CMAP compound-to-compound expander |
        and the response only contains the following entries in "source"
            | source                             |
            | test input                         |
            | CMAP compound-to-compound expander |

    Scenario: Check transformation
        Given the transformer
        when we fire "/compound/gene/transform" query with the following body:
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
            "collection": [
                {
                    "id": "CID:2244",
                    "identifiers": {
                        "pubchem": "CID:2244"
                    }
                }
            ]
        }
        """
        then the size of the response is 11

    Scenario: Check transformation
        Given the transformer
        when we fire "/gene/compound/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "score threshold",
                    "value": "95.0"
                },
                {
                    "name": "maximum number",
                    "value": "0"
                }
            ],
            "collection": [
                {
                    "id": "NCBIGene:3675",
                    "identifiers": {
                        "entrez": "NCBIGene:3675"
                    }
                }
            ]
        }
        """
        then the size of the response is 7

    Scenario: Check transformation
        Given the transformer
        when we fire "/gene/gene/transform" query with the following body:
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
            "collection": [
                {
                    "id": "NCBIGene:3675",
                    "identifiers": {
                        "entrez": "NCBIGene:3675"
                    }
                }
            ]
        }
        """
        then the size of the response is 17

    Scenario: Check transformation with limit
        Given the transformer
        when we fire "/compound/gene/transform" query with the following body:
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
            "collection": [
                {
                    "id": "CID:2244",
                    "identifiers": {
                        "pubchem": "CID:2244"
                    }
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "source"
            | source                         |
            | CMAP compound-to-gene transformer |
        and the response only contains the following entries in "source"
            | source                         |
            | CMAP compound-to-gene transformer |
        and the response contains the following entries in "id"
            | id             |
            | NCBIGene:51176 |
            | NCBIGene:3675  |
        and the response only contains the following entries in "id"
            | id                         |
            | NCBIGene:51176 |
            | NCBIGene:3675  |

