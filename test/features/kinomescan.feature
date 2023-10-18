Feature: Check Kinomescan transformer

    Background: Specify transformer API
        Given a transformer at "https://translator.broadinstitute.org/kinomescan"


    Scenario: Check transformer info
        Given the transformer 
        when we fire "/compounds/transformer_info" query 
        then the size of "parameters" should be 1
        and the value of "label" should be "KINOMEscan"
        and the value of "version" should be "2.5.0"
        and the value of "function" should be "producer"

    Scenario: Check Kinomescan producer - single name 
        Given the transformer
        when we fire "/compounds/transform" query with the following body: 
        """
        {
            "controls":[
                {
                    "name": "small molecule",
                    "value": "CID:2051"
                },
                {
                    "name": "small molecule",
                    "value": "GSK1363089"
                },
                {
                    "name": "small molecule",
                    "value": "Foretinib"
                }
            ] 
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "id"
            | id                            |
            | LINCS.SMALLMOLECULE:HMSL10223 |
            | LINCS.SMALLMOLECULE:HMSL10157 |
        and the response only contains the following entries in "id"
            | id                            |
            | LINCS.SMALLMOLECULE:HMSL10223 |
            | LINCS.SMALLMOLECULE:HMSL10157 |
        and the response contains the following entries in "source"
            | source     |
            | KINOMEscan |
        and the response only contains the following entries in "source"
            | source     |
            | KINOMEscan |

    Scenario: Check Kinomescan producer - multi name
        Given the transformer
        when we fire "/compounds/transform" query with the following body:
        """
        { 
            "controls":[
                {
                    "name": "small molecule",
                    "value": "CID:2051"
                },
                {
                    "name": "small molecule",
                    "value": "Erlotinib"
                },
                {
                    "name": "small molecule",
                    "value": "GSK1363089"
                }
            ]
            
        }
        """
        then the size of the response is 3
        and the response contains the following entries in "id"
            | id                            |
            | LINCS.SMALLMOLECULE:HMSL10223 |
            | LINCS.SMALLMOLECULE:HMSL10097 |
            | LINCS.SMALLMOLECULE:HMSL10157 |
        and the response only contains the following entries in "id"
            | id                            |
            | LINCS.SMALLMOLECULE:HMSL10223 |
            | LINCS.SMALLMOLECULE:HMSL10097 |
            | LINCS.SMALLMOLECULE:HMSL10157 |
        and the response contains the following entries in "source"
            | source     |
            | KINOMEscan |
        and the response only contains the following entries in "source"
            | source     |
            | KINOMEscan |

    Scenario: Check Kinomescan small molecule to protein transformer
        Given the transformer
        when we fire "/activity/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "Kd nMol threshold",
                    "value": "5"
                },
                {
                    "name": "percent control threshold",
                    "value": "0"
                }
            ],
            "collection": [
                {
                    "id": "HMSL10037",
                    "biolink_class": "ChemicalSubstance",
                    "identifiers": {
                        "lincs": "LINCS.SMALLMOLECULE:LSM-1037"
                    },
                    "source": "MolePro",
                    "provided_by": "MolePro"
                }
            ]
        }
        """
        then the size of the response is 3
        and the response contains the following entries in "id"
            | id               |
            | UniProtKB:P36888 |
            | UniProtKB:P10721 |
            | UniProtKB:P07949 |
        and the response only contains the following entries in "id"
            | id               |
            | UniProtKB:P36888 |
            | UniProtKB:P10721 |
            | UniProtKB:P07949 |
        and the response contains the following entries in "source"
            | source     |
            | KINOMEscan |
        and the response only contains the following entries in "source"
            | source     |
            | KINOMEscan |
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | KINOMEscan activity transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | KINOMEscan activity transformer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source     |
            | KINOMEscan |
        and the response only contains the following entries in "source" of "names_synonyms" array
            | source     |
            | KINOMEscan |
        and the response contains the following entries in "source" of "connections" array
            | source     |
            | KINOMEscan |
        and the response only contains the following entries in "source" of "connections" array
            | source     |
            | KINOMEscan |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | HMSL10037         |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | HMSL10037         |
        and the response contains the following entries in "provided_by" of "connections" array
            | provided_by                     |
            | KINOMEscan activity transformer |
        and the response only contains the following entries in "provided_by" of "connections" array
            | provided_by                     |
            | KINOMEscan activity transformer |

    Scenario: Check Kinomescan small molecule to protein transformer - empty input list
        Given the transformer
        when we fire "/activity/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "Kd nMol threshold",
                    "value": "0"
                },
                {
                    "name": "percent control threshold",
                    "value": "0"
                }
            ],
            "collection": []
        }
        """
        then the size of the response is 0

    Scenario: Check Kinomescan protein to small molecule transformer transformer
        Given the transformer
        when we fire "/screening/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "Kd nMol threshold",
                    "value": "100"
                },
                {
                    "name": "percent control threshold",
                    "value": "0"
                }
            ],
            "collection": [
                {
                    "id": "UniProtKB:Q99759",
                    "biolink_class": "Protein",
                    "identifiers": {
                        "uniprot": "UniProtKB:Q99759"
                    },
                    "source": "MolePro",
                    "provided_by": "MolePro"
                }
            ]
        }
        """
        then the size of the response is 3
        and the response contains the following entries in "id"
            | id                            |
            | LINCS.SMALLMOLECULE:HMSL10189 |
            | LINCS.SMALLMOLECULE:HMSL10230 |
            | LINCS.SMALLMOLECULE:HMSL10151 |
        and the response only contains the following entries in "id"
            | id                            |
            | LINCS.SMALLMOLECULE:HMSL10189 |
            | LINCS.SMALLMOLECULE:HMSL10230 |
            | LINCS.SMALLMOLECULE:HMSL10151 |
        and the response contains the following entries in "source"
            | source     |
            | KINOMEscan |
        and the response only contains the following entries in "source"
            | source     |
            | KINOMEscan |
        and the response contains the following entries in "provided_by"
            | provided_by                      |
            | KINOMEscan screening transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                      |
            | KINOMEscan screening transformer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source     |
            | KINOMEscan |
        and the response only contains the following entries in "source" of "names_synonyms" array
            | source     |
            | KINOMEscan |
        and the response contains the following entries in "source" of "connections" array
            | source     |
            | KINOMEscan |
        and the response only contains the following entries in "source" of "connections" array
            | source     |
            | KINOMEscan |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | UniProtKB:Q99759  |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | UniProtKB:Q99759  |
        and the response contains the following entries in "provided_by" of "connections" array
            | provided_by                      |
            | KINOMEscan screening transformer |
        and the response only contains the following entries in "provided_by" of "connections" array
            | provided_by                      |
            | KINOMEscan screening transformer |

    Scenario: Check Kinomescan small molecule to protein transformer - empty input list
        Given the transformer
        when we fire "/activity/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "Kd nMol threshold",
                    "value": "0"
                },
                {
                    "name": "percent control threshold",
                    "value": "0"
                }
            ],
            "collection": []
        }
        """
        then the size of the response is 0

 Scenario: Check Kinomescan protein to small molecule transformer transformer
        Given the transformer
        when we fire "/screening/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "Kd nMol threshold",
                    "value": "0"
                },
                {
                    "name": "percent control threshold",
                    "value": "10"
                }
            ],
            "collection": [
                {
                    "id": "UniProtKB:P51617",
                    "biolink_class": "Protein",
                    "identifiers": {
                        "uniprot": "UniProtKB:Q99759"
                    },
                    "source": "MolePro",
                    "provided_by": "MolePro"
                }
            ]
        }
        """
        then the size of the response is 30
        and the response contains the following entries in "source"
            | source     |
            | KINOMEscan |
        and the response only contains the following entries in "source"
            | source     |
            | KINOMEscan |
        and the response contains the following entries in "provided_by"
            | provided_by                      |
            | KINOMEscan screening transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                      |
            | KINOMEscan screening transformer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source     |
            | KINOMEscan |
        and the response only contains the following entries in "source" of "names_synonyms" array
            | source     |
            | KINOMEscan |
        and the response contains the following entries in "source" of "connections" array
            | source     |
            | KINOMEscan |
        and the response only contains the following entries in "source" of "connections" array
            | source     |
            | KINOMEscan |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | UniProtKB:P51617  |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | UniProtKB:P51617  |
        and the response contains the following entries in "provided_by" of "connections" array
            | provided_by                      |
            | KINOMEscan screening transformer |
        and the response only contains the following entries in "provided_by" of "connections" array
            | provided_by                      |
            | KINOMEscan screening transformer |
    
