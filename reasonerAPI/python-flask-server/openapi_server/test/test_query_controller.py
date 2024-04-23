# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.query import Query  # noqa: E501
from openapi_server.models.response import Response  # noqa: E501
from openapi_server.test import BaseTestCase


class TestQueryController(BaseTestCase):
    """QueryController integration test stubs"""

    def test_query_post(self):
        """Test case for query_post

        Initiate a query and wait to receive a Response
        """
        request_body = None
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/molepro/trapi/v1.4/query',
            method='POST',
            headers=headers,
            data=json.dumps(request_body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
