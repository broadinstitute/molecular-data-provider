
Feature: Check reasoner API

    Background: Specify Reasoner API
        Given a reasoner API at "https://translator.broadinstitute.org/molepro/trapi/v1.5"


    Scenario: Check targets
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": {
                        "e00": {
                            "subject": "n00",
                            "object": "n01",
                            "predicates": ["biolink:affects"]
                        }
                    },
                    "nodes": {
                        "n00": {
                            "ids": ["CID:2244"],
                            "categories": ["biolink:SmallMolecule"]
                        },
                        "n01": {
                            "categories": ["biolink:Gene"]
                        }
                    }
                }
            },
            "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 94
        and the size of "message.knowledge_graph.edges" should be 94
        and the size of "message.knowledge_graph.nodes" should be 61


    Scenario: Check indications
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": {
                        "e00": {
                            "subject": "n00",
                            "object": "n01",
                            "predicates": ["biolink:treated_by"]
                        }
                    },
                    "nodes": {
                        "n00": {
                            "ids": ["MONDO:0007455"],
                            "categories": ["biolink:Disease"]
                        },
                        "n01": {
                            "categories": ["biolink:SmallMolecule"]
                        }
                    }
                }
            },
            "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 0


    Scenario: Check indications for a different disease
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": {
                        "e00": {
                            "subject": "n00",
                            "object": "n01",
                            "predicates": ["biolink:treated_by"]
                        }
                    },
                    "nodes": {
                        "n00": {
                            "ids": ["MONDO:0006805"],
                            "categories": ["biolink:Disease"]
                        },
                        "n01": {
                            "categories": ["biolink:SmallMolecule"]
                        }
                    }
                }
            },
            "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 23


    Scenario: Check indications with a different category
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": {
                        "e00": {
                            "subject": "n00",
                            "object": "n01",
                            "predicates": ["biolink:treated_by"]
                        }
                    },
                    "nodes": {
                        "n00": {
                            "ids": ["MONDO:0006805"],
                            "categories": ["biolink:Disease"]
                        },
                        "n01": {
                            "categories": ["biolink:ChemicalEntity"]
                        }
                    }
                }
            },
            "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 26


    Scenario: Check indications with a object id
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": {
                        "e00": {
                            "subject": "n01",
                            "object": "n00",
                            "predicates": ["biolink:treats"]
                        }
                    },
                    "nodes": {
                        "n00": {
                            "ids": ["MONDO:0006805"],
                            "categories": ["biolink:Disease"]
                        },
                        "n01": {
                            "categories": ["biolink:SmallMolecule"]
                        }
                    }
                }
            },
            "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 23


    Scenario: Check indications with no predicate
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
          "message": {
            "query_graph": {
              "edges": {
                "e00": {
                  "subject": "n01",
                  "object": "n00"
                }
              },
              "nodes": {
                "n00": {
                  "ids": [
                    "DRUGBANK:DB00215",
                    "DRUGBANK:DB01175",
                    "DRUGBANK:DB00176",
                    "DRUGBANK:DB01104"
                  ],
                  "categories": ["biolink:SmallMolecule"]
                },
                "n01": {
                  "categories": ["biolink:Disease"]
                }
              }
            }
          },
          "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 2103
        and the size of "message.knowledge_graph.edges" should be 2103
        and the size of "message.knowledge_graph.nodes" should be 1056


    Scenario: Check query with ChemicalEntity instead of SmallMolecule
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "nodes": {
                        "n0": {
                            "ids": ["PUBCHEM.COMPOUND:5755"],
                            "categories": [
                                "biolink:ChemicalEntity"
                            ],
                            "name": "Prednisone"
                        },
                        "n1": {
                            "categories": [
                                "biolink:Disease"
                            ]
                        }
                    },
                    "edges": {
                        "e0": {
                            "subject": "n0",
                            "object": "n1",
                            "predicates": ["biolink:related_to"]
                        }
                    }
                }
            },
            "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 279
        and the size of "message.knowledge_graph.edges" should be 279
        and the size of "message.knowledge_graph.nodes" should be 216


    Scenario: Check query with unknown predicate
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "nodes": {
                        "n0": {
                            "ids": ["CHEBI:41879"],
                            "categories": [
                                "biolink:ChemicalEntity"
                            ],
                            "name": "Dexamethasone"
                        },
                        "n1": {
                            "categories": [
                                "biolink:DiseaseOrPhenotypicFeature"
                            ]
                        }
                    },
                    "edges": {
                        "e0": {
                            "subject": "n0",
                            "object": "n1",
                            "predicates": ["biolink:has_real_world_evidence_of_association_with"]
                        }
                    }
                }
            },
            "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 0


    Scenario: Check query with no constraints
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": {
                        "e02": {
                            "object": "n0",
                            "subject": "n2",
                            "predicates": [
                                "biolink:related_to"
                            ]
                        }
                    },
                    "nodes": {
                        "n0": {
                            "ids": [
                                "NCBIGene:2321"
                            ],
                            "categories": [
                                "biolink:Gene"
                            ]
                        },
                        "n2": {
                            "categories": [
                                "biolink:SmallMolecule"
                            ]
                        }
                    }
                }
            },
            "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 374
        and the size of "message.knowledge_graph.edges" should be 374
        and the size of "message.knowledge_graph.nodes" should be 247


    Scenario: Check query with node constraints
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": {
                        "e02": {
                            "object": "n0",
                            "subject": "n2",
                            "predicates": [
                                "biolink:related_to"
                            ]
                        }
                    },
                    "nodes": {
                        "n0": {
                            "ids": [
                                "NCBIGene:2321"
                            ],
                            "categories": [
                                "biolink:Gene"
                            ]
                        },
                        "n2": {
                            "categories": [
                                "biolink:SmallMolecule"
                            ],
                            "constraints": [
                                {
                                    "id": "biolink:highest_FDA_approval_status",
                                    "name": "highest FDA approval status",
                                    "operator": "==",
                                    "value": ["regular_fda_approval","fda_clinical_research_phase_2"]
                                }
                            ]
                        }
                    }
                }
            },
            "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 111
        and the size of "message.knowledge_graph.edges" should be 111
        and the size of "message.knowledge_graph.nodes" should be 45


    Scenario: Check query with edge constraints
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": {
                        "e02": {
                            "object": "n0",
                            "subject": "n2",
                            "predicates": [
                                "biolink:related_to"
                            ],
                            "attribute_constraints": [
                                {
                                    "id": "biolink:primary_knowledge_source",
                                    "name": "primary knowledge source",
                                    "operator": "==",
                                    "value": "infores:chembl"
                                }
                            ]
                        }
                    },
                    "nodes": {
                        "n0": {
                            "ids": [
                                "NCBIGene:2321"
                            ],
                            "categories": [
                                "biolink:Gene"
                            ]
                        },
                        "n2": {
                            "categories": [
                                "biolink:SmallMolecule"
                            ]
                        }
                    }
                }
            },
            "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 218
        and the size of "message.knowledge_graph.edges" should be 218
        and the size of "message.knowledge_graph.nodes" should be 199


    Scenario: Check query with edge constraints
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": {
                        "e00": {
                            "constraints": [],
                            "object": "n01",
                            "predicates": [
                                "biolink:regulates",
                                "biolink:negatively_regulates",
                                "biolink:positively_regulates",
                                "biolink:entity_positively_regulates_entity",
                                "biolink:entity_negatively_regulates_entity",
                                "biolink:entity_regulates_entity",
                                "biolink:correlated_with"
                            ],
                            "subject": "n00"
                        }
                    },
                    "nodes": {
                        "n00": {
                            "constraints": [],
                            "ids": [
                                "HGNC:23785"
                            ],
                            "is_set": false
                        },
                        "n01": {
                            "categories": [
                                "biolink:Gene",
                                "biolink:Polypeptide"
                            ],
                            "constraints": [],
                            "is_set": false
                        }
                    }
                }
            },
            "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 0


    Scenario: Check query with edge constraints
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": {
                        "e00": {
                            "subject": "n00",
                            "object": "n01",
                            "predicates": [
                                "biolink:treats"
                            ]
                        }
                    },
                    "nodes": {
                        "n00": {
                            "categories": [
                                "biolink:Procedure"
                            ]
                        },
                        "n01": {
                            "categories": [
                                "biolink:Disease"
                            ],
                            "ids": [
                                "MONDO:0004833"
                            ]
                        }
                    }
                }
            },
            "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 0


    Scenario: Check query with two qualifier constraints
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": {
                        "e00": {
                            "subject": "n01",
                            "object": "n00",
                            "qualifier_constraints": [
                                {
                                    "qualifier_set": [
                                        {
                                            "qualifier_type_id": "biolink:subject_aspect_qualifier",
                                            "qualifier_value": "tautomer"
                                        }
                                    ]
                                },
                                {
                                    "qualifier_set": [
                                        {
                                            "qualifier_type_id": "biolink:derivative_qualifier",
                                            "qualifier_value": "conjugate_acid"
                                        }
                                    ]
                                }
                            ]
                        }
                    },
                    "nodes": {
                        "n00": {
                            "ids": [
                                "CID:193806"
                            ]
                        },
                        "n01": {
                            "categories": [
                                "biolink:SmallMolecule"
                            ]
                        }
                    }
                }
            },
            "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 4


    Scenario: Check query with one qualifier constraint
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": {
                        "e00": {
                            "subject": "n01",
                            "object": "n00",
                            "qualifier_constraints": [
                                {
                                    "qualifier_set": [
                                        {
                                            "qualifier_type_id": "biolink:subject_aspect_qualifier",
                                            "qualifier_value": "tautomer"
                                        }
                                    ]
                                }
                            ]
                        }
                    },
                    "nodes": {
                        "n00": {
                            "ids": [
                                "CID:193806"
                            ]
                        },
                        "n01": {
                            "categories": [
                                "biolink:SmallMolecule"
                            ]
                        }
                    }
                }
            },
            "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 2


    Scenario: Check query with workflow
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "nodes": {
                        "n2": {
                            "ids": [
                                "NCBIGene:819"
                            ],
                            "categories": [
                                "biolink:Gene"
                            ]
                        },
                        "n3": {
                            "categories": [
                                "biolink:SmallMolecule"
                            ]
                        }
                    },
                    "edges": {
                        "e03": {
                            "subject": "n2",
                            "object": "n3",
                            "predicates": [
                                "biolink:interacts_with"
                            ]
                        }
                    }
                }
            },
            "workflow": [
                {
                    "id": "lookup"
                },
                {
                    "id": "annotate_nodes",
                    "parameters": {
                        "attributes": [
                            "biolink:highest_FDA_approval_status",
                            "oral",
                            "topical"
                        ]
                    }
                }
            ],
            "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 2


    Scenario: Check chemically_similar_to query
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "nodes": {
                        "n0": {
                            "ids": [
                                "CID:2244"
                            ],
                            "categories": [
                                "biolink:SmallMolecule"
                            ]
                        },
                        "n1": {
                            "categories": [
                                "biolink:SmallMolecule"
                            ]
                        }
                    },
                    "edges": {
                        "e00": {
                            "subject": "n0",
                            "object": "n1",
                            "predicates": [
                                "biolink:chemically_similar_to"
                            ]
                        }
                    }
                }
            },
            "submitter": "behave test"
        }
        """
        then the size of "message.results" should be 117
        and the size of "message.knowledge_graph.edges" should be 117
        and the size of "message.knowledge_graph.nodes" should be 116

