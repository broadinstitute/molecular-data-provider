Feature: Check GWAS transformer

    Background: Specify transformer API
        Given a transformer at "https://translator.broadinstitute.org/gwas"


    Scenario: Check GWAS gene to disease transformer info
        Given the transformer
        when we fire "/gwas-diseases/transformer_info" query
        then the value of "name" should be "GWAS gene to disease transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "gene"
        and the value of "knowledge_map.output_class" should be "disease"
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "v1.4"
        and the size of "parameters" should be 0


    Scenario: Check GWAS disease to gene transformer info
        Given the transformer
        when we fire "/gwas-genes/transformer_info" query
        then the value of "name" should be "GWAS disease to gene transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "disease"
        and the value of "knowledge_map.output_class" should be "gene"
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "v1.4"
        and the size of "parameters" should be 0


    Scenario: Check STRING links transformer
        Given the transformer
        when we fire "/gwas-diseases/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "NCBIGene:1508",
                    "biolink_class": "Gene",
                    "identifiers": {
                        "entrez": "NCBIGene:1508"
                    },
                    "source": "STRING",
                    "provided_by": "STRING protein-protein interaction"
                }
            ]
        }
        """
        then the size of the response is 37
        and the response contains the following entries in "source"
            | source |
            | GWAS   |
        and the response only contains the following entries in "source"
            | source |
            | GWAS   |
        and the response contains the following entries in "provided_by"
            | provided_by                      |
            | GWAS gene to disease transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                      |
            | GWAS gene to disease transformer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | GWAS   |
        and the response only contains the following entries in "source" of "names_synonyms" array
            | source |
            | GWAS   |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | GWAS   |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | GWAS   |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | NCBIGene:1508     |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | NCBIGene:1508     |
        and the response contains the following entries in "provided_by" of "connections" array
            | provided_by                      |
            | GWAS gene to disease transformer |
        and the response only contains the following entries in "provided_by" of "connections" array
            | provided_by                      |
            | GWAS gene to disease transformer |


    Scenario: Check STRING links transformer with empty input list
        Given the transformer
        when we fire "/gwas-diseases/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": []
        }
        """
        then the size of the response is 0


    Scenario: Check STRING links transformer
        Given the transformer
        when we fire "/gwas-genes/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "MONDO:0014488",
                    "biolink_class": "Disease",
                    "identifiers": {
                        "entrez": "MONDO:0014488"
                    },
                    "source": "STRING",
                    "provided_by": "STRING protein-protein interaction"
                }
            ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "source"
            | source |
            | GWAS   |
        and the response only contains the following entries in "source"
            | source |
            | GWAS   |
        and the response contains the following entries in "provided_by"
            | provided_by                      |
            | GWAS disease to gene transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                      |
            | GWAS disease to gene transformer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | GWAS   |
        and the response only contains the following entries in "source" of "names_synonyms" array
            | source |
            | GWAS   |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | GWAS   |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | GWAS   |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | MONDO:0014488     |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | MONDO:0014488     |
        and the response contains the following entries in "provided_by" of "connections" array
            | provided_by                      |
            | GWAS disease to gene transformer |
        and the response only contains the following entries in "provided_by" of "connections" array
            | provided_by                      |
            | GWAS disease to gene transformer |


    Scenario: Check STRING links transformer with empty input list
        Given the transformer
        when we fire "/gwas-genes/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": []
        }
        """
        then the size of the response is 0
