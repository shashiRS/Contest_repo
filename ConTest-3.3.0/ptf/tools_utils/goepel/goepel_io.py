"""
    Copyright 2019 Continental Corporation

    :file: goepel_io.py
    :platform: Windows
    :synopsis:
        This package provides I/O api. It provides the possibility to interact with
        Goepel I/O devices.

    :author:
        - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""

# standard python imports
import ctypes

# custom imports
from ptf.tools_utils.goepel.goepel_common import GoepelCommon


class GoepelIO(GoepelCommon):
    """
    Class that provides a I/O controlling api using Goepel I/O hardware.
    """

    def __init__(self, interface_name='IO1'):
        """
        Creates a new I/O controller for goepel devices.

        :param str interface_name: The device name to use. Check Goepel HW explorer.

        Example::

            # creating a controller for IO2 device
            g_io = GoepelIO(interface_name="IO2")
        """
        super().__init__()

        self.open_interface(interface_name)

    def init_interface(self, flags):
        """
        Method to initialize the IO interface.

        :param int flags: One of 'G_Io_InitInterface_CmdFlags_t' in g_api_defines.py

        Example::

            # Reset all triggers on initialisation
            g_io.init_interface(g_api_defines.G_IO__INIT_INTERFACE__CMD_FLAG__RESET_TRIGGERS)
        """
        flags = ctypes.c_uint32(flags)
        ret_code = self.goepel_dlls["g_api_io"].G_Io_InitInterface(self.port_handle.value, flags)
        self.check_return_code(ret_code)

    def trigger_source_set(self, output_type, output_number, source_type, source_number):
        """
        Method to assign a trigger signal source to a trigger signal output.

        :param ctypes.c_uint8 output_type: Trigger signal destination.
                                           One of 'G_Io_Trigger_OutputType_t' in g_api_defines.py
        :param int output_number: Output number of selected output type (starts at 1)
        :param ctypes.c_uint8 source_type: Signal source selection.
                                           One of 'G_Io_Trigger_SourceType_t' in g_api_defines.py
        :param int source_number: Source number of the selected source type (starts at 1)

        Example::

            g_io.trigger_source_set(
                g_api_defines.G_IO__TRIGGER__OUTPUT_TYPE__UART_RX,
                1,
                g_api_defines.G_IO__TRIGGER__SOURCE_TYPE__LVDS_0_SER_DES_GPIO,
                6+1 # Use source number 6 and start counting at 1
            )
        """
        ret_code = self.goepel_dlls["g_api_io"].G_Io_Trigger_Source_Set(
            self.port_handle.value,
            output_type,
            ctypes.c_uint8(output_number),
            source_type,
            ctypes.c_uint8(source_number))

        self.check_return_code(ret_code)
