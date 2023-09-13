# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.async_query import AsyncQuery  # noqa: E501
from openapi_server.models.async_query_response import AsyncQueryResponse  # noqa: E501
from openapi_server.test import BaseTestCase


class TestAsyncqueryController(BaseTestCase):
    """AsyncqueryController integration test stubs"""

    def test_asyncquery_post(self):
        """Test case for asyncquery_post

        Initiate a query with a callback to receive the response
        """
        request_body = None
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/molepro/trapi/v1.4/asyncquery',
            method='POST',
            headers=headers,
            data=json.dumps(request_body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
