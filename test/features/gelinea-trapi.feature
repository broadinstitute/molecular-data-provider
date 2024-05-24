Feature: Check reasoner API

    Background: Specify Reasoner API
        Given a TRAPI at "https://translator.broadinstitute.org/gelinea-trapi/v1.5"


    Scenario: Check targets
        Given the TRAPI
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "nodes": {
                        "pathway": {
                            "categories": [
                                "biolink:Pathway"
                            ]
                        },
                        "gene": {
                            "set_interpretation": "MANY",
                            "ids": ["UUID:1231-2353"],
                            "member_ids": [
                                "HGNC:18017",
                                "HGNC:12017",
                                "HGNC:25525",
                                "HGNC:9021",
                                "NCBIGene:5566",
                                "NCBIGene:2023",
                                "NCBIGene:79023",
                                "NCBIGene:81929",
                                "NCBIGene:8086"
                            ]
                        }
                    },
                    "edges": {
                        "t_edge": {
                            "object": "gene",
                            "subject": "pathway",
                            "predicates": [
                                "biolink:related_to"
                            ],
                            "knowledge_type":"inferred"
                        }
                    }
                }
            },
            "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 3
        and the size of "logs" should be 4
        and the size of "message.knowledge_graph.edges" should be 12
        and the size of "message.knowledge_graph.nodes" should be 13
        and the response contains the following primary knowledge sources
            | primary_knowledge_source |
            | infores:gelinea          |


