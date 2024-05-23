# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.async_query_status_response import AsyncQueryStatusResponse  # noqa: E501
from openapi_server.test import BaseTestCase


class TestAsyncqueryStatusController(BaseTestCase):
    """AsyncqueryStatusController integration test stubs"""

    def test_asyncquery_status(self):
        """Test case for asyncquery_status

        Retrieve the current status of a previously submitted asyncquery given its job_id
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/gelinea-trapi/v1.5/asyncquery_status/{job_id}'.format(job_id='rXEOAosN3L'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
