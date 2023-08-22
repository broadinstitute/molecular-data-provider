Feature: Check Node_Normalizer transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-node-normalizer-transformer.transltr.io/node"


    Scenario: Node_Normalizer producer info
        Given the transformer
        when we fire "/normalizer/transformer_info" query
        then the value of "name" should be "SRI node normalizer producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "any"
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "2.0.10"
        and the size of "parameters" should be 2


    Scenario: Check Node_Normalizer compound-list producer
        Given the transformer
        when we fire "/normalizer/transform" query with the following body:
        """
            {
                "collection": [
                ],
                "controls":[
                        {
                  "name": "id",
                  "value": "MONDO:0005148"
                }
                ]
            }
        """
        then the size of the response is 1
        and the response contains the following entries in "id"
            | id               |
            | MONDO:0005148    |
        and the response only contains the following entries in "id"
            | id               |
            | MONDO:0005148    |
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | SRI node normalizer producer    |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | SRI node normalizer producer    |
        and the response contains the following entries in "snomed" of "identifiers"
            | snomed            |
            | SNOMEDCT:44054006 |
        and the response only contains the following entries in "snomed" of "identifiers"
            | snomed            |
            | SNOMEDCT:44054006 |
        and the response contains the following entries in "mesh" of "identifiers"
            | mesh         |
            | MESH:D003924 |
        and the response only contains the following entries in "mesh" of "identifiers"
            | mesh         |
            | MESH:D003924 |
        and the response contains the following entries in "icd10" of "identifiers"
            | icd10     |
            | ICD10:E11 |
        and the response only contains the following entries in "icd10" of "identifiers"
            | icd10     |
            | ICD10:E11 |
        and the response contains the following entries in "mondo" of "identifiers"
            | mondo         |
            | MONDO:0005148 |
        and the response only contains the following entries in "mondo" of "identifiers"
            | mondo         |
            | MONDO:0005148 |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source              |
            | SRI node normalizer |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                     |
            | type 2 diabetes mellitus |


