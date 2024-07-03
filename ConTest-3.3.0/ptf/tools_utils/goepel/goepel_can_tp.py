"""
 Copyright 2018 Continental Corporation

 Author:
    - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
    - Melchior Rabe <Melchior.Rabe@continental-corporation.com>

 File:
    goepel_can_tp.py

 Details:
    This file implements a CAN-TP APIs supported by Goepel API.
    CAN-TP (ISO-TP i.e. sending data packets over CAN-bus over 8 byte payload of CAN using multiple
    frames concept)
"""

# standard python imports
import ctypes
import threading

# custom imports
from ptf.tools_utils.goepel import g_api_structs
from ptf.tools_utils.goepel import g_api_defines
from ptf.tools_utils.goepel import goepel_common
from ptf.tools_utils.goepel.goepel_can import GoepelCan

LOG = goepel_common.LOG

class GoepelCanTp(GoepelCan):
    """
    Class that provides a CAN TP connection using a Goepel CAN interface.

    .. note::
        If the CONTEST shall support also basic CAN functions this class should inherit some basic
        functions from a parent class.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self._response_callback = None
        self.response_reception_thread = None
        self.thread_remove_flag = False
        self._channel = ctypes.c_uint8(-1)

    def configure_iso_tp(self, phy_src_id=0x00, phy_trg_id=0x00):
        """
        Method for configuring and verifying CAN-TP parameters

        :param hex phy_src_id: Source physical ID (Goepel device)
        :param hex phy_trg_id: Target physical ID (ECU or Core)

        Example::

            # assuming 'g_can_tp' is the object name
            # configuring CAN-TP with custom source and target IDs
            g_can_tp.configure_iso_tp(phy_src_id=0x3E, phy_trg_id=0x3C1)
        """
        # creating a structure with defined values of members for iso_tp params of can_tp
        iso_tp_params = g_api_structs.GCanTpConfigIsoTpParameters(
            PhysicalSourceAddress=0,
            PhysicalTargetAddress=0,
            FunctionalSourceAddress=0,
            FunctionalTargetAddress=0,
            PhysicalSourceId=phy_src_id,
            PhysicalTargetId=phy_trg_id,
            FunctionalSourceId=0x0,
            FunctionalTargetId=0x0,
            PhysicalAddressingFormat=0,
            FunctionalAddressingFormat=0,
            BlockSize=2,
            SeparationTime=10,
            Flags=g_api_defines.G_CAN__TP__CONFIG__ISOTP__CMD_FLAG__NONE,
            OwnSeparationTime=0,
            reserved1=0,
            reserved2=0,
            reserved3=0,
            TimeoutAs=1000,
            TimeoutAr=1000,
            TimeoutBs=1000,
            TimeoutCr=1000,
            TimeBrBetweenFfAndFc=0,
            TimeBrBetweenCfAndFc=0
        )

        # creating a structure with defined values of members for direct_iso_tp params of can_tp
        direct_iso_tp_params = g_api_structs.CanTpDirectSetPropertiesCommand(
            Channel=self._channel.value,
            Type=0x01,
            Flags=0x00
        )

        # configuring the multi-session channel as opened above for the transport protocol "ISO_TP"
        ret_code = self.goepel_dlls["g_api_can"].G_Can_Tp_Config_IsoTp(
            self.port_handle.value,
            self._channel.value,
            ctypes.byref(iso_tp_params)
        )
        self.check_return_code(ret_code)
        LOG.info("ISO-TP protocol configured")

        # settings ISO-TP direct protocol properties
        ret_code = self.goepel_dlls["g_api"].G_Command(
            self.port_handle,
            g_api_defines.CAN_CMD_TP_DIRECT_SET_PROPERTIES,
            ctypes.byref(direct_iso_tp_params),
            ctypes.sizeof(direct_iso_tp_params)
        )
        self.check_return_code(ret_code)
        LOG.info("ISO-TP direct properties are set")

    def register_message_callback(self, callback):
        """
        Method for registering a function to be called back once a response is received from target.
        This function also triggers a thread which monitors the ECU response in parallel or
        asynchronously.

        :param object callback: Callback function (object) to be executed once target responds to
            a request
        """
        if self._response_callback:
            LOG.warning("Message callback already registered with name '%s'. "
                        "Remove it first to re-register another.", self._response_callback.__name__)
        else:
            self._response_callback = callback
            LOG.info("Message callback registered '%s'", self._response_callback.__name__)
            # starting thread for collecting response(s) from ECU while other activities can be done
            # hence simulating non-blocking/asynchronous functionality
            self.response_reception_thread = threading.Thread(
                # assigning 'self._monitoring_thread' method as target for thread. In this method
                # 'G_CommandWithResponse will be sent and response received from ECU will be
                # processed in registered callback function
                target=self._monitoring_thread
            )
            # start of thread
            self.response_reception_thread.start()
            # making thread remove flag false in order to monitor response infinitely.
            self.thread_remove_flag = False

    def remove_message_callback(self):
        """
        Method for removing/un-registering response callback function. Moreover, this function stops
        the monitoring thread.
        """
        registered_function = self._response_callback.__name__
        self._response_callback = None
        LOG.info("Message callback '%s' unregistered", registered_function)
        # to stop the monitoring thread execution
        self.thread_remove_flag = True
        # join all forked thread/sub-thread
        self.response_reception_thread.join()

    def _monitoring_thread(self):
        """
        Method for monitoring response from target.

        This method runs in a separate thread (in parallel). Its execution starts when a function
        is registered using 'register_message_callback' method. This thread is stopped only when
        'remove_message_callback' is called explicitly.
        """
        # assigning channel to response command
        response_params = g_api_structs.CanTpDirectGetResponseCommand(
            Channel=self._channel.value
        )
        # initializing structure in which response from ECU will be stored
        response_struct = g_api_structs.CanTpDirectGetResponseResponse()

        # waiting for response
        while True:
            # it's important to refresh response length here otherwise Goepel device will re-write
            # it and we'll run short of response buffer size
            response_length = ctypes.c_int32(256)

            # fetching response from ECU
            ret_code = self.goepel_dlls["g_api"].G_CommandWithResponse(
                self.port_handle,
                g_api_defines.CAN_CMD_TP_DIRECT_GET_RESPONSE,
                ctypes.byref(response_params),
                ctypes.sizeof(response_params),
                ctypes.byref(response_struct),
                ctypes.byref(response_length)
            )
            self.check_return_code(ret_code)
            # execute callback only when target responds i.e. response length is greater than 1
            if response_struct.Length == 0:
                pass
            else:
                self._response_callback(response_struct)

            # if thread remove flag is high then break this thread
            if self.thread_remove_flag:
                break

    def send_message(self, byte_msg):
        """
        Method for sending a message to target

        This method sends a request message to target. The response of this request message is
        received by the monitoring thread asynchronously.

        :param bytearray byte_msg: Message (CAN-TP Payload Data) to be sent to target

        Example::

            # assuming 'g_can_tp' is the object name
            # registering a function to be called when target responds
            g_can_tp.register_message_callback(handle_response)
            # sending a command to target
            g_can_tp.send_message("00 00 00")
            # here user can do anything in parallel while response is fetched from target
            print("Hello World !!")
            # removing target response callback handling function
            g_can_tp.remove_message_callback()
        """
        msg_length = len(byte_msg)

        # setting-up request command parameters
        request_params = g_api_structs.CanTpDirectRequestCommand(
            Channel=self._channel.value,
            Flags=0,
            Send=1,
            Concatenate=0,
            Length=msg_length
        )
        # copying request message bytes to request_params "Data" array
        ctypes.memmove(request_params.Data, byte_msg, msg_length)

        # sending message to target (ECU) using set request parameters
        ret_code = self.goepel_dlls["g_api"].G_Command(
            self.port_handle,
            g_api_defines.CAN_CMD_TP_DIRECT_REQUEST,
            ctypes.byref(request_params),
            ctypes.sizeof(request_params)
        )
        self.check_return_code(ret_code)
        LOG.info("Message Sent")
