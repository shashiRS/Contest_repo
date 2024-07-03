"""
    Copyright 2018 Continental Corporation

    :file: helper.py
    :platform: Windows, Linux
    :synopsis:
        This file contains helping variables and functions
    :author:
        - M. F. Ali Khan <Muhammad.fakhar.ali.khan@continental-corporation.com>
        - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
        - Praveenkumar G K  <praveenkumar.gomathi.kaliamoorthi@continental-corporation.com>
"""

import os
import sys
import subprocess
import re
from os.path import join, isdir
from enum import Enum

# Use importlib.util here - not importlib - or importlib.util.* function calls  won't be found in
# ubuntu in runtime execution (but still works in debugger O.o)
import importlib.util

import global_vars


class InfoLevelType(Enum):
    """
    This Enum class which is used for warn level Type INFO, WARN, ERR, QUEST
    """

    INFO = 1
    WARN = 2
    ERR = 3
    QUEST = 4


# PrepareTestData.test_runner_data["paths"] dictionary key names
BASE_PATH = "basePath"
PTF_TEST = "ptfTests"
T32_TEST = "t32Scripts"
CANOE_CFG = "canoeCfg"
CTE_ZIP = "cteZip"
CTE_CFG = "cteCfg"
USE_CTE = "useCte"
TXT_REPORT = "txtReport"
HTML_REPORT = "htmlReport"
BASE_REPORT_DIR = "baseReport"
EXEC_RECORD_DIR = "execRecord"
EXTERNAL_REPORT = "externalReport"

# this dictionary contains PTF configuration data. It can be utilized by tools classes.
PTF_CFG_TOOL_DATA = {}
# keys for above dictionary (specifically for Lauterbach)
T32_EXE_PATH = "t32_exe_path"
T32_SRC_PATH = "t32_src_path"

# Method names that can be used for setup and teardown methods
# Order is: global setup, global teardown, setup, teardown
SETUP_TEARDOWN_METHOD_NAMES = ["global_setup", "global_teardown", "setup", "teardown"]

# Timer resolution in msec.
TC_TIMER_INCREMENT = 200

TEST_DEF_NAME_FORMATS = (
    "def swt_",
    "def SWT_",
    "def swit_",
    "def SWIT_",
    "def swrt_",
    "def SWRT_",
    "def swat_",
    "def SWAT_",
)
TEST_NAME_FORMATS = ("swt_", "SWT_", "swit_", "SWIT_", "swrt_", "SWRT_", "swat_", "SWAT_")


def sys_path_addition(directory):
    """
    Method for adding all the directories and sub directories from the given directory
    to system path

    :param str directory: Path of the directory
    """
    # walking through the given directory path
    for dir_path, _dir_names, _file_names in os.walk(directory):
        # check if subdirectory is in system path
        # if not then append it to system path for importing stuff
        if (dir_path not in sys.path) and ("__pycache__" not in dir_path):
            sys.path.append(dir_path)
        else:
            pass


def reload_py_scripts(script_folder):
    """
    Function for reloading all python modules or files (.py) in a directory

    :param string script_folder: Directory whose python scripts need to be reloaded

    :returns: error string if occurred else None
    :rtype: None or string
    """
    error = None
    # list which contains file names which don't need to be reloaded
    reload_ignore_list = ["__init__", "setup"]
    for dir_path, _dir_names, file_names in os.walk(script_folder):
        for files in file_names:
            # names of the files (or modules) saving into variable
            module_name = os.path.splitext(files)[0]
            # extensions of the files (or modules) saving into variable
            module_ext = os.path.splitext(files)[1]
            if module_ext == ".py" and module_name not in reload_ignore_list:
                try:
                    importlib.import_module(module_name)
                    importlib.reload(sys.modules[module_name])
                    importlib.import_module(module_name)
                except SyntaxError as exc:
                    error = (
                        f"Syntax error in {exc.filename}, Line {exc.lineno}, Char {exc.offset}.\n\t"
                        f"Line: '{exc.text}'"
                    )
                except Exception as exc:  # pylint: disable=broad-except
                    error = f"Error while loading file {os.path.join(dir_path, files)}: '{exc}'."
    return error


def alphabetic_dir_walk(top, topdown=True):
    """
    Function for generating given directory structure in alphabetic order.
    It's a shrinked version of standard 'os.walk' but it ensures alphabetic order.

    It's introduced since it was observed that 'os.walk' doesn't yields directory structure in
    alphabetic order but it yields alphabetic structure on windows machine.

    :param string top:
    :param topdown:

    :return: yields a tuple (root_dir, dirs_in_root_dir, non_dirs_in_root)
    :rtype: tuple
    """
    # get
    dir_content = os.listdir(top)
    dir_content.sort()
    dirs, non_dirs = [], []
    # loop for populating lists of directory or non directories
    for content in dir_content:
        if isdir(os.path.join(top, content)):
            dirs.append(content)
        else:
            non_dirs.append(content)
    # yield before recursion if going top down
    if topdown:
        yield top, dirs, non_dirs
    # recurse into sub-directories
    for name in dirs:
        path = join(top, name)
        if not os.path.islink(path):
            for x in alphabetic_dir_walk(path, topdown):
                yield x
    # yield after recursion if going bottom up
    if not topdown:
        yield top, dirs, non_dirs


def get_capl_modules(mods_list, ctf_mod_dict):
    """
    Function to extract test modules names from dictionary and populate them into list

    :param list mods_list: List needs to be populated with test module names
    :param dict ctf_mod_dict: Dictionary containing test module data with structure
    """
    for i, j in ctf_mod_dict.items():
        if j != "module":
            get_capl_modules(mods_list, j)
        else:
            mods_list.append(i)


def get_version_info():
    """
    Function to get tool release version and pre-release info (if any)

    Possible return values:
    - version = "unknown", pre_release_info = "", is_numeric_version = False
      when user on git and no branch or tag info is extracted
      or when user on release tag but release tag is not starting with v
    - version = "git-<branch_name>", pre_release_info = "Unofficial Version", is_numeric_version = False
      when user is on a git branch
    - version = "x.y.z", pre_release_info = "<if_any>", is_numeric_version = True
      when user is on a git and on a release tag (official release)
    - version = LATEST_VERSION, pre_release_info = LATEST_PRE_RELEASE_INFO, is_numeric_version = True
      when user is using tool without git i.e. downloaded in zip form from artifactory or git release artifacts

    :returns: tuple (version, pre_release_info, is_numeric_version)
    :rtype: tuple
    """
    git_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".git")
    git_dir_exists = os.path.isdir(git_dir)
    release_tag = None
    branch = None
    version = "unknown"
    pre_release_info = ""
    is_numeric_version = False
    try:
        if git_dir_exists:
            # this conditions means that user is using contest tool via git i.e. cloned contest git repo
            # so in this case we need to check whether user is on a release tag or on some branch e.g. master etc.
            try:
                # checking if user is on a release tag or not
                output = subprocess.check_output(
                    ["git", "describe", "--tags", "--exact-match"],
                    cwd=git_dir,
                    stderr=subprocess.PIPE,
                ).strip()
                release_tag = output.decode("utf-8")
            # ok to catch general exceptions
            # pylint: disable=broad-exception-caught
            except Exception:
                # in-case of any error (user not on a release tag), try to get the branch name
                try:
                    output = subprocess.check_output(
                        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                        cwd=git_dir,
                        stderr=subprocess.PIPE,
                    ).strip()
                    branch = output.decode("utf-8")
                except Exception:
                    # in-case of error, do nothing i.e. use default values of version and pre_release_info
                    pass
            if release_tag:
                # if user detected on a release tag then extract release tag and pre-release info (if any)
                if release_tag.startswith("v"):
                    match = re.search(r"(v\d+\.\d+\.\d+)(.*)", release_tag)
                    version = match.group(1).replace("v", "")
                    pre_release_info = match.group(2)
                    is_numeric_version = True
            elif branch:
                # if user is not detected on release tag then use branch name in version
                version = "git-" + branch
                pre_release_info = "Unofficial Version"
        else:
            # this condition means that user either downloaded via artifactory or git repo release link, therefore use
            # versions defined in this file above
            version = global_vars.LATEST_VERSION
            pre_release_info = global_vars.LATEST_PRE_RELEASE_INFO
            is_numeric_version = True
    # ok to catch general exceptions
    # pylint: disable=broad-exception-caught
    except Exception:
        # just use default values in-case of some overall error
        pass
    return version, pre_release_info, is_numeric_version
