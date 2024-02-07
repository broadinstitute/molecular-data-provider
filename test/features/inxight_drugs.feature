Feature: Check Inxight:Drugs  transformer
    Background: Specify transformer API
        Given a transformer at "https://molepro-inxightdrugs-transformer.transltr.io/inxight_drugs"


    Scenario: Check Inxight:Drugs substance producer info
        Given the transformer
        when we fire "/substances/transformer_info" query
        then the value of "name" should be "Inxight:Drugs substance-list producer"
        and the value of "label" should be "Inxight:Drugs"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "ChemicalEntity"
        and the size of "parameters" should be 1
        and the value of "version" should be "2.5.0"

    Scenario: Check Inxight:Drugs relationships transformer info
        Given the transformer
        when we fire "/relationships/transformer_info" query
        then the value of "name" should be "Inxight:Drugs relationship transformer"
        and the value of "label" should be "Inxight:Drugs"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "ChemicalEntity"
        and the value of "knowledge_map.output_class" should be "ChemicalEntity"
        and the size of "parameters" should be 0
        and the value of "version" should be "2.5.0"


    Scenario: Check Inxight:Drugs active_ingredients transformer info
        Given the transformer
        when we fire "/active_ingredients/transformer_info" query
        then the value of "name" should be "Inxight:Drugs active ingredients transformer"
        and the value of "label" should be "Inxight:Drugs"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "drug"
        and the value of "knowledge_map.output_class" should be "drug"
        and the size of "parameters" should be 1
        and the value of "version" should be "2.5.0" 


    Scenario: Check Inxight:Drugs substance producer
        Given the transformer
        when we fire "/substances/transform" query with the following body:
        """
          {
                "controls": [
                    {
                      "name": "substance",
                      "value": "bortezomib"
                    },
                    {
                      "name": "substance",
                      "value": "aspirin"
                    },
                    {
                      "name": "substance",
                      "value": "UNII:WK2XYI10QM"
                    },
                    {
                        "name": "substance",
                        "value": "UNII:08P1RJ5PDF"
                    },
                    {
                        "name": "substance",
                        "value": "UNII:01LSZ8XXL0"
                    },
                    {
                        "name": "substance",
                        "value": "UNII:T0N62K2M2Y"
                    }
               ]
           }
        """
        then the size of the response is 6
        and the response contains the following entries in "provided_by"
            | provided_by                           |
            | Inxight:Drugs substance-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                           |
            | Inxight:Drugs substance-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source        |
            | Inxight:Drugs |
        and the response may contain the following entries in "inchikey" of "identifiers"
            | inchikey      |
            | GXJABQQUPOEUTA-RDJZCZTQSA-N |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
        and the response may contain the following entries in "chebi" of "identifiers"
            | chebi         |
            | CHEBI:52717   |
            | CHEBI:15365   |
        and the response may contain the following entries in "pubchem" of "identifiers"
            | pubchem  |
            | CID:2244 |
            | CID:3672 |
        and the response contains the following entries in "unii" of "identifiers"
            | unii            |
            | UNII:69G8BD63PP |
            | UNII:R16CO5Y76E |
            | UNII:WK2XYI10QM |
            | UNII:08P1RJ5PDF |
            | UNII:01LSZ8XXL0 |
            | UNII:T0N62K2M2Y |
        and the response contains the following entries in "provided_by" of "names_synonyms" array
            | provided_by                           |
            | Inxight:Drugs substance-list producer |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                    |
            | BORTEZOMIB              |
            | ACETYLSALICYLIC ACID    |
            | IBUPROFEN               |
            | ARTEMISIA JUDAICA WHOLE |
            | TETRAHYDROISOHUMULONE   |
            | TRU-015                 |

    Scenario: Check Inxight:Drugs active_ingredients transformer using RxNorm
        Given the transformer
        when we fire "/active_ingredients/transform" query with the following body:
        """
        {
            "collection": [
               {
                 "biolink_class": "Drug",
                 "id": "RXCUI:1191",
                 "provided_by": "inxight_drugs",
                 "source": "inxight_drugs",        
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
            | source        |
            | Inxight:Drugs |
        and the response only contains the following entries in "source"
            | source                          |
            | Inxight:Drugs |
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
                 "provided_by": "inxight_drugs",
                 "source": "inxight_drugs",
                 "id": "UNII:R16CO5Y76E",
                 "identifiers":{
                     "unii":"UNII:R16CO5Y76E"
               }
             }
             ],
             "controls":[]
         }
"""
        then the size of the response is 17
        and the response contains the following entries in "biolink_class"
            | biolink_class |
            | SmallMolecule | 
        and the response contains the following entries in "source"
            | source        |
            | Inxight:Drugs |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source        |
            | Inxight:Drugs |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                       |
            | ASPIRIN CALCIUM            |
            | ASPIRIN COPPER             |
            | Salicylic acid             |
            | GENTISIC ACID              |
            | ALOXIPRIN                  |
            | CARBASPIRIN CALCIUM        |
            | ASPIRIN LYSINE             |
            | ASPIRIN MAGNESIUM          |
            | ASPIRIN ALUMINUM           |
            | ASPIRIN SODIUM             |
            | LITHIUM ACETYLSALICYLATE   |
            | CARBASPIRIN                |
            | N-SALICYLOYLGLYCINE        |
            | ASPIRIN GLYCINE CALCIUM    |
            | Aspirin Trelamine          |
            | ZINC ASPIRIN               |
            | ALUMINUM ACETYLSALICYLATE  |
        and the response only contains the following entries in "name" of "names_synonyms" array
            | name                       |
            | ASPIRIN CALCIUM            |
            | ASPIRIN COPPER             |
            | Salicylic acid             |
            | GENTISIC ACID              |
            | ALOXIPRIN                  |
            | CARBASPIRIN CALCIUM        |
            | ASPIRIN LYSINE             |
            | ASPIRIN MAGNESIUM          |
            | ASPIRIN ALUMINUM           |
            | ASPIRIN SODIUM             |
            | LITHIUM ACETYLSALICYLATE   |
            | CARBASPIRIN                |
            | N-SALICYLOYLGLYCINE        |
            | ASPIRIN GLYCINE CALCIUM    |
            | Aspirin Trelamine          |
            | ZINC ASPIRIN               |
            | ALUMINUM ACETYLSALICYLATE  |
