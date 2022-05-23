Feature: Check Drugbank transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-drugbank-transformer.ci.transltr.io/drugbank"


    Scenario: Check DrugBank producer info
        Given the transformer
        when we fire "/compounds/transformer_info" query
        then the value of "name" should be "DrugBank compound-list producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the size of "parameters" should be 1


    Scenario: Check DrugBank molecules producer info
        Given the transformer
        when we fire "/molecules/transformer_info" query
        then the value of "name" should be "DrugBank molecule-list producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "MolecularEntity"
        and the size of "parameters" should be 1


    Scenario: Check DrugBank gene target transformer info
        Given the transformer
        when we fire "/gene_targets/transformer_info" query
        then the value of "name" should be "DrugBank target genes transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the size of "parameters" should be 0


    Scenario: Check DrugBank protein target transformer info
        Given the transformer
        when we fire "/protein_targets/transformer_info" query
        then the value of "name" should be "DrugBank target proteins transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "protein"
        and the size of "parameters" should be 0


    Scenario: Check DrugBank compound-list producer
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
        and the response contains the following entries in "id"
            | id               |
            | DrugBank:DB00945 |
        and the response only contains the following entries in "id"
            | id               |
            | DrugBank:DB00945 |
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | DrugBank compound-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | DrugBank compound-list producer |
        and the response contains the following entries in "pubchem" of "identifiers"
            | pubchem  |
            | CID:2244 |
        and the response only contains the following entries in "pubchem" of "identifiers"
            | pubchem  |
            | CID:2244 |
        and the response contains the following entries in "drugbank" of "identifiers"
            | drugbank         |
            | DrugBank:DB00945 |
        and the response only contains the following entries in "drugbank" of "identifiers"
            | drugbank         |
            | DrugBank:DB00945 |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source   |
            | DrugBank |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                 |
            | Acetylsalicylic acid |
        and the response contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
        and the response only contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |


    Scenario: Check DrugBank molecule-list producer
        Given the transformer
        when we fire "/molecules/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compounds",
                    "value": "DrugBank:DB00002;DrugBank:DB00006"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "id"
            | id               |
            | DrugBank:DB00002 |
            | DrugBank:DB00006 |
        and the response only contains the following entries in "id"
            | id               |
            | DrugBank:DB00002 |
            | DrugBank:DB00006 |
        and the response contains the following entries in "provided_by"
            | provided_by                          |
            | DrugBank molecule-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                          |
            | DrugBank molecule-list producer |
        and the response contains the following entries in "unii" of "identifiers"
            | unii            |
            | UNII:TN9BEX005G |
            | UNII:PQX0D8J21J |
        and the response only contains the following entries in "unii" of "identifiers"
            | unii            |
            | UNII:TN9BEX005G |
            | UNII:PQX0D8J21J |
        and the response contains the following entries in "drugbank" of "identifiers"
            | drugbank         |
            | DrugBank:DB00002 |
            | DrugBank:DB00006 |
        and the response only contains the following entries in "drugbank" of "identifiers"
            | drugbank         |
            | DrugBank:DB00002 |
            | DrugBank:DB00006 |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source   |
            | DrugBank |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name        |
            | Cetuximab   |
            | Bivalirudin |


    Scenario: Check DrugBank target-list producer using DrugBank ID
        Given the transformer
        when we fire "/gene_targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "ChemicalSubstance",
                    "id": "CID:2244",
                    "provided_by": "drugbank",
                    "source": "drugbank",
                    "identifiers": {
                        "drugbank": "DrugBank:DB00945"
                    }
                }
            ]
        }
        """
        then the size of the response is 28


    Scenario: Check DrugBank target-list producer using pubchem ID
        Given the transformer
        when we fire "/gene_targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "ChemicalSubstance",
                    "id": "CID:2244",
                    "provided_by": "drugbank",
                    "source": "drugbank",
                    "identifiers": {
                        "pubchem": "CID:2244"
                    }
                }
            ]
        }
        """
        then the size of the response is 28

