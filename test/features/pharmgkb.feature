Feature: Check PharmGKB transformer

    Background: Specify transformer API
        Given a transformer at "http://translator.broadinstitute.org/pharmgkb"


    Scenario: Check PharmGKB producer info
        Given the transformer
        when we fire "/chemicals/transformer_info" query
        then the value of "name" should be "PharmGKB compound-list producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "Jan-2023"
        and the size of "parameters" should be 1


    Scenario: Check PharmGKB relations transformer info
        Given the transformer
        when we fire "/relations/transformer_info" query
        then the value of "name" should be "PharmGKB relations transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "Jan-2023"
        and the size of "parameters" should be 1


    Scenario: Check PharmGKB text-mining transformer info
        Given the transformer
        when we fire "/text-mining/transformer_info" query
        then the value of "name" should be "PharmGKB automated annotations transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the value of "version" should be "2.5.0"
        and the value of "properties.source_version" should be "Jan-2023"
        and the size of "parameters" should be 0


    Scenario: Check PharmGKB compound-list producer
        Given the transformer
        when we fire "/chemicals/transform" query with the following body:
        """
        {
            "controls": [
                {
                  "name": "compound",
                  "value": "cisplatin"       
                } 
            ]
        }
        """
        then the size of the response is 1 
        and the response contains the following entries in "id"
            | id                         |
            | PHARMGKB.CHEMICAL:PA449014 |
        and the response only contains the following entries in "id"
            | id                         |
            | PHARMGKB.CHEMICAL:PA449014 |
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | PharmGKB compound-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | PharmGKB compound-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source           |
            | infores:pharmgkb |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name      |
            | cisplatin |
        and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by                     |
            | PharmGKB compound-list producer |
        and the response only contains the following entries in "provided_by" of "attributes" array
            | provided_by                     |
            | PharmGKB compound-list producer |
        and the response contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | PharmGKB         |
        and the response only contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | PharmGKB         |
        and the response contains the following entries in "inchi" of "identifiers"
            | inchi                                          |
            | InChI=1S/2ClH.2H3N.Pt/h2*1H;2*1H3;/q;;;;+4/p-2 |
        and the response only contains the following entries in "inchi" of "identifiers"
            | inchi                                          |
            | InChI=1S/2ClH.2H3N.Pt/h2*1H;2*1H3;/q;;;;+4/p-2 |



    Scenario: Check PharmGKB relations transformer on two compound inputs
        Given the transformer
        when we fire "/relations/transform" query with the following body:
        """
        {
           "controls": [],
           "collection": [
            {
              "biolink_class": "SmallMolecule",
              "id": "query:1",
              "identifiers": {
                  "inchi": "InChI=1S/C22H25ClN2OS/c23-17-7-8-22-20(16-17)18(19-4-1-2-6-21(19)27-22)5-3-9-24-10-12-25(13-11-24)14-15-26/h1-2,4-8,16,26H,3,9-15H2/b18-5-",
                  "pharmgkb": "PHARMGKB.CHEMICAL:PA448383",
                  "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O"
               },
              "provided_by": "PharmGKB compound-list producer",
              "source": "PharmGKB"
           },
           {
              "biolink_class": "SmallMolecule",
              "id": "query:1",
              "identifiers": {
                  "pharmgkb": "PHARMGKB.CHEMICAL:PA164712302"
              },
            "provided_by": "PharmGKB compound-list producer",
            "source": "PharmGKB"
           }
         ]}
      """
      then the size of the response is 4 
      and  the response contains the following entries in "id"
            | id            |
            | NCBIGene:3753 |
            | NCBIGene:9992 |
            | NCBIGene:3757 |
            | NCBIGene:9722 |



    Scenario: Check PharmGKB relations transformer on ID input
        Given the transformer
        when we fire "/relations/transform" query with the following body:
        """
        {
           "controls": [],
           "collection": [
             {
              "biolink_class": "SmallMolecule",
              "id": "CID 4046",
              "provided_by": "pharmgkb",
              "source": "pharmgkb",
              "identifiers": {
                 "pharmgkb": "PHARMGKB.CHEMICAL:PA450428"
             }        
             }
          ]
        }
        """
        then the response contains the following entries in "id"
            | id            |
            | NCBIGene:5243 |
            | NCBIGene:4363 |



    Scenario: Check PharmGKB text-mining transformer on two compound inputs
        Given the transformer
        when we fire "/text-mining/transform" query with the following body:
        """
        {
           "controls": [],
           "collection": [
            {
              "biolink_class": "SmallMolecule",
              "id": "query:1", 
              "identifiers": {
                  "inchi": "InChI=1S/C22H25ClN2OS/c23-17-7-8-22-20(16-17)18(19-4-1-2-6-21(19)27-22)5-3-9-24-10-12-25(13-11-24)14-15-26/h1-2,4-8,16,26H,3,9-15H2/b18-5-",
                  "pharmgkb": "PHARMGKB.CHEMICAL:PA448383",
                  "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O"
               },
              "provided_by": "PharmGKB compound-list producer",
              "source": "PharmGKB"
           },
           {
              "biolink_class": "SmallMolecule",
              "id": "query:1",
              "identifiers": {
                  "pharmgkb": "PHARMGKB.CHEMICAL:PA164712302"
              },
            "provided_by": "PharmGKB compound-list producer",
            "source": "PharmGKB"
           } 
         ]}
      """
      then the size of the response is 7 
      and  the response contains the following entries in "id"
            | id            |
            | NCBIGene:9722 |
            | NCBIGene:10295|
            | NCBIGene:8529 |
            | NCBIGene:2677 |
            | NCBIGene:9429 |
            | NCBIGene:10295|
            | NCBIGene:8529 |
            | NCBIGene:2677 |
            | NCBIGene:9429 |
            | NCBIGene:9722 |
            | NCBIGene:10295|
            | NCBIGene:8529 |
            | NCBIGene:2677 |
            | NCBIGene:9429 |
            | NCBIGene:9722 |
            | NCBIGene:10295|
            |NCBIGene:8529  |
