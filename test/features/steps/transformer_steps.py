from behave import given, when, then
from contextlib import closing
import requests
import jsonpath_rw
import json


@given('a transformer at "{url}"')
def step_impl(context, url):
    """
    Given a base URL of a transformer
    """
    context.transformer_url = url


@given('the transformer')
def step_impl(context):
    """
    Given the gene-list sharpener
    """
    context.base_url = context.transformer_url
    context.gene_list_id = None


@when('we fire "{query}" query')
def step_impl(context, query):
    """
    Fire a knowledge-source query
    """
    url = context.base_url+query
    print('url:',url,'\n')
    with closing(requests.get(url)) as response:
        context.response = response
        context.response_json = response.json()


@when('we fire "{query}" query with the following body')
def step_impl(context, query):
    """
    Fire a knowledge-source query
    """
    url = context.base_url+query
    print('url:',url,'\n')
    with closing(requests.post(url, json=json.loads(context.text))) as response:
        context.response = response
        context.response_json = response.json()


@then('the value of "{path}" should be "{value}"')
def step_impl(context, path, value):
    """
    This step checks value specified by the path
    """
    json_path_expr = jsonpath_rw.parse(path)
    result = json_path_expr.find(context.response_json)
    print(result)
    assert result[0].value == value


@then('the int value of "{path}" should be {value}')
def step_impl(context, path, value):
    """
    This step checks value specified by the path
    """
    json_path_expr = jsonpath_rw.parse(path)
    result = json_path_expr.find(context.response_json)
    print(result)
    assert result[0].value == int(value)


@then('the size of "{path}" should be {size}')
def step_impl(context, path, size):
    """
    This step checks size specified by the path
    """
    json_path_expr = jsonpath_rw.parse(path)
    result = json_path_expr.find(context.response_json)
    print(result)
    print("len = ",len(result[0].value))
    assert len(result[0].value) == int(size)


@then('the response contains the following entries in "{key}" of "{parent}"')
def step_impl(context, key, parent):
    """
    This step checks whether all values specified in the test are contained in the response
    """
    entries = set()
    print('Collected entries:')
    for entry in context.response_json:
        print(' ', entry[parent][key])
        entries.add(entry[parent][key])
    print('Tested entries:')
    for row in context.table:
        print(' ', row[key])
        assert row[key] in entries


@then('the response contains the following entries in "{key}" of "{parent}" array')
def step_impl(context, key, parent):
    """
    This step checks whether all values specified in the test are contained in the response
    """
    entries = set()
    print('Collected entries:')
    for entry in context.response_json:
        for element in entry[parent]:
            if key in element:
                if element[key] not in entries:
                    print(' ', element[key])
                entries.add(element[key])
    print('Tested entries:')
    for row in context.table:
        print(' ', row[key])
        assert row[key] in entries


@then('the response contains the following entries in "{key}"')
def step_impl(context, key):
    """
    This step checks whether all values specified in the test are contained in the response
    """
    entries = set()
    print('Collected entries:')
    for entry in context.response_json:
        print(' ', entry[key])
        entries.add(entry[key])
    print('Tested entries:')
    for row in context.table:
        print(' ', row[key])
        assert row[key] in entries


@then('the response contains "{value}" in "{key}"')
def step_impl(context, key, value):
    """
    This step checks whether all values specified in the test are contained in the response
    """
    entries = set()
    print('Collected entries:')
    for entry in context.response_json:
        print(' ', entry[key])
        entries.add(entry[key])
    print('Tested entry:')
    print(' ', value)
    assert value in entries


@then('the response only contains the following entries in "{key}" of "{parent}"')
def step_impl(context, key, parent):
    """
    This step checks whether all values found in the response are contained in the test table
    """
    entries = set()
    print('Collected entries:')
    for row in context.table:
        print(' ', row[key])
        entries.add(row[key])
    print('Tested entries:')
    for entry in context.response_json:
        print(' ', entry[parent][key])
        assert entry[parent][key] in entries


@then('the response only contains the following entries in "{key}" of "{parent}" array')
def step_impl(context, key, parent):
    """
    This step checks whether all values found in the response are contained in the test table
    """
    entries = set()
    print('Collected entries:')
    for row in context.table:
        print(' ', row[key])
        entries.add(row[key])
    print('Tested entries:')
    for entry in context.response_json:
        for element in entry[parent]:
            print(' ', element[key])
            assert element[key] in entries


@then('the response only contains the following entries in "{key}"')
def step_impl(context, key):
    """
    This step checks whether all values found in the response are contained in the test table
    """
    entries = set()
    print('Collected entries:')
    for row in context.table:
        print(' ', row[key])
        entries.add(row[key])
    print('Tested entries:')
    for entry in context.response_json:
        print(' ', entry[key])
        assert entry[key] in entries


@then('the size of the response is {size}')
def step_impl(context, size):
    """
    This step checks the size of the response
    """
    print("len=",len(context.response_json))
    assert len(context.response_json) == int(size)
