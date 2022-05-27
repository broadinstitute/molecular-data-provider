Feature: Check Pharos transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-pharos-transformer.ci.transltr.io/pharos"


    Scenario: Check Pharos transformer info
        Given the transformer
        when we fire "/gene_targets/transformer_info" query
        then the value of "name" should be "Pharos target genes transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the size of "parameters" should be 0


    Scenario: Check Pharos transformer
        Given the transformer
        when we fire "/gene_targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "id": "CID:2244",
                    "biolink_class": "ChemicalSubstance",
                    "provided_by": "pharos",
                    "source": "pharos",
                    "identifiers": {
                        "chembl": "ChEMBL:CHEMBL25",
                        "pubchem": "CID:2244"
                    }
                }
            ]
        }
        """
        then the size of the response is 3
        and the response contains the following entries in "id"
            | id            |
            | NCBIGene:5743 |
            | NCBIGene:5742 |
            | NCBIGene:9311 |
        and the response only contains the following entries in "id"
            | id            |
            | NCBIGene:5743 |
            | NCBIGene:5742 |
            | NCBIGene:9311 |
        and the response contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | Pharos           |
        and the response only contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | Pharos           |



    Scenario: Check Pharos gene-target transformer with ChEMBL input
        Given the transformer
        when we fire "/gene_targets/transform" query with the following body:
        """
        {
        "controls": [],
        "collection": [
        {
            "biolink_class": "SmallMolecule",
            "id": "ChEMBL:CHEMBL99995",
            "provided_by": "pharos",
            "source": "pharos",
            "identifiers": {
            "chembl": "ChEMBL:CHEMBL99995"
        }
        }
        ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "id"
            | id            |
            | NCBIGene:6868 |
        and the response only contains the following entries in "id"
            | id            |
            | NCBIGene:6868 |
        and the response contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | Pharos           |
        and the response only contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | Pharos           |
