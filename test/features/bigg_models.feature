Feature: Check BiGG transformer


    Background: Specify transformer API
        Given a transformer at "https://translator.broadinstitute.org/bigg"


    Scenario: Check BiGG producer info
        Given the transformer
        when we fire "/metabolites/transformer_info" query
        then the value of "name" should be "BiGG compound-list producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "version" should be "2.3.0"
        and the value of "properties.source_version" should be "version 1.6.0 of BiGG, downloaded July 23, 2021"
        and the size of "parameters" should be 1


    Scenario: Check BiGG Compound Reactions transformer info
        Given the transformer
        when we fire "/reactions/transformer_info" query
        then the value of "name" should be "BiGG reactions transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "reaction"
        and the value of "version" should be "2.3.0"
        and the value of "properties.source_version" should be "version 1.6.0 of BiGG, downloaded July 23, 2021"
        and the size of "parameters" should be 0


    Scenario: Check  BiGG Compound Gene transformer info
        Given the transformer
        when we fire "/genes/transformer_info" query
        then the value of "name" should be "BiGG genes transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the value of "version" should be "2.3.0"
        and the value of "properties.source_version" should be "version 1.6.0 of BiGG, downloaded July 23, 2021"
        and the size of "parameters" should be 0


    Scenario: Check  BiGG Gene Reaction transformer info
        Given the transformer
        when we fire "/gene-reactions/transformer_info" query
        then the value of "name" should be "BiGG gene_reaction transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "gene"
        and the value of "knowledge_map.output_class" should be "reaction"
        and the value of "version" should be "2.3.0"
        and the value of "properties.source_version" should be "version 1.6.0 of BiGG, downloaded July 23, 2021"
        and the size of "parameters" should be 0


    Scenario: Check BiGG compound-list producer
        Given the transformer
        when we fire "/metabolites/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compounds",
                    "value": "adenosine"
                }
            ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "id"
            | id               |
            | BIGG.METABOLITE:adn |
        and the response only contains the following entries in "id"
            | id               |
            | BIGG.METABOLITE:adn |
        and the response contains the following entries in "source"
            | source                          |
            | BiGG |
        and the response only contains the following entries in "source"
            | source                          |
            | BiGG |
        and the response contains the following entries in "bigg" of "identifiers"
            | bigg         |
            | BIGG.METABOLITE:adn |
        and the response only contains the following entries in "bigg" of "identifiers"
            | bigg         |
            | BIGG.METABOLITE:adn |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source   |
            | BiGG     |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name      |
            | Adenosine |
        and the response contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | OIRDTQYFTABQOQ-KQYNXXCUSA-N |
        and the response only contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | OIRDTQYFTABQOQ-KQYNXXCUSA-N |



    Scenario: Check BiGG compound genes transformer using ChEMBL id
        Given the transformer
        when we fire "/genes/transform" query with the following body:
        """
        {
            "collection": [
                  {
                     "biolink_class": "ChemicalSubstance",
                      "id" : "CHEBI:13715",
                      "provided_by": "bigg",
                      "source": "bigg",
                      "identifiers":{
                         "chebi": "CHEBI:13715"
                        }
                  }
            ],
            "controls":[]
        }
        """
        then the size of the response is 9
        and the response contains the following entries in "id"
            | id                     |
            | BIGG.GENE:1103_AT1     |
            | BIGG.GENE:1103_AT2     |
            | BIGG.GENE:1103_AT3     |
            | BIGG.GENE:1103_AT4     |
            | BIGG.GENE:43_AT1       |
            | BIGG.GENE:43_AT2       |
            | BIGG.GENE:6572_AT1     |
            | BIGG.GENE:1103_AT1     |
            | BIGG.GENE:1103_AT2     |
            | BIGG.GENE:1103_AT3     |
            | BIGG.GENE:1103_AT4     |



    Scenario: Check BiGG compound reactions transformer using ChEMBL id
        Given the transformer
        when we fire "/reactions/transform" query with the following body:
        """
        {
            "collection": [
                  {
                     "biolink_class": "ChemicalSubstance",
                      "id" : "CHEBI:13715",
                      "provided_by": "bigg",
                      "source": "bigg",
                      "identifiers":{
                         "chebi": "CHEBI:13715"
                        }
                  }
            ],
            "controls":[]
        }
        """
        then the size of the response is 6
        and the response contains the following entries in "source"
            | source      |
            | BiGG Model  |
        and the response only contains the following entries in "source"
            | source      |
            | BiGG Model  |
        and the response contains the following entries in "id"
            | id                     |
            | BIGG.REACTION:ACHEe    |
            |BIGG.REACTION:ACHVESSEC |
            |BIGG.REACTION:ACHVESSEC_1 |
            |BIGG.REACTION:ACHtn     |
            |BIGG.REACTION:CHAT      |
            |BIGG.REACTION:CHATn     |
        and the response only contains the following entries in "id"
            | id               |
            | BIGG.REACTION:ACHEe    |
            | BIGG.REACTION:ACHVESSEC |
            |BIGG.REACTION:ACHVESSEC_1 |
            |BIGG.REACTION:ACHtn     |
            |BIGG.REACTION:CHAT      |
            |BIGG.REACTION:CHATn     |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source      |
            | BiGG Model  |


    Scenario: Check BiGG gene  reactions transformer using ChEMBL id
        Given the transformer
        when we fire "/gene-reactions/transform" query with the following body:
        """
        {
           "collection": [
               {
                 "biolink_class": "ChemicalSubstance",
                 "id": "MOLEPRO:10",
                 "provided_by": "bigg",
                 "source": "bigg",
                 "identifiers":{
                 "bigg": "BIGG.METABOLITE:glc__D",
                 "inchikey": "WQZGKKKJIJFFOK-GASJEMHNSA-N",
                 "ccds":["CCDS:CCDS12425.1"
                         ],
                 "entrez": "NCBIGene:11136",
                 "omim": "OMIM:604144"
                  }
               }
            ],
            "controls":[]
        } 
        """
        then the size of the response is 2 






 
