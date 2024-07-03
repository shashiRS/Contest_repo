"""
    Copyright 2023 Continental Corporation

    :file: test_get_test_info.py
    :platform: Windows, Linux
    :synopsis:
        Script for tests the usecase of `get_current_test_info`
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
    from global_vars import SUCCESS
finally:
    pass


class TestGetTestInfo(unittest.TestCase):
    """ Test Class tests the usecase of `get_current_test_info` in auto mode '-r auto'"""
    paths_dir = {
        'cfg': os.path.join(REPO_ROOT_DIR, 'cfg', 'get_test_info.ini'),
        'main': os.path.join(REPO_ROOT_DIR, 'main.py')
    }
    report_dir_name = "tests_reports"

    @classmethod
    def test_verify_execution(cls):
        """
        Test to verify that all tests existing in ``ConTest/ptf/demo_tests/get_test_info/swt_sample_test.pytest``
        passing
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
            '-l', os.path.join(REPO_ROOT_DIR, 'ptf', 'demo_tests', 'get_test_info')]
        # Run the ConTest application with given config file
        cls.test_exec = subprocess.run(run_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=set_shell)
        # If general error occurred during Contest gui execution, raise error
        if cls.test_exec.returncode != SUCCESS:
            raise RuntimeError(
                "get_test_info tests are failing '{}':\n{}".format(
                    run_cmd, (cls.test_exec.stdout + cls.test_exec.stdout).decode("utf-8")))

    @classmethod
    def tearDownClass(cls):
        """
        Terminates or deletes the open files and folders after running tests
        """
        # delete all report folders
        folders = glob.iglob(os.path.join(REPO_ROOT_DIR, 'ptf', 'demo_tests', 'get_test_info', cls.report_dir_name))
        for folder in folders:
            if os.path.isdir(folder):
                shutil.rmtree(folder)


if __name__ == '__main__':
    unittest.main(verbosity=2)
