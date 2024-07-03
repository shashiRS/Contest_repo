"""
    Module to provide information about selected test cases to be executed

    Copyright 2021 Continental Corporation

    :file: test_info.py
    :platform: Windows, Linux
    :synopsis:
        Scripts for fetching tests information

    :author:
        - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
"""

import logging

LOG = logging.getLogger('TEST_INFO')


class TestInfo:
    """Class to get tests information selected for execution"""

    def __init__(self, prj_specs):
        """Constructor

        :param dict prj_specs: Dictionary containing project/current test execution data
        """
        # private containers for python, cmm and capl test cases data objects list in order to
        # avoid overwriting of their member values which might lead to unknown behaviours while
        # tests execution
        LOG.info("Collecting selected tests information ...")
        self.__py_tests = prj_specs["py_tests"]
        self.__capl_tests = prj_specs["capl_tests"]
        self.__cmm_tests = prj_specs["cmm_tests"]
        self.__pytest_names = [py_test.name for py_test in self.__py_tests]
        self.__pytest_folders = [py_test.folder_structure for py_test in self.__py_tests]

    def return_selected_pytests_data(self):
        """
        To get the list of python tests data objects selected for execution

        :return: List containing TestData objects
        :rtype: list
        """
        return self.__py_tests

    def return_selected_cmm_data(self):
        """
        To get the list of cmm tests data objects selected for execution.

        :return: List containing TestData objects
        :rtype: list
        """
        return self.__cmm_tests

    def return_selected_capl_data(self):
        """
        To get the list of capl tests data objects selected for execution.

        :return: List containing TestData objects
        :rtype: list
        """
        return self.__capl_tests

    def return_selected_pytests_folders(self):
        """
        To get all the folders for the selected python tests.

        :return: List containing folder structures for the selected python tests
        :rtype: list
        """
        return self.__pytest_folders

    def return_selected_pytests_names(self):
        """
        To get all names for the selected python tests.

        :return: List containing folder structures for the se
        :rtype: list
        """
        return self.__pytest_names

    def return_specific_pytest_data(self, test_name):
        """
        To get data object of a specific python test data

        :param str test_name: Test case name whose test data object is required

        :return: Data object of requested test case or None in-case it's not found
        :rtype: Object/None
        """
        return_value = None
        # loop for finding the data object of a particular test case given by user
        for test_info in self.__py_tests:
            if test_info.name == test_name:
                # test case found exit the loop
                return_value = test_info
                break
        if return_value:
            LOG.info("Test Case '%s' data object found.", test_name)
        else:
            LOG.warning("Test Case '%s' was not selected or doesn't exist.", test_name)
        # throw back the return value
        return return_value
