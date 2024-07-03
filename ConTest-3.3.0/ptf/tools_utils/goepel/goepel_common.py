"""
 Copyright 2018 Continental Corporation

 Author:
    - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
    - Melchior Rabe <Melchior.Rabe@continental-corporation.com>
    - M. F. Ali Khan <muhammad.fakhar.ali.khan@continental-corporation.com>

 File:
    goepel_common.py

 Details:
    This file implements a common functions supported by all goepel supported interfaces e.g
    CAN, Ethernet, Flexray etc.
"""

# standard python imports
import logging
import ctypes
import os
# custom imports
from ptf.verify_utils import ptf_asserts
from ptf.tools_utils.goepel import g_api_defines

LOG = logging.getLogger('G_API')

# General base class for all types of Goepel interfaces
class GoepelCommon:
    """
    Class for providing a common interface class for all communication protocols supported by
    goepel API.
    """
    # class variables
    G_API_PATH = os.path.join("C:", os.sep, "Windows", "System32", "g_api.dll")
    G_API_COMMON_PATH = os.path.join("C:", os.sep, "Windows", "System32", "g_api_common.dll")
    G_API_CAN_PATH = os.path.join("C:", os.sep, "Windows", "System32", "g_api_can.dll")
    G_API_IO_PATH = os.path.join("C:", os.sep, "Windows", "System32", "g_api_io.dll")
    G_API_LVDS_PATH = os.path.join("C:", os.sep, "Windows", "System32", "g_api_lvds.dll")

    def __init__(self):
        """
        Constructor
        """
        # common  variables for all child classes.
        self.goepel_dlls = self._grab_dlls()
        self.port_handle = ctypes.c_int32(-1)

    def open_interface(self, interface_name):
        """
        Generic function to open any goepel supported interface.

        :param str interface_name: name of interface to be opened as defined in HW explorer
        """

        # opening a port for the communicating with the hardware.
        ret_code = self.goepel_dlls["g_api_common"].G_Common_OpenInterface(
            interface_name.encode(),
            ctypes.byref(self.port_handle)
        )
        self.check_return_code(ret_code)
        LOG.info("Communication port opened with interface name '%s'", interface_name)

    def check_return_code(self, return_code):
        """
        Method for checking return code of an executed command and raising CONTEST exception if
        return code is not equal to 0 (G_NO_ERROR)

        :param int return_code: Return code from G_API command
        """
        if return_code == g_api_defines.G_NO_ERROR:
            pass
        else:
            err_code_str, err_str = self.get_last_error()
            error = "G_Error Occurred \n\t" \
                    "G_Error Code\t: {}\n\t" \
                    "G_Error String\t: {}\n\t".format(err_code_str, err_str)
            # closing port handle if opened
            self.close_interface()
            ptf_asserts.fail(error)

    def get_last_error(self):
        """
        Method for getting last message occurred in Goepel device

        :returns: Tuple containing error code and error message (error_code, error_message)
        :rtype: tuple
        """
        err = ctypes.c_char_p(self.goepel_dlls["g_api"].G_GetLastErrorDescription())
        err_str = str(err.value.decode())
        # throw back error code and error string
        return hex(self.goepel_dlls["g_api"].G_GetLastErrorCode()), err_str

    def is_port_open(self):
        """
        Method for checking if port handle is open or closed

        :returns: True if port is open else False
        :rtype: bool
        """
        ret = False
        if self.port_handle.value != 255:
            ret = True
        else:
            pass
        # throw back status
        return ret

    def close_interface(self):
        """
        Method for closing opened interface with Goepel device
        """
        if self.is_port_open():
            self.goepel_dlls["g_api_common"].G_Common_CloseInterface(self.port_handle.value)
            LOG.info("Port Handle closed ...")
        else:
            LOG.debug("Port Handle was closed already ...")

    def get_firmware_version(self):
        """
        Returns the firmware version of an already opened Goepel device.

        :return: The firmware version
        :rtype: str

        Example::

            # Assuming 'g_device' is the object name. Usually this is 'g_can', 'g_io' or similar
            # from a sublcass of goepel_common
            version = g_device.get_firmware_version()
            print(version)
        """
        buffer = ctypes.create_string_buffer(4096)
        buffer_len = ctypes.c_uint32(len(buffer))
        result = self.goepel_dlls["g_api_common"].G_Common_GetFirmwareVersion(
            self.port_handle.value, buffer, ctypes.byref(buffer_len))

        self.check_return_code(result)

        return buffer.value.decode('utf-8')

    @staticmethod
    def _grab_dlls():
        """
        Method for grabbing goepel dlls using ctypes so that the can be used in python code.
        """
        goepel_dlls = dict()
        # capturing all required DLLs
        goepel_dlls["g_api"] = ctypes.cdll.LoadLibrary(GoepelCommon.G_API_PATH)
        goepel_dlls["g_api_common"] = ctypes.cdll.LoadLibrary(GoepelCommon.G_API_COMMON_PATH)
        goepel_dlls["g_api_can"] = ctypes.cdll.LoadLibrary(GoepelCommon.G_API_CAN_PATH)
        goepel_dlls["g_api_io"] = ctypes.cdll.LoadLibrary(GoepelCommon.G_API_IO_PATH)
        goepel_dlls["g_api_lvds"] = ctypes.cdll.LoadLibrary(GoepelCommon.G_API_LVDS_PATH)
        # throw back captured dlls
        return goepel_dlls
