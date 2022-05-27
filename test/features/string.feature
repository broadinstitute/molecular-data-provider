Feature: Check STRING transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-string-transformer.ci.transltr.io/string"


    Scenario: Check links transformer info
        Given the transformer
        when we fire "/links/transformer_info" query
        then the value of "name" should be "STRING protein-protein interaction"
        and the value of "knowledge_map.input_class" should be "gene"
        and the value of "knowledge_map.output_class" should be "gene"
        and the value of "version" should be "2.3.0"


    Scenario: Check STRING links transformer
        Given the transformer
        when we fire "/links/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "HGNC:2527",
                    "biolink_class": "Gene",
                    "identifiers": {
                        "entrez": "NCBIGene:1508"
                    },
                    "names_synonyms": [],
                    "connections": [],
                    "source": "STRING",
                    "provided_by": "STRING protein-protein interaction"
                }
            ]
        }
        """
        then the size of the response is 9
        and the response contains the following entries in "source"
            | source |
            | STRING |
        and the response only contains the following entries in "source"
            | source |
            | STRING |
        and the response contains the following entries in "provided_by"
            | provided_by                        |
            | STRING protein-protein interaction |
        and the response only contains the following entries in "provided_by"
            | provided_by                        |
            | STRING protein-protein interaction |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source    |
            | STRING    |
        and the response only contains the following entries in "source" of "names_synonyms" array
            | source    |
            | STRING    |
        and the response contains the following entries in "source" of "connections" array
            | source    |
            | STRING    |
        and the response only contains the following entries in "source" of "connections" array
            | source    |
            | STRING    |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | HGNC:2527         |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | HGNC:2527         |
        and the response contains the following entries in "provided_by" of "connections" array
            | provided_by                            |
            | STRING protein-protein interaction     |
        and the response only contains the following entries in "provided_by" of "connections" array
            | provided_by                            |
            | STRING protein-protein interaction     |


    Scenario: Check STRING links transformer with empty input list
        Given the transformer
        when we fire "/links/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": []
        }
        """
        then the size of the response is 0

