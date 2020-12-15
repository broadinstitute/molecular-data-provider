Feature: Check CMAP transformer

    Background: Specify transformer API
        Given a transformer at "https://translator.broadinstitute.org/depmap_expander"


    Scenario: Check transformer info
        Given the transformer
        when we fire "/transformer_info" query
        then the size of "parameters" should be 4
        and the value of "label" should be "DepMap"


    Scenario: Check transformation
        Given the transformer
        when we fire "/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "correlation threshold",
                    "value": "0.25"
                },
                {
                    "name": "correlation direction",
                    "value": "correlation"
                },
                {
                    "name": "correlated values",
                    "value": "gene knockout"
                },
                {
                    "name": "maximum number",
                    "value": "0"
                }
            ],
            "genes": [
                {
                    "attributes": [],
                    "gene_id": "NCBIGene:1645",
                    "identifiers": {
                        "entrez": "NCBIGene:1645"
                    }
                }
            ]
        }
        """
        then the size of the response is 8


    Scenario: Check transformation
        Given the transformer
        when we fire "/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "correlation threshold",
                    "value": "0.25"
                },
                {
                    "name": "correlation direction",
                    "value": "correlation"
                },
                {
                    "name": "correlated values",
                    "value": "gene knockout"
                },
                {
                    "name": "maximum number",
                    "value": "1"
                }
            ],
            "genes": [
                {
                    "attributes": [],
                    "gene_id": "NCBIGene:1645",
                    "identifiers": {
                        "entrez": "NCBIGene:1645"
                    }
                }
            ]
        }
        """
        then the size of the response is 1


    Scenario: Check transformation
        Given the transformer
        when we fire "/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "correlation threshold",
                    "value": "0.25"
                },
                {
                    "name": "correlation direction",
                    "value": "correlation"
                },
                {
                    "name": "correlated values",
                    "value": "gene knockout"
                },
                {
                    "name": "maximum number",
                    "value": "2"
                }
            ],
            "genes": [
                {
                    "attributes": [],
                    "gene_id": "NCBIGene:1645",
                    "identifiers": {
                        "entrez": "NCBIGene:1645"
                    }
                }
            ]
        }
        """
        then the size of the response is 2


    Scenario: Check transformation
        Given the transformer
        when we fire "/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "correlation threshold",
                    "value": "0.25"
                },
                {
                    "name": "correlation direction",
                    "value": "correlation"
                },
                {
                    "name": "correlated values",
                    "value": "gene knockout"
                },
                {
                    "name": "maximum number",
                    "value": "8"
                }
            ],
            "genes": [
                {
                    "attributes": [],
                    "gene_id": "NCBIGene:1645",
                    "identifiers": {
                        "entrez": "NCBIGene:1645"
                    }
                }
            ]
        }
        """
        then the size of the response is 8


    Scenario: Check transformation
        Given the transformer
        when we fire "/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "correlation threshold",
                    "value": "0.25"
                },
                {
                    "name": "correlation direction",
                    "value": "correlation"
                },
                {
                    "name": "correlated values",
                    "value": "gene knockout"
                },
                {
                    "name": "maximum number",
                    "value": "9"
                }
            ],
            "genes": [
                {
                    "attributes": [],
                    "gene_id": "NCBIGene:1645",
                    "identifiers": {
                        "entrez": "NCBIGene:1645"
                    }
                }
            ]
        }
        """
        then the size of the response is 8
