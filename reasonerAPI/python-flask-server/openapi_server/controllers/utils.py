import json

# input type translation map
type_translation_input = {
        # predicates
        'biolink:affected_by': 'affected_by',
        'biolink:affects': 'affects',
        'biolink:treated_by': 'treated_by',
        'biolink:treats': 'treats',
        'biolink:related_to': 'related_to',
        'biolink:correlated_with': 'correlated_with',
        'biolink:has_metabolite': 'has_metabolite',
        'biolink:has_evidence': 'has_evidence',
        'biolink:interacts_with': 'interacts_with',

        # categories
        'biolink:Gene': 'Gene',
        'biolink:ChemicalSubstance': 'ChemicalSubstance',
        'biolink:Disease': 'Disease',
        'biolink:Drug': 'Drug',
        'biolink:Pathway': 'Pathway',
        'biolink:MolecularEntity': 'MolecularEntity',
        'biolink:Assay': 'Assay',
    }

# reverse the type translation map for output
type_translation_output = dict((value, key) for key, value in type_translation_input.items())

# input curie translation map
cpd_curie_translation_input = {
        # compounds (biolink: molepro)
        'PUBCHEM.COMPOUND': 'CID',
        'CHEMBL.COMPOUND': 'ChEMBL',
        'DRUGBANK': 'DrugBank',
        'KEGG': 'KEGG.COMPOUND',
    }

# reverse the curie translation map for output
cpd_curie_translation_output = dict((value, key) for key, value in cpd_curie_translation_input.items())


# input curie translation map
target_curie_translation_input = {
        # targets (biolink: molepro)
        'CHEMBL.TARGET': 'ChEMBL'
    }

# reverse the curie translation map for output
target_curie_translation_output = dict((value, key) for key, value in target_curie_translation_input.items())


# input curie translation map
assay_curie_translation_input = {
        # assays (biolink: molepro)
        'CHEMBL.ASSAY': 'ChEMBL',
    }

# reverse the curie translation map for output
assay_curie_translation_output = dict((value, key) for key, value in assay_curie_translation_input.items())

curie_translation_input = {
    'biolink:ChemicalSubstance':cpd_curie_translation_input,
    'biolink:MolecularEntity':target_curie_translation_input,
    'biolink:Assay':assay_curie_translation_input,
}

curie_translation_output = {
    'biolink:ChemicalSubstance':cpd_curie_translation_output,
    'biolink:MolecularEntity':target_curie_translation_output,
    'biolink:Assay':assay_curie_translation_output,
}

def translate_type(input_type, is_input=True):
    """ translates the predicates and categories if necessary to/from biolink/molepro """
    result = input_type
    map={}
    if is_input:
        map = type_translation_input
    else:
        map = type_translation_output

    # only translate if necessary
    if input_type in map:
        result = map[input_type]

    # log
    # print("utils.translate_type: returning {} for input {}".format(result, input_type))

    # return
    return result

def translate_curie(input_curie, category, is_input=True):
    """ translates the curie prefix if necessary to/from biolink/molepro """
    result = input_curie
    map={}
    if is_input:
        map = curie_translation_input.get(category,{})
    else:
        map = curie_translation_output.get(category,{})

    # split the curie into prefix and value
    if input_curie:
        split_curie = input_curie.split(":")

        if len(split_curie) == 2:
            prefix = split_curie[0]
            value = split_curie[1]

            # if prefix needs to be translated, translate, else leave alone
            if prefix in map:
                result = map[prefix] + ":" + value

    # log
    # print("utils.translate_curie: returning {} for input {}".format(result, input_curie))

    # return
    return result

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
