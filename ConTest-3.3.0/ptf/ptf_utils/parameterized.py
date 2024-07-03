"""
    Module to handle parameterized testcases.
    Copyright 2019 Continental Corporation

    Parameterized testcases allow the tester to execute the same testcase under different
    conditions. E.g. the same function could be verified using different input parameters.
    Or the same tests can be run using different database engines. It is also possible to run the
    same tests against different ssh servers. Only your imagination is the limit.

    :file: parameterized.py
    :author:
        - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""
import random
import sys
import traceback
import logging
import functools
import ptf.ptf_utils.decorator as decorator
from ptf.ptf_utils import common
from ptf.ptf_utils.global_params import clear_local_params, _clear_files_for_report
from contest_verify.verify import contest_expects, contest_asserts, contest_warn
from global_vars import TestVerdicts

# Create logger object for this file
LOG = logging.getLogger("PARAMETERIZED")
# Contains strings of func_object, func_name and func parameter values
FUNC_INFO = ["__FUNC_OBJ__", "__FUNC_NAME__", "__PARAM_VALUES__", "__PARAM_NAMES__"]


# pylint: disable=invalid-name,too-few-public-methods
# CamelCase naming would look unexpected for decorators. Decorators also usually don't need public
# methods since they are only wrapping other functions transparently.
class parameterized:
    """
    This class can be used as decorator to parameterize a testcase:

        @parameterized([
            "foo", "bar"
        ])
        def SWT_DEMO_TEST_PARAMETERIZED_single_parameter__each(text):
            print("Text: {0}".format(text))

        @parameterized([
            ("foo", 1),
            ("bar", 2)
        ], print_full_parameters=False)
        def SWT_DEMO_TEST_PARAMETERIZED_tuple_params__each(text, number):
            print("Number: {0}, Text: {1}".format(number, text))
            contest_asserts.verify(number, 1, "Unexpected number")
    """

    def __init__(self, params, print_full_parameters=True, stop_on_first_failure=False, params_names=None):
        """
        Creates a new parameterized decorator.

        :param list params: A list of parameters to be passed to the function
        :param bool print_full_parameters: If the full parameter list should be printed before
                                           test execution or only the index
        :param bool stop_on_first_failure: If test execution should fail on first failure of test
                                           execution or only after all parameters are tested.
        :param list/tuple params_names: Optional argument to provide names of the params in form of list or tuple
        """
        # this variable is not used. if we remove this variable, it is wrapped with parameterized
        # decorator. throw with error message.
        self.__params = params
        self.__print_full_parameters = print_full_parameters
        self.__stop_on_first_failure = stop_on_first_failure
        self.__params_names = params_names
        # dictionary to store the test verdict data of current parameterized test bunch
        self.param_test_verdicts = dict()

    def __call__(self, func):
        """
        This function is called once the decorator is imported. It will return a wrapper
        to be executed once the testcase is called.

        :param function func: The testcase to execute
        :return: The wrapped function
        """

        @functools.wraps(func)
        def parameterized_runner(test_name, test_data, watcher_runner, setup_method, teardown_method, custom_setup,
                                 custom_teardown, setup_script_path, test_filter, random_execution, gui_obj,
                                 parameterized_tests_data, verifies_id, automates_id, tags, test_type,
                                 test_multiple_runs, global_setup_status):
            """
            This will call the testcase once for each parameter.

            :param str test_name: The name of the test to execute
            :param TestData test_data: object of data_handling.prepare_test_data.TestData class
            :param TestWatcherRunner watcher_runner: The watcher runner to notify on new watcher events
            :param function setup_method: The function to call before each testcase
            :param function teardown_method: The function to call after each testcase
            :param object custom_setup: custom setup function object
            :param object custom_teardown: custom teardown function object
            :param str setup_script_path: loaded/used setup.pytest script path
            :param list test_filter: A list of test names to execute. None to execute all
            :param boolean random_execution: If tests should be executed in random order
            :param object gui_obj: GUI object
            :param dict parameterized_tests_data: Contains parameterized test data for test runner
            :param list verifies_id: requirement/design id list
            :param list automates_id: automates id list
            :param list tags: list of the test tags
            :param str test_type: test case type
            :param bool test_multiple_runs: flag if user requested multiple runs of each parameter
            :param bool global_setup_status: bool flag, True in-case global_setup function passed
            """
            test_name_wo_testrun_tag = test_name.split("-testrun")[0]
            self.selected_param_sets = False
            # check the given test case name is available in the dictionary of
            # parameterized_tests_data
            params_list = list()
            if test_name_wo_testrun_tag in parameterized_tests_data:
                # get the list of tuples test data first is bool 'True/False' is valid/Invalid
                # second test parameter and its values for test runner
                # third parameter is bool 'True' means execute, 'False' means not execute
                # if user not selected any set then all valid and invalid parameters executed
                dict_param_sets = parameterized_tests_data[test_name_wo_testrun_tag]
                for param_set_indx, param_value in dict_param_sets.items():
                    if param_value["run"]:
                        params_list.append({param_set_indx: param_value["vals"]})
            self.param_test_verdicts.clear()
            if random_execution:
                # Shuffle the parameter list for random execution of param sets
                random.shuffle(params_list)

            for param_set in params_list:
                for index, param in param_set.items():
                    param_name_missing_msg = None
                    if self.__params_names:
                        try:
                            _ = self.__params_names[index]
                        except IndexError:
                            param_name_missing_msg = \
                                "Param set index {} name missing, using index number in test name".format(index)
                    if test_multiple_runs:
                        display_test_name = \
                            test_name + '(' + parameterized_tests_data[
                                test_name_wo_testrun_tag][index]["name"].split('(')[1]
                    else:
                        display_test_name = parameterized_tests_data[test_name_wo_testrun_tag][index]["name"]
                    # this condition is for skipping previously ran passed test cases
                    if test_filter is not None:
                        if display_test_name not in test_filter:
                            continue
                    # run the tests
                    self.__execute_test(
                        watcher_runner, test_data, setup_method, teardown_method, custom_setup, custom_teardown,
                        setup_script_path, display_test_name, func, param, index, verifies_id, automates_id, tags,
                        test_type, global_setup_status, param_name_missing_msg,
                        user_modified_param_test=parameterized_tests_data[
                            test_name_wo_testrun_tag][index]["user_added"])
                    # checking if user pressed stop button
                    if gui_obj:
                        if gui_obj[0].stop_state:
                            break
                    # cleanup local parameters for next iteration
                    clear_local_params()
                    # clean up failures of contest_expects.py
                    contest_expects.FAILURES.clear()
                    # clearing warning list for next test case
                    contest_warn._WARNINGS.clear()
            # following conditions to let test_runner.
            if TestVerdicts.FAIL in self.param_test_verdicts.values():
                raise Exception
            else:
                if TestVerdicts.INCONCLUSIVE in self.param_test_verdicts.values():
                    contest_warn.warn("Warning(s) logged in parameterized set(s), please check")
        decorator.sync_attributes(func, parameterized_runner)
        # assigning the name "parameterized_runner" to decorator function as the usage of "@functools.wraps(func)" over
        # parameterized_runner function will restore original function metadata and this name is used in framework
        # to distinguish between normal and parameterized test case
        parameterized_runner.__name__ = "parameterized_runner"
        # Storing the parameterized values and function object in the parameterized_runner
        set_parameterized_test_data(parameterized_runner, FUNC_INFO, func, self.__params, self.__params_names)
        return parameterized_runner

    def __execute_test(self, watcher_runner, test_data, setup_method, teardown_method, custom_setup, custom_teardown,
                       setup_script_path, display_test_name, func, param, index, verifies_id, automates_id, tags,
                       test_type, global_setup_status, param_names_missing_msg=None, user_modified_param_test=False):
        """
        Performs test execution of a single function.

        :param TestWatcherRunner watcher_runner: The watcher runner to notify on new watcher events
        :param TestData test_data: object of data_handling.prepare_test_data.TestData class
        :param function setup_method: The function to call before the testcase
        :param function teardown_method: The function to call after the testcase
        :param object custom_setup: custom setup function object
        :param object custom_teardown: custom teardown function object
        :param str setup_script_path: loaded/used setup.pytest script path
        :param str display_test_name: The name of the testcase to display
        :param function func: The function to call
        :param list param: The parameters for the function call
        :param int index: The index of the parameters currently called
        :param list verifies_id: requirement/design id list
        :param list automates_id: automates id list
        :param list tags: list of the test tags
        :param str test_type: test case type
        :param bool global_setup_status: bool flag, True in-case global_setup function passed
        :param str param_names_missing_msg: message or info to be printed if a param set name is missing
        :param bool user_modified_param_test: flag reporting if user did modification(s) (set value change or new
            set added) in parameterized tests
        """
        watcher_runner.test_started(
            display_test_name, func, verifies_id, automates_id, tags, test_type, index, user_modified_param_test)
        # check if `skip_if` decorator is used and the skip condition is `True`
        if common._get_test_skip_info(test_data):
            # skipping param test case execution as skip condition is `True`
            print("Skipping parameterized test due to reason: {}".format(test_data.skip_reason))
            watcher_runner.test_skip(test_data.skip_reason)
            watcher_runner.test_finished()
            return
        if param_names_missing_msg:
            LOG.info(param_names_missing_msg)
        # Debug info
        if self.__print_full_parameters:
            LOG.info("Running with parameters: %s", param)
            error_msg = "Failed for parameters: {0}".format(str(param))
        else:
            LOG.info("Running with parameter set: %s", index)
            error_msg = "Failed for parameter set: {0}".format(str(index))
        # dictionary for storing status of test case (setup function or test function) failure
        # and teardown function failure
        test_case_error = {"status": False, "err_str": str()}
        teardown_error = {"status": False, "err_str": str()}
        # boolean flag to save the param test case failure state
        param_test_failure_occurred = False
        try:
            # if global_setup function failed then no need to execute param test and therefore raising error
            if not global_setup_status:
                contest_asserts.fail(
                    "Execution of '{}' did not happen due to failure in 'global_setup' function".format(
                        display_test_name))
            # first checking if 'custom_setup' function is requested to be executed, if yes then execute it
            if custom_setup:
                setup_print = "*** running custom setup '{0}' from '{1}'".format(
                    custom_setup.__name__, setup_script_path)
                print("\n{0}".format("/" * len(setup_print)))
                print(setup_print)
                print("{0}\n".format("/" * len(setup_print)))
                custom_setup()
            # if custom setup function is not found then execute standard setup function if it exists
            elif setup_method:
                setup_print = "*** running standard setup '{0}' from '{1}'".format(
                    setup_method.__name__, setup_script_path)
                print("\n{0}".format("/" * len(setup_print)))
                print(setup_print)
                print("{0}\n".format("/" * len(setup_print)))
                setup_method()
            # Run the test function
            self.__run_test(func, param)
            # Check EXPECT failure(s) list.
            # If it is an empty list, then the test is PASSED.
            # Else raise exception to FAIL the test
            if contest_expects.FAILURES:
                raise contest_expects.ConTestExpectError(contest_expects.FAILURES)
        # catch all exceptions that might appear in test/setup function and report them
        except Exception as error:  # pylint: disable=broad-except
            param_test_failure_occurred = True
            # here saving the failure info if some failure happened in real test function or
            # setup() function, this change is being done since earlier implementation was not
            # ensuring that if some error happens in teardown() function then other param sets are
            # getting executed
            test_case_error["status"] = True
            test_case_error["err_str"] = error
            # here we need to print exceptions since in parameterized test case scenario we are
            # handling errors in nested exceptions and exception prints need to be done in exception
            # block for traceback information
            if isinstance(error, contest_asserts.ConTestAssertCompareError):
                contest_asserts._print_exception_info(error)
            elif isinstance(error, contest_expects.ConTestExpectError):
                print("\n--> ERROR: Expectation(s)")
                print("--> Failure(s) : ", error)
            else:
                traceback.print_exc(file=sys.stdout)
        finally:
            # trying to run teardown() function in pass/fail scenario
            try:
                # only execute standard or custom teardown if global_setup function passed
                if global_setup_status:
                    # first checking if 'custom_teardown' function is requested to be executed, if yes then execute it
                    if custom_teardown:
                        teardown_print = "*** running custom teardown '{0}' from '{1}'".format(
                            custom_teardown.__name__, setup_script_path)
                        print("\n{0}".format("/" * len(teardown_print)))
                        print(teardown_print)
                        print("{0}\n".format("/" * len(teardown_print)))
                        custom_teardown()
                        # check if any expect exception is raised and raise it
                        if contest_expects.FAILURES:
                            raise contest_expects.ConTestExpectError(contest_expects.FAILURES)
                    # if custom teardown function is not found then execute standard teardown function if it exists
                    elif teardown_method:
                        teardown_print = "*** running standard teardown '{0}' from '{1}'".format(
                            teardown_method.__name__, setup_script_path)
                        print("\n{0}".format("/" * len(teardown_print)))
                        print(teardown_print)
                        print("{0}\n".format("/" * len(teardown_print)))
                        teardown_method()
                        # check if any expect exception is raised and raise it
                        if contest_expects.FAILURES:
                            raise contest_expects.ConTestExpectError(contest_expects.FAILURES)
            # catch all exceptions and save it that might appear in teardown function
            except Exception as error:  # pylint: disable=broad-except
                param_test_failure_occurred = True
                teardown_error["status"] = True
                teardown_error["err_str"] = error
                # here we need to print exceptions since in parameterized test case scenario we are
                # handling errors in nested exceptions and exception prints need to be done in
                # exception block for traceback information
                if isinstance(error, contest_asserts.ConTestAssertCompareError):
                    contest_asserts._print_exception_info(error)
                elif isinstance(error, contest_expects.ConTestExpectError):
                    print("\n--> ERROR: Expectation(s)")
                    print("--> Failure(s) : ", error)
                else:
                    traceback.print_exc(file=sys.stdout)
            # in this final block a particular param set test failure (if its raised in setup(),
            # test function or teardown() functions)shall be reported
            finally:
                # this statement to capture error if it happened in setup or test function
                if test_case_error["status"]:
                    error = test_case_error["err_str"]
                # this statement to capture error if it happened in teardown function
                if teardown_error["status"]:
                    error = teardown_error["err_str"]
                # if error happened in any above condition then raise error
                if test_case_error["status"] or teardown_error["status"]:
                    # if we should fail on the first error, then finish here ...
                    if self.__stop_on_first_failure:
                        raise error
                    # report the failure with most recent error raised
                    watcher_runner.test_failed(error)
                    # capturing the verdict of individual parameterized test
                    self.param_test_verdicts[display_test_name] = TestVerdicts.FAIL
                    contest_expects._print_expectations("failure", "success", error_msg, param_flag=True)
                else:
                    if not param_test_failure_occurred and not contest_warn._WARNINGS:
                        # no exceptions and no warnings appeared therefore we can notify the watcher that test succeeded
                        watcher_runner.test_succeeded()
                        self.param_test_verdicts[display_test_name] = TestVerdicts.PASS
                    else:
                        if not param_test_failure_occurred and contest_warn._WARNINGS:
                            self.param_test_verdicts[display_test_name] = TestVerdicts.INCONCLUSIVE
                            watcher_runner.test_inconclusive(contest_warn._WARNINGS)
                watcher_runner.test_finished()
                # clear the test case metadata files after each set of param test case
                _clear_files_for_report()

    @staticmethod
    def __run_test(func, param):
        """
        Performs test execution depending on parameter type.

        :param function func: The function to call
        :param list param: The parameters for the function call
        """
        if isinstance(param, (list, tuple)):
            func(*param)
        elif isinstance(param, dict):
            func(**param)
        else:
            func(param)


def set_parameterized_test_data(parameterized_runner, func_info, func_obj, func_param_values, func_param_names):
    """
    Sets the parameterized test case values, function object and function name

    :param function parameterized_runner: The function should be tagged with test case data

    :param list func_info: This list contains as "__FUNC_OBJ__" ,  "__PARAM_VALUES__" ,
                           "__FUNC_NAME__"
    :param Object/list/string func_obj: This contains function object or list of param values
                                              or function name to set
    :param list func_param_values: This contains  list of param values
    :param list func_param_names: This contains  list of param names
    :return: The setattrr function of parameterized_runner
    :rtype: function
    """
    setattr(parameterized_runner, func_info[0], func_obj)
    setattr(parameterized_runner, func_info[1], func_obj.__name__)
    setattr(parameterized_runner, func_info[2], func_param_values)
    setattr(parameterized_runner, func_info[3], func_param_names)
    return parameterized_runner
