from behave import given, when, then
from contextlib import closing
import requests
import jsonpath_rw
import json


def _matches(item, row, headings):
    for h in headings:
        actual = item.get(h)
        if isinstance(actual, list):
            if row[h] not in [str(v) for v in actual]:
                return False
        elif str(actual) != row[h]:
            return False
    return True


def _values(value):
    return value if isinstance(value, list) else [value]


def _as_list(response_json):
    return response_json if isinstance(response_json, list) else [response_json]


def _element_items(context, array):
    for element in _as_list(context.response_json):
        yield from element.get(array, [])


def _connection_items(context, array):
    for connection in _element_items(context, 'connections'):
        yield from connection.get(array, [])


def _assert_contains(items, table):
    items = list(items)
    for row in table:
        print('Tested entry:', dict(row.items()))
        assert any(_matches(item, row, table.headings) for item in items), f'{dict(row.items())} not found'


def _assert_only_contains(items, table):
    for item in items:
        projected = {h: item.get(h) for h in table.headings}
        print('Tested entry:', projected)
        assert any(_matches(item, row, table.headings) for row in table), f'unexpected {projected}'


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
        if response.status_code != 200:
            print(response.status_code, response.reason, response.text)
        context.response = response
        try:
            context.response_json = response.json()
        except ValueError:
            context.response_json = None


@when('we fire "{query}" query with the following body')
def step_impl(context, query):
    """
    Fire a knowledge-source query
    """
    url = context.base_url+query
    print('url:',url,'\n')
    with closing(requests.post(url, json=json.loads(context.text))) as response:
        if response.status_code != 200:
            print(response.status_code, response.reason, response.text)
        context.response = response
        try:
            context.response_json = response.json()
        except ValueError:
            context.response_json = None


@then('the value of "{path}" should be "{value}"')
def step_impl(context, path, value):
    """
    This step checks value specified by the path
    """
    json_path_expr = jsonpath_rw.parse(path)
    result = json_path_expr.find(context.response_json)
    print(result)
    assert result, f'{path} not found'
    assert result[0].value == value


@then('the int value of "{path}" should be {value}')
def step_impl(context, path, value):
    """
    This step checks value specified by the path
    """
    json_path_expr = jsonpath_rw.parse(path)
    result = json_path_expr.find(context.response_json)
    print(result)
    assert result, f'{path} not found'
    assert result[0].value == int(value)


@then('the size of "{path}" should be {size}')
def step_impl(context, path, size):
    """
    This step checks size specified by the path
    """
    json_path_expr = jsonpath_rw.parse(path)
    result = json_path_expr.find(context.response_json)
    print(result)
    assert result, f'{path} not found'
    print("len = ",len(result[0].value))
    assert len(result[0].value) == int(size)


@then('the response contains the following entries in "{key}" of "{parent}"')
def step_impl(context, key, parent):
    """
    This step checks whether all values specified in the test are contained in the response
    """
    entries = set()
    print('Collected entries:')
    for entry in _as_list(context.response_json):
        if parent not in entry or key not in entry[parent]:
            continue
        print(' ', entry[parent][key])
        entries.update(_values(entry[parent][key]))
    print('Tested entries:')
    for row in context.table:
        print(' ', row[key])
        assert row[key] in entries


@then('the response may contain the following entries in "{key}" of "{parent}"')
def step_impl(context, key, parent):
    """
    This step checks whether all values specified in the test are contained in the response
    """
    entries = set()
    print('Collected entries:')
    for entry in context.response_json:
        if key in entry[parent] :
            print(' ', entry[parent][key])
            entries.update(_values(entry[parent][key]))
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
    response_list = context.response_json
    # if response is dict, make it a list for uniform processing
    if isinstance(context.response_json, dict):
        response_list = [context.response_json]
    for entry in response_list:
        for match in jsonpath_rw.parse(parent).find(entry):
            for element in match.value:
                if key in element:
                    for value in _values(element[key]):
                        if value not in entries:
                            print(' ', value)
                        entries.add(value)
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
    for entry in _as_list(context.response_json):
        print(' ', entry[key])
        entries.update(_values(entry[key]))
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
    for entry in _as_list(context.response_json):
        print(' ', entry[key])
        entries.update(_values(entry[key]))
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
    for entry in _as_list(context.response_json):
        if parent not in entry or key not in entry[parent]:
            continue
        print(' ', entry[parent][key])
        for value in _values(entry[parent][key]):
            assert value in entries


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
    response_list = context.response_json
    if isinstance(response_list, dict):
        response_list = [response_list]
    for entry in response_list:
        for match in jsonpath_rw.parse(parent).find(entry):
            for element in match.value:
                if key not in element:
                    continue
                print(' ', element[key])
                for value in _values(element[key]):
                    assert value in entries


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
    for entry in _as_list(context.response_json):
        print(' ', entry[key])
        for value in _values(entry[key]):
            assert value in entries


@then('the size of the response is {size}')
def step_impl(context, size):
    """
    This step checks the size of the response
    """
    print("len=",len(context.response_json))
    assert len(context.response_json) == int(size)


@then('the response status should be {code:d}')
def step_impl(context, code):
    print(context.response.status_code, context.response.text[:500])
    assert context.response.status_code == code


@then('the response contains the following "{array}" of elements')
def step_impl(context, array):
    _assert_contains(_element_items(context, array), context.table)


@then('the response only contains the following "{array}" of elements')
def step_impl(context, array):
    _assert_only_contains(_element_items(context, array), context.table)


@then('the response contains the following "{array}" of connections')
def step_impl(context, array):
    _assert_contains(_connection_items(context, array), context.table)


@then('the response only contains the following "{array}" of connections')
def step_impl(context, array):
    _assert_only_contains(_connection_items(context, array), context.table)


@then('the response does not contain the following entries in "{key}"')
def step_impl(context, key):
    entries = {str(v) for e in _as_list(context.response_json) for v in _values(e.get(key, []))}
    for row in context.table:
        print(' ', row[key])
        assert row[key] not in entries, f'{row[key]} should not be in the response'


@then('the element "{id}" contains the following "{array}"')
def step_impl(context, id, array):
    elements = [e for e in _as_list(context.response_json) if e['id'] == id]
    assert elements, f'element {id} not found'
    _assert_contains((i for e in elements for i in e.get(array, [])), context.table)


@then('the element "{id}" contains the following "{array}" of connections')
def step_impl(context, id, array):
    elements = [e for e in _as_list(context.response_json) if e['id'] == id]
    assert elements, f'element {id} not found'
    _assert_contains((i for e in elements for c in e.get('connections', []) for i in c.get(array, [])), context.table)
