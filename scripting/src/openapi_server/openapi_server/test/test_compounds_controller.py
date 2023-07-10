# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.collection import Collection  # noqa: E501
from openapi_server.models.collection_info import CollectionInfo  # noqa: E501
from openapi_server.models.element import Element  # noqa: E501
from openapi_server.models.error_msg import ErrorMsg  # noqa: E501
from openapi_server.test import BaseTestCase


class TestCompoundsController(BaseTestCase):
    """CompoundsController integration test stubs"""

    def test_compound_by_id_compound_id_get(self):
        """Test case for compound_by_id_compound_id_get

        Retrieve a compound by an id
        """
        query_string = [('cache', 'cache_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/molecular_data_provider/compound/by_id/{compound_id}'.format(compound_id='compound_id_example'),
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_compound_by_id_post(self):
        """Test case for compound_by_id_post

        Retrieve multiple compounds specified by ids
        """
        request_body = ['request_body_example']
        query_string = [('cache', 'cache_example')]
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/molecular_data_provider/compound/by_id',
            method='POST',
            headers=headers,
            data=json.dumps(request_body),
            content_type='application/json',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_compound_by_name_name_get(self):
        """Test case for compound_by_name_name_get

        Retrieve a compound by a name
        """
        query_string = [('cache', 'cache_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/molecular_data_provider/compound/by_name/{name}'.format(name='name_example'),
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_compound_by_name_post(self):
        """Test case for compound_by_name_post

        Retrieve multiple compounds specified by names
        """
        request_body = ['request_body_example']
        query_string = [('cache', 'cache_example')]
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/molecular_data_provider/compound/by_name',
            method='POST',
            headers=headers,
            data=json.dumps(request_body),
            content_type='application/json',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @unittest.skip("text/plain not supported by Connexion")
    def test_compound_by_structure_post(self):
        """Test case for compound_by_structure_post

        Retrieve a compound by a structure
        """
        body = 'body_example'
        query_string = [('cache', 'cache_example')]
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'text/plain',
        }
        response = self.client.open(
            '/molecular_data_provider/compound/by_structure',
            method='POST',
            headers=headers,
            data=json.dumps(body),
            content_type='text/plain',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
