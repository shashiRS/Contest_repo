"""
    Module can be used to hold common/re-usable functions and classes.
    Copyright 2023 Continental Corporation

    :file: common.py
    :author:
        - Praveenkumar G K <praveenkumar.gomathi.kaliamoorthi@continental-corporation.com>
"""

import os
import getpass
import platform
from datetime import datetime
from shutil import copyfile
from data_handling import helper
from ptf.ptf_utils.global_params import get_cfg_paths


def get_updated_file_path(file, test_case_obj):
    """
    This Method returns the base file name and meta data relative file path.
    Steps as below :
    1  From the original file path the new file name is created by appending
       test case name + timestamp + original FileName
    2. Copying the newly created file name from original file path location to metadata_files
       reports folder

    :param str file: original file path
    :param TestCase test_case_obj: TestCase Object
    :return: Returns meta data relative file path and base file name
    :rtype: tuple
    """
    html_report_path = get_cfg_paths(helper.HTML_REPORT)
    base_report_dir = get_cfg_paths(helper.BASE_REPORT_DIR)
    external_report_dir = get_cfg_paths(helper.EXTERNAL_REPORT)
    # updated the external report path by replacing the BASE_REPORT_DIR with user provided
    # EXTERNAL_REPORT in html report path and assign as updated external report path

    base_file_name = os.path.basename(file)
    file_info = base_file_name.split(".")
    time_stamps = datetime.now().strftime("%H-%M-%S_%f")
    # this if case is for parameterized test cases and else for normal test cases
    if test_case_obj.index is not None:
        test_name = test_case_obj.test_function.__name__ + "__index_" + str(test_case_obj.index)
        copy_file_name = file_info[0].replace(" ", "_") + "__" + test_name + "_" + time_stamps + "." + file_info[1]
    else:
        copy_file_name = (
            file_info[0].replace(" ", "_") + "__" + test_case_obj.name + "_" + time_stamps + "." + file_info[1]
        )
    updated_file_path = os.path.join(html_report_path, "metadata_files", copy_file_name)
    copyfile(file, updated_file_path)
    # if external report path directory exits then copy the created file to metadata file
    # folder in the external path directory
    if external_report_dir:
        external_report_path = html_report_path.replace(base_report_dir, external_report_dir)
        external_metadata_path = os.path.join(external_report_path, "metadata_files", copy_file_name)
        copyfile(file, external_metadata_path)

    metadata_rel_file_path = os.path.join("metadata_files", copy_file_name)
    return metadata_rel_file_path, base_file_name


def _get_test_skip_info(test_data):
    """
    Function to fetch the skip condition attribute from a test case data class

    :param TestData test_data: object of data_handling.prepare_test_data.TestData class
    """
    # "skip_condition" existing in data_handling.prepare_test_data.TestData.skip_condition
    # the existence of this attribute will be for test cases functions but not global_setup and global_teardown
    if "skip_condition" in dir(test_data):
        return test_data.skip_condition
    return False


def _get_user():
    """
    Function to return the username based on platform on which framework is running

    :returns: "jenkins_linux_user" if framework is running in docker on linux platform in jenkins due to Kyverno
        changes else actual username
    :rtype: string
    """
    if platform.system() == "Linux":
        if "WORKSPACE" in os.environ:
            user_id = "jenkins_linux_user"
        else:
            user_id = getpass.getuser()
    else:
        user_id = getpass.getuser()
    return user_id
