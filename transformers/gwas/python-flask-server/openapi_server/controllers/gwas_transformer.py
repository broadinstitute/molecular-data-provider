import requests

from transformers.transformer import Transformer  

class GWASTransformer(Transformer):
    variables = []
    def __init__(self, definition_file):
        super().__init__(self.variables, definition_file = definition_file)
        self.inverse_predicates = { edge.predicate:edge.inverse_predicate for edge in  self.info.knowledge_map.edges}

    def create_trapi_query(self, ids, biolink, predicate):
        query = {
                    "submitter":"MolePro",
                    "message": {
                        "query_graph": {
                            "nodes": {
                                "n0": {
                                    "ids": ids
                                },
                                "n1": {
                                    "categories":
                                        biolink
                                }
                            },
                            "edges": {
                                "e0": {
                                    "subject": "n0",
                                    "object": "n1",
                                    "predicates": [
                                        predicate
                                    ]
                                }
                            }
                        }
                    }
                }
        return query
    
    def call_trapi(self, query):
        response_obj = requests.post(self.info.properties.source_url, json=query)
        response = response_obj.json()
        return response

    def biolink_to_fieldname(self, category, element_id):
        biolink_class = category.split(":")[1]
        # no mapping to fieldname for Phenotypic Feature
        if biolink_class == "PhenotypicFeature":
            biolink_class = "Disease"
        biolink_prefix = element_id.split(":")[0]
        for fieldname in self.prefix_map[biolink_class]:
            if biolink_prefix == self.prefix_map[biolink_class][fieldname]["biolink_prefix"]:
                return fieldname

    def create_transformer_answer(self, answer_list, answers, response):
        nodes= response["message"]["knowledge_graph"]["nodes"]
        edges= response["message"]["knowledge_graph"]["edges"]
        results= response["message"]["results"]
        for result in results:
            element_id = result["node_bindings"]["n1"][0]["id"]
            source_element_id = result["node_bindings"]["n0"][0]["id"]
            edge_id = result["edge_bindings"]["e0"][0]["id"]
            name = nodes[element_id].get("name")
            names = [self.Names(name = name)] if name is not None else None
            category = nodes[element_id]["categories"][0]
            if element_id not in answers:
                element = self.Element(element_id, category, {self.biolink_to_fieldname(category, element_id): element_id}, names)
                answers[element_id] = element
                answer_list.append(element)
            else:
                element = answers[element_id]
            # Build connections using edge_id from results
            edge_info = edges[edge_id]
            if element.connections is None: 
                element.connections = []
            # extract attribute information
            attributes = []
            for attribute_info in edge_info["attributes"]:
                attribute_name = attribute_info.get("original_attribute_name", attribute_info.get("attribute_type_id"))
                attribute_value = str(attribute_info.get("value"))
                attribute_type = attribute_info.get("attribute_type_id")
                attribute_value_type = attribute_info.get("value_type_id")
                attribute_value_url = attribute_info.get("value_url")
                attribute_description = attribute_info.get("description")
                attribute = self.Attribute(attribute_name, attribute_value, attribute_type, attribute_value_type, attribute_value_url, attribute_description)
                attribute.attribute_source = attribute_info.get("attribute_source", self.SOURCE)
                if attribute_name is not None:
                    attributes.append(attribute)
            element.connections.append(self.Connection(source_element_id, edge_info["predicate"], self.inverse_predicates.get(edge_info["predicate"]), attributes= attributes))


class DiseaseToGeneTranformer(GWASTransformer):
    # transformer will go through collection identifiers
    def __init__(self):
        super().__init__('info/diseasetogene_transformer_info.json')
    def map(self, disease_list, controls):
        # resulting gene elements will go here
        gene_list = []
        genes = {} 
        disease_ids= []
        for disease in disease_list:
            element_id = disease.id
            # disease_identifiers = disease.identifiers
            disease_ids.append(element_id)
        if len(disease_ids) == 0:
            return gene_list
        query = self.create_trapi_query(disease_ids, ["biolink:Gene"], "biolink:condition_associated_with_gene")
        response = self.call_trapi(query)
        self.create_transformer_answer(gene_list, genes, response)
        return gene_list

class GeneToDiseaseTranformer(GWASTransformer):
    variables = []
    def __init__(self):
        super().__init__('info/genetodisease_transformer_info.json')
    def map(self, gene_list, controls):
        disease_list = []
        diseases ={}
        gene_ids= []
        for gene in gene_list: 
            element_id = gene.id
            gene_ids.append(element_id)
        if len(gene_ids) == 0:
            return disease_list
        query = self.create_trapi_query(gene_ids, ["biolink:Disease", "biolink:PhenotypicFeature"], "biolink:gene_associated_with_condition")
        response = self.call_trapi(query)
        self.create_transformer_answer(disease_list, diseases, response)
        return disease_list

    

 
    
    

    
