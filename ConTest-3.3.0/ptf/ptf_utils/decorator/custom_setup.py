"""
    Copyright 2023 Continental Corporation
    :file: custom_setup.py
    :platform: Windows, Linux
    :synopsis:
        Script containing implementation of custom setup, teardown decorator
    :author:
        - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
"""

import functools

from ptf.ptf_utils import decorator

__TEST_CASE_SETUP_FUNC__ = '__TEST_CASE_SETUP_FUNC__'
__TEST_CASE_TEARDOWN_FUNC__ = '__TEST_CASE_TEARDOWN_FUNC__'


# pylint: disable=invalid-name,too-few-public-methods
# CamelCase naming would look unexpected for decorators. Decorators also usually don't need public
# methods since they are only wrapping other functions transparently.
class custom_setup:
    """
    Decorator class to be used over test case function to specify custom setup & teardown functions to be used
    before and after test case execution respectively
    """
    def __init__(self, setup=None, teardown=None):
        """
        Constructor
        :param string setup: custom setup function name to be used
        :param string teardown: custom teardown function name to be used
        """
        self.setup_func = setup
        self.teardown_func = teardown

    def __call__(self, func):
        """
        This function is called once the decorator is imported. It will return a wrapper
        to be executed once the testcase is called.
        :param function func: The testcase to execute
        :return: The wrapped function
        :rtype: function
        """
        @functools.wraps(func)
        def setup_wrapper(*args, **kwargs):
            """
            This will finally execute the testcase. Will pass through arguments and return values.
            :param args: The original function arguments
            :param kwargs: The original keyword function arguments
            :return: The return value of the function
            """
            return func(*args, **kwargs)
        decorator.sync_attributes(func, setup_wrapper)
        set_test_func_attributes(setup_wrapper, self.setup_func, self.teardown_func)
        return setup_wrapper


def set_test_func_attributes(function, setup_func_name, teardown_func_name):
    """
    Function to set particular attributes in the object of the test case function
    :param object function: test case function object
    :param string setup_func_name: custom setup function name to be used
    :param string teardown_func_name: custom teardown function name to be used
    """
    if setup_func_name:
        setattr(function, __TEST_CASE_SETUP_FUNC__, setup_func_name)
    if teardown_func_name:
        setattr(function, __TEST_CASE_TEARDOWN_FUNC__, teardown_func_name)
    return function
