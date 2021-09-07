Feature: Check Translator Reasoner API

    Background: Specify Reasoner API
        Given a reasoner API at "https://translator.broadinstitute.org/molepro/trapi/v1.2"


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
            }
        }
        """
        then the size of "message.results" should be 56


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
            }
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
            }
        }
        """
        then the size of "message.results" should be 55


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
            }
        }
        """
        then the size of "message.results" should be 55


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
            }
        }
        """
        then the size of "message.results" should be 55


