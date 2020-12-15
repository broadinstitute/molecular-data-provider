Feature: Check STITCH transformer

    Background: Specify transformer API
        Given a transformer at "https://translator.broadinstitute.org/stitch"


    Scenario: Check chemicals transformer info
        Given the transformer
        when we fire "/chemicals/transformer_info" query
        then the value of "name" should be "STITCH compound-list producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"


    Scenario: Check links transformer info
        Given the transformer
        when we fire "/links/transformer_info" query
        then the value of "name" should be "STITCH link transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "protein"


    Scenario: Check STITCH compound-list producer
        Given the transformer
        when we fire "/chemicals/transform" query with the following body:
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
        and the response contains the following entries in "source"
            | source                          |
            | STITCH compound-list producer |
        and the response only contains the following entries in "source"
            | source                          |
            | STITCH compound-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | STITCH |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name    |
            | aspirin |
        and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by                   |
            | STITCH compound-list producer |
        and the response only contains the following entries in "provided_by" of "attributes" array
            | provided_by                   |
            | STITCH compound-list producer |
        and the response contains the following entries in "source" of "attributes" array
            | source |
            | STITCH |
        and the response only contains the following entries in "source" of "attributes" array
            | source |
            | STITCH |
        and the response contains the following entries in "value" of "attributes" array
            | value     |
            | 180.15742 |
        and the response contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
        and the response only contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |


    Scenario: Check STITCH links transformer
        Given the transformer
        when we fire "/links/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "score_threshold",
                    "value": "900"
                },
                {
                    "name": "limit",
                    "value": "0"
                }
            ],
            "collection": [
                {
                    "id": "ChEMBL:CHEMBL25",
                    "identifiers": {
                        "pubchem": "CID:2244",
                        "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                    }
                }
            ]
        }
        """
        then the size of the response is 19
        and the response contains the following entries in "biolink_class"
            | biolink_class |
            | Protein       |
        and the response only contains the following entries in "biolink_class"
            | biolink_class |
            | Protein       |
        and the response contains the following entries in "source"
            | source                         |
            | STITCH link transformer |
        and the response only contains the following entries in "source"
            | source                         |
            | STITCH link transformer |


