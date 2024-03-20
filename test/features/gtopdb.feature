Feature: Check GtoPdb transformer

    Background: Specify transformer API
    
        Given a transformer at "https://translator.broadinstitute.org/gtopdb"

    Scenario: Check transformer info
        Given the transformer
        when we fire "/molecules/transformer_info" query
        then the value of "name" should be "GtoPdb compound-list producer"
        and the value of "label" should be "GtoPdb"
        and the value of "version" should be "2.5.0"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "ChemicalEntity"
        and the value of "properties.source_version" should be "2023.2 (2023-08-07)"
        and the size of "parameters" should be 1


    Scenario: Check transformer info
        Given the transformer
        when we fire "/targets/transformer_info" query
        then the value of "name" should be "GtoPdb target transformer"
        and the value of "label" should be "GtoPdb"
        and the value of "version" should be "2.5.0"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the value of "properties.source_version" should be "2023.2 (2023-08-07)"
        and the size of "parameters" should be 0


    Scenario: Check GtoPdb compound-list producer with name
        Given the transformer
        when we fire "/molecules/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compound",
                    "value": "aspirin"
                }
            ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "id"
            | id       |
            | GTOPDB:4139 |
        and the response only contains the following entries in "id"
            | id       |
            | GTOPDB:4139 |


    Scenario: Check GtoPdb compound-list producer with CID
        Given the transformer
        when we fire "/molecules/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compound",
                    "value": "CID:2244"
                }
            ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "id"
            | id       |
            | GTOPDB:4139 |
        and the response only contains the following entries in "id"
            | id       |
            | GTOPDB:4139 |


    Scenario: Check GtoPdb compound-list producer with ligand id
        Given the transformer
        when we fire "/molecules/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compound",
                    "value": "GtoPdb:4829"
                }
            ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "id"
            | id       |
            | GTOPDB:4829 |
        and the response only contains the following entries in "id"
            | id       |
            | GTOPDB:4829 |


    Scenario: Check GtoPdb compound-list producer with two names
        Given the transformer
        when we fire "/molecules/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compound",
                    "value": "bortezomib"
                },
                {
                    "name": "compound",
                    "value": "aspirin"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "id"
            | id          |
            | GTOPDB:6391 |
            | GTOPDB:4139 |
        and the response only contains the following entries in "id"
            | id          |
            | GTOPDB:6391 |
            | GTOPDB:4139 |
        and the value of "[0].names_synonyms[0].name" should be "bortezomib"
        and the value of "[1].names_synonyms[0].name" should be "aspirin"



    Scenario: Check GtoPdb multi-compound-list producer
        Given the transformer
        when we fire "/molecules/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compound",
                    "value": "bortezomib"
                },
                {   
                    "name": "compound",
                    "value": "CID:2244"
                },
                {   
                    "name": "compound",
                    "value": "GTOPDB:4050"
                }
            ]
        }
        """
        then the size of the response is 3
        and the response contains the following entries in "id"
            | id          |
            | GTOPDB:4050 |
            | GTOPDB:6391 |
            | GTOPDB:4139 |
        and the response only contains the following entries in "id"
            | id          |
            | GTOPDB:6391 |
            | GTOPDB:4139 |
            | GTOPDB:4050 |


    Scenario: Check GtoPdb targets transformer
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class":"ChemicalSubstance",
                    "provided_by": "inxight_drugs",
                    "source": "inxight_drugs",
                    "id": "CID:2244",
                    "identifiers": {
                        "drugbank": "DrugBank:DB00945",
                        "pubchem": "CID:2244"
                    }
                }
            ]
        }
        """
        then the size of the response is 3
        and the response contains the following entries in "id"
            | id        |
            | HGNC:101  |
            | HGNC:9604 |
            | HGNC:9605 |
        and the response only contains the following entries in "id"
            | id        |
            | HGNC:101  |
            | HGNC:9604 |
            | HGNC:9605 |


    Scenario: Check GtoPdb targets transformer
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
        	{
            	  "biolink_class": "ChemicalSubstance",
            	  "provided_by": "inxight_drugs",
            	  "source": "inxight_drugs",
            	  "id": "DrugBank:DB00945",
            	  "identifiers":{
                      "drugbank": "DrugBank:DB00945",
                      "chembl": "ChEMBL:CHEMBL25"
                  }
                }   
            ]
        }
        """
        then the size of the response is 0


    Scenario: Check GtoPdb targets transformer
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
        	{
            	  "biolink_class": "ChemicalSubstance",
            	  "provided_by": "inxight_drugs",
            	  "source": "inxight_drugs",
            	  "id": "GTOPDB:9736",
            	  "identifiers":{
                      "gtopdb": "GTOPDB:9736"
                  }
                }   
            ]
        }
        """
        then the size of the response is 1


    Scenario: Check GtoPdb inhibitors transformer
        Given the transformer
        when we fire "/inhibitors/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {   
                    "biolink_class":"ChemicalSubstance",
                    "provided_by": "inxight_drugs",
                    "source": "inxight_drugs",
                    "id": "HGNC:3538",
                    "identifiers": {
                        "hgnc": "HGNC:3538"
                    }
                }
            ]
        }
        """
        then the size of the response is 23
