# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.log_level import LogLevel
from openapi_server import util

from openapi_server.models.log_level import LogLevel  # noqa: E501

class LogEntry(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, timestamp=None, level=None, code=None, message=None):  # noqa: E501
        """LogEntry - a model defined in OpenAPI

        :param timestamp: The timestamp of this LogEntry.  # noqa: E501
        :type timestamp: datetime
        :param level: The level of this LogEntry.  # noqa: E501
        :type level: LogLevel
        :param code: The code of this LogEntry.  # noqa: E501
        :type code: str
        :param message: The message of this LogEntry.  # noqa: E501
        :type message: str
        """
        self.openapi_types = {
            'timestamp': datetime,
            'level': LogLevel,
            'code': str,
            'message': str
        }

        self.attribute_map = {
            'timestamp': 'timestamp',
            'level': 'level',
            'code': 'code',
            'message': 'message'
        }

        self._timestamp = timestamp
        self._level = level
        self._code = code
        self._message = message

    @classmethod
    def from_dict(cls, dikt) -> 'LogEntry':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The LogEntry of this LogEntry.  # noqa: E501
        :rtype: LogEntry
        """
        return util.deserialize_model(dikt, cls)

    @property
    def timestamp(self):
        """Gets the timestamp of this LogEntry.

        Timestamp in ISO 8601 format  # noqa: E501

        :return: The timestamp of this LogEntry.
        :rtype: datetime
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        """Sets the timestamp of this LogEntry.

        Timestamp in ISO 8601 format  # noqa: E501

        :param timestamp: The timestamp of this LogEntry.
        :type timestamp: datetime
        """

        self._timestamp = timestamp

    @property
    def level(self):
        """Gets the level of this LogEntry.


        :return: The level of this LogEntry.
        :rtype: LogLevel
        """
        return self._level

    @level.setter
    def level(self, level):
        """Sets the level of this LogEntry.


        :param level: The level of this LogEntry.
        :type level: LogLevel
        """

        self._level = level

    @property
    def code(self):
        """Gets the code of this LogEntry.

        One of a standardized set of short codes e.g. QueryNotTraversable, KPNotAvailable, KPResponseMalformed  # noqa: E501

        :return: The code of this LogEntry.
        :rtype: str
        """
        return self._code

    @code.setter
    def code(self, code):
        """Sets the code of this LogEntry.

        One of a standardized set of short codes e.g. QueryNotTraversable, KPNotAvailable, KPResponseMalformed  # noqa: E501

        :param code: The code of this LogEntry.
        :type code: str
        """

        self._code = code

    @property
    def message(self):
        """Gets the message of this LogEntry.

        A human-readable log message  # noqa: E501

        :return: The message of this LogEntry.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """Sets the message of this LogEntry.

        A human-readable log message  # noqa: E501

        :param message: The message of this LogEntry.
        :type message: str
        """

        self._message = message
