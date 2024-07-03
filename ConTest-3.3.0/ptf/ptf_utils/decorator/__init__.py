"""
This package contains several decorators to configure test execution.
See the documentation for each decorator to see its usage.
"""
from ptf.ptf_utils.decorator import prioritization


def sync_attributes(from_function, to_function):
    """
    This function will synchronize the contest specific attributes between two functions.
    Should be called in each decorator before additional attributes are added.

    :param from_function: The function from which the attributes should be copied
    :param to_function: The function to which the attributes should be copied
    """
    # If you create a new decorator that stores additional attributes, please provide a method
    # to copy these attributes and call this function here.
    prioritization.copy_priority(from_function, to_function)
