Feature: Check Drug Repurposing Hub transformer

    Background: Specify transformer API
        Given a transformer at "https://translator.broadinstitute.org/repurposing"


    Scenario: Check compounds transformer info
        Given the transformer
        when we fire "/compounds/transformer_info" query
        then the value of "name" should be "Repurposing Hub compound-list producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"


    Scenario: Check targets transformer info
        Given the transformer
        when we fire "/targets/transformer_info" query
        then the value of "name" should be "Repurposing Hub target transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"


    Scenario: Check Drug Repurposing Hub compound-list producer
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
            | Repurposing Hub compound-list producer |
        and the response only contains the following entries in "source"
            | source                                 |
            | Repurposing Hub compound-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | Drug Repurposing Hub |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name    |
            | aspirin |
        and the response contains the following entries in "source" of "attributes" array
            | source                                 |
            | Repurposing Hub compound-list producer |
        and the response only contains the following entries in "source" of "attributes" array
            | source                                 |
            | Repurposing Hub compound-list producer |
        and the response contains the following entries in "value" of "attributes" array
            | value   |
            | aspirin |
        and the response contains the following entries in "inchikey" of "structure"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
        and the response only contains the following entries in "inchikey" of "structure"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |


    Scenario: Check Drug Repurposing Hub targets transformer
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "compounds": [
                {
                    "compound_id": "ChEMBL:CHEMBL25",
                    "identifiers": {
                        "pubchem": "CID:2244"
                    },
                    "structure": {
                        "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                    }
                }
            ]
        }
        """
        then the size of the response is 19
        and the response contains the following entries in "source" of "attributes" array
            | source                             |
            | Repurposing Hub target transformer |
        and the response only contains the following entries in "source" of "attributes" array
            | source                             |
            | Repurposing Hub target transformer |

