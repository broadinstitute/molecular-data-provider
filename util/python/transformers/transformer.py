from openapi_server.models.transformer_info import TransformerInfo
from openapi_server.models.element import Element
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.connection import Connection

import json
import csv
import os.path
from os import path
import sys, getopt

class Transformer:
    class_dict = None   # Dictionary of MolePro class to Biolink class
    prefix_map = None   # JSON mapping of Biolink class to MolePro & Biolink prefixes

    def __init__(self, variables, definition_file):
        self.variables = variables
        self.definition_file = definition_file
        self.transformer_info('bypass')

    def transform(self, query):
        query_controls = {}
        for control in query.controls:
            if control.name not in query_controls:
                query_controls[control.name] = [control.value]
            else:
                query_controls[control.name].append(control.value)
        controls = {}
      # iterate through the array(s) of parameters found in 'transformer_info.json'
        for variable, parameter in self.parameters.items():
        #   check that the value of name parameter (e.g., 'disease') is in the query JSON
            if parameter.name in query_controls:
                if parameter.multivalued:
                    controls[variable] = query_controls[parameter.name]
                else: 
                    if len(query_controls[parameter.name]) == 1:
                        try:
                            controls[variable] = Transformer.get_control(query_controls[parameter.name][0], parameter)
                        except ValueError:
                            msg = "invalid value '{}' provided".format(query_controls[parameter.name])
                            return ({ "status": 400, "title": "Bad Request", "detail": msg, "type": "about:blank" }, 400 )
                    else:
                        msg = "duplicate parameter'{}' provided".format(query_controls[parameter.name])
                        return ({ "status": 400, "title": "Bad Request", "detail": msg, "type": "about:blank" }, 400 )
            else:
                if parameter.required:
                    msg = "required parameter '{}' not specified".format(parameter.name)
                    return ({ "status": 400, "title": "Bad Request", "detail": msg, "type": "about:blank" }, 400 )
                else:
                    controls[variable] = parameter.default
        
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


#   Extract and return the correct type of collection from the request query's JSON 
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



    #######################################################################################################
    # This function reads & converts into a dictionary, the text file fetched from 
    # https://github.com/broadinstitute/scb-kp-dev/blob/master/MoleProAPI/java-play-framework-server/conf/BiolinkClassMap.txt
    # where the columns are:
    # class	| biolink_class
    #
    def get_class_dict(self):
            classDict = {}
            tsv_file = open("data/BiolinkClassMap.txt")
            for line in csv.DictReader(tsv_file, delimiter="\t"):
                classDict[line['class']] = line['biolink_class']
            return classDict


    #######################################################################################################
    # 
    # Read JSON file (data/prefixMap.json) that contains mapping of Biolink class, fieldname and molepro prefix
    # 
    # The prefixMap.json JSON file was converted from the spreadsheet prefixMap.csv into a JSON file.
    #
    # Then the JSON file is saved into a variable, prefixMap, for general usage by all class methods.
    #
    # The spreadsheet columns are:
    # MolePro class	| Biolink class	| MolePro field name  | MolePro CURIE prefix | Biolink CURIE prefix
    #
    def get_prefix_mapping(self):      
        with open('data/prefixMap.json') as json_file:
            prefixMap = json.load(json_file)                           
        return prefixMap


    #######################################################################################################
    #
    # If cache=='bypass' this method will reload transformer_info, BiolinkClassMap.txt and prefixMap.json; 
    # return transformer_info
    #
    # LOOKUP TABLES:
    # self.prefix_map: mapping from Biolink Class & Field Name to MolePro Prefix
    # self.class_dict: dictionary of MolePro Class to Biolnk Class 
    #
    def transformer_info(self, cache):
        if cache=='bypass':
            with open(self.definition_file,'r') as f:
                self.info = TransformerInfo.from_dict(json.loads(f.read()))
                self.parameters = dict(zip(self.variables, self.info.parameters))
                self.update_transformer_info(self.info) 
            self.prefix_map = self.get_prefix_mapping()
            self.class_dict = self.get_class_dict()
            self.SOURCE = self.info.label
            self.PROVIDED_BY  = self.info.name
            self.OUTPUT_CLASS = self.info.knowledge_map.output_class
            self.INPUT_CLASS  = self.info.knowledge_map.input_class
            if self.info.knowledge_map.edges is not None and len(self.info.knowledge_map.edges) > 0:
                self.PREDICATE    = self.info.knowledge_map.edges[0].predicate
                self.INVERSE_PREDICATE    = self.info.knowledge_map.edges[0].inverse_predicate 
        return self.info


    #######################################################################################################
    #
    # This method is overridden in the transformer child class.
    #
    #
    def update_transformer_info(self, json_obj):
        pass


    ########################################################################################################
    # Lookup the required CURIE Prefix corresponding to parameters:
    # (1) the MolePro field name of an identifier. e.g., field name "chembl" gets MolePro CURIE prefix "ChEMBL:"
    # (2) the MolePro class e.g., MolePro class determines the Biolink CURIE prefix for the field name "chembl"
    #
    def get_prefix(self,fieldname,molepro_class=None):
        if molepro_class == None:
            molepro_class = self.OUTPUT_CLASS 
        return self.prefix_map[self.class_dict[molepro_class]][fieldname]['molepro_prefix']


    #######################################################################################################
    #
    #   Check for MolePro prefix in the controls value, e.g., "UMLS:C0011860"
    # - uses input_class from the xxx_transformer_info.json file if molepro_class = None, 
    # - returns boolean;
    #  Parameters:
    #  * fieldname: a key in the JSON output
    #  * identifier: an id such as "UMLS:C0011860" or "ChEMBL:CHEMBL3727577"
    #  * molepro_class: such as "compound", as specified by output_class in the xxx_transformer_info.json file  
    # 
    #  This method was made case-insenstive with respect to the "identifier" argument.
    # 
    def has_prefix(self, fieldname, identifier, molepro_class=None):
        if molepro_class is None:
            molepro_class = self.INPUT_CLASS     
        if identifier.upper().find(self.prefix_map[self.biolink_class(molepro_class)][fieldname]['molepro_prefix'].upper()) == 0:
            return True
        else:
            return False


    #######################################################################################################
    #
    #  Removes prefix from identifier
    #  Parameters: 
    #  * fieldname: the key in the JSON input, e.g., "chembl" as in "chembl":"ChEMBL:CHEMBL3727577"
    #  * identifier: an id, such as "ChEMBL:CHEMBL3727577" that needs to be "split" into "ChEMBL" & "CHEMBL3727577"
    #  * molepro_class: such as "compound", as specified by input_class or output_class in the 
    #    xxx_transformer_info.json file
    #
    #  This method was made case-insenstive with respect to the "identifier" argument.
    #  
    def de_prefix(self, fieldname, identifier, molepro_class=None):
        if molepro_class is None:
            molepro_class = self.INPUT_CLASS 
        return identifier.upper().split(self.prefix_map[self.biolink_class(molepro_class)][fieldname]['molepro_prefix'].upper() ,1)[1] 


    #######################################################################################################
    #
    #  Add prefix to identifier if not already there
    #  Parameters:
    #  * fieldname: a key in the JSON output, e.g., "chembl" as in "chembl":"ChEMBL:CHEMBL3727577"
    #  * identifier: an id such as "CHEMBL3727577"
    #  * molepro_class: such as "compound", as specified by output_class in the xxx_transformer_info.json file 
    #
    def add_prefix(self, fieldname, identifier, molepro_class=None):
        if molepro_class == None:
            molepro_class = self.OUTPUT_CLASS   
        if not self.has_prefix(fieldname, identifier, molepro_class):
            return self.get_prefix(fieldname,molepro_class) + identifier
        else:
            return identifier

    
    #######################################################################################################
    #
    #  Map Biolink class for the given MolePro class
    #  Parameters:
    #  * molepro_class: such as "compound", as specified by input_class or output_class in the 
    #    xxx_transformer_info.json file
    #
    def biolink_class(self, molepro_class):      
        return self.class_dict[molepro_class]


    #######################################################################################################
    #
    #  convenience method to create attribute
    #
    def Attribute(self, name, value, type=None, value_type = None, url=None, description=None):
        if type == None:
            type = name
        return Attribute(
            attribute_type_id = type, 
            original_attribute_name = name, 
            value = value, 
            value_type_id = value_type, 
            attribute_source = self.SOURCE, 
            value_url = url, 
            description = description, 
            provided_by = self.PROVIDED_BY
        )


    #######################################################################################################
    #
    #  convenience method to create element
    #
    def Element(self, id, biolink_class, identifiers, names_synonyms = None, attributes = None):
        return Element(
            id=id, 
            biolink_class=biolink_class, 
            identifiers=identifiers, 
            names_synonyms=names_synonyms if names_synonyms is not None else [], 
            attributes=attributes if attributes is not None else [], 
            connections=[], 
            source=self.SOURCE, 
            provided_by=self.PROVIDED_BY
        )


    #######################################################################################################
    #
    #  convenience method to create names
    #
    def Names(self, name, synonyms=None, type=None, language = None):
        return Names(
            name=name, 
            synonyms=synonyms if synonyms is not None else [], 
            name_type=type, 
            source=self.SOURCE, 
            provided_by=self.PROVIDED_BY, 
            language=None
        )


    #######################################################################################################
    #
    #  convenience method to create names
    #
    def Connection(self, source_element_id, predicate, inv_predicate, relation=None, inv_relation=None, attributes = None):
        return Connection(
            source_element_id=source_element_id, 
            biolink_predicate=predicate, 
            inverse_predicate=inv_predicate, 
            relation=relation, 
            inverse_relation=inv_relation, 
            source=self.SOURCE, 
            provided_by=self.PROVIDED_BY, 
            attributes=attributes if attributes is not None else []
        )


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

############################################################################################
#
# A universal utility to convert to JSON, the prefixMap spreadsheet 
#
# JSON file is the resource where the python code can simply look up the prefix mapping without the
# cost of iterating through the rows of the spreadsheet.
#
# Parameter:
# * filepath: the relative path to the directory containing the prefixMap.csv spreadsheet
#
class TransformerUtility:
    def convert_csvmap_2_json(filepath):
        with open(filepath+'/prefixMap.csv', 'r') as data:
                prefixMap = {}
                for line in csv.DictReader(data):
                    if line['MolePro class'] != '':
                        if line['Biolink class'] not in prefixMap:
                            prefixMap[line['Biolink class']] = {}
                        prefix = {}
                        if line['MolePro CURIE prefix'] == "<none>":
                            prefix["molepro_prefix"] = ''
                        else:
                            prefix["molepro_prefix"] = line['MolePro CURIE prefix']
                        prefix["biolink_prefix"] = line['Biolink CURIE prefix']
                        prefixMap[line['Biolink class']][line['MolePro field name']]= prefix
                        
#       Save as a JSON file
        with open(filepath+'/prefixMap.json', 'w') as outfile:
            json.dump(prefixMap, outfile, indent=4, sort_keys=True)            


class Producer(Transformer):

    def produce(self, controls):
        element_list = []
        elements = {}
        for name in controls[self.variables[0]]:
            for id in self.find_names(name):
                if id not in elements:
                    element = self.create_element(id)
                    if element is not None:
                        elements[id] = element
                        element_list.append(element)
                if id in elements:
                    elements[id].attributes.append(
                        self.Attribute(name='query name', value=name, type='')
                )
        return element_list


############################################################################################
#
# The file's main( ) method with the one purpose to call the .csv to .json conversion of the
# CURIE prefix mapping
#
#
def main():
    TransformerUtility.convert_csvmap_2_json(str(sys.argv[1]))
if __name__ == "__main__":
    main()
