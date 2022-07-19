Feature: Check CMAP transformer

    Background: Specify transformer API
        Given a transformer at "https://translator.broadinstitute.org/pubchem"


    Scenario: Check transformer info
        Given the transformer
        when we fire "/compounds/transformer_info" query
        then the value of "name" should be "Pubchem compound-list producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the size of "knowledge_map" should be 4
        and the size of "parameters" should be 1
        and the value of "version" should be "2.4.1"
        and the value of "properties.source_version" should be "2022-05-11"
        and the value of "label" should be "PubChem"


    Scenario: Check neighbor transformer info
        Given the transformer
        when we fire "/neighbors/transformer_info" query
        then the value of "name" should be "PubChem chemical similarity transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "compound"
        and the size of "knowledge_map" should be 4
        and the size of "parameters" should be 0
        and the size of "knowledge_map.nodes" should be 1
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "2022-05-11"
        and the value of "label" should be "PubChem"


    Scenario: Check PubChem producer - name
        Given the transformer
        when we fire "/compounds/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compound",
                    "value": "aspirin"
                },
                {
                    "name": "compound",
                    "value": "Velcade"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "id"
            | id         |
            | CID:2244   |
            | CID:387447 |
        and the response only contains the following entries in "id"
            | id         |
            | CID:2244   |
            | CID:387447 |
        and the response contains the following entries in "source"
            | source  |
            | PubChem |
        and the response only contains the following entries in "source"
            | source  |
            | PubChem |
        and the response contains the following entries in "provided_by"
            | provided_by                    |
            | Pubchem compound-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                    |
            | Pubchem compound-list producer |


    Scenario: Check PubChem producer - InChIKey
        Given the transformer
        when we fire "/compounds/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compound",
                    "value": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                }
            ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "id"
            | id         |
            | CID:2244   |
        and the response only contains the following entries in "id"
            | id         |
            | CID:2244   |
        and the response contains the following entries in "source"
            | source  |
            | PubChem |
        and the response only contains the following entries in "source"
            | source  |
            | PubChem |
        and the response contains the following entries in "provided_by"
            | provided_by                    |
            | Pubchem compound-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                    |
            | Pubchem compound-list producer |


    Scenario: Check PubChem producer - CID
        Given the transformer
        when we fire "/compounds/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compound",
                    "value": "CID:2244"
                },
                {
                    "name": "compound",
                    "value": "CID:387447"
                },
                {
                    "name": "compound",
                    "value": "CID:5360728"
                }
            ]
        }
        """
        then the size of the response is 3
        and the response contains the following entries in "id"
            | id         |
            | CID:2244   |
            | CID:6666   |
            | CID:387447 |
        and the response only contains the following entries in "id"
            | id         |
            | CID:2244   |
            | CID:6666   |
            | CID:387447 |
        and the response contains the following entries in "source"
            | source  |
            | PubChem |
        and the response only contains the following entries in "source"
            | source  |
            | PubChem |
        and the response contains the following entries in "provided_by"
            | provided_by                    |
            | Pubchem compound-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                    |
            | Pubchem compound-list producer |


    Scenario: Check PubChem chemical similarity transformer
        Given the transformer
        when we fire "/neighbors/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "CID:86",
                    "identifiers": {
                        "pubchem": "CID:86"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                },
                {
                    "biolink_class": "SmallMolecule",
                    "id": "CID:20591",
                    "identifiers": {
                        "pubchem": "CID:20591"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                }
            ]
        }
        """
        then the size of the response is 21
        and the response contains the following entries in "id"
            | id            |
            | CID:86        |
            | CID:89        |
            | CID:11811     |
            | CID:20591     |
            | CID:95222     |
            | CID:151484    |
            | CID:164592    |
            | CID:440736    |
            | CID:440741    |
            | CID:443218    |
            | CID:3084521   |
            | CID:5743254   |
            | CID:6604307   |
            | CID:21145116  |
            | CID:49791998  |
            | CID:51377238  |
            | CID:54675871  |
            | CID:54686733  |
            | CID:54691710  |
            | CID:86205004  |
            | CID:157010391 |
        and the response only contains the following entries in "id"
            | id            |
            | CID:86        |
            | CID:89        |
            | CID:11811     |
            | CID:20591     |
            | CID:95222     |
            | CID:151484    |
            | CID:164592    |
            | CID:440736    |
            | CID:440741    |
            | CID:443218    |
            | CID:3084521   |
            | CID:5743254   |
            | CID:6604307   |
            | CID:21145116  |
            | CID:49791998  |
            | CID:51377238  |
            | CID:54675871  |
            | CID:54686733  |
            | CID:54691710  |
            | CID:86205004  |
            | CID:157010391 |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:86            |
            | CID:20591         |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:86            |
            | CID:20591         |
        and the response contains the following entries in "source"
            | source  |
            | PubChem |
        and the response only contains the following entries in "source"
            | source  |
            | PubChem |
        and the response contains the following entries in "provided_by"
            | provided_by                             |
            | PubChem chemical similarity transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                             |
            | PubChem chemical similarity transformer |
