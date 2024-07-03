"""
    Copyright 2019 Continental Corporation

    :file: project.py
    :platform: Windows, Linux
    :synopsis:
        Script for grabbing and saving test cases data

    :author:
        - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
        - M. Vanama Ravi Kumar <ravi.kumar.vanama@continental-corporation.com>
"""
# disabling all pylint checks for this file as it will be handled in
# https://jira.auto.continental.cloud/browse/GUILDS-3797
# pylint: disable-all

# standard python imports
import os
import traceback
import json
import sys
import logging
import glob
import itertools
import inspect
import functools
import fnmatch
import datetime
import re
import subprocess
from rest_service import client_informer
from collections import Counter
# using ordered dictionary from collections module to support python 3.5 version (primarily used on
# ubuntu machine)
# in python 3.5 version the normal dictionary keys does not come in order when accessed in loop
from collections import OrderedDict
# Use importlib.util here - not importlib - or importlib.util.* function calls  won't be found in
# ubuntu in runtime execution (but still works in debugger O.o)
import importlib.util
# custom imports
from . import helper
from .helper import InfoLevelType
from .data_reporter import DataReporter
from gui import ui_helper
import zipfile

LOG = logging.getLogger("DATA_PREP")


# pylint: disable=too-few-public-methods
class TestData:
    """
    Template class for saving test cases (python, cmm, capl) data
    """

    def __init__(self, test_case_name):
        """
        Constructor

        :param string test_case_name: Test cases name whose data need to be saved
        """
        self.name = test_case_name
        # this variable used to store the parameterized test case of param sets test names which is used to display on
        # output window
        self.param_test_names = list()
        self.tag = list()
        self.priority = None
        self.object = None
        self.test_script = None
        self.folder_structure = None
        self.execute = False
        self.groups = list()
        self.tests = list()
        self.order_value = None
        self.verifies_id = list()
        self.automates_id = list()
        self.status_of_test_verify = bool()
        self.test_case_parameters = list()
        self.test_case_parameters_values = list()
        # variable to store custom setup and teardown methods (non-standard) in loaded setup.pytest file
        self.custom_setup = None
        self.custom_teardown = None
        self.skip_condition = False
        self.skip_reason = "No skip reason specified"
        # variable to store the path of loaded setup.pytest script
        self.setup_script_path = None


# pylint: disable=too-many-public-methods
class PrepareTestData:
    """
    Class for preparing tests data to be used by test runner and/or gui
    """

    def __init__(self, gui=None):
        """
        Constructor

        :param object gui: Object of GUI which helps to communicate information (errors, warnings
            etc.) with GUI. This parameter will only be used when data preparation is requested from
            GUI otherwise the information will only be directed to console. Default value is None.
        """
        # allow dynamic loader to load also '.pytest' files
        importlib.machinery.SOURCE_SUFFIXES.append('.pytest')
        # grabbing the informer method object to share information with the user on console or with
        # gui if gui object is provided
        self.gui = gui
        self.data_reporter = DataReporter(self.gui)
        self.log = self.data_reporter.log
        # dictionary containing test cases related data
        self.data = {
            # list containing all python test cases and their data
            "py_test_data": list(),
            # list containing all python test cases found in all .pytest scripts for duplicate test
            # functions check
            "all_py_test_cases_for_duplicates_check": list(),
            # dictionary containing python test cases names as keys and key values as their data
            # this is added to get fast filtering when user selects tests on gui
            "py_test_data_dict": dict(),
            # list containing all cmm test cases and their data
            "cmm_test_data": list(),
            # dictionary containing cmm test cases names as keys and key values as their data
            # this is added to get fast filtering when user selects tests on gui
            "cmm_test_data_dict": dict(),
            # list containing all cmm test cases scripts (SWT_*.cmm)
            "cmm_files": list(),
            # list containing all python test cases scripts (swt_*.pytest)
            "pytest_files": list(),
            # list containing all setup scripts (setup*.pytest)
            "setup_files": list(),
            # dictionary containing the selected tests (python, cmm, capl)
            "tests_in_cfg": dict(),
            # dictionary for storing the canoe test modules names with hierarchy
            "canoe_test_data": dict(),
            # list containing names of all test modules in canoe cfg
            "canoe_test_names": list()
        }
        # dictionary to store the setup.pytest file function names as key and function object as their respective
        # value e.g. {"global_setup": <func_obj>, "global_teardown": <func_obj>, ...}
        self.setup_file_data = dict()
        # current configuration information
        self.current_cfg = None
        # project_paths info
        self.project_paths = None
        # tests_path info as dictionary
        self.tests_path = dict()
        # report_path is used for report folder path
        self.report_path = None
        # for saving the order number of the test case i.e. the order how tests are displayed on UI
        self.test_order_value = 0
        # dictionary contains python test cases information
        self.py_test_dict = dict()
        # capturing all the test case displayed into list
        self.appearing_overall_tests = list()
        # capturing all test cases based on filter tag as key and value as list of tests
        self.tag_filter_tests = dict()
        # dictionary contains tag information as key and value
        self.test_case_tag = dict()
        # list containing all tags for test cases
        self.tags = list()
        # dictionary for storing data for test runner stage
        self.test_runner_data = {
            "py_tests": list(),
            "cmm_tests": list(),
            "capl_tests": list(),
            "setup_files": dict(),
            "paths": dict(),
            "tests_frequency": 1,
            "randomize": False,
            "triggered_from_gui": False,
            "gui_object": list(),
            "missing_tests": list(),
            "parameterized_tests": dict(),
            # flag for storing the usage of CTF framework which shall be used in test runner
            # 'decorator_test_runner_capl' for fetching results of capl test cases from xml
            # generated reports in order to support traceability
            "ctf_enabled": False,
            "ext_report_dir_with_timestamp": None,
        }
        # Store all parameterized test case parameters and their values which is used for
        # test runner in default cases
        self.all_parameterized_tests = dict()

    def __detect_tests_duplications(self):
        """
        Method for detecting if user has any duplication of test scripts or test cases in base
        location. We don't allow duplications and if duplications are found then user will be
        prompted. If duplicated names for test scripts or test cases names are found then error
        will be raised.

        :return: returns a tuple with duplication status and error string if any
        :rtype: tuple
        """
        # first check duplication of test scripts
        # getting counter of all test scripts (.pytest, .cmm)
        test_script_list = Counter(
            [os.path.split(test_script)[1] for test_script in self.get_pytest_files()]
            + [os.path.split(test_script)[1] for test_script in self.get_cmm_files()])
        # checking if test scripts are duplicated via its counter value
        duplicate_scripts = \
            ["'{}' duplicated {} times".format(test_script, count) for test_script, count in
             test_script_list.items() if count > 1]
        # if duplication found then raise relevant error
        if duplicate_scripts:
            err_msg = "Same name(s) of test script(s) detected.\nSearch following scripts " \
                      "in base location folder '{}' and use unique names.\n\n" \
                      "Duplicate Scripts:\n{}".format(self.get_base_path(),
                                                      '\n'.join(duplicate_scripts))
            return True, err_msg
        # now check duplication of test cases names in all test scripts
        # getting counter of all test cases names in all scripts (.pytest, .cmm)
        py_cmm_test_cases_list = Counter(
            [test_case for test_case in self.data["all_py_test_cases_for_duplicates_check"]]
            + [test_data.name for test_data in self.data["cmm_test_data"]])
        # checking if test names are duplicated via its counter value
        duplicate_tests = \
            ["'{}' duplicated {} times".format(test_name, count) for test_name, count in
             py_cmm_test_cases_list.items() if count > 1]
        # if duplication found then raise relevant error
        if duplicate_tests:
            err_msg = "Same name(s) of test cases(s) detected.\nSearch following test names " \
                      "in test scripts at '{}' and use unique test names.\n\n" \
                      "Duplicate Test Names:\n{}".format(self.get_base_path(),
                                                         '\n'.join(duplicate_tests))
            return True, err_msg
        # now check duplication of test cases names in extracted CANoe test modules/test cases
        # getting counter of all test cases names
        canoe_test_cases_list = Counter(
            [canoe_test for canoe_test in self.data["canoe_test_names"]])
        # checking if test names are duplicated via its counter value
        canoe_duplicate_tests = \
            ["'{}' duplicated {} times".format(test_name, count) for test_name, count in
             canoe_test_cases_list.items() if count > 1]
        # if duplication found then raise relevant error
        if canoe_duplicate_tests:
            err_msg = "Same test module name(s) in CANoe configuration detected.\n" \
                      "Search following test module in loaded CANoe configuration and use unique " \
                      "test module names.\n\n" \
                      "Duplicate Test Modules:\n{}".format('\n'.join(canoe_duplicate_tests))
            return True, err_msg
        # no duplication was found therefore return False and None as error
        return False, None

    def __get_test_paths(self, configuration):
        """
        Getting tests paths (Python, CAPL, CMM) from project configuration
        TODO: How to expose paths to our general Classes (Lauterbach etc.)
        TODO: One way will be to make a temp files using 'tempfile' python module so information
        TODO: exists till test run ... other ways we can discover in POC

        :param ProjectConfigHandler configuration: Configuration file user selected

        :return: Dictionary containing paths of test types i.e. ptf tests, t32 tests and capl tests
        :rtype: dict
        """
        # getting tests paths. Read absolute paths.
        # Project Base Path
        self.tests_path[helper.BASE_PATH] = os.path.abspath(configuration.base_path)
        # Python Tests
        self.tests_path[helper.PTF_TEST] = os.path.abspath(configuration.ptf_test_path)
        # saving t32 tests path
        self.tests_path[helper.T32_TEST] = os.path.abspath(configuration.cmm_test_path) \
            if configuration.cmm_test_path else configuration.cmm_test_path
        # saving canoe cfg path
        self.tests_path[helper.CANOE_CFG] = os.path.abspath(configuration.canoe_cfg_path) \
            if configuration.canoe_cfg_path else configuration.canoe_cfg_path
        # saving cte exe path
        self.tests_path[helper.CTE_ZIP] = os.path.abspath(configuration.cte_location) \
            if configuration.cte_location else configuration.cte_location
        # saving cte cfg path
        self.tests_path[helper.CTE_CFG] = os.path.abspath(configuration.cte_cfg) \
            if configuration.cte_cfg else configuration.cte_cfg
        # saving cte use flag
        self.tests_path[helper.USE_CTE] = True if configuration.use_cte_checkbox == "True" else \
            False
        # reports path
        self.report_path = os.path.abspath(configuration.report_path)
        self.tests_path[helper.BASE_REPORT_DIR] = self.report_path
        # paths needed by tools are set here to be used by tools api
        helper.PTF_CFG_TOOL_DATA[helper.T32_EXE_PATH] = \
            configuration.t32_executable_name
        helper.PTF_CFG_TOOL_DATA[helper.T32_SRC_PATH] = \
            configuration.t32_source_code_path
        self.tests_path[helper.TXT_REPORT] = configuration.report_path
        # returning dictionary of test paths
        return self.tests_path

    @staticmethod
    def __getting_py_test_metadata(source_py_test_function, expected_metadata):
        """
        Internal Method to find the requested metadata within test function source

        :param source_py_test_function: source lines of the test function
        :param string expected_metadata: requested metadata (for example: "TESTTAG")
        :return: list of the requested metadata for a test function
        :rtype: list
        """
        request_meta_data = []
        function_corpus = "".join(source_py_test_function[0])

        # This regular expressions extracts the content of a string, i.e. the
        # text between single or double quotation marks. It doesn't resolve
        # variables, formatted strings or other functions returning string.
        pattern = re.compile(
            rf"""
                    {expected_metadata}  # Expected metadata-tag (e.g. TESTDATA)
                    \(                   # Opening parenthesis
                    \s*                  # Optional whitespaces (e.g. linebreaks)
                    [bBfFrRuU]*          # Optional string modifiers (binary, formatted,
                                         #     raw and unicode)
                    (['\"]{{3}}|['\"])   # Start of single- or multiline string
                    (.*?)                # Content of the string
                    \1                   # End of string
                    \s*                  # Optional whitespaces
                    \)                   # Closing parenthesis
                """,
            flags=re.DOTALL | re.VERBOSE,
        )

        for _, content in pattern.findall(function_corpus):
            if content and (content not in request_meta_data):
                request_meta_data.append(content)

        return request_meta_data

    @staticmethod
    def __check_for_test_verify_test_step(source_py_test_function):
        """
        Internal method to check test case contain ptf_expects or ptf_asserts

        :param source_py_test_function: source lines of the test function
        :return: return status
        :rtype:bool
        """
        metadata_line_list = [metadata_line for metadata_line in source_py_test_function[0]
                              if (metadata_line.lstrip().startswith("ptf_asserts.")
                                  or metadata_line.lstrip().startswith("ptf_expects.")
                                  or metadata_line.lstrip().startswith("assert"))
                              ]
        return bool(metadata_line_list)

    def get_tags(self):
        """
        Method which gives back the test tags and their frequency

        :return: Dictionary with keys as tags and their values as their frequency
        :rtype: Dictionary
        """
        return Counter(self.tags)

    def get_setup_files(self):
        """
        Method which gives back the list of setup*.pytest files residing in python test location

        :return: List containing all setup*.pytest files in python test location
        :rtype: list
        """
        return self.data["setup_files"]

    def get_pytest_files(self):
        """
        Method which gives back the list of swt_*.pytest files residing in python test location

        :return: List containing all swt_*.pytest files in python test location
        :rtype: list
        """
        return self.data["pytest_files"]

    def get_python_test_data(self):
        """
        Method for returning back the python tests extracted data
        """
        return self.data["py_test_data_dict"]

    def get_cmm_files(self):
        """
        Method which gives back the list of SWT_*.cmm files residing in cmm test location

        :return: List containing all SWT_*.cmm files in cmm test location
        :rtype: list
        """
        return self.data["cmm_files"]

    def get_cmm_test_data(self):
        """
        Method for returning back the cmm tests extracted data
        """
        return self.data["cmm_test_data_dict"]

    def get_capl_files(self):
        """
        Method which gives back the list of all test modules in loaded CANoe configuration

        :return: List containing all test modules in loaded CANoe configuration
        :rtype: list
        """
        return self.data["canoe_test_names"]

    def add_test_order_number(self, test):
        """

        :return:
        """
        self.test_order_value = self.test_order_value + 1
        test.order_value = self.test_order_value

    def prepare_cmm_tests(self):
        """
        Method for extracting data related to cmm test cases (name, test script, folder structure
          , execute etc.)
        CMM test scripts (SWT_*.cmm) will be checked for any initial errors
        (syntax errors etc.)
        """
        self.data["cmm_files"].clear()
        self.log(
            "Starting to prepare cmm tests data at {}".format(
                self.tests_path[helper.T32_TEST]))
        # get all files starting from "swt_" which will be treated as cmm test cases scripts
        self.data["cmm_files"] = self.get_filtered_files(
            self.tests_path[helper.T32_TEST], "SWT_*.cmm")
        if not self.data["cmm_files"]:
            self.log("No cmm test scripts found", InfoLevelType.WARN)
        else:
            self.log("{} cmm test scripts found".format(len(self.data["cmm_files"])))

        # loop for extracting test functions data in each test script and checking for initial
        # errors
        for test_script in self.data["cmm_files"]:
            self.extract_cmm_test_data(test_script)
        self.log("{} cmm tests found".format(len(self.data["cmm_test_data"])))

    def extract_cmm_test_data(self, cmm_test_script):
        """
        Method for extracting and saving test cases data existing in a given cmm script

        The extracted data for each test case (function) will be saved in a template class
        "TestData" and appended into cmm tests data list

        :param string cmm_test_script: Test cases script location (SWT_xxx.cmm)
        """
        # test case found in script therefore now inject test case data in template class
        test_name = os.path.basename(cmm_test_script)
        test_data = TestData(test_name)
        test_data.folder_structure, test_data.test_script = os.path.split(cmm_test_script)
        # Tag information of test data
        test_data.tag.append(ui_helper.CMM_FILTER_NAME)
        self.add_test_order_number(test_data)
        self.tags.append(ui_helper.CMM_FILTER_NAME)
        self.test_case_tag[test_name] = test_data.tag
        # store the test case name into list, to display number of test cases on LCD GUI
        self.appearing_overall_tests.append(test_name)
        # tag_filter_tests is used to store the tests based on tag into dict
        if ui_helper.CMM_FILTER_NAME not in self.tag_filter_tests:
            self.tag_filter_tests[ui_helper.CMM_FILTER_NAME] = list()
        self.tag_filter_tests[ui_helper.CMM_FILTER_NAME].append(test_data.name)

        # Not required  object, priority for Test data

        # if this test is present in selected list then make execution flag as True
        if test_name in self.data["tests_in_cfg"]["cmm_tests"]:
            test_data.execute = True
        self.data["cmm_test_data"].append(test_data)
        self.data["cmm_test_data_dict"][test_name] = test_data

    def prepare_canoe_tests(self, canoe_cfg, use_ctf, cte_zip, cte_cfg):
        """
        Method for preparation of CANoe related tests.

        :param string canoe_cfg: CANoe cfg path given in contest cfg file
        :param bool use_ctf: Flag for using CTF (CANoe Test Environment)
        :param string cte_zip: CTF (CANoe Test Environment) zip path on machine
        :param string cte_cfg: CTF (CANoe Test Environment) configuration path on machine
        """
        # clearing the saved data of canoe test modules if any
        self.data["canoe_test_data"].clear()
        self.data["canoe_test_names"].clear()
        canoe_app = None
        # take actions if CTF (CANoe Test Environment) is requested to be used
        if use_ctf:
            self.test_runner_data["ctf_enabled"] = True
            # call CTF here
            self.log("Calling CTF for CANoe tests preparation. "
                     "This will take sometime please wait ...")
            if self.gui and not self.gui.args['auto_gui']:
                ui_helper.pop_up_msg(
                    helper.InfoLevelType.INFO,
                    ui_helper.CTE_CANOE_PREP_MSG.format(canoe_cfg, cte_cfg))
            if not os.path.exists(cte_zip):
                self.log("CTF Zip file '{}' does not exist on machine.".format(cte_zip),
                         info_level=InfoLevelType.ERR)
            if not os.path.exists(cte_cfg):
                self.log("CTF Cfg file '{}' does not exist on machine.".format(cte_cfg),
                         info_level=InfoLevelType.ERR)
            # un-zipping ctf and extracting files in ctf zip
            extract_dir = os.sep.join(cte_zip.split("\\")[:-1])
            if extract_dir == "":
                extract_dir = os.sep.join(cte_zip.split("/")[:-1])
            with zipfile.ZipFile(cte_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            dist_dir = os.path.join(extract_dir, "dist")
            ctf_files = os.listdir(dist_dir)
            is_new_ctf = False
            # checking if ctf is github version (new) or ims version (old)
            if "TestModuleGenerator.exe" in ctf_files:
                cmd = "{} --settings={} --parse_a2l --parse_databases --parse_capl " \
                      "--create_testmodules --create_tse_files --confirm_exit_for_errors " \
                      "--create_json_with_testmodules " \
                      "--save_and_close_cfg".format(
                          os.path.join(dist_dir, "TestModuleGenerator.exe"), cte_cfg)
                is_new_ctf = True
            elif "xml_Testmodul_Parser.exe" in ctf_files:
                cmd = "{} --settings={} --parse_a2l --parse_databases --parse_capl " \
                      "--create_testmodules --create_tse_files " \
                      "--confirm_exit_for_errors --save_and_close_cfg".format(
                          os.path.join(dist_dir, "xml_Testmodul_Parser.exe"), cte_cfg)
            else:
                self.log("CTF exe not found at " + dist_dir, info_level=InfoLevelType.ERR)
            # deleting if there is any old ctf generated json file containing test modules
            if "Test_Modules_List.json" in os.listdir(dist_dir):
                os.remove(os.path.join(dist_dir, "Test_Modules_List.json"))
                self.log("Old Test_Modules_List.json file removed " + os.path.join(
                    dist_dir, "Test_Modules_List.json"))
            # running ctf
            try:
                self.log("Running CTF call '" + cmd)
                self.log("CTF will add Test Modules in " + canoe_cfg)
                self.log("Please make sure that your CANoe and Vector Hardware setup is working "
                         "with CTF")
                self.log("If your CANoe Vector Hardware setup is not working properly then kill "
                         "the Process with Ctrl+C and run again Contest after fixing the Vector "
                         "Canoe Hardware.")
                self.log("This process might take time. Please wait ...")
                process = subprocess.run(cmd, stdout=subprocess.PIPE, shell=False)
                if process.returncode != 0:
                    error = "Error during CTF call\n Error: {}".format(
                        process.stdout.decode("utf-8", "ignore"))
                    self.log(error, info_level=InfoLevelType.ERR)
                else:
                    # if ctf is new version then json file with test module data will be generated
                    # here checking if json is actually created or not
                    if is_new_ctf:
                        if "Test_Modules_List.json" not in os.listdir(dist_dir):
                            error = "Test module list is not created by CTF at {}.".format(
                                os.path.join(dist_dir, "Test_Modules_List.json"))
                            self.log(error, info_level=InfoLevelType.ERR)
                        else:
                            ctf_mods_json = os.path.join(dist_dir, "Test_Modules_List.json")
                    self.log("CTF execution is ok")
            except subprocess.CalledProcessError as exception:
                if exception.stderr is not None:
                    raise RuntimeError(exception.stderr.decode('ascii', 'ignore'))
            except Exception:
                self.log("Base Exception raised during CTF call", info_level=InfoLevelType.ERR)
        else:
            self.test_runner_data["ctf_enabled"] = False
            self.log("CTF usage was ignored in loaded ConTest configuration")
            if self.gui and not self.gui.args['auto_gui']:
                ui_helper.pop_up_msg(
                    helper.InfoLevelType.INFO, ui_helper.CANOE_PREP_MSG.format(canoe_cfg))
        # if ctf is new version then no need to fetch data from canoe cfg as its in ctf test module
        # json file therefore extracting test modules structure and names from it
        if use_ctf and is_new_ctf:
            self.log("Starting to prepare CANoe tests data.")
            with open(ctf_mods_json, 'r') as f:
                ctf_json = json.load(f)
            tst_mod_list = list()
            self.log("Fetching Test Modules from " + ctf_mods_json)
            helper.get_capl_modules(tst_mod_list, ctf_json)
            self.data["canoe_test_data"] = ctf_json
            self.data["canoe_test_names"] = tst_mod_list
            self.tags.extend([ui_helper.CANOE_FILTER_NAME] * len(self.data["canoe_test_names"]))
        # if ctf is old version then fetch test module data from canoe cfg itself
        else:
            try:
                self.log("Starting to prepare CANoe tests data from '{}'".format(canoe_cfg))
                from ptf.tools_utils.canoe import canoe
                canoe_app = canoe.Canoe()
                canoe_app.open_cfg(canoe_cfg, visible=False)
                self.data["canoe_test_data"] = canoe_app.tse_data
                self.data["canoe_test_names"] = canoe_app.test_modules_names
                self.tags.extend([ui_helper.CANOE_FILTER_NAME] * len(self.data["canoe_test_names"]))
            except Exception as err:
                error = "Error happened while preparing CANoe tests.\n\tError: {}".format(err)
                self.log(error, info_level=InfoLevelType.ERR)
            finally:
                if canoe_app:
                    self.log("Data from CANoe cfg {} is fetched.".format(canoe_cfg))
                    canoe_app.close()

    def prepare_python_tests(self, setup_file):
        """
        Method for extracting data related to python test cases (tags, priority, name, test function object etc.)

        Python test scripts (swt_*.pytest, setup*.pytest) will be checked for any initial errors (syntax errors etc.)

        :param str setup_file: Loaded setup.pytest file path or name
        """
        self.data["pytest_files"].clear()
        self.log("Starting to prepare python tests data at {}".format(self.tests_path[helper.PTF_TEST]))
        # get all files starting from "swt_" which will be treated as python test cases scripts
        self.data["pytest_files"] = self.get_filtered_files(self.tests_path[helper.PTF_TEST], "swt_*.pytest")
        if not self.data["pytest_files"]:
            self.log("No python test scripts found", InfoLevelType.WARN)
        else:
            self.log("{} python test scripts found".format(len(self.data["pytest_files"])))
        # get and set all files starting from "setup" which will be treated as setup scripts
        self.set_setup_files(self.get_filtered_files(self.tests_path[helper.PTF_TEST], "setup*.pytest"))
        self.log("{} setup scripts found".format(len(self.data["setup_files"])))
        # calling 'filter_and_get_setup_file_data' to store the setup/teardown funcs and their objects
        self.filter_and_get_setup_file_data(setup_file)
        # adding important paths to system paths
        contest_root = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
        helper.sys_path_addition(os.path.join(contest_root, 'ptf', 'ptf_utils'))
        helper.sys_path_addition(os.path.join(contest_root, 'ptf', 'tools_utils'))
        helper.sys_path_addition(os.path.join(contest_root, 'ptf', 'verify_utils'))
        # adding all folders at ptf tests location to system path
        # this will help users to directly import python modules in .pytest or normal .py files
        helper.sys_path_addition(self.project_paths[helper.PTF_TEST])
        LOG.info("Added '%s' paths to system path", self.project_paths[helper.PTF_TEST])
        # clearing the all found python test functions/cases list --> used for duplication checks
        self.data["all_py_test_cases_for_duplicates_check"].clear()
        # clearing the param tests dictionary for fresh usage
        self.all_parameterized_tests = dict()
        # loop for extracting test functions data in each test script and checking for initial errors
        for test_script in self.data["pytest_files"]:
            self.extract_python_test_data(test_script)
        self.log("{} python tests found".format(len(self.data["py_test_data"])))

    def extract_python_test_data(self, python_test_script):
        """
        Method for extracting and saving test cases data existing in a given python script

        The extracted data for each test case (function) will be saved in a template class
        "TestData" and appended into python tests data list

        :param string python_test_script: Test cases script location (swt_xxx.pytest)
        """
        # extracting all functions objects in given script
        test_scripts_objects = self.get_py_func_obj_in_script(python_test_script)
        test_cases = []
        for test_name in test_scripts_objects:
            # checking for valid test case (excluding __disabled ones)
            if test_name.startswith(helper.TEST_NAME_FORMATS) and ('__disable' not in test_name):
                # extracting test-case names e.g. SWT_XYZv1__each()
                test_data = TestData(test_name)
                # assigning skip values to test case info class if 'skip_if' decorator used
                self.assign_skip_flag_to_test_case(test_data, test_scripts_objects[test_name])
                # here checking if the test case used 'setup' decorator and assigning the custom setup-teardown
                # to particular test case info class to be used in test runner, if the custom setup-teardown functions
                # are not found in loaded setup.pytest file saved data then error shall be raised and the particular
                # test case will not be loaded
                error = self.assign_custom_setup_teardown_to_test_case(test_data, test_scripts_objects[test_name])
                if error:
                    if self.gui:
                        if not self.gui.args['auto_gui']:
                            # case for manual or gui mode
                            ui_helper.pop_up_msg(InfoLevelType.ERR, error)
                        else:
                            # case of auto_gui mode
                            raise RuntimeError(error)
                    else:
                        # case for auto mode
                        self.log(error, InfoLevelType.ERR)
                    continue
                test_cases.append(test_name)
                test_data.test_script = python_test_script.split(os.sep)[-1]
                test_data.folder_structure, test_data.test_script = os.path.split(python_test_script)
                self.add_test_order_number(test_data)
                # store the test case name into list, to display number of test cases on LCD GUI
                self.appearing_overall_tests.append(test_name)
                # python_test_script.split(os.sep)[:-1]
                # get filter-tags (running frequency) from test case name
                if "__" in test_name:
                    stage_tag = test_name.split("__")[1].split("(")[0]
                    test_data.tag.append(stage_tag)
                    self.tags.append(stage_tag)
                    # "tag_filter_tests" is used to store the tests based on stage_tag
                    if stage_tag not in self.tag_filter_tests:
                        self.tag_filter_tests[stage_tag] = list()
                    self.tag_filter_tests[stage_tag].append(test_data.name)
                # if this test is present in selected list then make execution flag as True
                if test_name in self.data["tests_in_cfg"]["selected_tests"]:
                    test_data.execute = True
                # if test name is present in given script function object dictionary key then get
                # its value (function object) and save it
                if test_name in test_scripts_objects:
                    test_data.object = [test_scripts_objects[test_name]]
                    # if test function has a priority decorator then save it value
                    if hasattr(test_data.object[0], "__TEST_EXECUTION_PRIORITY__"):
                        test_data.priority = test_data.object[0].__TEST_EXECUTION_PRIORITY__
                # appending test case data to python test case list
                self.data["py_test_data"].append(test_data)
                self.test_case_tag[test_name] = test_data.tag
                test_data.tag.append(ui_helper.PYTHON_FILTER_NAME)
                self.tags.append(ui_helper.PYTHON_FILTER_NAME)
                self.data["py_test_data_dict"][test_name] = test_data
                # "tag_filter_tests" is used to store the tests based on python filter tag
                if ui_helper.PYTHON_FILTER_NAME not in self.tag_filter_tests:
                    self.tag_filter_tests[ui_helper.PYTHON_FILTER_NAME] = list()
                self.tag_filter_tests[ui_helper.PYTHON_FILTER_NAME].append(test_data.name)
                # getting source lines of given object (test name)
                test_obj = test_scripts_objects[test_name]
                # check it is parameterized object
                if test_obj.__name__ == "parameterized_runner":
                    # from the test object get the test name of parameterized func
                    if test_obj.__FUNC_NAME__ == test_name:
                        try:
                            # getting the parameters and its values as list of dictionaries
                            test_case_parameters_values, total_test_case_parameters = \
                                self.getting_parameterized_test_data(test_obj)
                            # checking if there are any parameter set values are extracted if not then raise error
                            # pointed out the supported type of argument values
                            if not bool(test_case_parameters_values):
                                raise RuntimeError(
                                    f"Error detected in parameterized test {test_name} due to unsupported type of "
                                    f"parameter arguments values.\n\n"
                                    f"Supported types are: string, tuple, list, dictionary and function generator.")
                            # storing the 'parameterized' into tag
                            test_data.tag.append(ui_helper.PARAMETERIZED_FILTER_NAME)
                            self.tags.append(ui_helper.PARAMETERIZED_FILTER_NAME)
                            if ui_helper.PARAMETERIZED_FILTER_NAME not in self.tag_filter_tests:
                                self.tag_filter_tests[
                                    ui_helper.PARAMETERIZED_FILTER_NAME] = list()
                            self.tag_filter_tests[ui_helper.PARAMETERIZED_FILTER_NAME].append(
                                test_data.name)
                            # storing the test case parameters and values into test data
                            test_data.test_case_parameters_values = test_case_parameters_values
                            # storing the test case parameters(non-default and default parameters)
                            test_data.test_case_parameters = total_test_case_parameters
                            # storing the test case parameters and its values which is used for
                            # test runner purpose.
                            self.all_parameterized_tests[test_name] = test_case_parameters_values
                            # getting the test case parameter values from the test object
                            decorator_param_names = test_obj.__PARAM_NAMES__
                            for index, param_set in test_case_parameters_values.items():
                                if decorator_param_names:
                                    try:
                                        param_name = decorator_param_names[index]
                                    except IndexError:
                                        param_name = index
                                    display_test_name = "{0}(index: {1})".format(test_name, param_name)
                                else:
                                    display_test_name = "{0}(index: {1})".format(test_name, str(index))
                                test_data.param_test_names.append(display_test_name)
                        except Exception as exc:  # pylint: disable=broad-except
                            # remove the test case name for invalid one, then it is not allowed
                            # to show on gui
                            test_cases.remove(test_name)
                            # checking for gui mode
                            if self.gui:
                                ui_helper.pop_up_msg(InfoLevelType.ERR,
                                                     "Error while reading parameterized test data "
                                                     ":{}\nTest_Name: {}\nTest_Values: {}".format(
                                                         exc, test_obj.__FUNC_NAME__,
                                                         test_obj.__PARAM_VALUES__))
                            # non-gui mode
                            else:
                                self.log(
                                    "Error while reading parameterized test data: {}\nTest_Name: {}"
                                    "\nTest_Values: {}".format(exc, test_obj.__FUNC_NAME__, test_obj.__PARAM_VALUES__),
                                    InfoLevelType.ERR)
                    # fetch the parameterized test case object from cell contents
                    # test object contains parameterized test case information of 'TESTTAG',
                    # 'VERIFIES', 'DETAILS', 'PRECONDITION', etc...
                    test_obj = test_scripts_objects[test_name].__closure__[0].cell_contents
                getsource_test_name = inspect.getsourcelines(test_obj)
                if test_data:
                    # getting source lines with TESTTAG into a list
                    tags = self.__getting_py_test_metadata(getsource_test_name, "TESTTAG")
                    # checking for each test case valid tags are provided otherwise provide the warning message that
                    # please change the tags as per log message
                    valid_tags = list()
                    invalid_tags = list()
                    if tags:
                        # allowed tag names only alphanumeric
                        regex = re.compile(r'^[a-zA-Z0-9_]*$')
                        for tag in tags:
                            tag_status = regex.match(tag)
                            if bool(tag_status):
                                valid_tags.append(tag)
                            else:
                                invalid_tags.append(tag)
                    if invalid_tags:
                        LOG.warning(
                            "Invalid tags {} detected for test case '{}'. Only short alphanumeric characters including "
                            "underscores without any spaces are allowed to be used in 'TESTTAG' function.".format(
                                invalid_tags, test_name))
                    test_data.tag.extend(valid_tags)
                    self.tags.extend(valid_tags)
                    # "tag_filter_tests" is used to store the tests based on tag
                    # (user given tags in the pytest)
                    for tag in valid_tags:
                        if tag not in self.tag_filter_tests:
                            self.tag_filter_tests[tag] = list()
                        self.tag_filter_tests[tag].append(test_data.name)
                    # getting source lines with VERIFIES into a list
                    verifies = self.__getting_py_test_metadata(getsource_test_name, "VERIFIES")
                    test_data.verifies_id.extend(verifies)
                    # getting source lines with AUTOMATES into a list
                    automates = self.__getting_py_test_metadata(getsource_test_name, "AUTOMATES")
                    test_data.automates_id.extend(automates)
                    # commenting out below lines to detect asserts or expects modules usage and warning user
                    # this action is time-consuming while loading a configuration containing a large amount of tests
                    # if required it can be un-commented later
                    #
                    # # checking any ptf_assert or ptf_expect present in the test
                    # test_data.status_of_test_verify = self.__check_for_test_verify_test_step(getsource_test_name)
                    # if not test_data.status_of_test_verify:
                    #     LOG.warning("Test: missing with ptf_assert/ptf_expect/assert "
                    #                 ": %s. Please check 'assert' performed in external (imported) "
                    #                 "python module.",
                    #                 test_name)
        self.py_test_dict[str(python_test_script)] = test_cases

    @staticmethod
    def assign_skip_flag_to_test_case(test_case_class, test_case_obj):
        """
        Method to assign skip condition and skip reason to test case data class respective attributes

        :param TestData test_case_class: particular test case function data class
        :param object test_case_obj: particular test case function object
        """
        if hasattr(test_case_obj, "__SKIP_CONDITION__"):
            test_case_class.skip_condition = test_case_obj.__SKIP_CONDITION__
        if hasattr(test_case_obj, "__SKIP_REASON__"):
            test_case_class.skip_reason = test_case_obj.__SKIP_REASON__

    def assign_custom_setup_teardown_to_test_case(self, test_case_data_class, test_case_data_obj):
        """
        Method for checking if the test case used 'setup' decorator and assigning the custom setup-teardown to
        particular test case info class to be used in test runner, if the custom setup-teardown functions are not found
        in loaded setup.pytest file saved data then error strings will be returned

        :param TestData test_case_data_class: particular test case function data class
        :param object test_case_data_obj: particular test case function object

        :returns: error string if the custom setup-teardown functions are not found
        :rtype: str
        """
        error_setup, error_teardown = "", ""
        if hasattr(test_case_data_obj, "__TEST_CASE_SETUP_FUNC__"):
            custom_setup_func_name = test_case_data_obj.__TEST_CASE_SETUP_FUNC__
            if custom_setup_func_name not in self.setup_file_data:
                error_setup = "\n\nError in loading '{}'\nThe custom setup function '{}' given via '@custom_setup' " \
                              "decorator in '{}' was not found in loaded 'setup' file '{}'\nHint: Please make sure " \
                              "the custom setup function exists in loaded 'setup' file.".\
                    format(test_case_data_class.name, custom_setup_func_name, test_case_data_class.name,
                           self.setup_file_data["setup_file_path"])
            else:
                if self.gui:
                    self.gui.custom_decorator_used = True
                test_case_data_class.custom_setup = self.setup_file_data[custom_setup_func_name]
        if hasattr(test_case_data_obj, "__TEST_CASE_TEARDOWN_FUNC__"):
            custom_teardown_func_name = test_case_data_obj.__TEST_CASE_TEARDOWN_FUNC__
            if custom_teardown_func_name not in self.setup_file_data:
                error_teardown = "\n\nError in loading '{}'\nThe custom teardown function '{}' given via " \
                                 "'@custom_setup' decorator in '{}' was not found in loaded 'setup' file '{}'\n" \
                                 "Hint: Please make sure the custom teardown function exists in loaded 'setup' file.".\
                    format(test_case_data_class.name, custom_teardown_func_name, test_case_data_class.name,
                           self.setup_file_data["setup_file_path"])
            else:
                if self.gui:
                    self.gui.custom_decorator_used = True
                test_case_data_class.custom_teardown = self.setup_file_data[custom_teardown_func_name]
        test_case_data_class.setup_script_path = self.setup_file_data["setup_file_path"]
        return error_setup + error_teardown

    def getting_parameterized_test_data(self, test_obj):
        """
        Method to get the test case parameters and its values within parameterized test cases.

        Steps as follows:
        1. Validating the dictionary type keys are matching with test case parameters and
           returns the valid parameters or invalid error message
        2. Validating the list or tuple type values are equal or less than or greater than
           no of test case parameters( non-default and default parameters) and
           returns the valid parameters or invalid error message
        3. Validating the string type values and check test case parameter must be only one and
           returns the valid parameters or invalid error message

        :param object test_obj: test object of the test case information

        :returns: tuple as (
            {
                <arg_value_index>: (<validator>, {"<arg>": <arg_value>, ...}, <exe_bool_flag>),
                ...
            },
            [<all_arg_names>]
        )
        :rtype: tuple
        """
        # storing the valid and invalid data as dictionary with param set index as key and
        # values tuple
        # Dictionary of tuple {key: (bool, dictionary, bool)}
        # tuple first parameter as bool True or False, Valid/Invalid
        # tuple second parameter as dictionary contains parameters and values
        # tuple third parameter as bool True or False. which is used in execution of param set
        # in test runner
        given_tc_param_vals = dict()
        # getting test case object args information with function object
        test_case_args = inspect.signature(test_obj.__FUNC_OBJ__)
        # getting the test case parameters
        valid_tc_param_names = [p.name for p in test_case_args.parameters.values()]

        # store the default parameter and its value into dictionary
        tc_default_parameters = {param: value.default for param, value in
                                 test_case_args.parameters.items()
                                 if value.default is not inspect.Parameter.empty}
        # store the non-default parameter names
        tc_non_default_parameters = [param for param, value in
                                     test_case_args.parameters.items()
                                     if value.default is inspect.Parameter.empty]

        # getting the test case parameter values from the test object
        decorator_param_vals = test_obj.__PARAM_VALUES__

        # check if tc_parameters_values is not empty and then check its type is dict or list
        # or tuple or str
        # if tc_parameters_values is empty check in else any default values are available
        # for the parameterized test case
        # To display in GUI/CLI the format of storing as dictionary of tuples
        # (True, {Valid parameters}, True) or (False, {Invalid parameters}, True)
        # param values set index which is used as key for each set.
        param_values_set_indx = 0
        if decorator_param_vals:
            for param_values_set in decorator_param_vals:
                # if item is dict type then directly use the parameter values
                if isinstance(param_values_set, dict):
                    # validate the param_values with test case non-default and default parameters.
                    # validate the param keys are matching with test case non-default and
                    # default parameters .
                    # return the valid or invalid data as tuple - (True, {Valid parameters}) or
                    # (False, {Invalid parameters})
                    given_tc_param_vals[param_values_set_indx] = \
                        self.validate_parameters_for_dict_types(
                            param_values_set, tc_non_default_parameters, tc_default_parameters)
                # if param_values is list or tuple type convert list to dict as key and value
                elif isinstance(param_values_set, list) or isinstance(param_values_set, tuple):
                    # validate the param_values with test case non-default and default parameters
                    # and return the valid or invalid data as tuple -
                    # (True, {Valid parameters},True) or (False, {Invalid parameters}, True)
                    given_tc_param_vals[param_values_set_indx] = \
                        self.validate_parameters_for_list_tuple_types(
                            param_values_set, tc_non_default_parameters, tc_default_parameters)
                # if param_values is str type convert str to dict as key and value
                elif isinstance(param_values_set, str):
                    param_value = dict()
                    # Here converting to dictionary with parameter(key) and value
                    # for string type. The test case parameter must be only one
                    if len(valid_tc_param_names) == 1:
                        param_value[valid_tc_param_names[0]] = param_values_set
                        # check for default parameters and its value, if required
                        # add to the dictionary
                        given_tc_param_vals[param_values_set_indx] = (True, param_value, True)
                        # check non-default parameters >1 invalid case
                    else:
                        given_tc_param_vals[param_values_set_indx] = (False, param_values_set, True)
                param_values_set_indx += 1
        # tc_parameters_values is empty, so check any default values are available
        else:
            # default parameters
            if len(tc_default_parameters.keys()) == 1:
                given_tc_param_vals[param_values_set_indx] = (True, tc_default_parameters, True)
            # non-default parameters
            else:
                given_tc_param_vals[param_values_set_indx] = (False, decorator_param_vals, True)
        return given_tc_param_vals, valid_tc_param_names

    def validate_parameters_for_list_tuple_types(self, param_value_set, tc_non_default_parameters,
                                                 tc_default_parameters):
        """
        Method to validate test case parameters for dictionary type for below scenarios:
        - total number of param_values  must be equal to total test case parameters - valid
        - total number of param_values  must be equal to  total non default parameters -
                                        valid
        - total number of param_values  less than total non default parameters- invalid
        - total number of param_values  greater than total non default test case parameters and
          check it with total default parameters and decide valid or not
        - total number of param_values are zero :
           - default parameters valid case
           - non-default parameters invalid case

        :param tuple or list param_value_set: contains values in the format of tuple or list
        :param list tc_non_default_parameters: contains non default parameters
        :param dict tc_default_parameters: contains default parameters and vlaues
        returns valid or invalid test case parameters as
                (True, {Valid parameters})  or (False, {Invalid parameters})
        :rtype: tuple

        # These example's apply's for list and tuple parameterized test cases
        Example1: list type
        @parameterized([[],- Invalid
                        ["bar", "abc"],- Invalid
                        ["abc", "foo", "ravi", 1],-valid
                        ["abc", "foo", "ravi"],- valid
                        ["abc", "foo", "ravi", 3, 2, False] - valid
                        ])
        def SWT_DEMO_TEST_PARAMETERIZED_list_params(text1, text2, number1, number2=5, value=5,
                                            list_flag=True):
        Example2: list type
        @parameterized([[],- Invalid ])
        def SWT_DEMO_TEST_PARAMETERIZED_list_params_default_case(number=5, value=5,
                                            list_flag=True):
         Example1: tuple type
        @parameterized([(),- Invalid
                        ("bar", "abc"),- Invalid
                        ("abc", "foo", "woo"), 1,-valid
                        ("abc", "foo", "woo"),- valid
                        ("abc", "foo", "woo", 3, 2, False) - valid
                        ])
        def SWT_DEMO_TEST_PARAMETERIZED_list_params(text1, text2, number1, number2=5, value=5,
                                            tuple_flag=True):
        Example2: list type
        @parameterized([(),- Invalid ])
        def SWT_DEMO_TEST_PARAMETERIZED_tuple_params_default_case(number=5, value=5,
                                            tuple_flag=True):

        """
        # total number of parameter values in tuple or list type
        total_no_values_count = len(param_value_set)
        # total number of non default parameters
        total_tc_non_default_param_count = len(tc_non_default_parameters)
        # total number of default parameters
        total_tc_default_param_count = len(tc_default_parameters.keys())
        # total no of non-default and default parameters
        total_tc_param_count = total_tc_non_default_param_count + total_tc_default_param_count
        # total no of parameters in a list
        all_tc_param_names_list = tc_non_default_parameters + list(tc_default_parameters.keys())

        validated_param_value = tuple()
        # total no of values and total test case parameters are not empty
        if total_no_values_count > 0 and total_tc_param_count > 0:
            # local variable to store the mapping data
            param_value = dict()
            # total no of values are equal to total no of test case parameters(default and
            # non-default parameters) is valid case
            if total_no_values_count == total_tc_param_count:
                for index in range(total_no_values_count):
                    param_value[all_tc_param_names_list[index]] = param_value_set[index]
                validated_param_value = (True, param_value, True)
            # values are equal to total no of test case non-default parameters is valid case
            elif total_no_values_count == total_tc_non_default_param_count:
                for index in range(total_no_values_count):
                    param_value[tc_non_default_parameters[index]] = param_value_set[index]
                validated_param_value = (True, self.__check_default_parameters_and_store_data(
                    param_value, tc_default_parameters), True)
            # values are greater than total no of test case non-default parameters is valid case
            elif total_no_values_count > total_tc_non_default_param_count:
                for index in range(total_no_values_count):
                    param_value[all_tc_param_names_list[index]] = param_value_set[index]
                validated_param_value = (True, self.__check_default_parameters_and_store_data(
                    param_value, tc_default_parameters), True)
            # values are less than total no of test case non-default parameters is invalid case
            elif total_no_values_count < total_tc_non_default_param_count:
                validated_param_value = (False, param_value_set, True)
            return validated_param_value
        # total no of values are zero and check for non-default and default parameters
        else:
            # check total no of test case non-default parameters is invalid case
            if tc_default_parameters and not tc_non_default_parameters:
                validated_param_value = (True, tc_default_parameters, True)
            # check total no of test case default parameters is valid case,
            else:
                validated_param_value = (False, param_value_set, True)
            return validated_param_value

    def validate_parameters_for_dict_types(self, param_values_set, tc_non_default_parameters,
                                           tc_default_parameters):
        """
        Method to validate test case parameters for dictionary type for below scenarios:
        - total number of param_values  must be equal to total test case parameters and
          validate param_values  keys are matching with non-default and default parameters.
        - total number of param_values  less than total test case parameters(non-default and
          default parameters) and validate param_values  keys are matching with non-default and
          default parameters.
         - total number of param_values greater than total test case parameters and
           validate param_values  keys are matching with non-default and
           default parameters.
        - total number of param_values are empty:
           - default parameters - valid case
           - non default parameters - invalid case

        :param dict param_values_set: contains parameter and its values
        :param list tc_non_default_parameters: contains non default parameters
        :param dict tc_default_parameters: contains default parameter and its value
        :return: returns valid or invalid test case parameters as
                (True, {Valid parameters})  or (False, {Invalid parameters})
        :rtype: tuple

        # These example's apply's for dictionary type parameterized test cases
        Example 1: Incorrect keys - Invalid
        @parameterized([ {"text": "foo", "numb": 1}, {"number": 2, "text": "bar"}])
        def SWT_DEMO_TEST_PARAMETERIZED_dict_params_incorrect_keys(text, number):

        Example 2: correct keys - valid
        @parameterized([ {"text": "foo", "number": 1}, {"number": 2, "text": "bar"}])
        def SWT_DEMO_TEST_PARAMETERIZED_dict_params_correct_keys(text, number):

        Example 3: correct_keys and default parameters - valid
        @parameterized([{"text": "foo", "number": 1},{"number": 2, "text": "bar"} ])
        def SWT_DEMO_TEST_PARAMETERIZED_dict_params_corret_keys_with_default_parameters(text, number
                                                                                   , dic_flag=True):
        Example 4: correct_key and less than non-default parameters - invalid
        @parameterized([{"text": "foo"}])
        def SWT_DEMO_TEST_PARAMETERIZED_dict_params_values_less_than_non_default_parameters(text,
                                                                            number, dic_flag=True):
        Example 5: scenarios to cover
                   {} - invalid
                   {"text": "foo"} - valid
                   {"text": "foo", "number": 1} - valid
                   {"text": "foo", "number": 1, "value": 10, "dic_flag": False} - invalid
        @parameterized([{},{"text": "foo"}, {"text": "foo", "number": 1},
        {"text": "foo", "number": 1, "value": 10, "dic_flag": False}])
        def SWT_DEMO_TEST_PARAMETERIZED_dict_params_values_less_than_non_default_parameters1(text,
                                                                          number=10, dic_flag=True):
        Example 6: only default values - valid
        @parameterized([{}])
        def SWT_DEMO_TEST_PARAMETERIZED_dict_params_only_default_values(text='hello', number=10,
                                                                                   dic_flag=True):

        """
        # total number of parameter values in each dictionary
        total_no_of_values_count = len(param_values_set.keys())
        # total number of non default parameters
        total_tc_non_default_param_count = len(tc_non_default_parameters)
        # total number of default parameters
        total_tc_default_param_count = len(tc_default_parameters.keys())
        # total number of parameters
        total_tc_parameters_count = \
            total_tc_non_default_param_count + total_tc_default_param_count
        all_tc_param_names_list = tc_non_default_parameters + list(tc_default_parameters.keys())
        # check total no of values and total test case parameters are not empty.
        # else check for non-default or default parameters.
        if total_no_of_values_count > 0 and total_tc_parameters_count > 0:
            # valid case
            # total number of values must be equal to non default and default
            # parameters. Then check the param_values keys are matching with test case parameters.
            if total_no_of_values_count == total_tc_parameters_count:
                return self.__check_keys_matching(
                    self.__check_default_parameters_and_store_data(
                        param_values_set, tc_default_parameters), all_tc_param_names_list)
            # valid case
            # total number of values must be equal to non default and default
            # parameters. Then check the param_values keys are matching with test case parameters.
            elif total_no_of_values_count == total_tc_non_default_param_count:
                return self.__check_keys_matching(
                    self.__check_default_parameters_and_store_data(
                        param_values_set, tc_default_parameters), all_tc_param_names_list)
            # Invalid case
            # total number of values less than  non-default parameters.
            elif total_no_of_values_count < total_tc_non_default_param_count:
                validated_param_value = (False, param_values_set, True)
                return validated_param_value
            # Invalid case
            # total number of values greater than  non-default parameters
            elif total_no_of_values_count > total_tc_parameters_count:
                return self.__check_keys_matching(param_values_set, all_tc_param_names_list)
        else:
            # invalid case
            # check any non-default parameters and map value with None
            if tc_default_parameters and not tc_non_default_parameters:
                validated_param_value = (True, tc_default_parameters, True)
            # seems like valid case and store the default data.
            else:
                validated_param_value = (False, param_values_set, True)
            return validated_param_value

    @staticmethod
    def __check_default_parameters_and_store_data(param_value, default_parameter_value):
        """
        Method to check for the default parameters of the test case and update the dictionary with
        default parameter and value

        :param param_value: contains test case parameter and value stored in a dictionary format
        without default data
        :param default_parameter_value: contains test case default parameter and value stored in a
                                        dictionary format
        :return: dictionary with parameters as key  and parameter values as value
                 of the test case
        :rtype: dict
        """
        # check if default_parameter_value empty or not
        if default_parameter_value:
            # check if any default parameters are available in param_value dictionary and
            # update the param_value dictionary with the default parameter and its value
            for param, value in default_parameter_value.items():
                if param not in param_value.keys():
                    param_value[param] = value

        return param_value

    @staticmethod
    def __check_keys_matching(param_values_set, total_test_case_parameters):
        """
        Method to check the parameter values of dictionary type keys are matching with test case
        non-default and default parameters

        :param dict param_values_set: param_values_set is dict type contains parameters and
                                      its values
        :param list total_test_case_parameters: total_test_case_parameters contains default and
                                                non default parameters

        :return: returns valid or invalid test case parameters as (True, {Valid parameters})  or
                 (False, {Invalid parameters})
        :rtype: tuple
        """
        # For dictionary type check keys in parameterized data are matching with
        # test case parameters of the test function and store the correct and incorrect test case
        # parameters and its values. this will be show on GUI for user to correct the test case
        # check the 'param_values' dictionary keys are matching with test_case_parameters
        # check param_values are less than total test case parameters

        incorrect_keys = [param for param in param_values_set.keys()
                          if param not in total_test_case_parameters]

        # correct test case parameters are stored as tuple
        # tuple(True, param_values)
        if not incorrect_keys:
            validated_param_value = (True, param_values_set, True)
        else:
            validated_param_value = (False, param_values_set, True)

        return validated_param_value

    def set_setup_files(self, setup_files_list):
        """
        Method for set setup files as tuples, key (setup file path) and value as module setup file name

        :param list setup_files_list: Paths for setup scripts
        """
        self.data["setup_files"].clear()
        for setup_file in setup_files_list:
            module_name = os.path.basename(setup_file)
            self.data["setup_files"].append((setup_file, module_name))

    def get_setup_teardown_functions(self, setup_file):
        """
        Method for returning setup and teardown functions in given a setup file (setup.pytest)

        :param string setup_file: Path for setup script

        :return: Returns dictionary containing key as setup or teardown funcs and value as objects
        :rtype: dictionary
        """
        standard_setup_funcs = dict()
        self.setup_file_data.clear()
        try:
            module_spec = importlib.util.spec_from_file_location("setup.pytest", setup_file)
            loaded_module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(loaded_module)
            setup_functions = inspect.getmembers(loaded_module, inspect.isfunction)
            self.setup_file_data["setup_file_path"] = setup_file
            for test_name, test_object in setup_functions:
                if test_name in helper.SETUP_TEARDOWN_METHOD_NAMES:
                    self.setup_file_data[test_name] = test_object
                    standard_setup_funcs[test_name] = test_object
                else:
                    self.setup_file_data[test_name] = test_object
        except SyntaxError as exc:
            self.log("Syntax error in {}, Line {}, Char {}. Aborting.\n\tLine: '{}'"
                     .format(exc.filename, exc.lineno, exc.offset, exc.text), InfoLevelType.ERR)
        except Exception as exc:  # pylint: disable=broad-except
            self.log("Error while loading file setup.pytest: '{}'.\n{}\nTraceback:\n{}.".format(
                exc, "-" * 40, traceback.format_exc()), InfoLevelType.ERR)
        # throw back the objects of grabbed setup teardown functions
        return standard_setup_funcs

    @staticmethod
    def get_filtered_files(location, file_filter):
        """
        Method for applying a specific filter on files in a given directory (including
        sub-directories)

        Moreover the given location as well as all sub-directories inside it will be added to system
        path if not already added

        :param string location: Location in which specific files need to be searched
        :param string file_filter: Filter which need to be applied on each file e.g. "*.pytest",
            "*.cmm" means filter all files with extension .pytest , *.cmm

        :return: Returns list containing all files in given directory after applying extension and
            start file name filter
        :rtype: list
        """
        filtered_scripts_list = list()
        # loop for accessing all sub-folders in given location in alphabetic order
        for root_dir, _, _ in helper.alphabetic_dir_walk(location):
            # grab all files with given start filter and extension
            # sorted call is important to make sure filtered files are in alphabetic order
            filtered_files = sorted(glob.glob(os.path.join(root_dir, file_filter)))
            if filtered_files:
                filtered_scripts_list.append(filtered_files)
            # adding directory in system path if not already present also ignoring compilation
            # folder
            if (root_dir not in sys.path) and ('__pycache__' not in root_dir):
                sys.path.append(root_dir)
        # throw back list of filtered files after creating a list with list of lists
        return list(itertools.chain.from_iterable(filtered_scripts_list))

    def get_py_func_obj_in_script(self, python_script_path):
        """
        Method for capturing python functions objects in a python script

        Moreover the script is executed once to check if there are any execution errors (e.g.
        syntax errors etc.)

        NOTE: Since test cases are written in .pytest custom extension therefore it's necessary to
        add this custom extension in suffix list of source files
            --> importlib.machinery.SOURCE_SUFFIXES.append('.pytest')
        This step is done in class constructor

        :param string python_script_path: Python script path whose functions objects are required

        :return: OrderedDict containing key as function names and there values will be their objects
        :rtype: OrderedDict
        """
        # create a dictionary in which test case info ({'test_name': test_case_object}) will be
        # saved
        script_location, _ = os.path.split(python_script_path)
        # loading test scripts
        # loading each test-case file into a separate module, this avoids that variables
        # defined in file 'a' overwrite variables defined in file 'b'
        try:
            module_name = os.path.relpath(python_script_path, script_location).replace(
                os.path.sep, '.')
            module_spec = importlib.util.spec_from_file_location(
                module_name, python_script_path)
            loaded_module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(loaded_module)
        except SyntaxError as exc:
            self.log("Syntax error in {}, Line {}, Char {}. Aborting.\n\tLine: '{}'"
                     .format(exc.filename, exc.lineno, exc.offset, exc.text), InfoLevelType.ERR)
        except Exception as exc:  # pylint: disable=broad-except
            # checking for gui mode
            if self.gui:
                response = ui_helper.pop_up_msg(
                    InfoLevelType.QUEST,
                    "Error while loading file {}\n{}\n--> Error:\n'{}'\n{}\n--> Traceback:\n{}\n{}\n\n"
                    "-->HINT (in-case a python module is missing):\n\n"
                    "Do you want to continue and edit the configuration by adding missing module paths in "
                    "'Additional Paths' section? \n\nNOTE: If path(s) are not added then the test cases in the above "
                    "test script will not be loaded.".format(
                        python_script_path, "-" * 40, exc, "-" * 40, traceback.format_exc(), "-" * 40))
                # if user say 'Yes' then edit config window pop-up, the error .pytest file
                # test cases are not shown on GUI
                if response:
                    self.gui.edit_config_flag = True
            # non-gui mode
            else:
                self.log(
                    "Error while loading file {}\n{}\n--> Error:\n'{}'\n{}\n--> Traceback:\n{}\n{}\n\n".format(
                        python_script_path, "-" * 40, exc, "-" * 40, traceback.format_exc(), "-" * 40),
                    InfoLevelType.ERR)
        file_content = self.read_file(python_script_path)
        # finding all python test functions in read pytest file (python file)
        for content in file_content:
            # function will always start with 'def SWT_' i.e. only test cases
            if content.startswith(helper.TEST_DEF_NAME_FORMATS):
                # append to relevant list after right stripping not useful content from left and
                # right of string
                self.data["all_py_test_cases_for_duplicates_check"].append(
                    content.lstrip("def ").split("(")[0])

        def get_func_line_num(func):
            line_num = 0
            for index, line in enumerate(file_content):
                if "def " + func[0] + "(" in line:
                    line_num = index + 1
                    break
            return line_num

        # getting function from the loaded module
        dict_of_functions = dict(inspect.getmembers(loaded_module,
                                                    inspect.isfunction))
        test_info = OrderedDict(
            (val[0], val[1]) for val in (
                sorted(dict_of_functions.items(), key=get_func_line_num)))

        return test_info

    def read_file(self, file_to_read):
        """
        Function for reading a file

        :param string file_to_read: File to read

        :return: The read file in form of list
        :rtype: list
        """
        test_file = open(file_to_read)
        try:
            read_file = test_file.readlines()
        except UnicodeError as exc:
            err = \
                "Decoding error while loading file {}.Check for invalid character {} at " \
                "pos {}. Skipping.".format(
                    # pylint: disable=no-member
                    file_to_read, hex(exc.object[exc.start]), exc.start)
            self.log(err, InfoLevelType.ERR)
            read_file = ""
        finally:
            test_file.close()
        return read_file

    def get_base_path(self):
        """
        Method for returning back the base path
        """
        return self.tests_path[helper.BASE_PATH]

    def get_ptf_path(self):
        """
        Method for returning back the ptf path
        """
        return self.tests_path[helper.PTF_TEST]

    def get_cmm_path(self):
        """
        Method for returning back the cmm path
        """
        return self.tests_path[helper.T32_TEST]

    def get_canoe_cfg_path(self):
        """
        Method for returning back the capl path
        """
        return self.tests_path[helper.CANOE_CFG]

    def get_pytest_dict(self):
        """
        Method for returning back the pytest dictionary which is store with keys as test script
        and value as test cases
        """
        return self.py_test_dict

    def get_test_case_tags(self):
        """
        Method for returning back the test_case_tag  dictionary which is store with
        key as test case amd value as tag(list)
        """
        return self.test_case_tag

    def get_appearing_overall_tests_list(self):
        """
        Method for returning back the captured total appearing test case list
        """
        return self.appearing_overall_tests

    def get_filtered_tests_list_based_on_tag(self, tag_filter):
        """
        Method for returning back the filtered tests list based on filter tag
        :param string tag_filter: tag filter comes from GUI Combobox filter
        :return: returns store list of the tests in a dictionary based on filter tag
        :rtype: list
        """
        if tag_filter.split("(")[0].strip() in self.tag_filter_tests:
            return self.tag_filter_tests[tag_filter.split("(")[0].strip()]

    def get_directory_structure(self, test_path_dir, test_filter_type):
        """
        Creates a nested dictionary recursively that represents the folder structure of
        test_path_dir with filtering

        :param string test_path_dir: test path dir of pytest, cmm, can paths
        :param string test_filter_type: files type(*.pytest, *.cmm)

        :return: returns store dictionary of the folder, sub folder structure with file and
        test case information
        :rtype: dict
        """
        # store the final test dictionary
        final_test_type_dict = OrderedDict()
        test_path_dir = test_path_dir.rstrip(os.sep)
        start = test_path_dir.rfind(os.sep) + 1
        # go through the alphabetic walk in 'test_path_dir'
        for path, _, files in helper.alphabetic_dir_walk(test_path_dir):
            # list used for filter the files store in it
            file_matches = list()
            # dictionary is used to store the pytest dictionary
            test_script_cases = OrderedDict()
            folders = path[start:].split(os.sep)
            # based on files and test_filter_type filtering the files
            # sorted call is important to make sure filtered files are in alphabetic order
            for file in sorted(fnmatch.filter(files, test_filter_type)):
                if test_filter_type == "swt_*.pytest":
                    test_script_cases[file] = self.get_pytest_dict()[os.path.join(path, file)]
                elif test_filter_type == "SWT_*.cmm":
                    file_matches.append(os.path.basename(os.path.join(path, file)))

            # with test_filter_type *.pytest files test cases are separated in above
            # for loop and store in test_script_cases in dictionary as key(file path)
            # and value (as dict())
            if test_filter_type in ["swt_*.pytest"]:
                # sub directory as dictionary with key and value
                subdir = test_script_cases
            else:
                subdir = OrderedDict.fromkeys(file_matches)
            # this create a dictionary of nested dictionary into final_test_type_dict
            parent = functools.reduce(OrderedDict.get, folders[:-1], final_test_type_dict)
            parent[folders[-1]] = subdir
        # final_test_type_dict pass to below method to remove if any empty dictionary exits and
        # returns proper dictionary to the tree view display
        return self.remove_empty_dictionary(final_test_type_dict)

    def remove_empty_dictionary(self, test_type_dict):
        """
        The purpose to remove the nested dictionary recursively, if  any dictionary has empty
        data like as  key: "{}" to be removed that is not needed to display in the tree view.
        example as  pycache_  for *.pytest files
        :param dict test_type_dict : takes final test type dictionary as parameter
        :return: returns removed empty nested dictionary
        :rtype: dict
        """
        new_test_type_dict = OrderedDict()
        # goes through the nested dictionary and removes empty values of the dictionary
        # and prepares new dictionary
        # key as folder, sub folder directory and  value as  test_file, test_cases
        for folder_subfolder, test_file_cases in test_type_dict.items():
            if isinstance(test_file_cases, OrderedDict):
                test_file_cases = self.remove_empty_dictionary(test_file_cases)
            # if folder/subfolder doesn't contains any files remove it
            if test_file_cases not in ('', {}):
                new_test_type_dict[folder_subfolder] = test_file_cases
        return new_test_type_dict

    def clear_test_cases(self):
        """
        Method is to clear all tests that includes py_tests, cmm, capl
        """
        # selected tests are cleared from test runner
        self.test_runner_data["py_tests"].clear()
        self.test_runner_data["cmm_tests"].clear()
        self.test_runner_data["capl_tests"].clear()

    def update_and_get_parameterized_tests_for_test_runner(self, param_tests_window_obj=None):
        """
        Method for preparing a dictionary to be passed to test runner.
        It will prepare the parameterized tests sets data (validity, values, user modifications etc.) in a convienient
        way for better understanding in test runner

        :param TestCaseParametersView param_tests_window_obj: Class object of param test window

        :return: dictionary containing keys as param test name and values as their data respectively
            {"<test_name_1>": {<set_num>: {"valid": <True/False>, "vals": <set_values>, "run": <True/False>,
                               "name": "<test_name_with_param>", "user_added": <True/False>},
             "<test_name_2>": {<set_num>: {"valid": <True/False>, "vals": <set_values>, "run": <True/False>,
                               "name": "<test_name_with_param>", "user_added": <True/False>},
              ...
            }
        :returns: dictionary
        """
        # keep a copy for the all the parameterized tests and update on that copy which is used for test runner
        update_tc_parameters_values = dict(self.all_parameterized_tests)
        # preparing list of all tests which are selected to be run (selected via gui or saved in ini)
        all_selected_tests_to_run = [test_data.name for test_data in self.test_runner_data['py_tests']]
        # dictionary to store of param tests which are selected to run only not all tests
        selected_param_tests_to_run = dict()
        # adding data of only those param tests which are selected to run
        for test in all_selected_tests_to_run:
            if test in update_tc_parameters_values.keys():
                selected_param_tests_to_run[test] = update_tc_parameters_values[test]
        # checking the test_case_parameter_obj is not None i.e. user did not open param view window
        if param_tests_window_obj is not None:
            # get the selected param sets for the test cases which user are modified/selected/newly added
            selected_param_sets_from_gui = param_tests_window_obj.get_selected_param_sets_for_test_runner()
            for tc_name, param_set_data in selected_param_tests_to_run.items():
                # check the test case is selected or not (case for getting values from param window)
                if tc_name in selected_param_sets_from_gui:
                    # update the param set data for copy of selected_param_tests_to_run
                    gui_param_set_data = selected_param_sets_from_gui[tc_name]
                    to_be_updated = dict()
                    for test_set_index, param_key_value in gui_param_set_data.items():
                        if test_set_index in param_set_data.keys():
                            # get the tuple which contains as # (True, {Valid parameters},True) or
                            # (False, {Invalid parameters}, True)
                            param_tuple_set_data = param_set_data[test_set_index]
                            # param_tuple_set_data[1] gives the valid parameters information contains param set key
                            # and value, this condition is true when the user did not modify any input argument value
                            # in parameterized test set number i.e. `test_set_index`

                            if param_key_value == param_tuple_set_data[1]:
                                to_be_updated[test_set_index] = (
                                    {"valid": param_set_data[test_set_index][0],
                                     "vals": gui_param_set_data[test_set_index],
                                     "run": param_set_data[test_set_index][2], "user_added": False,
                                     "name": self.data["py_test_data_dict"][tc_name].param_test_names[test_set_index]})
                            else:
                                to_be_updated[test_set_index] = (
                                    {"valid": True, "vals": gui_param_set_data[test_set_index], "run": True,
                                     "user_added": True, "name":
                                         "{0}(index: {1})__USER_MODIFIED_INVALID".format(tc_name, str(test_set_index))})
                        else:
                            to_be_updated[test_set_index] = (
                                {"valid": True, "vals": gui_param_set_data[test_set_index], "run": True,
                                 "user_added": True, "name":
                                     "{0}(index: {1})__USER_ADDED_INVALID".format(tc_name, str(test_set_index))})
                    selected_param_tests_to_run.update({tc_name: to_be_updated})
                # condition to get values in-case user did not open param view window of particular param test
                else:
                    to_be_updated = dict()
                    for index in param_set_data.keys():
                        to_be_updated[index] = {"valid": param_set_data[index][0], "vals": param_set_data[index][1],
                                                "run": param_set_data[index][2], "user_added": False,
                                                "name": self.data["py_test_data_dict"][tc_name].param_test_names[index]}
                    selected_param_tests_to_run.update({tc_name: to_be_updated})
            return selected_param_tests_to_run
        # condition for auto mode and auto_gui mode when user has no chance of opening param view window
        else:
            ret_dictionary = dict()
            for param_test_name, param_test_info in selected_param_tests_to_run.items():
                ret_dictionary[param_test_name] = dict()
                for index, param_test_properties in param_test_info.items():
                    ret_dictionary[param_test_name][index] = {
                        "valid": param_test_properties[0], "vals": param_test_properties[1],
                        "run": param_test_properties[2], "user_added": False,
                        "name": self.data["py_test_data_dict"][param_test_name].param_test_names[index]}
            return ret_dictionary

    def prepare_test_data_from_cfg(self, configuration=None, filter_values=None, load_canoe=True, setup_file=None):
        """
        This method allows PTF model to set the configuration and set all the paths and
        directories accordingly. It is triggered by the main ui controller when a configurator
        object loads a configuration file successfully.

        :param ProjectConfigHandler configuration: configuration handler loaded by
                                                   main ui controller
        :param list filter_values: List containg filter values if given via CLI. This helps in
            auto mode to skip CMM and CANoe tests preparation if their tags are not given
        :param bool load_canoe: Flag for preparing canoe cfg data
        :param string setup_file: User given setup file (either via CLI or GUI)
        """
        # reset the client informer variables to default values
        client_informer.REST_CLIENT_INFORMER.reset_variables()
        # setting current config file
        self.current_cfg = configuration
        # preparing the contest config information for rest contest server
        client_informer.REST_CLIENT_INFORMER.loaded_config_path = self.current_cfg.loaded_config
        client_informer.REST_CLIENT_INFORMER.config_info = {
            "base_path": self.current_cfg.base_path, "python_tests": self.current_cfg.ptf_test_path,
            "t32_tests": self.current_cfg.ptf_test_path,
            "canoe_cfg": self.current_cfg.canoe_cfg_path,
            "use_ctf": self.current_cfg.use_cte_checkbox,
            "ctf_location": self.current_cfg.cte_location,
            "ctf_config": self.current_cfg.cte_cfg, "report_path": self.current_cfg.report_path,
            "additional_paths": self.current_cfg.additional_paths,
            "no_of_loops": self.current_cfg.num_loops,
            "selected_tests": self.current_cfg.selected_tests}
        self.data["tests_in_cfg"] = self.current_cfg.selected_tests
        # setting all project paths accordingly
        self.project_paths = self.__get_test_paths(self.current_cfg)
        # prepare python test cases data which need to be prepared anyway
        if self.project_paths[helper.PTF_TEST]:
            self.prepare_python_tests(setup_file)
            # updating setup file in rest client informer
            self.update_client_setup_file(setup_file)
        # prepare cmm test cases data
        if self.project_paths[helper.T32_TEST]:
            # if user gave cmm filter via cli (in auto run mode) only then prepare cmm tests
            # Also if the CLI arg "reverse_selection" is not included in the CLI call
            if filter_values is not None:
                if ui_helper.CMM_FILTER_NAME not in filter_values:
                    LOG.info("Ignoring CMM Tests Preparation as 't32' tag not mentioned.")
                else:
                    # prepare cmm tests data since t32 filter is mentioned
                    self.prepare_cmm_tests()
            else:
                self.prepare_cmm_tests()
        if load_canoe:
            # prepare canoe test cases data
            if self.project_paths[helper.CANOE_CFG]:
                # if user gave canoe filter via cli (in auto run mode) only then prepare canoe tests
                # Also if the CLI arg "reverse_selection" is not included in the CLI call
                if filter_values is not None:
                    if ui_helper.CANOE_FILTER_NAME not in filter_values:
                        LOG.info("Ignoring CANoe Tests Preparation as 'canoe' tag not mentioned.")
                    else:
                        # prepare canoe tests data since canoe filter is mentioned
                        self.prepare_canoe_tests(
                            self.project_paths[helper.CANOE_CFG],
                            self.project_paths[helper.USE_CTE],
                            self.project_paths[helper.CTE_ZIP],
                            self.project_paths[helper.CTE_CFG])
                else:
                    self.prepare_canoe_tests(
                        self.project_paths[helper.CANOE_CFG],
                        self.project_paths[helper.USE_CTE],
                        self.project_paths[helper.CTE_ZIP],
                        self.project_paths[helper.CTE_CFG])
        # "show all" filter tag contains all tests including (pytests, cmm, capl)
        self.tag_filter_tests["show all"] = self.get_appearing_overall_tests_list()
        return self.__detect_tests_duplications()

    def add_or_remove_test_for_runner(self, test_name, to_add, tags):
        """
        Method for adding or removing a test case from test runner data based on user interaction
        on UI

        :param string test_name: Test case name
        :param bool to_add: Flag for adding if True else False
        :param list tags: List containing test case tags
        """

        def add_or_remove_test(test_list, test_name, test_type, add):
            """
            Local function for adding or removing a test case from test runner data

            :param list test_list: Specific test type list (python or cmm)
            :param string test_name: Name of test case to add or remove
            :param string test_type: Specific test type python or cmm
            :param bool add: Flag for adding if True else False
            """
            # this condition for python and cmm tests since their data is saved in dictionary form
            if isinstance(test_list, dict):
                if test_name in test_list.keys():
                    if add:
                        self.test_runner_data[test_type].append(test_list[test_name])
                    else:
                        self.test_runner_data[test_type].remove(test_list[test_name])
            # this condition for canoe tests since their data is saved in list form
            elif isinstance(test_list, list):
                if test_name in test_list:
                    if add:
                        self.test_runner_data[test_type].append(test_name)
                    else:
                        self.test_runner_data[test_type].remove(test_name)
        # handle each test category in a different way with different input arguments
        if ui_helper.PYTHON_FILTER_NAME in tags:
            add_or_remove_test(self.get_python_test_data(), test_name, "py_tests", to_add)
        elif ui_helper.CMM_FILTER_NAME in tags:
            add_or_remove_test(self.get_cmm_test_data(), test_name, "cmm_tests", to_add)
        elif ui_helper.CANOE_FILTER_NAME in tags:
            add_or_remove_test(self.get_capl_files(), test_name, "capl_tests", to_add)

    def filter_and_get_setup_file_data(self, requested_setup_file):
        """
        Method for filtering setup files and get data of requested setup file if exists

        :param string requested_setup_file: setup file

        :return: dictionary containing setup, teardown func names as key and their objects as value
        :rtype: dictionary
        """
        setup_file_index = None
        setup_files_list = self.get_setup_files()
        standard_setup_funcs = dict()
        if not requested_setup_file:
            requested_setup_file = "setup"
        # add extension if not existing
        if not requested_setup_file.endswith(".pytest"):
            requested_setup_file = requested_setup_file + ".pytest"
        # go through all setup files found and grab objects of setup, teardown funcs if file matches
        for setup_file in setup_files_list:
            if setup_file[1] == os.path.split(requested_setup_file)[1]:
                setup_file_index = setup_files_list.index(setup_file)
                break
        # if setup file matched or found
        if setup_file_index is not None:
            setup_pytest = setup_files_list[setup_file_index][0]
            LOG.info("Given setup script found at %s, parsing it... ", setup_pytest)
        # if setup file not matched then look for default setup.pytest file
        else:
            setup_pytest = os.path.join(self.get_ptf_path(), "setup.pytest")
            LOG.info("Given setup script '%s' not found, fallback to default setup.pytest script", requested_setup_file)
        # if setup file after filtering exists then grab their funcs object
        if os.path.exists(setup_pytest):
            standard_setup_funcs = self.get_setup_teardown_functions(setup_pytest)
        else:
            # this statement is added in order to handle situation when no setup.pytest (default) exists
            self.setup_file_data["setup_file_path"] = None
            LOG.info("%s not found, ignoring ... ", setup_pytest)
        # throw back setup data
        return standard_setup_funcs

    def filter_tests_to_run(self, tests_in_cfg=None, filter_tag_values=None, reverse_tests_selection=False):
        """
        Method for filtering tests based on filter tag or tests in cfg file

        :param dictionary tests_in_cfg: Dictionary containing lists of test cases
        :param list filter_tag_values: List containing filter tags
        :param bool reverse_tests_selection: Test selection will be reversed if this is set to True.
            This argument comes from CLI arg ``reverse_selection``. Also filter tags will be
            ignored, if this is set to True.
        """
        # clearing lists for different test types
        self.test_runner_data["py_tests"].clear()
        self.test_runner_data["cmm_tests"].clear()
        self.test_runner_data["capl_tests"].clear()
        # flag in-case at-least one test found
        tests_found = False
        # if filter tag is given and CLI arg "reverse_selection" is not included in CLI call, then
        # grab test data of all tests having that tag
        if filter_tag_values is not None:
            if reverse_tests_selection:
                LOG.info("Reverse test selection is ignored, as the filter tag is provided")
            # filtering python tests with given tags via CLI
            for python_test in self.data["py_test_data"]:
                if any(tag in python_test.tag for tag in filter_tag_values):
                    python_test.execute = True
                    self.test_runner_data["py_tests"].append(python_test)
                    tests_found = True
            # filtering cmm tests with given tags via CLI
            if self.data["cmm_test_data"]:
                if ui_helper.CMM_FILTER_NAME in filter_tag_values:
                    self.test_runner_data["cmm_tests"] = self.data["cmm_test_data"]
                    tests_found = True
            # if canoe filter mentioned in CLI tag then save all canoe test modules to run
            if self.data["canoe_test_names"]:
                if ui_helper.CANOE_FILTER_NAME in filter_tag_values:
                    self.test_runner_data["capl_tests"] = self.data["canoe_test_names"]
                    tests_found = True
            # raise error if no test data found
            if not tests_found:
                raise RuntimeError(
                    "No tests filtered for given tag list {}".format(filter_tag_values))
        # if no filter tag given then grab data for tests given in cfg file
        else:
            existing_tests = list()
            # precondition based on "reverse_test_selection" argument coming from CLI
            # arg "reverse_selection"
            pre_condition = "not" if reverse_tests_selection else ""
            # check if any python test is mentioned in cfg file tests
            if tests_in_cfg["selected_tests"]:
                for python_test in self.data["py_test_data"]:
                    test_selection = eval(
                        '{} bool(python_test.name in tests_in_cfg["selected_tests"])'
                        .format(pre_condition))
                    if test_selection:
                        python_test.execute = True
                        self.test_runner_data["py_tests"].append(python_test)
                        tests_found = True
                        existing_tests.append(python_test.name)
            # check if any cmm test is mentioned in cfg file tests
            if tests_in_cfg["cmm_tests"]:
                for cmm_test in self.data["cmm_test_data"]:
                    test_selection = eval('{} bool(cmm_test.name in tests_in_cfg["cmm_tests"])'
                                          .format(pre_condition))
                    if test_selection:
                        cmm_test.execute = True
                        self.test_runner_data["cmm_tests"].append(cmm_test)
                        tests_found = True
                        existing_tests.append(cmm_test.name)
            # check if any canoe tests is mentioned in cfg file tests
            if tests_in_cfg["capl_tests"]:
                for canoe_test in self.data["canoe_test_names"]:
                    # if canoe_test in tests_in_cfg["capl_tests"]:
                    test_selection = eval('{} bool(canoe_test in tests_in_cfg["capl_tests"])'
                                          .format(pre_condition))
                    if test_selection:
                        self.test_runner_data["capl_tests"].append(canoe_test)
                        tests_found = True
                        existing_tests.append(canoe_test)
            if not reverse_tests_selection:
                # check if any tests are missing
                self.test_runner_data["missing_tests"] = \
                    [test for test in tests_in_cfg["selected_tests"] if test not in existing_tests]\
                    + [test for test in tests_in_cfg["cmm_tests"] if test not in existing_tests] \
                    + [test for test in tests_in_cfg["capl_tests"] if test not in existing_tests]
            # raise error if no test data found
            if not tests_found:
                raise RuntimeError("No tests found as given in configuration file.")

    @staticmethod
    def get_test_order_number(test):
        """
        Method for giving the order number of test case.
        This number determines the order number of test case which was extracted during test data
        preparation step.

        :param object test: Test case object of class 'TestData'

        :return: The order number of test case which was grabbed during test
        :rtype: int
        """
        return test.order_value

    def prepare_runner_data(self, randomize, report_dir, standard_setup_funcs, tests_freq, run_mode, external_paths_cli,
                            timestamp):
        """
        Method for updating test runner data based on input arguments

        :param bool randomize: Flag for executing tests in random order or not
        :param string report_dir: Location where reports can be generated outside base location
            for CI reporting help purpose
        :param dictionary standard_setup_funcs: Dictionary containing setup, teardown functions
        :param int tests_freq: Execution frequency for each test case
        :param str timestamp: Timestamp enabled status in log ('on', 'off')
        :param list external_paths_cli: Additional paths given in CLI to be added in sys.path list
        :param str run_mode: run mode configuration ('auto', 'auto_gui', 'manual')
        """
        self.test_runner_data["randomize"] = randomize
        self.test_runner_data["run_mode"] = run_mode
        self.test_runner_data["timestamp"] = timestamp
        self.test_runner_data["paths"] = self.project_paths
        self.test_runner_data["tests_frequency"] = tests_freq
        self.test_runner_data["setup_files"] = standard_setup_funcs
        self.test_runner_data["setup_file_path"] = self.setup_file_data['setup_file_path']
        self.test_runner_data["cfg_file_path"] = self.current_cfg.loaded_config
        # rearrange python tests with respect to their order number which is in alphabetic sequence
        self.test_runner_data["py_tests"].sort(key=self.get_test_order_number)
        # rearrange cmm tests with respect to their order number which is in alphabetic sequence
        self.test_runner_data["cmm_tests"].sort(key=self.get_test_order_number)
        # rearranging canoe test modules w.r.t to GUI view
        self.test_runner_data["capl_tests"] = sorted(
            self.test_runner_data["capl_tests"], key=lambda e: self.data["canoe_test_names"].index(e))
        # Additional paths form CLI and cfg
        self.test_runner_data["additional_paths"] = []
        if external_paths_cli:
            for path in [item for sub_list in external_paths_cli for item in sub_list]:
                self.test_runner_data["additional_paths"].append(path)
        if len(self.current_cfg.additional_paths) > 0:
            self.test_runner_data["additional_paths"].extend(self.current_cfg.additional_paths)
        time_stamp = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        self.test_runner_data["paths"][helper.EXEC_RECORD_DIR] = os.path.join(self.report_path, 'reports_') + \
            str(time_stamp) + os.sep
        self.test_runner_data["paths"][helper.TXT_REPORT] = os.path.join(
            self.report_path, 'reports_' + str(time_stamp), 'contest__txt_reports') + os.sep
        self.test_runner_data["paths"][helper.HTML_REPORT] = os.path.join(
            self.report_path, 'reports_' + str(time_stamp), 'contest__html_reports') + os.sep
        self.test_runner_data["paths"][helper.EXTERNAL_REPORT] = report_dir
        # if report directory given cli and it's not equal to report directory mentioned in cfg
        # file then update respective key value in 'test_runner_data' dictionary
        if report_dir and report_dir != self.report_path:
            LOG.info("External report directory: %s", report_dir)
            self.test_runner_data["paths"][helper.EXTERNAL_REPORT] = \
                report_dir + os.sep if not report_dir.endswith(os.sep) else report_dir
            self.test_runner_data["ext_report_dir_with_timestamp"] = os.path.join(
                self.test_runner_data["paths"][helper.EXTERNAL_REPORT], 'reports_' + str(time_stamp))

    def detect_duplicate_setup_files(self):
        """
        Method for detecting if there are any duplications of setup files in Python test location.
        In-case of duplication raise error.
        """
        similar_setup_file_names = list()
        # check duplication of names only if test type is python specific
        # loop for fetching similar names
        for index, to_compare in enumerate(self.get_setup_files()):
            for next_content in self.get_setup_files()[(index + 1):]:
                if to_compare[1] == next_content[1]:
                    similar_setup_file_names.append(to_compare[0])
                    similar_setup_file_names.append(next_content[0])
        # raise error in-case duplication found
        if similar_setup_file_names:
            similar_setup_file_names = set(similar_setup_file_names)
            err_msg = "Same names for setup.pytest scripts detected. Please use " \
                      "distinct names. Scripts names are printed on console."
            LOG.error(err_msg)
            if self.gui:
                ui_helper.pop_up_msg(helper.InfoLevelType.ERR, err_msg)
            LOG.error("-" * 100)
            for setup_file_name in similar_setup_file_names:
                LOG.error(setup_file_name)
            LOG.error("-" * 100)
            raise RuntimeError(err_msg)

    def update_client_setup_file(self, setup_file):
        """
        Method for the setup file information for REST client informer.

        :param string setup_file: contains user provided setup file
        """
        setup_file_path = None
        default_setup_file_path = None
        default_setup_file_list = [
            index[0] for index in self.data["setup_files"] if "setup.pytest" in index[1]]
        if default_setup_file_list:
            default_setup_file_path = default_setup_file_list[0]
        if setup_file:
            # unify file paths to be always os.path.sep
            setup_file = setup_file.replace('/', os.path.sep)
            setup_file = setup_file.replace('\\', os.path.sep)
            # extracting setup file path from list of saved setup file list
            setup_file_to_search = setup_file.split(os.sep)[-1]
        else:
            setup_file_to_search = "setup.pytest"
        # finding the path of setup file for assignment
        for index in self.data["setup_files"]:
            if setup_file_to_search in index[1]:
                setup_file_path = index[0]
                break
        # if no path found i.e. setup file not found then assign the default file "setup.pytest"
        if not setup_file_path:
            setup_file_path = default_setup_file_path
        # assign setup file path to gui variable (if required) and rest client informer
        if self.gui:
            self.gui.setup_file = setup_file_path
        client_informer.REST_CLIENT_INFORMER.setup_file_info = setup_file_path
