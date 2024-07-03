"""
    Copyright 2019 Continental Corporation

    :file: goepel_lvds.py
    :platform: Windows
    :synopsis:
        This package provides lvds api. It provides the possibility to interact with
        Goepel lvds devices.

    :author:
        - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""

# ignoring top level import as pip installer checker need to be above imports
import ctypes
import os
import time

import numpy as np
from PIL import Image

# custom imports
from ptf.tools_utils.goepel import g_api_defines, g_api_structs, goepel_common
from ptf.tools_utils.goepel.goepel_common import GoepelCommon
from ptf.verify_utils import ptf_asserts

LOG = goepel_common.LOG


class GoepelLVDS(GoepelCommon):
    """
    Class that provides a LVDS controlling api using Goepel LVDS hardware.
    """

    def __init__(self, interface_name='LVDS1'):
        """
        Creates a new lvds controller for goepel devices.

        :param str interface_name: The device name to use. Check Goepel HW explorer.

        Example::

            # creating a controller for LVDS2 device
            g_lvds = GoepelLVDS(interface_name="LVDS2")
        """
        super().__init__()

        self.open_interface(interface_name)

    def configure_by_file(self, filename):
        """
        Loads lvds device configuration from a given file.

        :param str filename: The file to load. Can be both a relative or absolute path.

        Example::

            # load lvds configuration
            g_lvds.configure_by_file("6222_RVS231_1920x1080_Conti.xml")
        """
        ptf_asserts.verify(os.path.exists(filename), True,
                           "File '{}' not found. Please make sure you set the correct path."
                           .format(filename))

        ret_code = self.goepel_dlls["g_api_lvds"].G_Lvds_Common_Config_Set(
            self.port_handle.value,
            g_api_defines.G_LVDS__COMMON__CONFIG__SET__CMD_FLAG__NONE,
            ctypes.c_char_p(filename.encode('utf-8'))
        )
        self.check_return_code(ret_code)
        LOG.info("Configuration loaded")

    def send_i2c_from_file(self, filename):
        """
        Sends i2c commands from a given file. The file needs to be compatible with the Goepel
        javascript command 'G.vLVDS_sendI2CFromFile(file)'.
        For details, please contact goepel support.

        :param str filename: The file to load. Can be absolute or relative path.

        Example::

            # send i2c commands from file
            g_lvds.send_i2c_from_file("MAX9296_95_Cfg_for_RVS231.txt")
        """

        ptf_asserts.verify(os.path.exists(filename), True,
                           "File '{}' not found. Please make sure you set the correct path."
                           .format(filename))

        # Read the whole file
        for line in open(filename):
            # The '#' indicates a comment, cut everything afterwards
            line = line.split('#')[0]
            # Remove leading/tailing whitespaces
            line = line.strip()

            # Check if there is still something left to process
            if line:
                # Split the values. Variable names reverse engineered from example file,
                # for details check goepel support.
                device_address, register_address, register_value, use_7bit_device_address, \
                    use_16bit_register_address, _, waittime = line.split(',')

                # Build together the flags
                flags = g_api_defines.G_LVDS__COMMON__DATA__REG__WR__CMD_FLAG__NONE
                if use_7bit_device_address == '1':
                    flags = flags | \
                        g_api_defines.G_LVDS__COMMON__DATA__REG__WR__CMD_FLAG__DEV_ADDR_7_BIT
                if use_16bit_register_address == '1':
                    flags = flags | \
                        g_api_defines.G_LVDS__COMMON__DATA__REG__WR__CMD_FLAG__REG_ADDR_WIDTH_16_BIT

                # Build up the cmd to send
                cmd = g_api_structs.GLvdsCommonDataRegisterWriteCmd()
                cmd.Flags = ctypes.c_uint32(flags)
                cmd.RegisterAddress = ctypes.c_uint16(int(register_address, 0))
                cmd.DeviceAddress = ctypes.c_uint8(int(device_address, 0))
                cmd.RegisterValue = ctypes.c_uint8(int(register_value, 0))

                # Send cmd and check return code
                ret_code = self.goepel_dlls["g_api_lvds"].G_Lvds_Common_Data_Register_Write(
                    self.port_handle.value,
                    ctypes.byref(cmd)
                )
                self.check_return_code(ret_code)

                # Wait defined time until next line is parsed
                time.sleep(int(waittime, 0) / 1000)

        LOG.info("Sent to i2c successful")

    def start_capturing(self):
        """
        Start capturing on the interface.

        Example::

            # start capturing
            g_lvds.start_capturing()
        """
        ret_code = self.goepel_dlls["g_api_lvds"].G_Lvds_FrameGrabber_StartCapturing(
            self.port_handle.value
        )
        self.check_return_code(ret_code)
        LOG.info("Capturing started ...")

    def stop_capturing(self):
        """
        Stop capturing on the interface.

        Example::

            # stop capturing
            g_lvds.stop_capturing()
        """
        ret_code = self.goepel_dlls["g_api_lvds"].G_Lvds_FrameGrabber_StopCapturing(
            self.port_handle.value
        )
        self.check_return_code(ret_code)
        LOG.info("Capturing stopped ...")

    def get_lock_state(self):
        """
        Read the lock state of the interface. Usually should be True for successful capturing.

        :return: The lock state.
        :rtype: bool

        Example::

            # get the lock state
            lock_state = g_lvds.get_lock_state()
        """
        length = ctypes.c_uint32(1)
        value = ctypes.c_uint8()
        ret_code = self.goepel_dlls["g_api_lvds"].G_Lvds_Common_Property_GetById(
            self.port_handle.value,
            g_api_defines.G_LVDS__COMMON__PROPERTY_ID__LOCK_STATE,
            ctypes.byref(length),
            ctypes.byref(value)
        )
        self.check_return_code(ret_code)
        return value.value == 1

    def set_ser_des_gpio_ioc_pin_config(self, flags, gpio_index, ioc_output_type, ioc_output_mod):
        """
        Method to set the input/output controller pin configuration of the
        serializer/deserializer board.

        :param ctypes.c_uint32 flags: One of 'G_Lvds_SerDesGpio_IocPinConfig_Set_CmdFlags_t'
                                      defined in g_api_defines.py
        :param int gpio_index: SerDes GPIO number (starting with 0)
        :param ctypes.c_uint8 ioc_output_type: Output type of the SerDes GPIO.
                                               One of 'G_Lvds_SerDesGpio_IocOutputType_t'
                                               defined in g_api_defines.py
        :param ctypes.c_uint8 ioc_output_mod: Output modification action of the selected
                                              input/output controller pin. One of
                                              'G_Lvds_SerDesGpio_IocOutputMod_t' defined
                                              in g_api_defines.py

        Example::

            # configure for camera usage
            g_lvds.set_ser_des_gpio_ioc_pin_config(
                g_api_defines.G_LVDS__SER_DES_GPIO__IOC_PIN_CONFIG__SET__CMD_FLAG__SET_OUTPUT_TYPE,
                5,
                g_api_defines.G_LVDS__SER_DES_GPIO__IOC_OUTPUT_TYPE__OPEN_DRAIN,
                g_api_defines.G_LVDS__SER_DES_GPIO__IOC_OUTPUT_MOD__NO_CHANGE
            )
        """
        cmd = g_api_structs.GLvdsSerDesGpioIocPinConfigSetCmd()
        cmd.Flags = flags
        cmd.GpioIndex = ctypes.c_uint8(gpio_index)
        cmd.IocOutputType = ioc_output_type
        cmd.IocOutputMod = ioc_output_mod

        ret_code = self.goepel_dlls["g_api_lvds"].G_Lvds_SerDesGpio_IocPinConfig_Set(
            self.port_handle.value,
            ctypes.byref(cmd)
        )
        self.check_return_code(ret_code)

    def get_single_image_raw(self, with_timestamp=False):
        """
        Reads a single frame from lvds device and returns the raw data captured.
        Capturing needs to be started using start_capturing() function.

        :param bool with_timestamp: If the timestamp of the frame should also be returned.

        :return: A tuple of data, length and timestamp. Data is an array of the raw data buffer,
            length is the length of returned data in bytes. Timestamp is either the timestamp
            of the image in nanoseconds (with_timestamp=True) or -1.
        :rtype: (Array[c_char], int, int)

        Example::

            # Start capturing and read raw image with timestamp
            g_lvds.start_capturing()
            data, frame_size, timestamp = g_lvds.get_single_image_raw(True)
        """

        # Initialize the buffer with the maximum currently supported frame size.
        # This is currently video dragon II with 4k video (4096 x 2160 resolution).
        # So final buffer size is 4096 x 2160 x 3 colors per pixel = 26542080 bytes.
        data = ctypes.create_string_buffer(26542080)
        length = ctypes.c_uint32(len(data))
        timestamp = ctypes.c_uint64()

        flag = g_api_defines.G_LVDS__FRAME_GRABBER__CAPTURE_TO_BUFFER_2__CMD_FLAG__NONE
        if with_timestamp:
            flag = g_api_defines.G_LVDS__FRAME_GRABBER__CAPTURE_TO_BUFFER_2__CMD_FLAG__USE_TIMESTAMP

        ret_code = self.goepel_dlls["g_api_lvds"].G_Lvds_FrameGrabber_CaptureToBuffer2(
            self.port_handle.value,
            ctypes.byref(flag),
            ctypes.byref(timestamp),
            data,
            ctypes.byref(length)
        )
        self.check_return_code(ret_code)

        if with_timestamp:
            return data, length.value, timestamp.value

        return data, length.value, -1

    def get_single_image(self, img_size_x, img_size_y, bit_depth, with_timestamp=False):
        """
        Reads a single frame from lvds device and returns an Image.
        Capturing needs to be started using start_capturing() function.

        :param int img_size_x: The size in horizontal direction of the image
        :param int img_size_y: The size in vertical direction of the image
        :param int bit_depth: The depth of the image in bit per pixel
        :param bool with_timestamp: If the timestamp of the frame should also be read
        :return: A tuple of the image and timestamp.
                 Timestamp is in nanoseconds (if with_timestamp=True) or -1
        :rtype: (Image, int)

        Example::

            # Start capturing, read image and timestamp and show the image.
            g_lvds.start_capturing()
            img, timestamp = g_lvds.get_single_image(1920, 1080, 24, True)
            img.show()
        """
        data, frame_size, timestamp = self.get_single_image_raw(with_timestamp)

        # create matrix from image buffer
        img_raw = np.frombuffer(data, dtype=np.uint8, count=frame_size)
        # third parameter is in bytes, so we need to convert the bits into bytes
        img_raw = np.reshape(img_raw, (img_size_y, img_size_x, int(bit_depth / 8)))
        # make rgb from bgr
        img_raw = img_raw[..., ::-1]
        # create (pillow) image from matrix
        img = Image.fromarray(img_raw)

        return img, timestamp
