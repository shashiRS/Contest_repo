"""
Unittest file for goepel CAN tool utility
Copyright 2020 Continental Corporation

:file: test_goepel_can.py
:platform: Linux, Windows
:synopsis: File containing Unittest for goepel CAN tool utility.
           Test cases for testing the Goepel CAN related utilities.
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
# pylint: disable=unused-argument, invalid-name, redefined-outer-name

# Adding path of the modules to system path for running the test externally
try:
    CWD = os.path.dirname(__file__)
    BASE_DIR = os.path.abspath(os.path.join(CWD, '..', '..', '..'))
    sys.path.append(os.path.abspath(os.path.join(BASE_DIR, '..')))
    sys.path.append(os.path.join(BASE_DIR, 'tool_utils'))
    from ptf.tools_utils.goepel.goepel_can import GoepelCan
    from ptf.tests.tools_utils.goepel.test_goepel_common import MockDLL
    from ptf.tools_utils.goepel import g_api_defines
finally:
    pass


class MockCTypes(MockDLL):
    """
    Dummy class with no realtime functions only for testing purpose. This class is inherited from
    another mocked class used in unittest test_goepel_common. Loaded dll libraries and ctypes in the
    Goepel module is mocked and returned with this class.
    """

    @staticmethod
    def G_Can_InitInterface(port_handle, byref, resp):
        """
        This a dummy method for testing

        :return: returns 0 as no error description
        """
        return 0

    @staticmethod
    def G_Can_Node_Baudrate_Set(port_handle, byref, resp, dummy):
        """
        This a dummy method for testing

        :return: returns 0 as no error description
        """
        return 0

    @staticmethod
    def G_Can_Node_BaudrateFd_Set(port_handle, byref, resp):
        """
        This a dummy method for testing

        :return: returns 0 as no error description
        """
        return 0

    @staticmethod
    def G_Can_UartGateway_Init(port_handle, byref, resp):
        """
        This a dummy method for testing

        :return: returns 0 as no error description
        """
        return 0


@pytest.fixture(scope="class")
@mock.patch('ctypes.cdll.LoadLibrary', return_value=MockCTypes())
def goepel_common_obj(mock_ctypes):
    """
    This function is a setup using fixture to create the object of the class, that has to be
    tested
    """
    return GoepelCan()


@pytest.mark.skipif(sys.platform != 'win32', reason="Executed only on Windows platform")
def test_init_interface(goepel_common_obj, caplog):
    """
    Function for testing the functionality of the method GoepelCan.init_interface

    Tested with two different calls:
    1. With deafult can_fd_baud_rate (-1)
    2. With can_fd_baud_rate that is greater than -1 (1)
    """
    # Call with default can_fd_baud_rate. Testing its LOG prints to ensure successful execution
    with caplog.at_level(logging.INFO):
        goepel_common_obj.init_interface()
    assert "CAN initialization is done" in caplog.text
    assert "Baud-rate set to '500000' Baud. The set baud-rate values can be read by accessing " \
           "'baud_rate_values' structure\n" in caplog.text

    # Call with 1 as can_fd_baud_rate. Testing its LOG prints to ensure successful execution
    with caplog.at_level(logging.INFO):
        goepel_common_obj.init_interface(can_fd_baud_rate=1)
    assert "CAN FD Baud-rate set to '1' Baud" in caplog.text


@pytest.mark.skipif(sys.platform != 'win32', reason="Executed only on Windows platform")
def test_init_uart_gateway(goepel_common_obj, caplog):
    """
    Function for testing the functionality of the method GoepelCan.test_init_uart_gateway
    Expecting sucessful execution behaviour
    """
    with caplog.at_level(logging.INFO):
        goepel_common_obj.init_uart_gateway(
            g_api_defines.G_CAN__UART_GATEWAY__INIT__CMD_FLAG__LENGTH_INCLUSIVE_LENGTH_BYTE,
            512,
            1000,
            g_api_defines.G_CAN__UART_GATEWAY__UART_INSTANCE_TYPE__LVDS_CONTROL_CHANNEL,
            0,
            g_api_defines.G_CAN__UART_GATEWAY__UART_PARITY__EVEN,
            1000000
        )
    assert "Uart gateway initialized" in caplog.text
