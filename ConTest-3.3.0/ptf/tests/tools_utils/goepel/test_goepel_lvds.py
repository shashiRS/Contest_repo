"""
Unittest file for goepel LVDS APIs
Copyright 2020 Continental Corporation
:file: test_goepel_lvds.py
:platform: Linux, Windows
:synopsis: File containing Unittest for goepel LVDS APIs supported by Goepel API.
           Test cases for testing the Goepel LVDS APIs related utilities.
:author: Christopher Mirajkar <Christopher.Charles.Mirajkar@continental-corporation.com>
"""

import sys
import os
import logging
import ctypes
import pytest
from pytest_mock import mock

# Disabling the PyLint warning is just for having better code rating.
# pylint: disable=unused-argument, invalid-name, redefined-outer-name, protected-access
# pylint: disable=too-many-arguments, wrong-import-position

# Adding path of the modules to system path for running the test externally
CWD = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.join(CWD, '..', '..', '..'))
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, '..')))
sys.path.append(os.path.join(BASE_DIR, 'tool_utils'))
from ptf.tools_utils.goepel.goepel_lvds import GoepelLVDS  # noqa: E402
from ptf.tools_utils.goepel import g_api_defines  # noqa: E402
from ptf.tests.tools_utils.goepel.test_goepel_common import MockDLL  # noqa: E402


class MockCTypes(MockDLL):
    """
    Dummy class with no realtime functions only for testing purpose. This class is inherited from
    another mocked class used in unittest test_goepel_common. Loaded dll libraries and ctypes in the
    Goepel module is mocked and returned with this class.
    """

    def __init__(self):
        """
        Creates a new instance
        """
        super().__init__()
        self.value = 1

    @staticmethod
    def G_Lvds_Common_Config_Set(port_handle, byref, resp):
        """
        This a dummy method for testing
        :return: returns 0 as no error description
        """
        return 0

    @staticmethod
    def G_Lvds_Common_Data_Register_Write(port_handle, byref):
        """
        This a dummy method for testing
        :return: returns 0 as no error description
        """
        return 0

    @staticmethod
    def G_Lvds_FrameGrabber_StartCapturing(port_handle):
        """
        This a dummy method for testing
        :return: returns 0 as no error description
        """
        return 0

    @staticmethod
    def G_Lvds_FrameGrabber_StopCapturing(port_handle):
        """
        This a dummy method for testing
        :return: returns 0 as no error description
        """
        return 0

    @staticmethod
    def G_Lvds_Common_Property_GetById(port_handle, byref, resp, val):
        """
        This a dummy method for testing
        :return: returns 0 as no error description
        """
        return 0

    @staticmethod
    def G_Lvds_SerDesGpio_IocPinConfig_Set(port_handle, byref):
        """
        This a dummy method for testing
        :return: returns 0 as no error description
        """
        return 0

    @staticmethod
    def G_Lvds_FrameGrabber_CaptureToBuffer2(port_handle, byref, resp, val, lent):
        """
        This a dummy method for testing
        :return: returns 0 as no error description
        """
        return 0


@pytest.fixture(scope="class")
@mock.patch('ctypes.cdll.LoadLibrary', return_value=MockCTypes())
def goepel_lvds_obj(mock_ctypes):
    """
    This function is a setup using fixture to create the object of the class, that has to be
    tested
    """
    return GoepelLVDS()


@pytest.mark.skipif(sys.platform != 'win32', reason="Executed only on Windows platform")
def test_configure_by_file(goepel_lvds_obj, caplog):
    """
    Function for testing the functionality of the method GoepelLVDS.configure_by_file
    - Testing its LOG prints to ensure successful execution
    - Giving the non real filename and expecting to raise error
    """
    # method call with proper file
    with caplog.at_level(logging.INFO):
        goepel_lvds_obj.configure_by_file(os.path.join(
            BASE_DIR, 'demo_tests', 'goepel_rvs231', '6222_RVS231_1920x1080_Conti.xml'))
    assert "Configuration loaded" in caplog.text

    # method call with 'dummy' string
    with pytest.raises(Exception) as error:
        goepel_lvds_obj.configure_by_file('dummy')
    assert "File 'dummy' not found. Please make sure you set the correct path." in str(error.value)


# Skip the execution on linux platform
@pytest.mark.skipif(sys.platform != 'win32', reason="Executed only on Windows platform")
def test_send_i2c_from_file(goepel_lvds_obj, caplog):
    """
    Function for testing the functionality of the method GoepelLVDS.send_i2c_from_file
    - Testing its LOG prints to ensure successful execution
    - Giving the non real filename and expecting to raise error
    """
    # method call with proper file
    with caplog.at_level(logging.INFO):
        goepel_lvds_obj.send_i2c_from_file(os.path.join(
            BASE_DIR, 'demo_tests', 'goepel_rvs231',
            'MAX9296_95_Cfg_for_RVS231_1920x1080_30fps_4Lanes_RGB888_Camera_mit_Reset.txt'))
    assert "Sent to i2c successful" in caplog.text

    # method call with 'dummy' string
    with pytest.raises(Exception) as error:
        goepel_lvds_obj.send_i2c_from_file('dummy')
    assert "File 'dummy' not found. Please make sure you set the correct path." in str(error.value)


@pytest.mark.skipif(sys.platform != 'win32', reason="Executed only on Windows platform")
def test_start_capturing(goepel_lvds_obj, caplog):
    """
    Function for testing the functionality of the method GoepelLVDS.start_capturing
    - Testing its LOG prints to ensure successful execution
    """
    with caplog.at_level(logging.INFO):
        goepel_lvds_obj.start_capturing()
    assert "Capturing started ..." in caplog.text


@pytest.mark.skipif(sys.platform != 'win32', reason="Executed only on Windows platform")
def test_stop_capturing(goepel_lvds_obj, caplog):
    """
    Function for testing the functionality of the method GoepelLVDS.stop_capturing
    - Testing its LOG prints to ensure successful execution
    """
    with caplog.at_level(logging.INFO):
        goepel_lvds_obj.stop_capturing()
    assert "Capturing stopped ..." in caplog.text


@pytest.mark.skipif(sys.platform != 'win32', reason="Executed only on Windows platform")
def test_get_lock_state(goepel_lvds_obj, caplog):
    """
    Function for testing the functionality of the method GoepelLVDS.get_lock_state
    - Testing the return value
    """
    with mock.patch('ctypes.c_uint8', return_value=MockCTypes()):
        with mock.patch('ctypes.byref'):
            lock_state = goepel_lvds_obj.get_lock_state()
    assert lock_state is True


@pytest.mark.skipif(sys.platform != 'win32', reason="Executed only on Windows platform")
def test_set_ser_des_gpio_ioc_pin_config(goepel_lvds_obj, caplog):
    """
    Function for testing the functionality of the method GoepelLVDS.set_ser_des_gpio_ioc_pin_config
    - Testing if the method was called with proper arguments
    """
    goepel_lvds_obj.set_ser_des_gpio_ioc_pin_config(
        g_api_defines.G_LVDS__SER_DES_GPIO__IOC_PIN_CONFIG__SET__CMD_FLAG__SET_OUTPUT_TYPE,
        5,
        g_api_defines.G_LVDS__SER_DES_GPIO__IOC_OUTPUT_TYPE__OPEN_DRAIN,
        g_api_defines.G_LVDS__SER_DES_GPIO__IOC_OUTPUT_MOD__NO_CHANGE)

    with mock.patch('ptf.tools_utils.goepel.goepel_lvds.GoepelLVDS.'
                    'set_ser_des_gpio_ioc_pin_config') as called_method:
        goepel_lvds_obj.set_ser_des_gpio_ioc_pin_config(
            g_api_defines.G_LVDS__SER_DES_GPIO__IOC_PIN_CONFIG__SET__CMD_FLAG__SET_OUTPUT_TYPE,
            5,
            g_api_defines.G_LVDS__SER_DES_GPIO__IOC_OUTPUT_TYPE__OPEN_DRAIN,
            g_api_defines.G_LVDS__SER_DES_GPIO__IOC_OUTPUT_MOD__NO_CHANGE)
    called_method.assert_called_with(
        g_api_defines.G_LVDS__SER_DES_GPIO__IOC_PIN_CONFIG__SET__CMD_FLAG__SET_OUTPUT_TYPE,
        5,
        g_api_defines.G_LVDS__SER_DES_GPIO__IOC_OUTPUT_TYPE__OPEN_DRAIN,
        g_api_defines.G_LVDS__SER_DES_GPIO__IOC_OUTPUT_MOD__NO_CHANGE)


@pytest.mark.skipif(sys.platform != 'win32', reason="Executed only on Windows platform")
def test_get_single_image_raw(goepel_lvds_obj, caplog):
    """
    Function for testing the functionality of the method GoepelLVDS.get_single_image_raw
    - Testing for both w/ and w/o timestamp
    - Testing their return values
    """
    # method call w/o timestamp
    data_1, frame_size_1, timestamp_1 = goepel_lvds_obj.get_single_image_raw()
    assert isinstance(data_1, type(ctypes.create_string_buffer(26542080)))
    assert frame_size_1 == 26542080
    assert timestamp_1 == -1

    # method call w/ timestamp
    data_2, frame_size_2, timestamp_2 = goepel_lvds_obj.get_single_image_raw(True)
    assert isinstance(data_2, type(ctypes.create_string_buffer(26542080)))
    assert frame_size_2 == 26542080
    assert timestamp_2 == 0


@pytest.mark.skipif(sys.platform != 'win32', reason="Executed only on Windows platform")
def test_get_single_image(goepel_lvds_obj, caplog):
    """
    Function for testing the functionality of the method GoepelLVDS.get_single_image
    - Testing the return values
    """
    img, timestamp = goepel_lvds_obj.get_single_image(4096, 2160, 24)
    assert img.size == (4096, 2160)
    assert timestamp == -1
