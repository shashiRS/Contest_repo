"""
    Copyright 2019 Continental Corporation

    :file: goepel_can.py
    :platform: Windows
    :synopsis:
        This package provides can api. It provides the possibility to interact with
        Goepel CAN devices.

    :author:
        - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""


# standard python imports
import ctypes

# custom imports
from ptf.tools_utils.goepel import g_api_defines
from ptf.tools_utils.goepel import g_api_structs
from ptf.tools_utils.goepel import goepel_common
from ptf.tools_utils.goepel.goepel_common import GoepelCommon

LOG = goepel_common.LOG

class GoepelCan(GoepelCommon):
    """
    Class that provides a CAN or CAN FD connection using a Goepel CAN interface.

    Example::

        # to be done in setup.pytest

        # in custom import section
        from ptf.ptf_utils.global_params import set_global_parameter, get_parameter
        from ptf.tools_utils.goepel.goepel_can import GoepelCan

        # recommended to be done in 'global_setup'
        # creating an object of goepel can utility and initializing it with CAN1 bus
        g_can = GoepelCan()
        g_can.init_interface()

        # creating a global parameter and assigning goepel can utility object to it
        set_global_parameter("g_can", g_can)

        # you can access 'g_can' object as follow in setup.pytest, .pytest or .py files
        g_can = get_parameter("g_can")
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # baud rate settings structure
        self.baud_rate_values = g_api_structs.GCanNodeBaudrateActualValues()

    def init_interface(self, interface_name='CAN1', baud_rate=500000, can_fd_baud_rate=-1):
        """
        Method for initializing CAN and CAN FD interface with Goepel device.

        Steps:
            1. Opening the interface using CAN interface name as defined in HW explorer
            2. self.open_interface(int_name) returns a port handle in self.port_handle variable
            3. self.port_handle is used further to initialize the CAN interface
            4. Setting of CAN baud-rate.
            5. Optional: Setting of CAN FD baud-rate

        :param str interface_name: Interface name which is available for use in Goepel HW explorer.
            Default is "CAN1"
        :param int baud_rate: Baud-rate to be set. Default is 500000 Baud.
        :param int can_fd_baud_rate: If set to a value > -1, CAN FD support will be configured with
                                     given baud rate. Otherwise, CAN FD is disabled.

        Example::

            # assuming 'g_can' is the object name
            # opening communication interface via CAN2 and baud-rate will be set as 500000
            g_can.init_interface(interface_name="CAN2", baud_rate=500000)
        """

        # opening a port with the given interface name, it returns the port handle in
        # self.port_handle variable defined in base class which can be accessed here.
        self.open_interface(interface_name)

        # setting/resetting the selected CAN interface without software reset into the initial state
        id_mode = g_api_defines.G_CAN__ID_MODE__STANDARD
        cmd_flags = g_api_defines.G_CAN__INIT_INTERFACE__CMD_FLAG__NONE

        if can_fd_baud_rate > -1:
            id_mode = g_api_defines.G_CAN__ID_MODE__MIXED
            cmd_flags = g_api_defines.G_CAN__INIT_INTERFACE__CMD_FLAG__FD_MODE__FD

        ret_code = self.goepel_dlls["g_api_can"].G_Can_InitInterface(
            self.port_handle.value,
            id_mode,
            cmd_flags
        )
        self.check_return_code(ret_code)
        LOG.info("CAN initialization is done")

        # setting the baud-rate
        baud_rate = ctypes.c_uint32(baud_rate)
        ret_code = self.goepel_dlls["g_api_can"].G_Can_Node_Baudrate_Set(
            self.port_handle.value,
            baud_rate.value,
            0,
            ctypes.byref(self.baud_rate_values)
        )
        self.check_return_code(ret_code)
        LOG.info("Baud-rate set to '%s' Baud. The set baud-rate values can be read "
                 "by accessing 'baud_rate_values' structure", baud_rate.value)

        if can_fd_baud_rate > -1:
            cmd = g_api_structs.GCanNodeBaudrateFdSetCmd()
            cmd.Flags = g_api_defines.G_CAN__NODE__BAUDRATE_FD__SET__CMD_FLAG__NONE
            cmd.BaudRate = ctypes.c_uint32(can_fd_baud_rate)

            resp = g_api_structs.GCanNodeBaudrateFdSetRsp()

            ret_code = self.goepel_dlls["g_api_can"].G_Can_Node_BaudrateFd_Set(
                self.port_handle.value,
                ctypes.byref(cmd),
                ctypes.byref(resp)
            )
            self.check_return_code(ret_code)
            LOG.info("CAN FD Baud-rate set to '%s' Baud.", can_fd_baud_rate)

    def init_uart_gateway(self, flags, max_retries, ack_timeout, uart_instance_type,
                          uart_instance_id, uart_parity, uart_baud_rate):
        """
        Method to initialize the CAN-UART Gateway on your CAN device.

        :param int flags: 'G_Lvds_SerDesGpio_IocOutputType_t' flags from g_api_defines.py
        :param int max_retries: Maximum TX retries when no ack is received
        :param int ack_timeout: Time in microseconds to wait for an ack
        :param ctypes.c_uint8 uart_instance_type: One of 'G_Can_UartGateway_UartInstanceType_t'
                                                  in g_api_defines.py
        :param int uart_instance_id: Instance ID of the UART instance, starting with 0
        :param ctypes.c_uint8 uart_parity: One of 'G_Can_UartGateway_UartParity_t'
                                           in g_api_defines.py
        :param int uart_baud_rate: UART baud rate, in baud

        Example::

            # assuming 'g_can' is the object name
            g_can.init_uart_gateway(
                g_api_defines.G_CAN__UART_GATEWAY__INIT__CMD_FLAG__LENGTH_INCLUSIVE_LENGTH_BYTE,
                512,
                1000,
                g_api_defines.G_CAN__UART_GATEWAY__UART_INSTANCE_TYPE__LVDS_CONTROL_CHANNEL,
                0,
                g_api_defines.G_CAN__UART_GATEWAY__UART_PARITY__EVEN,
                1000000
            )
        """

        cmd = g_api_structs.GCanUartGatewayInitCmd()
        cmd.Flags = ctypes.c_uint32(flags)
        cmd.MaxRetries = ctypes.c_uint32(max_retries)
        cmd.AckTimeout = ctypes.c_uint32(ack_timeout)
        cmd.UartInstanceType = uart_instance_type
        cmd.UartInstanceId = ctypes.c_uint8(uart_instance_id)
        cmd.UartParity = uart_parity
        cmd.UartBaudRate = ctypes.c_uint32(uart_baud_rate)

        resp = g_api_structs.GCanUartGatewayInitRsp()

        ret_code = self.goepel_dlls["g_api_can"].G_Can_UartGateway_Init(
            self.port_handle.value,
            ctypes.byref(cmd),
            ctypes.byref(resp)
        )
        self.check_return_code(ret_code)
        LOG.info("Uart gateway initialized")
