Feature: Check BindingBD  transformer

    Background: Specify transformer API
        Given a transformer at "https://translator.broadinstitute.org/bindingdb"


    Scenario: Check ligands transformer info
        Given the transformer
        when we fire "/ligands/transformer_info" query
        then the value of "name" should be "BindingBD ligand producer"
        and the value of "label" should be "BindingBD"
        and the value of "version" should be "2.4.0"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "properties.source_version" should be "2022m8 (2022-09-01)"
        and the size of "parameters" should be 1


    Scenario: Check bindings transformer info
        Given the transformer
        when we fire "/bindings/transformer_info" query
        then the value of "name" should be "BindingBD binding transformer"
        and the value of "label" should be "BindingBD"
        and the value of "version" should be "2.4.1"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "target"
        and the value of "properties.source_version" should be "2022m8 (2022-09-01)"
        and the size of "parameters" should be 1


    Scenario: Check BindingBD ligands transformer
        Given the transformer
        when we fire "/ligands/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "ligand",
                    "value": "bindingdb:BDBM22360"
                },
                {
                    "name": "ligand",
                    "value": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                },
                {
                    "name": "ligand",
                    "value": "bortezomib"
                },
                {
                    "name": "ligand",
                    "value": "BINDINGDB:22360"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "id"
            | id                 |
            | BINDINGDB:22360    |
            | BINDINGDB:50069989 |
        and the response only contains the following entries in "id"
            | id                 |
            | BINDINGDB:22360    |
            | BINDINGDB:50069989 |
        and the response contains the following entries in "source"
            | source    |
            | BindingBD |
        and the response only contains the following entries in "source"
            | source    |
            | BindingBD |
        and the response contains the following entries in "provided_by"
            | provided_by                |
            | BindingBD ligand producer  |
        and the response only contains the following entries in "provided_by"
            | provided_by                |
            | BindingBD ligand producer  |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source    |
            | BindingBD |
        and the response only contains the following entries in "source" of "names_synonyms" array
            | source    |
            | BindingBD |


    Scenario: Check BindingBD bindings transformer
        Given the transformer
        when we fire "/bindings/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "BINDINGDB:40948",
                    "identifiers": {
                        "bindingdb": "BINDINGDB:40948"
                    },
                    "provided_by": "BindingBD ligand producer",
                    "source": "BindingBD"
                },
                {
                    "biolink_class": "SmallMolecule",
                    "id": "BINDINGDB:51963",
                    "identifiers": {
                        "bindingdb": "BINDINGDB:51963"
                    },
                    "provided_by": "BindingBD ligand producer",
                    "source": "BindingBD"
                }
            ]
        }
        """
        then the size of the response is 3
        and the response contains the following entries in "id"
            | id               |
            | UniProtKB:Q932Y6 |
            | UniProtKB:Q9Y4P1 |
            | UniProtKB:P04054 |
        and the response only contains the following entries in "id"
            | id               |
            | UniProtKB:Q932Y6 |
            | UniProtKB:Q9Y4P1 |
            | UniProtKB:P04054 |
        and the response contains the following entries in "source"
            | source    |
            | BindingBD |
        and the response only contains the following entries in "source"
            | source    |
            | BindingBD |
        and the response contains the following entries in "provided_by"
            | provided_by                   |
            | BindingBD binding transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                   |
            | BindingBD binding transformer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source            |
            | infores:uniprot   |
            | infores:bindingdb |
        and the response only contains the following entries in "source" of "names_synonyms" array
            | source            |
            | infores:uniprot   |
            | infores:bindingdb |


    Scenario: Check BindingBD bindings transformer with a threshold
        Given the transformer
        when we fire "/bindings/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "threshold_nm",
                    "value": "30000"
                }
            ],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "BINDINGDB:40948",
                    "identifiers": {
                        "bindingdb": "BINDINGDB:40948"
                    },
                    "provided_by": "BindingBD ligand producer",
                    "source": "BindingBD"
                },
                {
                    "biolink_class": "SmallMolecule",
                    "id": "BINDINGDB:51963",
                    "identifiers": {
                        "bindingdb": "BINDINGDB:51963"
                    },
                    "provided_by": "BindingBD ligand producer",
                    "source": "BindingBD"
                }
            ]
        }
        """
        then the size of the response is 5
        and the response contains the following entries in "id"
            | id               |
            | UniProtKB:Q05397 |
            | UniProtKB:Q14289 |
            | UniProtKB:Q932Y6 |
            | UniProtKB:Q9Y4P1 |
            | UniProtKB:P04054 |
        and the response only contains the following entries in "id"
            | id               |
            | UniProtKB:Q05397 |
            | UniProtKB:Q14289 |
            | UniProtKB:Q932Y6 |
            | UniProtKB:Q9Y4P1 |
            | UniProtKB:P04054 |
        and the response contains the following entries in "source"
            | source    |
            | BindingBD |
        and the response only contains the following entries in "source"
            | source    |
            | BindingBD |
        and the response contains the following entries in "provided_by"
            | provided_by                   |
            | BindingBD binding transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                   |
            | BindingBD binding transformer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source            |
            | infores:uniprot   |
            | infores:bindingdb |
        and the response only contains the following entries in "source" of "names_synonyms" array
            | source            |
            | infores:uniprot   |
            | infores:bindingdb |


    Scenario: Check BindingBD bindings transformer with no results
        Given the transformer
        when we fire "/bindings/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "BINDINGDB:23410",
                    "identifiers": {
                        "pubchem": "CID:5281691"
                    },
                    "provided_by": "BindingBD ligand producer",
                    "source": "BindingBD"
                }
            ]
        }
        """
        then the size of the response is 0
