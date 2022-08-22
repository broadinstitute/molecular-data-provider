Feature: Check SIDER transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-sider-transformer.transltr.io/sider"


    Scenario: Check SIDER producer info
        Given the transformer
        when we fire "/drugs/transformer_info" query
        then the value of "name" should be "SIDER drug producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the size of "parameters" should be 1

    Scenario: Check SIDER drug producer
        Given the transformer
        when we fire "/drugs/transform" query with the following body:
        '''
        {
            "controls": [
                {
                    "name": "drug",
                    "value": "CID:2244"
                },
                {
                    "name": "drug",
                    "value": "Bortezomib"
                },
                {
                    "name": "drug",
                    "value": "acetaminophen"
                }
            ]
        }
        '''
        then the size of the response is 3
        and the response contains the following entries in "id"
            | id         |
            | CID:2244   |
            | CID:387447 |
            | CID:1983   |
        and the response only contains the following entries in "id"
            | id         |
            | CID:2244   |
            | CID:387447 |
            | CID:1983   |
        and the response contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | SIDER            |
        and the response only contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | SIDER            |
        and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by         |
            | SIDER drug producer |
        and the response only contains the following entries in "provided_by" of "attributes" array
            | provided_by         |
            | SIDER drug producer |



    Scenario: Check SIDER side effects transformer info
        Given the transformer
        when we fire "/sideeffects/transformer_info" query
        then the value of "name" should be "SIDER side effect transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "DiseaseOrPhenotypicFeature"
        and the size of "parameters" should be 0

    Scenario: Check SIDER side effects transformer
        Given the transformer
        when we fire "/sideeffects/transform" query with the following body:
        '''
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "ChEMBL:CHEMBL25",
                    "identifiers": {
                        "pubchem": "CID:119"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                }
            ]
        }
        '''
        then the size of the response is 6
        and the response contains the following entries in "id"
            | id            |
            | UMLS:C0002792 |
            | UMLS:C0002994 |
            | UMLS:C0030193 |
            | UMLS:C0042109 |
            | UMLS:C0151828 |
            | UMLS:C0863083 |
        and the response only contains the following entries in "id"
            | id            |
            | UMLS:C0002792 |
            | UMLS:C0002994 |
            | UMLS:C0030193 |
            | UMLS:C0042109 |
            | UMLS:C0151828 |
            | UMLS:C0863083 |
        and the response contains the following entries in "source"
            | source |
            | SIDER  |
        and the response only contains the following entries in "source"
            | source |
            | SIDER  |
        and the response contains the following entries in "provided_by"
            | provided_by                   |
            | SIDER side effect transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                   |
            | SIDER side effect transformer |



    Scenario: Check SIDER indications transformer info
        Given the transformer
        when we fire "/indications/transformer_info" query
        then the value of "name" should be "SIDER indication transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "DiseaseOrPhenotypicFeature"
        and the size of "parameters" should be 0

    Scenario: Check SIDER indications transformer
        Given the transformer
        when we fire "/indications/transform" query with the following body:
        '''
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "ChEMBL:CHEMBL25",
                    "identifiers": {
                        "pubchem": "CID:143"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                }
            ]
        }
        '''
        then the size of the response is 3
        and the response contains the following entries in "id"
            | id            |
            | UMLS:C0007102 |
            | UMLS:C0009402 |
            | UMLS:C1527249 |
        and the response only contains the following entries in "id"
            | id            |
            | UMLS:C0007102 |
            | UMLS:C0009402 |
            | UMLS:C1527249 |
        and the response contains the following entries in "source"
            | source |
            | SIDER  |
        and the response only contains the following entries in "source"
            | source |
            | SIDER  |
        and the response contains the following entries in "provided_by"
            | provided_by                  |
            | SIDER indication transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                  |
            | SIDER indication transformer |
    

    
    