"""
    Module to handle global parameters for (global_)setup and (global_)teardown methods.

    Copyright 2018 Continental Corporation

    :file: global_params.py
    :platform: Windows, Linux
    :synopsis:
        This module allows the user to make use of a global "key" -> "value" dictionary with
        different lifetimes for the variables. Using ``set_global_parameter()`` you will set a
        parameter that will live during whole test execution, where ``set_local_parameter()`` will
        only set the parameter for a single testcase. Use ``get_parameter()`` to read out the
        stored parameter.

    :author:
        - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""

import logging
import inspect
import time
import os
from contest_verify.verify import contest_asserts
import global_vars

LOG = logging.getLogger('GLOBAL_PARAMS')

# pylint: disable=global-statement
# The purpose of this module is to provide easy access to global parameters, therefore we need the
# global statement.

_GLOBAL_PARAMS = {}
_LOCAL_PARAMS = {}
_REPORT_PARAMS = {}
_REPORT_WATCHER = None

# dictionary stores project cfg paths
_PROJECT_SPECS = dict()
_Test_Verdict = dict()
_ALL_TESTS_TO_RUN = list()
# dictionary stores all the executed test cases information
_Test_Data_Info = dict()
# stores the test case meta-data files
_Test_Case_MetaData_Files = list()


def set_global_parameter(key, value, overwrite=False):
    """
    Sets a global parameter value that is available for all test methods globally.
    Values can be retrieved using ``get_parameter``.
    Global parameter are reset before a new test execution.

    :param str key: The name of the parameter to set
    :param int/str/bool/float/list/object value: The value of the parameter to set
    :param bool overwrite: Set this to true if you want to overwrite the value if it already exists

    Example::

        from ptf.ptf_utils.global_params import set_global_parameter

        # sets a global parameter of name "num_1" with integer value 10
        set_global_parameter("num_1", 10)
    """

    global _GLOBAL_PARAMS
    if not overwrite and key in _GLOBAL_PARAMS:
        raise KeyError(
            "Key '{}' already exists in global parameter. Please use a different one.".format(key))
    _GLOBAL_PARAMS[key] = value


def set_local_parameter(key, value, overwrite=False):
    """
    Sets a local parameter value that is available for a single test case. Local parameters will
    hide global parameters.
    Values can be retrieved using ``get_parameter``.
    Local parameter are reset before each testcase.

    :param str key: The name of the parameter to set
    :param int/str/bool/float/list/object value: The value of the parameter to set
    :param bool overwrite: Set this to true if you want to overwrite the value if it already
                      exists in global parameters

    Example::

        from ptf.ptf_utils.global_params import set_local_parameter

        # sets a local parameter of name "flag" with boolean value True
        set_local_parameter("flag", True)
    """

    global _LOCAL_PARAMS
    if not overwrite and (key in _GLOBAL_PARAMS or key in _LOCAL_PARAMS):
        raise KeyError(
            "Key '{}' already exists in global or local parameter."
            " Please use a different one.".format(key))
    _LOCAL_PARAMS[key] = value


def set_reporting_parameter(name_of_param, value_of_param):
    """
    Sets a reporting parameter value so that it can be passed into html summary report.
    Values can be retrieved using ``get_reporting_parameter`` or ``get_parameter``.

    :param str name_of_param: Name of the parameter
    :param str value_of_param: Value of the parameter

    Example::

        from ptf.ptf_utils.global_params import set_reporting_parameter

        # sets a reporting parameter which will be shown in tabular form in html summary report
        set_reporting_parameter("Test Type", "HIL Tests")
        set_reporting_parameter("Version", "1.0")
    """

    global _REPORT_PARAMS
    if name_of_param in _REPORT_PARAMS:
        raise KeyError(
            "Parameter '{}' already exists in report parameters."
            " Please use a different one.".format(name_of_param))
    _REPORT_PARAMS[name_of_param] = value_of_param


def add_meta_data_links_to_reports(files):
    """
    Function to add meta data file(s) in HTML and JSON report of the test case in which this API is called

    .. note::

        The files can be in any format ``jpg, png, html etc.``. This API will create hyperlinks
        in test case HTML and JSON report

    :param str/list files: list of files or single file as string

    Example::

        from ptf.ptf_utils.global_params import add_file_hyperlink_to_html_report
        # add files as hyperlinks which will be shown in test case html and json report in which this API
        # shall be called
        add_meta_data_links_to_reports(files=r"D:\\img\\img_jpg.jpg")
        add_meta_data_links_to_reports(files=r"D:\\img\\img_png.png")
        add_meta_data_links_to_reports(files=r"D:\\img\\img_html.html")
        add_meta_data_links_to_reports(files=[r"D:\\img\\img_1.jpg", r"D:\\img\\img.jpg"])
    """
    global _Test_Case_MetaData_Files
    files_not_existing = list()
    files_already_added = list()
    if isinstance(files, str):
        # check the file exits or not
        if not os.path.exists(files):
            contest_asserts.fail("File does not exist: {}".format(files))
        # check the file already exits in list or not
        if files in _Test_Case_MetaData_Files:
            contest_asserts.fail("File already added: {}".format(files))
        _Test_Case_MetaData_Files.append(files)
    elif isinstance(files, list):
        for file in files:
            # check the file exits or not then add
            if not os.path.exists(file):
                files_not_existing.append(file)
            # check the file found in the list or not then add
            elif file in _Test_Case_MetaData_Files:
                # only append if it's not already added to target list
                if file not in files_already_added:
                    files_already_added.append(file)
            # only add file to final list if all checks passed
            else:
                _Test_Case_MetaData_Files.append(file)
        # check the files already exits or added
        if files_not_existing:
            contest_asserts.fail("List of files or single file does not exist: {}".format(
                files_not_existing))
        if files_already_added:
            contest_asserts.fail(
                "List of files or single file already added with same name: {}".format(files_already_added))


def add_file_hyperlink_to_html_report(files):
    """
    Function to add file(s) in HTML report of the test case in which this API is called

    .. note::

        This API will be deprecated in future. Please use the new API ``add_meta_data_links_to_reports``, which will add
        the meta data files information to HTML and JSON reports.
    """
    LOG.info("'add_file_hyperlink_to_html_report' API will be deprecated in upcoming ConTest releases. "
             "\nPlease use the new API 'add_meta_data_links_to_reports', which will add the meta data files "
             "information to HTML and JSON reports")
    add_meta_data_links_to_reports(files)


def get_gui_stop_state():
    """
    Function to get the status of stop button of gui

    .. note::

        This API is only useful in GUI mode. Based on the state value users can take an action in
        their python scripts e.g. stopping the execution of tests etc.

    .. note::

        DISCLAIMER: User shall be responsible for any adverse effect(s). If result value of this
        API with some step(s) are taken with which will result in tests execution halt.

    :returns: GUI Stop button state, ``True`` (if button was pressed) ``False`` (if button was not
        pressed or gui was not used at all)
    :rtype: bool

    Example::

        from ptf.ptf_utils.global_params import get_gui_stop_state
        gui_stop_button_state = get_gui_stop_state()
        print(gui_stop_button_state)
    """
    return global_vars.STOP_STATE_GUI


def _get_files_for_report():
    """
    Returns the stored meta data files for html test case report.

    :return: returns the list of files
    :rtype: list
    """

    return _Test_Case_MetaData_Files


def _clear_files_for_report():
    """
    It clears test case metadata files
    """
    _Test_Case_MetaData_Files.clear()


def get_reporting_parameter():
    """
    Returns the stored reporting parameters.
    Reporting parameter or Test data stored can be fetched by this method

    :return: The dictionary with reporting parameters
    :rtype: dict

    Example::

        from ptf.ptf_utils.global_params import get_reporting_parameter

        # call to get all reporting parameters
        report_params = get_reporting_parameter()
        # print the dictionary returned just for example
        print(report_params)
    """
    return _REPORT_PARAMS


def get_parameter(key, default=None):
    """
    Returns the stored parameter value with a given name.
    Local values are hiding global values.

    :param str key: The name of the parameter to return
    :param object default: The default value if the key does not exist

    :return: The value of the parameter

    Example::

        from ptf.ptf_utils.global_params import get_parameter

        # call to get a parameter value
        value = get_parameter("num_1")
        # print the value returned just for example
        print(value)
    """

    if key in _LOCAL_PARAMS.keys():
        return _LOCAL_PARAMS[key]

    if key in _GLOBAL_PARAMS.keys():
        return _GLOBAL_PARAMS[key]

    if key in _REPORT_PARAMS.keys():
        return _REPORT_PARAMS[key]

    if default:
        return default

    raise KeyError(

        "Key '{}' is not found in global, local or report parameter list. Please check if you"
        " have created this key in global or local setups.".format(key))


def get_cfg_paths(cfg_path_name=""):
    """
    Returns all config paths or specific config path from the current running test

    :param str cfg_path_name: The name of the path that has to be returned.
                              When no path name is given(default), returns all available paths

    :return: str, dict: Specific path as a string or all paths in a dictionary.

    Example::

        from ptf.ptf_utils.global_params import get_cfg_paths

        # call to get the path in form of string where reports of tests are stored
        report_path = get_cfg_paths("baseReport")
        # call to get the paths in form of dictionary saved in current loaded configuration
        cfg_file_paths = get_cfg_paths()
    """
    path_name_list = list(_PROJECT_SPECS["paths"].keys())

    if cfg_path_name in path_name_list:
        return _PROJECT_SPECS["paths"][cfg_path_name]
    if not cfg_path_name:
        return _PROJECT_SPECS["paths"]
    contest_asserts.fail(
        "Config path name: '{}' is not found! Please check if the entered path name is correct. "
        "Available config paths: {}".format(cfg_path_name, path_name_list))


def clear_global_params():
    """
    .. note::
        JUST TO BE CALLED FROM TEST FRAMEWORK. DON'T CALL THIS IN YOUR SCRIPTS.
    """
    global _GLOBAL_PARAMS
    _GLOBAL_PARAMS.clear()


def clear_local_params():
    """
    .. note::
        JUST TO BE CALLED FROM TEST FRAMEWORK. DON'T CALL THIS IN YOUR SCRIPTS.
    """
    global _LOCAL_PARAMS
    _LOCAL_PARAMS.clear()


def clear_reporting_params():
    """
    .. note::
        JUST TO BE CALLED FROM TEST FRAMEWORK. DON'T CALL THIS IN YOUR SCRIPTS.
    """
    global _REPORT_PARAMS
    _REPORT_PARAMS.clear()


def get_test_verdict(test_name=None):
    """
    To get the test verdict of all tests or a specific test requested by user

    :param str test_name: Test case name whose verdict is required. Default is ``None`` where the verdicts of all
        tests shall be returned.

    :returns: Requested test case verdict in form of string or dictionary with verdicts of all tests.
        Possible values ``NOT_EXEC, NOT_AVAILABLE, PASS, INCONCLUSIVE, FAIL, SKIPPED``
    :rtype: str or dictionary

    Example::

        from ptf.ptf_utils.global_params import get_test_verdict

        # getting test verdict of "SWT_MY_TESTv1" test case
        test_verdict = get_test_verdict("SWT_MY_TESTv1")
        # getting verdicts of all tests
        all_test_verdict = get_test_verdict()
    """
    if test_name:
        if test_name in _ALL_TESTS_TO_RUN:
            if test_name in _Test_Verdict.keys():
                return _Test_Verdict[test_name]
            else:
                return "NOT_EXEC"
        else:
            return "NOT_AVAILABLE"
    else:
        tests_verdicts = dict()
        for test in _ALL_TESTS_TO_RUN:
            if test in _Test_Verdict.keys():
                tests_verdicts[test] = _Test_Verdict[test]
            else:
                tests_verdicts[test] = "NOT_EXEC"
        return tests_verdicts


def get_testcase_data(test_name):
    """
    To get the test case data information requested by user

    :param str test_name: Test case name whose data is required

    :returns: Requested test case data in the form of dictionary.
    :rtype: dict

    Example::

        from ptf.ptf_utils.global_params import get_test_data_info

        # getting test case data of "SWT_MY_TESTv1" test case
        test_data_info = get_test_data_info("SWT_MY_TESTv1")
    """
    if test_name in _Test_Data_Info.keys():
        return _Test_Data_Info[test_name]
    else:
        return {test_name: "NOT AVAILABLE or NOT EXECUTED"}


def manual_verification(query):
    """
    Function for manual verification to be used in semi automated test cases

    .. note:
        This function shall **NOT** be used in test cases which are meant to run in automated mode
        i.e. with `-r auto` CLI option.

    :param str query: User query data to display on popup window.

    :returns: List containing verdict and comment from user ['Yes/No', 'user_comment'].
        In Non-Gui mode list ['None', ''] will be returned.
    :rtype: list

    Example::

        from ptf.ptf_utils.global_params import manual_verification

        # call for opening a pop-up window with question "Is ECU connected?" which need to be
        # answered by user manually
        return_value = manual_verification("Is ECU connected?")
        # return value in case of yes/no answer
        ["Yes", "user comment (if any)"]
        ["No", "user comment (if any)"]
        # return value in case of automated runs e.g. jenkins
        ["None", ""]
    """

    if not _PROJECT_SPECS["gui_object"]:
        logging.critical("manual_verification function shall not be executed during non-gui mode")
        non_gui_ret_list = ['None', '']
        return non_gui_ret_list
    else:
        # Creating an object of SemiAutomation class
        man_ver_obj = _PROJECT_SPECS["gui_object"][0].semi_auto_obj
        man_ver_obj.timer_manual_verify.hide()
        # Clearing Class variable 'user_text' before calling popup window
        man_ver_obj.user_text.clear()
        # Signal emit for executing SemiAutomation window Class along with query and test case name
        _PROJECT_SPECS["gui_object"][0].emit_sig('test_manual_input', [query,
                                                                       inspect.stack()[1][3]])

        # Pausing the python program until the popup window is open
        # conditions to hold: timeout or user input entry
        while len(man_ver_obj.user_text) == 0:
            time.sleep(1)
            # Todo: Needs further investigation, as the below code creates a framework crash,
            #  when user tries to interact with window during window.
            # if enable_timer and timeout > 0:
            #     mins, secs = divmod(timeout - 1, 60)
            #     lcd_time = "{0:02d}:{1:02d}".format(mins, secs)
            #     _PROJECT_SPECS["gui_object"][0].semi_auto_obj.timer_manual_verify.show()
            #     _PROJECT_SPECS["gui_object"][0].semi_auto_obj.timer_manual_verify.display(lcd_time)
            #     timeout = timeout - 1
            # elif enable_timer and int(timeout) is 0:
            #     _PROJECT_SPECS["gui_object"][0].semi_auto_obj.user_text = [ManualVerifyReturns
            #                                                                .TIMEOUT.value, ""]
            #     _PROJECT_SPECS["gui_object"][0].semi_auto_obj.close()
            #     break
        # returns a user_text list containing button click info and input text
        return man_ver_obj.user_text


def get_selected_pytests_data_objs():
    """
    To get the list of python tests data objects selected for execution.

    :return: List containing TestData objects
    :rtype: list

    Example::

        # importing the relevant function
        from ptf.ptf_utils.global_params import get_selected_pytests_data_objs
        # get list of all python tests data objects selected for execution
        python_tests_data_objs = get_selected_pytests_data_objs()
    """
    return _PROJECT_SPECS["test_info"].return_selected_pytests_data()


def get_selected_cmm_tests_data_objs():
    """
    To get the list of cmm tests data objects selected for execution.

    :return: List containing TestData objects
    :rtype: list

    Example::

        # importing the relevant function
        from ptf.ptf_utils.global_params import get_selected_cmm_tests_data_objs
        # get list of all cmm tests data objects selected for execution
        cmm_tests_data_objs = get_selected_cmm_tests_data_objs()
    """
    return _PROJECT_SPECS["test_info"].return_selected_cmm_data()


def get_selected_capl_tests_data_objs():
    """
    To get the list of capl tests data objects selected for execution.

    :return: List containing TestData objects
    :rtype: list

    Example::

        # importing the relevant function
        from ptf.ptf_utils.global_params import get_selected_capl_tests_data_objs
        # get list of all capl tests data objects selected for execution
        capl_tests_data_objs = get_selected_capl_tests_data_objs()
    """
    return _PROJECT_SPECS["test_info"].return_selected_capl_data()


def get_selected_pytests_folders():
    """
    To get all script folders for the selected python tests.

    :return: List containing script folders of all selected python tests for execution
    :rtype: list

    Example::

        # importing the relevant function
        from ptf.ptf_utils.global_params import get_selected_pytests_folders
        # get list of all python tests script folders selected for execution
        python_tests_folders = get_selected_pytests_folders()
        # printing just for example
        print("The selected python tests folders are: ", python_tests_folders)
    """
    return _PROJECT_SPECS["test_info"].return_selected_pytests_folders()


def get_selected_pytests_names():
    """
    To get all names for the selected python tests.

    :return: List containing names of all selected python tests for execution
    :rtype: list

    Example::

        # importing the relevant function
        from ptf.ptf_utils.global_params import get_selected_pytests_names
        # get list of all python tests names selected for execution
        python_tests_names = get_selected_pytests_names()
        # printing just for example
        print("The selected python tests names are: ", python_tests_names)
    """
    return _PROJECT_SPECS["test_info"].return_selected_pytests_names()


def get_specific_pytest_data(test_name):
    """
    To get data object for a specific python test case

    :param str test_name: Test case name whose test data object is required

    :return: Data object of requested test case or None in-case it's not found
    :rtype: Object/None

    Example::

        # importing the relevant function
        from ptf.ptf_utils.global_params import get_specific_pytest_data
        # get data object of 'SWT_DEMOv1' test case
        test_data_obj = get_specific_pytest_data("SWT_DEMOv1")
        # printing just for example
        print("The test case script name: ", test_data_obj.test_script)
    """
    return _PROJECT_SPECS["test_info"].return_specific_pytest_data(test_name)


def get_current_test_info():
    """
    Function to get meta-data about current test case in execution phase

    .. note::
        It's recommended to call this function after your test specification functions i.e. ``DETAILS, TESTSTEPS etc.``

    :return: Class object the current test case meta-data information
    :rtype: TestCaseInfo Class object

    Example::

        # importing the relevant function in test scripts
        from ptf.ptf_utils.global_params import get_current_test_info

        # fetching meta-data
        test_info = get_current_test_info()

        # printing test case information
        print("Test ETM Automates ID: ", test_info.automates)
        print("Test Details: ", test_info.details)
        print("Test Preconditions: ", test_info.precondition)
        print("Test Tags: ", test_info.tags)
        print("Test Requirement IDs: ", test_info.verified_ids)

        # check further attributes of ``test_info`` and then access them as above if necessary
        print(dir(test_info))
    """
    # this will be set in .watcher.test_watcher.TestCaseInfo.__init__ for every new test case
    from ptf.ptf_utils.test_watcher import CURRENT_TESTCASE
    test_case_info = CURRENT_TESTCASE[0]
    return test_case_info
