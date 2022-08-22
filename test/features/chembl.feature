Feature: Check ChEMBL transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-chembl-transformer.transltr.io/chembl"


    Scenario: Check ChEMBL producer info
        Given the transformer
        when we fire "/molecules/transformer_info" query
        then the value of "name" should be "ChEMBL compound-list producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "30 (2022-03-09)"
        and the size of "parameters" should be 1


    Scenario: Check ChEMBL target transformer info
        Given the transformer
        when we fire "/targets/transformer_info" query
        then the value of "name" should be "ChEMBL gene target transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "30 (2022-03-09)"
        and the size of "parameters" should be 0


    Scenario: Check ChEMBL metabolites transformer info
        Given the transformer
        when we fire "/metabolites/transformer_info" query
        then the value of "name" should be "ChEMBL metabolite transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "30 (2022-03-09)"
        and the value of "knowledge_map.edges[0]['subject']" should be "SmallMolecule"
        and the size of "knowledge_map.nodes" should be 1
        and the size of "parameters" should be 0


    Scenario: Check ChEMBL indication transformer info
        Given the transformer
        when we fire "/indications/transformer_info" query
        then the value of "name" should be "ChEMBL indication transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "disease"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "30 (2022-03-09)"
        and the size of "parameters" should be 0

    Scenario: Check ChEMBL mechanism transformer info
        Given the transformer
        when we fire "/mechanisms/transformer_info" query
        then the value of "name" should be "ChEMBL mechanism transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "target"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "30 (2022-03-09)"
        and the size of "parameters" should be 0

    Scenario: Check ChEMBL compound-list producer
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
                    "value": "ChEMBL:CHEMBL4525786"
                }
            ]
        }
        """
        then the size of the response is 2 
        and the response contains the following entries in "id"
            | id                   |
            | ChEMBL:CHEMBL25      |
            | ChEMBL:CHEMBL4525786 |
        and the response only contains the following entries in "id"
            | id                   |
            | ChEMBL:CHEMBL25      |
            | ChEMBL:CHEMBL4525786 |
        and the response contains the following entries in "provided_by"
            | provided_by                          |
            | ChEMBL compound-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                          |
            | ChEMBL compound-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | ChEMBL |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                 |
            | Acetylsalicylic Acid |
        and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by                   |
            | ChEMBL compound-list producer |
        and the response only contains the following entries in "provided_by" of "attributes" array
            | provided_by                   |
            | ChEMBL compound-list producer |
        and the response contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | ChEMBL |
        and the response only contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | ChEMBL |
        and the response contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
            | IZFCJBVYODRRRU-LLVKDONJSA-N |
        and the response only contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
            | IZFCJBVYODRRRU-LLVKDONJSA-N |


    Scenario: Check ChEMBL targets transformer on ID input
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "CID:2244",
                    "identifiers": {
                        "chembl": "ChEMBL:CHEMBL25"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "id"
            | id                      |
            | ENSEMBL:ENSG00000073756 |
            | ENSEMBL:ENSG00000095303 |
        and the response only contains the following entries in "id"
            | id                      |
            | ENSEMBL:ENSG00000073756 |
            | ENSEMBL:ENSG00000095303 |
        and the response contains the following entries in "biolink_class"
            | biolink_class |
            | Gene          |
        and the response only contains the following entries in "biolink_class"
            | biolink_class |
            | Gene          |
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | ChEMBL gene target transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | ChEMBL gene target transformer |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                         |
            | Prostaglandin G/H synthase 1 |
            | Prostaglandin G/H synthase 2 |

    Scenario: Check ChEMBL targets transformer on structure input
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "CID:2244",
                    "identifiers": {
                        "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                }
            ]
        }
        """
        then the size of the response is 2







    Scenario: Check ChEMBL mechanism transformer on ID input
        Given the transformer
        when we fire "/mechanisms/transform" query with the following body:
        """
        {
           "controls": [],
           "collection": [
             {
              "biolink_class": "ChemicalSubstance",
              "id": "CID:2244",
              "provided_by": "chembl",
              "source": "chembl",
              "identifiers": {
                "chembl": "ChEMBL:CHEMBL25"
              }
             }
           ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "id"
            | id                          |
            | CHEMBL.TARGET:CHEMBL2094253 |
        and the response only contains the following entries in "id"
            | id                          |
            | CHEMBL.TARGET:CHEMBL2094253 | 
        and the response contains the following entries in "biolink_class"
            | biolink_class |
            | ProteinFamily |
        and the response only contains the following entries in "biolink_class"
            | biolink_class |
            | ProteinFamily |
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | ChEMBL mechanism transformer    |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | ChEMBL mechanism transformer    |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name           |
            | Cyclooxygenase |


    Scenario: Check ChEMBL mechanism transformer on structure input
        Given the transformer
        when we fire "/mechanisms/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "CID:2244",
                    "identifiers": {
                        "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                }
            ]
        }
        """
        then the size of the response is 1








    Scenario: Check ChEMBL activities transformer on ID input
        Given the transformer
        when we fire "/activities/transform" query with the following body:
        """
        {
           "controls": [],
           "collection": [
             {
              "biolink_class": "ChemicalSubstance",
              "id": "CID:86471",
              "provided_by": "chembl",
              "source": "chembl",
              "identifiers": {
                "chembl": "ChEMBL:CHEMBL1345"
              }
             }
           ]
        }
        """
        then the size of the response is 3
        and the response contains the following entries in "id"
            | id                          |
            | CHEMBL.TARGET:CHEMBL1075138 |
            | CHEMBL.TARGET:CHEMBL4303835 |
            | CHEMBL.TARGET:CHEMBL4523582 |
        and the response only contains the following entries in "id"
            | id                          |
            | CHEMBL.TARGET:CHEMBL1075138 |
            | CHEMBL.TARGET:CHEMBL4303835 |
            | CHEMBL.TARGET:CHEMBL4523582 |
        and the response contains the following entries in "biolink_class"
            | biolink_class     |
            | Organism          |
            | Protein           |
        and the response only contains the following entries in "biolink_class"
            | biolink_class |
            | Organism          |
            | Protein           |
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | ChEMBL activities transformer   |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | ChEMBL activities transformer    |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:86471         |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:86471         |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                            |
            | SARS-CoV-2                      |
            | Replicase polyprotein 1ab       |
            | Tyrosyl-DNA phosphodiesterase 1 |
        and the response only contains the following entries in "name" of "names_synonyms" array
            | name                            |
            | SARS-CoV-2                      |
            | Replicase polyprotein 1ab       |
            | Tyrosyl-DNA phosphodiesterase 1 |


    Scenario: Check ChEMBL activities transformer on structure input
        Given the transformer
        when we fire "/activities/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "CID:86471",
                    "identifiers": {
                        "inchikey": "YUFWAVFNITUSHI-UHFFFAOYSA-N"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                }
            ]
        }
        """
        then the size of the response is 3
        and the response contains the following entries in "id"
            | id                          |
            | CHEMBL.TARGET:CHEMBL1075138 |
            | CHEMBL.TARGET:CHEMBL4303835 |
            | CHEMBL.TARGET:CHEMBL4523582 |
        and the response only contains the following entries in "id"
            | id                          |
            | CHEMBL.TARGET:CHEMBL1075138 |
            | CHEMBL.TARGET:CHEMBL4303835 |
            | CHEMBL.TARGET:CHEMBL4523582 |
        and the response contains the following entries in "biolink_class"
            | biolink_class     |
            | Organism          |
            | Protein           |
        and the response only contains the following entries in "biolink_class"
            | biolink_class |
            | Organism          |
            | Protein           |
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | ChEMBL activities transformer   |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | ChEMBL activities transformer    |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:86471         |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:86471         |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                            |
            | SARS-CoV-2                      |
            | Replicase polyprotein 1ab       |
            | Tyrosyl-DNA phosphodiesterase 1 |
        and the response only contains the following entries in "name" of "names_synonyms" array
            | name                            |
            | SARS-CoV-2                      |
            | Replicase polyprotein 1ab       |
            | Tyrosyl-DNA phosphodiesterase 1 |


    Scenario: Check ChEMBL indications transformer
        Given the transformer
        when we fire "/indications/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "CID:2244",
                    "identifiers": {
                        "chembl": "ChEMBL:CHEMBL25",
                        "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                }
            ]
        }
        """
        then the size of the response is 142
        and the response contains the following entries in "biolink_class"
            | biolink_class              |
            | DiseaseOrPhenotypicFeature |
        and the response only contains the following entries in "biolink_class"
            | biolink_class              |
            | DiseaseOrPhenotypicFeature |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response contains the following entries in "biolink_predicate" of "connections" array
            | biolink_predicate |
            | treats            |
        and the response only contains the following entries in "biolink_predicate" of "connections" array
            | biolink_predicate |
            | treats            |
        and the response contains the following entries in "provided_by"
            | provided_by                   |
            | ChEMBL indication transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                   |
            | ChEMBL indication transformer |
        and the response contains the following entries in "source"
            | source |
            | ChEMBL |
        and the response only contains the following entries in "source"
            | source |
            | ChEMBL |


    Scenario: Check ChEMBL metabolites transformer
        Given the transformer
        when we fire "/metabolites/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "CID:2244",
                    "identifiers": {
                        "chembl": "ChEMBL:CHEMBL25",
                        "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                }
            ]
        }
        """
        then the size of the response is 8
        and the response contains the following entries in "biolink_class"
            | biolink_class |
            | SmallMolecule |
        and the response only contains the following entries in "biolink_class"
            | biolink_class |
            | SmallMolecule |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response contains the following entries in "biolink_predicate" of "connections" array
            | biolink_predicate |
            | has_metabolite    |
        and the response only contains the following entries in "biolink_predicate" of "connections" array
            | biolink_predicate |
            | has_metabolite    |
        and the response contains the following entries in "provided_by"
            | provided_by                   |
            | ChEMBL metabolite transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                   |
            | ChEMBL metabolite transformer |
        and the response contains the following entries in "source"
            | source |
            | ChEMBL |
        and the response only contains the following entries in "source"
            | source |
            | ChEMBL |
