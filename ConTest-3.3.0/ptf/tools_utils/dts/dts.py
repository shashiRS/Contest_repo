"""
    Copyright 2019 Continental Corporation

    :file: dts.py
    :platform: Windows
    :synopsis:
        File containing implementation of DTS related utilities (APIs)

    :author:
        - Praveenkumar G K  <praveenkumar.gomathi.kaliamoorthi@continental-corporation.com>
"""
import logging
from time import sleep

# Try to import the win com API
# This only works on windows or during test execution.
# Also it can be avoided for sphinx doc build
# On windows, the real api is imported, during test execution we provide a mocked api.
# pylint: disable=import-error
try:
    from win32com.client import Dispatch
    import pythoncom
except ImportError:
    pass


# PTF imports
from ptf.verify_utils import ptf_asserts

LOG = logging.getLogger('DTS')


class DtsApp:
    """
    Class is to use DTS tool in automation.
    In order to make use of this application use following example in your setup.pytest file

    Example::

        # to be done in setup.pytest

        # in custom import section
        from ptf.ptf_utils.global_params import get_parameter, set_global_parameter
        from ptf.tools_utils.dts import dts

        # recommended to be done in 'global_setup'
        # creating object of DTS
        dts_app = dts.DtsApp()
        # opening DTS project already created in system configurator of DTS
        dts_app.open_cfg("Example_Project", "VINFO_ExP")
        # setting dts object into "dts" global parameter
        set_global_parameter("dts", dts_app)

        # you can access 'dts' object as follow in setup.pytest, .pytest or .py files
        dts_app = get_parameter("dts")

        # recommended to be done in 'global_teardown'
        # getting dts object
        dts_app = get_parameter("dts")
        # Close the opened project
        dts_app.close()
    """

    def __init__(self):
        # co-initializing as test-runner is running in a separate thread
        pythoncom.CoInitialize()
        # Init automation api of DTS
        self.__dts_auto_api = Dispatch("AutomationAPI.dtsPcAPI")
        # Below will hold the COM object of DTS project opened using method open_project
        # which will be used in many other method.
        self.__project_init = None
        # Execution status OK
        self.execution_ok = 2
        # Error level
        self.error_level_max = 0
        # last error or most recent error
        self.last_error = 0
        # Execution status is pending with intermediate result
        self.exec_pending_with_intermediate_result = 5

    @staticmethod
    def __covering_req_resp_str(read_buffer):
        """
        Method is to convert the read buffer into a string.

        :param memory view object read_buffer: request or response buffer
        :return: ret diagnostic request or response string
        :rtype string
        """
        # getting read_buffer into list
        read_buffer_dec_list = read_buffer.tolist()
        # converting read_buffer list from decimal to hex
        read_buffer_hex = list(hex(value)[2:] for value in read_buffer_dec_list)
        # Converting list in hex to string inline with CANoe api
        ret = " ".join(map(str, read_buffer_hex))
        return ret

    def open_cfg(self, project_name, vit_name):
        """
        Method to open or init given DTS project.

        :param string project_name: Name of DTS project already created in system configurator of
            DTS.
        :param string vit_name: Vehicle information table of the given project.

        Example::

            # opening DTS project already created and mapped in system configurator of DTS
            # Below can be performed in global_setup() of setup.pytest
            dts_app.open_cfg("Example_Project", "VINFO_ExP")

        """
        # closing the existing opened project
        if self.__project_init:
            self.close()
        try:
            # Init DTS project
            self.__project_init = self.__dts_auto_api.dtsInit_UC(project_name, vit_name)
        except pythoncom.com_error:
            ptf_asserts.verify(True, False,
                               self.__dts_auto_api.getError(self.last_error, self.error_level_max))

    def __load_access_path(self, logical_link):
        """
        Loading access path with given logical link (which is similar to diag node)

        :param string logical_link: name of the logical link
        :return access_path
        :rtype access_path DTS object
        """
        access_path = None
        try:
            access_path = self.__project_init.loadAccessPath(logical_link)
        # handling exception raised by pythoncom
        except pythoncom.com_error:
            ptf_asserts.verify(True, False,
                               self.__dts_auto_api.getError(self.last_error,
                                                            self.error_level_max))
        return access_path

    def __release_access_path(self, access_path):
        """
        Method is used to release access path which is loaded already

        :param Access Path object access_path: access path object
        """
        try:
            self.__project_init.releaseAccessPath(access_path)
        # handling exception raised by pythoncom
        except pythoncom.com_error:
            ptf_asserts.verify(True, False,
                               self.__dts_auto_api.getError(self.last_error,
                                                            self.error_level_max))

    def send_diag_cmd_via_id(self, service_id, logical_link, security_access_req=None,
                             time_out=5):
        """
        Method is to send diagnostic command from database and return response

        :param string service_id: service_id needs to be executed from database
        :param string logical_link: logical link to connect.
        :param string security_access_req: if security_access needed. Provide short name
         of job needs to be executed before actual service id execution.
        :param int time_out: time_out for execution operation (Default: 5 s)
        :returns: diagnostics response
        :rtype: string

        Example::

            # sending diag request
             response = dts.send_diag_cmd_via_id(
                        "ReadDataByIdentifier_GeneralECM_Coding", "LL_ECM_UDS",
                        security_access_req="ChangeAuthenticatedState")
        """
        access_path = self.__load_access_path(logical_link)
        # variable return response
        response = None
        try:
            # check for security_access_req
            if security_access_req:
                self.__service_job_helper(security_access_req, access_path, time_out)
            routine_uc = self.__service_job_helper(service_id, access_path, time_out)
            # reading request buffer
            request_buffer = routine_uc.getRequestBuffer()
            request = self.__covering_req_resp_str(request_buffer)
            LOG.info("Requested Service_name: %s", service_id)
            LOG.info("Tx: %s", request)
            # reading result buffer(Response)
            response_buffer = routine_uc.getResultBuffer()
            response = self.__covering_req_resp_str(response_buffer)
            LOG.info("Rx: %s", response)
        # handling exception raised by pythoncom
        except pythoncom.com_error:
            ptf_asserts.verify(True, False,
                               self.__dts_auto_api.getError(self.last_error, self.error_level_max))
        finally:
            # releasing temp logical link
            self.__release_access_path(access_path)
        return response

    def __service_job_helper(self, job_name, access_path, time_out):
        """
        Method to perform given diagnostics service or job execution.

        :param string job_name: diagnostics job need to be executed
        :param access_path_obj access_path: logical link access path object
        :param int time_out: execution time out in seconds
        :return routine_UC: routine_UC DTS object of the job execution
        :rtype routine_UC object
        """
        # Below identifies AccessPath/LogicalLink
        access_path.variantIdentificationAndSelection()
        # getting routine UC
        routine_uc = access_path.getRoutineUC()
        # setting service (Diag command)  needs to be executed
        routine_uc.setService(job_name)
        # Executing the service
        routine_uc.execute()
        # waiting until request is finished executing
        routine_uc.waitUntilFinished(time_out * 1000)
        # Verifying routine_uc.execute() state whether OK
        # Delay: Since routine_uc.getExecState() takes some delay to update NOK or OK status
        # Adding maximum loop time as time_out, in order to avoid endless loop.
        while routine_uc.getExecState() == self.exec_pending_with_intermediate_result:
            # 100 ms sleep
            sleep(0.1)
            time_out -= 0.1
            if time_out <= 0:
                break
        ptf_asserts.verify(routine_uc.getExecState(), self.execution_ok,
                           "diag_job: {} execution is not successful".format(job_name))
        LOG.info("diag_job: %s executed successfully", job_name)
        return routine_uc

    def __flash_job_helper(self, flash_job_name, flash_session, access_path, time_out):
        """
         Flashing job helper method

        :param string flash_job_name: Name of the flashing job from database
        :param string flash_session: Name of the flashing session from database
        :param access_path_obj access_path: logical link access path object
        :param int time_out: Flashing time out in seconds
        """
        # Below identifies AccessPath/LogicalLink
        access_path.variantIdentificationAndSelection()
        # getting routine UC
        routine_uc = access_path.getRoutineUC()
        routine_uc.setFlashJob(flash_job_name, flash_session)
        routine_uc.execute()
        # waiting until request is finished executing
        routine_uc.waitUntilFinished(time_out * 1000)
        # Verifying routine_uc.execute() state whether OK
        # Delay: Since routine_uc.getExecState() takes some delay to update NOK or OK status
        # Adding maximum loop time as time_out, in order to avoid endless loop.
        while routine_uc.getExecState() == self.exec_pending_with_intermediate_result:
            # 100 ms sleep
            sleep(0.1)
            time_out -= 0.1
            if time_out <= 0:
                break
        ptf_asserts.verify(routine_uc.getExecState(), self.execution_ok,
                           "Flashing execution is not successful")
        LOG.info("Flashing successfully")

    def flash_job(self, flash_job_name, flash_session, logical_link,
                  security_access_req=None, time_out=300):
        """
        Method for flashing of ECU over DTS tool

        :param string flash_job_name: Name of the flashing job from database.
        :param string flash_session: Name of the flashing session from database.
        :param string logical_link: logical link to connect.
        :param string security_access_req: if security_access needed. Provide short name
         of job needs to be executed before actual flashing.
         Provide authentications job name here (Default is None)
        :param int time_out: time out for flashing job (Default is 300 secs)

         Example::

            # Flashing
            dts.flash_job("WVC_FlashProg", "2239021800_001_192309", "logical_link"
             security_access_req="ChangeAuthenticatedState", time_out=500)

        """
        access_path = self.__load_access_path(logical_link)
        try:
            # check for security_access_req
            if security_access_req:
                # taking security_access
                self.__service_job_helper(security_access_req, access_path, time_out)
            # flashing execution
            LOG.info("Flashing ...")
            self.__flash_job_helper(flash_job_name, flash_session, access_path, time_out)
        # handling exception raised by pythoncom
        except pythoncom.com_error:
            ptf_asserts.verify(True, False,
                               self.__dts_auto_api.getError(self.last_error, self.error_level_max))
        finally:
            # releasing temp logical link
            self.__release_access_path(access_path)

    def close(self):
        """
        Method to close the opened project

        Example::

            # Closing of project which can be performed in global_teardown() of setup.pytest
            dts_app.close()
        """
        try:
            # Closing project
            self.__dts_auto_api.dtsEnd(self.__project_init)
        # handling exception raised by pythoncom
        except pythoncom.com_error:
            ptf_asserts.verify(True, False,
                               self.__dts_auto_api.getError(self.last_error, self.error_level_max))
