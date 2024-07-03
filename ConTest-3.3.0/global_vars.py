"""
    Copyright Continental Corporation and subsidiaries. All rights reserved.

    :platform: Windows, Linux

    :synopsis:
        This file contains all the variables which are used globally within the Framework.
"""

import os
import re
import sys
import platform
import urllib.request
from enum import Enum

from data_handling.helper import get_version_info


THIS_FILE = os.path.dirname(os.path.realpath(__file__))

# please change the version and year also in 'ConTest\NOTICE_FILE.txt'
LATEST_VERSION = "3.3.0"
LATEST_PRE_RELEASE_INFO = ""
BASE_PYTHON_VERSION = platform.python_version()
PYTHON_PATH = sys.executable
PYTHON_BIT_ARCH = platform.architecture()[0]

FW_NAME = "ConTest"
# main release (ONLY NUMBERS) in form of <major_version>.<minor_version>.<patch_version>
# this will be used to compare the latest version in artifactory
# string containing pre-release info if any, for official release it can be empty string
#
# VERSION: version of the tool
# PRE_RELEASE_INFO: string containing pre-release info if any, for official release it can be empty string
VERSION, PRE_RELEASE_INFO, IS_VERSION_NUMERIC = get_version_info()
# version string to appear in user documentation i.e. extended with 'v' and 'pre-release'
CONTEST_VERSION = "v" + VERSION + " " + PRE_RELEASE_INFO
# converting 'VERSION' string to tuple for comparing it with tuple of release version from artifactory
if IS_VERSION_NUMERIC:
    LOCAL_VERSION_TUPLE = tuple(map(int, (VERSION.split("."))))
else:
    LOCAL_VERSION_TUPLE = None
TEST_ENVIRONMENT = FW_NAME + "_" + CONTEST_VERSION
URL = "https://eu.artifactory.conti.de/artifactory/c_adas_astt_generic_prod_eu_l/ConTest/"
# this SHOULD match with the git release tag otherwise the doc links WILL NOT WORK !!!
DOC_VERSION = "v" + LATEST_VERSION
# GUI window title
gui_window_title = FW_NAME + " " + CONTEST_VERSION

# list containing run mode names
AUTO_MODE = "auto"
# Auto mode with GUI option enabled
AUTO_GUI_MODE = "auto_gui"
MANUAL_MODE = "manual"
RUN_MODES = [AUTO_MODE, MANUAL_MODE, AUTO_GUI_MODE]
UIM_CLI_ARGS = ["latest", "none"]

# variables storing log and logo icon paths
LOGO_ICON = os.path.join(THIS_FILE, "gui", "gui_images", "logo_icon.png")
LOGO = os.path.join(THIS_FILE, "gui", "gui_images", "logo.png")
HTML_COPY_LINK = os.path.join(THIS_FILE, "gui", "gui_images", "html_report_copy_link_icon.png")
PASS_ICON = os.path.join(THIS_FILE, "gui", "gui_images", "pass_icon.png")
INCONCLUSIVE_ICON = os.path.join(THIS_FILE, "gui", "gui_images", "inconclusive_icon.png")
FAIL_ICON = os.path.join(THIS_FILE, "gui", "gui_images", "fail_icon.png")
SKIP_ICON = os.path.join(THIS_FILE, "gui", "gui_images", "skip_icon.png")
HTML_TEMPLATE_PATH = os.path.join(THIS_FILE, "data", "html_template")

# release main feature
RELEASE_MAIN_POINTS = (
    "<h2>Features/Changes</h2><br/>"
    "&nbsp;&nbsp;- ⚡ New HTML Summary Report Look<br/>"
    "&nbsp;&nbsp;- ⚡ TESTTAG Filter Logic Selection via GUI<br/>"
    "&nbsp;&nbsp;- ⚡ Run Execution Record<br/>"
    "&nbsp;&nbsp;- ⭐ Tool APIs Doc Button Active in UIM<br/>"
    "&nbsp;&nbsp;- ⭐ TAF Helper Changes<br/>"
    "<h2>🐛 Fixes</h2><br/>"
    "&nbsp;&nbsp;- Disable error pop-ups in auto_gui mode<br/>"
)

# exit codes
SUCCESS = 0
# if any general exception occurred
GENERAL_ERR = 1
# if any one test case failed
TEST_FAILURE = 2
# if any one or more test case is unstable and no other failure happened
INCONCLUSIVE = 3
# variable to store the state (true/false) of stop button on contest gui
STOP_STATE_GUI = False


class TestVerdicts(Enum):
    """
    Class for saving values of different test verdicts currently supported for test case functions

    Note: New verdicts can be added here
    """

    UNKNOWN = 0
    PASS = 1
    FAIL = 2
    INCONCLUSIVE = 3
    SKIP = 4


class ValidFilter(Enum):
    """
    A list of valid filter to be used for test case filtering.
    """

    # Filter for tags
    TAG = "tag"


def check_latest_version():
    """
    This method checks the latest available version of ConTest

    :returns: Latest available version string and version string in tuple form
    :rtype: tuple
    """
    latest_version_str = None
    latest_version_tuple = None
    version_list = []
    try:
        with urllib.request.urlopen(URL, timeout=2) as file:
            file = file.read()
            version = file.decode().split("\n")
            for result in version:
                latest_version_match = re.match(".*v([0-9+.]+)", result)
                if latest_version_match:
                    version_list.append(tuple(map(int, (latest_version_match.group(1).split(".")))))
            if version_list:
                latest_version_tuple = max(version_list, key=lambda t: t[:])
                return ".".join(str(s) for s in latest_version_tuple), latest_version_tuple
            return None, None
    # ok to catch general exceptions
    # pylint: disable=broad-exception-caught
    except Exception:
        return latest_version_str, latest_version_tuple
