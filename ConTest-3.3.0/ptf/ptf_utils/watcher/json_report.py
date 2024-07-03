"""
    Reports to json output.
    Copyright 2019 Continental Corporation

    This module contains a watcher to write the test status as json.

    :file: json_report.py
    :author:
        - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""

# standard Python imports
import json
import os
import time
import socket
from datetime import datetime

# custom imports
from ptf.ptf_utils.test_watcher import TestWatcher
from ptf.ptf_utils.common import _get_user
from data_handling import helper
from global_vars import TEST_ENVIRONMENT, TestVerdicts
from ..global_params import get_reporting_parameter, _get_files_for_report


class JsonReporter(TestWatcher):
    """
    This watcher will create the test output as json.
    """

    SCHEMA_VERSION_URL = (
        "https://cip-config.cmo.conti.de/v2/configuration/contest/"
        "json_report_schema/1.0/schemas/test_report_schema.json"
    )

    def __init__(self, paths):
        """
        Initializes the json reporter

        :param dictionary paths: Dictionary containing all paths
        """
        # extracting txt and base report locations from paths dictionary
        txt_report_path = paths["paths"][helper.TXT_REPORT]
        base_report_dir = paths["paths"][helper.BASE_REPORT_DIR]
        # create a list with initial value as txt report file
        self.report_file = [os.path.join(txt_report_path, "TEST_RESULT.json")]
        external_report_dir = paths["paths"][helper.EXTERNAL_REPORT]
        # if report directory was given via cli then add it to above list
        if external_report_dir:
            # prepare path for cli report directory and append to report file list
            external_report_dir = txt_report_path.replace(base_report_dir, external_report_dir)
            self.report_file.append(os.path.join(external_report_dir, "TEST_RESULT.json"))

        # fetching reporting parameters
        self.reporting_params = get_reporting_parameter()

        # the result directory that will be printed to file
        self.json_data = {}
        self.json_data["$schema"] = str()
        self.json_data["summary"] = {}
        self.json_data["tests"] = []

        # some statistics
        self.start_time = None
        self.failed_tests = 0
        self.passed_tests = 0
        self.skipped_tests = 0
        self.inconclusive_tests = 0
        self.ignored_tests = 0

    def test_finished(self, testcase):
        """
        Adds finished test information to the json data.

        :param TestCaseInfo testcase: The testcase that finished.
        """
        # ignore parameterized tests, instead only store the report for each parameter
        if testcase.test_function.__name__ == "parameterized_runner":
            return
        result_data = {
            "test_execution": testcase.steps,
            "test_type": testcase.test_type,
            "test_details": testcase.details,
            "precondition": testcase.precondition,
            "test_name": testcase.name,
            "test_duration": testcase.run_time * 1000,
            "test_date": datetime.fromtimestamp(testcase.start_time).strftime("%c"),
            "test_status": "",
            "test_verifies": testcase.verified_ids,
            "automates_id": testcase.automates,
            "test_tags": testcase.tags,
            "canoe_test_case_details": testcase.canoe_tm_tc_verdicts,
            # copy function is used, since this function is returning global variable
            # any changes to global variable is impacting the assigned value
            "meta_data_files": _get_files_for_report().copy(),
            # copy function is used, since this function is returning global variable
            # any changes to global variable is impacting the assigned value
            "test_warnings": testcase.inconclusive_info.copy(),
            "test_failure": None,
            "test_skip_reason": None,
        }
        if testcase.verdict == TestVerdicts.PASS:
            result_data["test_status"] = "PASSED"
            self.passed_tests = self.passed_tests + 1
        elif testcase.verdict == TestVerdicts.INCONCLUSIVE:
            result_data["test_status"] = "INCONCLUSIVE"
            self.inconclusive_tests = self.inconclusive_tests + 1
        elif testcase.verdict == TestVerdicts.FAIL:
            result_data["test_status"] = "FAILED"
            result_data["test_failure"] = str(testcase.failure_info)
            self.failed_tests = self.failed_tests + 1
        elif testcase.verdict == TestVerdicts.SKIP:
            result_data["test_status"] = "SKIPPED"
            result_data["test_skip_reason"] = str(testcase.skip_info)
            self.skipped_tests = self.skipped_tests + 1
        self.json_data["tests"].append(result_data)

    def test_run_started(self, _):
        """
        Triggered if test run is started.
        """
        self.start_time = time.time()

    def test_run_finished(self, missing_tests):
        """
        Writes the test run information to the disk.
        """
        self.json_data["$schema"] = JsonReporter.SCHEMA_VERSION_URL
        self.json_data["summary"] = {
            "Runtime": (time.time() - self.start_time) / 60,
            "Total_Tests": len(self.json_data["tests"]),
            "Failed_Tests": self.failed_tests,
            "Passed_Tests": self.passed_tests,
            "Inconclusive_Tests": self.inconclusive_tests,
            "Skipped_Tests": self.skipped_tests,
            "Ignored_Tests": self.ignored_tests,
            "Missing_Tests": len(missing_tests),
            "Test_Run_Result": True,
            "Test_Environment": TEST_ENVIRONMENT,
            "Machine": socket.gethostname(),
            "User": _get_user(),
            "Reporting_Parameters": self.reporting_params,
        }

        if self.failed_tests > 0:
            self.json_data["summary"]["Test_Run_Result"] = False

        for report in self.report_file:
            with open(report, "w", encoding="utf-8") as outfile:
                json.dump(self.json_data, outfile, indent=4)
