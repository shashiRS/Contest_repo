"""
Unittest file for goepel CAN-TP APIs
Copyright 2020 Continental Corporation
:file: test_goepel_can_tp.py
:platform: Linux, Windows
:synopsis: File containing Unittest for goepel CAN-TP APIs supported by Goepel API.
           Test cases for testing the Goepel CAN-TP APIs related utilities.
:author: Christopher Mirajkar <Christopher.Charles.Mirajkar@continental-corporation.com>
"""

import sys
import os
import logging
import pytest
from pytest_mock import mock

# Arguments used in mocked class are not used, they are placeholders when called by the module.
# Disabling the PyLint warning for 'unused arguments' is just for having better code rating.
# Also ignoring similar error for mocked class
# pylint: disable=unused-argument, invalid-name, redefined-outer-name, protected-access
# pylint: disable=too-many-arguments, wrong-import-position

# Adding path of the modules to system path for running the test externally
CWD = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.join(CWD, '..', '..', '..'))
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, '..')))
sys.path.append(os.path.join(BASE_DIR, 'tool_utils'))
from ptf.tools_utils.goepel.goepel_can_tp import GoepelCanTp  # noqa: E402
from ptf.tests.tools_utils.goepel.test_goepel_common import MockDLL  # noqa: E402
from ptf.demo_tests.evs.ptf_tests.evs_utils.evs_support import ResponseHandler  # noqa: E402


class MockCTypes(MockDLL):
    """
    Dummy class with no realtime functions only for testing purpose. This class is inherited from
    another mocked class used in unittest test_goepel_common. Loaded dll libraries and ctypes in the
    Goepel module is mocked and returned with this class.
    """

    @staticmethod
    def G_Can_Tp_Config_IsoTp(port_handle, byref, resp):
        """
        This a dummy method for testing
        :return: returns 0 as no error description
        """
        return 0

    @staticmethod
    def G_Command(port_handle, byref, resp, tp_params):
        """
        This a dummy method for testing
        :return: returns 0 as no error description
        """
        return 0

    @staticmethod
    def G_CommandWithResponse(port_handle, byref, resp, tp_params, res_struct, res_len):
        """
        This a dummy method for testing
        :return: returns 0 as no error description
        """
        return 0


@pytest.fixture(scope="class")
@mock.patch('ctypes.cdll.LoadLibrary', return_value=MockCTypes())
def goepel_can_tp_obj(mock_ctypes):
    """
    This function is a setup using fixture to create the object of the class, that has to be
    tested
    """
    return GoepelCanTp()


@pytest.mark.skipif(sys.platform != 'win32', reason="Executed only on Windows platform")
def test_configure_iso_tp(goepel_can_tp_obj, caplog):
    """
    Function for testing the functionality of the method GoepelCanTp.configure_iso_tp
    Testing its LOG prints to ensure successful execution
    """
    with caplog.at_level(logging.INFO):
        goepel_can_tp_obj.configure_iso_tp()
    assert "ISO-TP protocol configured" in caplog.text
    assert "ISO-TP direct properties are set" in caplog.text


@pytest.mark.skipif(sys.platform != 'win32', reason="Executed only on Windows platform")
def test_reg_rem_message_callback(goepel_can_tp_obj, caplog):
    """
    Function for testing the functionality of the method GoepelCanTp.register_message_callback and
    GoepelCanTp.remove_message_callback
    GoepelCanTp.remove_message_callback method is tested here so that registered 'callback_func' can
    be unregistered
    Testing LOG prints and class variables to ensure successful execution
    """
    response = ResponseHandler()

    # Calling register_message_callback method while initiating GoepelCanTp._response_callback to
    # 'callback_func', to get the warning message on conditional statement
    goepel_can_tp_obj._response_callback = response.callback_func
    with caplog.at_level(logging.WARNING):
        goepel_can_tp_obj.register_message_callback(response.callback_func)
    assert "Message callback already registered with name 'callback_func'. " \
           "Remove it first to re-register another." in caplog.text

    # Calling register_message_callback method while initiating GoepelCanTp._response_callback to
    # 'None', to skip conditional statement
    goepel_can_tp_obj._response_callback = None
    with caplog.at_level(logging.INFO):
        goepel_can_tp_obj.register_message_callback(response.callback_func)
    assert "Message callback registered 'callback_func'" in caplog.text
    assert goepel_can_tp_obj.thread_remove_flag is False

    # Test call for remove_message_callback method
    with caplog.at_level(logging.INFO):
        goepel_can_tp_obj.remove_message_callback()
    assert "Message callback 'callback_func' unregistered" in caplog.text
    assert goepel_can_tp_obj.thread_remove_flag is True


@pytest.mark.skipif(sys.platform != 'win32', reason="Executed only on Windows platform")
def test_send_message(goepel_can_tp_obj, caplog):
    """
    Function for testing the functionality of the method GoepelCanTp.send_message
    Testing its LOG prints to ensure successful execution
    """
    with caplog.at_level(logging.INFO):
        goepel_can_tp_obj.send_message(bytes([0x01, 0x02, 0x03, 0x04, 0x05]))
    assert "Message Sent" in caplog.text
