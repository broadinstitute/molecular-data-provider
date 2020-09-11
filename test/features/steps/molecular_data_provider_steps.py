from behave import given, when, then
from contextlib import closing
import requests
import json


@given('a Molecular Data Provider at "{url}"')
def step_impl(context, url):
    """
    Given a base URL of a transformer
    """
    context.molepro_url = url


@given('the Molecular Data Provider')
def step_impl(context):
    """
    Given the gene-list sharpener
    """
    context.base_url = context.molepro_url
    context.collection_id = ""


@given('a reasoner API at "{url}"')
def step_impl(context, url):
    """
    Given a base URL of a transformer
    """
    context.reasoner_api_url = url


@given('the reasoner API')
def step_impl(context):
    """
    Given the gene-list sharpener
    """
    context.base_url = context.reasoner_api_url


@given('a compound list "{compounds}"')
def step_impl(context, compounds):
    """
    Given a compound list
    """
    url = context.base_url+'/compound/by_name/'+compounds
    print(url)
    with closing(requests.get(url)) as response:
        context.response_json = response.json()
        context.collection_info = response.json()
        print("Collection size ",context.collection_info['size'])


@given('another compound list "{compounds}"')
def step_impl(context, compounds):
    """
    Given a compound list
    """
    url = context.base_url+'/compound/by_name/'+compounds
    print(url)
    with closing(requests.get(url)) as response:
        context.response_json = response.json()
        context.collection_1 = context.collection_info
        context.collection_2 = response.json()
        print("Collection size ",context.collection_2['size'])


@when('we call "{transformer}" transformer with no parameters')
def step_impl(context, transformer):
    """
    This step launches a transformer
    """
    url = context.base_url+'/transform'
    print(url)
    data = {"name":transformer,"collection_id":context.collection_id, "controls":[]}
    print(data)
    with closing(requests.post(url, json=data, stream=False)) as response:
        context.response = response
        context.collection_info = response.json()
        print(context.collection_info)
        context.collection_id = context.collection_info['id']
        with closing(requests.get(context.collection_info['url'])) as collection:
            context.response = collection
            context.response_json = collection.json()


@when('we call "{transformer}" transformer with the following parameters')
def step_impl(context, transformer):
    """
    This step launches a transformer
    """
    url = context.base_url+'/transform'
    print(url)
    controls = []
    values = context.table[0]
    for name in context.table.headings:
        controls.append({"name":name,"value":values[name]})
    data = {"name":transformer,"collection_id":context.collection_id, "controls":controls}
    print(data)
    with closing(requests.post(url, json=data, stream=False)) as response:
        context.response = response
        context.collection_info = response.json()
        print(context.collection_info)
        context.collection_id = context.collection_info['id']
        with closing(requests.get(context.collection_info['url'])) as collection:
            context.response = collection
            context.response_json = collection.json()


@then('the length of the collection should be {size}')
def step_impl(context, size):
    """
    This step checks the size of the response gene list
    """

    print('collection.size =',context.response_json['size'])
    assert context.response_json['size'] == int(size)
    print('collection.size =',len(context.response_json['elements']))
    assert len(context.response_json['elements']) == int(size)


@when('we call aggregator "{aggregator}"')
def step_impl(context, aggregator):
    """
    This step launches an aggregator
    """
    url = context.base_url+'/aggregate'
    print(url)
    data = {"operation":aggregator,"collection_ids":[context.collection_1['id'],context.collection_2['id']]}
    print(data)
    with closing(requests.post(url, json=data, stream=False)) as response:
        context.collection_info = response.json()
        print(context.collection_info)
        context.collection_id = context.collection_info['id']
        with closing(requests.get(context.collection_info['url'])) as collection:
            context.response = collection
            context.response_json = collection.json()


