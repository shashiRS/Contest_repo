"""
    Copyright 2023 Continental Corporation

    :file: common_funcs.py
    :platform: Windows, Linux
    :synopsis:
        File containing common functions for the usage of `skip_if` decorator

    :author:
        - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
"""

import sys


def check_windows_platforms():
    """
    Function to check if script is running on windows platform or not

    :return: Returns ``True`` if script is running on windows platform else ``False``
    :rtype: bool
    """
    if sys.platform == "win32":
        return True
    else:
        return False


def check_linux_platforms():
    """
    Function to check if script is running on linux platform or not

    :return: Returns ``True`` if script is running on linux platform else ``False``
    :rtype: bool
    """
    if sys.platform == "linux":
        return True
    else:
        return False


def cat_is_sick(sick_status=False):
    """
    Function to return the status of our cats sickness

    :param bool sick_status: Cats sickness status

    :return: Returns ``True`` cats are sick else ``False``
    :rtype: bool
    """
    return sick_status
