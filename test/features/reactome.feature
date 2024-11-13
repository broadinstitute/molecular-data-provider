Feature: Check Reactome  transformer
    Background: Specify transformer API
        Given a transformer at "https://translator.broadinstitute.org/reactome"


    Scenario: Check Reactome entity producer info
        Given the transformer
        when we fire "/entity-producer/transformer_info" query
        then the value of "name" should be "Reactome entity-list producer"
        and the value of "label" should be "Reactome"
        and the value of "infores" should be "infores:reactome"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "PhysicalEntity"
        and the size of "parameters" should be 1
        and the value of "version" should be "2.5.0"


    Scenario: Check Reactome reaction producer info
        Given the transformer
        when we fire "/reaction-producer/transformer_info" query
        then the value of "name" should be "Reactome reaction-list producer"
        and the value of "label" should be "Reactome"
        and the value of "infores" should be "infores:reactome"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "MolecularActivity"
        and the size of "parameters" should be 1
        and the value of "version" should be "2.5.0"


    Scenario: Check Reactome complex producer info
        Given the transformer
        when we fire "/complex-producer/transformer_info" query
        then the value of "name" should be "Reactome complex-list producer"
        and the value of "label" should be "Reactome"
        and the value of "infores" should be "infores:reactome"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "MacromolecularComplex"
        and the size of "parameters" should be 1
        and the value of "version" should be "2.5.0"


    Scenario: Check Reactome pathway producer info
        Given the transformer
        when we fire "/pathway-producer/transformer_info" query
        then the value of "name" should be "Reactome pathway-list producer"
        and the value of "label" should be "Reactome"
        and the value of "infores" should be "infores:reactome"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "Pathway"
        and the size of "parameters" should be 1
        and the value of "version" should be "2.5.0"


    Scenario: Check Reactome interaction transformer info
        Given the transformer
        when we fire "/interaction/transformer_info" query
        then the value of "name" should be "Reactome interaction transformer"
        and the value of "label" should be "Reactome"
        and the value of "infores" should be "infores:reactome"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "PhysicalEntity"
        and the value of "knowledge_map.output_class" should be "PhysicalEntity"
        and the size of "parameters" should be 0
        and the value of "version" should be "2.5.0"


    Scenario: Check Reactome reaction transformer info
        Given the transformer
        when we fire "/reaction/transformer_info" query
        then the value of "name" should be "Reactome reaction transformer"
        and the value of "label" should be "Reactome"
        and the value of "infores" should be "infores:reactome"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "PhysicalEntity"
        and the value of "knowledge_map.output_class" should be "MolecularActivity"
        and the size of "parameters" should be 0
        and the value of "version" should be "2.5.0" 

    Scenario: Check Reactome complex transformer info
        Given the transformer
        when we fire "/complex/transformer_info" query
        then the value of "name" should be "Reactome complex transformer"
        and the value of "label" should be "Reactome"
        and the value of "infores" should be "infores:reactome"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "PhysicalEntity"
        and the value of "knowledge_map.output_class" should be "MacromolecularComplex"
        and the size of "parameters" should be 0
        and the value of "version" should be "2.5.0" 

    Scenario: Check Reactome pathway transformer info
        Given the transformer
        when we fire "/pathway/transformer_info" query
        then the value of "name" should be "Reactome pathway transformer"
        and the value of "label" should be "Reactome"
        and the value of "infores" should be "infores:reactome"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "MacromolecularComplex"
        and the value of "knowledge_map.output_class" should be "Pathway"
        and the size of "parameters" should be 0
        and the value of "version" should be "2.5.0"         

    Scenario: Check Reactome entity producer with reactome native id
        Given the transformer
        when we fire "/entity-producer/transform" query with the following body:        
        """
            {"name": "Reactome entity-list producer", 
             "controls": [
                {
                    "name": "entity",
                    "value": "reactome:R-HSA-976878"
                }
                ]
            }
        """
        then the size of the response is 1
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | Reactome entity-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | Reactome entity-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source   |
            | Reactome |
        and the response may contain the following entries in "reactome" of "identifiers"
            |   reactome              |
            |   Reactome:R-HSA-976878 |
        and the response may contain the following entries in "uniprot" of "identifiers"
            |   uniprot               |
            |   UniProtKB:Q9Y287      |    
        and the response contains the following entries in "provided_by" of "names_synonyms" array
            | provided_by                           |
            | Reactome entity-list producer |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                          |
            | ITM2B(244-266)                |


    Scenario: Check Reactome entity producer
        Given the transformer
        when we fire "/entity-producer/transform" query with the following body:        
        """
            {"name": "Reactome entity-list producer", 
            "controls": [
                {"name": "entity",
                "value": "ITM2B(244-266)"
                },
                {"name": "entity",
                "value": "JADE1"
                }    
            ]
            }
        """
        then the size of the response is 6
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | Reactome entity-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | Reactome entity-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source   |
            | Reactome |
        and the response may contain the following entries in "reactome" of "identifiers"
            |   reactome              |
            |   Reactome:R-HSA-976878 |
            |   Reactome:R-CFA-452931 |
            |   Reactome:R-SSC-452931 |
            |   Reactome:R-BTA-452931 |
        and the response contains the following entries in "provided_by" of "names_synonyms" array
            | provided_by                           |
            | Reactome entity-list producer |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name              |
            | ITM2B(244-266)    |


    Scenario: Check Reactome reaction producer
        Given the transformer
        when we fire "/reaction-producer/transform" query with the following body:        
        """
        {"name": "Reactome reaction-list producer", 
        "controls": [
            {"name": "reaction",
            "value": "USP1:WDR48 deubiquitinates monoUb:K164-PCNA"
            },
            {"name": "reaction",
            "value": "PGM2:Mg2+ isomerises R1P to R5P"
            }
        ]
        }
        """
        then the size of the response is 25
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | Reactome reaction-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | Reactome reaction-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source   |
            | Reactome |
        and the response may contain the following entries in "reactome" of "identifiers"
            |   reactome              |
            |   Reactome:R-RNO-5655466 |
            |   Reactome:R-XTR-5655466 |
            |   Reactome:R-BTA-5655466 |
            |   Reactome:R-DRE-5655466 |
            |   Reactome:R-SPO-5655466 |
            |   Reactome:R-SSC-5655466 |
            |   Reactome:R-HSA-5655466 |
            |   Reactome:R-CFA-5655466 |
            |   Reactome:R-MMU-5655466 |
            |   Reactome:R-GGA-5655466 |
            |   Reactome:R-PFA-6787329 |
            |   Reactome:R-RNO-6787329 |
            |   Reactome:R-DME-6787329 |
            |   Reactome:R-SCE-6787329 |
            |   Reactome:R-MMU-6787329 |
            |   Reactome:R-DDI-6787329 |
            |   Reactome:R-GGA-6787329 |
            |   Reactome:R-SSC-6787329 |
            |   Reactome:R-CFA-6787329 |
            |   Reactome:R-HSA-6787329 |
            |   Reactome:R-CEL-6787329 |
            |   Reactome:R-DRE-6787329 |
            |   Reactome:R-SPO-6787329 |
            |   Reactome:R-XTR-6787329 |
            |   Reactome:R-BTA-6787329 |
        and the response contains the following entries in "provided_by" of "names_synonyms" array
            | provided_by                           |
            | Reactome reaction-list producer |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name              |
            | USP1:WDR48 deubiquitinates monoUb:K164-PCNA  |


    Scenario: Check Reactome pathway producer
        Given the transformer
        when we fire "/pathway-producer/transform" query with the following body:        
        """
            {"name": "Reactome pathway-list producer", 
            "controls": [
                {"name": "pathway",
                "value": "ABC transporter disorders"
                }
            ]
            }
        """
        then the size of the response is 1
        and the response contains the following entries in "provided_by"
            | provided_by                    |
            | Reactome pathway-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                    |
            | Reactome pathway-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source   |
            | Reactome |
        and the response may contain the following entries in "reactome" of "identifiers"
            |   reactome              |
            |   Reactome:R-HSA-5619084 |
        and the response contains the following entries in "provided_by" of "names_synonyms" array
            | provided_by                    |
            | Reactome pathway-list producer |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                       |
            | ABC transporter disorders  |


    Scenario: Check Reactome complex producer
        Given the transformer
        when we fire "/complex-producer/transform" query with the following body:        
        """
            {"name": "Reactome complex-list producer", 
            "controls": [
                {"name": "complex",
                "value": "DOCK-GEFs:RAC1, CDC42"
                }
            ]
            }
        """
        then the size of the response is 1
        and the response contains the following entries in "provided_by"
            | provided_by                    |
            | Reactome complex-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                    |
            | Reactome complex-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source   |
            | Reactome |
        and the response may contain the following entries in "reactome" of "identifiers"
            |   reactome               |
            |   Reactome:R-HSA-1012969 |
        and the response contains the following entries in "provided_by" of "names_synonyms" array
            | provided_by                    |
            | Reactome complex-list producer |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                   |
            | DOCK-GEFs:RAC1, CDC42  |


    Scenario: Check Reactome interaction transformer using Reactome with UniProtKB
        Given the transformer
        when we fire "/interaction/transform" query with the following body:
        """
        {
            "collection": [
            {
                "biolink_class": "PhysicalEntity",
                "provided_by": "reactome",
                "source": "reactome",
                "id": "test-01",
                "identifiers":{
                    "uniprot":"UniProtKB:P15172",
                    "reactome":"reactome:R-HSA-445441"
                }
            }
            ],
            "controls":[]
        }
        """
        then the size of the response is 3 
        and the response contains the following entries in "source"
            | source                          |
            | Reactome interaction transformer   |
        and the response only contains the following entries in "source"
            | source                          |
            | Reactome interaction transformer   |
        and the response contains the following entries in "id"
            | id               |
            | UniProtKB:Q02078 |
            | UniProtKB:Q06413 |
            | UniProtKB:P15923 |


    Scenario: Check Reactome interaction transformer using Reactome with ChEBI
        Given the transformer
        when we fire "/interaction/transform" query with the following body:
        """
        {
            "collection": [
            {
                "biolink_class": "PhysicalEntity",
                "provided_by": "reactome",
                "source": "reactome",
                "id": "test-01",
                "identifiers":{
                    "chebi":"ChEBI:59092"
                }
            }
            ],
            "controls":[]
        }
        """
        then the size of the response is 5
        and the response contains the following entries in "source"
            | source                          |
            | Reactome interaction transformer   |
        and the response only contains the following entries in "source"
            | source                          |
            | Reactome interaction transformer   |
        and the response contains the following entries in "id"
            | id               |
            | UniProtKB:Q9UKM7 |
            | UniProtKB:Q9BV94 |
            | UniProtKB:P33908 |
            | UniProtKB:Q9NR34 |
            | UniProtKB:O60476 |


    Scenario: Check Reactome reaction transformer using Reactome
        Given the transformer
        when we fire "/reaction/transform" query with the following body:
        """
        {
            "collection": [
            {
                "biolink_class": "PhysicalEntity",
                "provided_by": "reactome",
                "source": "reactome",
                "id": "test-01",
                "identifiers":{
                    "reactome":"reactome:R-HSA-194880"
                }
            }
            ],
            "controls":[]
        }
        """
        then the size of the response is 9 
        and the response contains the following entries in "source"
            | source                          |
            | Reactome reaction transformer   |
        and the response only contains the following entries in "source"
            | source                          |
            | Reactome reaction transformer   |
        and the response contains the following entries in "id"
            | id                    |
            | Reactome:R-HSA-2316434 |


    Scenario: Check Reactome complex transformer using Reactome
        Given the transformer
        when we fire "/complex/transform" query with the following body:
        """
            {
                "collection": [
                {
                    "biolink_class": "PhysicalEntity",
                    "provided_by": "reactome",
                    "source": "reactome",
                    "id": "test-01",
                    "identifiers":{
                        "uniprot":"UniProtKB:O15525"
                    }
                }
                ],
                "controls":[]
            }
        """
        then the size of the response is 5 
        and the response contains the following entries in "source"
            | source                          |
            | Reactome complex transformer   |
        and the response only contains the following entries in "source"
            | source                          |
            | Reactome complex transformer   |
        and the response contains the following entries in "id"
            | id                     |
            | Reactome:R-HSA-1008229 |
            | Reactome:R-HSA-9761745 |
            | Reactome:R-HSA-9761748 |
            | Reactome:R-HSA-1008206 |
            | Reactome:R-HSA-9759102 |


   Scenario: Check Reactome pathway transformer using Reactome
        Given the transformer
        when we fire "/pathway/transform" query with the following body:
        """
            {
                "collection": [
                {
                    "biolink_class": "MacromolecularComplex",
                    "provided_by": "reactome",
                    "source": "reactome",
                    "id": "test-01",
                    "identifiers":{
                        "reactome":"reactome:R-ALL-1006146"
                    }
                }
                ],
                "controls":[]
            }
        """
        then the size of the response is 1 
        and the response contains the following entries in "source"
            | source                          |
            | Reactome pathway transformer   |
        and the response only contains the following entries in "source"
            | source                          |
            | Reactome pathway transformer   |
        and the response contains the following entries in "id"
            | id                    |
            | Reactome:R-HSA-977606  |
