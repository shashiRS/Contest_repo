"""
    Module for generating XML report with JUNIT reporting template.
    Copyright 2019 Continental Corporation

    This module will generate XML report for overall test run according to JUNIT reporting template.
    This report will be parsed by Jenkins JUNIT plugin for displaying test results in presentable
    way on Jenkins web page.

    :platform: Linux, Windows
    :file: xml_report.py
    :author:
        - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
"""

# standard Python imports
import os
import re
import time
import socket
from xml.etree.ElementTree import Element, ElementTree

# custom imports
from ptf.ptf_utils.test_watcher import TestWatcher
from ptf.ptf_utils.common import _get_user
from data_handling import helper
from global_vars import TEST_ENVIRONMENT, TestVerdicts


class XmlReporter(TestWatcher):
    """
    Watcher for XML report generation.
    """

    def __init__(self, paths):
        """
        Initializes the xml reporter

        :param dictionary paths: Dictionary containing all paths
        """
        # extracting txt and base report locations from paths dictionary
        txt_report_path = paths["paths"][helper.TXT_REPORT]
        base_report_dir = paths["paths"][helper.BASE_REPORT_DIR]
        # create a list with initial value as txt report file
        self.report_file = [os.path.join(txt_report_path, "TEST_RESULT.xml")]
        external_report_dir = paths["paths"][helper.EXTERNAL_REPORT]
        # if report directory was given via cli then add it to above list
        if external_report_dir:
            # prepare path for cli report directory and append to report file list
            external_report_dir = txt_report_path.replace(base_report_dir, external_report_dir)
            self.report_file.append(os.path.join(external_report_dir, "TEST_RESULT.xml"))
        # dictionary for storing data
        self.__xml_data = {
            "start_time": None,
            "failed_tests": 0,
            "passed_tests": 0,
            "ignored_tests": 0,
            "skipped_tests": 0,
        }
        # for storing prints during a test case execution
        self.__system_output = ""
        # location for storing xml result file
        self.__report_file = self.report_file
        # creating 'testsuite' element and assigning it to main xml tree
        self.__test_suite = Element("testsuite")
        self.__xml_tree = ElementTree(self.__test_suite)
        self.__test_suite.set("name", TEST_ENVIRONMENT)
        self.__test_suite.set("machine", socket.gethostname())
        self.__test_suite.set("user", _get_user())

    def write(self, *args, **kwargs):
        """
        Overwrite method for capturing prints during test case execution

        :param tuple args: Tuple containing print information
        :param dictionary kwargs: Keyword args dictionary
        """
        # updating system output variable with prints
        self.__system_output = self.__system_output + args[0]

    @staticmethod
    def __ignore_xml_invalid_chars(output_str):
        """
        Method to replace invalid characters in XML file with empty string in order to avoid parsing
        in Jenkins via junit plugin

        :param str output_str: System output string

        :return: string with replacement if invalid xml characters (if exists)
        :rtype: str
        """
        return re.sub("[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]", "", output_str)

    def __create_test_element(self, test_case, failure=False, skipped=False):
        """
        Method for creating test case elements based on input params

        :param TestCaseInfo test_case: The testcase whose element need to be created
        :param bool failure: True if test passed else False
        :param bool skipped: True if test is ignored or skipped else False
        """
        # creating test case element with necessary attributes
        test_element = Element("testcase")
        test_element.set("classname", "Tests")
        # if test is not skipped or ignored then add respective attributes
        if not skipped:
            test_element.set("name", test_case.name)
            test_element.set("time", str(test_case.run_time))
            # in-case test case failed then add failure element as child to test_element
            if failure:
                try:
                    issue_element = "failure" if "ptf.verify_utils" in str(type(test_case.failure_info)) else "error"
                # disabling broad-exception-caught to catch all exceptions
                # pylint: disable=W0718
                except Exception:
                    issue_element = "failure"
                failure_element = Element(issue_element)
                if test_case.verdict == TestVerdicts.INCONCLUSIVE:
                    failure_element.set("message", str(test_case.inconclusive_info))
                elif test_case.verdict == TestVerdicts.FAIL:
                    failure_element.set("message", str(test_case.failure_info))
                test_element.append(failure_element)
        # else if test is skipped then add test name attribute and skipped element
        else:
            test_element.set("name", test_case.name)
            test_element.set("time", str(test_case.run_time))
            skip_element = Element("skipped")
            skip_element.set("message", str(test_case.skip_info))
            test_element.append(skip_element)
        # creating system output element and adding it as child to test_element
        sys_out_element = Element("system-out")
        # here first ignoring all chars which are invalid in xml with empty space before dumping
        # in report, it's require otherwise the parsing of xml report files in Jenkins via junit
        # plugin is not possible
        sys_out_element.text = self.__ignore_xml_invalid_chars(self.__system_output)
        test_element.append(sys_out_element)
        # updating test cases list with test element
        self.__test_suite.append(test_element)

    def test_finished(self, testcase):
        """
        Method for creating a 'testcase' element (Pass/Fail) and appending it to main test suite

        :param TestCaseInfo testcase: The testcase whose execution is finished
        """
        # Ignore parameterized tests, instead only store the report for each parameter
        if testcase.test_function.__name__ == "parameterized_runner":
            return
        if testcase.verdict == TestVerdicts.PASS:
            # incrementing the pass tests counter
            self.__xml_data["passed_tests"] = self.__xml_data["passed_tests"] + 1
            self.__create_test_element(testcase)
        elif testcase.verdict == TestVerdicts.SKIP:
            # incrementing the pass tests counter
            self.__xml_data["skipped_tests"] = self.__xml_data["skipped_tests"] + 1
            self.__create_test_element(testcase, skipped=True)
        else:
            # incrementing the fail tests counter if test is not passing i.e. failed or inconclusive
            # please note that inconclusive verdict of a test case (only warning occurred in test) is treated as failure
            # in junit xml report generated here as junit xml does not have separate section for inconclusive reporting
            self.__xml_data["failed_tests"] = self.__xml_data["failed_tests"] + 1
            self.__create_test_element(testcase, failure=True)
        # clearing system output variable after each test run finished
        self.__system_output = ""

    def test_run_started(self, _):
        """
        Triggered if test run is started.
        """
        self.__xml_data["start_time"] = time.time()

    def test_run_finished(self, _):
        """
        Method for adding final information to test suite element and creating XML report
        """
        total_run_time = str((time.time() - self.__xml_data["start_time"]))
        self.__test_suite.set("failures", str(self.__xml_data["failed_tests"]))
        self.__test_suite.set("skipped", str(self.__xml_data["skipped_tests"]))
        self.__test_suite.set("tests", str(self.__xml_data["passed_tests"]))
        self.__test_suite.set("time", total_run_time)
        for report in self.__report_file:
            self.__xml_tree.write(report, encoding="utf-8", xml_declaration=True)
