from molepro.server import elements

def names(collection, file):
    with open(file, 'w') as output:
        print('id', 'name', 'name_type', 'name_source', 'provided_by', sep='\t', file=output)
        for element in elements(collection):
            id = element.id
            for names in element.names_synonyms:
                name = names.name
                name_type = names.name_type or 'name'
                name_source = names.source
                provided_by = names.provided_by
                if name is not None:
                    print(id, name, name_type, name_source, provided_by, sep='\t', file=output)
                synonyms = names.synonyms or []
                name_type = names.name_type or 'synonym'
                for synonym in synonyms:
                    print(id, synonym, name_type, name_source, provided_by, sep='\t', file=output)
    print('[MolePro] Saved names to '+file)


def identifiers(collection, file):
    with open(file, 'w') as output:
        print('id', 'xref_source', 'xref', sep='\t', file=output)
        for element in elements(collection):
            id = element.id
            for source, xref in element.identifiers.items():
                if type(xref) == list:
                    xref = ";".join(xref)
                print(id, source, xref, sep='\t', file=output)
    print('[MolePro] Saved identifiers to '+file)


def attributes(collection, file):
    with open(file, 'w') as output:
        print('id', 'attribute_type_id', 'original_attribute_name', 'value', 'attribute_source', 'value_url', 'description', sep='\t', file=output)
        for element in elements(collection):
            id = element.id
            for attribute in element.attributes:
                value = attribute.value or ''
                description = attribute.description or ''
                print(id, attribute.attribute_type_id,attribute.original_attribute_name, value.replace('\n',' '), 
                    attribute.attribute_source, attribute.value_url or '', description.replace('\n',' '), sep='\t', file=output)
    print('[MolePro] Saved attributes to '+file)


def connections(collection, file):
    with open(file, 'w') as output:
        print('source_element_id', 'predicate', 'id', 'source', 'provided_by', sep='\t', file=output)
        for element in elements(collection):
            id = element.id
            for connection in element.connections:
                print(connection.source_element_id, connection.biolink_predicate, id, 
                    connection.source, connection.provided_by, sep='\t', file=output)
    print('[MolePro] Saved connections to '+file)

