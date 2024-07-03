"""
    Copyright 2023 Continental Corporation

    :file: skip.py
    :platform: Windows, Linux

    :synopsis:
        Script containing implementation of skip decorator

    :author:
        - Praveenkumar G K <praveenkumar.gomathi.kaliamoorthi@continental-corporation.com>
        - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
"""

import functools
from ptf.ptf_utils import decorator

__SKIP_CONDITION__ = "__SKIP_CONDITION__"
__SKIP_REASON__ = "__SKIP_REASON__"


# pylint: disable=invalid-name,too-few-public-methods
# CamelCase naming would look unexpected for decorators. Decorators also usually don't need public
# methods since they are only wrapping other functions transparently.
class skip_if:
    """
    Decorator class in order to skip a test case execution
    """
    def __init__(self, condition=False, reason="None"):
        """
        Constructor
        :param bool condition: boolean condition ``True`` or ``False`` which will determine test case execution skip
        :param string reason: reason to be specified in reports if ``condition`` is ``True``
        """
        self.__condition = condition
        self.__reason = reason

    def __call__(self, func):
        """
        This function is called once the decorator is imported. It will return a wrapper
        to be executed once the testcase is called.

        :param function func: The testcase to execute

        :return: The wrapped function
        :rtype: function
        """
        @functools.wraps(func)
        def skip_wrapper(*args, **kwargs):
            """
            This will finally execute the testcase. Will pass through arguments and return values.

            :param args: The original function arguments
            :param kwargs: The original keyword function arguments

            :return: The return value of the function
            """
            return func(*args, **kwargs)

        decorator.sync_attributes(func, skip_wrapper)
        set_skip_attr(wrapped_func=skip_wrapper, condition=self.__condition, reason=self.__reason)
        return skip_wrapper


def set_skip_attr(wrapped_func, condition, reason):
    """
    Function to set particular attributes in the object of the test case function

    :param object wrapped_func: test case function object
    :param bool condition: boolean condition ``True`` or ``False`` which will determine test case execution skip
    :param string reason: reason to be specified in reports if ``condition`` is ``True``
    """
    setattr(wrapped_func, __SKIP_CONDITION__, condition)
    setattr(wrapped_func, __SKIP_REASON__, reason)
    return wrapped_func
