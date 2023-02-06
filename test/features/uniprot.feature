Feature: Check UniProt transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-uniprot-transformer.ci.transltr.io/uniprot"

    Scenario: Check UniProt Protein producer info
        Given the transformer
        when we fire "/molecules/transformer_info" query
        then the size of "parameters" should be 1
        and the value of "name" should be "UniProt protein-list producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "protein"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "release-2022_04 (2022-10-12)"
        and the value of "label" should be "UniProt"
    
    Scenario: Check UniProt Gene transformer info
        Given the transformer
        when we fire "/genes/transformer_info" query
        then the size of "parameters" should be 0
        and the value of "name" should be "UniProt protein to gene transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "protein"
        and the value of "knowledge_map.output_class" should be "gene"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "release-2022_04 (2022-10-12)"
        and the value of "label" should be "UniProt"
    
    Scenario: Check UniProt Protein transformer info
        Given the transformer
        when we fire "/proteins/transformer_info" query
        then the size of "parameters" should be 0
        and the value of "name" should be "UniProt gene to protein transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "gene"
        and the value of "knowledge_map.output_class" should be "protein"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "release-2022_04 (2022-10-12)"
        and the value of "label" should be "UniProt"

    Scenario: Check UniProt Protein transformer
        Given the transformer
        when we fire "/molecules/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "protein",
                    "value": "ENSEMBL:ENSP00000269305"
                },
                {
                    "name": "protein",
                    "value": "UniProtKB:P04637"
                },
                {
                    "name": "protein",
                    "value": "neurotrimin"
                }
            ]
        }
        """
        then the size of the response is 9
        and the response contains the following entries in "id"
            | id                          |
            | UniProtKB:P04637            |
            | UniProtKB:Q9P121            |
            | UniProtKB:B7Z1Z5            |
            | UniProtKB:C9J0V2            |
            | UniProtKB:C9JK95            |
            | UniProtKB:H7BZ62            |
            | UniProtKB:F6WFR7            |
            | UniProtKB:F8VTR5            |
            | UniProtKB:F8W8Y1            |
        and the response only contains the following entries in "id"
            | id                          |
            | UniProtKB:P04637            |
            | UniProtKB:Q9P121            |
            | UniProtKB:B7Z1Z5            |
            | UniProtKB:C9J0V2            |
            | UniProtKB:C9JK95            |
            | UniProtKB:H7BZ62            |
            | UniProtKB:F6WFR7            |
            | UniProtKB:F8VTR5            |
            | UniProtKB:F8W8Y1            |
        and the response contains the following entries in "source"
            | source   |
            | UniProt  |
        and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by                     |
            | UniProt protein-list producer   |
        and the response only contains the following entries in "provided_by" of "attributes" array
            | provided_by                     |
            | UniProt protein-list producer   |


    Scenario: Check UniProt Protein transformer with single protein
        Given the transformer
        when we fire "/molecules/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "protein",
                    "value": "ENSEMBL:ENSP00000269305"
                },
                {
                    "name": "protein",
                    "value": "UniProtKB:P04637"
                }
            ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "id"
            | id                          |
            | UniProtKB:P04637            |
        and the response only contains the following entries in "id"
            | id                          |
            | UniProtKB:P04637            |
        and the response contains the following entries in "source"
            | source   |
            | UniProt  |
        and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by                     |
            | UniProt protein-list producer   |
        and the response only contains the following entries in "provided_by" of "attributes" array
            | provided_by                     |
            | UniProt protein-list producer   |


    Scenario: Check UniProt Gene transformer
        Given the transformer
        when we fire "/genes/transform" query with the following body:
        """
        {
            "collection": [
                {
                    "biolink_class": "Protein",
                    "id": "UniProtKB:P31947",
                    "identifiers": {
                        "uniprot": "UniProtKB:P31947"
                    },
                    "provided_by": "MoleProDB node producer",
                    "source": "MolePro"
                }
            ],
            "controls": []
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "id"
            | id            |
            | HGNC:10773    |
        and the response contains the following entries in "source"
            | source   |
            | UniProt  |
        and the response contains the following entries in "provided_by"
            | provided_by                           |
            | UniProt protein to gene transformer   |
        and the response only contains the following entries in "provided_by"
            | provided_by                           |
            | UniProt protein to gene transformer   |
    
    Scenario: Check UniProt Protein transformer
        Given the transformer
        when we fire "/proteins/transform" query with the following body:
        """
        {
            "collection": [
                {
                    "biolink_class": "Genes",
                    "id": "HGNC:12852",
                    "identifiers": {
                        "hgnc": "HGNC:12852"
                    },
                    "provided_by": "MoleProDB node producer",
                    "source": "MolePro"
                }
            ],
            "controls": []
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "id"
            | id                  |
            | UniProtKB:P61981    |
        and the response contains the following entries in "source"
            | source   |
            | UniProt  |
        and the response contains the following entries in "provided_by"
            | provided_by                           |
            | UniProt gene to protein transformer   |
        and the response only contains the following entries in "provided_by"
            | provided_by                           |
            | UniProt gene to protein transformer   |




