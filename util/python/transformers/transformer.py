from openapi_server.models.transformer_info import TransformerInfo

import json


class Transformer:

    def __init__(self, variables, definition_file = 'transformer_info.json'):
        with open(definition_file,'r') as f:
            self.info = TransformerInfo.from_dict(json.loads(f.read()))
            self.variables = variables
            self.parameters = dict(zip(variables, self.info.parameters))


    def transform(self, query):
        query_controls = {control.name: control.value for control in query.controls}
        controls = {}
        for variable, parameter in self.parameters.items():
            if parameter.name in query_controls:
                controls[variable] = Transformer.get_control(query_controls[parameter.name], parameter)
            else:
                msg = "required parameter '{}' not specified".format(parameter.name)
                return ({ "status": 400, "title": "Bad Request", "detail": msg, "type": "about:blank" }, 400 )

        if self.info.function == 'producer':
            return self.produce(controls)
        if self.info.function == 'expander':
            return self.expand(self.getCollection(query), controls)
        if self.info.function == 'filter':
            return self.filter(self.getCollection(query), controls)
        if self.info.function == 'exporter':
            return self.export(self.getCollection(query), controls)
        if self.info.function == 'transformer':
            return self.map(self.getCollection(query), controls)

        return ({ "status": 500, "title": "Internal Server Error",
            "detail": "Function '"+self.info.function+"' not implemented", "type": "about:blank" }, 500 )

# Extract and return the correct type of collection from the request query's JSON 
    def getCollection(self, query):
        if hasattr(query,'collection'):
            return query.collection
        if self.info.knowledge_map.input_class == 'gene':
            return query.genes
        if self.info.knowledge_map.input_class == 'compound':
            return query.compounds


    def produce(self, controls):
        return ({ "status": 500, "title": "Internal Server Error", "detail": "Producer not implemented", "type": "about:blank" }, 500 )


    def expand(self, collection, controls):
        return ({ "status": 500, "title": "Internal Server Error", "detail": "Expander not implemented", "type": "about:blank" }, 500 )


    def filter(self, collection, controls):
        return ({ "status": 500, "title": "Internal Server Error", "detail": "Filter not implemented", "type": "about:blank" }, 500 )


    def export(self, collection, controls):
        return ({ "status": 500, "title": "Internal Server Error", "detail": "Exporter not implemented", "type": "about:blank" }, 500 )


    def map(self, collection, controls):
        return ({ "status": 500, "title": "Internal Server Error", "detail": "Transformer not implemented", "type": "about:blank" }, 500 )


    @staticmethod
    def get_control(value, parameter):
        if parameter.type == 'double':
            return float(value)
        elif parameter.type == 'Boolean':
            return bool(value)
        elif parameter.type == 'int':
            return int(value)
        else:
            return value


