"""
 Copyright 2018 Continental Corporation

 Author:
    - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
    - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>

 File:
    g_api_structs.py

 Details:
    This file contains structures definitions in Python (Python replicas) which are using in
    Goepel APIs.
"""

# Python imports
import ctypes

# custom imports
from ptf.tools_utils.goepel import g_api_defines

# pylint: disable=too-few-public-methods
class GCanTpConfigIsoTpParameters(ctypes.Structure):
    """
    Structure Class for 'G_Can_Tp_Config_IsoTp_Parameters_t'

    Python replica of 'G_Can_Tp_Config_IsoTp_Parameters_t' in 'g_api_can.h' file
    """
    # defining structure members
    _fields_ = [
        # physical and functional addresses
        ('PhysicalSourceAddress', ctypes.c_uint8),
        ('PhysicalTargetAddress', ctypes.c_uint8),
        ('FunctionalSourceAddress', ctypes.c_uint8),
        ('FunctionalTargetAddress', ctypes.c_uint8),

        # physical and functional ids
        ('PhysicalSourceId', ctypes.c_uint32),
        ('PhysicalTargetId', ctypes.c_uint32),
        ('FunctionalSourceId', ctypes.c_uint32),
        ('FunctionalTargetId', ctypes.c_uint32),

        # physical and functional addressing format
        ('PhysicalAddressingFormat', ctypes.c_uint8),
        ('FunctionalAddressingFormat', ctypes.c_uint8),

        # to describe flow-control frames after consecutive frames
        ('BlockSize', ctypes.c_uint8),
        # time between CAN frames to be met by the communication partner (in msec.)
        ('SeparationTime', ctypes.c_uint8),

        # flag
        ('Flags', ctypes.c_uint32),

        # self-meeting time between two CAN messages within a segmented data exchange, given in
        # milliseconds
        ('OwnSeparationTime', ctypes.c_uint8),

        # reserved bytes
        ('reserved1', ctypes.c_uint8),
        ('reserved2', ctypes.c_uint8),
        ('reserved3', ctypes.c_uint8),

        # sending timeout send-site (in msec.)
        ('TimeoutAs', ctypes.c_uint16),
        # sending timeout receive-site (in msec.)
        ('TimeoutAr', ctypes.c_uint16),
        # flow-control frame receiving timeout send-site (in msec.)
        ('TimeoutBs', ctypes.c_uint16),
        # consecutive frame receiving timeout receive-site (in msec.)
        ('TimeoutCr', ctypes.c_uint16),

        # time between reception of a "first frame" and transmission of a "flow control" in milli
        # seconds. This time is used only if flag "USE_TIME_BR_BETWEEN_FF_AND_FC" within "Flags" is
        # set.
        ('TimeBrBetweenFfAndFc', ctypes.c_uint16),

        # time between reception of a "consecutive frame" and transmission of a "flow control" in
        # milli seconds. This time is used only if flag "USE_TIME_BR_BETWEEN_CF_AND_FC" within
        # "Flags" is set.
        ('TimeBrBetweenCfAndFc', ctypes.c_uint16)
    ]

# pylint: disable=too-few-public-methods
class CanTpDirectSetPropertiesCommand(ctypes.Structure):
    """
    Structure Class for 'Can_TpDirect_SetProperties_Command_t'

    Python replica of 'Can_TpDirect_SetProperties_Command_t' in 'host_para_can.h' file
    """
    # defining structure members
    _fields_ = [
        ('Channel', ctypes.c_uint8),
        ('Type', ctypes.c_uint8),
        ('reserved', ctypes.c_uint8),
        ('Flags', ctypes.c_uint8)
    ]

# pylint: disable=too-few-public-methods
class GCanNodeBaudrateActualValues(ctypes.Structure):
    """
    Structure Class for 'G_Can_Node_Baudrate_ActualValues_t'

    Python replica of 'G_Can_Node_Baudrate_ActualValues_t' in 'g_api_can.h' file
    """
    # defining structure members
    _fields_ = [
        ('Baudrate', ctypes.c_uint32),
        ('CanControllerClock', ctypes.c_uint32),

        ('SamplePoint', ctypes.c_uint8),
        ('NumberOfTimeQuanta', ctypes.c_uint8),
        ('TSeg1', ctypes.c_uint8),
        ('TSeg2', ctypes.c_uint8),

        ('Sjw', ctypes.c_uint8),
        ('reserved1', ctypes.c_uint8),
        ('reserved2', ctypes.c_uint8),
        ('reserved3', ctypes.c_uint8),
    ]

# pylint: disable=too-few-public-methods
class CanTpDirectStartCommand(ctypes.Structure):
    """
    Structure Class for 'Can_TpDirect_Start_Command_t'

    Python replica of 'Can_TpDirect_Start_Command_t' in 'host_para_can.h' file
    """
    # defining structure members
    _fields_ = [
        ('Channel', ctypes.c_uint8),
        ('Type', ctypes.c_uint8),
        ('reserved', ctypes.c_uint8),
        ('Flags', ctypes.c_uint8),
    ]

# pylint: disable=too-few-public-methods
class CanTpDirectRequestCommand(ctypes.Structure):
    """
    Structure Class for 'Can_TpDirect_Request_Command_t'

    Python replica of 'Can_TpDirect_Request_Command_t' in 'host_para_can.h' file
    """
    # defining structure members
    _fields_ = [
        ('Channel', ctypes.c_uint8),
        ('Flags', ctypes.c_uint8),
        ('Send', ctypes.c_uint8),
        ('Concatenate', ctypes.c_uint8),

        ('reserved1', ctypes.c_uint8),
        ('reserved2', ctypes.c_uint8),

        ('Length', ctypes.c_uint16),

        ('Data', ctypes.c_uint8 * (g_api_defines.PARAM_SIZE - 8))
    ]

# pylint: disable=too-few-public-methods
class CanTpDirectGetResponseCommand(ctypes.Structure):
    """
    Structure Class for 'Can_TpDirect_GetResponse_Command_t'

    Python replica of 'Can_TpDirect_GetResponse_Command_t' in 'host_para_can.h' file
    """
    # defining structure members
    _fields_ = [
        ('Channel', ctypes.c_uint8),
        ('reserved1', ctypes.c_uint8),
        ('reserved2', ctypes.c_uint8),
        ('reserved3', ctypes.c_uint8)
    ]

# pylint: disable=too-few-public-methods
class CanTpDirectGetResponseResponse(ctypes.Structure):
    """
    Structure Class for 'Can_TpDirect_GetResponse_Response_t'

    Python replica of 'Can_TpDirect_GetResponse_Response_t' in 'host_para_can.h' file
    """
    # defining structure members
    _fields_ = [
        ('Channel', ctypes.c_uint8),
        ('LastErrorCode', ctypes.c_uint8),
        ('Flags', ctypes.c_uint8),
        ('State', ctypes.c_uint8),

        ('Length', ctypes.c_uint16),
        ('RemainingLength', ctypes.c_uint16),

        ('Data', ctypes.c_uint8 * (g_api_defines.PARAM_SIZE - 8))
    ]

class GCanNodeBaudrateFdSetCmd(ctypes.Structure):
    """
    Structure Class for 'G_Can_Node_BaudrateFd_Set_Cmd_t'

    Python replica of 'G_Can_Node_BaudrateFd_Set_Cmd_t' in 'g_api_can.h'
    """
    # defining structure members
    _fields_ = [
        ('Flags', ctypes.c_uint32),
        ('BaudRate', ctypes.c_uint32),
        ('SamplePoint_Min', ctypes.c_uint8),
        ('SamplePoint_Max', ctypes.c_uint8),
        ('NumberOfTimeQuanta_Min', ctypes.c_uint8),
        ('NumberOfTimeQuanta_Max', ctypes.c_uint8),
        ('TSeg1_Min', ctypes.c_uint8),
        ('TSeg1_Max', ctypes.c_uint8),
        ('TSeg2_Min', ctypes.c_uint8),
        ('TSeg2_Max', ctypes.c_uint8),
        ('Sjw_Min', ctypes.c_uint8),
        ('Sjw_Max', ctypes.c_uint8),
        ('reserved1', ctypes.c_uint8),
        ('reserved2', ctypes.c_uint8),
        ('TdcOffset', ctypes.c_uint32)
    ]

class GCanNodeBaudrateFdSetRsp(ctypes.Structure):
    """
    Structure Class for 'G_Can_Node_BaudrateFd_Set_Rsp_t'

    Python replica of 'G_Can_Node_BaudrateFd_Set_Rsp_t' in 'g_api_can.h'
    """
    # defining structure members
    _fields_ = [
        ('Flags', ctypes.c_uint32),
        ('BaudRate', ctypes.c_uint32),
        ('CanControllerClock', ctypes.c_uint32),
        ('SamplePoint', ctypes.c_uint8),
        ('NumberOfTimeQuanta', ctypes.c_uint8),
        ('TSeg1', ctypes.c_uint8),
        ('TSeg2', ctypes.c_uint8),
        ('Sjw', ctypes.c_uint8),
        ('reserved1', ctypes.c_uint8),
        ('reserved2', ctypes.c_uint8),
        ('reserved3', ctypes.c_uint8),
        ('TdcOffset', ctypes.c_uint32)
    ]

class GCanUartGatewayInitCmd(ctypes.Structure):
    """
    Structure Class for 'G_Can_UartGateway_Init_Cmd_t'

    Python replica of 'G_Can_UartGateway_Init_Cmd_t' in 'g_api_can.h'
    """
    # defining structure members
    _fields_ = [
        ('Flags', ctypes.c_uint32),
        ('MaxRetries', ctypes.c_uint32),
        ('AckTimeout', ctypes.c_uint32),
        ('UartInstanceType', ctypes.c_uint8),
        ('UartInstanceId', ctypes.c_uint8),
        ('UartParity', ctypes.c_uint8),
        ('reserved', ctypes.c_uint8),
        ('UartBaudRate', ctypes.c_uint32)
    ]

class GCanUartGatewayInitRsp(ctypes.Structure):
    """
    Structure Class for 'G_Can_UartGateway_Init_Rsp_t'

    Python replica of 'G_Can_UartGateway_Init_Rsp_t' in 'g_api_can.h'
    """
    # defining structure members
    _fields_ = [
        ('UartBaudRate_Desired', ctypes.c_uint32),
        ('UartBaudRate_Actual', ctypes.c_uint32)
    ]

class GLvdsSerDesGpioIocPinConfigSetCmd(ctypes.Structure):
    """
    Structure Class for 'G_Lvds_SerDesGpio_IocPinConfig_Set_Cmd_t'

    Python replica of 'G_Lvds_SerDesGpio_IocPinConfig_Set_Cmd_t' in 'g_api_lvds.h'
    """
    # defining structure members
    _fields_ = [
        ('Flags', ctypes.c_uint32),
        ('GpioIndex', ctypes.c_uint8),
        ('IocOutputType', ctypes.c_uint8),
        ('IocOutputMod', ctypes.c_uint8),
        ('reserved', ctypes.c_uint8),
    ]

class GLvdsCommonDataRegisterWriteCmd(ctypes.Structure):
    """
    Structure Class for 'G_Lvds_Common_Data_Register_Write_Cmd_t'

    Python replica of 'G_Lvds_Common_Data_Register_Write_Cmd_t' in 'g_api_lvds.h'
    """
    # defining structure members
    _fields_ = [
        ('Flags', ctypes.c_uint32),
        ('RegisterAddress', ctypes.c_uint16),
        ('DeviceAddress', ctypes.c_uint8),
        ('RegisterValue', ctypes.c_uint8),
        ('NumberOfRegisters', ctypes.c_uint8),
        ('reserved1', ctypes.c_uint8),
        ('reserved2', ctypes.c_uint8),
        ('reserved3', ctypes.c_uint8),
        ('Data', ctypes.c_uint8)
    ]
