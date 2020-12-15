Feature: Check ChEBI transformer

    Background: Specify transformer API
        Given a transformer at "http://localhost:8310/chebi"


    Scenario: Check compounds producer info
        Given the transformer
        when we fire "/compounds/transformer_info" query
        then the value of "name" should be "ChEBI compound-list producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"


    Scenario: Check ChEBI compound-list producer
        Given the transformer
        when we fire "/compounds/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compounds",
                    "value": "aspirin"
                }
            ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "source"
            | source                                 |
            | ChEBI compound-list producer |
        and the response only contains the following entries in "source"
            | source                                 |
            | ChEBI compound-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | ChEBI  |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                 |
            | acetylsalicylic acid |
        and the response contains the following entries in "source" of "attributes" array
            | source                                 |
            | ChEBI compound-list producer |
        and the response only contains the following entries in "source" of "attributes" array
            | source                                 |
            | ChEBI compound-list producer |
        and the response contains the following entries in "value" of "attributes" array
            | value   |
            | aspirin |
        and the response contains the following entries in "inchikey" of "structure"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
        and the response only contains the following entries in "inchikey" of "structure"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |

