Feature: Check RxNorm transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-rxnorm-transformer.ci.transltr.io/rxnorm"

    Scenario: Check RxNorm molecules producer info
        Given the transformer
        when we fire "/molecules/transformer_info" query
        then the value of "name" should be "RxNorm compound-list producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "version" should be "2.1.0"
        and the size of "parameters" should be 01

    Scenario: Check RxNorm relations transformer info
        Given the transformer
        when we fire "/relations/transformer_info" query
        then the value of "name" should be "RxNorm drug relation info"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "drug"
        and the value of "knowledge_map.output_class" should be "drug"
        and the value of "version" should be "2.1.1"
        and the size of "parameters" should be 0

    Scenario: Check RxNorm drugs transformer info
        Given the transformer
        when we fire "/drugs/transformer_info" query
        then the value of "name" should be "RxNorm drug-list producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "drug"
        and the value of "version" should be "2.1.1"
        and the size of "parameters" should be 1

    Scenario: Check RxNorm compound-list producer
        Given the transformer
        when we fire "/molecules/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compounds",
                    "value": "aspirin"
                }
            ]
        }
        """

        then the size of the response is 1
        and the response contains the following entries in "id"
            | id               |
            | UNII:R16CO5Y76E  |
        and the response only contains the following entries in "id"
            | id               |
            | UNII:R16CO5Y76E |
        and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by                     |
            | RxNorm compound-list producer   |
        and the response only contains the following entries in "provided_by" of "attributes" array
            | provided_by                     |
            | RxNorm compound-list producer   |
        and the response contains the following entries in "pubchem" of "identifiers"
            | pubchem  |
            | CID:2244 |
        and the response only contains the following entries in "pubchem" of "identifiers"
            | pubchem  |
            | CID:2244 |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source   |
            | UNII     |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name    |
            | ASPIRIN |
        and the response contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
        and the response only contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |


    Scenario: Check RxNorm relations transformer
        Given the transformer
        when we fire "/relations/transform" query with the following body:
        """
        {
          "controls": [],
          "collection": [
            {
              "id": "RXCUI:2059287",
              "identifiers": {
                "rxnorm": "RXCUI:2059287"
               }
            }
           ]
        }
        """
       then the size of the response is 4
       and the response contains the following entries in "id"
            | id               |
            | RXCUI:1649574    |
            | RXCUI:2059269    |
            | RXCUI:2059286    |
            | RXCUI:2059288    |
       and the response only contains the following entries in "id"
            | id               |
            | RXCUI:1649574    |
            | RXCUI:2059269    |
            | RXCUI:2059286    |
            | RXCUI:2059288    |
            
            
 Scenario: Check RxNorm drugs transformer
        Given the transformer
        when we fire "/drugs/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "drugs",
                    "value": "aspirin"
                }
            ]
        }
        """
       then the size of the response is 1
       and the response contains the following entries in "id"
            | id               |
            | RXCUI:1191       |
       and the response only contains the following entries in "id"
            | id               |
            | RXCUI:1191       |
       and the response contains the following entries in "source"
            | source   |
            | RxNorm drug-list producer |
       and the response only contains the following entries in "source"
            | source   |
            | RxNorm drug-list producer |

       and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by      |
            | RxNorm drug-list producer |
       and the response contains the following entries in "source" of "names_synonyms" array
            | source      |
            | substance@RxNorm |

