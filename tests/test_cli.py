#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from threading import Thread
from time import sleep
import unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.dirname(THIS_DIR))
from mae.cli import ExporterServer


class TestCLIServer(unittest.TestCase):

    def setUp(self):
        self.exporter = ExporterServer(0, 'localhost', 0)

    def tearDown(self):
        self.exporter.socket.close()

    def test_mae_cli_1_simple_start(self):
        """
        Test if CLI can just run and start the Exporter server.
        """
        server_thread = Thread(target=self.exporter.serve_forever)
        server_thread.start()
        sleep(5)
        self.assertTrue(server_thread.is_alive)
        self.exporter.shutdown()
        self.exporter.socket.close()

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True)
