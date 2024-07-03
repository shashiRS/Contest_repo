"""
    Copyright 2023 Continental Corporation

    :file: test_custom_setup.py
    :platform: Windows, Linux
    :synopsis:
        Script for tests related to @custom_setup decorator usage in auto mode '-r auto'
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


class TestCutomSetup(unittest.TestCase):
    """ Test Class tests related to @custom_setup decorator usage in auto mode '-r auto'"""
    paths_dir = {
        'cfg': os.path.join(REPO_ROOT_DIR, 'cfg', 'contest_config_custom_setup.ini'),
        'main': os.path.join(REPO_ROOT_DIR, 'main.py')
    }
    verdicts_list = ["[PASSED]", "[INCONCLUSIVE]", "[FAILED]", "[SKIPPED]"]

    def extract_content_from_report(self, report_data, expected_test_flow, expected_result):
        """
        Method to read report, extract execution flow data and verdict for verification

        :param string report_data: path to test case generated report
        :param list expected_test_flow: list containing elements with string of expected execution flow
        :param list expected_result: list containing expected result for test under consideration
        """
        with open(report_data) as report:
            report_content = report.readlines()
        test_exe_flow_list = [content.strip(os.linesep) for content in report_content if content.startswith("TEST:")]
        actual_verdict = [
            content.strip(os.linesep) for content in report_content if content.strip(os.linesep) in self.verdicts_list]
        self.assertListEqual(expected_test_flow, test_exe_flow_list, "Problem in @custom_setup execution flow")
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
            '--report-dir', os.path.join(SCRIPT_DIR, 'reports_custom_setup'),
            '-l', os.path.join(REPO_ROOT_DIR, 'ptf', 'demo_tests', 'custom_setup'),
            '--setup-file', 'setup_custom']
        # Run the ConTest application with given config file
        cls.test_exec = subprocess.run(run_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=set_shell)
        # If general error occurred during Contest gui execution, raise error
        if cls.test_exec.returncode == GENERAL_ERR:
            raise RuntimeError(
                "Error in setUpClass for cmd '{}':\n{}".format(
                    run_cmd, (cls.test_exec.stdout + cls.test_exec.stdout).decode("utf-8")))
        # get current reports folder directory path which is created
        cls.report_folder_path = max(glob.glob(os.path.join(SCRIPT_DIR, 'reports_custom_setup', 'reports_*/')),
                                     key=os.path.getmtime)
        cls.reports_dir = os.path.join(cls.report_folder_path, 'contest__txt_reports')

    def test_global_setup_call(self):
        """
        Method for verifying the correct global_setup function call
        """
        test_name = "global_setup"
        expected_test_exe_flow_list = ["TEST: executing standard global_setup from setup_custom"]
        expected_verdict = ["[PASSED]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(test_case_report, expected_test_exe_flow_list, expected_verdict)

    def test_expects_in_custom_setup_exe_flow(self):
        """
        Test for execution flow check for a normal test with expects raised in @custom_setup call
        """
        test_name = "SWT_SETUP_EXPECT_ERRv1"
        expected_test_exe_flow_list = [
            "TEST: executing my_setup_fail_expects from setup_custom",
            "TEST: continue executing my_setup_fail_expects from setup_custom",
            "TEST: executing {}".format(test_name),
            "TEST: executing my_teardown from setup_custom"
        ]
        expected_verdict = ["[FAILED]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(test_case_report, expected_test_exe_flow_list, expected_verdict)

    def test_assert_in_custom_setup_exe_flow(self):
        """
        Test for execution flow check for a normal test with assertion raised in @custom_setup call
        """
        test_name = "SWT_SETUP_ASSERT_ERRv1"
        expected_test_exe_flow_list = [
            "TEST: executing my_setup_fail_assert from setup_custom",
            "TEST: executing my_teardown from setup_custom"
        ]
        expected_verdict = ["[FAILED]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(test_case_report, expected_test_exe_flow_list, expected_verdict)

    def test_warn_in_custom_setup_exe_flow(self):
        """
        Test for execution flow check for a normal test with warning logged in @custom_setup call
        """
        test_name = "SWT_SETUP_WARNv1"
        expected_test_exe_flow_list = [
            "TEST: executing my_setup_warn from setup_custom",
            "TEST: executing {}".format(test_name),
            "TEST: executing my_teardown from setup_custom"
        ]
        expected_verdict = ["[INCONCLUSIVE]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(test_case_report, expected_test_exe_flow_list, expected_verdict)

    def test_no_err_in_custom_setup_exe_flow(self):
        """
        Test for execution flow check for a normal test with no assertion raised in @custom_setup call
        """
        test_name = "SWT_SETUP_PASSv1"
        expected_test_exe_flow_list = [
            "TEST: executing my_setup_pass from setup_custom",
            "TEST: executing {}".format(test_name),
            "TEST: executing my_teardown from setup_custom"
        ]
        expected_verdict = ["[PASSED]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(test_case_report, expected_test_exe_flow_list, expected_verdict)

    def test_no_teardown_in_custom_setup_exe_flow(self):
        """
        Test for execution flow check for a normal test with no assertion raised in @custom_setup call without custom
        teardown call
        """
        test_name = "SWT_SETUP_PASS_WO_TEARDOWNv1"
        expected_test_exe_flow_list = [
            "TEST: executing my_setup_pass from setup_custom",
            "TEST: executing {}".format(test_name),
            "TEST: executing standard teardown from setup_custom"
        ]
        expected_verdict = ["[PASSED]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(test_case_report, expected_test_exe_flow_list, expected_verdict)

    def test_custom_setup_call_with_pass_and_expects_in_test(self):
        """
        Test for execution flow check for a normal test with expects raised and @custom_setup call
        """
        test_name = "SWT_EXPECTSv1"
        expected_test_exe_flow_list = [
            "TEST: executing my_setup_pass from setup_custom",
            "TEST: executing {}".format(test_name),
            "TEST: continue executing {}".format(test_name),
            "TEST: executing my_teardown from setup_custom",
        ]
        expected_verdict = ["[FAILED]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(test_case_report, expected_test_exe_flow_list, expected_verdict)

    def test_param_assert_in_custom_setup(self):
        """
        Test for execution flow check for a param test with assertion raised in @custom_setup call
        """
        param_test_name_0 = "SWT_PARAM_SETUP_ASSERTv1(index 0)"
        param_test_name_1 = "SWT_PARAM_SETUP_ASSERTv1(index 1)"
        expected_test_exe_flow_list = [
            "TEST: executing my_setup_fail_assert from setup_custom",
            "TEST: executing my_teardown from setup_custom",
        ]
        expected_verdict = ["[FAILED]"]
        test_case_report_0 = os.path.join(self.reports_dir, '{}.txt'.format(param_test_name_0))
        test_case_report_1 = os.path.join(self.reports_dir, '{}.txt'.format(param_test_name_1))
        self.extract_content_from_report(test_case_report_0, expected_test_exe_flow_list, expected_verdict)
        self.extract_content_from_report(test_case_report_1, expected_test_exe_flow_list, expected_verdict)

    def test_param_assert_in_custom_setup_wo_teardown(self):
        """
        Test for execution flow check for a param test with assertion raised in @custom_setup call without custom
        teardown call
        """
        param_test_name_0 = "SWT_PARAM_SETUP_ASSERT_WO_TEARDOWNv1(index 0)"
        param_test_name_1 = "SWT_PARAM_SETUP_ASSERT_WO_TEARDOWNv1(index 1)"
        expected_test_exe_flow_list = [
            "TEST: executing my_setup_fail_assert from setup_custom",
            "TEST: executing standard teardown from setup_custom",
        ]
        expected_verdict = ["[FAILED]"]
        test_case_report_0 = os.path.join(self.reports_dir, '{}.txt'.format(param_test_name_0))
        test_case_report_1 = os.path.join(self.reports_dir, '{}.txt'.format(param_test_name_1))
        self.extract_content_from_report(test_case_report_0, expected_test_exe_flow_list, expected_verdict)
        self.extract_content_from_report(test_case_report_1, expected_test_exe_flow_list, expected_verdict)

    def test_normal_param_wo_custom_setup(self):
        """
        Test for execution flow check for a normal param test with no assertion raised without @custom_setup call
        """
        test_name = "SWT_NORMAL_PARAM_TEST_1v1"
        param_test_name_0 = "{}(index hello)".format(test_name)
        param_test_name_1 = "{}(index abc)".format(test_name)
        expected_test_exe_flow_list = [
            "TEST: executing standard setup from setup_custom",
            "TEST: executing {}".format(test_name),
            "TEST: executing standard teardown from setup_custom",
        ]
        expected_verdict_0 = ["[FAILED]"]
        expected_verdict_1 = ["[PASSED]"]
        test_case_report_0 = os.path.join(self.reports_dir, '{}.txt'.format(param_test_name_0))
        test_case_report_1 = os.path.join(self.reports_dir, '{}.txt'.format(param_test_name_1))
        self.extract_content_from_report(test_case_report_0, expected_test_exe_flow_list, expected_verdict_0)
        self.extract_content_from_report(test_case_report_1, expected_test_exe_flow_list, expected_verdict_1)

    def test_normal_test_pass_wo_custom_setup(self):
        """
        Test for execution flow check for a normal test with no assertion raised without @custom_setup call
        """
        test_name = "SWT_NORMAL_TEST_PASSv1"
        expected_test_exe_flow_list = [
            "TEST: executing standard setup from setup_custom",
            "TEST: executing {}".format(test_name),
            "TEST: executing standard teardown from setup_custom",
        ]
        expected_verdict = ["[PASSED]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(test_case_report, expected_test_exe_flow_list, expected_verdict)

    def test_normal_test_fail_wo_custom_setup(self):
        """
        Test for execution flow check for a normal test with assertion raised without @custom_setup call
        """
        test_name = "SWT_NORMAL_TEST_FAILv1"
        expected_test_exe_flow_list = [
            "TEST: executing standard setup from setup_custom",
            "TEST: executing {}".format(test_name),
            "TEST: executing standard teardown from setup_custom",
        ]
        expected_verdict = ["[FAILED]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(test_case_report, expected_test_exe_flow_list, expected_verdict)

    def test_normal_test_warn_wo_custom_setup(self):
        """
        Test for execution flow check for a normal test with warning logged without @custom_setup call
        """
        test_name = "SWT_NORMAL_WARNv1"
        expected_test_exe_flow_list = [
            "TEST: executing standard setup from setup_custom",
            "TEST: executing {}".format(test_name),
            "TEST: executing standard teardown from setup_custom",
        ]
        expected_verdict = ["[INCONCLUSIVE]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(test_case_report, expected_test_exe_flow_list, expected_verdict)

    def test_global_teardown_call(self):
        """
        Method for verifying the correct global_teardown function call
        """
        test_name = "global_teardown"
        expected_test_exe_flow_list = ["TEST: executing standard global_teardown from setup_custom"]
        expected_verdict = ["[PASSED]"]
        test_case_report = os.path.join(self.reports_dir, '{}.txt'.format(test_name))
        self.extract_content_from_report(test_case_report, expected_test_exe_flow_list, expected_verdict)

    @classmethod
    def tearDownClass(cls):
        """
        Terminates or deletes the open files and folders after running tests
        """
        # delete all report folders
        folders = glob.iglob(os.path.join(SCRIPT_DIR, 'reports_custom_setup'))
        for folder in folders:
            if os.path.isdir(folder):
                shutil.rmtree(folder)


if __name__ == '__main__':
    unittest.main(verbosity=2)
