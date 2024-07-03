"""
    Copyright 2023 Continental Corporation

    :file: test_execution_flow_check.py
    :platform: Windows, Linux
    :synopsis:
        Script for tests checking execution flow control of test runner (normal and parameterized)
    :author:
        - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
"""
import os
import sys
import unittest
import subprocess
import shutil
import glob

try:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    REPO_ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
    sys.path.append(os.path.abspath(REPO_ROOT_DIR))
    from ptf.tests.release_testing import format_helper
    from global_vars import GENERAL_ERR
finally:
    pass


class TestExecutionFlow(unittest.TestCase):
    """Test Class containing tests related to execution flow"""
    paths_dir = {
        'cfg': os.path.join(SCRIPT_DIR, 'execution_flow', 'execution_flow.ini'),
        'main': os.path.join(REPO_ROOT_DIR, 'main.py')
    }
    verdicts_list = ["[PASSED]", "[INCONCLUSIVE]", "[FAILED]", "[SKIPPED]"]
    report_dir_name = os.path.join(SCRIPT_DIR, "execution_flow", "reports")
    report_folder_path = None

    def extract_content_from_summary_report(self, report_data, expected_test_flow, starting_tag):
        """
        Method to read summary report and extract execution flow data for verification

        :param string report_data: path to test case generated report
        :param list expected_test_flow: list containing elements with string of expected execution flow
        :param list starting_tag: list containing tags based on which concerned report output data can be extracted
        """
        with open(report_data) as report:
            report_content = report.readlines()
        test_exe_flow_list = list()
        starting_tag.extend(TestExecutionFlow.verdicts_list)
        for content in report_content:
            for tag in starting_tag:
                if content.startswith(tag):
                    test_exe_flow_list.append(content.strip(os.linesep).rstrip())
        self.assertListEqual(expected_test_flow, test_exe_flow_list, "Problem in execution flow")

    @classmethod
    def run_contest(cls, setup_file="setup.pytest"):
        """
        Method to run contest for checking tests execution flow

        :param string setup_file: Name of setup file to be used
        """
        cls.report_folder_path = None
        if sys.platform == "linux":
            set_shell = False
        else:
            set_shell = True
        run_cmd = [
            'python', cls.paths_dir['main'],
            '-c', cls.paths_dir['cfg'],
            '-r', 'auto',
            '-l', os.path.join(SCRIPT_DIR, 'execution_flow'),
            '--setup-file', setup_file]
        # Run the ConTest application with given config file
        cls.test_exec = subprocess.run(run_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=set_shell)
        # If general error occurred during Contest execution, raise error
        if cls.test_exec.returncode == GENERAL_ERR:
            raise RuntimeError(
                "Error in setUpClass for cmd '{}':\n{}".format(
                    run_cmd, (cls.test_exec.stdout + cls.test_exec.stdout).decode("utf-8")))
        # get current reports folder directory path which is created
        cls.report_folder_path = max(glob.glob(os.path.join(SCRIPT_DIR, cls.report_dir_name, 'reports_*/')),
                                     key=os.path.getmtime)
        cls.reports_dir = os.path.join(cls.report_folder_path, 'contest__txt_reports')

    def setUp(self) -> None:
        """
        setup function
        """
        pass

    def test_flow_without_global_setup_failure(self):
        """
        Method for verifying the execution flow when there is no failure in global_setup function
        """
        self.run_contest()
        expected_test_exe_flow_list = [
            "TEST: Executing global_setup",
            "[PASSED]",
            "TEST: Executing setup",
            "TEST: Executing SWT_NORMAL_TEST_PASSv1",
            "TEST: Executing teardown",
            "[PASSED]",
            "TEST: Executing setup",
            "TEST: Executing SWT_NORMAL_TEST_FAILv1",
            "TEST: Executing teardown",
            "--> Testcase failed with Failure(s):  TEST: Forced failure from SWT_NORMAL_TEST_FAILv1",
            "[FAILED]",
            "Skipping due to reason: TEST: skipped SWT_SKIPv1 as 1 == 1",
            "[SKIPPED]",
            "TEST: Executing setup",
            "TEST: Executing SWT_NO_SKIPv1",
            "TEST: Executing teardown",
            "[PASSED]",
            "TEST: Executing setup",
            "TEST: Executing SWT_NORMAL_PARAM_TESTv1(index: pass)",
            "TEST: Executing teardown",
            "[PASSED]",
            "TEST: Executing setup",
            "TEST: Executing SWT_NORMAL_PARAM_TESTv1(index: fail)",
            "TEST: Executing teardown",
            "[PASSED]",
            "[PASSED]",
            "Skipping parameterized test due to reason: TEST: skipped SWT_NORMAL_PARAM_TEST_SKIPv1 as 1 == 1",
            "[SKIPPED]",
            "Skipping parameterized test due to reason: TEST: skipped SWT_NORMAL_PARAM_TEST_SKIPv1 as 1 == 1",
            "[SKIPPED]",
            "[SKIPPED]",
            "TEST: Executing setup",
            "TEST: Executing SWT_NORMAL_PARAM_TEST_NO_SKIPv1(index: pass)",
            "TEST: Executing teardown",
            "[PASSED]",
            "TEST: Executing setup",
            "TEST: Executing SWT_NORMAL_PARAM_TEST_NO_SKIPv1(index: fail)",
            "TEST: Executing teardown",
            "[PASSED]",
            "[PASSED]",
            "TEST: Executing global_teardown",
            "[PASSED]"
        ]
        summary_report_txt = os.path.join(self.reports_dir, 'TESTS_SUMMARY.txt')
        self.extract_content_from_summary_report(
            summary_report_txt, expected_test_exe_flow_list,
            ["TEST:", "--> Testcase failed with Failure(s):", "Skipping due to reason:",
             "Skipping parameterized test due to reason:"])

    def test_flow_with_global_setup_failure(self):
        """
        Method for verifying the execution flow when there is a failure in global_setup function
        """
        self.run_contest(setup_file="setup_global_setup_failure.pytest")
        expected_test_exe_flow_list = [
            "--> Testcase failed with Failure(s):  TEST: Forced failure from global_setup",
            "[FAILED]",
            "--> Testcase failed with Failure(s):  Execution of 'SWT_NORMAL_TEST_PASSv1' did not happen due to "
            "failure in 'global_setup' function",
            "[FAILED]",
            "--> Testcase failed with Failure(s):  Execution of 'SWT_NORMAL_TEST_FAILv1' did not happen due to "
            "failure in 'global_setup' function",
            "[FAILED]",
            "Skipping due to reason: TEST: skipped SWT_SKIPv1 as 1 == 1",
            "[SKIPPED]",
            "--> Testcase failed with Failure(s):  Execution of 'SWT_NO_SKIPv1' did not happen due to "
            "failure in 'global_setup' function",
            "[FAILED]",
            "--> Testcase failed with Failure(s):  Execution of 'SWT_NORMAL_PARAM_TESTv1(index: pass)' "
            "did not happen due to failure in 'global_setup' function",
            "[FAILED]",
            "--> Testcase failed with Failure(s):  Execution of 'SWT_NORMAL_PARAM_TESTv1(index: fail)' "
            "did not happen due to failure in 'global_setup' function",
            "[FAILED]",
            "[FAILED]",
            "Skipping parameterized test due to reason: TEST: skipped SWT_NORMAL_PARAM_TEST_SKIPv1 as 1 == 1",
            "[SKIPPED]",
            "Skipping parameterized test due to reason: TEST: skipped SWT_NORMAL_PARAM_TEST_SKIPv1 as 1 == 1",
            "[SKIPPED]",
            "[SKIPPED]",
            "--> Testcase failed with Failure(s):  Execution of 'SWT_NORMAL_PARAM_TEST_NO_SKIPv1(index: pass)' "
            "did not happen due to failure in 'global_setup' function",
            "[FAILED]",
            "--> Testcase failed with Failure(s):  Execution of 'SWT_NORMAL_PARAM_TEST_NO_SKIPv1(index: fail)' "
            "did not happen due to failure in 'global_setup' function",
            "[FAILED]",
            "[FAILED]",
            "TEST: Executing global_teardown",
            "[PASSED]"
        ]
        summary_report_txt = os.path.join(self.reports_dir, 'TESTS_SUMMARY.txt')
        self.extract_content_from_summary_report(
            summary_report_txt, expected_test_exe_flow_list,
            ["TEST:", "--> Testcase failed with Failure(s):", "Skipping due to reason:",
             "Skipping parameterized test due to reason:"])

    def test_flow_with_local_setup_failure(self):
        """
        Method for verifying the execution flow when there is a failure in setup function
        """
        self.run_contest(setup_file="setup_local_setup_failure.pytest")
        expected_test_exe_flow_list = [
            "TEST: Executing global_setup",
            "[PASSED]",
            "TEST: Executing teardown",
            "--> Testcase failed with Failure(s):  TEST: Forced failure from setup",
            "[FAILED]",
            "TEST: Executing teardown",
            "--> Testcase failed with Failure(s):  TEST: Forced failure from setup",
            "[FAILED]",
            "Skipping due to reason: TEST: skipped SWT_SKIPv1 as 1 == 1",
            "[SKIPPED]",
            "TEST: Executing teardown",
            "--> Testcase failed with Failure(s):  TEST: Forced failure from setup",
            "[FAILED]",
            "--> Testcase failed with Failure(s):  TEST: Forced failure from setup",
            "TEST: Executing teardown",
            "[FAILED]",
            "--> Testcase failed with Failure(s):  TEST: Forced failure from setup",
            "TEST: Executing teardown",
            "[FAILED]",
            "[FAILED]",
            "Skipping parameterized test due to reason: TEST: skipped SWT_NORMAL_PARAM_TEST_SKIPv1 as 1 == 1",
            "[SKIPPED]",
            "Skipping parameterized test due to reason: TEST: skipped SWT_NORMAL_PARAM_TEST_SKIPv1 as 1 == 1",
            "[SKIPPED]",
            "[SKIPPED]",
            "--> Testcase failed with Failure(s):  TEST: Forced failure from setup",
            "TEST: Executing teardown",
            "[FAILED]",
            "--> Testcase failed with Failure(s):  TEST: Forced failure from setup",
            "TEST: Executing teardown",
            "[FAILED]",
            "[FAILED]",
            "TEST: Executing global_teardown",
            "[PASSED]"
        ]
        summary_report_txt = os.path.join(self.reports_dir, 'TESTS_SUMMARY.txt')
        self.extract_content_from_summary_report(
            summary_report_txt, expected_test_exe_flow_list,
            ["TEST:", "--> Testcase failed with Failure(s):", "Skipping due to reason:",
             "Skipping parameterized test due to reason:"])

    @classmethod
    def tearDown(cls):
        """
        Terminates or deletes the open files and folders after running tests
        """
        # delete all report folders
        folders = glob.iglob(os.path.join(SCRIPT_DIR, cls.report_dir_name))
        for folder in folders:
            if os.path.isdir(folder):
                shutil.rmtree(folder)


if __name__ == '__main__':
    unittest.main(verbosity=2)
