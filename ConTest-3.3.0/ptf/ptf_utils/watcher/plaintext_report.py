"""
    Reports console output to plaintext files.
    Copyright 2019 Continental Corporation

    This module contains a watcher to write the console output to plaintext files.

    :file: plaintext_report.py
    :author:
        - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""

import os

from ptf.ptf_utils.test_watcher import TestWatcher
from data_handling import helper


class PlainTextReporter(TestWatcher):
    """
    This watcher will write console output to plaintext files.
    """

    def __init__(self, paths):
        """
        Creates a new plaintext reporter

        :param dictionary paths: Dictionary containing all paths
        """
        # extracting txt and base report locations from paths dictionary
        txt_report_path = paths["paths"][helper.TXT_REPORT]
        base_report_dir = paths["paths"][helper.BASE_REPORT_DIR]
        # create a list with initial value as txt report directory
        self.report_dir = [txt_report_path]
        # if report directory was given via cli then add it to above list
        external_report_dir = paths["paths"][helper.EXTERNAL_REPORT]
        if external_report_dir:
            # prepare path for cli report directory and append to report directory list
            external_report_dir = txt_report_path.replace(base_report_dir, external_report_dir)
            self.report_dir.append(external_report_dir)
        # create report directories if not exists
        for directory in self.report_dir:
            if not os.path.exists(directory):
                os.makedirs(directory)
        # list containing report files objects
        self.overall_report = [open(os.path.join(directory, 'TESTS_SUMMARY.txt'), 'w') for
                               directory in self.report_dir]
        # the report for each single testcase
        self.single_report = None

    def write(self, *args, **kwargs):
        """
        Writes the given output to files.

        :param args: The arguments to write
        :param kwargs: The keyword arguments to write
        """
        if self.overall_report:
            for report in self.overall_report:
                report.write(*args, **kwargs)

        if self.single_report:
            for report in self.single_report:
                report.write(*args, **kwargs)

    def flush(self, *args, **kwargs):
        """
        Triggered when the output stream is flushed.

        :param args: Optional arguments
        :param kwargs: Optional keyword arguments
        """

        if self.overall_report:
            for report in self.overall_report:
                report.flush()

        if self.single_report:
            for report in self.single_report:
                report.flush()

    def test_started(self, testcase):
        """
        Creates a new plain text report for the current testcase.

        :param TestCaseInfo testcase: The testcase to write
        """
        # Ignore parameterized tests, instead only store the report for each parameter
        if testcase.test_function.__name__ == "parameterized_runner":
            return

        # Remove double point from testcase name to allow storing on windows
        name = testcase.name.replace(':', '')
        self.single_report = [open(os.path.join(directory, name + '.txt'), 'w') for
                              directory in self.report_dir]

    def test_finished(self, _):
        """
        Stops writing output for a single testcase.
        """
        if self.single_report:
            for report in self.single_report:
                report.close()
        self.single_report = None

    def test_run_finished(self, _):
        """
        Stops writing of overall report.
        """
        for report in self.overall_report:
            report.close()
        self.overall_report = None
