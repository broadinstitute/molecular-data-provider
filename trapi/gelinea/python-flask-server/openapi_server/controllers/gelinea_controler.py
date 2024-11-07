import requests
import logging
import datetime
import json
import yaml
import os

from contextlib import closing
from collections import OrderedDict

from openapi_server.models.analysis import Analysis
from openapi_server.models.async_query_status_response import AsyncQueryStatusResponse
from openapi_server.models.attribute import Attribute
from openapi_server.models.auxiliary_graph import AuxiliaryGraph
from openapi_server.models.edge import Edge
from openapi_server.models.edge_binding import EdgeBinding
from openapi_server.models.knowledge_graph import KnowledgeGraph
from openapi_server.models.log_entry import LogEntry
from openapi_server.models.log_level import LogLevel
from openapi_server.models.message import Message
from openapi_server.models.meta_edge import MetaEdge
from openapi_server.models.meta_knowledge_graph import MetaKnowledgeGraph
from openapi_server.models.meta_node import MetaNode
from openapi_server.models.node import Node
from openapi_server.models.node_binding import NodeBinding
from openapi_server.models.response import Response
from openapi_server.models.result import Result
from openapi_server.models.retrieval_source import RetrievalSource


GELINEA = 'Gene-list network enrichment analysis'
INFORES_GELINEA = 'infores:gelinea'
INFORES_GELINEA_SOURCE = RetrievalSource(INFORES_GELINEA, 'primary_knowledge_source')
INFORES_MOLEPRO_SOURCE = RetrievalSource('infores:molepro', 'aggregator_knowledge_source', upstream_resource_ids=[INFORES_GELINEA])
GENE_SET_AUX_GRAPH = 'gene_set_aux_graph'

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(name)s %(threadName)s : %(message)s')
logger = logging.getLogger(__name__)


BASE_URL = 'https://molepro.transltr.io/molecular_data_provider'
MOLEPRO_BASE_URL = os.environ.get('GELINEA_MOLEPRO_BASE_URL')
if MOLEPRO_BASE_URL:
    BASE_URL = MOLEPRO_BASE_URL
logger.info("using molepro base URL: {}".format(BASE_URL))

# read trapi and biolink versions
VERSION_BIOLINK = 0.1
VERSION_TRAPI = 1.0
with open("./openapi_server/openapi/openapi.yaml", "r") as stream:
    try:
        map_openapi = yaml.safe_load(stream)
        VERSION_BIOLINK = map_openapi.get('info').get('x-translator').get('biolink-version')
        VERSION_TRAPI = map_openapi.get('info').get('x-trapi').get('version')
    except yaml.YAMLError as exc:
        print(exc)
logger.info("Using biolink version: {} and trapi version: {}".format(VERSION_BIOLINK, VERSION_TRAPI))


def now():
    return str(datetime.datetime.now())

def load_biolink_hierarchy():
    with open('conf/biolink_hierarchy.json') as json_file:
        hierarchy = json.load(json_file)
        hierarchy['biolink_class_set'] = set()
        for key, item in hierarchy['biolink_class_parents'].items():
            hierarchy['biolink_class_set'].add(key)
            hierarchy['biolink_class_set'].update(item)
        hierarchy['biolink_predicate_set'] = set()
        for key, item in hierarchy['biolink_predicate_parents'].items():
            hierarchy['biolink_predicate_set'].add(key)
            hierarchy['biolink_predicate_set'].update(item)
        return hierarchy


BIOLINK_HIERARCHY = load_biolink_hierarchy()


class GeLiNEA_Query:

    workflow = None
    knowledge_graph = None
    genes = []
    pvalue_threshold = 0.01
    query_graph = None
    query_map = None
    logs = None
    match_class = True
    match_predicate = True


    def __init__(self, query, logs = None):
        self.logs = logs if logs is not None else []
        self.workflow = query.workflow
        self.query_graph = query.message.query_graph
        if self.workflow is not None and len(self.workflow) == 1:
            operation = self.workflow[0].get('id')
            if operation == 'enrich_results':
                self.parse_enrich_query(query, self.workflow[0]['parameters'])
                return
            if operation != 'lookup':
                self.logs.append(LogEntry(now(), LogLevel.ERROR, LogLevel.ERROR, 'Unknown operation: '+operation))
        self.parse_query_graph(query.message.query_graph)


    def parse_enrich_query(self, query, parameters):
        self.knowledge_graph = query.message.knowledge_graph
        self.genes = self.colect_genes(self.knowledge_graph)
        self.pvalue_threshold = parameters.get('pvalue_threshold')


    def parse_query_graph(self, query_graph):
        node_count = len(query_graph.nodes) if query_graph.nodes is not None else -1
        edge_count = len(query_graph.edges) if query_graph.edges is not None else -1
        msg =  'Query with {} nodes and {} edges'.format(node_count, edge_count)
        logger.info(msg)
        self.logs.append(LogEntry(now(), LogLevel.INFO, LogLevel.INFO, msg))
 
        if node_count != 2 or edge_count != 1:
            return

        for key, item in query_graph.edges.items():
            edge_id = key
            edge = item

        subject_node = None
        for key, node in query_graph.nodes.items():
            if node.set_interpretation == 'MANY':
                subject_id = key
                subject_node = node
            else:
                object_id = key
                object_node = node

        if subject_node is None:
            msg = 'No suitable set interpretation found in query graph'
            logger.warn(msg)
            self.logs.append(LogEntry(now(), LogLevel.WARNING, LogLevel.WARNING, msg))
            return
        set_id = None
        if subject_node.ids is not None:
            for id in subject_node.ids:
                set_id = id
                break

        self.knowledge_graph = KnowledgeGraph(nodes={}, edges={})
        self.query_map = {
            'edge_id':edge_id, 'edge':edge, 'set_id':set_id,
            'subject_id':subject_id, 'subject':subject_node, 
            'object_id':object_id, 'object':object_node
        }
        if object_node.categories is not None:
            self.match_class = False
            for category in object_node.categories:
                if category in BIOLINK_HIERARCHY['biolink_class_set']:
                    self.match_class = True
                    break
        if not self.match_class:
            msg = 'No suitable class found in query graph'
            logger.warn(msg)
            self.logs.append(LogEntry(now(), LogLevel.WARNING, LogLevel.WARNING, msg))
        if edge.predicates is not None:
            self.match_predicate = False
            for predicate in edge.predicates:
                if predicate in BIOLINK_HIERARCHY['biolink_predicate_set']:
                    self.match_predicate = True
                    break
        if not self.match_predicate:
            msg = 'No suitable predicate found in query graph'
            logger.warn(msg)
            self.logs.append(LogEntry(now(), LogLevel.WARNING, LogLevel.WARNING, msg))
        self.genes = subject_node.member_ids


    def colect_genes(self, knowledge_graph):
        genes = []
        for gene_id in knowledge_graph.nodes.keys():
            genes.append(gene_id)
        return genes


class GeLiNEA:

    response = None

    def __init__(self):
        response = None


    def run(self, query):
        response = GeLiNEA_Response(query)
        collection = self.get_gene_collection(query.genes, response.logs)
        if collection is not None and query.match_class and query.match_predicate:
            response.add_query_nodes(collection)
            collection_id = collection.get('id')
            gelinea = self.run_gelinea(collection_id, query.pvalue_threshold, response.logs)
            if len(gelinea.get('elements',[])) > 0:
                response.add_gelinea_results(gelinea)
            msg = 'response: {} pathway(s)'.format(len(gelinea.get('elements',[])))
            logger.info(msg)
            response.logs.append(LogEntry(now(), LogLevel.INFO, LogLevel.INFO, msg))
        return response.response()



    def get_gene_collection(self, genes, logs):
        msg = 'query: {} genes'.format(len(genes))
        logger.info(msg)
        logs.append(LogEntry(now(), LogLevel.INFO, LogLevel.INFO, msg))
        url = BASE_URL+'/element/by_id'
        with closing(requests.post(url, json=genes)) as id_response_obj:
            if id_response_obj.status_code != 200:
                return None
            response = id_response_obj.json()
            if response is not None and response.get('size', -1) > 0:
                collection_id = response.get('id')
                url = BASE_URL+'/collection/'+collection_id+'?cache=yes'
                with closing(requests.get(url)) as response_obj:
                    if response_obj.status_code == 200:
                        return response_obj.json()
        return None


    def run_gelinea(self, collection_id, pvalue_threshold, logs):
        url = BASE_URL+'/transform?cache=no'
        logs.append(LogEntry(now(), LogLevel.INFO, LogLevel.INFO, 'Running GeLiNEA at '+BASE_URL))
        with open('conf/gelinea_controls.json') as json_file:
            controls = json.load(json_file)
        if pvalue_threshold is not None:
            controls.append({'name':'maximum p-value', 'value': pvalue_threshold})
        query = {
            'name': GELINEA,
            'collection_id': collection_id,
            'controls': controls
        }
        with closing(requests.post(url, json=query)) as response_obj:
            response_json = response_obj.json()
            if response_obj.status_code != 200:
                log_msg = "failed querying GeLiNEA transformer at {} with {}".format(url, response_obj.status_code)
                logger.error(log_msg)
                logs.append(LogEntry(now(), LogLevel.WARNING, str(response_obj.status_code), log_msg))
                return None
            url = BASE_URL+'/collection/'+response_json['id']+'?cache=no'
            with closing(requests.get(url)) as response_obj:
                if response_obj.status_code != 200:
                    return {'elements':[]}
                return response_obj.json()


class GeLiNEA_Response:

    logs = None
    workflow = None
    query_graph = None
    knowledge_graph = None
    query_map = None
    gene_map = None
    aux_graphs = None
    results = None

    def __init__(self, query):
        self.logs = query.logs
        self.workflow = query.workflow
        self.query_graph = query.query_graph
        self.knowledge_graph = query.knowledge_graph
        self.query_map = query.query_map
        self.results = []
        self.gene_map = OrderedDict()
        for gene in query.genes:
            self.gene_map[gene] = ''


    def add_query_nodes(self, collection):
        if collection is not None:
            nodes = self.knowledge_graph.nodes
            for element in collection.get('elements',[]):
                element_id = element.get('id')
                element_name = get_element_name(element)
                element_category = element.get('biolink_class')
                if not element_category.startswith('biolink:'):
                    element_category = 'biolink:' + element_category
                if element_id not in nodes:
                    self.add_node(element_id, element_name, element_category)
                for query_id in get_query_ids(element):
                    if self.gene_map.get(query_id) == '':
                        self.gene_map[query_id] = element_id
        else:
            msg = 'failed to obtain query nodes'
            logger.warn(msg)
            self.logs.append(LogEntry(now(), LogLevel.WARNING, LogLevel.WARNING, msg))


    def add_gelinea_results(self, gelinea):
        gene_set_id = 'GeneSet:' + gelinea['id']
        if self.query_map is not None and 'set_id' in self.query_map:
            gene_set_id = self.query_map['set_id']
        aux_graph = self.add_geneset_node(gene_set_id)
        results = []
        for element in gelinea.get('elements',[]):
            element_name = get_element_name(element)
            attributes = [Attribute.from_dict(attribute) for attribute in element.get('attributes')]
            self.add_node(element['id'], element_name, 'biolink:Pathway', attributes)
            attributes = []
            if 'connections' in element and len(element['connections']) > 0:
                for attribute in element['connections'][0].get('attributes'):
                    attributes.append(Attribute.from_dict(attribute))
                    if attribute.get('attribute_type_id') == 'biolink:adjusted_p_value':
                        pvalue = float(attribute.get('value'))
            edge_id = self.add_edge(gene_set_id, 'biolink:enriched_in', element['id'], attributes)
            if self.query_map:
                results.append(self.get_result(element, edge_id, gene_set_id, pvalue))
        if self.query_map:
            self.results = results
            self.aux_graphs = {GENE_SET_AUX_GRAPH: aux_graph}


    def get_attributes(self, attributes):
        if attributes is None:
            attributes = []
        for attribute in attributes:
            if attribute.attributes is None:
                attribute.attributes = []
        return attributes

    def add_node(self, node_id, node_name, node_category, attributes = None, is_set = None):
        attributes = self.get_attributes(attributes)
        node = Node(node_name, [node_category], attributes = attributes, is_set = is_set)
        self.knowledge_graph.nodes[node_id] = node


    def add_edge(self, subject, predicate, object, attributes = None):
        attributes = self.get_attributes(attributes)
        edge = Edge(predicate, subject, object, attributes=attributes, sources=[INFORES_GELINEA_SOURCE,INFORES_MOLEPRO_SOURCE])
        edge_id = subject+".."+object
        self.knowledge_graph.edges[edge_id] = edge
        return edge_id


    def add_geneset_node(self, gene_set_id):
        aux_graph = []
        genes = [self.gene_map[gene] for gene in self.gene_map if self.gene_map[gene] != '']
        self.add_node(gene_set_id, str(genes), 'biolink:Gene', is_set=True)
        for gene in genes:
            edge_id = self.add_edge(gene, 'biolink:member_of', gene_set_id)
            aux_graph.append(edge_id)
        return AuxiliaryGraph(edges=aux_graph, attributes=[])


    def get_result(self, element, edge_id, gene_set_id, pvalue):
        node_bindings = { 
            self.query_map['subject_id']: [NodeBinding(id=gene_set_id, attributes=[])],
            self.query_map['object_id']: [NodeBinding(id=element['id'], attributes=[])]
        }
        edge_bindings = {
            self.query_map['edge_id']: [EdgeBinding(id=edge_id, attributes=[])]
        }
        score = 1 - pvalue if pvalue is not None else None
        analysis = Analysis(resource_id=INFORES_GELINEA, score=score, edge_bindings=edge_bindings, support_graphs=[GENE_SET_AUX_GRAPH],)
        return Result(node_bindings=node_bindings, analyses=[analysis])


    def response(self):
        message = Message(self.results, self.query_graph, self.knowledge_graph, self.aux_graphs)
        return Response(message=message, status='Success', description='Success, {} results found'.format(len(self.results)), 
                        logs=self.logs, workflow=self.workflow, 
                        schema_version=VERSION_TRAPI, biolink_version=VERSION_BIOLINK)


def get_query_ids(element):
    query_ids = []
    for attribute in element.get('attributes',[]):
        if attribute.get('original_attribute_name') == 'query name' and attribute.get('value') is not None:
            query_ids.append(attribute.get('value'))
    return query_ids


def get_element_name(element):
    element_name = None
    for names in element.get('names_synonyms',[]):
        if element_name is None and names.get('name') is not None:
            element_name = names.get('name')
    return element_name


def run_workflow(query):
    gelinea_query = GeLiNEA_Query(query)
    gelinea = GeLiNEA()
    response = gelinea.run(gelinea_query)
    return response


async def async_run_workflow(query, job_id, callback_url):
    msg = 'Job {} running'.format(job_id)
    logger.info(msg)
    logs = [LogEntry(now(), LogLevel.INFO, LogLevel.INFO, msg)]
    try:
        gelinea_query = GeLiNEA_Query(query, logs)
        logs = gelinea_query.logs
        if gelinea_query.genes is not None:
            gelinea = GeLiNEA()
            response = gelinea.run(gelinea_query)
            with closing(requests.post(callback_url, json=response.to_dict())) as response_obj:
                logger.info('results submitted to {} ({})'.format(callback_url, response_obj.status_code))
        else:
            response = Response(
                message=query.message, 
                status='Failed', 
                description='Failed, 400 Bad Request', 
                logs=logs, 
                workflow=query.workflow, 
                schema_version=VERSION_TRAPI, 
                biolink_version=VERSION_BIOLINK
            )
            with closing(requests.post(callback_url, json=response.to_dict())) as response_obj:
                logger.info('results submitted to {} ({})'.format(callback_url, response_obj.status_code))
    except Exception as e:
        err_msg = 'GeLiNEA failed: '+str(e)
        logs.append(LogEntry(now(), LogLevel.ERROR, LogLevel.ERROR, err_msg))
        logger.error(err_msg)
        response = Response(
            message=query.message, 
            status='Failed', 
            description=err_msg, 
            logs=logs, 
            workflow=query.workflow, 
            schema_version=VERSION_TRAPI, 
            biolink_version=VERSION_BIOLINK
        )
        with closing(requests.post(callback_url, json=response.to_dict())) as response_obj:
            logger.info('results submitted to {} ({})'.format(callback_url, response_obj.status_code))
    if os.path.exists('jobs/{}'.format(job_id)):
        os.remove('jobs/{}'.format(job_id))
    msg = 'Job {} finished'.format(job_id)
    logger.info(msg)


def async_query_status(job_id):
    status = 'Completed'
    description = 'job completed'
    if os.path.exists('jobs/{}'.format(job_id)):
        status = 'Running'
        description = 'job running'
    logs = [
        LogEntry(now(), LogLevel.INFO, LogLevel.INFO, description)
    ]
    return AsyncQueryStatusResponse(status=status, description=description, logs=logs)


def meta_knowledge_graph():
    nodes = {
        'biolink:Gene': MetaNode(id_prefixes=['NCBIGene','HGNC']),
        'biolink:Pathway': MetaNode(id_prefixes=['MSigDB'])
    }
    edges = [MetaEdge(
        subject='biolink:Gene',
        predicate='biolink:enriched_in',
        object='biolink:Pathway',
        knowledge_types=['inferred']
    )]
    return  MetaKnowledgeGraph(nodes, edges)
