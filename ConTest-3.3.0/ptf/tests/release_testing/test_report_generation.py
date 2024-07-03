"""
    Copyright 2019 Continental Corporation

    :file: test_report_generation.py
    :platform: Windows, Linux
    :synopsis:
        File containing release test. Checking if the reports are generated as expected
    :author:
        - Christopher Mirajkar <Christopher.Charles.Mirajkar@continental-corporation.com>
"""
import os
import sys
import unittest
import json
import subprocess
import shutil
import glob
from lxml import etree

try:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
    sys.path.append(os.path.abspath(os.path.join(BASE_DIR, '..')))
    from ptf.tests.release_testing import format_helper
    from global_vars import GENERAL_ERR
finally:
    pass


class TestReportGeneration(unittest.TestCase):
    """ Test Class for checking test report generation"""

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
            ['python', cls.app_run_dict['contest_app'], '-c', cls.app_run_dict['config_file'],
             '-r', 'auto', '-l', os.path.join(SCRIPT_DIR, 'sample_test')], stderr=subprocess.PIPE,
            stdout=subprocess.PIPE, shell=set_shell)
        # If general error occurred
        if cls.test_exec.returncode:
            cls.test_exec_again = subprocess.run(
                ['python', cls.app_run_dict['contest_app'], '-c', cls.app_run_dict['config_file'],
                 '-r', 'auto', '-l', os.path.join(SCRIPT_DIR, 'sample_test')],
                stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=set_shell)
            # If general error occurred during Contest gui execution, raise error
            if cls.test_exec_again.returncode == GENERAL_ERR:
                raise RuntimeError(
                    "ERROR OCCURRED WHILE RUNNING CONTEST APPLICATION IN setUpClass:\n{}".format(
                        (cls.test_exec.stdout + cls.test_exec_again.stdout).decode("utf-8")))
        # get current reports folder directory path which is created
        cls.new_report_folder_path = max(glob.glob(os.path.join(SCRIPT_DIR, 'sample_test', 'reports_*/')),
                                         key=os.path.getmtime)

    def test_verify_json_report_template(self):
        """
        Method to check if json report matches the desired template
        """
        ref_dict_list = []
        report_dict_list = []
        # keys which don't need to be compared because they contain varying information
        # e.g. timestamps
        differing_keys = {"Runtime", "test_duration", "test_date", "test_execution"}

        test_result_json_report = os.path.join(self.new_report_folder_path, 'contest__txt_reports',
                                               'TEST_RESULT.json')
        # reading the json report to a variable
        with open(test_result_json_report, 'r') as file:
            data = json.load(file)

        # Saving values from keys 'summary' and 'tests' of json report to a list.
        # Here nested dictionaries are captured to single list of dictionaries.
        for value in data.values():
            if not isinstance(value, list):
                report_dict_list.append(value)
            else:
                for dct in value:
                    report_dict_list.append(dct)

        # Saving values from keys 'summary' and 'tests' of reference json template to a list.
        # Here nested dictionaries are captured to single list of dictionaries.
        for ref_key, ref_value in format_helper.JSON_TEMPLATE.items():
            # checking for keys 'summary' and 'tests'
            self.assertIn(ref_key, data.keys(), ref_key + " key is missing!")
            if not isinstance(ref_value, list):
                ref_dict_list.append(ref_value)
            else:
                for dct in ref_value:
                    ref_dict_list.append(dct)

        # Comparing json data to the reference template
        for dict_1, dict_2 in zip(report_dict_list, ref_dict_list):
            if isinstance(dict_1, dict) and isinstance(dict_2, dict):
                # Checking if keys of reference template are present in json report before
                # filtering the differing keys(or values)
                self.assertEqual(dict_1.keys(), dict_2.keys(), str(dict_2.keys()) + " is missing!")
                # Filtering the values that are ignored
                d1_filtered = dict((k, v) for k, v in dict_1.items() if k not in differing_keys)
                d2_filtered = dict((k, v) for k, v in dict_2.items() if k not in differing_keys)
                # Checking if filtered dictionaries are equal
                self.assertDictEqual(d1_filtered, d2_filtered,
                                     "Reference format do not match with Actual JSON report data!")
            else:
                self.assertEqual(dict_1, dict_2, str(dict_2) + " is missing!")

    def test_verify_txt_report_global_setup(self):
        """
        Method for checking if global_setup txt report has the desired texts
        """
        text_report = format_helper.SETUP_TXT_TEMPLATE.split('\n')

        setup_txt_report = os.path.join(self.new_report_folder_path, 'contest__txt_reports',
                                        'global_setup.txt')
        with open(setup_txt_report) as file:
            data = file.read()
        for word in text_report:
            self.assertIn(word, data, word + " is missing in the report")

    def test_verify_txt_report_global_teardown(self):
        """
        Method for checking if global_teardown txt report has the desired texts
        """
        text_report = format_helper.TEAR_DOWN_TXT_TEMPLATE.split('\n')
        tear_down_txt_report = os.path.join(self.new_report_folder_path, 'contest__txt_reports',
                                            'global_teardown.txt')
        with open(tear_down_txt_report) as file:
            data = file.read()
        for word in text_report:
            self.assertIn(word, data, word + " is missing in the report")

    def test_verify_txt_report_testcase(self):
        """
        Method for checking if test-case txt report has the desired texts
        """
        test_pass = format_helper.TEST_CASE_PASS_TXT_TEMPLATE.split('\n')
        test_fail = format_helper.TEST_CASE_FAIL_TXT_TEMPLATE.split('\n')

        test_case_pass_txt_report = os.path.join(
            self.new_report_folder_path, 'contest__txt_reports',
            format_helper.REPORT_TEST_CASE_NAME_PASS + '.txt')
        test_case_fail_txt_report = os.path.join(
            self.new_report_folder_path, 'contest__txt_reports',
            format_helper.REPORT_TEST_CASE_NAME_FAIL + '.txt')
        with open(test_case_pass_txt_report) as file:
            data_pass = file.read()
        for word in test_pass:
            self.assertIn(word, data_pass, word + " is missing in the report")

        with open(test_case_fail_txt_report) as file:
            data_fail = file.read()
        for word in test_fail:
            self.assertIn(word, data_fail, word + " is missing in the report")

    def test_verify_txt_report_summary(self):
        """
        Method for checking if tests summary txt report has the desired texts
        """
        text_report = format_helper.SUMMARY_TXT_TEMPLATE.split('\n')
        summary_txt_report = os.path.join(self.new_report_folder_path, 'contest__txt_reports',
                                          'TESTS_SUMMARY.txt')
        with open(summary_txt_report) as file:
            data = file.read()
        for word in text_report:
            self.assertIn(word, data, word + " is missing in the report")

    # pylint: disable=c-extension-no-member
    def test_verify_xml_report(self):
        """
        Method for checking if generated xml report is as per desired XML Schema
        """
        xml_content = [format_helper.SETUP_TXT_TEMPLATE.split('\n'),
                       format_helper.TEAR_DOWN_TXT_TEMPLATE.split('\n'),
                       format_helper.TEST_CASE_PASS_TXT_TEMPLATE.split('\n'),
                       format_helper.TEST_CASE_FAIL_TXT_TEMPLATE.split('\n')]

        test_result_xml_report = os.path.join(self.new_report_folder_path, 'contest__txt_reports',
                                              'TEST_RESULT.xml')
        # parse XML report(file object) to ElementTree object
        xml_doc = etree.parse(test_result_xml_report)
        # parse XML schema(file object) to ElementTree object
        xmlschema_doc = etree.parse(format_helper.XSD_FILE_OBJECT)
        # turn ElementTree document into an XML Schema validator
        xmlschema = etree.XMLSchema(xmlschema_doc)

        # Validate the generated report template
        self.assertTrue(xmlschema.validate(xml_doc), "The generated XML report does not match with"
                                                     " the schema")

        # Look in for the content of the report
        with open(test_result_xml_report) as file:
            data = file.read()
        for content in xml_content:
            for word in content:
                self.assertIn(word, data, word + " is missing in the report")

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
