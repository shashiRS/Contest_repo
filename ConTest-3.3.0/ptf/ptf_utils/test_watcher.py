"""
    This module implements the test watcher handling.
    Copyright 2019 Continental Corporation

    Test watchers allow the framework to react on different events during test execution. E.g. the
    watchers will be notified if a new testcase was started or finished, if a testcase was
    successful or not, or if a test was ignored. For a full list, which events where triggered
    please see the `TestWatcher` class.
    Usually, the test watcher will get a `TestCaseInfo` instance as parameter. This instance
    contains several runtime information about the currently executed testcase.

    For example implementations of test watchers, check the modules in the `watcher` package.

    :file: test_watcher.py
    :author:
        - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""

import sys
import time
from copy import deepcopy

from ptf.ptf_utils.global_params import _Test_Verdict, _ALL_TESTS_TO_RUN, _Test_Data_Info
from global_vars import TestVerdicts
from datetime import datetime
# global list to be shared between 'test_watcher.TestCaseInfo' class and
# 'ptf.ptf_utils.report' module functions
CURRENT_TESTCASE = [None]


class TestCaseInfo:
    """
    This class wraps the information for a single test case execution.
    It will also calculate execution time as time between object creation and call of `finished`
    function.
    Will register itself in `report` module as currently running testcase.
    """

    # This is just a data container
    # pylint: disable=too-few-public-methods

    def __init__(self, name, test_function, verified_ids, automates_id, tags, test_type, index=None,
                 user_modified_param_test=False):
        """
        Creates a new test case info instance

        :param str name: The name of the testcase
        :param function test_function: The test function that is executed
        :param list verified_ids: The list of verified ids
        :param list tags: The list of tags
        :param str test_type: The string contains test type
        :param int index: Contains index of the parameterized test cases, other wise None
        """
        self.name = name
        self.test_function = test_function
        self.start_date_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        self.stop_date_time = ""
        self.start_time = time.time()
        self.stop_time = None
        self.run_time = None
        self.verdict = TestVerdicts.UNKNOWN
        self.failure_info = None
        self.inconclusive_info = list()
        # this value will help in detecting a parameterized test as in that case it shall be 1
        self.index = index
        self.skipped = False
        self.skip_info = None
        self.test_to_be_skipped = False
        self.details = []
        self.precondition = []
        self.steps = []
        self.verified_ids = verified_ids
        self.tags = tags
        self.automates = automates_id
        self.testcase_id = list()
        # type of the test case (capl, cmm, python)
        self.test_type = test_type
        # CANoe Test Module Test Case Verdicts for reporting
        self.canoe_tm_tc_verdicts = list()
        # flag for detecting if a param test case was modified by user via gui (added a new set or modified set values)
        self.user_modified_param_test = user_modified_param_test
        # reassigning the value for every new test case
        CURRENT_TESTCASE[0] = self

    def finished(self):
        """
        Will mark the testcase as finished
        """
        self.stop_time = time.time()
        self.stop_date_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        self.run_time = self.stop_time - self.start_time


class TestWatcher:
    """
    Base class for new watchers. Contains all functions that can be called by the watcher runner.
    Every watcher should overwrite the functions for the events that need to be handled by the
    watcher.
    """

    def write(self, *args, **kwargs):
        """
        Triggered if some information is written to stdout.

        :param args: The arguments to write
        :param kwargs: The keyword arguments to write
        """
        # This is just a dummy implementation
        # pylint: disable=unnecessary-pass
        pass

    def flush(self, *args, **kwargs):
        """
        Triggered when the stdout stream is flushed.

        :param args: Optional arguments
        :param kwargs: Optional keyword arguments
        """
        # This is just a dummy implementation
        # pylint: disable=unnecessary-pass
        pass

    def test_run_started(self, test_cases):
        """
        Triggered when a new testrun has started.

        :param list test_cases: A list of testcases to be executed in the following run
        """
        # This is just a dummy implementation
        # pylint: disable=unnecessary-pass
        pass

    def test_run_finished(self, missing_tests):
        """
        Triggered when a testrun has finished.

        :param list missing_tests: A list of testcases that where configured to be executed, but
                                   where not found during execution
        """
        # This is just a dummy implementation
        # pylint: disable=unnecessary-pass
        pass

    def test_started(self, testcase):
        """
        Triggered when a testcase has started

        :param TestCaseInfo testcase: The testcase that has started
        """
        # This is just a dummy implementation
        # pylint: disable=unnecessary-pass
        pass

    def test_succeeded(self, testcase):
        """
        Triggered when a testcase finished successfully

        :param TestCaseInfo testcase: The testcase that finished
        """
        # This is just a dummy implementation
        # pylint: disable=unnecessary-pass
        pass

    def test_inconclusive(self, testcase):
        """
        Triggered when some warning(s) were logged in the running test case

        :param TestCaseInfo testcase: The testcase in which warning is logged
        """
        # This is just a dummy implementation
        # pylint: disable=unnecessary-pass
        pass

    def test_skip(self, testcase):
        """
        Triggered when test case execution is skipped
        """
        # This is just a dummy implementation
        # pylint: disable=unnecessary-pass
        pass

    def test_failed(self, testcase):
        """
        Triggered when a testcase failed

        :param TestCaseInfo testcase: The testcase that failed
        """
        # This is just a dummy implementation
        # pylint: disable=unnecessary-pass
        pass

    def test_finished(self, testcase):
        """
        Triggered when a testcase finished (both successfully and failed)

        :param TestCaseInfo testcase: The testcase that finished
        """
        # This is just a dummy implementation
        # pylint: disable=unnecessary-pass
        pass

    def test_canoe_tm_tc_verdicts(self, test_cases_details):
        """
        Triggered when a testcase CANoe test module executed to collect the test case details with
        its verdicts

        :param list test_cases_details: List contains test case details in dict.
        """
        # This is just a dummy implementation
        # pylint: disable=unnecessary-pass
        pass


class TestWatcherRunner:
    """
    This class handles the watcher implementations. It will trigger the different functions of the
    watcher, take care of test case info creation and other required maintenance.

    New watchers can be registered by calling `append` function of your runner instance.
    To successfully capture stdout, use the watcher runner like this:
    `with TestWatcherRunner() as <your_runner_name>:
        # your code here`
    """

    def __init__(self):
        """
        Creates a new testwatcher runner
        """
        self.current_testcases = []
        self.orig_stdout = None
        # The list of watcher to notify
        self.__watcher = []

    def __enter__(self):
        """
        Will redirect stdout stream to current instance.

        :return The current instance
        """
        # save old sys.stdout as member variable
        self.orig_stdout = sys.stdout
        # override sys.stdout so print goes to our methods
        sys.stdout = self
        return self

    def write(self, *args, **kwargs):
        """
        Triggered if some information is written to stdout.

        :param args: The arguments to write
        :param kwargs: The keyword arguments to write
        """
        for watcher in self.__watcher:
            watcher.write(*args, **kwargs)

        self.orig_stdout.write(*args, **kwargs)

    def flush(self, *args, **kwargs):
        """
        Triggered when the stdout stream is flushed.

        :param args: Optional arguments
        :param kwargs: Optional keyword arguments
        """
        for watcher in self.__watcher:
            watcher.flush(*args, **kwargs)

        self.orig_stdout.flush(*args, **kwargs)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Restores the original output stream.

        :param exc_type: The type of the exception that occurred (if any)
        :param exc_val: The value of the exception that occurred (if any)
        :param exc_tb: Traceback of the exception that occurred (if any)
        """
        # flush everything from input
        self.flush()

        # restore original output
        sys.stdout = self.orig_stdout

        return exc_type is None

    def append(self, watcher):
        """
        Adds a new watcher to the list of watchers to notify

        :param TestWatcher watcher: The watcher to add
        """
        self.__watcher.append(watcher)

    def test_run_started(self, test_cases):
        """
        Will notify the watchers that a new test run started.

        :param list test_cases: The testcases to execute
        """
        _Test_Verdict.clear()
        _ALL_TESTS_TO_RUN.clear()
        _Test_Data_Info.clear()
        # test_case contains [test_name, wrapped_test_function, verifies_id, test_tags, test_type, param_tests_names]
        for test in test_cases:
            test_name = test[0]
            test_object = test[1]
            # check if `test` is a param test
            if test_object.__name__ == "parameterized_runner":
                # now get name of all names of param tests sets and append them in `_ALL_TESTS_TO_RUN`
                for test_case in test[5]:
                    _ALL_TESTS_TO_RUN.append(test_case)
            # simply add test name in `_ALL_TESTS_TO_RUN` as `test` is a normal one not param tests
            _ALL_TESTS_TO_RUN.append(test_name)
        for watcher in self.__watcher:
            watcher.test_run_started(test_cases)

    def test_run_finished(self, missing_tests):
        """
        Will notify the watchers that a testrun has finished.

        :param list missing_tests: A list of testcases that where configured to be executed, but
                                   where not found during execution
        """
        for watcher in self.__watcher:
            watcher.test_run_finished(missing_tests)

    def test_started(
            self, name, test_function, verified_ids, automates_id, tags, test_type, index=None,
            user_modified_param_test=False):
        """
        Will notify the watchers that a new testcase has started.

        :param str name: The name of the testcase
        :param function test_function: The test function that is executed
        :param str test_type: type of the test case, one of (capl, cmm , python)
        :param int index: Contains index of the parameterized test cases currently called, otherwise ``None``
        """
        testcase = TestCaseInfo(name, test_function, verified_ids, automates_id, tags, test_type, index,
                                user_modified_param_test)
        self.current_testcases.append(testcase)
        for watcher in self.__watcher:
            watcher.test_started(testcase)

    def test_succeeded(self):
        """
        Will notify the watchers that the currently running testcase succeeded.
        """
        testcase = self.current_testcases[-1]
        testcase.verified_ids = sorted(list(set(testcase.verified_ids)))
        testcase.tags = sorted(list(set(testcase.tags)))
        testcase.verdict = TestVerdicts.PASS
        testcase.finished()
        _Test_Verdict[testcase.name] = TestVerdicts.PASS.name
        for watcher in self.__watcher:
            watcher.test_succeeded(testcase)

    def test_inconclusive(self, inconclusive_info=None):
        """
        Will notify the watchers that the currently running testcase logged a warning

        :param list inconclusive_info: The warnings raised during test execution for inconclusive verdict reporting
        """
        testcase = self.current_testcases[-1]
        testcase.inconclusive_info = inconclusive_info
        testcase.verified_ids = sorted(list(set(testcase.verified_ids)))
        testcase.tags = sorted(list(set(testcase.tags)))
        testcase.verdict = TestVerdicts.INCONCLUSIVE
        testcase.finished()
        _Test_Verdict[testcase.name] = TestVerdicts.INCONCLUSIVE.name
        for watcher in self.__watcher:
            watcher.test_inconclusive(testcase)

    def test_failed(self, error):
        """
        Will notify the watchers that the currently running testcase failed.

        :param Exception error: The error that occurred during execution.
        """
        testcase = self.current_testcases[-1]
        testcase.failure_info = error
        testcase.verified_ids = sorted(list(set(testcase.verified_ids)))
        testcase.tags = sorted(list(set(testcase.tags)))
        testcase.verdict = TestVerdicts.FAIL
        testcase.finished()
        _Test_Verdict[testcase.name] = TestVerdicts.FAIL.name
        for watcher in self.__watcher:
            watcher.test_failed(testcase)

    def test_skip(self, skip_reason):
        """
        Will notify the watchers that the currently running testcase is skipped.

        :param Exception skip_reason: The error that occurred during execution which shall be treated as skip reason
        """
        testcase = self.current_testcases[-1]
        testcase.skip_info = skip_reason
        testcase.verified_ids = sorted(list(set(testcase.verified_ids)))
        testcase.tags = sorted(list(set(testcase.tags)))
        testcase.verdict = TestVerdicts.SKIP
        testcase.finished()
        _Test_Verdict[testcase.name] = TestVerdicts.SKIP.name
        for watcher in self.__watcher:
            watcher.test_skip(testcase)

    def test_canoe_tm_tc_verdicts(self, test_cases_details):
        """
        Triggered when a testcase CANoe test module executed to collect the test case details with
        its verdicts

        :param list test_cases_details: List contains test case details dictionaries.
        """
        testcase = self.current_testcases[-1]
        testcase.canoe_tm_tc_verdicts.append(deepcopy(test_cases_details))

    def test_finished(self):
        """
        Will notify the watchers that the currently running testcase finished (either failed or succeeded)
        """
        testcase = self.current_testcases.pop()
        # contains information of the test case
        test_case_info = {
            "test_execution": testcase.steps,
            "test_type": testcase.test_type,
            "test_details": testcase.details,
            "precondition": testcase.precondition,
            "test_duration": testcase.run_time * 1000,
            "test_date": datetime.fromtimestamp(testcase.start_time).strftime("%c"),
            "test_status": "",
            "test_verifies": testcase.verified_ids,
            "testcase_id": testcase.testcase_id,
            "test_tags": testcase.tags,
            "test_automates": testcase.automates,
            "canoe_test_case_details": testcase.canoe_tm_tc_verdicts,
            "test_failure": None,
            "test_inconclusive_info": list(),
            "test_skip_info": list()
        }
        if testcase.verdict == TestVerdicts.PASS:
            test_case_info["test_status"] = "PASSED"
        elif testcase.verdict == TestVerdicts.FAIL:
            test_case_info["test_status"] = "FAILED"
            test_case_info["test_failure"] = str(testcase.failure_info)
        elif testcase.verdict == TestVerdicts.INCONCLUSIVE:
            test_case_info["test_status"] = "INCONCLUSIVE"
            test_case_info["test_inconclusive_info"] = str(testcase.inconclusive_info)
        elif testcase.verdict == TestVerdicts.SKIP:
            test_case_info["test_status"] = "SKIPPED"
            test_case_info["test_skip_info"] = str(testcase.skip_info)
        # store the test case information for that test case name as key in _Test_Data_Info
        _Test_Data_Info[testcase.name] = test_case_info
        for watcher in self.__watcher:
            watcher.test_finished(testcase)
