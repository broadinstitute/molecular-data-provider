Feature: Check DSSToxDB transformer
    Background: Specify transformer API
        Given a transformer at "https://molepro-dsstoxdb-transformer.test.transltr.io/dsstoxdb"


    Scenario: Check DSSToxDB chemical producer info
        Given the transformer
        when we fire "/chemical/transformer_info" query
        then the value of "name" should be "DSSToxDB chemical producer"
        and the value of "label" should be "DSSToxDB"
        and the value of "infores" should be "infores:dsstoxdb"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "ChemicalEntity"
        and the size of "parameters" should be 1
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "7 (2024-04-10)"
       

    Scenario: Check DSSToxDB chemical producer with native identifier
        Given the transformer
        when we fire "/chemical/transform" query with the following body:        
        """
            {"name": "DSSToxDB producer", 
            "controls": [
                {"name": "chemical",
                "value": "comptox:DTXSID2020006"
                }
            ]
            }
        """
        then the size of the response is 1
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | DSSToxDB chemical producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | DSSToxDB chemical producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source   |
            | DSSToxDB |
        and the response may contain the following entries in "comptox" of "identifiers"
            |   comptox               |
            |   comptox:DTXSID2020006 |
        and the response contains the following entries in "provided_by" of "names_synonyms" array
            | provided_by                |
            | DSSToxDB chemical producer |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name             |
            | Acetaminophen    |


Scenario: Check DSSToxDB chemical producer with preferred name
        Given the transformer
        when we fire "/chemical/transform" query with the following body:        
        """
            {"name": "DSSToxDB producer", 
            "controls": [
                {"name": "chemical",
                "value": "Acetaminophen"
                }
            ]
            }
        """
        then the size of the response is 1
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | DSSToxDB chemical producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | DSSToxDB chemical producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source   |
            | DSSToxDB |
        and the response may contain the following entries in "comptox" of "identifiers"
            |   comptox               |
            |   comptox:DTXSID2020006 |
        and the response contains the following entries in "provided_by" of "names_synonyms" array
            | provided_by                |
            | DSSToxDB chemical producer |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name             |
            | Acetaminophen    |


Scenario: Check DSSToxDB chemical producer with INCHIKEY
        Given the transformer
        when we fire "/chemical/transform" query with the following body:        
        """
            {"name": "DSSToxDB producer", 
            "controls": [
                {"name": "chemical",
                "value": "INCHIKEY:FERIUCNNQQJTOY-AZXPZELESA-N"
                }
            ]
            }
        """
        then the size of the response is 1
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | DSSToxDB chemical producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | DSSToxDB chemical producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source   |
            | DSSToxDB |
        and the response may contain the following entries in "comptox" of "identifiers"
            |   comptox                |
            |   comptox:DTXSID10431003 |
        and the response contains the following entries in "provided_by" of "names_synonyms" array
            | provided_by                |
            | DSSToxDB chemical producer |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name               |
            | Butyric acid-1-13C |