Feature: Check RefMet transformer

    Background: Specify transformer API
        Given a transformer at "https://translator.broadinstitute.org/refmet"


    Scenario: Check RefMet producer info
        Given the transformer
        when we fire "/metabolites/transformer_info" query
        then the value of "name" should be "RefMet metabolite-list producer"
        and the value of "label" should be "RefMet"
        and the value of "infores" should be "infores:refmet"
        and the value of "version" should be "2.6.0"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "properties.source_version" should be "2025-02-11"
        and the value of "properties.source_date" should be "2025-02-11"
        and the size of "parameters" should be 1


    Scenario: Check RefMet target transformer info
        Given the transformer
        when we fire "/metabolite_classes/transformer_info" query
        then the value of "name" should be "RefMet metabolite super-class transformer"
        and the value of "label" should be "RefMet"
        and the value of "infores" should be "infores:refmet"
        and the value of "version" should be "2.6.0"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "ChemicalEntity"
        and the value of "properties.source_version" should be "2025-02-11"
        and the value of "properties.source_date" should be "2025-02-11"
        and the size of "parameters" should be 0


    Scenario: Check RefMet metabolite-list producer
        Given the transformer
        when we fire "/metabolites/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "metabolite",
                    "value": "glucose"
                }
            ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "id"
            | id         |
            | CHEBI:4167 |
        and the response only contains the following entries in "id"
            | id         |
            | CHEBI:4167 |
        and the response contains the following entries in "source"
            | source |
            | RefMet |
        and the response only contains the following entries in "source"
            | source |
            | RefMet |
        and the response contains the following entries in "pubchem" of "identifiers"
            | pubchem  |
            | CID:5793 |
        and the response only contains the following entries in "pubchem" of "identifiers"
            | pubchem  |
            | CID:5793 |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | RefMet |


    Scenario: RefMet metabolite super-class transformer
        Given the transformer
        when we fire "/metabolite_classes/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
               {
                  "biolink_class": "SmallMolecule",
                  "provided_by": "RefMet",
                  "source": "RefMet",
                  "id": "Glucose",
                  "identifiers": {
                      "inchi_key": "WQZGKKKJIJFFOK-GASJEMHNSA-N"
                   }
               }
            ]
         }
        """
        then the size of the response is 3
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | Glucose           |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | Glucose           |
        and the response contains the following entries in "id"
            | id          |
            | CHEBI:18133 |
            | CHEBI:35381 |
            | CHEBI:18133 |
        and the response only contains the following entries in "id"
            | id          |
            | CHEBI:18133 |
            | CHEBI:35381 |
            | CHEBI:16646 |
        and the response contains the following entries in "chebi" of "identifiers"
            | chebi       |
            | CHEBI:18133 |
            | CHEBI:35381 |
            | CHEBI:18133 |
        and the response only contains the following entries in "chebi" of "identifiers"
            | chebi       |
            | CHEBI:18133 |
            | CHEBI:35381 |
            | CHEBI:16646 |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name            |
            | Hexoses         |
            | Monosaccharides |
            | Carbohydrates   |
        and the response only contains the following entries in "name" of "names_synonyms" array
            | name            |
            | Hexoses         |
            | Monosaccharides |
            | Carbohydrates   |


    Scenario: RefMet metabolite super-class transformer with RefMet id
        Given the transformer
        when we fire "/metabolite_classes/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
               {
                  "biolink_class": "SmallMolecule",
                  "provided_by": "RefMet",
                  "source": "RefMet",
                  "id": "RM0003901",
                  "identifiers": {
                      "refmet": "refmet:RM0003901"
                   }
               },
               {
                  "biolink_class": "SmallMolecule",
                  "provided_by": "RefMet",
                  "source": "RefMet",
                  "id": "RM0003902",
                  "identifiers": {
                      "refmet": "refmet:RM0003902"
                   }
               }
            ]
         }
        """
        then the size of the response is 1
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | RM0003901         |
            | RM0003902         |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | RM0003901         |
            | RM0003902         |
        and the response contains the following entries in "id"
            | id          |
            | CHEBI:22315 |
        and the response only contains the following entries in "id"
            | id          |
            | CHEBI:22315 |
        and the response contains the following entries in "chebi" of "identifiers"
            | chebi       |
            | CHEBI:22315 |
        and the response only contains the following entries in "chebi" of "identifiers"
            | chebi       |
            | CHEBI:22315 |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name      |
            | Alkaloids |
        and the response only contains the following entries in "name" of "names_synonyms" array
            | name      |
            | Alkaloids |

