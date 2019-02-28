#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
from os import environ
from six.moves.BaseHTTPServer import HTTPServer
from sys import stdout

from .mae import MetricsServer

logging.basicConfig(stream=stdout, level=environ.get('LOG_LEVEL', logging.INFO))

MESOS_SLAVE_ADDRESS = 'localhost'
MESOS_SLAVE_PORT = 5051
APP_PORT = 8888


def ExporterServer(app_port=APP_PORT, slave_address=MESOS_SLAVE_ADDRESS, slave_port=MESOS_SLAVE_PORT):
    # type: (int, str, int) -> HTTPServer
    """
    Returns the exporter as a HTTPServer instance.

    :param app_port: Port the exporter will listen on.
    :param slave_address: Mesos slave address.
    :param slave_port: Mesos slave port.
    """
    exporter = HTTPServer(('', app_port), MetricsServer(slave_address, slave_port))
    logging.info('Starting Mesos app exporter for Prometheus on port {0} and listening to Mesos slave at {1}:{2}'.format(exporter.server_port, slave_address, slave_port))
    return exporter


def main():
    """
    Runs a Prometheus exporter as a HTTP server.
    The default loging level can be overridden with the `LOG_LEVEL` environment variable.
    """
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('app_port', help='Port on which this exporter will run on', default=APP_PORT, type=int)
        parser.add_argument('slave_address', help='Mesos slave address', default=MESOS_SLAVE_ADDRESS)
        parser.add_argument('slave_port', help='Mesos slave port', default=MESOS_SLAVE_PORT, type=int)
        args = parser.parse_args()
        server = ExporterServer(**vars(args))
        server.serve_forever()

    except KeyboardInterrupt:
        logging.warning('Ctrl + C received, shutting down the Mesos app exporter for Prometheus...')
        server.shutdown()
        server.socket.close()

if __name__ == '__main__':
    main()
