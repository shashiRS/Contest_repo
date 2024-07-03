"""
    File containing template for PTF test suite
    Copyright 2018 Continental Corporation

    :file: test_template.py
    :platform: Windows, Linux
    :synopsis:
        This file contains templates for files which can be created at the time of configuration
        creation.

    :author:
        - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
"""

import time


PYTEST_STARTER = """\"""
    Copyright {} Continental Corporation

    :file: swt_<what_ever>.pytest
    :platform: Windows, Linux
    :synopsis:
        <fill_details>

    :author:
        - <your_name>
\"""

# standard Python import area


# ConTest or custom import area
# NOTE : ALWAYS IMPORT (contest_expects, contest_asserts, contest_warn, report and get_parameter) AS BELOW.
#        FOR PROPER DOCUMENTATION AND ERROR REPORTING
from contest_verify.verify import contest_asserts
from contest_verify.verify import contest_expects
from contest_verify.verify import contest_warn
from ptf.ptf_utils.report import *
from ptf.ptf_utils.global_params import get_parameter


""".format(time.strftime("%Y"))

# template for setup.pytest file
SETUP_PYTEST = """\"""
    Copyright {} Continental Corporation

    This file contains up to four methods that will be called by the test framework:
        - global_setup(): Will be called before ALL test-cases
        - setup(): Will be called before EACH test-case
        - teardown(): Will be called after EACH test-case. Will also be called if test-case fails.
        - global_teardown(): Will be called after ALL test-cases.
                             Will be called if any execution before fails.

    :file: setup.pytest

    :author:
        - <your_name>
\"""

# standard Python import area


# ConTest or custom import area
# NOTE : ALWAYS IMPORT (contest_expects, contest_asserts, contest_warn, report and get_parameter) AS BELOW.
#        FOR PROPER DOCUMENTATION AND ERROR REPORTING
from contest_verify.verify import contest_asserts
from contest_verify.verify import contest_expects
from contest_verify.verify import contest_warn
from ptf.ptf_utils.global_params import *


def global_setup():
    \"""
    This method will be called before ALL test-cases are executed.

    You can set global variables with :func:`set_global_parameter`.
    Will skip execution of tests if this method fails.
    \"""
    pass


def global_teardown():
    \"""
    This method will be called after ALL test-cases are executed.

    You can access global variables with :func:`get_parameter`.
    Guaranteed to be called, even if any test or global setup fails.
    \"""
    pass


def setup():
    \"""
    This method will be called before EACH test-case is executed.

    You can set local variables just available for the next test-case
    using :func:`set_local_parameter`.

    You can access global variables with :func:`get_parameter`.

    Will skip execution of test if this method fails.
    Skipped if global setup fails.
    \"""
    pass


def teardown():
    \"""
    This method will be called after EACH testcase is executed.

    You can access global variables with :func:`get_parameter`.

    Guaranteed to be called, even if the test or setup fails.
    Skipped if global setup fails.
    \"""
    pass

""".format(time.strftime("%Y"))


# template for a sample test file
SAMPLE_TEST_FILE = PYTEST_STARTER + """
def SWT_SAMPLE_TESTv1():
    DETAILS("Fill With Details")
    DETAILS("Fill With Details")

    PRECONDITION("Fill in precondition")

    VERIFIES("Mention requirement satisfied by this test case")

    TESTTAG("sil")
    TESTTAG("hil")
    TESTTAG("integration")
    TESTTAG("blackbox")

    TESTSTEP("Mention test step")
    EXPECTED("Mention expectation of test step")
    # You can access global variables created in setup.pytest file with :func:`get_parameter`.
    print("Hello World!")

"""

# readme file text
READ_ME = "This is the location where test cases can be written.\n" \
          "Following is some important information:\n\n" \
          " 1. setup.pytest file contains setup and teardown function for setting up your test" \
          " cases\n" \
          " 2. A sample test file has been created 'swt_sample_test.pytest'\n" \
          " 3. In this folder you can create many swt_<what_ever>.pytest files also in "\
          "sub-folders\n"\
          " 4. You can create .py files and import them as normal scripts in .pytest files\n" \
          " 5. Read ConTest documentation 'GUI->Help->User Manual' for detail information\n"
