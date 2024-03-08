Feature: Check STRING transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-string-transformer.ci.transltr.io/string"


    Scenario: Check links transformer info
        Given the transformer
        when we fire "/links/transformer_info" query
        then the value of "name" should be "STRING protein-protein links transformer"
        and the value of "label" should be "STRING"
        and the value of "infores" should be "infores:string"
        and the value of "function" should be "expander"
        and the value of "knowledge_map.input_class" should be "gene"
        and the value of "knowledge_map.output_class" should be "gene"
        and the size of "knowledge_map.nodes" should be 1
        and the size of "knowledge_map.edges" should be 1
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "v12.0 (2023-08-22)"
        and the size of "parameters" should be 2


    Scenario: Check physical_links transformer info
        Given the transformer
        when we fire "/physical_links/transformer_info" query
        then the value of "name" should be "STRING protein-protein physical links transformer"
        and the value of "label" should be "STRING"
        and the value of "infores" should be "infores:string"
        and the value of "function" should be "expander"
        and the value of "knowledge_map.input_class" should be "gene"
        and the value of "knowledge_map.output_class" should be "gene"
        and the size of "knowledge_map.nodes" should be 1
        and the size of "knowledge_map.edges" should be 1
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "v12.0 (2023-08-22)"
        and the size of "parameters" should be 2


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
                         "names_synonyms": [{
                         "name": "CSTA",
                         "name_type": "primary name",
                         "provided_by": "STRING protein-protein interaction",
                         "source": "STRING",
                         "synonyms": []
                 }],
                    "connections": [],
                    "source": "STRING",
                    "provided_by": "STRING protein-protein interaction"
                }
            ]
        }
        """
        then the size of the response is 38
        and the response contains the following entries in "source"
            | source |
            | STRING |
        and the response only contains the following entries in "source"
            | source |
            | STRING |
            | STRING protein-protein links transformer |
        and the response contains the following entries in "provided_by"
            | provided_by                        |
            | STRING protein-protein links transformer |         
        and the response only contains the following entries in "provided_by"
            | provided_by                        |
            | STRING protein-protein links transformer |
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
            | provided_by                              |
            | STRING protein-protein links transformer |
        and the response only contains the following entries in "provided_by" of "connections" array
            | provided_by                              |
            | STRING protein-protein links transformer |


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



    Scenario: Check STRING links transformer with multiple queries
        Given the transformer
        when we fire "/links/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "maximum number of genes",
                    "value": "8"
                }
            ],
            "collection": [
             {
                 "id": "QUERY1",
                 "biolink_class": "Gene",
                 "identifiers": {
                     "entrez": "NCBIGene:1508"
                   },
                 "names_synonyms": [],
                 "connections": [],
                 "source": "STRING",
                 "provided_by": "STRING protein-protein links transformer"
              },
              {
                 "id": "query2",
                 "biolink_class": "Gene",
                 "identifiers": {
                     "entrez": "NCBIGene:1475"
                  },
                 "names_synonyms": [],
                 "connections": [],
                 "source": "STRING",
                 "provided_by": "STRING protein-protein links transformer"
              }  
             ]
         }
         """
        then the size of the response is 14
        and the response contains the following entries in "source"
            | source |
            | STRING |
        and the response only contains the following entries in "source"
            | source |
            | STRING |
            | STRING protein-protein links transformer |
        and the response contains the following entries in "provided_by"
            | provided_by                        |
            | STRING protein-protein links transformer |         
        and the response only contains the following entries in "provided_by"
            | provided_by                        |
            | STRING protein-protein links transformer |
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
            | QUERY1            |
            | query2            |
        and the response contains the following entries in "provided_by" of "connections" array
            | provided_by                              |
            | STRING protein-protein links transformer |
        and the response only contains the following entries in "provided_by" of "connections" array
            | provided_by                              |
            | STRING protein-protein links transformer |


Scenario: Check STRING physical links transformer with multiple queries
        Given the transformer
        when we fire "/physical_links/transform" query with the following body:
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
                    },
                    {
                        "id": "query2",
                        "biolink_class": "Gene",
                        "identifiers": {
                            "entrez": "NCBIGene:2553"
                        },
                        "names_synonyms": [],
                        "connections": [],
                        "source": "STRING",
                        "provided_by": "STRING protein-protein interaction"
                    }       
                ]
            }
         """
        then the size of the response is 54
        and the response contains the following entries in "source"
            | source |
            | STRING |
        and the response only contains the following entries in "source"
            | source |
            | STRING |
            | STRING protein-protein physical links transformer |
        and the response contains the following entries in "provided_by"
            | provided_by                                       |
            | STRING protein-protein physical links transformer |         
        and the response only contains the following entries in "provided_by"
            | provided_by                                       |
            | STRING protein-protein physical links transformer |
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
            | query2            |
        and the response contains the following entries in "provided_by" of "connections" array
            | provided_by                                       |
            | STRING protein-protein physical links transformer |
        and the response only contains the following entries in "provided_by" of "connections" array
            | provided_by                                       |
            | STRING protein-protein physical links transformer |