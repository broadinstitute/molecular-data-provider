from behave import given, when, then
from contextlib import closing
import requests
import json


@given('a TRAPI at "{url}"')
def step_impl(context, url):
    """
    Given a base URL of a transformer
    """
    context.reasoner_api_url = url


@given('the TRAPI')
def step_impl(context):
    """
    Given the gene-list sharpener
    """
    context.base_url = context.reasoner_api_url


@then('the response contains the following primary knowledge sources')
def step_impl(context):
    """
    This step checks whether all values specified in the test are contained in the response
    """
    entries = set()
    print('Collected entries:')
    for edge in context.response_json['message']['knowledge_graph']['edges'].values():
        for source in edge['sources']:
            if source['resource_role'] == 'primary_knowledge_source':
                print(' ', source['resource_id'])
                entries.add(source['resource_id'])
    print('Tested entries:')
    for row in context.table:
        print(' ', row["primary_knowledge_source"])
        assert row["primary_knowledge_source"] in entries


