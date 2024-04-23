import json
import logging
import sys

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(name)s %(threadName)s : %(message)s')
handler = logging.StreamHandler(sys.stdout)

# singleton class to keep translations in memory, avoid repeated file reading
# see https://www.geeksforgeeks.org/singleton-method-python-design-patterns/
class BiolinkSingleton:
  
    __shared_instance = 'biolink'
  
    @staticmethod
    def getInstance():
        """Static Access Method"""
        if BiolinkSingleton.__shared_instance == 'biolink':
            BiolinkSingleton()
        return BiolinkSingleton.__shared_instance
  
    def __init__(self):
        """virtual private constructor"""
        if BiolinkSingleton.__shared_instance != 'biolink':
            raise Exception ("This class is a singleton class !")
        else:
            # read the biolink translations file
            with open('conf/biolinkTranslation.json') as json_file:
                # read the map
                self.biolink = json.load(json_file)

                # reverse the maps
                self.biolink['type_translation_output'] = dict((value, key) for key, value in self.biolink.get('type_translation_input').items())
                self.biolink['type_translation_output']['ChemicalSubstance'] = 'biolink:SmallMolecule'
                self.biolink['cpd_curie_translation_output'] = dict((value, key) for key, value in self.biolink.get('cpd_curie_translation_input').items())
                self.biolink['target_curie_translation_output'] = dict((value, key) for key, value in self.biolink.get('target_curie_translation_input').items())
                self.biolink['assay_curie_translation_output'] = dict((value, key) for key, value in self.biolink.get('assay_curie_translation_input').items())

            # read biolink attributes
                with open('conf/biolinkAttributes.json') as json_file:
                    # read the map
                    biolink_attributes = json.load(json_file)
                    self.node_attributes = set(biolink_attributes.get('node_attributes'))
                    print('loaded '+str(len(self.node_attributes))+' node attributes')
                    self.edge_attributes = set(biolink_attributes.get('edge_attributes'))
                    print('loaded '+str(len(self.edge_attributes))+' edge attributes')
                    self.hidden_attributes = set(biolink_attributes.get('hidden_attributes'))
                    print('loaded '+str(len(self.hidden_attributes))+' hidden attributes')


            # set the object
            BiolinkSingleton.__shared_instance = self

def get_logger(name): 
    # get the logger
    logger = logging.getLogger(name)

    # return
    return logger 

# get the biolink translation object
biolink_object = BiolinkSingleton.getInstance()

def translate_type(input_type, is_input=True):
    """ translates the predicates and categories if necessary to/from biolink/molepro """
    result = input_type
    map={}
    if is_input:
        # map = type_translation_input
        map = biolink_object.biolink.get('type_translation_input')
    else:
        # map = type_translation_output
        map = biolink_object.biolink.get('type_translation_output')

    # only translate if necessary
    if input_type in map:
        result = map[input_type]

    # log
    # print("utils.translate_type: returning {} for input {}".format(result, input_type))

    # return
    return result


def translate_curie(input_curie, category, is_input=True, field=None):
    """ translates the curie prefix if necessary to/from biolink/molepro """
    result = input_curie
    map={}
    if is_input:
        # map = curie_translation_input.get(category,{})
        map = biolink_object.biolink.get('curie_translation_input').get(category,{})
    else:
        # map = curie_translation_output.get(category,{})
        map = biolink_object.biolink.get('curie_translation_output').get(category,{})

    # split the curie into prefix and value
    if input_curie:
        split_curie = input_curie.split(":")

        if len(split_curie) == 2:
            prefix = split_curie[0]
            value = split_curie[1]

            # if prefix needs to be translated, translate, else leave alone
            if prefix in map:
                result = map[prefix] + ":" + value

        if len(split_curie) == 1 and field in map:
            result = map[field] + ":" + input_curie

    # log
    # print("utils.translate_curie: returning {} for input {}".format(result, input_curie))

    # return
    return result


def node_attributes():
    return biolink_object.node_attributes

    
def edge_attributes():
    return biolink_object.edge_attributes


def hidden_attributes():
    return biolink_object.hidden_attributes


def migrate_transformer_chains(inFile, outFile):
    with open(inFile) as f:
        json_obj = json.load(f)
    for chain in json_obj:
        chain['subject'] = translate_type(chain['subject'], False)
        chain['predicate'] = translate_type(chain['predicate'], False)
        chain['object'] = translate_type(chain['object'], False)
        print(chain['subject'],chain['predicate'],chain['object'],'\n')
    with open(outFile, 'w') as json_file:
        json.dump(json_obj, json_file, indent=4, separators=(',', ': ')) # save to file with prettifying

if (__name__ == "__main__"):
    curie = "ChEMBL:CHEMBL1197118"
    translated_curie = translate_curie(curie, False)

    migrate_transformer_chains("transformer_chains.json","transformer_chains.json")
