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
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "20AA_220307F (2022-03-07)"
        and the size of "parameters" should be 01

    Scenario: Check RxNorm molecules producer info
        Given the transformer
        when we fire "/unii/transformer_info" query
        then the value of "name" should be "UNII ingredient-list producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "ChemicalEntity"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "20AA_220307F (2022-03-07)"
        and the size of "parameters" should be 01

    Scenario: Check RxNorm relations transformer info
        Given the transformer
        when we fire "/relations/transformer_info" query
        then the value of "name" should be "RxNorm drug relation info"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "drug"
        and the value of "knowledge_map.output_class" should be "drug"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "20AA_220307F (2022-03-07)"
        and the size of "parameters" should be 0

    Scenario: Check RxNorm drugs transformer info
        Given the transformer
        when we fire "/drugs/transformer_info" query
        then the value of "name" should be "RxNorm drug-list producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "drug"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "20AA_220307F (2022-03-07)"
        and the size of "parameters" should be 1


    Scenario: Check RxNorm ingredients transformer info
        Given the transformer
        when we fire "/ingredients/transformer_info" query
        then the value of "name" should be "RxNorm active ingredient transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "drug"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "20AA_220307F (2022-03-07)"
        and the size of "parameters" should be 0


    Scenario: Check RxNorm components transformer info
        Given the transformer
        when we fire "/components/transformer_info" query
        then the value of "name" should be "RxNorm components transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "drug"
        and the value of "knowledge_map.output_class" should be "drug"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "20AA_220307F (2022-03-07)"
        and the size of "parameters" should be 0


    Scenario: Check RxNorm compound-list producer
        Given the transformer
        when we fire "/molecules/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compound",
                    "value": "aspirin"
                },
                {
                    "name": "compound",
                    "value": "UNII:0258808825"
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


    Scenario: Check RxNorm compound-list producer
        Given the transformer
        when we fire "/unii/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "ingredient",
                    "value": "aspirin"
                },
                {
                    "name": "ingredient",
                    "value": "UNII:0258808825"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "id"
            | id               |
            | UNII:R16CO5Y76E  |
            | UNII:0258808825  |
        and the response only contains the following entries in "id"
            | id               |
            | UNII:R16CO5Y76E |
            | UNII:0258808825  |
        and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by                   |
            | UNII ingredient-list producer |
        and the response only contains the following entries in "provided_by" of "attributes" array
            | provided_by                   |
            | UNII ingredient-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source   |
            | UNII     |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                     |
            | ASPIRIN                  |
            | MACROPIPER EXCELSUM LEAF |
        and the response only contains the following entries in "name" of "names_synonyms" array
            | name                     |
            | ASPIRIN                  |
            | MACROPIPER EXCELSUM LEAF |


    Scenario: Check RxNorm relations transformer
        Given the transformer
        when we fire "/relations/transform" query with the following body:
        """
        {
          "controls": [],
          "collection": [
            {
              "id": "RXCUI:2059287",
              "biolink_class": "Drug",
              "source": "RxNorm",
              "provided_by": "RxNorm",
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
                    "name": "drug",
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
            | source |
            | RxNorm |
       and the response only contains the following entries in "source"
            | source |
            | RxNorm |
       and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by      |
            | RxNorm drug-list producer |
       and the response contains the following entries in "source" of "names_synonyms" array
            | source      |
            | RxNorm |


    Scenario: Check RxNorm ingredients transformer
        Given the transformer
        when we fire "/ingredients/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "UNII:69G8BD63PP",
                    "biolink_class": "SmallMolecule",
                    "identifiers": {
                        "unii": "UNII:69G8BD63PP"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                },
                {
                    "id": "UNII:002RK9L1FN",
                    "biolink_class": "ChemicalEntity",
                    "identifiers": {
                        "unii": "UNII:002RK9L1FN"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                },
                {
                    "id": "UNII:EM8BM710ZC",
                    "biolink_class": "ChemicalEntity",
                    "identifiers": {
                        "unii": "UNII:EM8BM710ZC"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                }
            ]
        }
        """
       then the size of the response is 7
       and the response contains the following entries in "id"
            | id            |
            | RXCUI:358258  |
            | RXCUI:2043326 |
            | RXCUI:9518    |
            | RXCUI:689519  |
            | RXCUI:689554  |
            | RXCUI:689799  |
            | RXCUI:1008262 |
       and the response only contains the following entries in "id"
            | id            |
            | RXCUI:358258  |
            | RXCUI:2043326 |
            | RXCUI:9518    |
            | RXCUI:689519  |
            | RXCUI:689554  |
            | RXCUI:689799  |
            | RXCUI:1008262 |
        and the response contains the following entries in "provided_by" of "connections" array
            | provided_by                          |
            | RxNorm active ingredient transformer |
        and the response only contains the following entries in "provided_by" of "connections" array
            | provided_by                          |
            | RxNorm active ingredient transformer |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | UNII:69G8BD63PP   |
            | UNII:002RK9L1FN   |
            | UNII:EM8BM710ZC   |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | UNII:69G8BD63PP   |
            | UNII:002RK9L1FN   |
            | UNII:EM8BM710ZC   |


    Scenario: Check RxNorm components transformer
        Given the transformer
        when we fire "/components/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "RXCUI:214153",
                    "biolink_class": "Drug",
                    "source": "RxNorm",
                    "provided_by": "RxNorm",
                    "identifiers": {
                        "rxnorm": "RXCUI:214153"
                    }
                },
                {
                    "id": "RXCUI:1191",
                    "biolink_class": "Drug",
                    "source": "RxNorm",
                    "provided_by": "RxNorm",
                    "identifiers": {
                        "rxnorm": "RXCUI:1191"
                    }
                },
                {
                    "id": "RXCUI:214181",
                    "biolink_class": "Drug",
                    "source": "RxNorm",
                    "provided_by": "RxNorm",
                    "identifiers": {
                        "rxnorm": "RXCUI:214181"
                    }
                }
            ]
        }
        """
       then the size of the response is 4
       and the response contains the following entries in "id"
            | id          |
            | RXCUI:161   |
            | RXCUI:22892 |
            | RXCUI:27946 |
            | RXCUI:3498  |
       and the response only contains the following entries in "id"
            | id          |
            | RXCUI:161   |
            | RXCUI:22892 |
            | RXCUI:27946 |
            | RXCUI:3498  |
        and the response contains the following entries in "provided_by" of "connections" array
            | provided_by                          |
            | RxNorm components transformer |
        and the response only contains the following entries in "provided_by" of "connections" array
            | provided_by                          |
            | RxNorm components transformer |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | RXCUI:214181      |
            | RXCUI:214153      |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | RXCUI:214181      |
            | RXCUI:214153      |

