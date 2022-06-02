Feature: Check HMDB transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-hmdb-transformer.test.transltr.io/hmdb"


    Scenario: Check HMDB producer info
        Given the transformer
        when we fire "/metabolites/transformer_info" query
        then the value of "name" should be "HMDB metabolite producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "5.0 (2021-11-17)"
        and the size of "parameters" should be 1


    Scenario: Check HMDB protein targets transformer info
        Given the transformer
        when we fire "/protein_targets/transformer_info" query
        then the value of "name" should be "HMDB target proteins transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "protein"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "5.0 (2021-11-17)"
        and the size of "parameters" should be 0


    Scenario: Check HMDB gene targets transformer info
        Given the transformer
        when we fire "/gene_targets/transformer_info" query
        then the value of "name" should be "HMDB target genes transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "5.0 (2021-11-17)"
        and the size of "parameters" should be 0


    Scenario: Check HMDB disorders transformer info
        Given the transformer
        when we fire "/disorders/transformer_info" query
        then the value of "name" should be "HMDB disorders transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "disease"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "5.0 (2021-11-17)"
        and the size of "parameters" should be 0


    Scenario: Check HMDB protein targets transformer
        Given the transformer
        when we fire "/protein_targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "CHEBI:52717",
                    "identifiers": {
                        "inchikey": "GXJABQQUPOEUTA-RDJZCZTQSA-N"
                    },
                    "provided_by": "HMDB metabolite producer",
                    "source": "HMDB"
                }
            ]
        }
        """
        then the size of the response is 9
        and the response contains the following entries in "id"
            | id               |
            | UniProtKB:P08684 |
            | UniProtKB:P11712 |
            | UniProtKB:P33261 |
            | UniProtKB:P05177 |
            | UniProtKB:P10632 |
            | UniProtKB:P10635 |
            | UniProtKB:P04798 |
            | UniProtKB:P23219 |
            | UniProtKB:O15431 |
        and the response only contains the following entries in "id"
            | id               |
            | UniProtKB:P08684 |
            | UniProtKB:P11712 |
            | UniProtKB:P33261 |
            | UniProtKB:P05177 |
            | UniProtKB:P10632 |
            | UniProtKB:P10635 |
            | UniProtKB:P04798 |
            | UniProtKB:P23219 |
            | UniProtKB:O15431 |
        and the response contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | HMDB             |
        and the response only contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | HMDB             |
        and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by                      |
            | HMDB target proteins transformer |
        and the response only contains the following entries in "provided_by" of "attributes" array
            | provided_by                      |
            | HMDB target proteins transformer |


    Scenario: Check HMDB protein targets transformer
        Given the transformer
        when we fire "/protein_targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "HMDB:HMDB0011105",
                    "identifiers": {
                        "hmdb": "HMDB:HMDB0011105"
                    },
                    "provided_by": "HMDB metabolite producer",
                    "source": "HMDB"
                }
            ]
        }
        """
        then the size of the response is 3
        and the response contains the following entries in "id"
            | id               |
            | UniProtKB:P18440 |
            | UniProtKB:P11245 |
            | UniProtKB:A4Z6T7 |
        and the response only contains the following entries in "id"
            | id               |
            | UniProtKB:P18440 |
            | UniProtKB:P11245 |
            | UniProtKB:A4Z6T7 |
        and the response contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | HMDB             |
        and the response only contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | HMDB             |
        and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by                      |
            | HMDB target proteins transformer |
        and the response only contains the following entries in "provided_by" of "attributes" array
            | provided_by                      |
            | HMDB target proteins transformer |


    Scenario: Check HMDB gene targets transformer
        Given the transformer
        when we fire "/gene_targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "HMDB:HMDB0011105",
                    "identifiers": {
                        "hmdb": "HMDB:HMDB0011105"
                    },
                    "provided_by": "HMDB metabolite producer",
                    "source": "HMDB"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "id"
            | id          |
            | NCBIGene:9  |
            | NCBIGene:10 |
        and the response only contains the following entries in "id"
            | id          |
            | NCBIGene:9  |
            | NCBIGene:10 |
        and the response contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | HMDB             |
        and the response only contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | HMDB             |
        and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by                   |
            | HMDB target genes transformer |
        and the response only contains the following entries in "provided_by" of "attributes" array
            | provided_by                   |
            | HMDB target genes transformer |


    Scenario: Check HMDB disorders transformer
        Given the transformer
        when we fire "/disorders/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "HMDB:HMDB0001875",
                    "identifiers": {
                        "hmdb": "HMDB:HMDB0001875"
                    },
                    "provided_by": "HMDB metabolite producer",
                    "source": "HMDB"
                }
            ]
        }
        """
        then the size of the response is 9
        and the response contains the following entries in "id"
            | id            |
            | MONDO:0005361 |
            | MONDO:0005101 |
            | MONDO:0009960 |
            | MONDO:0005011 |
            | MONDO:0013209 |
            | EFO:0009959   |
            | MONDO:0008383 |
            | MONDO:0002046 |
            | UMLS:C0001973 |
        and the response only contains the following entries in "id"
            | id            |
            | MONDO:0005361 |
            | MONDO:0005101 |
            | MONDO:0009960 |
            | MONDO:0005011 |
            | MONDO:0013209 |
            | EFO:0009959   |
            | MONDO:0008383 |
            | MONDO:0002046 |
            | UMLS:C0001973 |
        and the response contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | HMDB             |
        and the response only contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | HMDB             |
        and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by                |
            | HMDB disorders transformer |
        and the response only contains the following entries in "provided_by" of "attributes" array
            | provided_by                |
            | HMDB disorders transformer |


    Scenario: Check HMDB locations transformer
        Given the transformer
        when we fire "/locations/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "HMDB:HMDB0011105",
                    "identifiers": {
                        "hmdb": "HMDB:HMDB0011105"
                    },
                    "provided_by": "HMDB metabolite producer",
                    "source": "HMDB"
                },
                {
                    "biolink_class": "SmallMolecule",
                    "id": "HMDB:HMDB0001250",
                    "identifiers": {
                        "hmdb": "HMDB:HMDB0001250"
                    },
                    "provided_by": "HMDB metabolite producer",
                    "source": "HMDB"
                },
                {
                    "biolink_class": "SmallMolecule",
                    "id": "HMDB:HMDB0000001",
                    "identifiers": {
                        "hmdb": "HMDB:HMDB0000001"
                    },
                    "provided_by": "HMDB metabolite producer",
                    "source": "HMDB"
                }
            ]
        }
        """
        then the size of the response is 10
        and the response contains the following entries in "id"
            | id             |
            | GO:0005737     |
            | UBERON:0000178 |
            | UBERON:0001988 |
            | UBERON:0001088 |
            | UBERON:0002113 |
            | UBERON:0002107 |
            | UBERON:0000158 |
            | GO:0016020     |
            | UBERON:0001836 |
            | UBERON:0001987 |
        and the response only contains the following entries in "id"
            | id             |
            | GO:0005737     |
            | UBERON:0000178 |
            | UBERON:0001988 |
            | UBERON:0001088 |
            | UBERON:0002113 |
            | UBERON:0002107 |
            | UBERON:0000158 |
            | GO:0016020     |
            | UBERON:0001836 |
            | UBERON:0001987 |
        and the response contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | HMDB             |
        and the response only contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | HMDB             |
        and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by                |
            | HMDB locations transformer |
        and the response only contains the following entries in "provided_by" of "attributes" array
            | provided_by                |
            | HMDB locations transformer |


    Scenario: Check HMDB pathways transformer
        Given the transformer
        when we fire "/pathways/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "HMDB:HMDB0011105",
                    "identifiers": {
                        "hmdb": "HMDB:HMDB0011105"
                    },
                    "provided_by": "HMDB metabolite producer",
                    "source": "HMDB"
                },
                {
                    "biolink_class": "MoleculeMixture",
                    "id": "HMDB:HMDB0000008",
                    "identifiers": {
                        "hmdb": "HMDB:HMDB0000008"
                    },
                    "provided_by": "HMDB metabolite producer",
                    "source": "HMDB"
                }
            ]
        }
        """
        then the size of the response is 5
        and the response contains the following entries in "id"
            | id                    |
            | SMPDB:SMP00028        |
            | SMPDB:SMP00198        |
            | SMPDB:SMP00502        |
            | SMPDB:SMP00201        |
            | KEGG.PATHWAY:map00640 |
        and the response only contains the following entries in "id"
            | id                    |
            | SMPDB:SMP00028        |
            | SMPDB:SMP00198        |
            | SMPDB:SMP00502        |
            | SMPDB:SMP00201        |
            | KEGG.PATHWAY:map00640 |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | HMDB:HMDB0000008  |
            | HMDB:HMDB0011105  |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | HMDB:HMDB0000008  |
            | HMDB:HMDB0011105  |
        and the response contains the following entries in "provided_by"
            | provided_by                |
            | HMDB pathways transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                |
            | HMDB pathways transformer |
