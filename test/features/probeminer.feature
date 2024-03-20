Feature: Check ProbeMiner transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-probeminer-transformer.test.transltr.io/probeminer"


    Scenario: Check ProbeMiner producer info
        Given the transformer
        when we fire "/chemicals/transformer_info" query
        then the value of "name" should be "ProbeMiner compound-list producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the size of "knowledge_map" should be 4
        and the size of "parameters" should be 1
        and the value of "version" should be "2.4.0"


    Scenario: Check ProbeMiner chemical-interactions transformer info
        Given the transformer
        when we fire "/chemical_interactions/transformer_info" query
        then the value of "name" should be "ProbeMiner chemical interactions transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "protein"
        and the size of "knowledge_map" should be 4
        and the size of "parameters" should be 0
        and the value of "version" should be "2.4.0"


    Scenario: Check ProbeMiner protein-interactions transformer info
        Given the transformer
        when we fire "/protein_interactions/transformer_info" query
        then the value of "name" should be "ProbeMiner protein interactions transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "protein"
        and the value of "knowledge_map.output_class" should be "compound"
        and the size of "knowledge_map" should be 4
        and the size of "parameters" should be 1
        and the value of "version" should be "2.4.0"


    Scenario: Check ProbeMiner compound-list producer
        Given the transformer
        when we fire "/chemicals/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compound",
                    "value": "KTUFNOKKBVMGRW-UHFFFAOYSA-N"
                },
                {
                    "name": "compound",
                    "value": "ACARBOSE"
                },
                {
                    "name": "compound",
                    "value": "canSAR:1901573"
                }
            ]
        }
        """
        then the size of the response is 4
        and the response contains the following entries in "id"
            | id                          |
            | KTUFNOKKBVMGRW-UHFFFAOYSA-N |
            | XUFXOAAUWZOOIT-SXARVLRPSA-N |
            | XUFXOAAUWZOOIT-UGEKTDRHSA-N |
            | GXJABQQUPOEUTA-RDJZCZTQSA-N |
        and the response only contains the following entries in "id"
            | id                          |
            | KTUFNOKKBVMGRW-UHFFFAOYSA-N |
            | XUFXOAAUWZOOIT-SXARVLRPSA-N |
            | XUFXOAAUWZOOIT-UGEKTDRHSA-N |
            | GXJABQQUPOEUTA-RDJZCZTQSA-N |
        and the response contains the following entries in "provided_by"
            | provided_by                       |
            | ProbeMiner compound-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                       |
            | ProbeMiner compound-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source     |
            | ProbeMiner |
        and the response contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | ProbeMiner       |
        and the response only contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | ProbeMiner       |


    Scenario: Check ProbeMiner chemical-interactions transformer
        Given the transformer
        when we fire "/chemical_interactions/transform" query with the following body:
        """
        {
            "controls": [],
            "collection":[
            {
                "attributes": [],
                "biolink_class": "ChemicalSubstance",
                "connections": [],
                "id": "canSAR:453726",
                "identifiers": {
                    "inchikey": "",
                    "cansar":"canSAR:453726"
                },
                "names_synonyms": [],
                "provided_by": "ProbeMiner producer",
                "source": "ProbeMiner"
            }]
        }
        """
        then the size of the response is 4
        and the response contains the following entries in "provided_by"
            | provided_by                                  |
            | ProbeMiner chemical interactions transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                                  |
            | ProbeMiner chemical interactions transformer |
        and the response contains the following entries in "id"
            | id               |
            | UniProtKB:A0AVT1 |
            | UniProtKB:P41226 |
            | UniProtKB:Q13564 |
            | UniProtKB:Q9UBE0 |
        and the response only contains the following entries in "id"
            | id               |
            | UniProtKB:A0AVT1 |
            | UniProtKB:P41226 |
            | UniProtKB:Q13564 |
            | UniProtKB:Q9UBE0 |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
        and the response contains the following entries in "source" of "connections" array
            | source     |
            | ProbeMiner |
        and the response only contains the following entries in "source" of "connections" array
            | source     |
            | ProbeMiner |


    Scenario: Check ProbeMiner protein-interactions transformer
        Given the transformer
        when we fire "/protein_interactions/transform" query with the following body:
        """
        {
             "controls": [],
            "collection":[
            {
                "attributes": [],
                "biolink_class": "Protein",
                "connections": [],
                "id": "UniProtKB:A0AVT1",
                "identifiers": {
                    "uniprot": "UniProtKB:A0AVT1"
                },
                "names_synonyms": [],
                "provided_by": "ProbeMiner producer",
                "source": "ProbeMiner"
            }
        ]
        }
        """
        then the size of the response is 5
        and the response contains the following entries in "provided_by"
            | provided_by                                 |
            | ProbeMiner protein interactions transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                                 |
            | ProbeMiner protein interactions transformer |
        and the response contains the following entries in "id"
            | id                          |
            | PGAMXUGSHMQFKD-BPAMBQHCSA-N |
            | MPUQHZXIXSTTDU-QXGSTGNESA-N |
            | AQGFWBQRVLPCIX-QXGSTGNESA-N |
            | IJTNGILWAIPCPO-OHNRDTAOSA-N |
            | VRTUMOBMFCLTAF-JKSBSHDWSA-N |
        and the response only contains the following entries in "id"
            | id                          |
            | PGAMXUGSHMQFKD-BPAMBQHCSA-N |
            | MPUQHZXIXSTTDU-QXGSTGNESA-N |
            | AQGFWBQRVLPCIX-QXGSTGNESA-N |
            | IJTNGILWAIPCPO-OHNRDTAOSA-N |
            | VRTUMOBMFCLTAF-JKSBSHDWSA-N |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
        and the response contains the following entries in "source" of "connections" array
            | source     |
            | ProbeMiner |
        and the response only contains the following entries in "source" of "connections" array
            | source     |
            | ProbeMiner |
