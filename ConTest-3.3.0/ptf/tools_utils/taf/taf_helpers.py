#!/usr/bin/env python
"""
    Copyright 2020 Continental Corporation

    :file: taf_helpers.py
    :platform: Windows
    :synopsis:
        File containing implementation of TAF related utilities (APIs)

    :author:
        - Berger, Andras (uib44246) <andras.berger@continental-corporation.com>
"""

# ignoring top level import as pip installer checker need to be above imports
import logging
import os
import re
import sys
import time
from argparse import Namespace
from enum import Enum
from threading import Timer

# ConTest
from contest_verify.verify import contest_asserts

import ptf.tools_utils.lauterbach.lauterbach as lauterbach_util
from ptf.ptf_utils.global_params import set_global_parameter
from ptf.tools_utils.canoe import canoe

# TAF
try:
    from custom_events.taf_custom_event import log_event
    from robot_libs.flashing import Flashing
    from robot_libs.reporting import Reporting
    from robot_libs.testrun import Testrun
    from robot_libs.workspace_preparator import WorkspacePreparator
    from run_trace32_test_modules import KeycodeHandler, TRACE32Startup  # , ExceptionHandler
    from RunTRACE32TestModules import prepare_log_folder, setup_environment
    from tools.command import set_stream
    from tools.process import kill_processes
    from tools.utils import TxSelfAckError, check_tx_self_ack, delete_file
    from trace32_libs.config import BaseConfig, ProjConfig, ProjectConfigDependingEnvVars
except ImportError as import_err:
    # ignore the error if "CONTEST_DOC_BUILDER" env variable is not present, the presence of this variable indicates
    # that this script will be used for documentation generation
    if "CONTEST_DOC_BUILDER" not in os.environ:
        raise RuntimeError(
            "'cip_taf_automation_utils' Python modules missing. "
            "(1) Install 'cip_taf_automation_utils' by running 'get_externals.ps1' and "
            "(2) use the '-e' parameter to specify the path to the Python modules "
            "e.g. '-e <WS>\\DebugScripts\\TAF\\05_Testing\\06_Test_Tools\\Automation_Utils\\Python' "
            "to start ConTest."
        ) from import_err


LOG = logging.getLogger("TAF")
Verdicts = {"PASS": 0, "FAIL": 1, "ERROR": 2, "ERROR_TIMEOUT": 3}
CANOE_DELAY_FINISH = 10


class TafHelper:  # pylint: disable=too-many-instance-attributes
    """Helper class for TAF Canoe and Trace32"""

    class TestType(Enum):
        """Available test types"""

        NOTEST = 0
        TRACE32 = 1
        CANOE = 2
        FLASHING_T32 = 3
        FLASHING_XCP = 4
        FLASHING_FLASHTOOL = 5
        FLASHING_PCAT = 6

    def __init__(self, taf_config, is_bricks=False):
        self.taf_config = taf_config
        self.prj_config_json_file_path = None
        self.t32_startup_script = None
        self.t32_base_path = None
        self.canoe_cfg_path = None
        self.t32_version = None
        self.t32_apps = None
        self.t32_cfgs = None
        self.t32_project = None
        self.t32_target_controller = None
        self.t32_target_controller_name = None
        self.elf_file_names = None
        self.elf_file_path = None
        self.relay_target_state = None
        self.t32_logdir = None
        self.skip_on_failure = False
        # ConTest redirects the stream, need to set it again (will point to the captured stream,
        # instead of console)
        set_stream(sys.stdout)
        # Instantiate TAF Robot keyword libraries with the configuration (robot independent mode)
        self.workspace_preparator = WorkspacePreparator(taf_config)
        self.flashing = Flashing(taf_config)
        self.testrun = Testrun(taf_config)
        self.reporting = Reporting(taf_config)
        self.project_config = None
        self.base_config = None
        self.trace32_startup = None

        self.is_bricks = is_bricks

        self.test_type = self.TestType.NOTEST

    def init_canoe(self, canoe_cfg_path):
        """
        Init CANoe parameters

        :param string canoe_cfg_path: Canoe configuration path
        """
        self.canoe_cfg_path = canoe_cfg_path

    def init_t32(
        self,
        prj_config_json_file_path,
        t32_base_path=None,
        t32_version=None,
        t32_apps=None,
        t32_cfgs=None,
        t32_project=None,
        t32_target_controller=None,
        t32_target_controller_name=None,
        elf_file_names=None,
        elf_file_path=None,
    ):
        # pylint: disable=too-many-arguments
        """
        Init T32 parameters

        :param string prj_config_json_file_path: Relative path of the project configuration .json
            file. Base path shall be the project workspace. E.g. "conf\\T32_TAF_ProjectConfig.json"

        Following parameters are only applicable in the old TRACE32-TAF framework (IMS) use case

        :param string t32_base_path: Path to the main T32 directory, i.e.: C:\\Tools\\T32
        :param string t32_version: The T32 version string, i.e: T32_R_2017_09_000092037
        :param list t32_apps: List of absolute paths to the T32 executables,
            the one for master instance must be the first one, i.e.:
            C:\\Tools\\T32\\T32_R_2017_09_000092037\\bin\\windows64\\t32marm.exe
            C:\\Tools\\T32\\T32_R_2017_09_000092037\\bin\\windows64\\t32marm64.exe
        :param list t32_cfgs: List of path to the T32 configuration files,
            the one for master instance must be the first one, i.e.:
            startup\\Component\\R-CarV3H\\startup_config_C0.t32
            startup\\Component\\R-CarV3H\\startup_config_A53_C1.t32
        :param string t32_project: The project name in the TAF T32 framework, i.e.: MFC500
        :param string t32_target_controller: The target controller in the TAF T32 framework,
            i.e.: Controller1
        :param string t32_target_controller_name: The target controller in the TAF T32
            framework, i.e.: R-CarV3H
        :param list elf_file_names: List of elf files for the TAF T32 framework
        :param list elf_file_path: The path of elf files for the TAF T32 framework
        """
        self.prj_config_json_file_path = prj_config_json_file_path
        self.t32_base_path = t32_base_path
        self.t32_version = t32_version
        self.t32_apps = t32_apps
        self.t32_cfgs = t32_cfgs
        self.t32_project = t32_project
        self.t32_target_controller = t32_target_controller
        self.t32_target_controller_name = t32_target_controller_name
        self.elf_file_names = elf_file_names
        self.elf_file_path = elf_file_path
        self.setup_taf_trace32_env()

    def start_canoe(self, start_simulation=True):
        """
        Open CANoe and start the measurement

        :param bool start_simulation: Whether to start the simulation
        """
        canoe_app = None
        if self.skip_on_failure:
            # The verdict of ConTest test cases is set to FAIL if their execution was skipped
            # on purpose.
            contest_asserts.fail(
                "CANoe test cases execution was skipped due to "
                "an unstable result of a test case which has set the "
                "'skip_on_failure_request' flag to True"
            )

        canoe_app = canoe.Canoe()
        # Avoid save-dialog on previously opened CANoe configuration
        canoe_app.suppress_save_cfg = True
        canoe_app.open_cfg(cfg_name=os.path.join(self.taf_config["WORKSPACE"], self.canoe_cfg_path))
        try:
            check_tx_self_ack(canoe_app._get_general_setup_object())  # pylint: disable=protected-access
        except TxSelfAckError as exc:
            LOG.error("Error %s", exc)
            canoe_app.close()
            contest_asserts.fail(error_str="TxSelfACK is enabled in CANoe hardware configuration")

        if start_simulation:
            canoe_app.disable_all_test_modules()
            canoe_app.start_simulation()
        set_global_parameter("canoe", canoe_app, overwrite=True)
        return canoe_app

    def run_canoe_tests(self, testmodules, verify=True):
        """
        Run CANoe tests

        :param list testmodules: A list containing the xml testmodules
        """
        self.test_type = self.TestType.CANOE
        self.testrun.power_supply_control("on")
        failed = False
        canoe_app = None
        try:
            # CANoe setup
            canoe_app = self.start_canoe(start_simulation=False)
            canoe_app.disable_all_test_modules()

            verify_testmodules = [module if isinstance(module, tuple) else (module, verify) for module in testmodules]
            canoe_app.enable_test_modules([module for module, _ in verify_testmodules])

            canoe_app.start_simulation()
            # CANoe testrun
            for testmodule, verify_flag in verify_testmodules:
                try:
                    canoe_app.run_test_module(testmodule, verify=verify_flag)
                except contest_asserts.ConTestAssertCompareError as err:
                    print(err)
                    failed = True
        finally:
            # CANoe cleanup
            if canoe_app:
                self.close_canoe(canoe_app)
            self.testrun.power_supply_control("off")
        contest_asserts.verify(failed, False, "There were failed CANoe tests.")

    @staticmethod
    def close_canoe(canoe_application):
        """
        Close CANoe

        :param canoe_application: contains Canoe object
        """
        close_with_success = False
        start_time = time.time()
        delta = 0.0
        while delta <= CANOE_DELAY_FINISH:
            try:
                canoe_application.close()
            except contest_asserts.ConTestEqualsError:
                LOG.exception("=============CANoe was not closed successfully=============")
                delta = time.time() - start_time
            else:
                close_with_success = True
                LOG.info("CANoe was closed successfully.")
                break
        if close_with_success is False:
            LOG.info("=============CANoe processes will be killed.=============")
            kill_processes("CANoe\\d+\\.exe")

    def read_configuration_files(self, args):
        """
        Read project and base configuration .json files files.
        """
        self.project_config = ProjConfig(args.prj_config_json_file_path)
        self.project_config.read_configuration(args)
        self.project_config.setup_environment()
        self.t32_logdir = self.project_config.env_vars["T32_TAF_ROOT_DIR"] + "\\cmm\\logs"

        project_config_depending_env_vars = ProjectConfigDependingEnvVars()
        project_config_depending_env_vars.setup_environment(args, self.project_config)

        self.base_config = BaseConfig(project_config_depending_env_vars.env_vars["BASE_CONFIG_JSON_FILE_PATH"])
        self.base_config.read_configuration(args)
        self.base_config.set_t32_exe_abs_file_paths(self.project_config, project_config_depending_env_vars)
        self.base_config.setup_environment(self.project_config)

        self.t32_apps = []
        self.t32_cfgs = []
        key_startup_enabled_template = f"{args.controller_id}_GUI{{}}_STARTUP_ENABLED"
        key_exec_file_path_template = f"{args.controller_id}_GUI{{}}_EXEC_FILE_PATH"
        key_startup_component_name = f"{args.controller_id}_CONTROLLER_NAME"
        startup_config_filename_template = "startup_config_GUI{}.t32"
        gui_num = 0
        key_startup_enabled = key_startup_enabled_template.format(gui_num)
        key_exec_file_path = key_exec_file_path_template.format(gui_num)
        if key_startup_enabled in self.project_config.env_vars:
            while key_exec_file_path in self.base_config.env_vars:
                if "TRUE" in self.project_config.env_vars[key_startup_enabled]:
                    self.t32_apps.append(self.base_config.env_vars[key_exec_file_path])
                    startup_config_filename = startup_config_filename_template.format(gui_num)
                    startup_component_name = self.base_config.env_vars[key_startup_component_name]
                    self.t32_cfgs.append(
                        os.path.join("startup\\Component", startup_component_name, startup_config_filename)
                    )
                gui_num = gui_num + 1
                key_startup_enabled = key_startup_enabled_template.format(gui_num)
                key_exec_file_path = key_exec_file_path_template.format(gui_num)
        else:
            LOG.error(
                "'GUI startup enabled' key '%s' not found in project configuration file '%s'",
                key_startup_enabled,
                args.prj_config_json_file_path,
            )
            contest_asserts.fail(
                f"'GUI startup enabled' key '{key_startup_enabled}' not found in project configuration file "
                "'{args.prj_config_json_file_path}'"
            )

        LOG.info("t32_apps: %s", " ".join([str(item) for item in self.t32_apps]))
        LOG.info("t32_cfgs: %s", " ".join([str(item) for item in self.t32_cfgs]))

    def setup_taf_trace32_env(self):
        """Set the TAF T32 environment variables"""

        # is_bricks helps to differentiate between new and old framework (only TRACE32 is impacted)
        # new framework (Bricks/GitHub) - most options are read from .json configs
        # old framework (IMS) - most options are hardcoded in .t32 configs or python scripts
        if not self.is_bricks:
            # TODO: The code on this branch must be kept in sync manually with the changes in
            #       RunTRACE32TestModules.RunTRACE32TestModules()
            args = Namespace
            args.project = self.t32_project
            args.elf_file_path = self.elf_file_path
            args.target_description_file_path = None
            args.t32_base_path = self.t32_base_path
            args.t32_taf_root_path = os.path.join(self.taf_config["WORKSPACE"], self.taf_config["TRACE32_PATH"])
            args.target_controller = self.t32_target_controller
            args.t32_version = self.t32_version

            setup_environment(args)

            os.environ["TB_TARGET_CONTROLLER"] = self.t32_target_controller_name
            for i, elf_file_name in enumerate(self.elf_file_names):
                key = f"ELF_FILENAME{i}"
                os.environ[key] = elf_file_name

            self.t32_startup_script = "startup\\Generic\\startup_C0.cmm"
            self.t32_logdir = os.path.join(self.taf_config["WORKSPACE"], self.taf_config["TRACE32_PATH"], "cmm", "logs")
            prepare_log_folder(self.t32_logdir)
        else:
            # TODO: The code on this branch must be kept in sync manually with the changes in
            #       run_trace32_test_modules.main()
            args = Namespace

            # run_trace32_test_modules.main() parameter settings:
            # With coding set to 'True' tests won't run automatically and TRACE32 GUIs stay open
            # until run_t32_tests() quits them.
            args.coding = True
            args.workspace_dir = self.taf_config["WORKSPACE"]
            orig_workspace = os.environ.get("ORIG_WORKSPACE", args.workspace_dir)
            args.prj_config_json_file_path = os.path.join(orig_workspace, self.prj_config_json_file_path)
            # For now we only support to start single-microcontroller setups
            args.controller_id = "CONTROLLER0"
            # Use T32 SW version as specified in project configuration
            args.t32_sw_version = None
            args.keycode = None

            # Code from run_trace32_test_modules.main()
            # exception_handler = ExceptionHandler()
            self.trace32_startup = TRACE32Startup()

            self.read_configuration_files(args)

            keycode_handler = KeycodeHandler(args)
            keycode_handler.prepare(self.project_config)

            # Remove TRACE32 report zip archive from log folder. Otherwise with the
            # unzip_saved_results after test execution the test reports from this archive will
            #  overwrite the new ones.
            delete_file(os.path.join(self.t32_logdir, "TestReportsPreviousTestRun.zip"), False)

            # Code from run_trace32_test_modules.start_trace32_gui0()
            self.trace32_startup._controller_id = args.controller_id  # pylint: disable=protected-access
            os.environ["CONTROLLER_ID"] = args.controller_id

            self.trace32_startup.check_and_set_trace32_startup_paths(self.base_config, self.project_config)
            self.t32_startup_script = "startup\\Generic\\startup_GUI0.cmm"
            # self.trace32_startup.assemble_trace32_startup_call(args, self.base_config,
            # self.project_config) method sets the SCREEN environment variable.
            # SCREEN OFF hides the TRACE32 GUIs to improve execution speed and fail fast when
            # debugger hangs (ConTest will have closed the TRACE32 GUIs after a few retries)
            # os.environ["SCREEN"] = "OFF"

    def start_trace32(self, lauterbach_guis, time_out=60.0):
        """
        Start Trace32 with TAF

        :param list lauterbach_guis: Lauterbach instances
        :param float time_out: Number of seconds to wait for Trace32 GUI startup check (default=60s)
        """
        start_time = time.time()
        delta_time = 0
        trace32_startup_finished = False
        t32_cfg = os.path.join(self.taf_config["WORKSPACE"], self.taf_config["TRACE32_PATH"], self.t32_cfgs[0])
        t32_startup_script = os.path.join(
            self.taf_config["WORKSPACE"], self.taf_config["TRACE32_PATH"], self.t32_startup_script
        )

        # ConTest Trace32 setup
        # Creating master T32 instance
        lauterbach_app = lauterbach_util.Lauterbach(
            t32_app=self.t32_apps[0],
            t32_cfg=t32_cfg,
            multicore=True,
            t32_startup_script=t32_startup_script,  # can start slave T32 instance(s)
            t32_args=[
                "0",  # &Coding==0, automated tests execution
                "1",  # &Contest==1, ConTest orchestrates tests execution
            ],
        )
        lauterbach_guis.append(lauterbach_app)
        set_global_parameter("t32", lauterbach_app, overwrite=True)

        # Attaching to the slave T32 instance(s), started by the master instance
        for i, t32_cfg in enumerate(self.t32_cfgs[1:], start=1):
            t32_cfg = os.path.join(self.taf_config["WORKSPACE"], self.taf_config["TRACE32_PATH"], self.t32_cfgs[i])
            t32_gui = lauterbach_util.Lauterbach(
                t32_app=self.t32_apps[i], t32_cfg=t32_cfg, multicore=True, already_open=True
            )
            lauterbach_guis.append(t32_gui)
            # global variable name for T32 slave instances will be <exe_name>_<gui_no>
            # e.g.: [RAD6xx] -> t32m6000_2, t32marm_3
            t32_var = t32_gui.multicore_info["gui_no"]
            set_global_parameter(t32_var, t32_gui, overwrite=True)

        # Check Trace32 GUI startup
        # If successful T32 startup message is not printed out in T32 area content
        # in 'time_out' time frame (default = 60.0s) then the bellow assert will fail
        while delta_time <= time_out:
            get_full_area = lauterbach_guis[0]._get_window_content("area")  # pylint: disable=protected-access
            if "TRACE32-TAF GUIs started up successfully" in "".join(get_full_area):
                trace32_startup_finished = True
                break
            delta_time = time.time() - start_time
        contest_asserts.verify(trace32_startup_finished, True, "TRACE32 GUIs startup failed. Timeout elapsed.")

    def run_t32_tests(
        self,
        scripts,
        project,
        testsuite,
        restbus=True,
        script_timeout=600,
        skip_on_failure_request=False,
        delay_power_on=0,
        verify=True,
        taf_t32_debug_mode=False,
    ):
        # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        """
        Run TAF Trace32 tests

        :param list scripts: A list of cmm scripts to execute
                             ("test_script_file.cmm", "test_report_file.msg")
        :param string project: Magic tester project
        :param string testsuite: Magic tester test suite
        :param bool restbus: Whether to start restbus simulation
        :param string script_timeout: Test run timeout for each script
        :param bool skip_on_failure_request: If 'True' it skips all remaining test scripts of the
                                             current ConTest test case and test scripts called
                                             by all remaining ConTest test cases after a FAIL
                                             (unstable) verdict of any test script.
        :param float delay_power_on: Number of seconds to delay turning the power on after TRACE32.
        :param string verify: Whether to fail on unstable tests. If 'False' test scripts are
                              executed but ConTest test result is forced to 'PASS' result even
                              if the test was 'FAIL' (unstable). Tests with 'ERROR' (Cat2)
                              result are not affected by the 'verify' flag set to 'False'.
                              'verify' setting is ignored if 'skip_on_failure_request' is 'True'.
        :param taf_t32_debug_mode: Let ConTest keep T32 GUIs open until the user closes the T32-GUIs.
                                   Setting taf_t32_debug_mode to True is meant for T32 test script manual
                                   debugging purposes using the Test Automation Framework (TAF), only.
        """

        testsuites = {item.strip() for item in testsuite.split(",")}
        if testsuites.intersection({"flashing"}):
            self.test_type = self.TestType.FLASHING_T32
        else:
            self.test_type = self.TestType.TRACE32

        # If self.skip_on_failure is True ConTest will still call all remaining test
        # cases but PRACTICE test scripts execution is inhibited.
        if not self.skip_on_failure:
            # Set env. variable AUTOMATION_UTILS_PATH required in global.cmm
            os.environ["AUTOMATION_UTILS_PATH"] = os.path.join(
                self.taf_config["WORKSPACE"], self.taf_config["AUTOMATION_UTILS_PATH"]
            )

            self.testrun.run_magic_tester(project, testsuite)
            if self.relay_target_state is not None:
                self.power_reset_debugger(target_state=self.relay_target_state)

            lauterbach_guis = []
            canoe_app = None
            try:
                self.testrun.power_supply_control("off")
                if restbus:
                    canoe_app = self.start_canoe(start_simulation=True)

                # Some projects (ARS620DP14) are turning the ECU off in <1s (when there is no CAN
                # message or debugger connected flag is not set)
                # Allow to delay turning the power supply on to ensure proper ECU startup
                timer = Timer(delay_power_on, self.testrun.power_supply_control, args=("on",))
                timer.start()
                try:
                    self.start_trace32(lauterbach_guis)
                except contest_asserts.ConTestEqualsError as exc:
                    self.skip_on_failure = True
                    raise exc from None
                finally:
                    timer.join()
                # The t32 message reader would pick up and print the test reports of even those
                # tests which already ran and print their results on the console. To prevent this
                # the test reports are zipped prior to starting the t32 message reader and unzipped
                # after t32 message reader was stopped.
                self.trace32_startup.prepare_test_report_log_folder(self.t32_logdir)
                self.testrun.start_t32_message_reader(self.t32_logdir)

                # Test lauterbach instances access
                for gui in lauterbach_guis:
                    t32_cfg = os.path.basename(gui.t32_cfg)
                    sent_message = f"Hello from API ({t32_cfg})"
                    gui.run_t32_cmd(f'Print "{sent_message}"')
                    retrieved_message = gui.grab_last_area_message()
                    LOG.info("Message from lauterbach instance: %s", retrieved_message)
                    # If TRACE32 generates automatic messages in between write and read,
                    # then the bellow assert will fail
                    # e.g.: "Warning: file D:\0\src\stubs\OS\Os_Core.c not found"
                    # contest_asserts.verify(
                    #     retrieved_message, sent_message,
                    #     "Unexpected message found on Lauterbach window (%s)!" % t32_cfg)

                # Trace32 testrun
                any_scripts_test_failed = False
                final_verdict = "PASS"
                for script_info in scripts:
                    if any_scripts_test_failed and skip_on_failure_request:
                        self.skip_on_failure = True
                        if final_verdict != "ERROR_TIMEOUT":
                            LOG.info("Test script produced a 'FAIL' result.")
                            LOG.info(
                                "Skip all remaining test scripts of the current ConTest test "
                                "case and skip test scripts called by all remaining ConTest "
                                "test cases"
                            )
                            error_str = "Check the TAF reports found in taf_reports folder or in Jenkins job artifacts"
                        else:
                            error_str = (
                                "Timeout occurred while test script was running. Check the test script for"
                                "possible hang-up reasons."
                            )
                        contest_asserts.verify(final_verdict, "PASS", error_str)

                    try:
                        lauterbach_guis[0].run_t32_script(
                            os.path.join(
                                self.taf_config["WORKSPACE"], self.taf_config["TRACE32_PATH"], "cmm", script_info[0]
                            ),
                            script_timeout=script_timeout,
                            taf_t32_debug_mode=taf_t32_debug_mode,
                        )
                    except contest_asserts.ConTestEqualsError as exc:
                        if exc.error_msg.startswith("PRACTICE test script not executed after "):
                            LOG.info("A timeout error occurred: '%s'", str(exc))
                            any_scripts_test_failed = True
                            final_verdict = "ERROR_TIMEOUT"
                        if exc.error_msg.startswith(
                            "T32 PRACTICE test script manual debug mode stopped on user request"
                        ):
                            LOG.info("Exiting test script execution: '%s'", str(exc))
                            # Skip remaining test scripts
                            break

                    else:
                        if verify or skip_on_failure_request:
                            LOG.info("Verify result for test: '%s'", script_info[0])
                            verdict = lauterbach_guis[0].verify_taf_result(
                                os.path.join(self.t32_logdir, script_info[1]), parse_only=True
                            )
                            if verdict in ["FAIL", "ERROR"]:
                                LOG.info("Test '%s' failed with verdict: '%s'", script_info[0], verdict)
                                any_scripts_test_failed = True
                                if Verdicts[final_verdict] < Verdicts[verdict]:
                                    final_verdict = verdict
                        else:
                            LOG.info("Ignore the 'FAIL' verdict of the test script '%s'", script_info[0])

                if any_scripts_test_failed:
                    if skip_on_failure_request:
                        self.skip_on_failure = True
                    if final_verdict != "ERROR_TIMEOUT":
                        error_str = "Check the TAF reports found in taf_reports folder or in Jenkins' job artifacts"
                    else:
                        error_str = (
                            "Timeout occurred while the test script was running. Check the test script "
                            "for possible hang-up reasons."
                        )
                    contest_asserts.verify(final_verdict, "PASS", error_str)
                else:
                    LOG.info(
                        "All test scripts produced a 'PASS' result. Call the final verify to "
                        "finish the ConTest test case."
                    )
                    contest_asserts.verify("PASS", "PASS", " See console output for details")

            finally:
                # Trace32 cleanup
                if lauterbach_guis:
                    # Ensure we close master T32 instance first
                    lauterbach_guis[0].close()
                    # Close the slave instance(s) last
                    for t32_instance in lauterbach_guis[1:]:
                        t32_instance.close()
                if canoe_app:
                    self.close_canoe(canoe_app)
                self.testrun.terminate_t32_message_reader()
                self.reporting.unzip_saved_results(self.t32_logdir)
                self.testrun.power_supply_control("off")
                if self.relay_target_state is not None:
                    self.power_down_debugger(target_state=self.relay_target_state)
        else:
            # The verdict of ConTest test cases is set to FAIL if their execution was skipped
            # on purpose.
            contest_asserts.verify(
                "FAIL",
                "PASS",
                " PRACTICE test script execution was skipped due to an unstable result of a test case which has set "
                "the 'skip_on_failure_request' flag to True",
            )

    def run_xcp_flashing_tests(self, xcp_project, flash_files, relay_options=None):
        """
        Run TAF Xcp flashing tests

        :param string xcp_project: The name of the project in the tool
        :param list flash_files: Contains the files to flash
        :param string relay_options: Contains relay_options
        """
        self.test_type = self.TestType.FLASHING_XCP
        if self.skip_on_failure:
            # The verdict of ConTest test cases is set to FAIL if their execution was skipped
            # on purpose.
            contest_asserts.fail(
                "Xcp-dlt flash test execution was skipped due to an unstable result of"
                " a test case which has set 'skip_on_failure_request' flag to True"
            )
        try:
            for file_name in flash_files:
                file_path = os.path.join(self.taf_config["WORKSPACE"], file_name)
                self.flashing.run_xcp_downloadtool(xcp_project, file_path, relay_options)
        except Exception:  # pylint: disable=broad-except
            LOG.info("Test script produced a 'FAIL' result.")
            LOG.info(
                "Skip all remaining test scripts of the current ConTest test case and skip "
                "test scripts called by all remaining ConTest test cases"
            )
            self.skip_on_failure = True
            contest_asserts.verify(
                "FAIL", "PASS", " Check the TAF reports found in taf_reports folder or in Jenkins job artifacts"
            )

    # Ported TAF robot keywords
    def power_up_debugger(self, relays=1, target_state=0):
        """
        Calls the relay controller to power up the debugger.

        :param int relays: The relay number
        :param int target_state: The target state of the relay: 0 -> NO, 1 -> NC
        """
        subcommand = "deactivate" if target_state > 0 else "activate"
        self.testrun.relay_controller(subcommand, relays=relays)

    def power_down_debugger(self, relays=1, target_state=0):
        """
        Calls the relay controller to power down the debugger.

        :param int relays: The relay number
        :param int target_state: The target state of the relay: 0 -> NO, 1 -> NC
        """
        subcommand = "activate" if target_state > 0 else "deactivate"
        self.testrun.relay_controller(subcommand, relays=relays)

    def power_reset_debugger(self, relays=1, wait_time=1, target_state=0):
        """
        Calls the relay controller to reset the debugger.

        :param int relays: The relay number
        :param int wait_time: The delay between the operations
        :param int target_state: The target state of the relay: 0 -> NO, 1 -> NC
        """
        self.testrun.relay_controller("reset", relays=relays, wait_time=wait_time, target_state=target_state)

    def set_relay_state(self, relays, target_state=0):
        """
        Calls the relay controller to switch the relay state.

        :param int relays: The relay number
        :param int target_state: The target state of the relay: 0 -> NO, 1 -> NC
        """
        subcommand = "activate" if target_state > 0 else "deactivate"
        self.testrun.relay_controller(subcommand, relays=relays)

    def custom_events_end_flash(self, variant):
        """
        Logs custom events
        """
        try:
            id_setup = os.environ["CUSTOM_EVENT_ID_SETUP"]
            id_flash = re.sub(r"taf_\d{1,3}", "taf_200", id_setup)
            id_exec = os.environ["CUSTOM_EVENT_ID_EXEC"]
            type_of_run = os.environ["CUSTOM_EVENT_TYPE_OF_RUN"]
            tas_name = os.environ["NODE_NAME"]
        except Exception as exc:
            print(f"Error occurred: {exc}")
            print("Custom Event not implemented (missing environment variables: CUSTOM_EVENT_*)?")
            raise
        retry_count = id_setup[-1]
        message = f"variant: {variant}, retry: {retry_count}, type_of_run: {type_of_run}, TAS: {tas_name}"
        log_event(is_start=False, id=id_setup, subname="TSSetup")
        log_event(is_start=False, id=id_flash, subname="TSFlash")
        log_event(is_start=True, id=id_exec, subname="TSExec", message=message)
