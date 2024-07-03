"""
Unittest file for report
Copyright 2018 Continental Corporation

:file: test_report.py
:platform: Unix, Windows
:synopsis: File containing Unittest for report. For testing the function of report
    with 100% coverage
:author: Christopher Mirajkar <Christopher.Charles.Mirajkar@continental-corporation.com>
"""

import sys
import os
import unittest
import re

# Adding path of the modules used in ptf_asserts to system path for running the test externally
try:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    sys.path.append(os.path.join(BASE_DIR, 'ptf_utils'))
    from ptf.ptf_utils import report
    from ptf.ptf_utils.test_watcher import TestCaseInfo, CURRENT_TESTCASE
finally:
    pass


class TestReport(unittest.TestCase):
    """ A class for testing the proper working of report.py """

    def setUp(self):
        """
        Initialize report class for proper testing
        """
        verifies_id = []
        automates_id = []
        tags = []
        test_type = ""
        self.current_tc = TestCaseInfo(
            "DummyTest", self.setUp, verifies_id, automates_id, tags, test_type)

    def test_details(self):
        """ Method for testing the functionality of report.DETAILS"""
        expected_output = ['This is a unittest']
        # Call the method
        report.DETAILS("This is a unittest")
        self.assertEqual(
            CURRENT_TESTCASE[0].details,
            expected_output,
            "TEST_DETAILS does not match the argument passed")

    def test_testcase(self):
        """ Method for testing the functionality of report.TESTCASE"""
        self.assertEqual(
            report.TESTCASE(),
            None,
            "Method was not called properly")

    def test_teststep(self):
        """ Method for testing the functionality of report.TESTSTEP"""
        # Changed expected string to cater timestamp values which will be different
        expected_output = r' Test Step-\d\d:\d\d:\d\d.\d\d\d\d\d\d: This is a test step in unittest'
        # Call the method
        report.TESTSTEP("This is a test step in unittest")
        result = True if re.match(expected_output, CURRENT_TESTCASE[0].steps[0]) else False
        self.assertTrue(result, "'Test Step' string is not as expected")

    def test_expected(self):
        """ Method for testing the functionality of report.EXPECTED"""
        # Changed expected string to cater timestamp values which will be different
        expected_output = r' Expected-\d\d:\d\d:\d\d.\d\d\d\d\d\d: ' \
                          'This is the test step description in unittest'
        # Call the method
        report.EXPECTED("This is the test step description in unittest")
        result = True if re.match(expected_output, CURRENT_TESTCASE[0].steps[0]) else False
        self.assertTrue(result, "'Expected' string is not as expected")

    def test_verifies(self):
        """ Method for testing the functionality of report.VERIFIES"""
        expected_output = ['This is the test step Requirement/ID in unittest']
        # Call the method
        report.VERIFIES("This is the test step Requirement/ID in unittest")
        self.assertEqual(
            CURRENT_TESTCASE[0].verified_ids,
            expected_output,
            "TEST_VERIFIED_IDS does not match the argument passed")

        with self.assertRaises(Exception) as error:
            report.VERIFIES("")
        self.assertEqual(
            "Cannot add empty requirement",
            str(error.exception),
            "Exception raised do not match with actual")

    def test_automates(self):
        """ Method for testing the functionality of report.AUTOMATES"""
        expected_output = ['ID_1']
        # Call the method
        report.AUTOMATES("ID_1")
        self.assertEqual(
            CURRENT_TESTCASE[0].automates,
            expected_output,
            "TEST_AUTOMATES_IDS does not match the argument passed")

    def test_testtag(self):
        """ Method for testing the functionality of report.TESTTAG"""
        expected_output = ['This is the tag line in unittest']
        # Call the method
        report.TESTTAG("This is the tag line in unittest")
        self.assertEqual(
            CURRENT_TESTCASE[0].tags,
            expected_output,
            "TEST_TAGS does not match the argument passed")

        with self.assertRaises(Exception) as error:
            report.TESTTAG("")
        self.assertEqual(
            "Cannot add empty tag",
            str(error.exception),
            "Exception raised do not match with actual")


if __name__ == '__main__':
    unittest.main(verbosity=2)
