Feature: Check reasoner API

    Background: Specify Reasoner API
        Given a reasoner API at "http://localhost:8080"


    Scenario: Check targets
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": [
                        {
                            "id": "e00",
                            "source_id": "n00",
                            "target_id": "n01",
                            "type": "affects"
                        }
                    ],
                    "nodes": [
                        {
                            "curie": "CID:2244",
                            "id": "n00",
                            "type": "chemical_substance"
                        },
                        {
                            "id": "n01",
                            "type": "gene"
                        }
                    ]
                }
            }
        }
        """
        then the size of "results" should be 65


    Scenario: Check ChEMBL targets
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": [
                        {
                            "id": "e00",
                            "source_id": "n00",
                            "target_id": "n01",
                            "type": "affects"
                        }
                    ],
                    "nodes": [
                        {
                            "curie": "ChEMBL:CHEMBL25",
                            "id": "n00",
                            "type": "chemical_substance"
                        },
                        {
                            "id": "n01",
                            "type": "gene"
                        }
                    ]
                }
            }
        }
        """
        then the size of "results" should be 65


    Scenario: Check indications
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": [
                        {
                            "id": "e00",
                            "source_id": "n00",
                            "target_id": "n01",
                            "type": "treated_by"
                        }
                    ],
                    "nodes": [
                        {
                            "curie": "MONDO:0007455",
                            "id": "n00",
                            "type": "disease"
                        },
                        {
                            "id": "n01",
                            "type": "chemical_substance"
                        }
                    ]
                }
            }
        }
        """
        then the size of "results" should be 0



    Scenario: Check indications for a different disease
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": [
                        {
                            "id": "e00",
                            "source_id": "n00",
                            "target_id": "n01",
                            "type": "treated_by"
                        }
                    ],
                    "nodes": [
                        {
                            "curie": "MONDO:0021668",
                            "id": "n00",
                            "type": "disease"
                        },
                        {
                            "id": "n01",
                            "type": "chemical_substance"
                        }
                    ]
                }
            }
        }
        """
        then the size of "results" should be 55


    Scenario: Check has_metabolite
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": [
                        {
                            "id": "e00",
                            "source_id": "n00",
                            "target_id": "n01",
                            "type": "has_metabolite"
                        }
                    ],
                    "nodes": [
                        {
                            "curie": "ChEMBL:CHEMBL424",
                            "id": "n00",
                            "type": "chemical_substance"
                        },
                        {
                            "id": "n01",
                            "type": "chemical_substance"
                        }
                    ]
                }
            }
        }
        """
        then the size of "results" should be 5



    Scenario: Check indications
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": [
                        {
                            "id": "e00",
                            "source_id": "n00",
                            "target_id": "n01",
                            "type": "treats"
                        }
                    ],
                    "nodes": [
                        {
                            "curie": "ChEMBL:CHEMBL424",
                            "id": "n00",
                            "type": "chemical_substance"
                        },
                        {
                            "id": "n01",
                            "type": "disease"
                        }
                    ]
                }
            }
        }
        """
        then the size of "results" should be 16


    Scenario: Check assays
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": [
                        {
                            "id": "e00",
                            "source_id": "n00",
                            "target_id": "n01",
                            "type": "has_evidence"
                        }
                    ],
                    "nodes": [
                        {
                            "curie": "ChEMBL:CHEMBL424",
                            "id": "n00",
                            "type": "chemical_substance"
                        },
                        {
                            "id": "n01",
                            "type": "assay"
                        }
                    ]
                }
            }
        }
        """
        then the size of "results" should be 518


    Scenario: Check MOA
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": [
                        {
                            "id": "e00",
                            "source_id": "n00",
                            "target_id": "n01",
                            "type": "affects"
                        }
                    ],
                    "nodes": [
                        {
                            "curie": "CID:2244",
                            "id": "n00",
                            "type": "chemical_substance"
                        },
                        {
                            "id": "n01",
                            "type": "molecular_entity"
                        }
                    ]
                }
            }
        }
        """
        then the size of "results" should be 1

