Feature: Check MSigDB transformer
    Background: Specify transformer API
        Given a transformer at "https://molepro-msigdb-transformer.ci.transltr.io/msigdb"

    Scenario: Check MSigDB pathway transformer transformer info
        Given the transformer
        when we fire "/pathways/transformer_info" query
        then the value of "name" should be "MSigDB pathways transformer"
        and the value of "function" should be "exporter"
        and the value of "knowledge_map.input_class" should be "gene"
        and the value of "knowledge_map.output_class" should be "pathway"
        and the value of "properties.source_version" should be "msigdb_v2024.1.Hs"
        and the value of "properties.source_date" should be "2024-08-09"
        and the size of "parameters" should be 0


    Scenario: Check MSigDB genes transformer transformer info
        Given the transformer
        when we fire "/genes/transformer_info" query
        then the value of "name" should be "MSigDB genes transformer"
        and the value of "function" should be "exporter"
        and the value of "knowledge_map.input_class" should be "pathway"
        and the value of "knowledge_map.output_class" should be "gene"
        and the value of "properties.source_version" should be "msigdb_v2024.1.Hs"
        and the value of "properties.source_date" should be "2024-08-09"
        and the size of "parameters" should be 0



    Scenario: Check MSigDB pathway transformer with NCBI identifier
        Given the transformer
        when we fire "/pathways/transform" query with the following body:        
        """
            {
                "controls": [],
                "collection": [
                    {
                        "biolink_class": "Gene",
                        "id": "test",
                        "identifiers": {
                            "entrez": "NCBIGene:946"
                        },
                        "provided_by": "MoleProDB node producer",
                        "source": "MolePro"
                    }
                ]
            }
        """
        then the size of the response is 77
        and the response contains the following entries in "id"
            | id                                                |
            | MSigDB:GSE10856_CTRL_VS_TNFRSF6B_IN_MACROPHAGE_DN |
            | MSigDB:GSE15215_CD2_POS_VS_NEG_PDC_UP             |
        and the response contains the following entries in "biolink_class"
            | biolink_class |
            | Pathway       |
        and the response only contains the following entries in "biolink_class"
            | biolink_class |
            | Pathway       |
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | MSigDB pathways transformer     |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | MSigDB pathways transformer     |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | MSigDB |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | MSigDB |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id|
            | test     |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id|
            | test     |             

    Scenario: Check MSigDB gene transformer with gene_set/pathway
        Given the transformer
        when we fire "/genes/transform" query with the following body:        
        """
            {
                "controls": [],
                "collection": [
                    {
                        "biolink_class": "Pathway",
                        "id": "test",
                        "identifiers": {
                            "msigdb": "MSigDB:GSE28726_NAIVE_CD4_TCELL_VS_NAIVE_NKTCELL_DN"
                        },
                        "provided_by": "MoleProDB node producer",
                        "source": "MolePro"
                    }
                ]
            }
        """
        then the size of the response is 200
        and the response contains the following entries in "id"
            | id            |
            | NCBIGene:9400 |
            | NCBIGene:54474|
            | NCBIGene:6899 |
            | NCBIGene:120  |
        and the response contains the following entries in "biolink_class"
            | biolink_class |
            | Gene          |
        and the response only contains the following entries in "biolink_class"
            | biolink_class |
            | Gene          |
        and the response contains the following entries in "provided_by"
            | provided_by               |
            | MSigDB genes transformer  |
        and the response only contains the following entries in "provided_by"
            | provided_by                  |
            | MSigDB genes transformer     |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | MSigDB |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | MSigDB |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id|
            | test |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id|
            | test             |
