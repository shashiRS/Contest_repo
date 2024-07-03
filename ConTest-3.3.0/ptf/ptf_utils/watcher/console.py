"""
    Module to report to console output.
    Copyright 2019 Continental Corporation

    This module contains a watcher to print the output to the console.

    :file: console.py
    :author:
        - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""

# standard Python imports
import sys
import time
import traceback
import socket

# custom imports
from contest_verify.verify import contest_asserts, contest_expects
from ptf.ptf_utils.test_watcher import TestWatcher
from ptf.ptf_utils.common import _get_user
from global_vars import TEST_ENVIRONMENT, TestVerdicts


class ConsoleReporter(TestWatcher):
    """
    Watcher implementation that will print status notifications on the console.
    """

    def __init__(self):
        """
        Initializes the console information.
        """
        self.passed_tests = []
        self.failing_tests = []
        self.ignored_tests = []
        self.inconclusive_tests = []
        self.start_time = None
        self.end_time = None
        self.skipped_tests = []

    def test_started(self, testcase):
        """
        Prints notification that test started.

        :param TestCaseInfo testcase: The testcase that started.
        """
        # pylint: disable=C0209
        print("\n{0}\n".format(" begin {0} ".format(testcase.name).center(79, "=")))

    def test_succeeded(self, testcase):
        """
        Add test name to passed test list.

        :param TestCaseInfo testcase: The successful testcase
        """
        # this statement is to ignore the abstract or generic parameterized test case since the
        # abstract test case is not need to be marked as passed as it runs with params
        if testcase.test_function.__name__ == "parameterized_runner":
            return
        self.passed_tests.append(testcase.name)

    def test_inconclusive(self, testcase):
        """
        Add test to inconclusive test list

        :param TestCaseInfo testcase: The testcase in which warning is logged
        """
        if testcase.test_function.__name__ == "parameterized_runner":
            return
        self.inconclusive_tests.append(testcase.name)

    def test_failed(self, testcase):
        """
        Add test to failed test list. Also print error depending on type.

        :param TestCaseInfo testcase: The failed testcase.
        """
        # this statement is to ignore the abstract or generic parameterized test case since the
        # abstract test case is not need to be marked as failed as it runs with params
        if testcase.test_function.__name__ == "parameterized_runner":
            return
        self.failing_tests.append(testcase.name)
        error = testcase.failure_info
        # here detecting if test case is parameterized since index will be an int value set in
        # parameterized.py-->parameterized class--> __execute_test method
        # then we don't need to do failure prints since it will be done in __execute_test method
        # itself
        if testcase.index is None:
            if isinstance(error, contest_asserts.ConTestAssertCompareError):
                # protected-access is ok here
                # pylint: disable=W0212
                contest_asserts._print_exception_info(error)
            elif isinstance(error, contest_expects.ConTestExpectError):
                print("\n--> ERROR: Expectation(s)")
                print("--> Failure(s) : ", error)
            else:
                traceback.print_exc(file=sys.stdout)

    def test_skip(self, testcase):
        """
        Add test to skipped test list

        :param TestCaseInfo testcase: The testcase in which warning is skipped
        """
        if testcase.test_function.__name__ == "parameterized_runner":
            return
        self.skipped_tests.append(testcase.name)

    def test_finished(self, testcase):
        """
        Prints some information about finished testcase.

        :param TestCaseInfo testcase: The finished testcase.
        """
        # pylint: disable=C0209
        print("\nExecuted in {} msec".format(testcase.run_time * 1000))
        if testcase.verdict == TestVerdicts.PASS:
            print("[PASSED]")
        elif testcase.verdict == TestVerdicts.INCONCLUSIVE:
            print("[INCONCLUSIVE]")
        elif testcase.verdict == TestVerdicts.FAIL:
            print("[FAILED]")
        elif testcase.verdict == TestVerdicts.SKIP:
            print("[SKIPPED]")
        # pylint: disable=C0209
        print("\n{0}\n".format(" end {0} ".format(testcase.name).center(79, "=")))

    def test_run_started(self, test_cases):
        """
        Prints some information about a started testrun.

        :param list test_cases: The testcases to be executed.
        """
        # todo uncomment after fixing parameterized tests count
        # print("\n[Total Number of Test Cases ] : {0}".format(len(test_cases)))
        self.start_time = time.time()

    def test_run_finished(self, missing_tests):
        """
        Prints some information about the finished testrun.

        :param list missing_tests: A list of testcases that where configured to be executed, but
                                   where not found during execution
        """
        print("\n==================== TEST REPORT LOG ======================")
        print(
            "[Total Tests]        : "
            + str(
                len(self.passed_tests)
                + len(self.failing_tests)
                + len(self.ignored_tests)
                + len(self.inconclusive_tests)
                + len(self.skipped_tests)
            )
        )
        print(
            "[Running Tests]      : "
            + str(
                len(self.passed_tests)
                + len(self.failing_tests)
                + len(self.inconclusive_tests)
                + len(self.skipped_tests)
            )
        )
        print("[Passed Tests]       : " + str(len(self.passed_tests)))
        print("[Inconclusive Tests] : " + str(len(self.inconclusive_tests)))
        print("[Skipped Tests]      : " + str(len(self.skipped_tests)))
        print("[Failed Tests]       : " + str(len(self.failing_tests)))
        print("[Ignored Tests]      : " + str(len(self.ignored_tests)))
        print("[Missing Tests]      : " + str(len(missing_tests)))
        print("[Machine Name]       : " + socket.gethostname())
        print("[User Name]          : " + _get_user())
        if self.passed_tests:
            print("\n[Passed Tests] :")
            for test in self.passed_tests:
                print("                 " + test)
        if self.inconclusive_tests:
            print("\n[Inconclusive Tests] :")
            for test in self.inconclusive_tests:
                print("                 " + test)
        if self.skipped_tests:
            print("\n[Skipped Tests] :")
            for test in self.skipped_tests:
                print("                 " + test)
        if self.failing_tests:
            print("\n[Failing Tests] :")
            for test in self.failing_tests:
                print("                 " + test)
        if self.ignored_tests:
            print("\n[Ignored Tests] :")
            for test in self.ignored_tests:
                print("                 " + test)
        if missing_tests:
            print("\n[Missing Tests] : ")
            for test in missing_tests:
                print("                 " + test)
        execution_time = (time.time() - self.start_time) / 60
        print("\n[Execution Time]  : " + str(execution_time) + " mins\n")
        print("[TimeStamp]  : " + time.strftime("%c") + "\n")
        print("[TestEnvironment] : " + TEST_ENVIRONMENT)
        print("============================================================\n")
