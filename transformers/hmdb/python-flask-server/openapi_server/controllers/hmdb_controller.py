import sqlite3
import re

from collections import defaultdict

from transformers.transformer import Transformer, Producer


inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')


class HmdbTargets(Transformer):


    def __init__(self, variables, definition_file):
        super().__init__(variables, definition_file)


    def map(self, compound_list, controls):
        target_list = []
        targets = {}
        for compound in compound_list:
            metabolite = find_metabolite(self, compound)
            if metabolite is not None:
                metabolite_id = metabolite['METABOLITE_ID']
                for target in get_targets(metabolite_id):
                    uniprot_id = target['UNIPROT_ID']
                    if uniprot_id not in targets:
                        element = self.create_target(target)
                        if element is not None:
                            # handle one gene with multiple uniprot ids
                            if element.id in targets:
                                element = targets[element.id]
                            else:
                                targets[element.id] = element
                                target_list.append(element)
                            targets[uniprot_id] = element
                    else:
                        element = targets.get(uniprot_id)
                    if element is not None:
                        connection = self.Connection(compound.id, self.PREDICATE, self.INVERSE_PREDICATE)
                        connection.attributes.append(self.Attribute('biolink:primary_knowledge_source','infores:hmdb'))
                        element.connections.append(connection)
        return target_list


class HmdbProteinTargets(HmdbTargets):

    def __init__(self):
        super().__init__([], definition_file='info/protein_targets_transformer_info.json')

    def update_transformer_info(self, info):
        info.knowledge_map.nodes[self.biolink_class('SmallMolecule')].count = metabolite_count()
        info.knowledge_map.nodes[self.biolink_class('Protein')].count = protein_count()
        info.knowledge_map.edges[0].count = target_count()


    def create_target(self, target):
        uniprot_id = target['UNIPROT_ID']
        hmdb_protein = target['PROTEIN_ACCESSION']
        protein_name = target['PROTEIN_NAME']
        gene_symbol = target['GENE_NAME']
        protein_type = target['PROTEIN_TYPE']
        id = self.add_prefix('uniprot', uniprot_id, 'Protein')
        identifiers = {
            'uniprot': id,
            'hmdb': self.add_prefix('hmdb',hmdb_protein)
        }
        name = self.Names(protein_name)
        gene_symbol_attr = self.Attribute('gene_name', gene_symbol)
        gene_symbol_attr.attribute_type_id = 'biolink:symbol'
        attributes = [
            gene_symbol_attr,
            self.Attribute('protein_type', protein_type)
        ]
        return self.Element(id, self.biolink_class('Protein'), identifiers, [name], attributes)


class HmdbGeneTargets(HmdbTargets):

    def __init__(self):
        super().__init__([], definition_file='info/gene_targets_transformer_info.json')


    def update_transformer_info(self, info):
        self.load_ids()
        info.knowledge_map.nodes[self.biolink_class('SmallMolecule')].count = metabolite_count()
        info.knowledge_map.nodes[self.biolink_class('Gene')].count = len(self.id_map)
        info.knowledge_map.edges[0].count = target_count()


    def create_target(self, target):
        uniprot_id = target['UNIPROT_ID']
        hmdb_protein = target['PROTEIN_ACCESSION']
        protein_name = target['PROTEIN_NAME']
        gene_symbol = target['GENE_NAME']
        protein_type = target['PROTEIN_TYPE']
        gene_id = self.id_map.get(uniprot_id)
        if gene_id is None:
            return None
        id = self.add_prefix('entrez', gene_id, 'Gene')
        identifiers = {
            'entrez': id
        }
        name = self.Names(protein_name)
        gene_symbol_attr = self.Attribute('gene_name', gene_symbol)
        gene_symbol_attr.attribute_type_id = 'biolink:symbol'
        return self.Element(id, self.biolink_class('Gene'), identifiers, [name], [gene_symbol_attr])


    def load_ids(self):
        self.id_map = {}
        with open("data/UniProt2Entrez.txt",'r') as f:
            first_line = True
            for line in f:
                if not first_line:
                    row = line.strip().split('\t')
                    uniprot = row[0]
                    entrez = row[1]
                    self.id_map[uniprot] = entrez
                first_line = False


class HmdbDisorders(Transformer):


    def __init__(self):
        super().__init__([], definition_file='info/disorders_transformer_info.json')


    def update_transformer_info(self, info):
        self.id_map = load_ids(['disease'])
        info.knowledge_map.nodes[self.biolink_class('SmallMolecule')].count = metabolite_count()
        info.knowledge_map.nodes['DiseaseOrPhenotypicFeature'].count = disease_count()
        info.knowledge_map.edges[0].count = indications_count()


    field_map = {
        'EFO': 'efo',
        'HP': 'hpo',
        'MONDO': 'mondo',
        'NCIT': 'nci_thesaurus',
        'OMIM': 'omim',
        'UMLS': 'umls'
    }


    def map(self, compound_list, controls):
        disorder_list = []
        disorders = {}
        for compound in compound_list:
            metabolite = find_metabolite(self, compound)
            if metabolite is not None:
                metabolite_id = metabolite['METABOLITE_ID']
                if metabolite_id is not None:
                    references = self.get_disorder_references(metabolite_id)
                    for disorder in self.find_disorders(metabolite_id):
                        id = disorder['id']
                        if id is not None:
                            element = disorders.get(id)
                            if element is None:
                                element = self.create_element(id, disorder)
                                disorder_list.append(element)
                                disorders[id] = element
                            connection = self.create_connections(compound.id, references.get(disorder['disease_id']))
                            element.connections.append(connection)
        return disorder_list


    def get_disorder_references(self, metabolite_id):
        references = defaultdict(list)
        for row in get_disorder_references(metabolite_id):
            disease_id = row['DISEASE_ID']
            references[disease_id].append(row)
        return references


    def find_disorders(self, metabolite_id):
        disorders = []
        for row in get_disorders(metabolite_id):
            for terms in self.id_map.get(row['DISEASE'], [{'primary_id': None, 'primary_name': None}]):
                omim_id = self.add_prefix('omim', row['OMIM_ID'], 'disease') if row['OMIM_ID'] is not None else None
                field = self.find_field(terms['primary_id'])
                primary_id = terms['primary_id'] if field is not None else None
                id = primary_id if primary_id is not None else omim_id
                disorders.append({
                    'id': id,
                    'disease_id': row['DISEASE_ID'],
                    'term': row['DISEASE'],
                    'definition': row['DEFINITION'],
                    'omim_id': omim_id,
                    'primary_id': terms['primary_id'],
                    'primary_name': terms['primary_name'],
                    'field': field
                })
        return disorders


    def find_field(self, primary_id):
        if primary_id is None:
            return None
        return self.field_map.get(primary_id.split(':')[0])


    def create_element(self, id, disorder):
        identifiers = {}
        if disorder['field'] is not None:
            identifiers[disorder['field']] = disorder['primary_id']
        if disorder['omim_id'] is not None:
            identifiers['omim'] = disorder['omim_id']
        name = self.Names(disorder['term'])
        primary_name = self.Names(disorder['term'], name_source='infores:sri-name-resolver')
        attributes = []
        if disorder['definition'] is not None:
            attributes.append(self.Attribute('definition', disorder['definition'], 'biolink:description'))
        element = self.Element(id, self.biolink_class('disease'), identifiers, [name, primary_name], attributes)
        return element


    def create_connections(self, source_element_id, references):
        attributes = []
        for reference in references:
            attr_value = 'PMID:'+str(reference['PUBMED_ID']) if reference['PUBMED_ID'] is not None else reference['REFERENCE']
            attributes.append(
                self.Attribute('reference', attr_value, 'biolink:publication', description=reference['REFERENCE'])
            )
        connection = self.Connection(
            source_element_id = source_element_id,
            predicate = self.PREDICATE,
            inv_predicate = self.INVERSE_PREDICATE,
            attributes = attributes
        )
        return connection


class HmdbLocations(Transformer):


    def __init__(self):
        super().__init__([], definition_file='info/locations_transformer_info.json')


    def update_transformer_info(self, info):
        self.id_map = load_ids(['biospecimen', 'cellular', 'tissue'])
        info.knowledge_map.nodes[self.biolink_class('SmallMolecule')].count = metabolite_count()
        info.knowledge_map.nodes['AnatomicalEntity'].count = len(self.id_map)
        #info.knowledge_map.edges[0].count = locations_count()


    field_map = {
        'CL': 'cell_ontology',
        'GO': 'go',
        'MONDO': 'mondo',
        'NCIT': 'nci_thesaurus',
        'UBERON': 'uberon',
        'UMLS': 'umls'
    }


    def map(self, compound_list, controls):
        locations_list = []
        locations = {}
        for compound in compound_list:
            connections = {}
            metabolite = find_metabolite(self, compound)
            if metabolite is not None:
                metabolite_id = metabolite['METABOLITE_ID']
                if metabolite_id is not None:
                    for location in self.find_locations(metabolite_id):
                        id = location['id']
                        if id is not None:
                            element = locations.get(id)
                            if element is None:
                                element = self.create_element(id, location)
                                locations_list.append(element)
                                locations[id] = element
                            connection = self.create_connections(compound.id)
                            connections[id] = connection
                            element.connections.append(connection)
                    for concentration in self.get_concentrations(metabolite_id):
                        id = concentration['id']
                        if id is not None:
                            element = locations.get(id)
                            if element is None:
                                element = self.create_element(id, concentration)
                                locations_list.append(element)
                                locations[id] = element
                            connection = connections.get(id)
                            if connection is None:
                                connection = self.create_connections(compound.id)
                                connections[id] = connection
                                element.connections.append(connection)
                            connection.attributes.append(concentration['attribute'])
        return locations_list


    def find_locations(self, metabolite_id):
        locations = []
        for row in get_locations(metabolite_id):
            for terms in self.id_map.get(row['VALUE'],[]):
                locations.append({
                    'location': row['VALUE'],
                    'id': terms['primary_id'], 
                    'primary_name': terms['primary_name'],
                    'definition': row['DEFINITION'],
                    'field': self.field_map.get(terms['primary_id'].split(':')[0])
                })
        return locations


    def create_element(self, id, location):
        identifiers = {}
        if location['field'] is not None:
            identifiers[location['field']] = location['id']
        name = self.Names(location['location'])
        primary_name = self.Names(location['location'], name_source='infores:sri-name-resolver')
        attributes = []
        if location['definition'] is not None:
            attributes.append(self.Attribute('definition', location['definition'], 'biolink:description'))
        element = self.Element(id, self.biolink_class('AnatomicalEntity'), identifiers, [name, primary_name], attributes)
        return element


    def create_connections(self, source_element_id):
        attributes = []
        connection = self.Connection(
            source_element_id = source_element_id,
            predicate = self.PREDICATE,
            inv_predicate = self.INVERSE_PREDICATE,
            attributes = attributes
        )
        return connection


    def get_concentrations(self, metabolite_id):
        concentration_attributes = []
        prev_conc_id = -1
        prev_conc_attr = []
        for row in get_concentrations(metabolite_id):
            location = row['BIOSPECIMEN']
            reference = reference_attribute(self, row)
            if prev_conc_id == row['CONCENTRATION_ID'] and reference is not None:
                for attr in prev_conc_attr:
                    attr.attributes.append(reference)
            else:
                prev_conc_id = row['CONCENTRATION_ID']
                prev_conc_attr = []
                for terms in self.id_map.get(location,[]):
                    name = 'abnormal_concentration' if row['ABNORMAL_CONCENTRATION'] == 1 else 'normal_concentration'
                    subattributes = []
                    self.add_attribute(subattributes, 'concentration_units', row['CONCENTRATION_UNITS']),
                    self.add_attribute(subattributes, 'subject_age', row['AGE']),
                    self.add_attribute(subattributes, 'subject_gender', row['GENDER']),
                    self.add_attribute(subattributes, 'subject_condition', row['SUBJECT_CONDITION']),
                    self.add_attribute(subattributes, 'patient_information', row['PATIENT_INFORMATION']),
                    self.add_attribute(subattributes, 'comment', row['COMMENT']),
                    if reference is not None:
                        subattributes.append(reference)
                    attribute = self.Attribute(
                        name = name,
                        value = row['CONCENTRATION_VALUE'],
                        attributes = subattributes
                    )
                    concentration_attributes.append({
                        'location': location,
                        'attribute': attribute,
                        'id': terms['primary_id'],
                        'primary_name': terms['primary_name'],
                        'definition': row['DEFINITION'],
                        'field': self.field_map.get(terms['primary_id'].split(':')[0])
                    })
                    prev_conc_attr.append(attribute)

        return concentration_attributes


    def add_attribute(self, attributes, name, value):
        if value is not None:
            attributes.append( self.Attribute(name, value))


class HmdbPathways(Transformer):


    def __init__(self):
        super().__init__([], definition_file='info/pathways_transformer_info.json')


    def update_transformer_info(self, info):
        self.id_map = load_ids(['biospecimen', 'cellular', 'tissue'])
        info.knowledge_map.nodes[self.biolink_class('SmallMolecule')].count = metabolite_count()
        info.knowledge_map.nodes['Pathway'].count = pathways_count()
        info.knowledge_map.edges[0].count = pathways_connections_count()


    def map(self, compound_list, controls):
        pathway_list = []
        pathways = {}
        for compound in compound_list:
            metabolite = find_metabolite(self, compound)
            if metabolite is not None:
                metabolite_id = metabolite['METABOLITE_ID']
                if metabolite_id is not None:
                    for pathway in find_pathways(metabolite_id):
                        name = pathway['PATHWAY_NAME']
                        if name is not None:
                            element = pathways.get(name)
                            if element is None:
                                element = self.create_element(name, pathway)
                                if element.id is not None:
                                    pathway_list.append(element)
                                    pathways[name] = element
                            connection = self.create_connection(compound.id)
                            element.connections.append(connection)
        return pathway_list


    def create_element(self, name, pathway):
        smpdb_id = self.add_prefix('smpdb', pathway['SMPDB_ID']) if pathway['SMPDB_ID'] is not None else None
        kegg_id =  self.add_prefix('kegg', pathway['KEGG_MAP_ID']) if pathway['KEGG_MAP_ID'] is not None else None
        id = smpdb_id if smpdb_id is not None else kegg_id
        identifiers = {}
        if smpdb_id is not None:
            identifiers['smpdb'] = smpdb_id
        if kegg_id is not None:
            identifiers['kegg'] = kegg_id
        element = self.Element(id, self.biolink_class('pathway'), identifiers, [self.Names(name)])
        return element


    def create_connection(self, source_element_id):
        return self.Connection(
            source_element_id = source_element_id,
            predicate = self.PREDICATE,
            inv_predicate = self.INVERSE_PREDICATE,
            attributes = []
        )


class HmdbMetabolites(Producer):


    variables = ['metabolite']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/metabolites_transformer_info.json')


    def update_transformer_info(self, info):
        info.knowledge_map.nodes['SmallMolecule'].count = metabolite_count()


    def find_names(self, name):
        if self.has_prefix('hmdb', name, self.OUTPUT_CLASS):
            return self.metabolites(find_metabolite_by_hmdb_id(self.de_prefix('hmdb',name,self.OUTPUT_CLASS)))
        elif name.upper().startswith('HMDB'):
            return self.metabolites(find_metabolite_by_hmdb_id(name))
        elif inchikey_regex.match(name) is not None:
            return self.metabolites(find_metabolite_by_inchikey(name))
        else:
            metabolites = self.metabolites(find_metabolite_by_name(name))
            if len(metabolites) != 0:
                return metabolites
            return self.metabolites(find_metabolite_by_synonym(name))


    def metabolites(self, results):
        compounds = []
        for row in results:
            compounds.append(row['METABOLITE_ID'])
        return compounds


    def create_element(self, metabolite_id):
        for row in get_metabolite(metabolite_id):
            primary_name = row['NAME']
            id = self.add_prefix('hmdb', row['ACCESSION'])
        identifiers = self.identifiers(metabolite_id)
        identifiers['hmdb'] = id
        biolink_class = self.biolink_class(self.OUTPUT_CLASS)
        names = self.get_names(metabolite_id, primary_name)
        attributes = self.get_attributes(metabolite_id)
        element = self.Element(id, biolink_class, identifiers, names_synonyms=names, attributes=attributes)
        return element


    def identifiers(self, metabolite_id):
        identifiers = {}
        for row in get_dentifiers(metabolite_id):
            field = self.field_map.get(row['TAG'])
            if field is not None:
                xref = self.add_prefix(field, row['XREF'])
                if field in identifiers:
                    identifiers[field].append(xref)
                else:
                    identifiers[field] = [xref]
        for field in identifiers:
            if len(identifiers[field]) == 1:
                identifiers[field] = identifiers[field][0]
        return identifiers


    def get_names(self, metabolite_id, primary_name):
        synonyms = []
        iupac_name = None
        traditional_iupac = None
        for row in get_synonyms(metabolite_id):
            name = row['NAME']
            name_type = row['NAME_TYPE']
            if name_type == 'iupac_name':
                iupac_name = self.Names(name = name, type='iupac_name')
            elif name_type == 'traditional_iupac':
                traditional_iupac = self.Names(name = name, type='traditional_iupac')
            else:
                synonyms.append(name)
        names = [self.Names(name=primary_name, synonyms=synonyms)]
        if iupac_name is not None:
            names.append(iupac_name)
        if traditional_iupac is not None:
            names.append(traditional_iupac)
        return names


    def get_attributes(self, metabolite_id):
        attributes = []
        for row in get_properties(metabolite_id):
            name = row['KIND'] if row['KIND'] is not None else row['TAG']
            tag = row['TAG'] if row['KIND'] is not None else None
            attribute = self.Attribute(name, row['VALUE'], value_type=tag)
            if row['SOURCE'] is not None:
                subattribute = self.Attribute('property_source',row['SOURCE'])
                attribute.attributes = [subattribute]
            attributes.append(attribute)
        for row in get_taxonomy_properties(metabolite_id):
            attribute = self.Attribute(row['TAG'], row['VALUE'])
            attributes.append(attribute)
        for row in get_taxonomy(metabolite_id):
            attributes.append(self.Attribute('Direct Parent', row['DIRECT_PARENT'], description=row['DESCRIPTION']))
            if row['SUBCLASS'] is not None:
                attributes.append(self.Attribute('Sub Class', row['SUBCLASS']))
            attributes.append(self.Attribute('Taxonomy Class', row['TAXONOMY_CLASS']))
            attributes.append(self.Attribute('Super Class', row['SUPERCLASS']))
            attributes.append(self.Attribute('Kingdom', row['KINGDOM']))
            if row['MOLECULAR_FRAMEWORK'] is not None:
                attributes.append(self.Attribute('Molecular Framework', row['MOLECULAR_FRAMEWORK']))
        for row in get_references(metabolite_id):
            reference = row['REFERENCE']
            pmid = 'PMID:'+str(row['PUBMED_ID']) if row['PUBMED_ID'] is not None else None
            tag = row['TAG']
            if pmid is None:
                attribute = self.Attribute(tag, reference)
            else:
                attribute = self.Attribute(tag, pmid, description=reference)
            attribute.attribute_type_id = 'biolink:publication'
            attributes.append(attribute)
        for row in get_role(metabolite_id):
            attributes.append(self.Attribute('biolink:chemical_role', row['ONTOLOGY_TERM'], description=row['DEFINITION']))
        return attributes


    field_map = { 
        'bigg_id': 'bigg',
        'cas_registry_number': 'cas',
        'chebi_id': 'chebi',
        'drugbank_id': 'drugbank',
        'inchi': 'inchi',
        'inchikey': 'inchikey',
        'kegg_id': 'kegg',
        'pdb_id': 'pdb',
        'pubchem_compound_id': 'pubchem',
        'secondary_accession': 'secondary_hmdb',
        'smiles': 'smiles',
    }


def reference_attribute(transformer, reference):
    if reference['REFERENCE'] is None:
        return None
    pmid = 'PMID:'+str(reference['PUBMED_ID']) if reference['PUBMED_ID'] is not None else None
    name = reference['TAG'] if 'TAG' in reference else 'reference'
    return transformer.Attribute(
        name = name,
        value = pmid if pmid is not None else reference['REFERENCE'],
        type = 'biolink:publication',
        description = reference['REFERENCE'] if pmid is not None else  None
    )


def load_ids(tags):
    id_map = defaultdict(list)
    with open("data/HMDB-term.tsv",'r') as f:
        for line in f:
            row = line.strip().split('\t')
            tag = row[0]
            term = row[1]
            primary_id = row[2]
            primary_name = row[3]
            if tag in tags:
                id_map[term].append({'primary_id': primary_id, 'primary_name': primary_name})
    return id_map


def find_metabolite(transformer, compound):
    if compound.identifiers is not None:
        if 'hmdb' in compound.identifiers and compound.identifiers['hmdb'] is not None:
            hmdb_id = transformer.de_prefix('hmdb',compound.identifiers['hmdb'])
            for metabolite in find_metabolite_by_hmdb_id(hmdb_id):
                return metabolite
        if 'inchikey' in compound.identifiers and compound.identifiers['inchikey'] is not None:
            for metabolite in find_metabolite_by_inchikey(compound.identifiers['inchikey']):
                return metabolite
    return None


connection = sqlite3.connect("data/HMDB.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row


def tag_id(tag):
    query = """
        SELECT TAG_ID
        FROM TAG
        WHERE TAG = ?
    """
    cur = connection.cursor()
    tag_id = None
    cur.execute(query,(tag,))
    for row in cur.fetchall():
        tag_id = row['TAG_ID']
    return tag_id


def metabolite_count():
    query = """
        SELECT COUNT(METABOLITE_ID) AS COUNT
        FROM METABOLITE
    """
    return count(query, 'metabolite_count')


def protein_count():
    query = """
        SELECT COUNT(PROTEIN_ID) AS COUNT
        FROM PROTEIN
    """
    return count(query, 'protein_count')


def target_count():
    query = """
        SELECT COUNT(PROTEIN_MAP_ID) AS COUNT
        FROM PROTEIN_MAP
    """
    return count(query, 'target_count')


def disease_count():
    query = """
        SELECT COUNT(DISEASE_ID) AS COUNT
        FROM DISEASE
    """
    return count(query, 'disease_count')


def indications_count():
    query = """
        SELECT COUNT(DISEASE_MAP_ID) AS COUNT
        FROM DISEASE_MAP
    """
    return count(query, 'indications_count')


def locations_count():
    query = """
        SELECT count(METABOLITE_PROPERTY_ID) AS COUNT
        FROM METABOLITE_PROPERTY
        JOIN PROPERTY ON PROPERTY.PROPERTY_ID = METABOLITE_PROPERTY.PROPERTY_ID
        JOIN TAG ON TAG.TAG_ID = PROPERTY.TAG_ID
        AND TAG IN (
            'cellular_locations',
            'biospecimen_locations',
            'tissue_locations'
        );
    """
    return count(query, 'locations_count')


def pathways_count():
    query = """
        SELECT COUNT(PATHWAY_ID) AS COUNT
        FROM PATHWAY
    """
    return count(query, 'pathways_count')


def pathways_connections_count():
    query = """
        SELECT COUNT(PATHWAY_MAP_ID) AS COUNT
        FROM PATHWAY_MAP
    """
    return count(query, 'pathways_connections_count')


def count(query, prefix):
    cur = connection.cursor()
    cur.execute(query)
    count = -1
    for row in cur.fetchall():
        count = row['COUNT']
    print(prefix, count, sep=': ')
    return count


def get_child_roles(parent_id):
    roles = []
    query = """
        SELECT ONTOLOGY_ID, ONTOLOGY_TERM, DEFINITION, ONTOLOGY_TYPE
        FROM ONTOLOGY
        WHERE ONTOLOGY_PARENT_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(parent_id,))
    for row in cur.fetchall():
        ontology_type = row['ONTOLOGY_TYPE']
        ontology_id = row['ONTOLOGY_ID']
        if ontology_type == 'parent':
            roles.extend(get_child_roles(ontology_id))
        else:
            roles.append({
                'ONTOLOGY_ID': ontology_id,
                'ONTOLOGY_TERM': row['ONTOLOGY_TERM'],
                'DEFINITION' : row['DEFINITION']
            })
    return roles


def get_roles():
    query = """
        SELECT ONTOLOGY_ID
        FROM ONTOLOGY
        WHERE ONTOLOGY_TERM = 'Role'
    """
    parent_id = -1
    cur = connection.cursor()
    cur.execute(query)
    for row in cur.fetchall():
        parent_id = row['ONTOLOGY_ID']
    roles = {}
    for role in get_child_roles(parent_id):
        roles[role['ONTOLOGY_ID']] = role
    return roles


ROLES = get_roles()


def get_role(metabolite_id):
    roles = []
    query = """
        SELECT ONTOLOGY_ID
        FROM ONTOLOGY_MAP
        WHERE METABOLITE_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(metabolite_id,))
    for row in cur.fetchall():
        ontology_id = row['ONTOLOGY_ID']
        if ontology_id in ROLES:
            roles.append(ROLES[ontology_id])
    return roles


INCHIKEY_TAG_ID = tag_id('inchikey')


def find_metabolite_by_hmdb_id(id):
    query = """
        SELECT METABOLITE_ID
        FROM METABOLITE
        WHERE ACCESSION = ?
    """
    cur = connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()


def find_metabolite_by_inchikey(inchikey):
    query = """
        SELECT METABOLITE_ID
        FROM IDENTIFIER
        WHERE XREF = ? AND TAG_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(inchikey, INCHIKEY_TAG_ID))
    return cur.fetchall()


def find_metabolite_by_name(name):
    query = """
        SELECT METABOLITE_ID
        FROM METABOLITE
        WHERE NAME = ? COLLATE NOCASE
    """
    cur = connection.cursor()
    cur.execute(query,(name,))
    return cur.fetchall()


def find_metabolite_by_synonym(synonym):
    query = """
        SELECT METABOLITE_ID
        FROM NAME
        WHERE NAME = ? COLLATE NOCASE
    """
    cur = connection.cursor()
    cur.execute(query,(synonym,))
    return cur.fetchall()


def get_metabolite(metabolite_id):
    query = """
        SELECT ACCESSION, NAME
        FROM METABOLITE
        WHERE METABOLITE_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(metabolite_id,))
    return cur.fetchall()
    

def get_dentifiers(metabolite_id):
    query = """
        SELECT TAG, XREF
        FROM IDENTIFIER
        INNER JOIN TAG ON TAG.TAG_ID = IDENTIFIER.TAG_ID
        WHERE METABOLITE_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(metabolite_id,))
    return cur.fetchall()


def get_synonyms(metabolite_id):
    query = """
        SELECT NAME, NAME_TYPE
        FROM NAME
        WHERE METABOLITE_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(metabolite_id,))
    return cur.fetchall()


def get_properties(metabolite_id):
    query = """
        SELECT TAG, KIND, VALUE, SOURCE
        FROM METABOLITE_PROPERTY
        JOIN PROPERTY ON PROPERTY.PROPERTY_ID = METABOLITE_PROPERTY.PROPERTY_ID
        JOIN TAG ON TAG.TAG_ID = PROPERTY.TAG_ID
        WHERE METABOLITE_ID = ?
        AND TAG IN (
            'description',
            'chemical_formula',
            'average_molecular_weight',
            'monisotopic_molecular_weight',
            'state',
            'experimental_properties',
            'predicted_properties'
        )
    """
    cur = connection.cursor()
    cur.execute(query,(metabolite_id,))
    return cur.fetchall()


def get_taxonomy_properties(metabolite_id):
    query = """
        SELECT TAG, VALUE
        FROM TAXONOMY_PROPERTY
        JOIN PROPERTY ON PROPERTY.PROPERTY_ID = TAXONOMY_PROPERTY.PROPERTY_ID
        JOIN TAG ON TAG.TAG_ID = PROPERTY.TAG_ID
        WHERE METABOLITE_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(metabolite_id,))
    return cur.fetchall()


def get_taxonomy(metabolite_id):
    query = """
        SELECT DESCRIPTION, DIRECT_PARENT, KINGDOM, SUPERCLASS, TAXONOMY_CLASS, SUBCLASS, MOLECULAR_FRAMEWORK
        FROM TAXONOMY
        JOIN TAXONOMY_MAP ON TAXONOMY_MAP.TAXONOMY_ID = TAXONOMY.TAXONOMY_ID
        WHERE METABOLITE_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(metabolite_id,))
    return cur.fetchall()


def get_references(metabolite_id):
    query = """
        SELECT REFERENCE, PUBMED_ID, TAG
        FROM REFERENCE
        JOIN REFERENCE_MAP ON REFERENCE_MAP.REFERENCE_ID = REFERENCE.REFERENCE_ID
        JOIN TAG ON TAG.TAG_ID = REFERENCE_MAP.TAG_ID
        WHERE METABOLITE_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(metabolite_id,))
    return cur.fetchall()



def get_targets(metabolite_id):
    query = """
        SELECT PROTEIN_ACCESSION, PROTEIN_NAME, UNIPROT_ID, GENE_NAME, PROTEIN_TYPE
        FROM PROTEIN_MAP
        JOIN PROTEIN ON PROTEIN.PROTEIN_ID = PROTEIN_MAP.PROTEIN_ID
        WHERE METABOLITE_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(metabolite_id,))
    return cur.fetchall()


def get_disorders(metabolite_id):
    query = """
        SELECT DISEASE.DISEASE_ID, DISEASE, OMIM_ID, DEFINITION
        FROM DISEASE_MAP
        JOIN DISEASE ON DISEASE.DISEASE_ID = DISEASE_MAP.DISEASE_ID
        LEFT JOIN ONTOLOGY ON ONTOLOGY.ONTOLOGY_TERM = DISEASE.DISEASE
        WHERE METABOLITE_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(metabolite_id,))
    return cur.fetchall()


def get_disorder_references(metabolite_id):
    query = """
        SELECT DISEASE_ID, REFERENCE, PUBMED_ID
        FROM DISEASE_REFERENCE_MAP
        JOIN REFERENCE ON REFERENCE.REFERENCE_ID = DISEASE_REFERENCE_MAP.REFERENCE_ID
        WHERE METABOLITE_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(metabolite_id,))
    return cur.fetchall()


def get_locations(metabolite_id):
    query = """
        SELECT TAG, KIND, VALUE, SOURCE, DEFINITION
        FROM METABOLITE_PROPERTY
        JOIN PROPERTY ON PROPERTY.PROPERTY_ID = METABOLITE_PROPERTY.PROPERTY_ID
        JOIN TAG ON TAG.TAG_ID = PROPERTY.TAG_ID
        LEFT JOIN ONTOLOGY ON ONTOLOGY.ONTOLOGY_TERM = PROPERTY.VALUE
        WHERE METABOLITE_ID = ?
        AND TAG IN (
            'cellular_locations',
            'biospecimen_locations',
            'tissue_locations'
        )
    """
    cur = connection.cursor()
    cur.execute(query,(metabolite_id,))
    return cur.fetchall()


def get_concentrations(metabolite_id):
    query = """
        SELECT 
            CONCENTRATION.CONCENTRATION_ID,
            ABNORMAL_CONCENTRATION,
            BIOSPECIMEN,
            CONCENTRATION_VALUE,
            CONCENTRATION_UNITS,
            AGE,
            GENDER,
            SUBJECT_CONDITION,
            PATIENT_INFORMATION,
            COMMENT,
            REFERENCE,
            PUBMED_ID,
            DEFINITION
        FROM CONCENTRATION
        LEFT JOIN CONCENTRATION_REFERENCE_MAP ON CONCENTRATION_REFERENCE_MAP.CONCENTRATION_ID = CONCENTRATION.CONCENTRATION_ID
        LEFT JOIN REFERENCE ON REFERENCE.REFERENCE_ID = CONCENTRATION_REFERENCE_MAP.REFERENCE_ID
        LEFT JOIN ONTOLOGY ON ONTOLOGY.ONTOLOGY_TERM = CONCENTRATION.BIOSPECIMEN
        WHERE CONCENTRATION_VALUE IS NOT NULL
        AND METABOLITE_ID = ?
        ORDER BY CONCENTRATION.CONCENTRATION_ID
    """
    cur = connection.cursor()
    cur.execute(query,(metabolite_id,))
    return cur.fetchall()


def find_pathways(metabolite_id):
    query = """
        SELECT PATHWAY_NAME, SMPDB_ID, KEGG_MAP_ID
        FROM PATHWAY
        JOIN PATHWAY_MAP ON PATHWAY.PATHWAY_ID = PATHWAY_MAP.PATHWAY_ID
        WHERE METABOLITE_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(metabolite_id,))
    return cur.fetchall()
