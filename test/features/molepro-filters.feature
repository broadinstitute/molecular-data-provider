Feature: Check MolePro filters

    Background: Specify Molecular Data Provider API
        Given a Molecular Data Provider at "https://translator.broadinstitute.org/molecular_data_provider"


    Scenario: Check MoleProDB node producer
        Given the Molecular Data Provider
        when we call "MoleProDB node producer" transformer with the following parameters:
        | name | value            |
        | id   | CID:2244         |
        | id   | DrugBank:DB00188 |
        | id   | CHEBI:4167       |
        then the length of the collection should be 3


    Scenario: Check integer less then filter
        Given the Molecular Data Provider
        when we call "MoleProDB node producer" transformer with the following parameters:
        | name | value            |
        | id   | CID:2244         |
        | id   | DrugBank:DB00188 |
        | id   | CHEBI:4167       |
        and we call "Element attribute filter" transformer with the following parameters:
        | id                   | name      | operator | value |
        | ROTATABLE_BOND_COUNT | ROTATABLE_BOND_COUNT | < | 5 |
        then the length of the collection should be 2


    Scenario: Check integer equals filter
        Given the Molecular Data Provider
        when we call "MoleProDB node producer" transformer with the following parameters:
        | name | value            |
        | id   | CID:2244         |
        | id   | DrugBank:DB00188 |
        | id   | CHEBI:4167       |
        and we call "Element attribute filter" transformer with the following parameters:
        | id                   | name      | operator | value |
        | ROTATABLE_BOND_COUNT | ROTATABLE_BOND_COUNT | == | 9 |
        then the length of the collection should be 1


    Scenario: Check integer not equals filter
        Given the Molecular Data Provider
        when we call "MoleProDB node producer" transformer with the following parameters:
        | name | value            |
        | id   | CID:2244         |
        | id   | DrugBank:DB00188 |
        | id   | CHEBI:4167       |
        and we call "Element attribute filter" transformer with the following parameters:
        | id                   | name      |   not | operator | value |
        | ROTATABLE_BOND_COUNT | ROTATABLE_BOND_COUNT | true | == | 9 |
        then the length of the collection should be 2


    Scenario: Check integer more then filter
        Given the Molecular Data Provider
        when we call "MoleProDB node producer" transformer with the following parameters:
        | name | value            |
        | id   | CID:2244         |
        | id   | DrugBank:DB00188 |
        | id   | CHEBI:4167       |
        and we call "Element attribute filter" transformer with the following parameters:
        | id                   | name      | operator | value |
        | ROTATABLE_BOND_COUNT | ROTATABLE_BOND_COUNT | > | 5 |
        then the length of the collection should be 1


    Scenario: Check float then filter
        Given the Molecular Data Provider
        when we call "MoleProDB node producer" transformer with the following parameters:
        | name | value            |
        | id   | CID:2244         |
        | id   | DrugBank:DB00188 |
        | id   | CHEBI:4167       |
        and we call "Element attribute filter" transformer with the following parameters:
        | id               | name       | operator | value |
        | MOLECULAR_WEIGHT | MOLECULAR_WEIGHT | < | 199.99 |
        then the length of the collection should be 2


    Scenario: Check float more then filter
        Given the Molecular Data Provider
        when we call "MoleProDB node producer" transformer with the following parameters:
        | name | value            |
        | id   | CID:2244         |
        | id   | DrugBank:DB00188 |
        | id   | CHEBI:4167       |
        and we call "Element attribute filter" transformer with the following parameters:
        | id               | name       | operator | value |
        | MOLECULAR_WEIGHT | MOLECULAR_WEIGHT | > | 199.99 |
        then the length of the collection should be 1


    Scenario: Check string equals filter
        Given the Molecular Data Provider
        when we call "MoleProDB node producer" transformer with the following parameters:
        | name | value            |
        | id   | CID:2244         |
        | id   | DrugBank:DB00188 |
        | id   | CHEBI:4167       |
        and we call "Element attribute filter" transformer with the following parameters:
        | id              | name    | operator | value |
        | biolink:routes_of_delivery | biolink:routes_of_delivery | == | oral |
        then the length of the collection should be 1


    Scenario: Check no connections filter
        Given the Molecular Data Provider
        when we call "MoleProDB node producer" transformer with the following parameters:
        | name | value            |
        | id   | CID:2244         |
        | id   | DrugBank:DB00188 |
        | id   | CHEBI:4167       |
        and we call "MoleProDB connections transformer" transformer with the following parameters:
        | biolink_class |
        | Gene          |
        then the length of the collection should be 312


    Scenario: Check connections filter
        Given the Molecular Data Provider
        when we call "MoleProDB node producer" transformer with the following parameters:
        | name | value            |
        | id   | CID:2244         |
        | id   | DrugBank:DB00188 |
        | id   | CHEBI:4167       |
        and we call "MoleProDB connections transformer" transformer with the following parameters:
        | biolink_class |
        | Gene          |
        and we call "Connection attribute filter" transformer with the following parameters:
        | id      | name    | operator | value |
        | action_type | biolink:relation |  ==  | INHIBITOR |
        then the length of the collection should be 56


    Scenario: Check negated connections filter
        Given the Molecular Data Provider
        when we call "MoleProDB node producer" transformer with the following parameters:
        | name | value            |
        | id   | CID:2244         |
        | id   | DrugBank:DB00188 |
        | id   | CHEBI:4167       |
        and we call "MoleProDB connections transformer" transformer with the following parameters:
        | biolink_class |
        | Gene          |
        and we call "Connection attribute filter" transformer with the following parameters:
        | name     | value                            |
        | id       | biolink:primary_knowledge_source |
        | name     | actions                          |
        | not      | true                             |
        | operator | ==                               |
        | value    | infores:drugbank                 |
        then the length of the collection should be 298

