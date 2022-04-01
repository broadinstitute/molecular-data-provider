Feature: Check Inxight:Drugs  transformer
    Background: Specify transformer API
        Given a transformer at "https://molepro-inxightdrugs-transformer.transltr.io/inxight_drugs"

    Scenario: Check Inxight:Drugs substance producer info
        Given the transformer
        when we fire "/substances/transformer_info" query
        then the value of "name" should be "Inxight:Drugs substance-list producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "substance"
        and the size of "parameters" should be 1

    Scenario: Check Inxight:Drugs relationships transformer info
        Given the transformer
        when we fire "/relationships/transformer_info" query
        then the value of "name" should be "Inxight:Drugs relationship transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "substance"
        and the value of "knowledge_map.output_class" should be "substance"
        and the size of "parameters" should be 0
        and the value of "version" should be "2.2.0"


    Scenario: Check Inxight:Drugs active_ingredients transformer info
        Given the transformer
        when we fire "/active_ingredients/transformer_info" query
        then the value of "name" should be "Inxight:Drugs active ingredients transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "drug"
        and the value of "knowledge_map.output_class" should be "substance"
        and the size of "parameters" should be 1
        and the value of "version" should be "2.2.0" 


    Scenario: Check Inxight:Drugs substance producer
        Given the transformer
        when we fire "/substances/transform" query with the following body:
        """
        {
        "controls": [
            {
                "name": "substances",
                "value": "aspirin"
            }
        ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "source"
            | source        |
            | Inxight:Drugs substance-list producer |
        and the response only contains the following entries in "source"
            | source                          |
            | Inxight:Drugs substance-list producer |
        and the response contains the following entries in "inchikey" of "identifiers"
            | inchikey                   |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
        and the response only contains the following entries in "pubchem" of "identifiers"
            | pubchem  |
            | CID:2244 |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source        |
            | Inxight:Drugs |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                 |
            | aspirin              |


    Scenario: Check Inxight:Drugs active_ingredients transformer using RxNorm
        Given the transformer
        when we fire "/active_ingredients/transform" query with the following body:
        """
        {
           "collection": [
              {
                "biolink_class": "Drug",
                "id": "RXCUI:1191",
                "identifiers":{
                   "rxnorm":"RXCUI:1191"
                 }
               }
            ],
           "controls":[]
        }
        """
        then the size of the response is 1 
        and the response contains the following entries in "source"
            | source                                       |
            | Inxight:Drugs active ingredients transformer |
        and the response only contains the following entries in "source"
            | source                          |
            | Inxight:Drugs active ingredients transformer |
        and the response contains the following entries in "id"
            | id              |
            | UNII:R16CO5Y76E |



    Scenario: Check  Inxight:Drugs relationships transformer
        Given the transformer
        when we fire "/relationships/transform" query with the following body:
        """
        {
           "collection": [
              {
                 "biolink_class": "ChemicalSubstance",
                 "id": "UNII:R16CO5Y76E",
                 "identifiers":{
                     "unii":"UNII:R16CO5Y76E"
                  }
              }
           ],
           "controls":[]
        }
        """
        then the size of the response is 26
        and the response contains the following entries in "biolink_class"
            | biolink_class |
            | ChemicalSubstance | 
        and the response contains the following entries in "source"
            | source |
            | Inxight:Drugs relationship transformer|
        and the response contains the following entries in "source" of "names_synonyms" array
            | source        |
            | Inxight:Drugs |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                      |
            | SALSALATE                 |
            | ASPIRIN CALCIUM           |
            | 4-HYDROXYBENZOIC ACID     |
            | ASPIRIN ANHYDRIDE         |
            | CARBASPIRIN CALCIUM       |
            | ASPIRIN LYSINE            | 
            | SALICYLIC ACID            | 
            | ASPIRIN MAGNESIUM         |
            | ASPIRIN ALUMINUM          |
            | ASPIRIN SODIUM            | 
            | 4-HYDROXYBENZOIC ACID     |
            | LITHIUM ACETYLSALICYLATE  |
            | CARBASPIRIN               | 
            | N-SALICYLOYLGLYCINE       |
            | ACETYLSALICYLSALICYLIC ACID |
            | ASPIRIN GLYCINE CALCIUM   |
            | 4-HYDROXYISOPHTHALIC ACID |
            | ASPIRIN                   |
            | ALUMINUM ACETYLSALICYLATE |

