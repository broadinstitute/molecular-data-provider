# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.element import Element  # noqa: E501
from openapi_server.models.error_msg import ErrorMsg  # noqa: E501
from openapi_server.models.transformer_info import TransformerInfo  # noqa: E501
from openapi_server.models.transformer_query import TransformerQuery  # noqa: E501
from openapi_server.test import BaseTestCase


class TestTransformersController(BaseTestCase):
    """TransformersController integration test stubs"""

    def test_service_transform_post(self):
        """Test case for service_transform_post

        Transform a list of genes or compounds
        """
        transformer_query = {}
        query_string = [('cache', 'cache_example')]
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/uniprot/{service}/transform'.format(service='service_example'),
            method='POST',
            headers=headers,
            data=json.dumps(transformer_query),
            content_type='application/json',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_service_transformer_info_get(self):
        """Test case for service_transformer_info_get

        Retrieve transformer info
        """
        query_string = [('cache', 'cache_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/uniprot/{service}/transformer_info'.format(service='service_example'),
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
