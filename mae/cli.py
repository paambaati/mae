#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
from os import environ
from six.moves.BaseHTTPServer import HTTPServer
from sys import stdout

from mae import MetricsServer

logging.basicConfig(stream=stdout, level=environ.get('LOG_LEVEL', logging.INFO))

MESOS_SLAVE_ADDRESS = 'localhost'
MESOS_SLAVE_PORT = 5051
APP_PORT = 8888


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
        server = HTTPServer(('', args.app_port), MetricsServer(args.slave_address, args.slave_port))
        logging.info('Started Mesos app exporter for Prometheus on port {}'.format(args.app_port))
        server.serve_forever()

    except KeyboardInterrupt:
        logging.warning('Ctrl + C received, shutting down the Mesos app exporter for Prometheus...')
        server.socket.close()

if __name__ == '__main__':
    main()
