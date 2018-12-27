#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from mock import Mock, patch
import os
import requests
import sys
import unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.dirname(THIS_DIR))
from mae.mae import MesosAppExporter


class TestMesosAppExporter(unittest.TestCase):
    def __readFile(self, filename):
        with open('{0}/{1}'.format(THIS_DIR, filename)) as file:
            data = file.read()
        return data

    def __readJsonFile(self, filename):
        return json.loads(self.__readFile(filename))

    def __mock_response(self, status=200, content='CONTENT', json_data=None, raise_for_status=None):
        """
        since we typically test a bunch of different
        requests calls for a service, we are going to do
        a lot of mock responses, so its usually a good idea
        to have a helper function that builds these things
        """
        mock_resp = Mock()
        # mock raise_for_status call w/optional error
        mock_resp.raise_for_status = Mock()
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        # set status code and content
        mock_resp.status_code = status
        mock_resp.content = content
        mock_resp.text = content
        # add json data if provided
        if json_data:
            mock_resp.json = Mock(
                return_value=json_data
            )
        return mock_resp

    def setUp(self):
        self.exporter = MesosAppExporter('localhost', 5051)

    def tearDown(self):
        pass

    def test_mae_get_endpoint_1_single_task(self):
        """
        Test if task data with a single matching app is picked up.
        """
        task_data = self.__readJsonFile('fixtures/task_data_1.json')
        endpoints = self.exporter.get_app_metrics_endpoints(task_data)
        self.assertEqual(len(endpoints), 1)
        self.assertEqual(endpoints[0], 'http://localhost:31065/metrics')

    def test_mae_get_endpoint_2_multiple_tasks(self):
        """
        Test if task data with 2 matching apps are picked up.
        Also test if both default and custom labels (endpoint and port index) work.
        """
        task_data = self.__readJsonFile('fixtures/task_data_2.json')
        endpoints = self.exporter.get_app_metrics_endpoints(task_data)
        self.assertEqual(len(endpoints), 2)
        self.assertEqual(endpoints[0], 'http://localhost:31521/metrics')
        self.assertEqual(endpoints[1], 'http://localhost:31065/prometheus')

    def test_mae_get_endpoint_3_no_matching_tasks(self):
        """
        Test if task data without any matching apps are correctly parsed.
        """
        task_data = self.__readJsonFile('fixtures/task_data_3.json')
        endpoints = self.exporter.get_app_metrics_endpoints(task_data)
        self.assertEqual(len(endpoints), 0)

    @patch('requests.get')
    def test_get_metrics_1_single_app(self, mock_request):
        """
        Test if app metrics from a single app is returned correctly.
        """
        fixture = self.__readFile('fixtures/app_metrics_1.txt')
        mock_resp = self.__mock_response(content=fixture)
        mock_request.return_value = mock_resp
        response = self.exporter.get_metrics(['http://localhost:6666/metrics'])
        self.assertEqual(response, fixture)

    @patch('requests.get')
    def test_get_metrics_2_multiple_apps(self, mock_request):
        """
        Test if app metrics from multiple apps are returned correctly.
        """
        fixtures = [self.__readFile('fixtures/app_metrics_2a.txt'), self.__readFile('fixtures/app_metrics_2b.txt')]
        mock_request.side_effect = iter([self.__mock_response(content=fixture) for fixture in fixtures])
        response = self.exporter.get_metrics(['http://localhost:6666/metrics', 'http://localhost:6667/metrics'])
        self.assertEqual(response, self.__readFile('fixtures/app_metrics_2_combined.txt'))

if __name__ == '__main__':
    unittest.main()
