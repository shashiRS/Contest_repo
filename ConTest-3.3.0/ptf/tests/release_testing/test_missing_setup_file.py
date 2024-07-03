"""
    Copyright 2023 Continental Corporation

    :file: test_missing_setup_file.py
    :platform: Windows, Linux
    :synopsis:
        Script containing test to check the use-case when setup.pytest file is missing

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


class TestMissingSetup(unittest.TestCase):
    """ Test Class containing test to check the use-case when setup.pytest file is missing in auto mode '-r auto'"""
    paths_dir = {
        'cfg': os.path.join(SCRIPT_DIR, 'missing_setup', 'missing_setup.ini'),
        'main': os.path.join(REPO_ROOT_DIR, 'main.py')
    }
    report_dir_name = os.path.join(SCRIPT_DIR, "missing_setup", "reports")
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
        self.assertListEqual(expected_test_flow, test_exe_flow_list, "Problem in test case execution flow")
        self.assertListEqual(expected_result, actual_verdict, "Problem in test case verdict verification")

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
            '-l', os.path.join(SCRIPT_DIR, 'missing_setup')]
        # Run the ConTest application with given config file
        cls.test_exec = subprocess.run(run_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=set_shell)
        # If general error occurred during Contest gui execution, raise error
        if cls.test_exec.returncode == GENERAL_ERR:
            raise RuntimeError(
                "Error in setUpClass for cmd '{}':\n{}".format(
                    run_cmd, (cls.test_exec.stdout + cls.test_exec.stdout).decode("utf-8")))
        # get current reports folder directory path which is created
        cls.report_folder_path = max(glob.glob(os.path.join(cls.report_dir_name, 'reports_*/')), key=os.path.getmtime)
        cls.txt_reports_dir = os.path.join(cls.report_folder_path, 'contest__txt_reports')
        cls.html_reports_dir = os.path.join(cls.report_folder_path, 'contest__html_reports')

    def test_setup_pytest_non_existence(self):
        """
        Test for verifying the non-existence of setup.pytest file
        """
        self.assertTrue(
            not os.path.exists(os.path.join(SCRIPT_DIR, 'missing_setup', 'setup.pytest')),
            "'setup.pytest' file exists in base location")

    def test_global_setup_non_existence(self):
        """
        Test for verifying the non-existence or non-execution of 'global_setup' function
        """
        test_name = "global_setup"
        test_case_txt_report = os.path.join(self.txt_reports_dir, '{}.txt'.format(test_name))
        test_case_html_report = os.path.join(self.html_reports_dir, '{}.html'.format(test_name))
        self.assertTrue(
            not os.path.exists(test_case_txt_report),
            "'{}' text report is generated although setup.pytest file is missing".format(test_name))
        self.assertTrue(
            not os.path.exists(test_case_html_report),
            "'{}' html report is generated although setup.pytest file is missing".format(test_name))

    def test_global_teardown_non_existence(self):
        """
        Test for verifying the non-existence or non-execution of 'global_teardown' function
        """
        test_name = "global_teardown"
        test_case_txt_report = os.path.join(self.txt_reports_dir, '{}.txt'.format(test_name))
        test_case_html_report = os.path.join(self.html_reports_dir, '{}.html'.format(test_name))
        self.assertTrue(
            not os.path.exists(test_case_txt_report),
            "'{}' text report is generated although setup.pytest file is missing".format(test_name))
        self.assertTrue(
            not os.path.exists(test_case_html_report),
            "'{}' html report is generated although setup.pytest file is missing".format(test_name))

    def test_sample_test_execution(self):
        """
        Test for verifying the proper execution of sample test case without setup.pytest file existence
        """
        test_name = "SWT_SAMPLE_TESTv1"
        test_case_txt_report = os.path.join(self.txt_reports_dir, '{}.txt'.format(test_name))
        test_case_html_report = os.path.join(self.html_reports_dir, '{}.html'.format(test_name))
        self.assertTrue(os.path.exists(test_case_txt_report), "'{}' text report is not generated".format(test_name))
        self.assertTrue(os.path.exists(test_case_html_report), "'{}' html report is not generated".format(test_name))
        expected_test_exe_flow_list = ["TEST: Hello World from missing setup release test"]
        expected_verdict = ["[PASSED]"]
        self.extract_content_from_report(test_case_txt_report, expected_test_exe_flow_list, expected_verdict)

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
