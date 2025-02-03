Feature: Check DGIdb transformer

    Background: Specify transformer API
        Given a transformer at "https://translator.broadinstitute.org/dgidb"


    Scenario: Check DGIdb producer info
        Given the transformer
        when we fire "/molecules/transformer_info" query
        then the value of "name" should be "DGIdb compound-list producer"
        and the value of "label" should be "DGIdb"
        and the value of "infores" should be "infores:dgidb"
        and the value of "version" should be "2.6.0"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "SmallMolecule"
        and the value of "properties.source_version" should be "v5"
        and the value of "properties.source_date" should be "2024-11-27"
        and the size of "parameters" should be 1


    Scenario: Check DGIdb target transformer info
        Given the transformer
        when we fire "/targets/transformer_info" query
        then the value of "name" should be "DGIdb target transformer"
        and the value of "label" should be "DGIdb"
        and the value of "infores" should be "infores:dgidb"
        and the value of "version" should be "2.6.0"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the value of "properties.source_version" should be "v5"
        and the value of "properties.source_date" should be "2024-11-27"
        and the size of "parameters" should be 0


    Scenario: Check DGIdb inhibitor transformer info
        Given the transformer
        when we fire "/inhibitors/transformer_info" query
        then the value of "name" should be "DGIdb inhibitor transformer"
        and the value of "label" should be "DGIdb"
        and the value of "infores" should be "infores:dgidb"
        and the value of "version" should be "2.6.0"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "gene"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "properties.source_version" should be "v5"
        and the value of "properties.source_date" should be "2024-11-27"
        and the size of "parameters" should be 0


    Scenario: Check DGIdb compound-list producer
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
            | id              |
            | ChEMBL:CHEMBL25 |
        and the response only contains the following entries in "id"
            | id              |
            | ChEMBL:CHEMBL25 |
        and the response contains the following entries in "source"
            | source |
            | DGIdb  |
        and the response only contains the following entries in "source"
            | source |
            | DGIdb  |
        and the response contains the following entries in "chembl" of "identifiers"
            | chembl          |
            | ChEMBL:CHEMBL25 |
        and the response only contains the following entries in "chembl" of "identifiers"
            | chembl          |
            | ChEMBL:CHEMBL25 |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source   |
            | DGIdb |

    Scenario: Check DGIdb target transformer using ChEMBL id
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
    	   "controls": [],
    	   "collection": [
               {
            	  "biolink_class": "SmallMolecule",
                  "provided_by": "dgidb",
                  "source": "dgidb",
                  "id": "CHEMBL25",
                  "identifiers": {
                        "chembl": "CHEMBL:CHEMBL25"
                   }
               }
            ]
         }

        """
        then the size of the response is 89
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CHEMBL25          |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CHEMBL25          |

    Scenario: Check DGIdb target transformer with no ChEMBL id
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "provided_by": "dgidb",
                    "source": "dgidb",
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
                    "biolink_class": "SmallMolecule",
                    "provided_by": "dgidb",
                    "source": "dgidb",
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
                    "biolink_class": "Gene",
                    "provided_by": "dgidb",
                    "source": "dgidb",
                    "id": "HGNC:9604",
                    "identifiers": {
                        "entrez": "NCBIGene:5742"
                    }
                }
            ]
        }
        """
        then the size of the response is 82
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | HGNC:9604         |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | HGNC:9604         |


    Scenario: Check DGIdb inhibitor transformer with no gene id
        Given the transformer
        when we fire "/inhibitors/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "Gene",
                    "provided_by": "dgidb",
                    "source": "dgidb",
                    "id": "HGNC:9604",
                    "identifiers": {
                        "hgnc": "HGNC:9604"
                    }
                }
            ]
        }
        """
        then the size of the response is 82
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | HGNC:9604         |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | HGNC:9604         |


    Scenario: Check DGIdb inhibitor transformer with null gene id
        Given the transformer
        when we fire "/inhibitors/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "Gene",
                    "provided_by": "dgidb",
                    "source": "dgidb",
                    "id": "HGNC:9604",
                    "identifiers": {
                        "hgnc": "HGNC:9604",
                        "entrez": null
                    }
                }
            ]
        }
        """
        then the size of the response is 82
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | HGNC:9604         |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | HGNC:9604         |

