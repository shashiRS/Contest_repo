"""
    Copyright 2023 Continental Corporation

    :file: test_skip_decorator_normal.py
    :platform: Windows, Linux
    :synopsis:
        Script for tests related to @skip_if decorator usage in auto mode '-r auto' for normal test
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


class TestSkipIf(unittest.TestCase):
    """ Test Class tests related to @skip_if decorator usage in auto mode '-r auto'"""
    paths_dir = {
        'cfg': os.path.join(REPO_ROOT_DIR, 'cfg', 'skip_tests.ini'),
        'main': os.path.join(REPO_ROOT_DIR, 'main.py')
    }
    verdicts_list = ["[PASSED]", "[INCONCLUSIVE]", "[FAILED]", "[SKIPPED]"]
    report_dir_name = "reports_skip_normal"

    def extract_content_from_report(self, report_data, expected_test_flow, expected_result, starting_tag):
        """
        Method to read report, extract execution flow data and verdict for verification

        :param string report_data: path to test case generated report
        :param list expected_test_flow: list containing elements with string of expected execution flow
        :param list expected_result: list containing expected result for test under consideration
        :param string starting_tag: string containing tag based on which concerned report output data can be extracted
        """
        with open(report_data) as report:
            report_content = report.readlines()
        test_exe_flow_list = [
            content.strip(os.linesep) for content in report_content if content.startswith(starting_tag)]
        actual_verdict = [
            content.strip(os.linesep) for content in report_content if content.strip(os.linesep) in self.verdicts_list]
        self.assertListEqual(expected_test_flow, test_exe_flow_list, "Problem in @skip_if execution flow")
        self.assertListEqual(expected_result, actual_verdict, "Problem in verdict verification")

    @classmethod
    def setUpClass(cls):
        """
        Initialize the class with variables, objects etc., for testing
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
            '--report-dir', os.path.join(SCRIPT_DIR, cls.report_dir_name),
            '-l', os.path.join(REPO_ROOT_DIR, 'ptf', 'demo_tests', 'skip_tests', 'normal')]
        # Run the ConTest application with given config file
        cls.test_exec = subprocess.run(run_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=set_shell)
        # If general error occurred during Contest gui execution, raise error
        if cls.test_exec.returncode == GENERAL_ERR:
            raise RuntimeError(
                "Error in setUpClass for cmd '{}':\n{}".format(
                    run_cmd, (cls.test_exec.stdout + cls.test_exec.stdout).decode("utf-8")))
        # get current reports folder directory path which is created
        cls.report_folder_path = max(glob.glob(os.path.join(SCRIPT_DIR, cls.report_dir_name, 'reports_*/')),
                                     key=os.path.getmtime)
        cls.reports_dir = os.path.join(cls.report_folder_path, 'contest__txt_reports')

    def test_global_setup_call(self):
        """
        Method for verifying the correct global_setup function call
        """
        test_name = "global_setup"
        expected_test_exe_flow_list = ["TEST: executing standard global_setup"]
        expected_verdict = ["[PASSED]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(test_case_report, expected_test_exe_flow_list, expected_verdict, "TEST:")

    def test_global_teardown_call(self):
        """
        Method for verifying the correct global_setup function call
        """
        test_name = "global_teardown"
        expected_test_exe_flow_list = ["TEST: executing standard global_teardown"]
        expected_verdict = ["[PASSED]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(test_case_report, expected_test_exe_flow_list, expected_verdict, "TEST:")

    def test_normal_test_without_skip(self):
        """
        Test for execution flow check for a normal test
        """
        test_name = "SWT_NORMAL_TESTv1"
        expected_test_exe_flow_list = [
            "TEST: executing standard setup",
            "TEST: Hello World",
            "TEST: executing standard teardown"
        ]
        expected_verdict = ["[PASSED]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(test_case_report, expected_test_exe_flow_list, expected_verdict, "TEST:")

    def test_skip_on_linux_via_statement(self):
        """
        Test for execution flow check for a test skipped on linux platform
        """
        test_name = "SWT_SKIP_ON_LINUX_VIA_STATEMENT_TESTv1"
        if sys.platform == "win32":
            extract_string = "TEST:"
            expected_test_exe_flow_list = [
                extract_string + " executing standard setup",
                extract_string + " Running on '{}' platform".format(sys.platform),
                extract_string + " executing standard teardown"
            ]
            expected_verdict = ["[PASSED]"]
        else:
            extract_string = "Skipping due to reason:"
            expected_test_exe_flow_list = [
                extract_string + " This test shall only run on windows platform"
            ]
            expected_verdict = ["[SKIPPED]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(
            test_case_report, expected_test_exe_flow_list, expected_verdict, extract_string)

    def test_skip_on_windows_via_statement(self):
        """
        Test for execution flow check for a test skipped on windows platform
        """
        test_name = "SWT_SKIP_ON_WINDOWS_VIA_STATEMENT_TESTv1"
        if sys.platform == "linux":
            extract_string = "TEST:"
            expected_test_exe_flow_list = [
                extract_string + " executing standard setup",
                extract_string + " Running on '{}' platform".format(sys.platform),
                extract_string + " executing standard teardown"
            ]
            expected_verdict = ["[PASSED]"]
        else:
            extract_string = "Skipping due to reason:"
            expected_test_exe_flow_list = [
                extract_string + " This test shall only run on linux platform"
            ]
            expected_verdict = ["[SKIPPED]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(
            test_case_report, expected_test_exe_flow_list, expected_verdict, extract_string)

    def test_skip_on_linux_via_function(self):
        """
        Test for execution flow check for a test skipped on linux platform
        """
        test_name = "SWT_SKIP_ON_LINUX_VIA_FUNC_TESTv1"
        if sys.platform == "win32":
            extract_string = "TEST:"
            expected_test_exe_flow_list = [
                extract_string + " executing standard setup",
                extract_string + " Running on '{}' platform".format(sys.platform),
                extract_string + " executing standard teardown"
            ]
            expected_verdict = ["[PASSED]"]
        else:
            extract_string = "Skipping due to reason:"
            expected_test_exe_flow_list = [
                extract_string + " This test shall only run on windows platform"
            ]
            expected_verdict = ["[SKIPPED]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(
            test_case_report, expected_test_exe_flow_list, expected_verdict, extract_string)

    def test_skip_on_windows_via_function(self):
        """
        Test for execution flow check for a test skipped on windows platform
        """
        test_name = "SWT_SKIP_ON_WINDOWS_VIA_FUNC_TESTv1"
        if sys.platform == "linux":
            extract_string = "TEST:"
            expected_test_exe_flow_list = [
                extract_string + " executing standard setup",
                extract_string + " Running on '{}' platform".format(sys.platform),
                extract_string + " executing standard teardown"
            ]
            expected_verdict = ["[PASSED]"]
        else:
            extract_string = "Skipping due to reason:"
            expected_test_exe_flow_list = [
                extract_string + " This test shall only run on linux platform"
            ]
            expected_verdict = ["[SKIPPED]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(
            test_case_report, expected_test_exe_flow_list, expected_verdict, extract_string)

    def test_param_test_no_skip(self):
        """
        Test for execution flow check for a param test not skipped
        """
        test_name = "SWT_CATS_BREEDS_HEALTHYv1"
        param_test_name_0 = "{}(index british)".format(test_name)
        param_test_name_1 = "{}(index american)".format(test_name)
        param_test_name_2 = "{}(index scotish)".format(test_name)
        extract_string = "TEST:"
        expected_test_exe_flow_list = [
            extract_string + " executing standard setup",
            extract_string + " cat breeds printed",
            extract_string + " executing standard teardown",
        ]
        expected_verdict = ["[PASSED]"]
        test_case_report_0 = os.path.join(self.reports_dir, '{}.txt'.format(param_test_name_0))
        test_case_report_1 = os.path.join(self.reports_dir, '{}.txt'.format(param_test_name_1))
        test_case_report_2 = os.path.join(self.reports_dir, '{}.txt'.format(param_test_name_2))
        self.extract_content_from_report(
            test_case_report_0, expected_test_exe_flow_list, expected_verdict, extract_string)
        self.extract_content_from_report(
            test_case_report_1, expected_test_exe_flow_list, expected_verdict, extract_string)
        self.extract_content_from_report(
            test_case_report_2, expected_test_exe_flow_list, expected_verdict, extract_string)

    def test_param_test_skip(self):
        """
        Test for execution flow check for a param test skipped
        """
        test_name = "SWT_CATS_BREEDS_SICKv1"
        param_test_name_0 = "{}(index british)".format(test_name)
        param_test_name_1 = "{}(index american)".format(test_name)
        param_test_name_2 = "{}(index scotish)".format(test_name)
        extract_string = "Skipping parameterized test due to reason:"
        expected_test_exe_flow_list = [
            extract_string + " Our cats are sick",
        ]
        expected_verdict = ["[SKIPPED]"]
        test_case_report_0 = os.path.join(self.reports_dir, '{}.txt'.format(param_test_name_0))
        test_case_report_1 = os.path.join(self.reports_dir, '{}.txt'.format(param_test_name_1))
        test_case_report_2 = os.path.join(self.reports_dir, '{}.txt'.format(param_test_name_2))
        self.extract_content_from_report(
            test_case_report_0, expected_test_exe_flow_list, expected_verdict, extract_string)
        self.extract_content_from_report(
            test_case_report_1, expected_test_exe_flow_list, expected_verdict, extract_string)
        self.extract_content_from_report(
            test_case_report_2, expected_test_exe_flow_list, expected_verdict, extract_string)

    @classmethod
    def tearDownClass(cls):
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
