Feature: Check ChEBI transformer

    Background: Specify transformer API
        Given a transformer at "http://localhost:8310/chebi"

    Scenario: Check compounds producer info
        Given the transformer
        when we fire "/compounds/transformer_info" query
        then the value of "name" should be "ChEBI compound-list producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "properties.source_version" should be "rel213 (2022-09-09)"

    Scenario: Check ChEBI compound-list producer
        Given the transformer
        when we fire "/compounds/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compounds",
                    "value": "Aspirin"
                }
            ]
        }
        """
        then the size of the response is 1
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
        and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by                  |
            | ChEBI compound-list producer |
        and the response only contains the following entries in "provided_by" of "attributes" array
            | provided_by                  |
            | ChEBI compound-list producer |
        and the response contains the following entries in "value" of "attributes" array
            | value   |
            | Aspirin |
        and the response contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
        and the response only contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |


    Scenario: Check relations transformer info
        Given the transformer
        when we fire "/relations/transformer_info" query
        then the value of "name" should be "ChEBI relations transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "properties.source_version" should be "rel213 (2022-09-09)"


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
        then the size of the response is 14
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
            | name                      |
            | (4S)-4-hydroxy-4-[(1E,3R)-3-hydroxybut-1-en-1-yl]-3,5,5-trimethylcyclohex-2-en-1-one |
            | (6S,9R)-vomifoliol        |
            | (4S)-4-hydroxy-4-[(1E)-3-hydroxybut-1-en-1-yl]-3,5,5-trimethylcyclohex-2-en-1-one    |
            | 4-hydroxy-4-[(1E)-3-hydroxybut-1-en-1-yl]-3,5,5-trimethylcyclohex-2-en-1-one         |
            | terpenoids                |
            | isoprenoids               |
            | lipids                    |
            | molecular entity          |
            | (4R)-4-hydroxy-4-[(1E,3S)-3-hydroxybut-1-en-1-yl]-3,5,5-trimethylcyclohex-2-en-1-one |
            | (6S,9R)-vomifoliol        |
        and the response contains the following entries in "relation" of "connections" array
	    | relation			|
	    | is_a			|
            | has_part                  |
	    | is_enantiomer_of          |
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
