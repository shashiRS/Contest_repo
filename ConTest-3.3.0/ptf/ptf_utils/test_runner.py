"""
    Copyright Continental Corporation and subsidiaries. All rights reserved.

    :platform: Windows and Linux

    :synopsis:
        This file contains code for PTF test runner. ConTest test runner will receive project specifications from
        ConTest GUI Controller and then execute the tests. Also reporting is triggered in this file.
"""

# standard Python modules imports
import functools
import logging
import os
import random
import time

# custom imports
from contest_verify.verify import contest_expects, contest_asserts, contest_warn
from data_handling import helper as model_helper
from global_vars import SUCCESS, TEST_FAILURE, INCONCLUSIVE
from rest_service import client_informer
from ptf.ptf_utils.global_params import _PROJECT_SPECS
from ptf.ptf_utils.test_info import TestInfo
from ptf.ptf_utils import decorator, common
from ptf.ptf_utils.decorator import prioritization
from ptf.ptf_utils.exe_record import save_exe_record
from .global_params import (
    get_parameter,
    clear_local_params,
    clear_global_params,
    clear_reporting_params,
    _clear_files_for_report,
)
from .test_watcher import TestWatcherRunner
from .watcher.console import ConsoleReporter
from .watcher.gui_notifier import GuiNotifier
from .watcher.html_report import HtmlReporter
from .watcher.json_report import JsonReporter
from .watcher.plaintext_report import PlainTextReporter
from .watcher.xml_report import XmlReporter
from .watcher.cathat_xml_report import CatHatXmlReporter

LOG = logging.getLogger("TEST_RUNNER")

# Disabling warnings  as current implementation is required as per logic
# pylint: disable=too-many-arguments,too-many-locals,too-many-statements


def decorator_runner_parameterized(
    test_to_wrap,
    test_data,
    test_name,
    setup_method,
    teardown_method,
    custom_setup,
    custom_teardown,
    setup_script_path,
    test_filter,
    random_execution,
    gui_obj,
    parameterized_tests_data,
    verifies_id,
    automates_id,
    tags,
    test_type,
    test_multiple_runs=False,
):
    """
    Decorator for parameterized test cases. This function is calling parameterized tests with
    parameters defined on configuration time. On calls of func.__name__ it will return the name
    of the wrapped function.

    :param function test_to_wrap: Test case method
    :param TestData test_data: object of data_handling.prepare_test_data.TestData class
    :param string test_name: The name of the testcase
    :param function setup_method: The method to call before the test
    :param function teardown_method: The method to call after the test
    :param object custom_setup: custom setup function object
    :param object custom_teardown: custom teardown function object
    :param str setup_script_path: loaded/used setup.pytest script path
    :param list test_filter: A list of test names to execute. None to execute all
    :param boolean random_execution: If execution should be randomized
    :param object gui_obj: GUI object
    :param dict parameterized_tests_data: Contains parameterized test data for test runner
    :param list verifies_id: requirement/design id list
    :param list automates_id: automates id list
    :param list tags: list of the test tags
    :param str test_type: test case type
    :param bool test_multiple_runs: if user requested multiple test run
    :return: The wrapped test case
    """

    @functools.wraps(test_to_wrap)
    def wrapper(watcher_runner, global_setup_status=True):
        """
        Wrapper function for parameterized tests

        :param object watcher_runner: test watcher object
        :param bool global_setup_status: bool flag, True in-case global_setup function passed
        """
        return test_to_wrap(
            test_name,
            test_data,
            watcher_runner,
            setup_method,
            teardown_method,
            custom_setup,
            custom_teardown,
            setup_script_path,
            test_filter,
            random_execution,
            gui_obj,
            parameterized_tests_data,
            verifies_id,
            automates_id,
            tags,
            test_type,
            test_multiple_runs,
            global_setup_status,
        )

    return wrapper


def decorator_test_runner(
    test_to_wrap, setup_method, teardown_method, custom_setup, custom_teardown, setup_script_path
):
    """
    Decorator for test cases. This function is responsible to wrap test cases
    with functionalities which are necessary to be called before start of each
    test case.

    :param function test_to_wrap: Test case method
    :param function setup_method: The method to call before the test
    :param function teardown_method: The method to call after the test
    :param object custom_setup: custom setup function object
    :param object custom_teardown: custom teardown function object
    :param str setup_script_path: loaded/used setup.pytest script path

    :return: The wrapped test case
    """

    def wrapper(global_setup_status=True):
        """
        Wrapper for test case which executes setup/teardown before/after the testcase

        :param bool global_setup_status: bool flag, True in-case global_setup function passed
        """
        # if global_setup function failed then raise relevant error and no need to run test
        if not global_setup_status:
            contest_asserts.fail(
                f"Execution of '{test_to_wrap.__name__}' did not happen due to failure in 'global_setup' function"
            )
        try:
            # first checking if 'custom_setup' function is requested to be executed, if yes then execute it
            if custom_setup:
                setup_print = f"*** running custom setup '{custom_setup.__name__}' from '{setup_script_path}'"
                print(f"\n{'/' * len(setup_print)}")
                print(setup_print)
                print(f"{'/' * len(setup_print)}\n")
                custom_setup()
            # if custom setup function is not found then execute standard setup function if it exists
            elif setup_method:
                setup_print = f"*** running standard setup '{setup_method.__name__}' from '{setup_script_path}'"
                print(f"\n{'/' * len(setup_print)}")
                print(setup_print)
                print(f"{'/' * len(setup_print)}\n")
                setup_method()
            result = test_to_wrap()
        finally:
            # first checking if 'custom_teardown' function is requested to be executed, if yes then execute it
            if custom_teardown:
                teardown_print = f"*** running custom teardown '{custom_teardown.__name__}' from '{setup_script_path}'"
                print(f"\n{'/' * len(teardown_print)}")
                print(teardown_print)
                print(f"{'/' * len(teardown_print)}\n")
                custom_teardown()
            # if custom teardown function is not found then execute standard teardown function if it exists
            elif teardown_method:
                teardown_print = (
                    f"*** running standard teardown '{teardown_method.__name__}' " f"from '{setup_script_path}'"
                )
                print(f"\n{'/' * len(teardown_print)}")
                print(teardown_print)
                print(f"{'/' * len(teardown_print)}\n")
                teardown_method()
        return result

    # throw back the wrapped test case object with associated parameters
    return wrapper


def decorator_test_runner_capl(setup_method, teardown_method, capl_module, ctf_enabled):
    """
    Decorator for CAPL test modules. This function is responsible to wrap test cases
    with functionalities which are necessary to be called before start of each
    test case.

    :param function setup_method: The method to call before the test i.e. atomic setup
    :param function teardown_method: The method to call after the test i.e. atomic teardown
    :param str capl_module: The name of the test-case to call
    :param bool ctf_enabled: Flag for detecting if CTF framework is used or not
    :return: The wrapped test case
    """

    def wrapper(watcher_runner, global_setup_status=True):
        """
        Wrapper for test case which executes atomic setup/teardown before/after the testcase

        :param object watcher_runner: test watcher object
        :param bool global_setup_status: bool flag, True in-case global_setup function passed
        """
        # if global_setup function failed then raise relevant error and no need to run test
        if not global_setup_status:
            contest_asserts.fail(
                f"Execution of '{capl_module}' did not happen due to failure in 'global_setup' function"
            )
        try:
            if setup_method:
                setup_method()
            _capl_test_module_runner(capl_module, ctf_enabled, watcher_runner)
        finally:
            if teardown_method:
                teardown_method()

    # throw back the wrapped test case object with associated parameters
    return wrapper


def decorator_test_runner_t32(setup_method, teardown_method, test_name, script_dir, report_dir):
    """
    Decorator for t32 test cases. This function is responsible to wrap test cases
    with functionalities which are necessary to be called before start of each
    test case.

    :param function setup_method: The method to call before the test i.e. atomic setup
    :param function teardown_method: The method to call after the test i.e. atomic teardown
    :param str test_name: The name of the test-case to call
    :param str script_dir: The directory containing the test scripts
    :param str report_dir: The directory where test reports should be stored
    :return: The wrapped test case
    """

    def wrapper(global_setup_status=True):
        """
        Wrapper for test case which executes setup/teardown before/after the testcase

        :param bool global_setup_status: bool flag, True in-case global_setup function passed
        """
        # if global_setup function failed then raise relevant error and no need to run test
        if not global_setup_status:
            contest_asserts.fail(f"Execution of '{test_name}' did not happen due to failure in 'global_setup' function")
        try:
            if setup_method:
                setup_method()
            _t32_test_runner(test_name, script_dir, report_dir)
        finally:
            if teardown_method:
                teardown_method()

    # throw back the wrapped test case object with associated parameters
    return wrapper


def _capl_test_module_runner(capl_test_module, ctf_enabled, watcher_runner):
    """
    Function for running CAPL Test Modules

    :param string capl_test_module: CAPL Test Module to run
    :param bool ctf_enabled: Flag for detecting if CTF framework is used or not
    :param object watcher_runner: test watcher object
    """
    try:
        canoe_obj = get_parameter("canoe")
        # disabling pylint check for protected access call because the calling method is made
        # protected in order to disable its appearance in user manual generated by sphinx
        # pylint: disable=protected-access
        tm_info, tc_verdicts = canoe_obj._run_capl_test_modules(capl_test_module, ctf_used=ctf_enabled)
        watcher_runner.test_canoe_tm_tc_verdicts(tc_verdicts)
        # checking test module verdict
        contest_asserts.verify(
            tm_info["Verdict"],
            "Passed",
            "Test Module Verdict Failed/Not-Available ... for detail see report --> "
            "\n\t" + tm_info["Report"] + "\n\tTest Module: " + capl_test_module + "\n",
        )
    except KeyError:
        # the error is known here and no need to capture the error in except statement
        # pylint: disable=raise-missing-from
        raise KeyError("Did not find parameter 'canoe'. Please create a canoe object in global_setup method")


def _t32_test_runner(test_name, scripts_dir, report_dir):
    """
    Function for running .cmm scripts which contain test cases

    :param str test_name: Test script name
    :param dictionary specs: Dictionary containing all info & objects
    :param str report_dir: The directory where test reports should be stored
    """
    try:
        get_parameter("t32").run_t32_test_script(test_name, scripts_dir, report_dir)
    except KeyError:
        # the error is known here and no need to capture the error in except statement
        # pylint: disable=raise-missing-from
        raise KeyError("Did not find parameter 't32'. Please create a lauterbach object in global_setup method")


# It won't have many public methods, but is required for proper abstraction.
# pylint: disable=too-few-public-methods
class TestRunner:
    """Class for controlling PTF test runner"""

    def __init__(self, project_specs, test_filter):
        """constructor

        :param dict project_specs: Project specifications coming from ui
        :param list test_filter: A list of testcase names to be executed.
                                 If None, all selected testcases are executed.
                                 Can be used e.g. to only execute failed testcases
        """
        self.project_specs = project_specs.test_runner_data
        _PROJECT_SPECS.update(self.project_specs)
        # creating a new key with value of TestInfo class object which will collect information
        # about selected tests to be used later in some APIs in global_params.py
        _PROJECT_SPECS["test_info"] = TestInfo(self.project_specs)
        self.test_filter = test_filter

    @staticmethod
    def __update_final_test_list(
        final_list,
        test_obj,
        test_name,
        multiple_runs,
        wrapped_test,
        verfies_id,
        automates_id,
        tags,
        test_type,
        param_test_names,
        parameterized_info=None,
    ):
        """
        Method for updating final test cases list

        :param list final_list: Final test case list
        :param list test_obj: object of data_handling.prepare_test_data.TestData class
        :param string test_name: Name of test case to be added to final_list
        :param int multiple_runs: No of times test need to run
        :param object wrapped_test: Decorated test
        :param list verfies_id: list of the verification (Req ID) fetched from test case
        :param list automates_id: list of the automates (Req ID) fetched from test case
        :param list tags: list of test case tags fetched from python and cmm test case
        :param str test_type: type of the test case. (Supported types are capl, cmm, python)
        :param list param_test_names: Contains list of parameterized test sets names
        :param list parameterized_info: List containing information for parameterized tests wrapping
            Default is None.
        """
        # if no test re-run is required
        if multiple_runs == 1:
            final_list.append(
                [test_name, wrapped_test, verfies_id, tags, test_type, param_test_names, test_obj, automates_id]
            )
        # in-case tests re-run is required
        else:
            # loop for filling final dictionary with number of re-runs required
            for loop_count in range(multiple_runs):
                # modifying test case name with test re-run tag
                modified_test_name = test_name + "-testrun__" + str(loop_count + 1)
                # for parameterized testcases we need to create a new wrapper for each testrun
                # to get the proper name notified by the watcher and generate e.g. proper
                # reports.
                modified_param_test_names = []
                if wrapped_test.__name__ == "parameterized_runner":
                    for param_test_name in param_test_names:
                        params = param_test_name.split("(")
                        modified_param_test_names.append(
                            (params[0] + "-testrun__" + str(loop_count + 1) + "(" + params[1])
                        )
                    wrapped_test = decorator_runner_parameterized(
                        parameterized_info[0],
                        test_obj,
                        modified_test_name,
                        *parameterized_info[1:],
                        verfies_id,
                        automates_id,
                        tags,
                        test_type,
                        test_multiple_runs=True,
                    )
                final_list.append(
                    [
                        modified_test_name,
                        wrapped_test,
                        verfies_id,
                        tags,
                        test_type,
                        modified_param_test_names,
                        test_obj,
                        automates_id,
                    ]
                )

    # pylint: disable=too-many-branches
    # The code is well documented and understandable
    def __load_test_cases(self, project_specs):
        """
        Function responsible for loading test cases and wrapping of test cases.

        :param dict project_specs: Project specification dictionary
        :returns: The wrapped test cases in form of a list: [test name, test wrapped function]
        :rtype: list
        """
        # initializing a list which will be filled with relevant test cases
        # information before throwing it back to the main executor
        final_test_list = []
        # first load local setup and teardown methods
        setup_method = None
        func_name = model_helper.SETUP_TEARDOWN_METHOD_NAMES[2]
        if func_name in project_specs["setup_files"].keys():
            setup_method = project_specs["setup_files"][func_name]
        else:
            LOG.info("'%s()' not found in setup.pytest. Won't execute anything before each testcase", func_name)
        teardown_method = None
        func_name = model_helper.SETUP_TEARDOWN_METHOD_NAMES[3]
        if func_name in project_specs["setup_files"].keys():
            teardown_method = project_specs["setup_files"][func_name]
        else:
            LOG.info("'%s()' not found in setup.pytest. Won't execute anything after each testcase", func_name)
        test_runs = project_specs["tests_frequency"]
        # decorate python tests (normal and parameterized)
        for python_test in project_specs["py_tests"]:
            # wrapping each test case with some pre-testrun steps
            param_tests_output_display = []
            if python_test.object[0].__name__ == "parameterized_runner":
                param_tests_output_display = [
                    test["name"] for test in project_specs["parameterized_tests"][python_test.name].values()
                ]
                test_case = decorator_runner_parameterized(
                    python_test.object[0],
                    python_test,
                    python_test.name,
                    setup_method,
                    teardown_method,
                    python_test.custom_setup,
                    python_test.custom_teardown,
                    python_test.setup_script_path,
                    self.test_filter,
                    project_specs["randomize"],
                    project_specs["gui_object"],
                    project_specs["parameterized_tests"],
                    python_test.verifies_id,
                    python_test.automates_id,
                    python_test.tag,
                    "python",
                    test_multiple_runs=False,
                )
                self.__update_final_test_list(
                    final_test_list,
                    python_test,
                    python_test.name,
                    test_runs,
                    test_case,
                    python_test.verifies_id,
                    python_test.automates_id,
                    python_test.tag,
                    "python",
                    param_tests_output_display,
                    parameterized_info=[
                        python_test.object[0],
                        setup_method,
                        teardown_method,
                        python_test.custom_setup,
                        python_test.custom_teardown,
                        python_test.setup_script_path,
                        self.test_filter,
                        project_specs["randomize"],
                        project_specs["gui_object"],
                        project_specs["parameterized_tests"],
                    ],
                )
            else:
                test_case = decorator_test_runner(
                    python_test.object[0],
                    setup_method,
                    teardown_method,
                    python_test.custom_setup,
                    python_test.custom_teardown,
                    python_test.setup_script_path,
                )
                self.__update_final_test_list(
                    final_test_list,
                    python_test,
                    python_test.name,
                    test_runs,
                    test_case,
                    python_test.verifies_id,
                    python_test.automates_id,
                    python_test.tag,
                    "python",
                    param_tests_output_display,
                )
            decorator.sync_attributes(python_test.object[0], test_case)
        # decorate T32 tests
        for t32_test in project_specs["cmm_tests"]:
            test_case = decorator_test_runner_t32(
                setup_method,
                teardown_method,
                t32_test.name,
                t32_test.folder_structure,
                project_specs["paths"]["txtReport"],
            )
            self.__update_final_test_list(
                final_test_list,
                t32_test,
                t32_test.name,
                test_runs,
                test_case,
                verfies_id=[],
                automates_id=[],
                tags=[],
                test_type="cmm",
                param_test_names=[],
            )
        # decorate CAPL (CANoe) tests modules to run
        for capl_test in project_specs["capl_tests"]:
            test_case = decorator_test_runner_capl(
                setup_method, teardown_method, capl_test, self.project_specs["ctf_enabled"]
            )
            self.__update_final_test_list(
                final_test_list,
                capl_test,
                capl_test,
                test_runs,
                test_case,
                verfies_id=[],
                automates_id=[],
                tags=[],
                test_type="capl",
                param_test_names=[],
            )
        # Filter the test-cases
        final_test_list = self.__filter_testcases(final_test_list, self.test_filter)

        # Randomize tests-cases
        if project_specs["randomize"]:
            random.shuffle(final_test_list)

        # Order by priority. This should keep the randomized order within a single group.
        final_test_list = sorted(final_test_list, key=lambda elem: prioritization.get_priority(elem[1]), reverse=True)

        # Finally add global setup method to test list. Do this after all modifications to make
        # sure it is really the first function to be executed
        func_name = model_helper.SETUP_TEARDOWN_METHOD_NAMES[0]
        if func_name in project_specs["setup_files"].keys():
            setup_method = project_specs["setup_files"][func_name]
            verifies_id = []
            automates_id = []
            tags = []
            param_tests = []
            final_test_list.insert(
                0, [func_name, setup_method, verifies_id, tags, "python", param_tests, setup_method, automates_id]
            )
        else:
            LOG.info("'%s()' not found in setup.pytest. Won't execute anything before all testcases", func_name)

        # Add global teardown method to test list to make sure it is really the last function
        # to be executed
        func_name = model_helper.SETUP_TEARDOWN_METHOD_NAMES[1]
        if func_name in project_specs["setup_files"].keys():
            global_teardown_method = project_specs["setup_files"][func_name]
            verifies_id = []
            automates_id = []
            tags = []
            param_tests = []
            final_test_list.append(
                [
                    func_name,
                    global_teardown_method,
                    verifies_id,
                    tags,
                    "python",
                    param_tests,
                    global_teardown_method,
                    automates_id,
                ]
            )
        else:
            LOG.info("'%s()' not found in setup.pytest. Won't execute anything after all testcases", func_name)
        # returning test cases list
        return final_test_list

    @staticmethod
    def __filter_testcases(test_list, test_filter):
        """
        Returns a test list containing only testcases in test_filter.

        :param list test_list: The list to filter.
        :param list test_filter: A list of testcase names to be executed. None to execute all tests.
        :return: A list of filtered tests
        :rtype: list
        """
        if test_filter is not None:
            # removing the 'testrun' tag and deleting duplications in failed test cases list in
            # order to filter test cases (for running only failed tests scenario from GUI)
            # 'testrun' string is added in test name for multiple test runs
            test_filter_without_testrun_tag = list(dict.fromkeys([test.split("-testrun")[0] for test in test_filter]))
            filtered_list = []
            for testcase_name, testcase, verifies_id, tags, test_type, param_tests, test_obj, automates_id in test_list:
                # store failed param test names
                failed_param_tests = []
                # Only add if the test cases are in the filter list
                for test_failed in test_filter:
                    if test_failed in param_tests:
                        # To avoid duplication in failed_param_tests
                        if test_failed not in failed_param_tests:
                            failed_param_tests.append(test_failed)
                if testcase_name.split("-testrun")[0] in test_filter_without_testrun_tag:
                    filtered_list.append(
                        [
                            testcase_name,
                            testcase,
                            verifies_id,
                            tags,
                            test_type,
                            failed_param_tests,
                            test_obj,
                            automates_id,
                        ]
                    )
            return filtered_list
        return test_list

    # need to access protected members as part of test runner
    # pylint: disable=protected-access
    def __init_default_watcher(self, watcher_runner):
        """
        Initializes the default test watcher to a given runner.

        :param TestWatcherRunner watcher_runner: The runner instance at which the watcher should
                                                 be registered
        """

        watcher_runner.append(ConsoleReporter())
        if self.project_specs["triggered_from_gui"]:
            watcher_runner.append(GuiNotifier(self.project_specs["gui_object"][0]))
        watcher_runner.append(PlainTextReporter(self.project_specs))
        watcher_runner.append(JsonReporter(self.project_specs))
        watcher_runner.append(XmlReporter(self.project_specs))
        watcher_runner.append(HtmlReporter(self.project_specs))
        watcher_runner.append(CatHatXmlReporter(self.project_specs))

        # assigning test watcher runner class object to _REPORT_WATCHER in global_params module
        # this will be helpful in accessing test watcher runner object in other modules
        # pylint: disable=import-outside-toplevel
        from ptf.ptf_utils import global_params

        global_params._REPORT_WATCHER = watcher_runner

    def __final_logs(self):
        """
        Method for logging final information
        """
        LOG.info("Finished Tests Execution")
        LOG.info("TXT Reports at : %s", self.project_specs["paths"][model_helper.TXT_REPORT])
        LOG.info("HTML Reports at: %s", self.project_specs["paths"][model_helper.HTML_REPORT])
        if self.project_specs["paths"][model_helper.EXTERNAL_REPORT]:
            LOG.info("Reports also generated at %s", self.project_specs["paths"][model_helper.EXTERNAL_REPORT])

        client_informer.REST_CLIENT_INFORMER.report_location = os.path.abspath(
            os.path.join(self.project_specs["paths"][model_helper.TXT_REPORT], os.pardir)
        )
        client_informer.REST_CLIENT_INFORMER.html_test_report = (
            self.project_specs["paths"][model_helper.HTML_REPORT] + "TESTS_SUMMARY.html"
        )
        client_informer.REST_CLIENT_INFORMER.xml_test_report = (
            self.project_specs["paths"][model_helper.TXT_REPORT] + "TEST_RESULT.xml"
        )
        client_informer.REST_CLIENT_INFORMER.json_test_report = (
            self.project_specs["paths"][model_helper.TXT_REPORT] + "TEST_RESULT.json"
        )
        client_informer.REST_CLIENT_INFORMER.txt_test_report = (
            self.project_specs["paths"][model_helper.TXT_REPORT] + "TESTS_SUMMARY.txt"
        )

    # Pylint also seems to count our try-catch-finally blocks as nested blocks.
    # Since they are straight forward, we can ignore the "too-many-nested-blocks" warning here
    # pylint: disable=too-many-nested-blocks, inconsistent-return-statements, protected-access
    def run(self):
        """
        Will load test cases and execute them. During execution, test watchers will be notified.

        :rtype: int
        :returns: returns 0 in-case all tests are passed else 2
        """
        # variable for storing the status of test execution
        status = SUCCESS
        # boolean flag to save the warning state of complete test execution
        # test warning state: if warning(s) occurred in a test case without any failure(s)
        warning_occurred = False
        orig_cdw = ""
        # for redirecting console output to report file
        with TestWatcherRunner() as watcher_runner:
            try:
                # Redirect current working directory to base directory so that relative calls in
                # the testcases are relative to base directory
                orig_cdw = os.path.abspath(os.getcwd())
                os.chdir(self.project_specs["paths"][model_helper.BASE_PATH])

                self.__init_default_watcher(watcher_runner)

                # loading all test cases after wrapping for necessary
                # pre-call executions
                test_cases = self.__load_test_cases(self.project_specs)
                LOG.info("Starting Tests Execution")
                watcher_runner.test_run_started(test_cases)

                # reset global parameters
                clear_global_params()

                # reset reporting parameters
                clear_reporting_params()

                # Stores if global setup was successful or not
                global_setup_success = True

                # loop for running all tests
                for test_index, test_data in enumerate(test_cases):
                    # boolean flag to save the test case failure state
                    test_failure_occurred = False
                    # fetching test data from 'test_data' list
                    test_name, test_function, verifies_id, tags, test_type, test_case_data, automates_id = (
                        test_data[0],
                        test_data[1],
                        test_data[2],
                        test_data[3],
                        test_data[4],
                        test_data[6],
                        test_data[7],
                    )
                    try:
                        watcher_runner.test_started(
                            test_name, test_function, verifies_id, automates_id, tags, test_type
                        )
                        # test_case_status = {"status": "running", "current_test": test_name}
                        client_informer.REST_CLIENT_INFORMER.status = "running"
                        client_informer.REST_CLIENT_INFORMER.test_name = test_name
                        # call for test case(s)
                        # If we have a parameterized_runner, we pass the watcher runner so that
                        # additional watcher calls can be done if required
                        if test_function.__name__ == "parameterized_runner":
                            test_function(watcher_runner, global_setup_success)
                        # test case is of type CAPL, we pass the watcher runner to capture capl test
                        # cases execution status into report
                        elif test_function.__qualname__ == "decorator_test_runner_capl.<locals>.wrapper":
                            test_function(watcher_runner, global_setup_success)
                        else:
                            # if test is either 'global_setup' or 'global_teardown' simply execute them as they are
                            # no wrappers for them
                            if test_name in ("global_setup", "global_teardown"):
                                test_function()
                            # if test is not 'global_setup' or 'global_teardown' and global_setup passed then check
                            # skip flag as below
                            else:
                                # check if `skip_if` decorator is used and the skip condition is `True`
                                if not common._get_test_skip_info(test_case_data):
                                    test_function(global_setup_success)
                                else:
                                    print(f"Skipping due to reason: {test_case_data.skip_reason}")
                        # Check EXPECT failure(s) list.
                        # If it is an empty list, then the test is PASSED.
                        # Else raise exception to FAIL the test
                        if contest_expects.FAILURES:
                            raise contest_expects.ConTestExpectError(contest_expects.FAILURES)
                        # no exception appeared until now, so we can notify the watcher that the test succeeded only if
                        # there are no warnings logged in the test function
                        if not contest_warn._WARNINGS:
                            if not common._get_test_skip_info(test_case_data):
                                watcher_runner.test_succeeded()
                            else:
                                watcher_runner.test_skip(skip_reason=test_case_data.skip_reason)
                    # Catch all exceptions that might appear in test function and report them
                    except Exception as error:  # pylint: disable=broad-except
                        test_failure_occurred = True
                        # changing status value to 1 to report exit_code with failure
                        if status == SUCCESS:
                            status = TEST_FAILURE
                        watcher_runner.test_failed(error)
                        if test_name == "global_setup":
                            global_setup_success = False
                    finally:
                        # call watchers 'test_inconclusive' function if no failure happened in test and warnings were
                        # logged  in the test
                        if not test_failure_occurred and contest_warn._WARNINGS:
                            warning_occurred = True
                            watcher_runner.test_inconclusive(contest_warn._WARNINGS)
                        # checking if user pressed stop button
                        if self.project_specs["triggered_from_gui"]:
                            if self.project_specs["gui_object"][0].stop_state:
                                if test_cases[-1][0] == "global_teardown":
                                    # removing all tests except 'global_teardown' in test_cases list
                                    # if 'global_teardown' exists in test_cases list
                                    del test_cases[test_index:-2]
                                else:
                                    # removing all remaining tests
                                    del test_cases[test_index:]
                        watcher_runner.test_finished()
                        # clear the test case metadata files after the test case files are processed for html report
                        _clear_files_for_report()
                    # Give sometime to end all processes from previous testcase.
                    # Randomly chosen time that showed to be safe. Adapt if needed.
                    time.sleep(0.5)
                    # cleanup local parameters. do this AFTER all testcases to have them cleaned up
                    # also for teardown method
                    clear_local_params()
                    # clean up failures of contest_expects.py
                    contest_expects.FAILURES.clear()
                    # clearing warning list for next test case
                    contest_warn._WARNINGS.clear()
                # changing the final return status of test runner if there were no failures captured during complete
                # test run and at-least a test case logged warning
                if warning_occurred and status != TEST_FAILURE:
                    status = INCONCLUSIVE
                watcher_runner.test_run_finished(self.project_specs["missing_tests"])
                self.__final_logs()

            # handle all exceptions within the framework and notify the user
            except Exception as error:  # pylint: disable=broad-except
                LOG.exception(error)

            finally:
                client_informer.REST_CLIENT_INFORMER.status = "idle"
                client_informer.REST_CLIENT_INFORMER.test_name = None
                # Reset cwd to original one
                os.chdir(orig_cdw)
                save_exe_record()
        # returning tests execution status
        return status
