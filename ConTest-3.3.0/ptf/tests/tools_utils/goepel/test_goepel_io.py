"""
Unittest file for goepel io utility
Copyright 2020 Continental Corporation

:file: test_goepel_io.py
:platform: Linux, Windows
:synopsis: File containing Unittest for goepel io utility.
           Test cases for testing the GoepelIO(inherited from GoepelCommon) related utilities.
:author: Christopher Mirajkar <Christopher.Charles.Mirajkar@continental-corporation.com>
"""

import sys
import os
import unittest
import pytest
from unittest.mock import patch

# Positional arguments are set based on the patch decorators for each test-case.
# These arguments are not called directly but their functions are used within test-cases.
# Disabling the PyLint warning for 'unused arguments' is just for having better code rating.
# Also ignoring similar error for arguments used in setUpClass
# pylint: disable=unused-argument, invalid-name, too-many-arguments, arguments-differ

# Adding path of the modules to system path for running the test externally
try:
    CWD = os.path.dirname(__file__)
    BASE_DIR = os.path.abspath(os.path.join(CWD, '..', '..', '..'))
    sys.path.append(os.path.abspath(os.path.join(BASE_DIR, '..')))
    sys.path.append(os.path.join(BASE_DIR, 'tool_utils'))
    from ptf.tools_utils.goepel import goepel_io, g_api_defines
    from ptf.tests.tools_utils.goepel.test_goepel_common import MockDLL
finally:
    pass


class MockCTypes(MockDLL):
    """
    Dummy class with no realtime functions only for testing purpose. This class is inherited from
    another mocked class used in unittest test_goepel_common. Loaded dll libraries and ctypes in the
    Goepel module is mocked and returned with this class.
    """

    def __init__(self, expect_error=False):
        """
        Creates a new instance

        :param bool expect_error: Set to True when we expect the methods to return error code(!=0).
                                  Default is set to False, expected to return G_NO_ERROR(0).
        """
        super().__init__()
        self.expect_error = expect_error

    def G_Io_InitInterface(self, port_handle, flags):
        """
        This a dummy method for testing, so that check_return_code method raises error (or) no error

        :return: returns 0 which is G_NO_ERROR if no error expected, returns 1 when error expected.
        """
        if self.expect_error:
            ret_code = 1
        else:
            ret_code = 0
        return ret_code

    def G_Io_Trigger_Source_Set(self, port_handle, output_type, output_number, source_type,
                                source_number):
        """
        This a dummy method for testing, so that check_return_code method raises error (or) no error

        :return: returns 0 which is G_NO_ERROR if no error expected, returns 1 when error expected.
        """
        if self.expect_error:
            ret_code = 1
        else:
            ret_code = 0
        return ret_code


@pytest.mark.skipif(sys.platform != 'win32', reason="Executed only on Windows platform")
class TestGoepelIO(unittest.TestCase):
    """ A class for testing Goepel IO module"""

    @classmethod
    @patch('ctypes.cdll.LoadLibrary', return_value=MockCTypes())
    def setUpClass(cls, mock_ctypes):
        """
        Set up class method to be executed before all test cases i.e global setup.
        """
        # test_object_1 for error free execution
        cls.test_object_1 = goepel_io.GoepelIO(interface_name="test_io")
        # test_object_2 for error during execution
        with patch('ctypes.cdll.LoadLibrary', return_value=MockCTypes(expect_error=True)):
            cls.test_object_2 = goepel_io.GoepelIO(interface_name="test_io")

    @classmethod
    def tearDownClass(cls):
        """
        Method for global tear down.
        """
        # deleting the objects
        del cls.test_object_1
        del cls.test_object_2

    @patch('ctypes.c_char_p', return_value=MockDLL())
    def test_init_interface(self, mock_ctypes):
        """
        Method for testing the functionality of GoepelIO.init_interface
        Testing both successful error in execution
        """
        expected_err = "G_Error Occurred \n\t" \
                       "G_Error Code\t: 0x1\n\t" \
                       "G_Error String\t: 1\n\t"
        # Test call for init_interface. Expecting no error
        self.assertEqual(
            self.test_object_1.init_interface(
                g_api_defines.G_IO__INIT_INTERFACE__CMD_FLAG__RESET_TRIGGERS),
            None,
            "The method returned with error"
        )
        # Test call for init_interface with mocked return code 1. Expecting to raise error
        with self.assertRaises(Exception) as error:
            self.test_object_2.init_interface(
                g_api_defines.G_IO__INIT_INTERFACE__CMD_FLAG__RESET_TRIGGERS)
        self.assertIn(expected_err, str(error.exception))

    @patch('ctypes.c_char_p', return_value=MockDLL())
    def test_trigger_source_set(self, mock_ctypes):
        """
        Method for testing the functionality of GoepelIO.trigger_source_set
        Testing both successful error in execution
        """
        expected_err = "G_Error Occurred \n\t" \
                       "G_Error Code\t: 0x1\n\t" \
                       "G_Error String\t: 1\n\t"
        # Test call for trigger_source_set. Expecting no error
        self.assertEqual(
            self.test_object_1.trigger_source_set(
                g_api_defines.G_IO__TRIGGER__OUTPUT_TYPE__UART_RX,
                1,
                g_api_defines.G_IO__TRIGGER__SOURCE_TYPE__LVDS_0_SER_DES_GPIO,
                6 + 1),
            None,
            "The method returned with error"
        )
        # Test call for trigger_source_set with mocked return code 1. Expecting to raise error
        with self.assertRaises(Exception) as error:
            self.test_object_2.trigger_source_set(
                g_api_defines.G_IO__TRIGGER__OUTPUT_TYPE__UART_RX,
                1,
                g_api_defines.G_IO__TRIGGER__SOURCE_TYPE__LVDS_0_SER_DES_GPIO,
                6 + 1)
        self.assertIn(expected_err, str(error.exception))


if __name__ == '__main__':
    unittest.main(verbosity=2)
