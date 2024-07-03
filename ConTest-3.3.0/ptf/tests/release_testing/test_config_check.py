"""
    Copyright 2019 Continental Corporation

    :file: test_config_check.py
    :platform: Windows, Linux
    :synopsis:
        File containing test implementation of checking PTF configuration file
        is fetched properly by UI Controller.
    :author:
        - Praveenkumar G K  <praveenkumar.gomathi.kaliamoorthi@continental-corporation.com>
"""
import os
import sys
import unittest as ut
import argparse
from data_handling import common_utils
from PyQt5 import QtWidgets


# Adding path of the modules used in ptf_asserts to system path for running the test externally
try:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
    sys.path.append(BASE_DIR)
finally:
    pass


class TestPtfConfigEntries(ut.TestCase):
    """ Test Class for checking ConTest configuration file is fetched properly by Project
    configuration"""

    @classmethod
    def setUpClass(cls):
        """
        Set up class method to be executed before all test cases i.e global setup.
        here, creating object of project configuration which is used in below tests.
        """
        cls.test_object = common_utils.store_cfg_data(
            os.path.join(SCRIPT_DIR, 'ConTest_Config.ini'), BASE_DIR)

    def test_verify_config_file_name(self):
        """
        Checking for the configuration file name is correctly fetched
        """
        self.assertEqual(self.test_object.loaded_config,
                         os.path.join(SCRIPT_DIR, 'ConTest_Config.ini'))

    def test_verify_selected_tests(self):
        """
        checking for selected tests are from config is fetched by project configuration
        """
        self.assertEqual(
            self.test_object.selected_tests['selected_tests'],
            ['SWT_SAMPLE_TESTv1__each'])

    @classmethod
    def tearDownClass(cls):
        """
        Method for global tear down.
        """
        # deleting the object
        del cls.test_object


if __name__ == '__main__':
    ut.main(verbosity=2)
