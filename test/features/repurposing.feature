Feature: Check Drug Repurposing Hub transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-rephub-transformer.test.transltr.io/repurposing"


    Scenario: Check compounds transformer info
        Given the transformer
        when we fire "/compounds/transformer_info" query
        then the value of "name" should be "Drug Repurposing Hub compound-list producer"
        and the value of "label" should be "Repurposing"
        and the value of "infores" should be "infores:drug-repurposing-hub"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "2020-03-24"
        and the size of "knowledge_map.nodes" should be 1
        and the size of "knowledge_map.edges" should be 0
        and the size of "parameters" should be 1


    Scenario: Check targets transformer info
        Given the transformer
        when we fire "/targets/transformer_info" query
        then the value of "name" should be "Drug Repurposing Hub target transformer"
        and the value of "label" should be "Repurposing"
        and the value of "infores" should be "infores:drug-repurposing-hub"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "2020-03-24"
        and the size of "knowledge_map.nodes" should be 2
        and the size of "knowledge_map.edges" should be 1
        and the size of "parameters" should be 0


    Scenario: Check indication transformer info
        Given the transformer
        when we fire "/indications/transformer_info" query
        then the value of "name" should be "Drug Repurposing Hub indication transformer"
        and the value of "label" should be "Repurposing"
        and the value of "infores" should be "infores:drug-repurposing-hub"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "DiseaseOrPhenotypicFeature"
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "2020-03-24"
        and the size of "knowledge_map.nodes" should be 2
        and the size of "knowledge_map.edges" should be 3
        and the size of "parameters" should be 0


    Scenario: Check Drug Repurposing Hub compound-list producer
        Given the transformer
        when we fire "/compounds/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compound",
                    "value": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                },
                {
                    "name": "compound",
                    "value": "CID:387447"
                },
                {
                    "name": "compound",
                    "value": "Avitinib"
                }
            ]
        }
        """
        then the size of the response is 3
        and the response contains the following entries in "provided_by"
            | provided_by                                 |
            | Drug Repurposing Hub compound-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                                 |
            | Drug Repurposing Hub compound-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | Repurposing |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name       |
            | aspirin    |
            | bortezomib |
            | avitinib   |
        and the response contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | Repurposing      |
        and the response only contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | Repurposing      |
        and the response contains the following entries in "value" of "attributes" array
            | value                    |
            | cyclooxygenase inhibitor |
            | proteasome inhibitor     |
        and the response contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
            | GXJABQQUPOEUTA-RDJZCZTQSA-N |
            | UOFYSRZSLXWIQB-UHFFFAOYSA-N |
        and the response only contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
            | GXJABQQUPOEUTA-RDJZCZTQSA-N |
            | UOFYSRZSLXWIQB-UHFFFAOYSA-N |


    Scenario: Check Drug Repurposing Hub targets transformer
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "ChEMBL:CHEMBL25",
                    "biolink_class": "ChemicalSubstance",
                    "identifiers": {
                        "pubchem": "CID:2244",
                        "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                    },
                    "provided_by": "Drug Repurposing Hub compound-list producer",
                    "source": "Repurposing"
                }
            ]
        }
        """
        then the size of the response is 19
        and the response contains the following entries in "provided_by" of "connections" array
            | provided_by                             |
            | Drug Repurposing Hub target transformer |
        and the response only contains the following entries in "provided_by" of "connections" array
            | provided_by                             |
            | Drug Repurposing Hub target transformer |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | ChEMBL:CHEMBL25   |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | ChEMBL:CHEMBL25   |


    Scenario: Check Drug Repurposing Hub indications transformer
        Given the transformer
        when we fire "/indications/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "ChEMBL:CHEMBL25",
                    "biolink_class": "ChemicalSubstance",
                    "identifiers": {
                        "pubchem": "CID:2244",
                        "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                    },
                    "provided_by": "Drug Repurposing Hub compound-list producer",
                    "source": "Repurposing"
                },
                {
                    "id": "CID:896",
                    "biolink_class": "ChemicalSubstance",
                    "identifiers": {
                        "pubchem": "CID:896",
                        "inchikey": "DRLFMBDRBRZALE-UHFFFAOYSA-N"
                    },
                    "provided_by": "Drug Repurposing Hub compound-list producer",
                    "source": "Repurposing"
                }
            ]
        }
        """
        then the size of the response is 5
        and the response contains the following entries in "provided_by" of "connections" array
            | provided_by                                 |
            | Drug Repurposing Hub indication transformer |
        and the response only contains the following entries in "provided_by" of "connections" array
            | provided_by                                 |
            | Drug Repurposing Hub indication transformer |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | ChEMBL:CHEMBL25   |
            | CID:896           |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | ChEMBL:CHEMBL25   |
            | CID:896           |
        and the response contains the following entries in "biolink_predicate" of "connections" array
            | biolink_predicate |
            | biolink:treats    |
            | biolink:ameliorates_condition |
        and the response only contains the following entries in "biolink_predicate" of "connections" array
            | biolink_predicate |
            | biolink:treats    |
            | biolink:ameliorates_condition |
