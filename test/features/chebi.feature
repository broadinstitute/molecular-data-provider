Feature: Check ChEBI transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-chebi-transformer.ci.transltr.io/chebi"


    Scenario: Check compounds producer info
        Given the transformer
        when we fire "/compounds/transformer_info" query
        then the value of "name" should be "ChEBI compound-list producer"
        and the value of "label" should be "ChEBI"
        and the value of "version" should be "2.4.0"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "properties.source_version" should be "rel213 (2022-09-09)"
        and the size of "parameters" should be 1


    Scenario: Check relations transformer info
        Given the transformer
        when we fire "/relations/transformer_info" query
        then the value of "name" should be "ChEBI relations transformer"
        and the value of "label" should be "ChEBI"
        and the value of "version" should be "2.4.0"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "properties.source_version" should be "rel213 (2022-09-09)"
        and the size of "parameters" should be 1


    Scenario: Check ChEBI compound-list producer
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
                    "value": "CHEBI:26596"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "provided_by"
            | provided_by                  |
            | ChEBI compound-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                  |
            | ChEBI compound-list producer |
        and the response contains the following entries in "source"
            | source |
            | ChEBI  |
        and the response only contains the following entries in "source"
            | source |
            | ChEBI  |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | ChEBI  |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                 |
            | acetylsalicylic acid |
            | salicylates          |
        and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by                  |
            | ChEBI compound-list producer |
        and the response only contains the following entries in "provided_by" of "attributes" array
            | provided_by                  |
            | ChEBI compound-list producer |
        and the response contains the following entries in "value" of "attributes" array
            | value       |
            | aspirin     |
            | CHEBI:26596 |
        and the response contains the following entries in "biolink_class"
            | biolink_class  |
            | ChemicalEntity |
            | SmallMolecule  |
        and the response only contains the following entries in "biolink_class"
            | biolink_class  |
            | ChemicalEntity |
            | SmallMolecule  |


    Scenario: Check ChEBI relations transformer
        Given the transformer
        when we fire "/relations/transform" query with the following body:
        """
        {
           "controls": [],
           "collection": [
             {
              "biolink_class": "ChemicalSubstance",
              "id": "CID 4046",
              "provided_by": "chebi",
              "source": "chebi",
              "identifiers": {
                "chebi": "CHEBI:49164"
              }        
             }
           ]
        }
        """
        then the size of the response is 24
        and the response contains the following entries in "provided_by"
            | provided_by                  |
            | ChEBI relations transformer  |
        and the response only contains the following entries in "provided_by"
            | provided_by                  |
            | ChEBI relations transformer  |
        and the response contains the following entries in "biolink_class"
            | biolink_class  |
            | ChemicalEntity |
        and the response contains the following entries in "provided_by" of "names_synonyms" array
            | provided_by                  |
            | ChEBI relations transformer  |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                      |
            | terpenoids                |
            | isoprenoids               |
            | lipids                    |
            | molecular entity          |
            | (6S)-vomifoliol           |
            | (6R,9S)-vomifoliol        |
            | (4R)-4-hydroxy-4-[(1E,3S)-3-hydroxybut-1-en-1-yl]-3,5,5-trimethylcyclohex-2-en-1-one |
            | (4S)-4-hydroxy-4-[(1E)-3-hydroxybut-1-en-1-yl]-3,5,5-trimethylcyclohex-2-en-1-one    |
            | 4-hydroxy-4-[(1E)-3-hydroxybut-1-en-1-yl]-3,5,5-trimethylcyclohex-2-en-1-one         |
         and the response contains the following entries in "relation" of "connections" array
            | relation         |
            | is_a             |
            | has_part         |
            | is_enantiomer_of |
        and the response contains the following entries in "biolink_predicate" of "connections" array
            | biolink_predicate         |
            | subclass_of               |
            | has_part                  |
            | chemically_similar_to     |
        and the response contains the following entries in "inverse_predicate" of "connections" array
            | inverse_predicate         |
            | superclass_of             |
            | part_of                   |
            | chemically_similar_to     |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID 4046          |


    Scenario: Check ChEBI relations transformer (down)
        Given the transformer
        when we fire "/relations/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "direction",
                    "value": "down"
                }
            ],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "connections": [],
                    "id": "CHEBI:15365",
                    "identifiers": {
                        "chebi": "CHEBI:15365"
                    },
                    "provided_by": "ChEBI compound-list producer",
                    "source": "ChEBI"
                }
            ]
        }
        """
        then the size of the response is 4
        and the response contains the following entries in "provided_by"
            | provided_by                  |
            | ChEBI relations transformer  |
        and the response only contains the following entries in "provided_by"
            | provided_by                  |
            | ChEBI relations transformer  |
        and the response contains the following entries in "biolink_class"
            | biolink_class |
            | ChemicalEntity |
        and the response contains the following entries in "provided_by" of "names_synonyms" array
            | provided_by                  |
            | ChEBI relations transformer  |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                                 |
            | 2-acetyloxy-4-pentadecylbenzoic acid |
            | aspirin-based probe AP               |
            | Yosprala                             |
            | acetylsalicylate                     |
         and the response contains the following entries in "relation" of "connections" array
            | relation                  |
            | has_functional_parent     |
            | has_part                  |
            | is_conjugate_base_of      |
        and the response contains the following entries in "biolink_predicate" of "connections" array
            | biolink_predicate         |
            | chemically_similar_to     |
            | has_part                  |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CHEBI:15365       |
