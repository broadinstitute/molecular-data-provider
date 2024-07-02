Feature: Check ChemBank transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-chembank-transformer.test.transltr.io/chembank"


    Scenario: Check transformer info
        Given the transformer
        when we fire "/compounds/transformer_info" query
        then the value of "name" should be "ChemBank compound-list producer"
        and the value of "label" should be "ChemBank"
        and the value of "infores" should be "infores:chembank"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "2 (2019-05-01)"
        and the size of "knowledge_map.nodes" should be 1
        and the size of "parameters" should be 1


    Scenario: Check ChemBank producer - single name
        Given the transformer
        when we fire "/compounds/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compound",
                    "value": "ChemBank:1472"
                }
            ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "id"
            | id            |
            | ChemBank:1472 |
        and the response only contains the following entries in "id"
            | id            |
            | ChemBank:1472 |
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
                    "name": "compound",
                    "value": "ChemBank:1472"
                },
                {
                    "name": "compound",
                    "value": "aspirin"
                },
                {
                    "name": "compound",
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
        and the response contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
            | HEFNNWSXXWATRW-JTQLQIEISA-N |
        and the response only contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
            | HEFNNWSXXWATRW-JTQLQIEISA-N |