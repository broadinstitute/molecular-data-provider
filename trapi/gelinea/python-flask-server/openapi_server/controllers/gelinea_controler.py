import requests
import logging
import datetime
import json
import yaml
import os

from contextlib import closing

from openapi_server.models.response import Response
from openapi_server.models.node import Node
from openapi_server.models.edge import Edge
from openapi_server.models.message import Message
from openapi_server.models.attribute import Attribute
from openapi_server.models.retrieval_source import RetrievalSource
from openapi_server.models.meta_knowledge_graph import MetaKnowledgeGraph
from openapi_server.models.meta_node import MetaNode
from openapi_server.models.meta_edge import MetaEdge
from openapi_server.models.log_entry import LogEntry
from openapi_server.models.log_level import LogLevel


GELINEA = 'Gene-list network enrichment analysis'
INFORES_GELINEA = RetrievalSource('infores:gelinea', 'primary_knowledge_source')
INFORES_MOLEPRO = RetrievalSource('infores:molepro', 'aggregator_knowledge_source', upstream_resource_ids=['infores:gelinea'])

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(name)s %(threadName)s : %(message)s')
logger = logging.getLogger(__name__)


BASE_URL = 'https://molepro.broadinstitute.org/molecular_data_provider'
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


def colect_genes(knowledge_graph):
    genes = []
    for gene_id in knowledge_graph.nodes.keys():
        genes.append(gene_id)
    return genes


def get_gene_collection(genes):
    url = BASE_URL+'/element/by_id'
    with closing(requests.post(url, json=genes)) as id_response_obj:
        if id_response_obj.status_code != 200:
            return None
        response = id_response_obj.json()
        if response is not None and response.get('size', -1) > 0:
            return response.get('id')
    return None


def run_gelinea(collection_id, pvalue_threshold, logs):
    url = BASE_URL+'/transform?cache=no'
    logs.append(LogEntry(datetime.datetime.now(), LogLevel.INFO, LogLevel.INFO, 'Running GeLiNEA at '+BASE_URL))
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
            logs.append(LogEntry(datetime.datetime.now(), LogLevel.WARNING, str(response_obj.status_code), log_msg))
            return None
        url = BASE_URL+'/collection/'+response_json['id']+'?cache=no'
        with closing(requests.get(url)) as response_obj:
            if response_obj.status_code != 200:
                return {'elements':[]}
            return response_obj.json()        


def add_node(knowledge_graph, node_id, node_name, node_category, attributes = None):
    node = Node(node_name, [node_category], attributes)
    knowledge_graph.nodes[node_id] = node


def add_edge(knowledge_graph, subject, predicate, object, attributes = None):
    edge = Edge(predicate, subject, object, attributes=attributes, sources=[INFORES_GELINEA,INFORES_MOLEPRO])
    knowledge_graph.edges[subject+".."+object] = edge


def add_geneset_node(knowledge_graph, genes, gene_set_id):
    add_node(knowledge_graph, gene_set_id, str(genes), 'biolink:GeneSet')
    for gene in genes:
        add_edge(knowledge_graph, gene, 'biolink:member_of', gene_set_id)


def add_gelinea_results(knowledge_graph, gene_set_id, gelinea):
    for element in gelinea.get('elements',[]):
        element_name = None
        for names in element.get('names_synonyms',[]):
            if element_name is None and names.get('name') is not None:
                element_name = names.get('name')
        attributes = [Attribute.from_dict(attribute) for attribute in element.get('attributes')]
        add_node(knowledge_graph, element['id'], element_name, 'biolink:Pathway', attributes)
        attributes = None
        if 'connections' in element and len(element['connections']) > 0:
            attributes = [Attribute.from_dict(attribute) for attribute in element['connections'][0].get('attributes')]
        add_edge(knowledge_graph, gene_set_id, 'biolink:enriched_in', element['id'], attributes)


def run_enrichment(query_message, logs, pvalue_threshold):
    knowledge_graph = query_message.knowledge_graph
    genes = colect_genes(knowledge_graph)
    msg = 'query: {} genes'.format(len(genes))
    logger.info(msg)
    logs.append(LogEntry(datetime.datetime.now(), LogLevel.INFO, LogLevel.INFO, msg))
    collection_id = get_gene_collection(genes)
    gelinea = run_gelinea(collection_id, pvalue_threshold, logs)
    if len(gelinea.get('elements',[])) > 0:
        gene_set_id = 'GeneSet:' + gelinea['id']
        add_geneset_node(knowledge_graph, genes, gene_set_id)
        add_gelinea_results(knowledge_graph, gene_set_id, gelinea)
    msg = 'response: {} pathway(s)'.format(len(gelinea.get('elements',[])))
    logger.info(msg)
    logs.append(LogEntry(datetime.datetime.now(), LogLevel.INFO, LogLevel.INFO, msg))
    message = Message(query_graph=query_message.query_graph, knowledge_graph=knowledge_graph)
    return message


def run_workflow(query):
    workflow = query.workflow
    logs = []
    if len(workflow) == 1:
        if workflow[0].get('id') == 'enrich_results':
            pvalue_threshold = None
            if 'parameters' in workflow[0]:
                pvalue_threshold = workflow[0]['parameters'].get('pvalue_threshold')
            message = run_enrichment(query.message, logs, pvalue_threshold)
            return Response(message=message, logs=logs, workflow=workflow, schema_version=VERSION_TRAPI, biolink_version=VERSION_BIOLINK)
    else:
        return ({"status": 400, "title": "Bad Request", "detail": "unexpeced workflow, expected lengeth 1", "type": "about:blank"}, 400)


def meta_knowledge_graph():
    nodes = {
        'biolink:Disease': MetaNode(id_prefixes=['MONDO']),
        'biolink:Pathway': MetaNode(id_prefixes=['MSigDB'])
    }
    edges = [MetaEdge(
        subject='biolink:Disease',
        predicate='biolink:enriched_in',
        object='biolink:Pathway',
        knowledge_types=['inferred']
    )]
    return  MetaKnowledgeGraph(nodes, edges)
