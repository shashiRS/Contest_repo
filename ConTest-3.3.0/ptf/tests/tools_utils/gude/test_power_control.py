"""
    Copyright Continental Corporation and subsidiaries. All rights reserved.

    :platform: Windows, Linux

    :synopsis:
        File containing Unittest for GUDE power control.
        Test cases for testing the GUDE power control related utilities.
"""

# disabling import error as they are installed at start of framework
# pylint: disable=import-error
import sys
import os
import unittest
from unittest.mock import patch
import pytest

# Positional arguments are set based on the patch decorators for each test-case.
# These arguments are not called directly but their functions are used within test-cases.
# Disabling the PyLint warning for 'unused arguments' is just for having better code rating.
# Also ignoring similar error for arguments used in setUpClass
# pylint: disable=unused-argument, arguments-differ

# Adding path of the modules used in power_control.py to system path for running the test externally
# pylint: disable=import-error, broad-exception-caught
try:
    CWD = os.path.dirname(__file__)
    BASE_DIR = os.path.abspath(os.path.join(CWD, "..", "..", ".."))
    sys.path.append(os.path.abspath(os.path.join(BASE_DIR, "..")))
    sys.path.append(os.path.join(BASE_DIR, "tool_utils"))
    from ptf.tools_utils.gude import power_control
except Exception:
    # remove this exception when the tests are fixed for Python 3.9
    pass
finally:
    pass


@pytest.mark.skip(reason="Needs fix after using python 3.9.12 in jenkins run")
class TestPowerControl(unittest.TestCase):
    """A class for testing GUDE PowerControl module"""

    @classmethod
    @patch("ptf.verify_utils.ptf_asserts.verify", return_value=None)
    @patch("builtins.next", return_value=["", "", "", [["", "1"]]])
    def setUpClass(cls, mock_next, mock_ptf_asserts):
        cls.test_object = power_control.PowerControl()

    @patch("builtins.next", return_value=["", "", "", [["", "1"]]])
    def test_get_state_success(self, mock_next):
        """
        Method for testing PowerControl.get_state
        During successful execution
        """
        # Test call for get_state with port_num=None
        self.assertEqual(self.test_object.get_state(), [1], "The method returned invalid port states")

        # Test call for get_state with port_num=1
        self.assertEqual(self.test_object.get_state(1), 1, "The method returned invalid port state")

    def test_get_state_failure(self):
        """
        Method for testing PowerControl.get_state
        During error in execution
        """
        expected_err = "Invalid port number found. Must be > 0"
        # Test call for get_state with port_num=0
        with self.assertRaises(Exception) as error:
            self.test_object.get_state(0)
        self.assertIn(expected_err, str(error.exception))

    @patch("builtins.next", return_value=["", "", "", [["", "0"]]])
    def test_set_state_success(self, mock_next):
        """
        Method for testing PowerControl.set_state
        During successful execution
        """
        # Test call for set_state with port_num=1 state=0 (OFF)
        self.assertEqual(self.test_object.set_state(1, 0), None, "The method failed to set the state")

    def test_set_state_failure(self):
        """
        Method for testing PowerControl.set_state
        During error in execution
        """
        expected_err_1 = "Invalid port number found. Must be > 0"
        # Test call for set_state with port_num=0 (wrong port number)
        with self.assertRaises(Exception) as error:
            self.test_object.set_state(0, 1)
        self.assertIn(expected_err_1, str(error.exception))

        # Test call for set_state with state=2 (unknown state)
        expected_err_2 = "State needs to be either 0 or 1"
        with self.assertRaises(Exception) as error:
            self.test_object.set_state(1, 2)
        self.assertIn(expected_err_2, str(error.exception))

    @patch("builtins.next", return_value=["", "", "", [["", "1"]]])
    def test_set_states_success(self, mock_next):
        """
        Method for testing PowerControl.set_states
        During successful execution
        """
        ports_list = [1, None, 1]
        # Test call for set_states
        self.assertEqual(self.test_object.set_states(ports_list), None, "The method failed to set the states")

    @patch("builtins.next", return_value=["", "", "", [["", "1"]]])
    def test_set_states_failure(self, mock_next):
        """
        Method for testing PowerControl.set_states
        During error in execution
        """
        ports_list = [2, None, 1]
        expected_err = "State needs to be either 0 or 1"
        # Test call for set_states with unknown state
        with self.assertRaises(Exception) as error:
            self.test_object.set_states(ports_list)
        self.assertIn(expected_err, str(error.exception))

    @patch("builtins.next", return_value=["", "", "", [["", "0"]]])
    def test_set_all_success(self, mock_next):
        """
        Method for testing PowerControl.set_all
        During successful execution
        """
        # Test call for set_all with state=0 (OFF)
        self.assertEqual(self.test_object.set_all(0), None, "The method failed to set all the states")

    @patch("builtins.next", return_value=["", "", "", [["", "1"]]])
    def test_set_all_failure(self, mock_next):
        """
        Method for testing PowerControl.set_all
        During error in execution
        """
        expected_err = "State needs to be either 0 or 1"
        # Test call for set_all with unknown state
        with self.assertRaises(Exception) as error:
            self.test_object.set_all(2)
        self.assertIn(expected_err, str(error.exception))

    @patch("builtins.next", return_value=["test_error_indication", "", "", [["", "1"]]])
    def test_read_device_name_failure_1(self, mock_next):
        """
        Method for creating instance of PowerControl with error (error_indication) while executing
        __read_device_name
        """
        expected_err = "test_error_indication"
        with self.assertRaises(Exception) as error:
            self.test_object = power_control.PowerControl()
        self.assertIn(expected_err, str(error.exception))

    @patch("builtins.next", return_value=["", "test_error_status", "", [["", "1"]]])
    def test_read_device_name_failure_2(self, mock_next):
        """
        Method for creating instance of PowerControl with error (error_status) while executing
        __read_device_name
        """
        expected_err = "test_error_status"
        with self.assertRaises(Exception) as error:
            self.test_object = power_control.PowerControl()
        self.assertIn(expected_err, str(error.exception))

    @patch("builtins.next", return_value=["test_error_indication", "", "", [["", "1"]]])
    def test_read_port_state_failure_1(self, mock_next):
        """
        Method for executing PowerControl.get_state with error (error_indication) while executing
        __read_port_state
        """
        expected_err = "test_error_indication"
        with self.assertRaises(Exception) as error:
            self.test_object.get_state()
        self.assertIn(expected_err, str(error.exception))

    @patch("builtins.next", return_value=["", "test_error_status", "", [["", "1"]]])
    def test_read_port_state_failure_2(self, mock_next):
        """
        Method for executing PowerControl.get_state with error (error_status) while executing
        __read_port_state
        """
        expected_err = "test_error_status"
        with self.assertRaises(Exception) as error:
            self.test_object.get_state()
        self.assertIn(expected_err, str(error.exception))

    @patch("builtins.next", return_value=["test_error_indication", "", "", [["", "1"]]])
    def test_write_port_state_failure_1(self, mock_next):
        """
        Method for executing PowerControl.set_state with error (error_indication) while executing
        __write_port_state
        """
        expected_err = "test_error_indication"
        with self.assertRaises(Exception) as error:
            self.test_object.set_state(1, 0)
        self.assertIn(expected_err, str(error.exception))

    @patch("builtins.next", return_value=["", "test_error_status", "", [["", "1"]]])
    def test_write_port_state_failure_2(self, mock_next):
        """
        Method for executing PowerControl.set_state with error (error_status) while executing
        __write_port_state
        """
        expected_err = "test_error_status"
        with self.assertRaises(Exception) as error:
            self.test_object.set_state(1, 0)
        self.assertIn(expected_err, str(error.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
