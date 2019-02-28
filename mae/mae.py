#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Mesos App Exporter collects Prometheus metrics from all running executors on a Mesos slave.
"""

from . import __name__, __version__
import json
import logging
import requests
from six.moves.BaseHTTPServer import BaseHTTPRequestHandler

REQUEST_HEADERS = {'User-Agent': '{0}/{1}'.format(__name__, __version__), 'Connection': 'close'}
MESOS_LABEL_ENABLED = 'prometheus.metrics.enabled'
MESOS_LABEL_PORT_INDEX = 'prometheus.metrics.port_index'
MESOS_LABEL_ENDPOINT = 'prometheus.metrics.endpoint'


class MesosAppExporter:
    """
    MesosAppExporter collects metrics from all running Mesos executors.
    """
    def __init__(self, slave_address='localhost', slave_port=5051):
        # type: (str, int) -> None
        """
        Construct a new 'MesosAppExporter' object.

        :param slave_address: Mesos slave process address.
        :param slave_port: Mesos slave process port.
        """
        self.__slave_address = slave_address
        self.__GET_TASKS_PAYLOAD = {'type': 'GET_TASKS'}
        self.__mesos_slave_state = 'http://{0}:{1}/api/v1/state'.format(slave_address, slave_port)
        logging.info('Initialized Mesos App Metrics collector at {}'.format(self.__mesos_slave_state))

    def get_app_metrics_endpoints(self, slave_state=dict()):
        # type: (Dict) -> List
        """
        Derives every Mesos app's metrics endpoints from slave state data.

        :param slave_state: Mesos slave state data.
        """
        tasks = slave_state.get('get_tasks').get('launched_tasks')

        app_metrics_endpoints = list()
        for index, task in enumerate(tasks):
            labels = task.get('labels', {}).get('labels', {})
            label_dict = dict()
            for label in labels:
                label_dict.update({label.get('key'): label.get('value')})

            if MESOS_LABEL_ENABLED in label_dict:
                prom_metrics_port_index = int(label_dict.get(MESOS_LABEL_PORT_INDEX, 0))
                prom_metrics_endpoint = label_dict.get(MESOS_LABEL_ENDPOINT, '/metrics')
                framework_port = tasks[index].get('discovery').get('ports').get('ports')[prom_metrics_port_index].get('number')
                app_metrics_endpoint = 'http://{0}:{1}{2}'.format(self.__slave_address, framework_port, prom_metrics_endpoint)
                app_metrics_endpoints.append(app_metrics_endpoint)

        logging.debug('Got app metrics endpoints from {} apps!'.format(len(app_metrics_endpoints)))
        return app_metrics_endpoints

    def get_metrics(self, endpoints=list()):
        # type: (List) -> str
        """
        Queries each Mesos app's metrics endpoint and returns the combined metrics.

        :param endpoints: List of app metric endpoints.
        """
        combined_metrics = ''
        for index, endpoint in enumerate(endpoints):
            r = requests.get(endpoint, headers=REQUEST_HEADERS)
            app_metrics = r.text
            r.close()
            combined_metrics = '\n'.join([combined_metrics, app_metrics])
        return combined_metrics.strip('\n')

    def get_mesos_slave_state(self):
        # type: (None) -> str
        """
        Queries Mesos slave daemon for its state.
        """
        r = requests.post(self.__mesos_slave_state, json=self.__GET_TASKS_PAYLOAD, headers=REQUEST_HEADERS)
        task_data = r.json()
        r.close()
        return task_data

    def collect(self):
        # type: (None) -> str
        """
        Collects each app's metrics and returns the combined metrics.
        """
        slave_state = self.get_mesos_slave_state()
        endpoints = self.get_app_metrics_endpoints(slave_state)
        combined_metrics = self.get_metrics(endpoints)
        return combined_metrics


def MetricsServer(mesos_slave_address, mesos_slave_port):
    # type: (str, int) -> BaseHTTPRequestHandler
    """
    Metrics HTTP server that servers app metrics for Prometheus to scrape.

    :param mesos_slave_address: Mesos slave process address.
    :param mesos_slave_port: Mesos slave process port.
    """
    class MetricsHTTPHandler(BaseHTTPRequestHandler, object):
        """
        Metrics HTTP handler factory.
        """
        def __init__(self, *args, **kwargs):
            self.server_version = __name__
            self.sys_version = __version__
            self.__mesos_app_exporter = MesosAppExporter(mesos_slave_address, mesos_slave_port)
            super(MetricsHTTPHandler, self).__init__(*args, **kwargs)

        def log_message(self, format, *args):
            return

        def do_GET(self):
            app_metrics = self.__mesos_app_exporter.collect()
            response_body = app_metrics or ''
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(response_body.encode())
            return
    return MetricsHTTPHandler
