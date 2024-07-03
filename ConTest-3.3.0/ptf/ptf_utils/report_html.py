"""
:file: report_html.py

:synopsis: This file is DEPRECATED and will be removed in the future.
           Please use `report.py` instead.

:author: M. Shan Ur Rehman
        <Muhammad.Shan.ur.Rehman@continental-corporation.com>
"""

# pylint: disable=invalid-name
# We define several functions to be used within the testcases. For easier visibility, they won't fit
# the default function name pattern.

import sys

from ptf.ptf_utils import report as report

# Print a warning when this module is used
sys.stderr.write("The 'report_html' module is deprecated and will be removed in future versions.\n"
                 "Please use the 'report' module instead.\n")


def DETAILS(detail):
    """
    Deprecated. Please use `DETAILS` from `report.py` instead

    :param str detail: Description of test case
    """
    report.DETAILS(detail)


def TESTCASE():
    """
    Deprecated. Please use `TESTCASE` from `report.py` instead
    """
    report.TESTCASE()


def TESTSTEP(step):
    """
    Deprecated. Please use `TESTSTEP` from `report.py` instead

    :param str step: Description of test step
    """
    report.TESTSTEP(step)


def EXPECTED(expect):
    """
    Deprecated. Please use `EXPECTED` from `report.py` instead

    :param str expect: Description of expected result
    """
    report.EXPECTED(expect)


def VERIFIES(requirement):
    """
    Deprecated. Please use `VERIFIES` from `report.py` instead

    :param str requirement: Requirement name/ID
    """
    report.VERIFIES(requirement)


def TESTTAG(tag):
    """
    Deprecated. Please use `TESTTAG` from `report.py` instead

    :param str tag: Test methods and intended usage of test cases
    """
    report.TESTTAG(tag)


def PRECONDITION(precondition):
    """
    Function for adding precondition

    :param str precondition: Description of precondition
    """
    report.PRECONDITION(precondition)


def IMAGE(image):
    """
    Function for adding Image

    :param str image: path of the image
    """
    report.IMAGE(image)


def LINK(path_to_file):
    """
    Function for hyperlinking any files in Test Case Execution Sequence for easy navigation.

    :param str path_to_file: path to the file needs to be hyperlinked
    """
    report.LINK(path_to_file)
