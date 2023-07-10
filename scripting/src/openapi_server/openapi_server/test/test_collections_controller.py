# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.collection import Collection  # noqa: E501
from openapi_server.models.compound_list import CompoundList  # noqa: E501
from openapi_server.models.error_msg import ErrorMsg  # noqa: E501
from openapi_server.models.gene_list import GeneList  # noqa: E501
from openapi_server.test import BaseTestCase


class TestCollectionsController(BaseTestCase):
    """CollectionsController integration test stubs"""

    def test_collection_collection_id_get(self):
        """Test case for collection_collection_id_get

        Retrieve a collection
        """
        query_string = [('cache', 'cache_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/molecular_data_provider/collection/{collection_id}'.format(collection_id='collection_id_example'),
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_compound_list_list_id_get(self):
        """Test case for compound_list_list_id_get

        Retrieve a compound list
        """
        query_string = [('cache', 'cache_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/molecular_data_provider/compound/list/{list_id}'.format(list_id='list_id_example'),
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_gene_list_list_id_get(self):
        """Test case for gene_list_list_id_get

        Retrieve a gene list
        """
        query_string = [('cache', 'cache_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/molecular_data_provider/gene/list/{list_id}'.format(list_id='list_id_example'),
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
