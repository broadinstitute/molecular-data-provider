Feature: Check DGIdb transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-dgidb-transformer.test.transltr.io/dgidb"


    Scenario: Check DGIdb producer info
        Given the transformer
        when we fire "/molecules/transformer_info" query
        then the value of "name" should be "DGIdb compound-list producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the size of "parameters" should be 1


    Scenario: Check DGIdb target transformer info
        Given the transformer
        when we fire "/targets/transformer_info" query
        then the value of "name" should be "DGIdb target transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the size of "parameters" should be 0


    Scenario: Check DGIdb inhibitor transformer info
        Given the transformer
        when we fire "/inhibitors/transformer_info" query
        then the value of "name" should be "DGIdb inhibitor transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "gene"
        and the value of "knowledge_map.output_class" should be "compound"
        and the size of "parameters" should be 0


    Scenario: Check DGIdb compound-list producer
        Given the transformer
        when we fire "/molecules/transform" query with the following body:
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
            | id              |
            | ChEMBL:CHEMBL25 |
        and the response only contains the following entries in "id"
            | id              |
            | ChEMBL:CHEMBL25 |
        and the response contains the following entries in "source"
            | source                          |
            | DGIdb compound-list producer |
        and the response only contains the following entries in "source"
            | source                          |
            | DGIdb compound-list producer |
        and the response contains the following entries in "chembl" of "identifiers"
            | chembl          |
            | ChEMBL:CHEMBL25 |
        and the response only contains the following entries in "chembl" of "identifiers"
            | chembl          |
            | ChEMBL:CHEMBL25 |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source   |
            | DGIdb |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                 |
            | aspirin              |
            | Acetylsalicylic Acid |


    Scenario: Check DGIdb target transformer using ChEMBL id
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "ChEMBL:CHEMBL25",
                    "identifiers": {
                        "chembl": "ChEMBL:CHEMBL25"
                    }
                }
            ]
        }
        """
        then the size of the response is 37


    Scenario: Check DGIdb target transformer with no ChEMBL id
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "CID:2244",
                    "identifiers": {
                        "pubchem": "CID:2244"
                    }
                }
            ]
        }
        """
        then the size of the response is 0


    Scenario: Check DGIdb target transformer with null ChEMBL id
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "CID:2244",
                    "identifiers": {
                        "pubchem": "CID:2244",
                        "chembl": null
                    }
                }
            ]
        }
        """
        then the size of the response is 0


    Scenario: Check DGIdb inhibitor transformer
        Given the transformer
        when we fire "/inhibitors/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "HGNC:9604",
                    "identifiers": {
                        "entrez": "NCBIGene:5742"
                    }
                }
            ]
        }
        """
        then the size of the response is 88


    Scenario: Check DGIdb inhibitor transformer with no gene id
        Given the transformer
        when we fire "/inhibitors/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "HGNC:9604",
                    "identifiers": {
                        "hgnc": "HGNC:9604"
                    }
                }
            ]
        }
        """
        then the size of the response is 0


    Scenario: Check DGIdb inhibitor transformer with null gene id
        Given the transformer
        when we fire "/inhibitors/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "HGNC:9604",
                    "identifiers": {
                        "hgnc": "HGNC:9604",
                        "entrez": null
                    }
                }
            ]
        }
        """
        then the size of the response is 0

