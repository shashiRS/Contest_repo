"""
 Copyright 2018 Continental Corporation

 Author:
    - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
    - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>

 File:
    g_api_defines.py

 Details:
    This file contains definitions of Goepel APIs defines
"""

import ctypes

# G_API No Error flag
G_NO_ERROR = 0

# general
MESSAGE_SIZE = 1024
HEADER_SIZE = 12
PARAM_SIZE = MESSAGE_SIZE - HEADER_SIZE

# command codes defined in "host_para_can.h"
CAN_CMD_TP_DIRECT_SET_PROPERTIES = 0x84
CAN_CMD_TP_DIRECT_REQUEST = 0x86
CAN_CMD_TP_DIRECT_GET_RESPONSE = 0x87

# buffer mode parameters for 'G_Can_Monitor_BufferMode_Start' defined in 'g_api_can.h' file
G_CAN__MONITOR__BUFFER_MODE__MODE__NOTHING = ctypes.c_uint8(0x00)
G_CAN__MONITOR__BUFFER_MODE__MODE__RX = ctypes.c_uint8(0x01)
G_CAN__MONITOR__BUFFER_MODE__MODE__TX = ctypes.c_uint8(0x02)
G_CAN__MONITOR__BUFFER_MODE__MODE__TX_AND_RX = ctypes.c_uint8(0x03)
G_CAN__MONITOR__BUFFER_MODE__MODE__ERROR_FRAME = ctypes.c_uint8(0x04)
G_CAN__MONITOR__BUFFER_MODE__MODE__ERROR_FRAME_AND_RX = ctypes.c_uint8(0x05)
G_CAN__MONITOR__BUFFER_MODE__MODE__ERROR_FRAME_AND_TX = ctypes.c_uint8(0x06)
G_CAN__MONITOR__BUFFER_MODE__MODE__ERROR_FRAME_AND_TX_AND_RX = ctypes.c_uint8(0x07)

# address format macros for 'G_Can_Tp_Config_IsoTp_Parameters_t' defined in 'g_api_can.h' file
G_CAN__TP__CONFIG__ISOTP__ADDRESSING_FORMAT__NORMAL = ctypes.c_uint8(0x00)
G_CAN__TP__CONFIG__ISOTP__ADDRESSING_FORMAT__EXTENDED = ctypes.c_uint8(0x01)
G_CAN__TP__CONFIG__ISOTP__ADDRESSING_FORMAT__MIXED = ctypes.c_uint8(0x02)

# command flags for 'G_Can_Tp_Config_IsoTp_Parameters_t' defined in 'g_api_can.h' file
G_CAN__TP__CONFIG__ISOTP__CMD_FLAG__NONE = ctypes.c_uint32(0x00)
G_CAN__TP__CONFIG__ISOTP__CMD_FLAG__USE_OWN_SEPARATION_TIME = ctypes.c_uint32(0x01)
G_CAN__TP__CONFIG__ISOTP__CMD_FLAG__START_SN_WITH_ZERO = ctypes.c_uint32(0x02)
G_CAN__TP__CONFIG__ISOTP__CMD_FLAG__SEPARATION_TIME_BETWEEN_FC_AND_CF = ctypes.c_uint32(0x04)
G_CAN__TP__CONFIG__ISOTP__CMD_FLAG__SET_DLC_TO_NUMBER_OF_USED_BYTES = ctypes.c_uint32(0x08)
G_CAN__TP__ISOTP__FLAG__USE_TIME_BR_BETWEEN_FF_AND_FC = ctypes.c_uint32(0x10)
G_CAN__TP__ISOTP__FLAG__USE_TIME_BR_BETWEEN_CF_AND_FC = ctypes.c_uint32(0x11)

# id mode flags defined in 'g_api_can.h' file
G_CAN__ID_MODE__STANDARD = ctypes.c_uint8(0x00)
G_CAN__ID_MODE__EXTENDED = ctypes.c_uint8(0x01)
G_CAN__ID_MODE__MIXED = ctypes.c_uint8(0x02)

# command flags defined in 'g_api_can.h' file
G_CAN__INIT_INTERFACE__CMD_FLAG__NONE = ctypes.c_uint32(0x00)
G_CAN__INIT_INTERFACE__CMD_FLAG__ENABLE_ANALYZER = ctypes.c_uint32(0x01)
G_CAN__INIT_INTERFACE__CMD_FLAG__ENABLE_BLINKING = ctypes.c_uint32(0x02)
G_CAN__INIT_INTERFACE__CMD_FLAG__DISABLE_NO_ACK_PAUSES = ctypes.c_uint32(0x04)
G_CAN__INIT_INTERFACE__CMD_FLAG__FD_MODE__FD = ctypes.c_uint32(0x08)
G_CAN__INIT_INTERFACE__CMD_FLAG__FD_MODE__TX_FD = ctypes.c_uint32(0x10)
G_CAN__INIT_INTERFACE__CMD_FLAG__FD_MODE__TX_FD_BRS = ctypes.c_uint32(0x20)
G_CAN__INIT_INTERFACE__CMD_FLAG__FD_MODE__TX_NO_FD = ctypes.c_uint32(0x40)

# command flags for 'G_Can_Node_BaudrateFd_Set_CmdFlags_t' defined in 'g_api_can.h' file
G_CAN__NODE__BAUDRATE_FD__SET__CMD_FLAG__NONE = ctypes.c_uint32(0x00)
G_CAN__NODE__BAUDRATE_FD__SET__CMD_FLAG__CHANGE_TDC = ctypes.c_uint32(0x01)
G_CAN__NODE__BAUDRATE_FD__SET__CMD_FLAG__TDC = ctypes.c_uint32(0x02)

# response flags for 'G_Can_Node_BaudrateFd_Set_RspFlags_t' defined in 'g_api_can.h' file
G_CAN__NODE__BAUDRATE_FD__SET__RSP_FLAG__NONE = ctypes.c_uint32(0x00)
G_CAN__NODE__BAUDRATE_FD__SET__RSP_FLAG__FD = ctypes.c_uint32(0x01)
G_CAN__NODE__BAUDRATE_FD__SET__RSP_FLAG__TDC = ctypes.c_uint32(0x02)

# command flags for 'G_Can_UartGateway_Init_CmdFlags_t' defined in 'g_api_can.h' file
G_CAN__UART_GATEWAY__INIT__CMD_FLAG__NONE = 0x00
G_CAN__UART_GATEWAY__INIT__CMD_FLAG__ACK_ENABLE = 0x01
G_CAN__UART_GATEWAY__INIT__CMD_FLAG__UART_PARITY_CHECK_ENABLE = 0x02
G_CAN__UART_GATEWAY__INIT__CMD_FLAG__UART_SW_LOOP_ENABLE = 0x04
G_CAN__UART_GATEWAY__INIT__CMD_FLAG__LENGTH_INCLUSIVE_LENGTH_BYTE = 0x08

# uart instance types for 'G_Can_UartGateway_UartInstanceType_t' defined in 'g_api_can.h' file
G_CAN__UART_GATEWAY__UART_INSTANCE_TYPE__LVDS_CONTROL_CHANNEL = ctypes.c_uint8(0x00)
G_CAN__UART_GATEWAY__UART_INSTANCE_TYPE__UNKNOWN = ctypes.c_uint8(0x01)

# uart parity for 'G_Can_UartGateway_UartParity_t' defined in 'g_api_can.h' file
G_CAN__UART_GATEWAY__UART_PARITY__NONE = ctypes.c_uint8(0x00)
G_CAN__UART_GATEWAY__UART_PARITY__EVEN = ctypes.c_uint8(0x01)
G_CAN__UART_GATEWAY__UART_PARITY__ODD = ctypes.c_uint8(0x02)
G_CAN__UART_GATEWAY__UART_PARITY__UNKNOWN = ctypes.c_uint8(0x03)

# command flags for 'G_Io_InitInterface_CmdFlags_t' defined in 'g_api_io.h' file
G_IO__INIT_INTERFACE__CMD_FLAG__ZERO = 0x00
G_IO__INIT_INTERFACE__CMD_FLAG__RESET_OUTPUTS = 0x01
G_IO__INIT_INTERFACE__CMD_FLAG__RESET_RELAYS = 0x02
G_IO__INIT_INTERFACE__CMD_FLAG__RESET_TRIGGERS = 0x04

# trigger signal destinatons for 'G_Io_Trigger_OutputType_t' defined in 'g_api_io.h' file
G_IO__TRIGGER__OUTPUT_TYPE__UNKNOWN = ctypes.c_uint8(0x00)
G_IO__TRIGGER__OUTPUT_TYPE__TRIGGER_BUS_OUT = ctypes.c_uint8(0x01)
G_IO__TRIGGER__OUTPUT_TYPE__DIGITAL_OUT = ctypes.c_uint8(0x02)
G_IO__TRIGGER__OUTPUT_TYPE__SOFTWARE_IN = ctypes.c_uint8(0x03)
G_IO__TRIGGER__OUTPUT_TYPE__INTERNAL_SIGNAL_IN = ctypes.c_uint8(0x04)
G_IO__TRIGGER__OUTPUT_TYPE__LVDS_GRABBER__START = ctypes.c_uint8(0x05)
G_IO__TRIGGER__OUTPUT_TYPE__LVDS_GRABBER__STOP = ctypes.c_uint8(0x06)
G_IO__TRIGGER__OUTPUT_TYPE__LVDS_0_SER_DES_GPIO = ctypes.c_uint8(0x07)
G_IO__TRIGGER__OUTPUT_TYPE__LVDS_1_SER_DES_GPIO = ctypes.c_uint8(0x08)
G_IO__TRIGGER__OUTPUT_TYPE__LVDS_0_TRIGGER_IN = ctypes.c_uint8(0x09)
G_IO__TRIGGER__OUTPUT_TYPE__LVDS_1_TRIGGER_IN = ctypes.c_uint8(0x0A)
G_IO__TRIGGER__OUTPUT_TYPE__UART_RX = ctypes.c_uint8(0x0B)

# signal source selections for 'G_Io_Trigger_SourceType_t' defined in 'g_api_io.h' file
G_IO__TRIGGER__SOURCE_TYPE__UNKNOWN = ctypes.c_uint8(0x00)
G_IO__TRIGGER__SOURCE_TYPE__TRIGGER_BUS_IN = ctypes.c_uint8(0x01)
G_IO__TRIGGER__SOURCE_TYPE__DIGITAL_IN = ctypes.c_uint8(0x02)
G_IO__TRIGGER__SOURCE_TYPE__SOFTWARE_OUT = ctypes.c_uint8(0x03)
G_IO__TRIGGER__SOURCE_TYPE__MOST_NETWORK_FRAME_CLOCK = ctypes.c_uint8(0x04)
G_IO__TRIGGER__SOURCE_TYPE__TOG = ctypes.c_uint8(0x05)
G_IO__TRIGGER__SOURCE_TYPE__INTERNAL_SIGNAL_OUT = ctypes.c_uint8(0x06)
G_IO__TRIGGER__SOURCE_TYPE__LVDS_VIDEO_LOCK = ctypes.c_uint8(0x07)
G_IO__TRIGGER__SOURCE_TYPE__LVDS_VIDEO_ACTIVE = ctypes.c_uint8(0x08)
G_IO__TRIGGER__SOURCE_TYPE__LVDS_GRABBER_READY = ctypes.c_uint8(0x09)
G_IO__TRIGGER__SOURCE_TYPE__LVDS_GRABBER_COMPLETE = ctypes.c_uint8(0x0A)
G_IO__TRIGGER__SOURCE_TYPE__LVDS_GRABBER_ERROR = ctypes.c_uint8(0x0B)
G_IO__TRIGGER__SOURCE_TYPE__SENT_TRANSMITTER = ctypes.c_uint8(0x0C)
G_IO__TRIGGER__SOURCE_TYPE__CAN_STM_TRIGGER_OUT = ctypes.c_uint8(0x0D)
G_IO__TRIGGER__SOURCE_TYPE__LVDS_0_SER_DES_GPIO = ctypes.c_uint8(0x0E)
G_IO__TRIGGER__SOURCE_TYPE__LVDS_1_SER_DES_GPIO = ctypes.c_uint8(0x0F)
G_IO__TRIGGER__SOURCE_TYPE__LVDS_0_TRIGGER_OUT = ctypes.c_uint8(0x10)
G_IO__TRIGGER__SOURCE_TYPE__LVDS_1_TRIGGER_OUT = ctypes.c_uint8(0x11)
G_IO__TRIGGER__SOURCE_TYPE__UART_TX = ctypes.c_uint8(0x12)
G_IO__TRIGGER__SOURCE_TYPE__INTERNAL_SOURCE = ctypes.c_uint8(0x13)
G_IO__TRIGGER__SOURCE_TYPE__NO_SOURCE = ctypes.c_uint8(0xFF)

# command flags for 'G_Lvds_FrameGrabber_CaptureToBuffer2_Cmd_t' defined in 'g_api_lvds.h' file
G_LVDS__FRAME_GRABBER__CAPTURE_TO_BUFFER_2__CMD_FLAG__NONE = ctypes.c_uint32(0x00)
G_LVDS__FRAME_GRABBER__CAPTURE_TO_BUFFER_2__CMD_FLAG__USE_TIMESTAMP = ctypes.c_uint32(0x01)

# property flags for 'G_Lvds_Common_PropertyId_t' defined in 'g_api_lvds.h' file
G_LVDS__COMMON__PROPERTY_ID__LOCK_STATE = ctypes.c_uint32(0x03)

# command flags for 'G_Lvds_SerDesGpio_IocPinConfig_Set_CmdFlags_t' defined in 'g_api_lvds.h' file
G_LVDS__SER_DES_GPIO__IOC_PIN_CONFIG__SET__CMD_FLAG__NONE = ctypes.c_uint32(0x00)
G_LVDS__SER_DES_GPIO__IOC_PIN_CONFIG__SET__CMD_FLAG__SET_OUTPUT_TYPE = ctypes.c_uint32(0x01)

# output types for 'G_Lvds_SerDesGpio_IocOutputType_t' defined in 'g_api_lvds.h' file
G_LVDS__SER_DES_GPIO__IOC_OUTPUT_TYPE__DISABLED = ctypes.c_uint8(0x00)
G_LVDS__SER_DES_GPIO__IOC_OUTPUT_TYPE__PUSH_PULL = ctypes.c_uint8(0x01)
G_LVDS__SER_DES_GPIO__IOC_OUTPUT_TYPE__OPEN_DRAIN = ctypes.c_uint8(0x02)
G_LVDS__SER_DES_GPIO__IOC_OUTPUT_TYPE__UNKNOWN = ctypes.c_uint8(0x03)

# output types for 'G_Lvds_SerDesGpio_IocOutputMod_t' defined in 'g_api_lvds.h' file
G_LVDS__SER_DES_GPIO__IOC_OUTPUT_MOD__NO_CHANGE = ctypes.c_uint8(0x00)
G_LVDS__SER_DES_GPIO__IOC_OUTPUT_MOD__SET = ctypes.c_uint8(0x01)
G_LVDS__SER_DES_GPIO__IOC_OUTPUT_MOD__CLEAR = ctypes.c_uint8(0x02)
G_LVDS__SER_DES_GPIO__IOC_OUTPUT_MOD__TOGGLE = ctypes.c_uint8(0x03)
G_LVDS__SER_DES_GPIO__IOC_OUTPUT_MOD__UNKNOWN = ctypes.c_uint8(0x04)

# command flags for 'G_Lvds_Common_Config_Set_CmdFlags_t' defined in 'g_api_lvds.h' file
G_LVDS__COMMON__CONFIG__SET__CMD_FLAG__NONE = ctypes.c_uint32(0x00)

# command flags for 'G_Lvds_Common_Data_Register_Write_CmdFlags_t' defined in 'g_api_lvds.h' file
G_LVDS__COMMON__DATA__REG__WR__CMD_FLAG__NONE = 0x00
G_LVDS__COMMON__DATA__REG__WR__CMD_FLAG__REG_ADDR_WIDTH_16_BIT = 0x01
G_LVDS__COMMON__DATA__REG__WR__CMD_FLAG__DEV_ADDR_7_BIT = 0x02
G_LVDS__COMMON__DATA__REG__WR__CMD_FLAG__EXTENDED_DATA = 0x04
G_LVDS__COMMON__DATA__REG__WR__CMD_FLAG__REGISTER_BLOCK = 0x08
