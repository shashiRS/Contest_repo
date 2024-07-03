"""
    This module implements prioritisation possibilities for testcases.
    Copyright 2019 Continental Corporation

    This module provides the possibility to decorate a function with a priority for execution.
    During execution, the testcases are executed in the order of given priority.

    :file: priority.py
    :author:
        - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""
import functools
from enum import IntEnum

from ptf.ptf_utils import decorator

# The attribute name to be used for tagging priority to a function
__TEST_EXECUTION_PRIORITY_PROPERTY_NAME__ = '__TEST_EXECUTION_PRIORITY__'

class Priority(IntEnum):
    """
    Available priorities to be used for @priority decorator.
    """
    # Lowest value is lowest priority
    # using constant numbers since 'auto' module is not Python 3.5 (tested on Ubuntu machine)
    LOW = 0  # Autogenerate ids, starting with 0
    MEDIUM = 1
    HIGH = 2

# pylint: disable=invalid-name,too-few-public-methods
# CamelCase naming would look unexpected for decorators. Decorators also usually don't need public
# methods since they are only wrapping other functions transparently.
class priority:
    """
    This class can be used as decorator set the priority of a testcase.

    @priority(Priority.LOW)
    def SWT_DEMO_TEST_HIGH_PRIORITY__each():
        print("This is executed with high priority")

    @priority(Priority.MEDIUM)
    def SWT_DEMO_TEST_MEDIUM_PRIORITY__each():
        print("This is executed with medium priority")
    """

    def __init__(self, test_case_priority):
        """
        Creates a new priority decorator.

        :param Priority test_case_priority: The priority of the testcase
        """
        self.__priority = test_case_priority

    def __call__(self, func):
        """
        This function is called once the decorator is imported. It will return a wrapper
        to be executed once the testcase is called. Also, it will tag the priority to the function.

        :param function func: The testcase to execute
        :return: The wrapped function
        :rtype: function
        """

        @functools.wraps(func)
        def priority_runner(*args, **kwargs):
            """
            This will finally execute the testcase. Will pass through arguments and return values.

            :param args: The original function arguments
            :param kwargs: The original keyword function arguments
            :return: The return value of the function
            """
            return func(*args, **kwargs)

        decorator.sync_attributes(func, priority_runner)
        tag_with_priority(priority_runner, self.__priority)
        return priority_runner

def tag_with_priority(function_to_tag, test_case_priority):
    """
    Sets the priority as attribute to a given function

    :param function function_to_tag: The function that should be tagged
    :param Priority test_case_priority: The priority to tag to the function
    :return: The tagged function
    :rtype: function
    """
    setattr(
        function_to_tag,
        __TEST_EXECUTION_PRIORITY_PROPERTY_NAME__,
        test_case_priority
    )
    return function_to_tag

def get_priority(function):
    """
    Returns the tagged priority of a given function. Default is medium priority.

    :param function function: The function to get the priority from.
    :return: The priority.
    :rtype: Priority
    """
    return getattr(
        function,
        __TEST_EXECUTION_PRIORITY_PROPERTY_NAME__,
        Priority.MEDIUM
    )

def copy_priority(from_function, to_function):
    """
    Copies the priority from a given function to another function. E.g. useful when additional
    decorators are applied.

    :param function from_function: The function to copy the priority from.
    :param function to_function: The function to copy the priority to.
    """
    tag_with_priority(to_function, get_priority(from_function))
