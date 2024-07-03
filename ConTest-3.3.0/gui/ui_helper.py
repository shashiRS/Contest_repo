"""
    Copyright Continental Corporation and subsidiaries. All rights reserved.

    :platform: Windows, Linux

    :synopsis:
        File containing general functions acting as helper utilities for main UI interface
"""

# disabling import error as they are installed at start of framework
# pylint: disable=import-error, no-name-in-module
import os
import platform
import subprocess
import sys
import logging
from PyQt5 import QtWidgets, QtCore, QtGui
import global_vars
from data_handling import helper


# ConTest links
CONTEST_CONFLUENCE_LINK = (
    "<a href='https://confluence.auto.continental.cloud/display/EPM/ConTest+Guidelines'>ConTest Confluence</a>"
)
FAQ_RTD_LINK = "https://cip-docs.cmo.conti.de/static/docfiles/ConTest/" + global_vars.DOC_VERSION + "/faq.html"
UIM_RTD_LINK = "https://cip-docs.cmo.conti.de/static/docfiles/ConTest/" + global_vars.DOC_VERSION + "/uim.html"
TRAINING_VIDEOS_LINK = (
    "https://cip-docs.cmo.conti.de/static/docfiles/ConTest/" + global_vars.DOC_VERSION + "/training.html"
)
FAQ_LINK = f"<a href='{FAQ_RTD_LINK}'>FAQs</a>"
TRAINING_VIDEO = f"<a href='{TRAINING_VIDEOS_LINK}'>Training Videos</a>"
PMT_SERVICE_LINK = "<a href='https://jira.auto.continental.cloud/plugins/servlet/desk/portal/1'>PMT Service Desk</a>"
PMT_VIDEO_LINK = (
    "<a href='https://confluence-adas.zone2.agileci.conti.de/download/attachments"
    "/402900537/211214c_How%20to%20Create%20a%20Ticket.mp4?version=1&modification"
    "Date=1651730331827&api=v2'>PMT Service Desk Usage Video</a>"
)


GREEN = QtGui.QColor(39, 174, 96)
RED = QtGui.QColor(203, 67, 53)
YELLOW = QtGui.QColor(252, 210, 0)
GREY = QtGui.QColor(119, 136, 153)
MSG_BOX_RED_COLOR = "#E74C3C"
MSG_BOX_BLUE_COLOR = "#127dc4"
MSG_BOX_ORANGE_COLOR = "#E67E22"

PYTHON_TESTS_QT_STR = "Python Tests"
T32_TESTS_QT_STR = "Trace32 Tests"
CANOE_TESTS_QT_STR = "CANoe Cfg Tests Modules"
TEST_TYPE_QT_STR_LIST = [PYTHON_TESTS_QT_STR, T32_TESTS_QT_STR, CANOE_TESTS_QT_STR]

# stylesheet for the status lcd for changing the background color
NON_RUNNING_LCD_NUM = "QFrame { border: 1px solid #495971; } QLCDNumber { background-color: none }"
PASSED_LCD_NUM = "QLCDNumber { background-color: rgb(39, 174, 96) }"
FAILED_LCD_NUM = "QLCDNumber { background-color: rgb(241, 124, 98 ) }"
INCONCLUSIVE_LCD_NUM = "QLCDNumber { background-color: rgb(237, 210, 76 ) }"
SKIPPED_LCD_NUM = "QLCDNumber { background-color: rgb(179, 173, 173 ) }"

# welcome message
WELCOME_MSG = f"{global_vars.FW_NAME} Framework {platform.system()} Platform"
# fetching contest root to be used later
CONTEST_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
# documentation path
USER_MANUAL = "https://cip-docs.cmo.conti.de/static/docfiles/ConTest/" + global_vars.DOC_VERSION + "/index.html"
# release notes path
RELEASE_NOTES_HTD_LINK = (
    "https://cip-docs.cmo.conti.de/static/docfiles/ConTest/"
    + global_vars.DOC_VERSION
    + "/release.html#release-"
    + global_vars.DOC_VERSION.replace(".", "-")
)
TOOL_APIS_LINK = "https://cip-docs.cmo.conti.de/ConTest/latest/tool_api_auto.html#tool-apis"
# setting PTF work space
PTF_WORK_SPACE = os.path.join(CONTEST_ROOT, "ptf")
# setting PTF documentation directories
DOC_BUILD_DIR = os.path.join(PTF_WORK_SPACE, "doc")
VERIFY_DOC_DIR = os.path.join(DOC_BUILD_DIR, "source", "verify_doc")
API_DOC_DIR = os.path.join(DOC_BUILD_DIR, "source", "api_doc")
ICON = ":/resources/gui_images/msg_icon_trans.png"
ERR_ICON = ":/resources/gui_images/msg_err_icon.png"
WARN_ICON = ":/resources/gui_images/msg_warn_icon.png"
INFO_ICON = ":/resources/gui_images/msg_info_icon.png"
PASS_ICON = ":/resources/gui_images/pass_icon.png"
FAIL_ICON = ":/resources/gui_images/fail_icon.png"
NO_STATUS_ICON = ":/resources/gui_images/no_status_icon.png"
INCONCLUSIVE_ICON = os.path.join(CONTEST_ROOT, "gui", "gui_images", "inconclusive_icon.png")
SKIP_ICON = os.path.join(CONTEST_ROOT, "gui", "gui_images", "skip_icon.png")
CANOE_ICON = os.path.join(CONTEST_ROOT, "gui", "gui_images", "canoe_icon.png")
T32_ICON = os.path.join(CONTEST_ROOT, "gui", "gui_images", "t32_icon.png")
PYTHON_ICON = os.path.join(CONTEST_ROOT, "gui", "gui_images", "python_icon.png")
CONTEST_ICON = os.path.join(CONTEST_ROOT, "gui", "gui_images", "logo_icon.png")
PENDING_ICON = os.path.join(CONTEST_ROOT, "gui", "gui_images", "pending_icon.png")
DATA_ICON = os.path.join(CONTEST_ROOT, "gui", "gui_images", "data_collect_icon.png")
GUI_ICON = os.path.join(CONTEST_ROOT, "gui", "gui_images", "gui_prepare_icon.png")
BROWSE_ICON = os.path.join(CONTEST_ROOT, "gui", "gui_images", "browse_icon.png")
CLEAR_ICON = os.path.join(CONTEST_ROOT, "gui", "gui_images", "clear_browse_icon.png")
# initial action prints
INITIAL_MSG = [
    "-" * 100,
    "ConTest " + global_vars.CONTEST_VERSION,
    "Press short key 'CTRL + n' to create new ConTest Configuration (*.ini) file",
    "Press short key 'CTRL + l' to load ConTest Configuration (*.ini) file",
    "-" * 100,
]

# CLI option dictionary
CLI_OPTIONS = {
    "cfg": None,
    "auto_mode": False,
    "auto_gui": False,
    "no_of_loops": None,
    "base_loc": None,
    "random_execution": False,
    "reverse_selection": False,
    "dark_mode": False,
    "setup_file": None,
    "filter": None,
    "report_dir": None,
}
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
TOOL_CFG_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "tool_info.ini"))

# By default filter string is "show all (default)"
DEFAULT_FILTER_STRING = "show all"
# python tests filter name
PYTHON_FILTER_NAME = "python"
# capl (.can) tests filter name
CANOE_FILTER_NAME = "canoe"
# T32 (.cmm) tests filter name
CMM_FILTER_NAME = "t32"
# parameterized tests filter name
PARAMETERIZED_FILTER_NAME = "parameterized"
GIT_TAG = f"Git Tag: '{global_vars.CONTEST_VERSION}'"

# about message
ABOUT_MSG = (
    f"<b>Continental Software Testing Tool (ConTest)</b><br/>"
    f"Release Version : {global_vars.CONTEST_VERSION}<br/><br/>"
    f"Developed by <b>AMS ADAS ENP TEMP TPT</b><br/><br/>"
    f"{GIT_TAG}<br/><br/>"
    f"{CONTEST_CONFLUENCE_LINK}<br/>"
    f"{TRAINING_VIDEO}<br/>"
    f"{FAQ_LINK}<br/><br/>"
    "More Info. at <b>Help->User Manual</b>"
)

FEATURE_MSG = (
    f"<b>Create a Feature Request by clicking {PMT_SERVICE_LINK}</b><br/><br/>"
    f"<b>Click on 'Change Request'</b><br/><br/>"
    f"Follow following steps:<br/><br/>"
    f"<b>Summary:</b> Write short summary of your request<br/>"
    f"<b>Your Organization:</b> Select your org<br/>"
    f"<b>Requesting Project:</b> Select your project or select Other if not found<br/>"
    f"<b>Tool/Process Area (mandatory):</b> ConTest Test Tool (ADAS)<br/>"
    f"<b>Description:</b> Write description of your request<br/>"
    f"<b>Impact:</b> Select your request impact<br/><br/>"
    f"Once request has been created it will be routed to ConTest team for support."
    f"<br/><br/>"
)

PMT_VIDEO_MSG = f"For details on how to create tickets using PMT Service Desk Platform, take a look at {PMT_VIDEO_LINK}"


DOC_ACCESS_MSG = (
    f"<b>Following information will help you to get access to User Manual.</b><br/><br/>"
    f"1. Open {PMT_SERVICE_LINK}<br/>2. Click <b>Access Request</b><br/>"
    f"3. Fill the fields with data:<br/><br/>"
    f"&nbsp;&nbsp;&nbsp;&nbsp;<b>Summary:</b> Access to ADAS CIP Doc Server<br/>"
    f"&nbsp;&nbsp;&nbsp;&nbsp;<b>Your Organization:</b> AMS ADAS<br/>"
    f"&nbsp;&nbsp;&nbsp;&nbsp;<b>Requesting Project:</b> 'Pick your relevant project'<br/>"
    f"&nbsp;&nbsp;&nbsp;&nbsp;<b>Tool/Instance:</b> CIP Docs (ADAS)<br/>"
    f"&nbsp;&nbsp;&nbsp;&nbsp;<b>Approver:</b> 'Your Manager or Other Lead'<br/>"
    f"&nbsp;&nbsp;&nbsp;&nbsp;<b>Description:</b> Need access to ConTest tool doc<br/><br/>"
    f"4. Click Create<br/><br/>After request completion you will get access to "
    f"online User Manual."
)

FEAT_CREATE_VIDEO_LINK = r"https://web.microsoftstream.com/video/07171b3c-dcb8-4cb1-8f8f-bb9d1503fd06"
BUG_CREATE_VIDEO_LINK = r"https://web.microsoftstream.com/video/d395c5dc-558d-4f12-990b-5dfd2fb9232a"
DOC_ACCESS_VIDEO_LINK = r"https://web.microsoftstream.com/video/0ab492f3-7463-430c-86b9-7f99bd990188"

BUG_MSG = (
    f"<b>Create a Problem Report by clicking {PMT_SERVICE_LINK}</b><br/><br/>"
    f"<b>Click on 'Problem Report'</b><br/><br/>"
    f"Follow following steps:<br/><br/>"
    f"<b>Summary:</b> Write short summary of your problem<br/>"
    f"<b>Your Organization:</b> Select your org<br/>"
    f"<b>Requesting Project:</b> Select your project or select Other if not found<br/>"
    f"<b>Tool/Process Area (mandatory):</b> ConTest Test Tool (ADAS)<br/>"
    f"<b>Description:</b> Write description of your problem<br/>"
    f"<b>Impact:</b> Select your problem impact<br/><br/>"
    f"Once problem report has been created it will be routed to ConTest team for support."
    f"<br/><br/>"
)

EXT_SCRIPTS_RELOAD_MSG = (
    "<b>Do you want to reload Python scripts mentioned in Misc. Section "
    "of loaded configuration?</b><br/><br/>"
    "<b>Misc. Paths are mentioned in Configuration.</b><br/>{}<br/><br/>"
    "<b>Misc. Section or Additional Paths</b> are location(s) where some "
    "Python scripts outside Python Tests Locations are located.<br/><br/>"
    "<b>NOTE:</b><br/>"
    "Please note that in reloading step of Python scripts "
    "<b>recompilation</b> and <b>re-execution</b> of scripts will happen. "
    "So if you have global code in scripts then it will be executed during "
    "reload step."
)

CANOE_PREP_MSG = (
    "Starting to prepare data from CANoe Cfg<br/><br/>"
    "<b>Note:</b> The preparation step for CANoe might take some time so please be"
    " patient. After preparation step test modules in CANoe configuration will be "
    "shown on ConTest GUI for selection and saving purpose.<br/><br/>"
    "Following steps will be performed:<br/>"
    "    - CAPL tests data fetched from CANoe cfg<br/>"
    "    - CAPL tests shown on GUI for selection<br/><br/>"
    "<b>CANoe Cfg:</b> {}<br/><br/>"
    "<b>Please also make sure that your CANoe & Vector Hardware setup "
    "is working fine.</b><br/><br/>For details please check console."
)

CTE_CANOE_PREP_MSG = (
    "Starting to prepare data from CANoe Cfg via CTF<br/><br/>"
    "<b>Note:</b> The preparation step might take some time so please be "
    "patient. After preparation step test modules in CANoe configuration will "
    "be shown on ConTest GUI for selection and saving purpose.<br/><br/>"
    "Following steps will be performed:<br/>"
    "    - CTF will be called to add and save CAPL tests in CANoe cfg.<br/>"
    "    - CAPL tests data fetched from CANoe cfg<br/>"
    "    - CAPL tests shown on GUI for selection<br/><br/>"
    "<b>CANoe Cfg:</b> {}<br/>"
    "<b>CTF Cfg:</b> {}<br/><br/>"
    "<b>Please also make sure that your CANoe & Vector Hardware setup "
    "is working fine with CTF as well as CANoe.</b><br/><br/>"
    "For details please check console."
)

CANOE_BACKPORT_MSG = (
    "<b>NOTE:</b><br/>Your ConTest cfg contains path to CAPL tests which is"
    " now changed to CANoe cfg path.<br/>This means that you can now mention "
    "the path of CANoe cfg directly in ConTest cfg and all test modules in "
    "CANoe cfg will appear on ConTest GUI for selection and saving purpose.<br/>"
    "<br/>You can do this from <b>Menu->Edit Config</b> option."
)

HELPER_FILE_MSG = (
    "<br/>Do you want to create helper files?<br/><br/>If you want to create an "
    "example <b>setup.pytest, swt_sample_test.pytest and a README </b> file at the "
    "location of the python test case, please select <b>'yes'</b>. <br/>"
    "<br/>These files are intended to help new users get started with ConTest."
)

# storing original 'sys.stdout' object in order to print information on console
STD_OUT_ORIGINAL = sys.stdout

# dictionary template for storing test of different categories in cfg file
TESTS_FOR_CFG = {"selected_tests": [], "cmm_tests": [], "capl_tests": []}

# short cut information
SHORT_CUTS = [
    {"Option": "Run Tests", "Short Cut": "ctrl+r"},
    {"Option": "Reload Tests", "Short Cut": "ctrl+shift+l"},
    {"Option": "Stop Tests", "Short Cut": "ctrl+k"},
    {"Option": "Create Config", "Short Cut": "ctrl+n"},
    {"Option": "Load Config", "Short Cut": "ctrl+l"},
    {"Option": "Generate Tests", "Short Cut": "ctrl+g"},
    {"Option": "Edit Config", "Short Cut": "ctrl+e"},
    {"Option": "Save Config", "Short Cut": "ctrl+s"},
    {"Option": "Save as Config", "Short Cut": "ctrl+shift+s"},
    {"Option": "Reset", "Short Cut": "ctrl+shift+r"},
    {"Option": "Exit", "Short Cut": "ctrl+q"},
]


def run_subprocess(cmd_to_run):
    """
    Method to running a command via subprocess

    :param str cmd_to_run: Command to run via subprocess
    """
    with subprocess.Popen(
        cmd_to_run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    ) as process:
        # start process and fetch process output and error
        output, error = process.communicate()
    # throw back output and error
    return output, error


def pop_up_msg(title, msg_str, auto_mode=False):
    """
    Function for a generic pop up message function

    :param object title: Pop-up window title
    :param str msg_str: Pop-up message
    :param bool auto_mode: Framework auto running mode. Default is False

    :returns: True, in case YES or OK (default response). False, in case of NO
    :rtype: bool
    """
    cwd = os.path.dirname(os.path.realpath(__file__))
    info_icon = os.path.abspath(os.path.join(cwd, "gui_images", "info_icon.png"))
    quest_icon = os.path.abspath(os.path.join(cwd, "gui_images", "quest_icon"))
    err_icon = os.path.abspath(os.path.join(cwd, "gui_images", "err_icon"))
    win_icon = os.path.abspath(os.path.join(cwd, "gui_images", "logo_icon.png"))
    # only show pop-up when not in auto mode
    if not auto_mode:
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle(title.name)
        msg.setText(msg_str)
        msg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        msg.setWindowIcon(QtGui.QIcon(win_icon))
        if title == helper.InfoLevelType.INFO:
            msg.setIconPixmap(QtGui.QPixmap(info_icon).scaledToHeight(80, QtCore.Qt.SmoothTransformation))
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        elif title == helper.InfoLevelType.QUEST:
            msg.setIconPixmap(QtGui.QPixmap(quest_icon).scaledToHeight(80, QtCore.Qt.SmoothTransformation))
            msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        elif title == helper.InfoLevelType.ERR:
            msg.setIconPixmap(QtGui.QPixmap(err_icon).scaledToHeight(80, QtCore.Qt.SmoothTransformation))
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        # execute the pop up message and get the outcome in result variable
        result = msg.exec_()
        if result == QtWidgets.QMessageBox.No:
            ret_var = False
        else:
            # return true in all other cases
            ret_var = True
        return ret_var
    # when in auto mode then don't show pop-up messages
    return True


def custom_except_hook(error_type, error_msg, traceback):
    """
    This method is for handling exceptions raised when using GUI. PyQt5(QApplication.exec_) does not
    handle the exceptions, instead exits the GUI with error. This Hook helps GUI remain alive when
    exceptions are raised

    :param class error_type: type of exception raised
    :param str error_msg: error message to be printed
    :param obj traceback: most recent call last
    """
    # call the default handler
    sys.__excepthook__(error_type, error_msg, traceback)


def help_info(title="", info=""):
    """
    Method for displaying help related information

    :param str title: Title for the window
    :param str info: Message to be displayed on window
    """
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle(title)
    msg.setWindowIcon(
        QtGui.QIcon(
            os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "gui_images", "logo_icon.png"))
        )
    )
    msg.setTextFormat(QtCore.Qt.RichText)
    msg.setText(info)
    msg.exec_()


def ask_for_helper_files():
    """
    Method for pop-up asking user whether to create helper files or not.

    :returns: 'QtWidgets.QMessageBox.Yes' if the user selects option 'Yes'
               'QtWidgets.QMessageBox.No' if the user selects option 'No' or closes window.

    :rtype: QMessageBox.StandardButton
    """
    option_box = QtWidgets.QMessageBox()
    option_box.setWindowIcon(
        QtGui.QIcon(
            os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "gui_images", "logo_icon.png"))
        )
    )
    option_box.setTextFormat(QtCore.Qt.RichText)
    option_box.setText(HELPER_FILE_MSG)
    option_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    option_box.setEscapeButton(QtWidgets.QMessageBox.No)
    result = option_box.exec_()
    return result


class QtHandler(logging.Handler, QtCore.QObject):
    """
    A handler for logging signals to be displayed on a qt gui.
    Since the gui might run in a different thread than the function that initiated logging,
    this handler will only emit a qt signal that triggers a defined log function.
    This log function will then update the ui.
    """

    # The signaller to be used to notify the gui
    signaller = QtCore.pyqtSignal(logging.LogRecord)

    def __init__(self, log_function, *args, **kwargs):
        """
        Initializes the gui log handler.

        :param log_function The log function that will update the ui.
        :param args: Additional arguments for logging.Handler
        :param kwargs: Additional keyword arguments logging.Handler
        """
        super().__init__(*args, **kwargs)
        # Make sure that all qt classes are properly initialized. Default inheritance handling
        # seems somehow to fail here.
        # pylint: disable=bad-super-call
        super(logging.Handler, self).__init__(*args, **kwargs)
        super(QtCore.QObject, self).__init__()
        self.signaller.connect(log_function)

    def emit(self, record):
        """
        Sends the record as a signal to the connected log function.

        :param logging.LogRecord record: The record to log.
        """
        self.signaller.emit(record)


# public methods are not required at the moment
# pylint: disable=too-few-public-methods
class CommSignals(QtCore.QObject):
    """
    Custom signal class is defined here to establish a communication channel
    between GUI and PTF test runner and engine.
    This captures signals emitted from PTF test runner and engine to inform
    GUI regarding necessary steps to be taken based on the emitted signals.
    """

    def __init__(self):
        """Constructor"""
        # super is required to make connections with UIController class
        # it's PyLint issue
        # pylint: disable=useless-super-delegation
        super().__init__()

    def emit_sig(self, emit_signal_type, signal_data):
        """
        Method for handling emitted signals from 'test_runner' module

        :param str emit_signal_type: For detecting type emitted signal in order to call respective
            methods
        :param list/str signal_data: Signal data to be processed
        """
        if emit_signal_type == "result":
            # emit signal for getting test case parameters after test case
            # completion this signal which is sent by gui_notifier.py watcher
            # contains test case parameters (test_name, executionTime, status)
            #
            # GUI grabs this signal and shows info on display e.g. color change
            # for test passed or failed etc. more info can be added in signal
            # if required
            self.result_sig.emit(signal_data)
        elif emit_signal_type == "test_run_started":
            # emit the signal to rebuild the list of executed tests
            self.test_run_started_sig.emit(signal_data)
        # emit the signal to call the semi automation pop up window
        elif emit_signal_type == "test_manual_input":
            self.call_manual_input_window.emit(signal_data)
        # emit the signal to call the parametrized test case from GUI to update for test runner
        elif emit_signal_type == "parameterized_tc_from_gui":
            self.call_check_uncheck_parameterized_tc.emit(signal_data)
        else:
            # do nothing
            pass


def update_ui_with_tests(tests, gui_obj, logger, test_type):
    """
    Method for updating UI tree view with selected tests

    :param list tests: List containing selected tests in cfg for a specific test type
    :param object gui_obj: UIController class object
    :param object logger: Logger object
    :param string test_type: Test type (python, cmm or capl)
    """
    if tests:
        logger.info("%s %s test(s) in cfg file", len(tests), test_type)
        # extracting test case names from selected test list 'tests_from_config' without
        # brackets. In release v1.4 changes were done to discard brackets from test names on
        # GUI in order to make status color changes work properly. If an old saved configuration
        #  (v1.0, v1.1) which contains the brackets in selected test names is loaded in new
        # version then tests in config file will be discarded. To cater this '()' are neglected
        # with below line to make it backward compatible
        tests_from_config = [test.split("(")[0] for test in tests]
        # Selecting tests on UI
        for test in tests_from_config:
            item = gui_obj.test_cases_model.findItems(test, QtCore.Qt.MatchFixedString | QtCore.Qt.MatchRecursive, 0)

            if item:
                item[0].setCheckState(QtCore.Qt.Checked)
                # updating tree view items check states
                proxy_ind = gui_obj.filter_proxy_model.mapFromSource(item[0].index())
                gui_obj.items_check_state_handler(proxy_ind)
            else:
                # storing tests not found in a list i.e. missing tests
                logger.warning("%s not found", test)
                gui_obj.data.test_runner_data["missing_tests"].append(test)

            # warn user about duplicated naming of items
            if len(item) > 1:
                logger.warning(
                    "'%s' item found more than once, the selections will be affected, use unique names", test
                )


def get_tests_for_saving(tests_dict):
    """
    Method for getting tests names extracted from selected tests data dictionary

    :param dictionary tests_dict: dictionary containing test names

    :return: dictionary containing tests to save
    :rtype: dictionary
    """
    tests_to_save = {
        "selected_tests": [test_object.name for test_object in tests_dict["py_tests"]],
        "cmm_tests": [test_object.name for test_object in tests_dict["cmm_tests"]],
        "capl_tests": tests_dict["capl_tests"],
    }
    # before saving tests in cfg file update the test dictionary with selections on GUI
    return tests_to_save
