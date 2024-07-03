"""
    Copyright 2020 Continental Corporation

    :file: test_canoe.py
    :platform: Windows
    :synopsis:
        File containing system (Integration) test implementation for verifying CANoe tool utility.
    :author:
        - Praveenkumar G K  <praveenkumar.gomathi.kaliamoorthi@continental-corporation.com>
"""
import os
import unittest as ut
import subprocess
import shutil
import glob


# Adding path of the modules used in ptf_asserts to system path for running the test externally
try:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
finally:
    pass


class TestCanoeUtility(ut.TestCase):
    """Test Class to verify canoe utility"""

    @classmethod
    def setUpClass(cls):
        # path where contest reports are stored
        cls.new_report_folder_path = None

        cls.app_run_dict = {
            'config_file': os.path.join(SCRIPT_DIR, "ConTest_Config_CANoe.ini"),
            'contest_app': os.path.join(SCRIPT_DIR, '..', '..', '..', '..', 'main.py'),
            'report': os.path.join(SCRIPT_DIR, 'report')
        }

        # Run the ConTest application with given config file
        cls.test_exec = subprocess.run(
            ['python', cls.app_run_dict['contest_app'], '-c', cls.app_run_dict['config_file'],
             '-r', 'auto', '-l', SCRIPT_DIR], stderr=subprocess.PIPE,
            stdout=subprocess.PIPE, shell=False)
        # get current reports folder directory path which is created
        cls.new_report_folder_path = max(glob.glob(os.path.join(SCRIPT_DIR, 'report',
                                                                'reports_*/')),
                                         key=os.path.getmtime)

    @classmethod
    def tearDownClass(cls):
        """
        Terminates or deletes the open files and folders after running unittests
        """
        # deletes the generated report folder
        if os.path.exists(os.path.join(cls.app_run_dict['report'])):
            shutil.rmtree(os.path.join(cls.app_run_dict['report']))

    def test_verify_canoe_report_generation(self):
        """
        Test is to verify canoe specific reports are generated in specified directory provided
        from Contest API
        """

        for name, test in [['test1', 'CANoe__Test_1.vtestreport'],
                           ['test2', 'CANoe__Test_2.vtestreport']]:
            with self.subTest(name):
                self.assertTrue(
                    os.path.exists(os.path.join(self.app_run_dict['report'], test)),
                    "Expected CANoe report not found: {}"
                    .format(os.path.join(self.app_run_dict['report'], test)))

    def test_verify_canoe_test_module_not_linked_error(self):
        """
        Test for checking whether Error is raised for not linking CAN test modules in
        CANoe test step
        """

        summary_txt_report = os.path.join(self.new_report_folder_path, 'ptf__txt_reports',
                                          'TESTS_SUMMARY.txt')
        with open(summary_txt_report) as file:
            data = file.read()
        for name, test in [['test1', "--> Failure(s) :  Test Module Script"
                                     " 'test_3.can' not linked to any Test Module"],
                           ['test2', "--> Failure(s) :  Test Module Script"
                                     " 'test_4.can' not linked to any Test Module"]]:
            with self.subTest(name):
                self.assertTrue(test in data,
                                "Error not raised as expected")


if __name__ == '__main__':
    ut.main(verbosity=2)
