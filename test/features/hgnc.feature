Feature: Check HGNC  transformer

    Background: Specify transformer API
        Given a transformer at "https://translator.broadinstitute.org/hgnc"


    Scenario: Check HGNC gene producer transformer info
        Given the transformer
        when we fire "/genes/transformer_info" query
        then the value of "name" should be "HGNC gene-list producer"
        and the value of "label" should be "HGNC"
        and the value of "infores" should be "infores:hgnc"
        and the value of "version" should be "2.5.0"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "gene"
        and the size of "knowledge_map.nodes" should be 1
        and the value of "properties.source_version" should be "2023-01-01"
        and the size of "parameters" should be 1


    Scenario: Check HGNC gene producer
        Given the transformer
        when we fire "/genes/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "gene",
                    "value": "GPX4"
                },
                {
                    "name": "gene",
                    "value": "NCBIgene:6790"
                },
                {
                    "name": "gene",
                    "value": "HGNC:2243"
                },
                {
                    "name": "gene",
                    "value": "ENSEMBL:ENSG00000183044"
                },
                {
                    "name": "gene",
                    "value": "4-aminobutyrate aminotransferase"
                }
            ]
        }
        """
        then the size of the response is 4
        and the response contains the following entries in "id"
            | id         |
            | HGNC:4556  |
            | HGNC:11393 |
            | HGNC:2243  |
            | HGNC:23    |
        and the response only contains the following entries in "id"
            | id         |
            | HGNC:4556  |
            | HGNC:11393 |
            | HGNC:2243  |
            | HGNC:23    |
        and the response contains the following entries in "source"
            | source |
            | HGNC   |
        and the response only contains the following entries in "source"
            | source |
            | HGNC   |
        and the response contains the following entries in "provided_by"
            | provided_by             |
            | HGNC gene-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by             |
            | HGNC gene-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | HGNC   |
        and the response only contains the following entries in "source" of "names_synonyms" array
            | source |
            | HGNC   |


