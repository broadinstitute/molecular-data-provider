# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.meta_knowledge_graph import MetaKnowledgeGraph  # noqa: E501
from openapi_server.test import BaseTestCase


class TestMetaKnowledgeGraphController(BaseTestCase):
    """MetaKnowledgeGraphController integration test stubs"""

    def test_meta_knowledge_graph_get(self):
        """Test case for meta_knowledge_graph_get

        Meta knowledge graph representation of this TRAPI web service.
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/molepro/trapi/v1.3/meta_knowledge_graph',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
