# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.aggregation_query import AggregationQuery  # noqa: E501
from openapi_server.models.collection_info import CollectionInfo  # noqa: E501
from openapi_server.models.error_msg import ErrorMsg  # noqa: E501
from openapi_server.models.mole_pro_query import MoleProQuery  # noqa: E501
from openapi_server.models.transformer_info import TransformerInfo  # noqa: E501
from openapi_server.test import BaseTestCase


class TestTransformersController(BaseTestCase):
    """TransformersController integration test stubs"""

    def test_aggregate_post(self):
        """Test case for aggregate_post

        Aggregate multiple collections
        """
        aggregation_query = {}
        query_string = [('cache', 'cache_example')]
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/molecular_data_provider/aggregate',
            method='POST',
            headers=headers,
            data=json.dumps(aggregation_query),
            content_type='application/json',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_transform_post(self):
        """Test case for transform_post

        Transform a list of genes or compounds
        """
        mole_pro_query = {}
        query_string = [('cache', 'cache_example')]
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/molecular_data_provider/transform',
            method='POST',
            headers=headers,
            data=json.dumps(mole_pro_query),
            content_type='application/json',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_transformers_get(self):
        """Test case for transformers_get

        Retrieve a list of transformers
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/molecular_data_provider/transformers',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
