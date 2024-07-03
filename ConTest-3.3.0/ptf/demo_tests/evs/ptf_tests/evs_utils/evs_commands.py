"""
 Copyright 2018 Continental Corporation

 Author:
    M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>

 File:
    evs_commands.py

 Details:
    This file contains commands supported by EVS software
"""

# software version reading commands
RH850_SW_VERSION = bytes([0x2D, 0x01, 0x00, 0x01, 0x00, 0x35,
                          0x0B, 0x00, 0x04, 0x00, 0xA2, 0x06, 0x00])

AURIX_SW_VERSION = bytes([0x2D, 0x01, 0x00, 0x01, 0x00, 0x35,
                          0x01, 0x00, 0x02, 0x00, 0xA2, 0x06, 0x00])
