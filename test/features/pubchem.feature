Feature: Check CMAP transformer

    Background: Specify transformer API
        Given a transformer at "http://localhost:8200/pubchem_producer"


    Scenario: Check transformer info
        Given the transformer
        when we fire "/transformer_info" query
        then the size of "parameters" should be 1
        and the value of "label" should be "PubChem"


    Scenario: Check PubChem producer - name
        Given the transformer
        when we fire "/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compounds",
                    "value": "aspirin; bortezomib"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "compound_id"
            | compound_id |
            | CID:2244    |
            | CID:387447  |
        and the response only contains the following entries in "compound_id"
            | compound_id |
            | CID:2244    |
            | CID:387447  |
        and the response contains the following entries in "source"
            | source                         |
            | Pubchem compound-list producer |
        and the response only contains the following entries in "source"
            | source                         |
            | Pubchem compound-list producer |


    Scenario: Check PubChem producer - CID
        Given the transformer
        when we fire "/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compounds",
                    "value": "CID:2244; CID:387447"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "compound_id"
            | compound_id |
            | CID:2244    |
            | CID:387447  |
        and the response only contains the following entries in "compound_id"
            | compound_id |
            | CID:2244    |
            | CID:387447  |
        and the response contains the following entries in "source"
            | source                         |
            | Pubchem compound-list producer |
        and the response only contains the following entries in "source"
            | source                         |
            | Pubchem compound-list producer |
