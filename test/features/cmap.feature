Feature: Check CMAP transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-cmap-transformer.ci.transltr.io/cmap"


    Scenario: Check transformer info
        Given the transformer
        when we fire "/compound/producer/transformer_info" query
        then the value of "name" should be "CMAP compound-list producer"
        and the value of "label" should be "CMAP"
        and the value of "infores" should be "infores:cmap"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "2021-11-23"
        and the size of "knowledge_map.nodes" should be 1
        and the size of "knowledge_map.edges" should be 0
        and the size of "parameters" should be 1


    Scenario: Check transformer info
        Given the transformer
        when we fire "/gene/gene/transformer_info" query
        then the value of "name" should be "CMAP gene-to-gene expander"
        and the value of "label" should be "CMAP"
        and the value of "infores" should be "infores:cmap"
        and the value of "function" should be "expander"
        and the value of "knowledge_map.input_class" should be "gene"
        and the value of "knowledge_map.output_class" should be "gene"
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "2021-11-23"
        and the size of "knowledge_map.nodes" should be 1
        and the size of "knowledge_map.edges" should be 1
        and the size of "parameters" should be 2


    Scenario: Check transformer info
        Given the transformer
        when we fire "/gene/compound/transformer_info" query
        then the value of "name" should be "CMAP gene-to-compound transformer"
        and the value of "label" should be "CMAP"
        and the value of "infores" should be "infores:cmap"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "gene"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "2021-11-23"
        and the size of "knowledge_map.nodes" should be 2
        and the size of "knowledge_map.edges" should be 1
        and the size of "parameters" should be 2


    Scenario: Check transformer info
        Given the transformer
        when we fire "/compound/gene/transformer_info" query
        then the value of "name" should be "CMAP compound-to-gene transformer"
        and the value of "label" should be "CMAP"
        and the value of "infores" should be "infores:cmap"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "2021-11-23"
        and the size of "knowledge_map.nodes" should be 2
        and the size of "knowledge_map.edges" should be 1
        and the size of "parameters" should be 2


    Scenario: Check transformer info
        Given the transformer
        when we fire "/compound/compound/transformer_info" query
        then the value of "name" should be "CMAP compound-to-compound expander"
        and the value of "label" should be "CMAP"
        and the value of "infores" should be "infores:cmap"
        and the value of "function" should be "expander"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "2021-11-23"
        and the size of "knowledge_map.nodes" should be 1
        and the size of "knowledge_map.edges" should be 1
        and the size of "parameters" should be 2


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
                    "biolink_class":"SmallMolecule",
                    "identifiers": {
                        "pubchem": "CID:2244"
                    },
                    "source": "CMAP compound-list producer",
                    "provided_by": "CMAP"
                }
            ]
        }
        """
        then the size of the response is 13
        and the response contains the following entries in "source"
            | source                             |
            | CMAP compound-list producer        |
            | CMAP                               |
        and the response only contains the following entries in "source"
            | source                             |
            | CMAP compound-list producer        |
            | CMAP                               |


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
                    "biolink_class":"SmallMolecule",
                    "identifiers": {
                        "pubchem": "CID:2244"
                    },
                    "source": "CMAP compound-list producer",
                    "provided_by": "CMAP"
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
                    "biolink_class":"Gene",
                    "identifiers": {
                        "entrez": "NCBIGene:3675"
                    },
                    "source": "CMAP compound-list producer",
                    "provided_by": "CMAP"
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
                    "biolink_class":"Gene",
                    "identifiers": {
                        "entrez": "NCBIGene:3675"
                    },
                    "source": "CMAP compound-list producer",
                    "provided_by": "CMAP"
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
                    "id": "CHEBI:15365",
                    "biolink_class":"SmallMolecule",
                    "identifiers": {
                        "pubchem": "CID:2244"
                    },
                    "source": "CMAP compound-list producer",
                    "provided_by": "CMAP"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "source"
            | source |
            | CMAP   |
        and the response only contains the following entries in "source"
            | source |
            | CMAP   |
        and the response contains the following entries in "provided_by"
            | provided_by                       |
            | CMAP compound-to-gene transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                       |
            | CMAP compound-to-gene transformer |
        and the response contains the following entries in "id"
            | id             |
            | NCBIGene:51176 |
            | NCBIGene:3675  |
        and the response only contains the following entries in "id"
            | id                         |
            | NCBIGene:51176 |
            | NCBIGene:3675  |
