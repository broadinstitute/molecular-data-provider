import requests
from collections import defaultdict

from molepro.openapi_server.classes.transformer_info import TransformerInfo

url = 'https://molepro.broadinstitute.org/molecular_data_provider/transformers'


def generate_transformers(transformers):

    print('from molepro.server import transform')
    print('from molepro.server import aggregate')
    print('from molepro.utils import get_controls')
    print()
    print()
    for transformer in transformers:
        generate_transformer(transformer)


def generate_transformer(transformer: TransformerInfo):
    function_name = name_to_function_name(transformer.name)
    variable_list = '('
    cache = ",cache='yes'"
    if transformer.function == 'producer':
        variable_list = variable_list + get_variable_list(transformer)[2:]+')'
    elif transformer.function == 'aggregator':
        variable_list = variable_list + '*args'+cache+')'
    else:
        variable_list += 'collection'+get_variable_list(transformer)+cache+')'
    print('def '+function_name+variable_list+':')

    print("    transformer = '"+ transformer.name +"'")

    if transformer.function == 'producer':
        print('    collection_id = None')
    elif transformer.function == 'aggregator':
        print('    collection_ids = [collection.id for collection in args]')
    else:
        print('    collection_id = collection.id')
    
    controls = get_controls(transformer)
    if controls == []:
        print('    controls = []')
    else:
        print('    controls = get_controls(' + ", ".join(get_controls(transformer)) + ')')

    if transformer.function == 'aggregator':
        print('    return aggregate(transformer, collection_ids)')
    else:
        print('    return transform(transformer, collection_id, controls)')

    print()
    print()


def name_to_function_name(name: str):
    function_name = name.lower().replace(' ','_')
    function_name = function_name.replace('-','_')
    function_name = function_name.replace(':','')
    function_name = function_name.replace('(','')
    function_name = function_name.replace(')','')
    return function_name


def parameter_to_variable(parameter: str, space='_', dash='_'):
    variable = parameter.lower().replace(' ',space).replace('-',dash)
    if parameter in ['not']:
        variable = '_'+variable
    return variable


def get_variable_list(transformer: TransformerInfo):
    variable_list = ""
    for parameter in transformer.parameters:
        if parameter.required is None or parameter.required == True:
            variable_list = variable_list + ', '+parameter_to_variable(parameter.name)
    for parameter in transformer.parameters:
        if parameter.required is not None and parameter.required == False:
            variable_list = variable_list + ', '+parameter_to_variable(parameter.name) + "='" + str(parameter.default)+"'"
    return variable_list


def get_controls(transformer: TransformerInfo):
    controls = []
    for parameter in transformer.parameters:
        controls.append(parameter_to_variable(parameter.name, '__', '___')+'='+parameter_to_variable(parameter.name))
    return controls


def generate_transformer_groups(transformers):
    trans_by_class = defaultdict(list)
    for transformer in transformers:
        trans_by_class[(transformer.knowledge_map.input_class,transformer.knowledge_map.output_class)].append(transformer)
    for classes in trans_by_class.keys():
        input_class, output_class = classes
        if len(trans_by_class[classes]) > 2 and (input_class == 'compound' or output_class == 'compound'):
            generate_transformer_group(input_class, output_class, trans_by_class[classes])
        elif input_class in ('none','disease') and output_class in ('gene','protein','disease'):
            generate_transformer_group(input_class, output_class, trans_by_class[classes])


def generate_transformer_group(input_class, output_class, transformers):
    parameters = []
    for transformer in transformers:
        for parameter in transformer.parameters:
            if parameter.name not in parameters:
                parameters.append(parameter.name)
    
    if input_class == 'none':
        function_name = output_class+'_producer'
        argument = 'elements'
    else:
        function_name = 'transform_'+input_class+'_to_'+output_class
        argument = 'collection'
        for parameter in parameters:
            argument += ', ' + parameter_to_variable(parameter)
    print('def '+function_name+'('+argument+'):')
    collections = []
    for i, transformer in enumerate(transformers):
        function_name = name_to_function_name(transformer.name)
        if transformer.function == 'producer':
            variable_list = 'elements'
            if len(transformer.parameters) != 1:
                print("    #### WARN - handle additional parameters")
        else:
            variable_list = 'collection'+get_variable_list(transformer)
        print('    x'+str(i)+' = '+function_name+'('+variable_list+')')
        collections.append('x'+str(i))
    print('    return union(' + ",".join(collections) + ",cache='no')")
    print()
    print()


def main():
    response = requests.get(url)
    transformers = [TransformerInfo.from_dict(transformer) for transformer in response.json()]
    generate_transformers(transformers)
    generate_transformer_groups(transformers)


if __name__ == "__main__":
    main()