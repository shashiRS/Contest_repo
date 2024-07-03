"""
Unittest file for goepel common tool utility
Copyright 2020 Continental Corporation

:file: test_goepel_common.py
:platform: Linux, Windows
:synopsis: File containing Unittest for goepel common tool utility.
           Test cases for testing the goepel common related utilities.
:author: Christopher Mirajkar <Christopher.Charles.Mirajkar@continental-corporation.com>
"""

import sys
import os
import unittest
from unittest.mock import patch
import pytest

# Positional arguments are set based on the patch decorators for each test-case.
# These arguments are not called directly but their functions are used within test-cases.
# Disabling the PyLint warning for 'unused arguments' is just for having better code rating.
# Also ignoring similar error for arguments used in setUpClass
# pylint: disable=unused-argument, arguments-differ, invalid-name

# Adding path of the modules used in power_control.py to system path for running the test externally
try:
    CWD = os.path.dirname(__file__)
    BASE_DIR = os.path.abspath(os.path.join(CWD, '..', '..', '..'))
    sys.path.append(os.path.abspath(os.path.join(BASE_DIR, '..')))
    sys.path.append(os.path.join(BASE_DIR, 'tool_utils'))
    from ptf.tools_utils.goepel import goepel_common
finally:
    pass


class MockDLL:
    """
    Dummy class with no realtime functions only for testing purpose. Loaded dll libraries in the
    Goepel Common module is mocked and returned with this class.
    """
    def __init__(self):
        """
        Creates a new instance
        """
        self.value = str(1).encode('utf-8')

    def __len__(self):
        return 1

    @staticmethod
    def G_Common_OpenInterface(interface_name, ctypes_byref):
        """
        This a dummy method for testing, so that check_return_code method raises no error

        :return: returns 0 which is G_NO_ERROR
        """
        return 0

    @staticmethod
    def G_GetLastErrorDescription():
        """
        This a dummy method for testing

        :return: returns 1 as error description
        """
        return 1

    @staticmethod
    def G_GetLastErrorCode():
        """
        This a dummy method for testing

        :return: returns 1 as error last code
        """
        return 1

    @staticmethod
    def G_Common_CloseInterface(port_handle_value):
        """
        This a dummy method for testing
        """
        return

    @staticmethod
    def G_Common_GetFirmwareVersion(port_handle_value, buffer, ctypes_byref):
        """
        This a dummy method for testing, so that check_return_code method raises no error

        :return: returns 0 which is G_NO_ERROR
        """
        return 0


@pytest.mark.skipif(sys.platform != 'win32', reason="Executed only on Windows platform")
class TestGoepelCommon(unittest.TestCase):
    """ A class for testing Goepel Common module"""

    @classmethod
    @patch('ctypes.cdll.LoadLibrary', return_value=MockDLL())
    def setUpClass(cls, mock_ctypes):
        """
        Set up class method to be executed before all test cases i.e global setup.
        """
        cls.test_object = goepel_common.GoepelCommon()

    def test_open_interface(self):
        """
        Method for testing the functionality of GoepelCommon.open_interface
        Testing successful execution
        """
        interface_name = "Test_CAN"
        expected_output = "Communication port opened with interface name '{}'".format(
            interface_name)
        with self.assertLogs('G_API', 'INFO') as logger:
            # Test call for open_interface
            self.test_object.open_interface(interface_name)
            self.assertTrue(expected_output in logger.output[0])

    @patch('ctypes.c_char_p', return_value=MockDLL())
    def test_check_return_code(self, mock_ctypes):
        """
        Method for testing the functionality of GoepelCommon.check_return_code. This method also
        covers GoepelCommon.get_last_error method
        Testing both successful and failure in execution
        """
        expected_err = "G_Error Occurred \n\t" \
                       "G_Error Code\t: 0x1\n\t" \
                       "G_Error String\t: 1\n\t"
        # Test call for check_return_code with return code 0. Expecting no error
        self.assertEqual(
            self.test_object.check_return_code(0),
            None,
            "The method returned with error"
        )

        # Test call for check_return_code with return code 1. Expecting to raise error
        with self.assertRaises(Exception) as error:
            self.test_object.check_return_code(1)
        self.assertIn(expected_err, str(error.exception))

    def test_close_interface(self):
        """
        Method for testing the functionality of GoepelCommon.close_interface. This method also
        covers GoepelCommon.is_port_open method
        Testing both when port is open and closed
        """
        expected_output_1 = "Port Handle closed ..."
        expected_output_2 = "Port Handle was closed already ..."
        with self.assertLogs('G_API', 'INFO') as logger:
            # Test call for close_interface when port is open
            self.test_object.close_interface()
        self.assertTrue(expected_output_1 in logger.output[0])

        with self.assertLogs('G_API', 'DEBUG') as debugger:
            with patch('ptf.tools_utils.goepel.goepel_common.GoepelCommon.is_port_open',
                       return_value=False):
                # Test call for close_interface when port is closed
                self.test_object.close_interface()
        self.assertTrue(expected_output_2 in debugger.output[0])

    @patch('ctypes.create_string_buffer', return_value=MockDLL())
    def test_get_firmware_version(self, mock_ctypes):
        """
        Method for testing the functionality of GoepelCommon.get_firmware_version.
        ctypes.create_string_buffer is mocked and returned with class MockDLL, which has value = 1
        """
        firmware_ver = self.test_object.get_firmware_version()
        self.assertEqual(
            int(firmware_ver),
            1,
            "Expected version '1' but found '{}'".format(firmware_ver))


if __name__ == '__main__':
    unittest.main(verbosity=2)
