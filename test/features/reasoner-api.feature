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
        then the size of "results" should be 30


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



    Scenario: Check disease-gene connections
        Given the reasoner API
        when we fire "/query" query with the following body:
        """
        {
            "message": {
                "query_graph": {
                    "edges": [
                        {
                            "id": "e01",
                            "source_id": "n00",
                            "target_id": "n02",
                            "type": "related_to"
                        }
                    ],
                    "nodes": [
                        {
                            "curie": "MONDO:0007455",
                            "id": "n00",
                            "type": "disease"
                        },
                        {
                            "id": "n02",
                            "type": "gene"
                        }
                    ]
                }
            }
        }
        """
        then the size of "results" should be 29

