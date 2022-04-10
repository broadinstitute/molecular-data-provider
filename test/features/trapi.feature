#https://molepro-trapi.ci.transltr.io/molepro/trapi/v1.2/ui/

Feature: Check reasoner API

    Background: Specify Reasoner API
        Given a reasoner API at "https://molepro-trapi.test.transltr.io/molepro/trapi/v1.2"


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
        then the size of "message.results" should be 60


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
                            "ids": ["MONDO:0021668"],
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
        then the size of "message.results" should be 340


    Scenario: Check indications with a different predicate
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
                            "predicates": ["biolink:related_to"]
                        }
                    },
                    "nodes": {
                        "n00": {
                            "ids": ["MONDO:0021668"],
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
        then the size of "message.results" should be 936


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
                            "predicates": ["biolink:related_to"]
                        }
                    },
                    "nodes": {
                        "n00": {
                            "ids": ["MONDO:0021668"],
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
        then the size of "message.results" should be 936


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
                    "DRUGBANK:DB00472",
                    "DRUGBANK:DB00176",
                    "DRUGBANK:DB00715",
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
        then the size of "message.results" should be 126


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
            }
        }
        """
        then the size of "message.results" should be 169


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
            }
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
            }
        }
        """
        then the size of "message.results" should be 272


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
                                    "value": ["FDA Approval","FDA Clinical Research Phase 2"]
                                }
                            ]
                        }
                    }
                }
            }
        }
        """
        then the size of "message.results" should be 52


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
                            "constraints": [
                                {
                                    "id": "biolink:primary_knowledge_source",
                                    "name": "primary knowledge source",
                                    "operator": "==",
                                    "value": "infores:drugbank"
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
            }
        }
        """
        then the size of "message.results" should be 16



