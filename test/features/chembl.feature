Feature: Check ChEMBL transformer

    Background: Specify transformer API
        Given a transformer at "https://molepro-chembl-transformer.ci.transltr.io/chembl"

    Scenario: Check ChEMBL producer info
        Given the transformer
        when we fire "/molecules/transformer_info" query
        then the value of "name" should be "ChEMBL compound-list producer"
        and the value of "function" should be "producer"
        and the value of "knowledge_map.input_class" should be "none"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "30 (2022-03-09)"
        and the size of "parameters" should be 1


    Scenario: Check ChEMBL target transformer info
        Given the transformer
        when we fire "/targets/transformer_info" query
        then the value of "name" should be "ChEMBL gene target transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "gene"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "30 (2022-03-09)"
        and the size of "parameters" should be 0


    Scenario: Check ChEMBL metabolites transformer info
        Given the transformer
        when we fire "/metabolites/transformer_info" query
        then the value of "name" should be "ChEMBL metabolite transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "compound"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "30 (2022-03-09)"
        and the value of "knowledge_map.edges[0]['subject']" should be "SmallMolecule"
        and the size of "knowledge_map.nodes" should be 1
        and the size of "parameters" should be 0


    Scenario: Check ChEMBL indication transformer info
        Given the transformer
        when we fire "/indications/transformer_info" query
        then the value of "name" should be "ChEMBL indication transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "disease"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "30 (2022-03-09)"
        and the size of "parameters" should be 0

    Scenario: Check ChEMBL mechanism transformer info
        Given the transformer
        when we fire "/mechanisms/transformer_info" query
        then the value of "name" should be "ChEMBL mechanism transformer"
        and the value of "function" should be "transformer"
        and the value of "knowledge_map.input_class" should be "compound"
        and the value of "knowledge_map.output_class" should be "target"
        and the value of "version" should be "2.4.0"
        and the value of "properties.source_version" should be "30 (2022-03-09)"
        and the size of "parameters" should be 0

    Scenario: Check ChEMBL compound-list producer
        Given the transformer
        when we fire "/molecules/transform" query with the following body:
        """
        {
            "controls": [
                {
                    "name": "compound",
                    "value": "aspirin"
                },
                {
                    "name": "compound",
                    "value": "ChEMBL:CHEMBL4525786"
                }
            ]
        }
        """
        then the size of the response is 2 
        and the response contains the following entries in "id"
            | id                   |
            | ChEMBL:CHEMBL25      |
            | ChEMBL:CHEMBL4525786 |
        and the response only contains the following entries in "id"
            | id                   |
            | ChEMBL:CHEMBL25      |
            | ChEMBL:CHEMBL4525786 |
        and the response contains the following entries in "provided_by"
            | provided_by                          |
            | ChEMBL compound-list producer |
        and the response only contains the following entries in "provided_by"
            | provided_by                          |
            | ChEMBL compound-list producer |
        and the response contains the following entries in "source" of "names_synonyms" array
            | source |
            | ChEMBL |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                 |
            | Acetylsalicylic Acid |
        and the response contains the following entries in "provided_by" of "attributes" array
            | provided_by                   |
            | ChEMBL compound-list producer |
        and the response only contains the following entries in "provided_by" of "attributes" array
            | provided_by                   |
            | ChEMBL compound-list producer |
        and the response contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | ChEMBL |
        and the response only contains the following entries in "attribute_source" of "attributes" array
            | attribute_source |
            | ChEMBL |
        and the response contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
            | IZFCJBVYODRRRU-LLVKDONJSA-N |
        and the response only contains the following entries in "inchikey" of "identifiers"
            | inchikey                    |
            | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
            | IZFCJBVYODRRRU-LLVKDONJSA-N |


    Scenario: Check ChEMBL targets transformer on ID input
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "CID:2244",
                    "identifiers": {
                        "chembl": "ChEMBL:CHEMBL25"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                }
            ]
        }
        """
        then the size of the response is 2
        and the response contains the following entries in "id"
            | id                      |
            | ENSEMBL:ENSG00000073756 |
            | ENSEMBL:ENSG00000095303 |
        and the response only contains the following entries in "id"
            | id                      |
            | ENSEMBL:ENSG00000073756 |
            | ENSEMBL:ENSG00000095303 |
        and the response contains the following entries in "biolink_class"
            | biolink_class |
            | Gene          |
        and the response only contains the following entries in "biolink_class"
            | biolink_class |
            | Gene          |
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | ChEMBL gene target transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | ChEMBL gene target transformer |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name                         |
            | Prostaglandin G/H synthase 1 |
            | Prostaglandin G/H synthase 2 |

    Scenario: Check ChEMBL targets transformer on structure input
        Given the transformer
        when we fire "/targets/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "CID:2244",
                    "identifiers": {
                        "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                }
            ]
        }
        """
        then the size of the response is 2







    Scenario: Check ChEMBL mechanism transformer on ID input
        Given the transformer
        when we fire "/mechanisms/transform" query with the following body:
        """
        {
           "controls": [],
           "collection": [
             {
              "biolink_class": "ChemicalSubstance",
              "id": "CID:2244",
              "provided_by": "chembl",
              "source": "chembl",
              "identifiers": {
                "chembl": "ChEMBL:CHEMBL25"
              }
             }
           ]
        }
        """
        then the size of the response is 1
        and the response contains the following entries in "id"
            | id                          |
            | CHEMBL.TARGET:CHEMBL2094253 |
        and the response only contains the following entries in "id"
            | id                          |
            | CHEMBL.TARGET:CHEMBL2094253 | 
        and the response contains the following entries in "biolink_class"
            | biolink_class |
            | ProteinFamily |
        and the response only contains the following entries in "biolink_class"
            | biolink_class |
            | ProteinFamily |
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | ChEMBL mechanism transformer    |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | ChEMBL mechanism transformer    |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name           |
            | Cyclooxygenase |


    Scenario: Check ChEMBL mechanism transformer on structure input
        Given the transformer
        when we fire "/mechanisms/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "CID:2244",
                    "identifiers": {
                        "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                }
            ]
        }
        """
        then the size of the response is 1








    Scenario: Check ChEMBL activities transformer on ID input
        Given the transformer
        when we fire "/activities/transform" query with the following body:
        """
        {
           "controls": [],
           "collection": [
             {
              "biolink_class": "ChemicalSubstance",
              "id": "CID:2244",
              "provided_by": "chembl",
              "source": "chembl",
              "identifiers": {
                "chembl": "ChEMBL:CHEMBL25"
              }
             }
           ]
        }
        """
        then the size of the response is 302
        and the response contains the following entries in "id"
                 | id                           |
        	 | CHEMBL.TARGET:CHEMBL3253     |
        	 | CHEMBL.TARGET:CHEMBL376	|
        	 | CHEMBL.TARGET:CHEMBL230	|
        	 | CHEMBL.TARGET:CHEMBL2949	|
        	 | CHEMBL.TARGET:CHEMBL2094253	|
        	 | CHEMBL.TARGET:CHEMBL375	|
        	 | CHEMBL.TARGET:CHEMBL372	|
        	 | CHEMBL.TARGET:CHEMBL612884	|
        	 | CHEMBL.TARGET:CHEMBL374	|
        	 | CHEMBL.TARGET:CHEMBL2096674	|
        	 | CHEMBL.TARGET:CHEMBL369	|
        	 | CHEMBL.TARGET:CHEMBL2093869	|
        	 | CHEMBL.TARGET:CHEMBL613490	|
        	 | CHEMBL.TARGET:CHEMBL1835	|
        	 | CHEMBL.TARGET:CHEMBL614830	|
        	 | CHEMBL.TARGET:CHEMBL614207	|
        	 | CHEMBL.TARGET:CHEMBL4102	|
        	 | CHEMBL.TARGET:CHEMBL312	|
        	 | CHEMBL.TARGET:CHEMBL612558	|
        	 | CHEMBL.TARGET:CHEMBL5061	|
        	 | CHEMBL.TARGET:CHEMBL2111358	|
        	 | CHEMBL.TARGET:CHEMBL221	|
        	 | CHEMBL.TARGET:CHEMBL4681	|
        	 | CHEMBL.TARGET:CHEMBL360	|
        	 | CHEMBL.TARGET:CHEMBL384	|
        	 | CHEMBL.TARGET:CHEMBL613652	|
        	 | CHEMBL.TARGET:CHEMBL613427	|
        	 | CHEMBL.TARGET:CHEMBL613426	|
        	 | CHEMBL.TARGET:CHEMBL4296519	|
        	 | CHEMBL.TARGET:CHEMBL5653	|
        	 | CHEMBL.TARGET:CHEMBL5269	|
        	 | CHEMBL.TARGET:CHEMBL613416	|
        	 | CHEMBL.TARGET:CHEMBL613450	|
        	 | CHEMBL.TARGET:CHEMBL235	|
        	 | CHEMBL.TARGET:CHEMBL261	|
        	 | CHEMBL.TARGET:CHEMBL205	|
        	 | CHEMBL.TARGET:CHEMBL5696	|
        	 | CHEMBL.TARGET:CHEMBL2860	|
        	 | CHEMBL.TARGET:CHEMBL5685	|
        	 | CHEMBL.TARGET:CHEMBL5738	|
        	 | CHEMBL.TARGET:CHEMBL5016	|
        	 | CHEMBL.TARGET:CHEMBL3254	|
        	 | CHEMBL.TARGET:CHEMBL2756	|
        	 | CHEMBL.TARGET:CHEMBL1914	|
        	 | CHEMBL.TARGET:CHEMBL613561	|
        	 | CHEMBL.TARGET:CHEMBL613564	|
        	 | CHEMBL.TARGET:CHEMBL613617	|
        	 | CHEMBL.TARGET:CHEMBL614058	|
        	 | CHEMBL.TARGET:CHEMBL613712	|
        	 | CHEMBL.TARGET:CHEMBL2728	|
        	 | CHEMBL.TARGET:CHEMBL613860	|
        	 | CHEMBL.TARGET:CHEMBL368	|
        	 | CHEMBL.TARGET:CHEMBL612348	|
        	 | CHEMBL.TARGET:CHEMBL612851	|
        	 | CHEMBL.TARGET:CHEMBL612849	|
        	 | CHEMBL.TARGET:CHEMBL612888	|
        	 | CHEMBL.TARGET:CHEMBL613064	|
        	 | CHEMBL.TARGET:CHEMBL364	|
        	 | CHEMBL.TARGET:CHEMBL612880	|
        	 | CHEMBL.TARGET:CHEMBL612879	|
        	 | CHEMBL.TARGET:CHEMBL612848	|
        	 | CHEMBL.TARGET:CHEMBL367	|
        	 | CHEMBL.TARGET:CHEMBL612877	|
        	 | CHEMBL.TARGET:CHEMBL612853	|
        	 | CHEMBL.TARGET:CHEMBL612855	|
        	 | CHEMBL.TARGET:CHEMBL4159	|
        	 | CHEMBL.TARGET:CHEMBL1293226	|
        	 | CHEMBL.TARGET:CHEMBL614696	|
        	 | CHEMBL.TARGET:CHEMBL1963	|
        	 | CHEMBL.TARGET:CHEMBL1075138	|
        	 | CHEMBL.TARGET:CHEMBL3577	|
        	 | CHEMBL.TARGET:CHEMBL4372	|
        	 | CHEMBL.TARGET:CHEMBL1293237	|
        	 | CHEMBL.TARGET:CHEMBL1293255	|
        	 | CHEMBL.TARGET:CHEMBL276	|
        	 | CHEMBL.TARGET:CHEMBL1626541	|
        	 | CHEMBL.TARGET:CHEMBL1697861	|
        	 | CHEMBL.TARGET:CHEMBL2179	|
        	 | CHEMBL.TARGET:CHEMBL6032	|
        	 | CHEMBL.TARGET:CHEMBL1871	|
        	 | CHEMBL.TARGET:CHEMBL2034	|
        	 | CHEMBL.TARGET:CHEMBL6035	|
        	 | CHEMBL.TARGET:CHEMBL5391	|
        	 | CHEMBL.TARGET:CHEMBL5365	|
        	 | CHEMBL.TARGET:CHEMBL614818	|
        	 | CHEMBL.TARGET:CHEMBL1287617	|
        	 | CHEMBL.TARGET:CHEMBL1743316	|
        	 | CHEMBL.TARGET:CHEMBL1743319	|
        	 | CHEMBL.TARGET:CHEMBL220	|
        	 | CHEMBL.TARGET:CHEMBL226	|
        	 | CHEMBL.TARGET:CHEMBL251	|
        	 | CHEMBL.TARGET:CHEMBL256	|
        	 | CHEMBL.TARGET:CHEMBL319	|
        	 | CHEMBL.TARGET:CHEMBL315	|
        	 | CHEMBL.TARGET:CHEMBL223	|
        	 | CHEMBL.TARGET:CHEMBL1867	|
        	 | CHEMBL.TARGET:CHEMBL1942	|
        	 | CHEMBL.TARGET:CHEMBL1916	|
        	 | CHEMBL.TARGET:CHEMBL213	|
        	 | CHEMBL.TARGET:CHEMBL210	|
        	 | CHEMBL.TARGET:CHEMBL246	|
        	 | CHEMBL.TARGET:CHEMBL222	|
        	 | CHEMBL.TARGET:CHEMBL2622	|
        	 | CHEMBL.TARGET:CHEMBL4607	|
        	 | CHEMBL.TARGET:CHEMBL3157	|
        	 | CHEMBL.TARGET:CHEMBL1832	|
        	 | CHEMBL.TARGET:CHEMBL218	|
        	 | CHEMBL.TARGET:CHEMBL4015	|
        	 | CHEMBL.TARGET:CHEMBL2414	|
        	 | CHEMBL.TARGET:CHEMBL274	|
        	 | CHEMBL.TARGET:CHEMBL4029	|
        	 | CHEMBL.TARGET:CHEMBL2434	|
        	 | CHEMBL.TARGET:CHEMBL1901	|
        	 | CHEMBL.TARGET:CHEMBL3356	|
        	 | CHEMBL.TARGET:CHEMBL5282	|
        	 | CHEMBL.TARGET:CHEMBL3622	|
        	 | CHEMBL.TARGET:CHEMBL3397	|
        	 | CHEMBL.TARGET:CHEMBL289	|
        	 | CHEMBL.TARGET:CHEMBL5281	|
        	 | CHEMBL.TARGET:CHEMBL340	|
        	 | CHEMBL.TARGET:CHEMBL2056	|
        	 | CHEMBL.TARGET:CHEMBL217	|
        	 | CHEMBL.TARGET:CHEMBL234	|
        	 | CHEMBL.TARGET:CHEMBL219	|
        	 | CHEMBL.TARGET:CHEMBL238	|
        	 | CHEMBL.TARGET:CHEMBL252	|
        	 | CHEMBL.TARGET:CHEMBL206	|
        	 | CHEMBL.TARGET:CHEMBL242	|
        	 | CHEMBL.TARGET:CHEMBL3392921	|
        	 | CHEMBL.TARGET:CHEMBL231	|
        	 | CHEMBL.TARGET:CHEMBL1941	|
        	 | CHEMBL.TARGET:CHEMBL402	|
        	 | CHEMBL.TARGET:CHEMBL5486	|
        	 | CHEMBL.TARGET:CHEMBL1909043	|
        	 | CHEMBL.TARGET:CHEMBL1798	|
        	 | CHEMBL.TARGET:CHEMBL4358	|
        	 | CHEMBL.TARGET:CHEMBL4644	|
        	 | CHEMBL.TARGET:CHEMBL259	|
        	 | CHEMBL.TARGET:CHEMBL4608	|
        	 | CHEMBL.TARGET:CHEMBL1951	|
        	 | CHEMBL.TARGET:CHEMBL216	|
        	 | CHEMBL.TARGET:CHEMBL211	|
        	 | CHEMBL.TARGET:CHEMBL245	|
        	 | CHEMBL.TARGET:CHEMBL1821	|
        	 | CHEMBL.TARGET:CHEMBL2035	|
        	 | CHEMBL.TARGET:CHEMBL4777	|
        	 | CHEMBL.TARGET:CHEMBL4018	|
        	 | CHEMBL.TARGET:CHEMBL3048	|
        	 | CHEMBL.TARGET:CHEMBL3464	|
        	 | CHEMBL.TARGET:CHEMBL236	|
        	 | CHEMBL.TARGET:CHEMBL237	|
        	 | CHEMBL.TARGET:CHEMBL233	|
        	 | CHEMBL.TARGET:CHEMBL1827	|
        	 | CHEMBL.TARGET:CHEMBL250	|
        	 | CHEMBL.TARGET:CHEMBL240	|
        	 | CHEMBL.TARGET:CHEMBL1909044	|
        	 | CHEMBL.TARGET:CHEMBL4074	|
        	 | CHEMBL.TARGET:CHEMBL4801	|
        	 | CHEMBL.TARGET:CHEMBL4071	|
        	 | CHEMBL.TARGET:CHEMBL248	|
        	 | CHEMBL.TARGET:CHEMBL332	|
        	 | CHEMBL.TARGET:CHEMBL321	|
        	 | CHEMBL.TARGET:CHEMBL299	|
        	 | CHEMBL.TARGET:CHEMBL3385	|
        	 | CHEMBL.TARGET:CHEMBL4040	|
        	 | CHEMBL.TARGET:CHEMBL260	|
        	 | CHEMBL.TARGET:CHEMBL4445	|
        	 | CHEMBL.TARGET:CHEMBL203	|
        	 | CHEMBL.TARGET:CHEMBL1841	|
        	 | CHEMBL.TARGET:CHEMBL1824	|
        	 | CHEMBL.TARGET:CHEMBL258	|
        	 | CHEMBL.TARGET:CHEMBL3243	|
        	 | CHEMBL.TARGET:CHEMBL273	|
        	 | CHEMBL.TARGET:CHEMBL3459	|
        	 | CHEMBL.TARGET:CHEMBL224	|
        	 | CHEMBL.TARGET:CHEMBL1833	|
        	 | CHEMBL.TARGET:CHEMBL225	|
        	 | CHEMBL.TARGET:CHEMBL5017	|
        	 | CHEMBL.TARGET:CHEMBL3371	|
        	 | CHEMBL.TARGET:CHEMBL228	|
        	 | CHEMBL.TARGET:CHEMBL287	|
        	 | CHEMBL.TARGET:CHEMBL249	|
        	 | CHEMBL.TARGET:CHEMBL2327	|
        	 | CHEMBL.TARGET:CHEMBL3072	|
        	 | CHEMBL.TARGET:CHEMBL1868	|
        	 | CHEMBL.TARGET:CHEMBL5144	|
        	 | CHEMBL.TARGET:CHEMBL1889	|
        	 | CHEMBL.TARGET:CHEMBL613107	|
        	 | CHEMBL.TARGET:CHEMBL614054	|
        	 | CHEMBL.TARGET:CHEMBL614078	|
        	 | CHEMBL.TARGET:CHEMBL614519	|
        	 | CHEMBL.TARGET:CHEMBL614997	|
        	 | CHEMBL.TARGET:CHEMBL614388	|
        	 | CHEMBL.TARGET:CHEMBL383	|
        	 | CHEMBL.TARGET:CHEMBL613508	|
        	 | CHEMBL.TARGET:CHEMBL614860	|
        	 | CHEMBL.TARGET:CHEMBL614922	|
        	 | CHEMBL.TARGET:CHEMBL614021	|
        	 | CHEMBL.TARGET:CHEMBL385	|
        	 | CHEMBL.TARGET:CHEMBL614213	|
        	 | CHEMBL.TARGET:CHEMBL614177	|
        	 | CHEMBL.TARGET:CHEMBL613829	|
        	 | CHEMBL.TARGET:CHEMBL614643	|
        	 | CHEMBL.TARGET:CHEMBL615022	|
        	 | CHEMBL.TARGET:CHEMBL614214	|
        	 | CHEMBL.TARGET:CHEMBL612555	|
        	 | CHEMBL.TARGET:CHEMBL614164	|
        	 | CHEMBL.TARGET:CHEMBL614300	|
        	 | CHEMBL.TARGET:CHEMBL614056	|
        	 | CHEMBL.TARGET:CHEMBL612262	|
        	 | CHEMBL.TARGET:CHEMBL614387	|
        	 | CHEMBL.TARGET:CHEMBL614709	|
        	 | CHEMBL.TARGET:CHEMBL614317	|
        	 | CHEMBL.TARGET:CHEMBL614882	|
        	 | CHEMBL.TARGET:CHEMBL614051	|
        	 | CHEMBL.TARGET:CHEMBL614096	|
        	 | CHEMBL.TARGET:CHEMBL614072	|
        	 | CHEMBL.TARGET:CHEMBL614917	|
        	 | CHEMBL.TARGET:CHEMBL392	|
        	 | CHEMBL.TARGET:CHEMBL614451	|
        	 | CHEMBL.TARGET:CHEMBL612263	|
        	 | CHEMBL.TARGET:CHEMBL394	|
        	 | CHEMBL.TARGET:CHEMBL613977	|
        	 | CHEMBL.TARGET:CHEMBL614487	|
        	 | CHEMBL.TARGET:CHEMBL390	|
        	 | CHEMBL.TARGET:CHEMBL387	|
        	 | CHEMBL.TARGET:CHEMBL614925	|
        	 | CHEMBL.TARGET:CHEMBL614361	|
        	 | CHEMBL.TARGET:CHEMBL614610	|
        	 | CHEMBL.TARGET:CHEMBL614697	|
        	 | CHEMBL.TARGET:CHEMBL614067	|
        	 | CHEMBL.TARGET:CHEMBL614908	|
        	 | CHEMBL.TARGET:CHEMBL613102	|
        	 | CHEMBL.TARGET:CHEMBL612796	|
        	 | CHEMBL.TARGET:CHEMBL382	|
        	 | CHEMBL.TARGET:CHEMBL614740	|
        	 | CHEMBL.TARGET:CHEMBL614919	|
        	 | CHEMBL.TARGET:CHEMBL614886	|
        	 | CHEMBL.TARGET:CHEMBL614561	|
        	 | CHEMBL.TARGET:CHEMBL613834	|
        	 | CHEMBL.TARGET:CHEMBL614391	|
        	 | CHEMBL.TARGET:CHEMBL614139	|
        	 | CHEMBL.TARGET:CHEMBL612544	|
        	 | CHEMBL.TARGET:CHEMBL400	|
        	 | CHEMBL.TARGET:CHEMBL614725	|
        	 | CHEMBL.TARGET:CHEMBL614530	|
        	 | CHEMBL.TARGET:CHEMBL612518	|
        	 | CHEMBL.TARGET:CHEMBL397	|
        	 | CHEMBL.TARGET:CHEMBL613373	|
        	 | CHEMBL.TARGET:CHEMBL1777665	|
        	 | CHEMBL.TARGET:CHEMBL2073671	|
        	 | CHEMBL.TARGET:CHEMBL4302	|
        	 | CHEMBL.TARGET:CHEMBL1641347	|
        	 | CHEMBL.TARGET:CHEMBL2157	|
        	 | CHEMBL.TARGET:CHEMBL1741186	|
        	 | CHEMBL.TARGET:CHEMBL2146316	|
        	 | CHEMBL.TARGET:CHEMBL395	|
        	 | CHEMBL.TARGET:CHEMBL2007625	|
        	 | CHEMBL.TARGET:CHEMBL1743121	|
        	 | CHEMBL.TARGET:CHEMBL5619	|
        	 | CHEMBL.TARGET:CHEMBL613979	|
        	 | CHEMBL.TARGET:CHEMBL5658	|
        	 | CHEMBL.TARGET:CHEMBL613424	|
        	 | CHEMBL.TARGET:CHEMBL373	|
        	 | CHEMBL.TARGET:CHEMBL4794	|
        	 | CHEMBL.TARGET:CHEMBL3396942	|
        	 | CHEMBL.TARGET:CHEMBL612556	|
        	 | CHEMBL.TARGET:CHEMBL366	|
        	 | CHEMBL.TARGET:CHEMBL612647	|
        	 | CHEMBL.TARGET:CHEMBL612843	|
        	 | CHEMBL.TARGET:CHEMBL612446	|
        	 | CHEMBL.TARGET:CHEMBL612546	|
        	 | CHEMBL.TARGET:CHEMBL3308912	|
        	 | CHEMBL.TARGET:CHEMBL6020	|
        	 | CHEMBL.TARGET:CHEMBL4523138	|
        	 | CHEMBL.TARGET:CHEMBL5748	|
        	 | CHEMBL.TARGET:CHEMBL5918	|
        	 | CHEMBL.TARGET:CHEMBL1743128	|
        	 | CHEMBL.TARGET:CHEMBL614279	|
        	 | CHEMBL.TARGET:CHEMBL4296457	|
        	 | CHEMBL.TARGET:CHEMBL4483230	|
        	 | CHEMBL.TARGET:CHEMBL2001	|
        	 | CHEMBL.TARGET:CHEMBL4296518	|
        	 | CHEMBL.TARGET:CHEMBL612255	|
        	 | CHEMBL.TARGET:CHEMBL612557	|
        	 | CHEMBL.TARGET:CHEMBL613510	|
        	 | CHEMBL.TARGET:CHEMBL614285	|
        	 | CHEMBL.TARGET:CHEMBL4303835	|
        	 | CHEMBL.TARGET:CHEMBL2439	|
        	 | CHEMBL.TARGET:CHEMBL614247	|
        	 | CHEMBL.TARGET:CHEMBL614392	|
        	 | CHEMBL.TARGET:CHEMBL4523510	|
        	 | CHEMBL.TARGET:CHEMBL614049	|
        	 | CHEMBL.TARGET:CHEMBL4523354	|
        	 | CHEMBL.TARGET:CHEMBL4483221	|
        	 | CHEMBL.TARGET:CHEMBL4296391	|
        	 | CHEMBL.TARGET:CHEMBL4523582	|
        	 | CHEMBL.TARGET:CHEMBL613963	|
        	 | CHEMBL.TARGET:CHEMBL391	|
        	 | CHEMBL.TARGET:CHEMBL2487	|
        	 | CHEMBL.TARGET:CHEMBL613847	|
        	 | CHEMBL.TARGET:CHEMBL614875	|



        and the response only contains the following entries in "id"
            | id                          |
        	 | CHEMBL.TARGET:CHEMBL3253     |
        	 | CHEMBL.TARGET:CHEMBL376	|
        	 | CHEMBL.TARGET:CHEMBL230	|
        	 | CHEMBL.TARGET:CHEMBL2949	|
        	 | CHEMBL.TARGET:CHEMBL2094253	|
        	 | CHEMBL.TARGET:CHEMBL375	|
        	 | CHEMBL.TARGET:CHEMBL372	|
        	 | CHEMBL.TARGET:CHEMBL612884	|
        	 | CHEMBL.TARGET:CHEMBL374	|
        	 | CHEMBL.TARGET:CHEMBL2362975	|
        	 | CHEMBL.TARGET:CHEMBL2096674	|
        	 | CHEMBL.TARGET:CHEMBL369	|
        	 | CHEMBL.TARGET:CHEMBL2093869	|
        	 | CHEMBL.TARGET:CHEMBL613490	|
        	 | CHEMBL.TARGET:CHEMBL1835	|
        	 | CHEMBL.TARGET:CHEMBL614830	|
        	 | CHEMBL.TARGET:CHEMBL614207	|
        	 | CHEMBL.TARGET:CHEMBL4102	|
        	 | CHEMBL.TARGET:CHEMBL312	|
        	 | CHEMBL.TARGET:CHEMBL3879801	|
        	 | CHEMBL.TARGET:CHEMBL612558	|
        	 | CHEMBL.TARGET:CHEMBL5061	|
        	 | CHEMBL.TARGET:CHEMBL2111358	|
        	 | CHEMBL.TARGET:CHEMBL221	|
        	 | CHEMBL.TARGET:CHEMBL4681	|
        	 | CHEMBL.TARGET:CHEMBL360	|
        	 | CHEMBL.TARGET:CHEMBL384	|
        	 | CHEMBL.TARGET:CHEMBL613652	|
        	 | CHEMBL.TARGET:CHEMBL613427	|
        	 | CHEMBL.TARGET:CHEMBL613426	|
        	 | CHEMBL.TARGET:CHEMBL4296519	|
        	 | CHEMBL.TARGET:CHEMBL5653	|
        	 | CHEMBL.TARGET:CHEMBL5269	|
        	 | CHEMBL.TARGET:CHEMBL613416	|
        	 | CHEMBL.TARGET:CHEMBL613450	|
        	 | CHEMBL.TARGET:CHEMBL235	|
        	 | CHEMBL.TARGET:CHEMBL261	|
        	 | CHEMBL.TARGET:CHEMBL205	|
        	 | CHEMBL.TARGET:CHEMBL5696	|
        	 | CHEMBL.TARGET:CHEMBL2860	|
        	 | CHEMBL.TARGET:CHEMBL5685	|
        	 | CHEMBL.TARGET:CHEMBL5738	|
        	 | CHEMBL.TARGET:CHEMBL5016	|
        	 | CHEMBL.TARGET:CHEMBL3254	|
        	 | CHEMBL.TARGET:CHEMBL2756	|
        	 | CHEMBL.TARGET:CHEMBL1914	|
        	 | CHEMBL.TARGET:CHEMBL613561	|
        	 | CHEMBL.TARGET:CHEMBL613564	|
        	 | CHEMBL.TARGET:CHEMBL613617	|
        	 | CHEMBL.TARGET:CHEMBL614058	|
        	 | CHEMBL.TARGET:CHEMBL613712	|
        	 | CHEMBL.TARGET:CHEMBL2728	|
        	 | CHEMBL.TARGET:CHEMBL613860	|
        	 | CHEMBL.TARGET:CHEMBL368	|
        	 | CHEMBL.TARGET:CHEMBL612348	|
        	 | CHEMBL.TARGET:CHEMBL612851	|
        	 | CHEMBL.TARGET:CHEMBL612849	|
        	 | CHEMBL.TARGET:CHEMBL612888	|
        	 | CHEMBL.TARGET:CHEMBL613064	|
        	 | CHEMBL.TARGET:CHEMBL364	|
        	 | CHEMBL.TARGET:CHEMBL612880	|
        	 | CHEMBL.TARGET:CHEMBL612879	|
        	 | CHEMBL.TARGET:CHEMBL612848	|
        	 | CHEMBL.TARGET:CHEMBL367	|
        	 | CHEMBL.TARGET:CHEMBL612877	|
        	 | CHEMBL.TARGET:CHEMBL612853	|
        	 | CHEMBL.TARGET:CHEMBL612855	|
        	 | CHEMBL.TARGET:CHEMBL4159	|
        	 | CHEMBL.TARGET:CHEMBL1293226	|
        	 | CHEMBL.TARGET:CHEMBL614696	|
        	 | CHEMBL.TARGET:CHEMBL1963	|
        	 | CHEMBL.TARGET:CHEMBL1075138	|
        	 | CHEMBL.TARGET:CHEMBL3577	|
        	 | CHEMBL.TARGET:CHEMBL4372	|
        	 | CHEMBL.TARGET:CHEMBL1293237	|
        	 | CHEMBL.TARGET:CHEMBL1293255	|
        	 | CHEMBL.TARGET:CHEMBL276	|
        	 | CHEMBL.TARGET:CHEMBL1626541	|
        	 | CHEMBL.TARGET:CHEMBL1697861	|
        	 | CHEMBL.TARGET:CHEMBL2179	|
        	 | CHEMBL.TARGET:CHEMBL6032	|
        	 | CHEMBL.TARGET:CHEMBL1871	|
        	 | CHEMBL.TARGET:CHEMBL2034	|
        	 | CHEMBL.TARGET:CHEMBL6035	|
        	 | CHEMBL.TARGET:CHEMBL5391	|
        	 | CHEMBL.TARGET:CHEMBL5365	|
        	 | CHEMBL.TARGET:CHEMBL614818	|
        	 | CHEMBL.TARGET:CHEMBL1287617	|
        	 | CHEMBL.TARGET:CHEMBL1743316	|
        	 | CHEMBL.TARGET:CHEMBL1743319	|
        	 | CHEMBL.TARGET:CHEMBL220	|
        	 | CHEMBL.TARGET:CHEMBL226	|
        	 | CHEMBL.TARGET:CHEMBL251	|
        	 | CHEMBL.TARGET:CHEMBL256	|
        	 | CHEMBL.TARGET:CHEMBL319	|
        	 | CHEMBL.TARGET:CHEMBL315	|
        	 | CHEMBL.TARGET:CHEMBL223	|
        	 | CHEMBL.TARGET:CHEMBL1867	|
        	 | CHEMBL.TARGET:CHEMBL1942	|
        	 | CHEMBL.TARGET:CHEMBL1916	|
        	 | CHEMBL.TARGET:CHEMBL213	|
        	 | CHEMBL.TARGET:CHEMBL210	|
        	 | CHEMBL.TARGET:CHEMBL246	|
        	 | CHEMBL.TARGET:CHEMBL222	|
        	 | CHEMBL.TARGET:CHEMBL2622	|
        	 | CHEMBL.TARGET:CHEMBL4607	|
        	 | CHEMBL.TARGET:CHEMBL3157	|
        	 | CHEMBL.TARGET:CHEMBL1832	|
        	 | CHEMBL.TARGET:CHEMBL218	|
        	 | CHEMBL.TARGET:CHEMBL4015	|
        	 | CHEMBL.TARGET:CHEMBL2414	|
        	 | CHEMBL.TARGET:CHEMBL274	|
        	 | CHEMBL.TARGET:CHEMBL4029	|
        	 | CHEMBL.TARGET:CHEMBL2434	|
        	 | CHEMBL.TARGET:CHEMBL1901	|
        	 | CHEMBL.TARGET:CHEMBL3356	|
        	 | CHEMBL.TARGET:CHEMBL5282	|
        	 | CHEMBL.TARGET:CHEMBL3622	|
        	 | CHEMBL.TARGET:CHEMBL3397	|
        	 | CHEMBL.TARGET:CHEMBL289	|
        	 | CHEMBL.TARGET:CHEMBL5281	|
        	 | CHEMBL.TARGET:CHEMBL340	|
        	 | CHEMBL.TARGET:CHEMBL2056	|
        	 | CHEMBL.TARGET:CHEMBL217	|
        	 | CHEMBL.TARGET:CHEMBL234	|
        	 | CHEMBL.TARGET:CHEMBL219	|
        	 | CHEMBL.TARGET:CHEMBL238	|
        	 | CHEMBL.TARGET:CHEMBL252	|
        	 | CHEMBL.TARGET:CHEMBL206	|
        	 | CHEMBL.TARGET:CHEMBL242	|
        	 | CHEMBL.TARGET:CHEMBL3392921	|
        	 | CHEMBL.TARGET:CHEMBL231	|
        	 | CHEMBL.TARGET:CHEMBL1941	|
        	 | CHEMBL.TARGET:CHEMBL402	|
        	 | CHEMBL.TARGET:CHEMBL5486	|
        	 | CHEMBL.TARGET:CHEMBL1909043	|
        	 | CHEMBL.TARGET:CHEMBL1798	|
        	 | CHEMBL.TARGET:CHEMBL4358	|
        	 | CHEMBL.TARGET:CHEMBL4644	|
        	 | CHEMBL.TARGET:CHEMBL259	|
        	 | CHEMBL.TARGET:CHEMBL4608	|
        	 | CHEMBL.TARGET:CHEMBL1951	|
        	 | CHEMBL.TARGET:CHEMBL216	|
        	 | CHEMBL.TARGET:CHEMBL211	|
        	 | CHEMBL.TARGET:CHEMBL245	|
        	 | CHEMBL.TARGET:CHEMBL1821	|
        	 | CHEMBL.TARGET:CHEMBL2035	|
        	 | CHEMBL.TARGET:CHEMBL4777	|
        	 | CHEMBL.TARGET:CHEMBL4018	|
        	 | CHEMBL.TARGET:CHEMBL3048	|
        	 | CHEMBL.TARGET:CHEMBL3464	|
        	 | CHEMBL.TARGET:CHEMBL236	|
        	 | CHEMBL.TARGET:CHEMBL237	|
        	 | CHEMBL.TARGET:CHEMBL233	|
        	 | CHEMBL.TARGET:CHEMBL1827	|
        	 | CHEMBL.TARGET:CHEMBL250	|
        	 | CHEMBL.TARGET:CHEMBL240	|
        	 | CHEMBL.TARGET:CHEMBL1909044	|
        	 | CHEMBL.TARGET:CHEMBL4074	|
        	 | CHEMBL.TARGET:CHEMBL4801	|
        	 | CHEMBL.TARGET:CHEMBL4071	|
        	 | CHEMBL.TARGET:CHEMBL248	|
        	 | CHEMBL.TARGET:CHEMBL332	|
        	 | CHEMBL.TARGET:CHEMBL321	|
        	 | CHEMBL.TARGET:CHEMBL299	|
        	 | CHEMBL.TARGET:CHEMBL3385	|
        	 | CHEMBL.TARGET:CHEMBL4040	|
        	 | CHEMBL.TARGET:CHEMBL260	|
        	 | CHEMBL.TARGET:CHEMBL4445	|
        	 | CHEMBL.TARGET:CHEMBL203	|
        	 | CHEMBL.TARGET:CHEMBL1841	|
        	 | CHEMBL.TARGET:CHEMBL1824	|
        	 | CHEMBL.TARGET:CHEMBL258	|
        	 | CHEMBL.TARGET:CHEMBL3243	|
        	 | CHEMBL.TARGET:CHEMBL273	|
        	 | CHEMBL.TARGET:CHEMBL3459	|
        	 | CHEMBL.TARGET:CHEMBL224	|
        	 | CHEMBL.TARGET:CHEMBL1833	|
        	 | CHEMBL.TARGET:CHEMBL225	|
        	 | CHEMBL.TARGET:CHEMBL5017	|
        	 | CHEMBL.TARGET:CHEMBL3371	|
        	 | CHEMBL.TARGET:CHEMBL228	|
        	 | CHEMBL.TARGET:CHEMBL287	|
        	 | CHEMBL.TARGET:CHEMBL249	|
        	 | CHEMBL.TARGET:CHEMBL2327	|
        	 | CHEMBL.TARGET:CHEMBL3072	|
        	 | CHEMBL.TARGET:CHEMBL1868	|
        	 | CHEMBL.TARGET:CHEMBL5144	|
        	 | CHEMBL.TARGET:CHEMBL1889	|
        	 | CHEMBL.TARGET:CHEMBL613107	|
        	 | CHEMBL.TARGET:CHEMBL614054	|
        	 | CHEMBL.TARGET:CHEMBL614078	|
        	 | CHEMBL.TARGET:CHEMBL614519	|
        	 | CHEMBL.TARGET:CHEMBL614997	|
        	 | CHEMBL.TARGET:CHEMBL614388	|
        	 | CHEMBL.TARGET:CHEMBL383	|
        	 | CHEMBL.TARGET:CHEMBL613508	|
        	 | CHEMBL.TARGET:CHEMBL614860	|
        	 | CHEMBL.TARGET:CHEMBL614922	|
        	 | CHEMBL.TARGET:CHEMBL614021	|
        	 | CHEMBL.TARGET:CHEMBL385	|
        	 | CHEMBL.TARGET:CHEMBL614213	|
        	 | CHEMBL.TARGET:CHEMBL614177	|
        	 | CHEMBL.TARGET:CHEMBL613829	|
        	 | CHEMBL.TARGET:CHEMBL614643	|
        	 | CHEMBL.TARGET:CHEMBL615022	|
        	 | CHEMBL.TARGET:CHEMBL614214	|
        	 | CHEMBL.TARGET:CHEMBL612555	|
        	 | CHEMBL.TARGET:CHEMBL614164	|
        	 | CHEMBL.TARGET:CHEMBL614300	|
        	 | CHEMBL.TARGET:CHEMBL614056	|
        	 | CHEMBL.TARGET:CHEMBL612262	|
        	 | CHEMBL.TARGET:CHEMBL614387	|
        	 | CHEMBL.TARGET:CHEMBL614709	|
        	 | CHEMBL.TARGET:CHEMBL614317	|
        	 | CHEMBL.TARGET:CHEMBL614882	|
        	 | CHEMBL.TARGET:CHEMBL614051	|
        	 | CHEMBL.TARGET:CHEMBL614096	|
        	 | CHEMBL.TARGET:CHEMBL614072	|
        	 | CHEMBL.TARGET:CHEMBL614917	|
        	 | CHEMBL.TARGET:CHEMBL392	|
        	 | CHEMBL.TARGET:CHEMBL614451	|
        	 | CHEMBL.TARGET:CHEMBL612263	|
        	 | CHEMBL.TARGET:CHEMBL394	|
        	 | CHEMBL.TARGET:CHEMBL613977	|
        	 | CHEMBL.TARGET:CHEMBL614487	|
        	 | CHEMBL.TARGET:CHEMBL390	|
        	 | CHEMBL.TARGET:CHEMBL387	|
        	 | CHEMBL.TARGET:CHEMBL614925	|
        	 | CHEMBL.TARGET:CHEMBL614361	|
        	 | CHEMBL.TARGET:CHEMBL614610	|
        	 | CHEMBL.TARGET:CHEMBL614697	|
        	 | CHEMBL.TARGET:CHEMBL614067	|
        	 | CHEMBL.TARGET:CHEMBL614908	|
        	 | CHEMBL.TARGET:CHEMBL613102	|
        	 | CHEMBL.TARGET:CHEMBL612796	|
        	 | CHEMBL.TARGET:CHEMBL382	|
        	 | CHEMBL.TARGET:CHEMBL614740	|
        	 | CHEMBL.TARGET:CHEMBL614919	|
        	 | CHEMBL.TARGET:CHEMBL614886	|
        	 | CHEMBL.TARGET:CHEMBL614561	|
        	 | CHEMBL.TARGET:CHEMBL613834	|
        	 | CHEMBL.TARGET:CHEMBL614391	|
        	 | CHEMBL.TARGET:CHEMBL614139	|
        	 | CHEMBL.TARGET:CHEMBL612544	|
        	 | CHEMBL.TARGET:CHEMBL400	|
        	 | CHEMBL.TARGET:CHEMBL614725	|
        	 | CHEMBL.TARGET:CHEMBL614530	|
        	 | CHEMBL.TARGET:CHEMBL612518	|
        	 | CHEMBL.TARGET:CHEMBL397	|
        	 | CHEMBL.TARGET:CHEMBL613373	|
        	 | CHEMBL.TARGET:CHEMBL1777665	|
        	 | CHEMBL.TARGET:CHEMBL2073671	|
        	 | CHEMBL.TARGET:CHEMBL4302	|
        	 | CHEMBL.TARGET:CHEMBL1641347	|
        	 | CHEMBL.TARGET:CHEMBL2157	|
        	 | CHEMBL.TARGET:CHEMBL1741186	|
        	 | CHEMBL.TARGET:CHEMBL2146316	|
        	 | CHEMBL.TARGET:CHEMBL395	|
        	 | CHEMBL.TARGET:CHEMBL2007625	|
        	 | CHEMBL.TARGET:CHEMBL1743121	|
        	 | CHEMBL.TARGET:CHEMBL5619	|
        	 | CHEMBL.TARGET:CHEMBL613979	|
        	 | CHEMBL.TARGET:CHEMBL5658	|
        	 | CHEMBL.TARGET:CHEMBL613424	|
        	 | CHEMBL.TARGET:CHEMBL373	|
        	 | CHEMBL.TARGET:CHEMBL4794	|
        	 | CHEMBL.TARGET:CHEMBL3396942	|
        	 | CHEMBL.TARGET:CHEMBL612556	|
        	 | CHEMBL.TARGET:CHEMBL366	|
        	 | CHEMBL.TARGET:CHEMBL612647	|
        	 | CHEMBL.TARGET:CHEMBL612843	|
        	 | CHEMBL.TARGET:CHEMBL612446	|
        	 | CHEMBL.TARGET:CHEMBL612546	|
        	 | CHEMBL.TARGET:CHEMBL3308912	|
        	 | CHEMBL.TARGET:CHEMBL6020	|
        	 | CHEMBL.TARGET:CHEMBL4523138	|
        	 | CHEMBL.TARGET:CHEMBL5748	|
        	 | CHEMBL.TARGET:CHEMBL5918	|
        	 | CHEMBL.TARGET:CHEMBL1743128	|
        	 | CHEMBL.TARGET:CHEMBL614279	|
        	 | CHEMBL.TARGET:CHEMBL4296457	|
        	 | CHEMBL.TARGET:CHEMBL4483230	|
        	 | CHEMBL.TARGET:CHEMBL2001	|
        	 | CHEMBL.TARGET:CHEMBL4296518	|
        	 | CHEMBL.TARGET:CHEMBL612255	|
        	 | CHEMBL.TARGET:CHEMBL612557	|
        	 | CHEMBL.TARGET:CHEMBL613510	|
        	 | CHEMBL.TARGET:CHEMBL614285	|
        	 | CHEMBL.TARGET:CHEMBL4303835	|
        	 | CHEMBL.TARGET:CHEMBL2439	|
        	 | CHEMBL.TARGET:CHEMBL614247	|
        	 | CHEMBL.TARGET:CHEMBL614392	|
        	 | CHEMBL.TARGET:CHEMBL4523510	|
        	 | CHEMBL.TARGET:CHEMBL614049	|
        	 | CHEMBL.TARGET:CHEMBL4523354	|
        	 | CHEMBL.TARGET:CHEMBL4483221	|
        	 | CHEMBL.TARGET:CHEMBL4296391	|
        	 | CHEMBL.TARGET:CHEMBL4523582	|
        	 | CHEMBL.TARGET:CHEMBL613963	|
        	 | CHEMBL.TARGET:CHEMBL391	|
        	 | CHEMBL.TARGET:CHEMBL2487	|
        	 | CHEMBL.TARGET:CHEMBL613847	|
        	 | CHEMBL.TARGET:CHEMBL614875	|
        and the response contains the following entries in "biolink_class"
            | biolink_class     |
            | AnatomicalEntity  |
            | Cell              |
            | CellLine          |
            | CellularComponent |
            | ChemicalEntity    |
            | Organism          |
            | PhenotypicFeature |
            | Protein           |
            | ProteinComplex    |
            | ProteinFamily     |
        and the response only contains the following entries in "biolink_class"
            | biolink_class |
            | AnatomicalEntity  |
            | Cell              |
            | CellLine          |
            | CellularComponent |
            | ChemicalEntity    |
            | NON-MOLECULAR     |
            | Organism          |
            | PhenotypicFeature |
            | Protein           |
            | ProteinComplex    |
            | ProteinFamily     |
        and the response contains the following entries in "provided_by"
            | provided_by                     |
            | ChEMBL activities transformer   |
        and the response only contains the following entries in "provided_by"
            | provided_by                     |
            | ChEMBL activities transformer    |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response contains the following entries in "name" of "names_synonyms" array
            | name           |
            | Cyclooxygenase |


    Scenario: Check ChEMBL activities transformer on structure input
        Given the transformer
        when we fire "/activities/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "CID:2244",
                    "identifiers": {
                        "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                }
            ]
        }
        """
        then the size of the response is 302













    Scenario: Check ChEMBL indications transformer
        Given the transformer
        when we fire "/indications/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "CID:2244",
                    "identifiers": {
                        "chembl": "ChEMBL:CHEMBL25",
                        "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                }
            ]
        }
        """
        then the size of the response is 142
        and the response contains the following entries in "biolink_class"
            | biolink_class              |
            | DiseaseOrPhenotypicFeature |
        and the response only contains the following entries in "biolink_class"
            | biolink_class              |
            | DiseaseOrPhenotypicFeature |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response contains the following entries in "biolink_predicate" of "connections" array
            | biolink_predicate |
            | treats            |
        and the response only contains the following entries in "biolink_predicate" of "connections" array
            | biolink_predicate |
            | treats            |
        and the response contains the following entries in "provided_by"
            | provided_by                   |
            | ChEMBL indication transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                   |
            | ChEMBL indication transformer |
        and the response contains the following entries in "source"
            | source |
            | ChEMBL |
        and the response only contains the following entries in "source"
            | source |
            | ChEMBL |


    Scenario: Check ChEMBL metabolites transformer
        Given the transformer
        when we fire "/metabolites/transform" query with the following body:
        """
        {
            "controls": [],
            "collection": [
                {
                    "biolink_class": "SmallMolecule",
                    "id": "CID:2244",
                    "identifiers": {
                        "chembl": "ChEMBL:CHEMBL25",
                        "inchikey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
                    },
                    "provided_by": "ChEMBL compound-list producer",
                    "source": "ChEMBL"
                }
            ]
        }
        """
        then the size of the response is 8
        and the response contains the following entries in "biolink_class"
            | biolink_class |
            | SmallMolecule |
        and the response only contains the following entries in "biolink_class"
            | biolink_class |
            | SmallMolecule |
        and the response contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response only contains the following entries in "source_element_id" of "connections" array
            | source_element_id |
            | CID:2244          |
        and the response contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response only contains the following entries in "source" of "connections" array
            | source |
            | ChEMBL |
        and the response contains the following entries in "biolink_predicate" of "connections" array
            | biolink_predicate |
            | has_metabolite    |
        and the response only contains the following entries in "biolink_predicate" of "connections" array
            | biolink_predicate |
            | has_metabolite    |
        and the response contains the following entries in "provided_by"
            | provided_by                   |
            | ChEMBL metabolite transformer |
        and the response only contains the following entries in "provided_by"
            | provided_by                   |
            | ChEMBL metabolite transformer |
        and the response contains the following entries in "source"
            | source |
            | ChEMBL |
        and the response only contains the following entries in "source"
            | source |
            | ChEMBL |


