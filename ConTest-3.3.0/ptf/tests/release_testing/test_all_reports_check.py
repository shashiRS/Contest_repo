"""
    Copyright 2022 Continental Corporation

    :file: test_all_reports_check.py
    :platform: Windows, Linux
    :synopsis:
        File containing release test. Checking if all the reports are generated
    :author:
        - Vanama Ravi Kumar <ravi.kumar.vanama@continental-corporation.com>
"""
import os
import sys
import unittest
import subprocess
import shutil
import glob

try:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
    sys.path.append(os.path.abspath(os.path.join(BASE_DIR, '..')))
    from global_vars import GENERAL_ERR
finally:
    pass


class TestReportCheck(unittest.TestCase):
    """ Test Class for checking that all reports are generated if there is any failure in
     global_setup / global_teardown / setup / teardown """

    @classmethod
    def setUpClass(cls):
        """
        Initialize the class with variables, objects etc., for testing
        """
        cls.new_report_folder_path = None

        cls.app_run_dict = {
            'config_file': os.path.join(SCRIPT_DIR, 'PTF_Config_report_gen.ini'),
            'contest_app': os.path.join(SCRIPT_DIR, '..', '..', '..', 'main.py')
        }

        if sys.platform == "linux":
            set_shell = False
        else:
            set_shell = True
        # Run the ConTest application with given config file
        cls.test_exec = subprocess.run(
            ['python3', cls.app_run_dict['contest_app'], '-c', cls.app_run_dict['config_file'],
             '-r', 'auto', '-l', os.path.join(SCRIPT_DIR, 'sample_test'), '--setup-file',
             os.path.join(SCRIPT_DIR, 'sample_test', 'setup_report_test.pytest')],
            stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=set_shell)
        # If general error occurred
        if cls.test_exec.returncode:
            cls.test_exec_again = subprocess.run(
                ['python', cls.app_run_dict['contest_app'], '-c', cls.app_run_dict['config_file'],
                 '-r', 'auto', '-l', os.path.join(SCRIPT_DIR, 'sample_test'), '--setup-file',
                 os.path.join(SCRIPT_DIR, 'sample_test', 'setup_report_test.pytest')],
                stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=set_shell)
            # If general error occurred during Contest gui execution, raise error
            if cls.test_exec_again.returncode == GENERAL_ERR:
                raise RuntimeError(
                    "ERROR OCCURRED WHILE RUNNING CONTEST APPLICATION IN setUpClass:\n{}".format(
                        (cls.test_exec.stdout + cls.test_exec_again.stdout).decode("utf-8")))
        # get current reports folder directory path which is created
        cls.new_report_folder_path = max(glob.glob(os.path.join(SCRIPT_DIR, 'sample_test',
                                                                'reports_*/')),
                                         key=os.path.getmtime)

    def test_check_all_reports_generated(self):
        """
        Method for checking if test reports are generated
        """
        cathat_xml_report = os.path.join(self.new_report_folder_path, 'contest__txt_reports',
                                         'CATHAT_TEST_RESULT.xml')
        test_result_json_report = os.path.join(self.new_report_folder_path, 'contest__txt_reports',
                                               'TEST_RESULT.json')
        test_result_xml_report = os.path.join(self.new_report_folder_path, 'contest__txt_reports',
                                              'TEST_RESULT.xml')
        summary_txt_report = os.path.join(self.new_report_folder_path, 'contest__txt_reports',
                                          'TESTS_SUMMARY.txt')
        global_setup_report = os.path.join(self.new_report_folder_path, 'contest__txt_reports',
                                           'global_setup.txt')
        global_teardown_report = os.path.join(self.new_report_folder_path, 'contest__txt_reports',
                                              'global_teardown.txt')
        html_report = os.path.join(self.new_report_folder_path, 'contest__html_reports',
                                   'TESTS_SUMMARY.html')
        report_paths = [cathat_xml_report, test_result_json_report, test_result_xml_report,
                        summary_txt_report, global_setup_report, global_teardown_report,
                        html_report]
        for path in report_paths:
            self.assertEqual(os.path.exists(path), True, "Missed Report Path : {}".format(path))

    @classmethod
    def tearDownClass(cls):
        """
        Terminates or deletes the open files and folders after running unittests
        """
        # delete all report folders
        folders = glob.iglob(os.path.join(SCRIPT_DIR, "sample_test", "reports_*"))
        for folder in folders:
            if os.path.isdir(folder):
                shutil.rmtree(folder)


if __name__ == '__main__':
    unittest.main(verbosity=2)
