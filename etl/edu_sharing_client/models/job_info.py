# coding: utf-8

"""
    edu-sharing Repository REST API

    The public restful API of the edu-sharing repository.  # noqa: E501

    OpenAPI spec version: 1.1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six


class JobInfo(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'start_time': 'int',
        'finish_time': 'int',
        'status': 'str',
        'worst_level': 'Level',
        'log': 'list[LogEntry]',
        'job_detail': 'JobDetail'
    }

    attribute_map = {
        'start_time': 'startTime',
        'finish_time': 'finishTime',
        'status': 'status',
        'worst_level': 'worstLevel',
        'log': 'log',
        'job_detail': 'jobDetail'
    }

    def __init__(self, start_time=None, finish_time=None, status=None, worst_level=None, log=None, job_detail=None):  # noqa: E501
        """JobInfo - a model defined in Swagger"""  # noqa: E501
        self._start_time = None
        self._finish_time = None
        self._status = None
        self._worst_level = None
        self._log = None
        self._job_detail = None
        self.discriminator = None
        if start_time is not None:
            self.start_time = start_time
        if finish_time is not None:
            self.finish_time = finish_time
        if status is not None:
            self.status = status
        if worst_level is not None:
            self.worst_level = worst_level
        if log is not None:
            self.log = log
        if job_detail is not None:
            self.job_detail = job_detail

    @property
    def start_time(self):
        """Gets the start_time of this JobInfo.  # noqa: E501


        :return: The start_time of this JobInfo.  # noqa: E501
        :rtype: int
        """
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        """Sets the start_time of this JobInfo.


        :param start_time: The start_time of this JobInfo.  # noqa: E501
        :type: int
        """

        self._start_time = start_time

    @property
    def finish_time(self):
        """Gets the finish_time of this JobInfo.  # noqa: E501


        :return: The finish_time of this JobInfo.  # noqa: E501
        :rtype: int
        """
        return self._finish_time

    @finish_time.setter
    def finish_time(self, finish_time):
        """Sets the finish_time of this JobInfo.


        :param finish_time: The finish_time of this JobInfo.  # noqa: E501
        :type: int
        """

        self._finish_time = finish_time

    @property
    def status(self):
        """Gets the status of this JobInfo.  # noqa: E501


        :return: The status of this JobInfo.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this JobInfo.


        :param status: The status of this JobInfo.  # noqa: E501
        :type: str
        """
        allowed_values = ["Running", "Failed", "Aborted", "Finished"]  # noqa: E501
        if status not in allowed_values:
            raise ValueError(
                "Invalid value for `status` ({0}), must be one of {1}"  # noqa: E501
                .format(status, allowed_values)
            )

        self._status = status

    @property
    def worst_level(self):
        """Gets the worst_level of this JobInfo.  # noqa: E501


        :return: The worst_level of this JobInfo.  # noqa: E501
        :rtype: Level
        """
        return self._worst_level

    @worst_level.setter
    def worst_level(self, worst_level):
        """Sets the worst_level of this JobInfo.


        :param worst_level: The worst_level of this JobInfo.  # noqa: E501
        :type: Level
        """

        self._worst_level = worst_level

    @property
    def log(self):
        """Gets the log of this JobInfo.  # noqa: E501


        :return: The log of this JobInfo.  # noqa: E501
        :rtype: list[LogEntry]
        """
        return self._log

    @log.setter
    def log(self, log):
        """Sets the log of this JobInfo.


        :param log: The log of this JobInfo.  # noqa: E501
        :type: list[LogEntry]
        """

        self._log = log

    @property
    def job_detail(self):
        """Gets the job_detail of this JobInfo.  # noqa: E501


        :return: The job_detail of this JobInfo.  # noqa: E501
        :rtype: JobDetail
        """
        return self._job_detail

    @job_detail.setter
    def job_detail(self, job_detail):
        """Sets the job_detail of this JobInfo.


        :param job_detail: The job_detail of this JobInfo.  # noqa: E501
        :type: JobDetail
        """

        self._job_detail = job_detail

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(JobInfo, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, JobInfo):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
