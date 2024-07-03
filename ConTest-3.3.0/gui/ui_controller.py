"""
    Copyright Continental Corporation and subsidiaries. All rights reserved.

    :platform: Windows, Linux

    :synopsis:
        This file contains code for controlling ConTest GUI.
        It takes actions based on user selections e.g. loading and running of test cases.
"""

# disabling import error as they are installed at start of framework
# pylint: disable=import-error, no-name-in-module
# standard python imports
import copy
import ctypes
import logging
import os
import platform
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QAction
from PyQt5.QtCore import Qt, QRegExp, QPoint

import qdarkstyle

# framework related imports
import global_vars
from data_handling import common_utils, helper, prepare_test_data
from uim import uim
from . import ui_helper
from .gui_utils import config_editor, project_config_handler, what_new_window
from .gui_utils import test_template, tests_generator, semi_automation, test_case_parameterized, uim_manager
from .gui_utils import shortcut_information
from .gui_utils.user_config_handler import UserConfigHandler
from .ui_states import UIStates


# assigning custom exception hook to standard system exception hook in order to report raised
# errors during normal UI run
sys.excepthook = ui_helper.custom_except_hook

LOG = logging.getLogger("UI")
RETURN_CODE = global_vars.SUCCESS


# pylint: disable=too-many-instance-attributes, too-many-public-methods, too-many-lines, no-member, too-many-locals
class UIController(UIStates, ui_helper.CommSignals):
    """
    Main GUI controller class which inherits the state class.
    This class is responsible for controlling some common interfaces.
    """

    # The colors for the different logging levels
    COLORS = {
        logging.DEBUG: ui_helper.MSG_BOX_BLUE_COLOR,
        logging.INFO: ui_helper.MSG_BOX_BLUE_COLOR,
        logging.WARNING: ui_helper.MSG_BOX_ORANGE_COLOR,
        logging.ERROR: ui_helper.MSG_BOX_RED_COLOR,
        logging.CRITICAL: ui_helper.MSG_BOX_RED_COLOR,
    }
    # assigned signals handlers, these signals will be emitted by "test_runner" containing information about tests
    # execution
    result_sig = QtCore.pyqtSignal(dict, name="test_result_params")
    # creating pyqt signal which is used for manual_verification API
    call_manual_input_window = QtCore.pyqtSignal(list, name="test_manual_input")
    test_run_started_sig = QtCore.pyqtSignal(list, name="test_run_started")
    call_check_uncheck_parameterized_tc = QtCore.pyqtSignal(tuple, name="parameterized_tc_from_gui")

    # This variable is accessed before the constructor call, so added here.
    # edit config flag as boolean variable, by default false
    edit_config_flag = False
    prev_selected_filters = []

    # the initialization of variables are required in constructor for proper ui functionality
    # pylint: disable=too-many-statements

    def __init__(self, args=None, selected_tests_exec_record=None):
        """
        Constructor responsible for initializing variables and making UI connections

        :param argparser args: Arguments coming from cli
        :param list selected_tests_exec_record: Selected test cases that needs to be run based on selected verdict,
                when run_exec_record was requested on CLI
        """
        # super initialization to access parent or base class method or data
        super().__init__()
        # assigning "UIController" object to "setupUi" that is designer interface
        self.setupUi(self)
        # getting the position of UI window during previous run
        position = self.user_config.last_position
        # getting the size of UI window during previous run
        size = self.user_config.last_size
        # moving UI window to last opened position
        self.move(QPoint(position[0], position[1]))
        # resizing UI window to last opened coordinates
        self.resize(size[0], size[1])
        # hide the message log area(event log dock widget)
        self.dockWidget.hide()
        # bool variable which shall be True when its detected that ptf.ptf_utils.decorator.custom_setup.custom_setup
        # is used in a test function from user side
        self.custom_decorator_used = False
        # bool variable which shall be true if run execution record was selected in CLI
        self.exec_record_requested = args.subparser_name == "run_exec_record"
        # selected test cases to run with execution record data
        self.selected_tests_exec_record = selected_tests_exec_record
        # save run mode option to pass it to test runner
        self.run_mode = args.r
        # save timestamp enable flag to pass it to test runner
        self.timestamp_en = args.timestamp
        # save  external paths from CLI  to pass it to test runner
        self.external_paths_cli = args.e
        # Initialize logging on the UI
        self.__initialize_logging()
        # assigning argument(s) in to a variable
        self.args = self.__handle_args(args)
        self.what_new_window_obj = what_new_window.WhatNewWindow()
        # taking the UI to an initial state in which only few things will be active
        self.__gui_initial_state()
        # configurator object container
        # TODO Generate dynamically for each call
        self.configurator_obj = config_editor.ConfigEditor(self)
        # The project configuration that is currently loaded
        self.project_configuration = None
        # test generator object container
        # TODO Generate dynamically for each call
        self.test_generator_obj = tests_generator.TestGenerator(self)
        self.uim_manager = uim_manager.UimGui()
        # short cut information object container
        self.short_cut_info_obj = shortcut_information.ShortCutsInfo()
        # configurator editor object container
        self.edit_configurator_obj = None
        # SemiAutomation object container
        self.semi_auto_obj = semi_automation.SemiAutomation(self)
        # Test case parameter view object container
        self.test_case_parameter_obj = None
        # container for storing tree model data
        self.test_cases_model = None
        self.current_loaded_cfg = None
        # container for prepare data class
        self.data = None
        # creating object of proxy model for live filtering of data i.e. test cases
        self.filter_proxy_model = QtCore.QSortFilterProxyModel()
        # list which will contain selected test cases
        # this list will be used for updating Test Stats LCD's as well as making checks during
        # save or save as options
        self.selected_tests_on_gui = []
        # dictionary for storing selected tests on UI for different test types which will be
        # required during saving cfg action
        self.tests_for_saving_action = copy.copy(ui_helper.TESTS_FOR_CFG)
        # creating an instance of ThreadClass responsible for test execution
        self.thread_class = ThreadClass(self)
        # variable storing if tests execution started or not
        self.tests_running = False
        # store the list of expanded QStandardItem text
        self.__expanded_state = []
        # container for storing selected setup file
        self.setup_file = None
        # list for storing failed test cases
        self.__failed_tests = []
        # list for storing failed items from main tree view
        self.tree_item_failure_list = []
        # list for storing inconclusive items from main tree view
        self.tree_item_inconclusive_list = []
        self.uim_info_thread = UimInfoThread(self)
        # make ui connections and signals
        self.__make_ui_connections()
        self.__make_signal_connections()
        # declaring a QCompleter object
        self.completer = QtWidgets.QCompleter()
        # setting-up search bar
        self.__setup_search_bar()
        # all lcd related data variables in this dictionary are initialized
        self.lcd_data = {
            "total_tests_appearing": [],
            "total_selected_tests": [],
            "passed_test_cases": 0,
            "inconclusive_test_cases": 0,
            "skipped_test_cases": 0,
            "failed_test_cases": 0,
            "total_execution_time": {"hours": 0, "mins": 0, "secs": 0},
            "test_case_exe_time": {"mins": 0, "secs": 0, "msecs": 0},
            "progress_bar_value": float(0),
        }
        # tests status icon (pass/fail/un-known) dictionary
        self.status_icon = {
            "pass": QtGui.QIcon(ui_helper.PASS_ICON),
            "fail": QtGui.QIcon(ui_helper.FAIL_ICON),
            "inconclusive": QtGui.QIcon(ui_helper.INCONCLUSIVE_ICON),
            "skip": QtGui.QIcon(ui_helper.SKIP_ICON),
            "no_status": QtGui.QIcon(ui_helper.NO_STATUS_ICON),
        }
        # test types icons
        self.test_type_icons = {
            "contest": QtGui.QIcon(ui_helper.CONTEST_ICON),
            "python": QtGui.QIcon(ui_helper.PYTHON_ICON),
            "t32": QtGui.QIcon(ui_helper.T32_ICON),
            "canoe": QtGui.QIcon(ui_helper.CANOE_ICON),
        }
        # variable storing stop button state
        self.stop_state = False
        # list for storing QStandardItem object for all test cases which will help to access tests qt items objects
        # for various purposes e.g. changing checkbox states in case of reversing tests selections etc.
        self.tests_q_st_items_objs = []
        # Initializing the filter tags combo box
        self.__initialize_filter_tags_combox()
        # if user gave some arguments then take actions based on them
        self.__take_actions_on_args()
        # print initial message for user help
        for line in ui_helper.INITIAL_MSG:
            LOG.info(line)
        # store last html report path
        self.last_html_report_path = None
        # store last report folder path
        self.last_report_folder_path = None
        # store last external report folder path
        self.last_external_report_folder_path = None
        # if manual mode then grap contest tool utils wheel packages in the background
        if not self.args["auto_gui"]:
            self.__utility_install_manager()

    def __initialize_filter_tags_combox(self):
        """
        Initializes the filter tags combo box with initial settings
        """
        # Make the combo editable to set a custom text, but readonly
        self.stage_select_combobox.setEditable(True)
        self.stage_select_combobox.lineEdit().setReadOnly(True)
        # Hide and show popup when clicking the line edit
        self.stage_select_combobox.installEventFilter(self)
        # setting the dark color to the combo box line edit
        if self.user_config.darkmode:
            dark_palette = QtGui.QPalette()
            dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(35, 35, 35))
            self.stage_select_combobox.lineEdit().setPalette(dark_palette)

    def __initialize_logging(self):
        """
        Initializes the logging framework to display log messages on our UI and console.
        """
        self.qt_log_handler = ui_helper.QtHandler(self.__log)
        # We don't want to show these logs in the testcases, so use sys.stdout here
        # (in contrary to root logger)
        console_log_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("[%(levelname)s@%(asctime)s] %(message)s", datefmt="%H:%M.%S")
        self.qt_log_handler.setFormatter(formatter)
        console_log_handler.setFormatter(formatter)

        for logger in (
            LOG,
            prepare_test_data.LOG,
            config_editor.LOG,
            tests_generator.LOG,
            project_config_handler.LOG,
            # Get the testrunner logger this way to avoid import of test_runner
            # at this time. The import is not working at this time since sys.path
            # is modified only at a later step.
            logging.getLogger("TEST_RUNNER"),
        ):
            logger.addHandler(self.qt_log_handler)
            logger.addHandler(console_log_handler)
            logger.propagate = False

    @pyqtSlot(logging.LogRecord)
    def __log(self, record):
        log_msg = self.qt_log_handler.format(record)
        color = self.COLORS.get(record.levelno)
        self.event_log_handler(color)
        info_html = f'<span style="color: {color}">{log_msg}</span>'
        # printing the information
        # "\n" is added when append the string in ui-plain text to the next line, other wise in
        # ubuntu application crashes when mouse cursor is moved on plaintext area.
        self.message_plaintextedit.appendHtml(info_html + "\n")

    def __make_ui_connections(self):
        """
        This method connects pyqt signals coming from various widgets to the UI controller methods.
        """
        self.clear_status_txt_pushbutton.clicked.connect(self.clear_status_msg)
        self.runtest_pushbutton.clicked.connect(self.run_tests)
        self.stop_pushbutton.clicked.connect(self.__stop_tests)
        self.action_user_manual.triggered.connect(self.__open_user_manual)
        self.action_release_notes.triggered.connect(self.__open_release_notes)
        self.main_treeview.clicked.connect(self.items_check_state_handler)
        self.main_treeview.doubleClicked.connect(self.__select_on_double_click)
        self.main_treeview.customContextMenuRequested.connect(self.__action_menu_context)
        self.main_treeview.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
        self.main_treeview.keyPressEvent = self.__handle_main_treeview_key_press_event
        self.menu_context = QtWidgets.QMenu(self.main_treeview)
        self.filter_proxy_model.dataChanged.connect(self.update_appear_selected_tests_count)
        self.actionLoad_config.triggered.connect(self.__load_core_configuration)
        self.actionCreate_config.triggered.connect(self.__create_configuration)
        self.actionEdit_Config.triggered.connect(self.edit_configuration)
        self.action_generate_tests.triggered.connect(self.__generate_tests)
        self.actionSave_Config.triggered.connect(self.__save_config)
        self.actionSave_as_config.triggered.connect(self.__save_as_config)
        self.action_short_cuts.triggered.connect(self.__shortcuts)
        self.action_about.triggered.connect(lambda: ui_helper.help_info(title="About", info=ui_helper.ABOUT_MSG))
        self.action_report_open.triggered.connect(lambda: self.open_folder("report"))
        self.action_external_report_open.triggered.connect(lambda: self.open_folder("external_report"))
        self.action_open_base_loc.triggered.connect(lambda: self.open_folder("base_loc"))
        self.action_open_pytest_loc.triggered.connect(lambda: self.open_folder("py_loc"))
        self.action_doc_access_info.triggered.connect(
            lambda: ui_helper.help_info(title="How to Access User Manual", info=ui_helper.DOC_ACCESS_MSG)
        )
        self.action_create_feature_video_2.triggered.connect(lambda: webbrowser.open(ui_helper.FEAT_CREATE_VIDEO_LINK))
        self.action_create_bug_video_2.triggered.connect(lambda: webbrowser.open(ui_helper.BUG_CREATE_VIDEO_LINK))
        self.action_doc_access_video.triggered.connect(lambda: webbrowser.open(ui_helper.DOC_ACCESS_VIDEO_LINK))
        self.action_open_html_report.triggered.connect(self.open_html_report)
        self.action_open_txt_report.triggered.connect(self.open_txt_report)
        self.action_open_json_report.triggered.connect(self.open_json_report)
        self.action_open_xml_report.triggered.connect(self.open_xml_report)
        self.action_open_cathat_xml_report.triggered.connect(self.open_cathat_xml_report)
        self.action_open_setup_file.triggered.connect(self.open_setup_file)
        self.action_config_file_data.triggered.connect(self.view_config_data)
        self.action_Line_wrap_output_log.triggered.connect(self.line_wrap_log_prints)
        # enabling auto-scrolling of message area
        self.message_plaintextedit.ensureCursorVisible()
        # grabbing the object of out console's vertical scroll bar and assigning
        # slot (method) '__console_slider_moved' to it's signal 'actionTriggered'
        console_vertical_slider = self.output_console_textedit.verticalScrollBar()
        console_vertical_slider.actionTriggered.connect(self.__console_slider_moved)
        self.action_create_sample_setup_file.triggered.connect(lambda: self.__generic_new_file("setup_file"))
        self.action_create_sample_pytest_file.triggered.connect(lambda: self.__generic_new_file("pytest_file"))
        self.slider_dark_mode.sliderPressed.connect(self.__slider_toggle)
        self.slider_dark_mode.valueChanged.connect(self.__dark_mode)
        self.action_reopen_last_opened_configuration.triggered.connect(self.__reopen_last_clicked)
        self.user_config.last_configurations_changed.connect(self.__update_recent_configurations)
        # timer shows execution time of the test cases
        self.timer = QtCore.QTimer(self)
        # connecting the timer with __display_time function
        self.timer.timeout.connect(self.__display_time)
        self.reload_pushbutton.clicked.connect(self.reload_test_cases)
        # connecting output table's item clicked signal to specific slot 'self.__move_to_text'
        self.output_tablewidget.itemClicked.connect(self.__move_to_text)
        self.output_tablewidget.customContextMenuRequested.connect(self.__action_output_display_menu_context)
        self.menu_select_setup_pytest.triggered.connect(self.__select_setup_file)
        # single test case timer
        # this timer shows individual execution time of each test case
        self.tc_timer = QtCore.QTimer(self)
        # connecting test case timer with __display_execution_time method
        self.tc_timer.timeout.connect(self.__display_execution_time)
        # setting timer as a 'precise type', by default its coarse type (rounding off)
        self.tc_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.msg_toolButton.clicked.connect(self.event_log)
        self.expand_tree_pushbutton.clicked.connect(self.expand_collapse_tree)
        self.main_treeview.expanded.connect(lambda: self.__change_button_text("Collapse All"))
        self.main_treeview.collapsed.connect(lambda: self.__change_button_text("Expand All"))
        self.action_create_feature.triggered.connect(
            lambda: ui_helper.help_info(title="Create Feature Request", info=ui_helper.FEATURE_MSG)
        )
        self.action_create_bug.triggered.connect(
            lambda: ui_helper.help_info(title="Create Problem Report", info=ui_helper.BUG_MSG)
        )
        self.action_pmt_service_desk_video.triggered.connect(
            lambda: ui_helper.help_info(title="PMT Service Desk Usage Video", info=ui_helper.PMT_VIDEO_MSG)
        )
        self.action_faqs.triggered.connect(lambda: webbrowser.open(ui_helper.FAQ_RTD_LINK))
        self.action_training_videos.triggered.connect(lambda: webbrowser.open(ui_helper.TRAINING_VIDEOS_LINK))
        self.stage_select_combobox.view().pressed.connect(self.filter_tag_selected)
        self.cb_all_tags.clicked.connect(self.all_tags_checked_unchecked)
        self.cb_or_tags_filter.clicked.connect(self.or_tags_filter_logic)
        self.cb_and_tags_filter.clicked.connect(self.and_tags_filter_logic)
        self.cb_run_unselected.clicked.connect(self.handle_tests_reverse_selections)
        self.action_uim.triggered.connect(self.__open_uim)
        self.action_uim_doc.triggered.connect(lambda: webbrowser.open(ui_helper.UIM_RTD_LINK))

    def __open_uim(self):
        """
        Method to start UIM UI
        """
        self.uim_manager.init_state()

    def __utility_install_manager(self):
        """
        Method to start UIM Info collection thread
        """
        self.uim_info_thread.start()

    # pylint: disable=invalid-name
    # cannot change name it's an internal built-in pyqt function and here we are over-riding it for
    # a logic
    def __handle_main_treeview_key_press_event(self, event):
        """
        Method for selecting or de-selecting set of selected rows (tests) on main tree view

        :param obj event: Key pressed event to be analyzed
        """
        if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            selected_rows = self.main_treeview.selectionModel().selectedRows()
            for row in selected_rows:
                self.__select_on_double_click(row)
            ui_helper.pop_up_msg(helper.InfoLevelType.INFO, "Multiple tests selections/de-selections done.")

    @staticmethod
    def __show_in_explorer(filename):
        """
        Method for showing the given file in the folder
        :param string filename: Path of the file that has to be shown in explorer
        """
        LOG.info("Showing the file '%s' in the folder...", filename)
        try:
            if platform.system() == "Windows":
                # this is just to open the folder and no other action is performed
                # pylint: disable=consider-using-with
                subprocess.Popen(rf'explorer /select,"{filename}"')
            else:
                # this is just to open the folder and no other action is performed
                # pylint: disable=consider-using-with
                subprocess.Popen(
                    ("xdg-open", os.path.dirname(filename)), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
                )
        except IOError as error:
            LOG.error(error)

    @staticmethod
    def __open_in_editor(filename):
        """
        Method for opening the given file onto machine's default editor
        :param string filename: Path of the file that has to be opened
        """
        LOG.info("Opening the file '%s' in your default editor...", filename)
        try:
            if platform.system() == "Windows":
                os.startfile(filename)
            else:
                subprocess.call(("xdg-open", filename))
        except IOError as error:
            LOG.error(error)

    def __action_menu_context(self, event):
        """
        Method for creating the sub menu (or menu context) for all test files on main_treeview.
        Here we are adding the following actions:
        1. action to open the selected file on machine's default editor
        2. action to show selected file in explorer

        :param QPoint event: Coordinates of the position where mouse was clicked
        """
        # list of all available test files
        test_files = []
        # test files extensions
        test_files_extensions = (".pytest", ".cmm")
        # getting all available test files
        test_files.extend(self.data.get_pytest_files())
        test_files.extend(self.data.get_cmm_files())
        # Capture the currently clicked item on main_treeview
        for selected_item in self.main_treeview.selectedIndexes():
            test_name = selected_item.data()
            # checking if item data is not 'none' type and is a test file
            if test_name and test_name.endswith(test_files_extensions):
                # clear added actions to avoid duplicity
                self.menu_context.clear()
                # adding edit action to the menu context
                action_edit = self.menu_context.addAction("Open in Editor")
                # adding show in explorer action to the menu context
                action_show_in_exp = self.menu_context.addAction("Show in Explorer")
                # display the menu on mouse clicked event position
                action = self.menu_context.exec_(self.main_treeview.mapToGlobal(event))
                filename = [file for file in test_files if test_name in file]
                # checking if the file exists and then open, if not prompt the user
                if os.path.exists(filename[0]):
                    if action == action_edit:
                        # open the user selected file into editor
                        self.__open_in_editor(filename[0])
                    elif action == action_show_in_exp:
                        # show the user selected file into explorer
                        self.__show_in_explorer(filename[0])
                else:
                    msg = f"The file '{filename[0]}' does not exist!!"
                    LOG.error(msg)
                    ui_helper.pop_up_msg(helper.InfoLevelType.ERR, msg_str=msg)
        # context menu for Open Parameterized Values View
        # reading the test case name from the first column 0
        test_case_name = self.main_treeview.selectedIndexes()[0].data()
        # reading the tag name from the first column 1
        test_case_name_tag = self.main_treeview.selectedIndexes()[1].data()
        if ui_helper.PARAMETERIZED_FILTER_NAME in test_case_name_tag:
            # clear added actions to avoid duplicity
            self.menu_context.clear()
            # adding edit action to the menu context
            action_open = self.menu_context.addAction("Open Parameterized Values View ")
            # display the menu on mouse clicked event position
            action = self.menu_context.exec_(self.main_treeview.mapToGlobal(event))
            if action == action_open:
                test_data_dict = self.data.get_python_test_data()
                test_data = test_data_dict[test_case_name]
                self.test_case_parameter_view(test_data)

    def __action_output_display_menu_context(self, event):
        """
        Method for creating the sub menu (or menu context) for all test files on output table widget
        display. Here we are adding the following actions:
        1. action to open the selected test case report in html format
        2. action to open the selected test case report in txt format

        :param QPoint event: Coordinates of the position where mouse was clicked
        """
        # Capture the currently clicked item on output display table widget

        selected_item = self.output_tablewidget.itemAt(event)
        # check the selected item is test case, 0- column is test case and 1 -column  execution time
        if selected_item is not None:
            if selected_item.column() == 0:
                # get the executed test case name
                test_name = self.output_tablewidget.item(selected_item.row(), selected_item.column()).text()
                # test_name.replace(':', '')
                # get the executed test case report path
                tc_html_report_path = os.path.join(self.last_html_report_path, test_name.replace(":", "") + ".html")
                tc_txt_report_path = os.path.join(self.last_report_folder_path, test_name.replace(":", "") + ".txt")
                # check the test case report path exits or not
                if os.path.exists(tc_html_report_path) and os.path.exists(tc_txt_report_path):
                    output_display_menu_context = QtWidgets.QMenu()
                    # adding edit action to the menu context
                    action_html_report = output_display_menu_context.addAction("Open html report")
                    action_txt_report = output_display_menu_context.addAction("Open txt report")
                    # display the menu on mouse clicked event position
                    action = output_display_menu_context.exec_(self.output_tablewidget.mapToGlobal(event))
                    # checking if the file exists and then open, if not prompt the user
                    if action == action_html_report:  # open the user selected file into editor
                        webbrowser.open(tc_html_report_path)
                    elif action == action_txt_report:  # open the user selected file into editor
                        webbrowser.open(tc_txt_report_path)
                else:
                    msg = (
                        f"The test case html and txt report paths '{tc_html_report_path} \n {tc_txt_report_path}' "
                        "does not exist!!"
                    )
                    LOG.error(msg)
                    ui_helper.pop_up_msg(helper.InfoLevelType.ERR, msg_str=msg)

    def __change_button_text(self, text):
        """
        A generic method for setting the text on button

        :param String text: Text that has to be set on button
        """
        self.expand_tree_pushbutton.setText(text)

    def __make_signal_connections(self):
        """
        Method for making connections for handling signals which will be emitted by PTF core
        """
        # if 'test_result_params' signal is emitted, execute 'sig_handler_from_run_tests' function
        # This signal marks the end of test cases execution
        # At the end, it stops the timer and reload all imports
        self.result_sig.connect(self.__sig_handler_from_run_tests)
        # Its for the pop-up window triggered by manual verification api
        self.call_manual_input_window.connect(self.open_manual_input_window)
        # If a new testrun started, update the testcases shown for execution
        self.test_run_started_sig.connect(self.__display_tests_to_output)
        # update the test data for parameterized test cases
        self.call_check_uncheck_parameterized_tc.connect(self.__check_uncheck_parameterized_test_cases)

    def open_manual_input_window(self, window_data):
        """
        This Method calls SemiAutomation pop up window for user input entry.
        This method will be called from ptf.ptf_utils.global_params.manual_verification()

        :param list window_data: Contains the Window Title and the query to be displayed on
            the window
        """
        # Setting Window title to default string + Test Case name
        self.semi_auto_obj.setWindowTitle("Manual Verification Dialog from " + window_data[1])
        # Setting the label data as per the user query
        self.semi_auto_obj.user_question.setText(window_data[0])
        # Clearing the input box before each pop up appearance
        self.semi_auto_obj.user_explanation.clear()
        # Calling SemiAutomation popup window
        self.semi_auto_obj.exec_()

    def __move_to_text(self, table_item):
        """
        Method acting as slot for output table widget signal 'itemClicked'.
        It will scroll to specific item text (test case) on console area when clicked.

        :param QTableWidgetItem table_item: Item that was clicked on Output Table Widget
        """
        # first moving the console area cursor to end position since we'll do backward search
        cursor = self.output_console_textedit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.output_console_textedit.setTextCursor(cursor)
        # now finding the item on console in backward direction and moving cursor to that position
        self.output_console_textedit.find(" begin " + table_item.text() + " ", QtGui.QTextDocument.FindBackward)

    def __console_search_text(self, text_to_search):
        """
        Method for searching the text on console output window.
        It will scroll to the matched text(s) on console when return button is pressed.

        :param String text_to_search: String(or text) that has to searched
        """
        result = self.output_console_textedit.find(text_to_search)
        if not result:
            # move cursor to the beginning and restart search
            self.output_console_textedit.moveCursor(QtGui.QTextCursor.Start)
            self.output_console_textedit.find(text_to_search)

    def __display_time(self):
        """
        Method for TIMER

        Whenever TIMER's timeout, this method is called.
        Timeout time is set as 1 sec.
        Moreover, Timer is actually started when user starts executing test
        cases.
        """
        if self.lcd_data["total_execution_time"]["secs"] < 59:
            self.lcd_data["total_execution_time"]["secs"] += 1
        else:
            if self.lcd_data["total_execution_time"]["mins"] < 59:
                self.lcd_data["total_execution_time"]["secs"] = 0
                self.lcd_data["total_execution_time"]["mins"] += 1
            elif (
                self.lcd_data["total_execution_time"]["mins"] == 59
                and self.lcd_data["total_execution_time"]["hours"] < 24
            ):
                self.lcd_data["total_execution_time"]["hours"] += 1
                self.lcd_data["total_execution_time"]["mins"] = 0
                self.lcd_data["total_execution_time"]["secs"] = 0
            else:
                self.timer.stop()
        lcd_time_hours = self.lcd_data["total_execution_time"]["hours"]
        lcd_time_mins = self.lcd_data["total_execution_time"]["mins"]
        lcd_time_secs = self.lcd_data["total_execution_time"]["secs"]
        lcd_time = f"{lcd_time_hours:02d}:{lcd_time_mins:02d}:{lcd_time_secs:02d}"
        self.exe_time_lcd.setDigitCount(len(lcd_time))
        self.exe_time_lcd.display(lcd_time)

    def __increment_tc_timer(self):
        """
        Method for incrementing the time in milli-seconds, whereas time interval is defined
        helper.TC_TIMER_INCREMENT
        """
        # Clock to increment the time
        # milli-sec counter
        self.lcd_data["test_case_exe_time"]["msecs"] += helper.TC_TIMER_INCREMENT

        if self.lcd_data["test_case_exe_time"]["msecs"] >= 1000:
            self.lcd_data["test_case_exe_time"]["msecs"] = 0
            # seconds counter
            self.lcd_data["test_case_exe_time"]["secs"] += 1
            if self.lcd_data["test_case_exe_time"]["secs"] >= 60:
                self.lcd_data["test_case_exe_time"]["secs"] = 0
                # minutes counter
                self.lcd_data["test_case_exe_time"]["mins"] += 1

    def __reset_test_case_timer(self):
        """
        Method to reset test case execution timer every time once its execution is completed.
        """
        self.lcd_data["test_case_exe_time"]["secs"] = 0
        self.lcd_data["test_case_exe_time"]["mins"] = 0
        self.lcd_data["test_case_exe_time"]["msecs"] = 0

    def __update_output_lcds(self):
        """
        This method updates the status of all LCDs on the output side of the GUI.
        """
        self.passed_running_lcd.display(self.lcd_data["passed_test_cases"])
        self.failed_running_lcd.display(self.lcd_data["failed_test_cases"])
        self.inconclusive_running_lcd.display(self.lcd_data["inconclusive_test_cases"])
        self.skip_running_lcd.display(self.lcd_data["skipped_test_cases"])
        # setting the background of passed status lcd to green if tests are passed
        if self.lcd_data["passed_test_cases"]:
            self.passed_running_lcd.setStyleSheet(ui_helper.PASSED_LCD_NUM)
        # setting the background of failed status lcd to red if tests are failed
        if self.lcd_data["failed_test_cases"]:
            self.failed_running_lcd.setStyleSheet(ui_helper.FAILED_LCD_NUM)
        # setting the background of inconclusive status lcd to yellow if tests are inconclusive
        if self.lcd_data["inconclusive_test_cases"]:
            self.inconclusive_running_lcd.setStyleSheet(ui_helper.INCONCLUSIVE_LCD_NUM)
        # setting the background of skipped status lcd to grey if tests are skipped
        if self.lcd_data["skipped_test_cases"]:
            self.skip_running_lcd.setStyleSheet(ui_helper.SKIPPED_LCD_NUM)

    def __update_progress_bar(self):
        """
        This method updates the progress bar as each test runs.
        """
        # getting total test from output list widget.
        total_test = self.output_tablewidget.rowCount()
        # total tests currently executed
        total_executed = (
            self.lcd_data["passed_test_cases"]
            + self.lcd_data["failed_test_cases"]
            + self.lcd_data["inconclusive_test_cases"]
            + self.lcd_data["skipped_test_cases"]
        )
        # progress is all executed by total tests.
        self.lcd_data["progress_bar_value"] = total_executed / total_test * 100
        # updating the progress bar
        self.tests_progressbar.setValue(self.lcd_data["progress_bar_value"])

    def __display_execution_time(self):
        """
        This method is always called after time interval defined at
        helper.TC_TIMER_INCREMENT and updates the execution time of a test case
        accordingly at UI output.
        """
        # incrementing the timer by helper.TC_TIMER_INCREMENT
        self.__increment_tc_timer()

        # getting the row number of currently running test case
        row = self.output_tablewidget.row(self.lcd_data["test_case_running"])

        # time in mins:seconds:milli-seconds format
        widget_time_mins = self.lcd_data["test_case_exe_time"]["mins"]
        widget_time_secs = self.lcd_data["test_case_exe_time"]["secs"]
        widget_time_msecs = self.lcd_data["test_case_exe_time"]["msecs"]
        widget_time = f"{widget_time_mins:02d}:{widget_time_secs:02d}:{widget_time_msecs:03d}"

        # second column is reserved for test case execution time
        col_exe_time = 1
        # updating the time-item at (row, col) location on output table
        self.output_tablewidget.setItem(row, col_exe_time, QtWidgets.QTableWidgetItem(widget_time))

    def __select_setup_file(self, action):
        """
        This method is used to get the absolute path of the selected Action in
        the setup selection menu.
        :param QAction action: The selected action from the setup menu
        """
        for item in self.menu_select_setup_pytest.actions():
            # Uncheck all not selected actions
            if item != action:
                item.setChecked(False)
        # action.text() is the path of the setup file that shall be used
        # assign only selected or checked item to setup_file variable in-case of unchecked response
        # reset setup_file variable value
        self.setup_file = action.text() if action.isChecked() else None
        # checking if ptf.ptf_utils.decorator.custom_setup.custom_setup was used which will help to decide if reloading
        # of tests are required in order to find the custom setup and teardown functions when user selects a new
        # setup file
        if self.custom_decorator_used:
            info = (
                "Reloading of tests are required as there are some tests using '@custom_setup' decorator, "
                f"which need to be checked in '{self.setup_file}'"
            )
            if not self.args["auto_gui"]:
                ui_helper.pop_up_msg(helper.InfoLevelType.INFO, info)
            else:
                LOG.info(info)
            self.reload_test_cases()
        # update the setup file which is used for REST client informer
        self.data.update_client_setup_file(self.setup_file)

    def __slider_toggle(self):
        """
        Method for making slider to function like toggle switch
        """
        # Changing slider position when clicked on handle(toggle-switch)
        if self.slider_dark_mode.sliderPosition() == 0:
            self.slider_dark_mode.setSliderPosition(1)
        else:
            self.slider_dark_mode.setSliderPosition(0)

    def __dark_mode(self):
        """
        This method enables and disables the UI Dark Mode, based on the state of the dark_mode
        """
        # Get the currently running QApplication object (GUI)
        app = QtWidgets.QApplication.instance()
        # If User switched on to Dark Mode, load the stylesheet from qdarkstyle.
        if self.slider_dark_mode.sliderPosition() == 1:
            self.user_config.darkmode = True
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        # If User switched off Dark Mode, load an "empty" stylesheet to restore default color value
        else:
            self.user_config.darkmode = False
            app.setStyleSheet("")

    def __reopen_last_clicked(self, checked):
        """
        Handler for the checkbox if most recent loaded configuration should be reopened on start.
        """
        self.user_config.reopen_last_configuration = checked

    def __generic_new_file(self, filetype):
        """
        This method is executed when User attempts to create new file by selecting
        action_create_sample_setup_file (for setup file) resp.
        action_create_sample_pytest_file (for pytest script)
        under 'Option > Create New File..' .
        :param string filetype: Filetype to be created,
        either setup_file or pytest_file
        """
        # Set the default directory of user Dialog to BASE_PATH (from project config)
        new_py_dir = self.data.get_base_path()

        # Determine values for the Dialogbox based on user action.
        if "setup_file" in filetype:
            dialog_caption = "Create New Setup File"
            type_filter = "Setup File (*.pytest)"
            file_path = os.path.join(new_py_dir, "setup.pytest")
            file_template = test_template.SETUP_PYTEST
        elif "pytest_file" in filetype:
            dialog_caption = "Create New Test Script"
            type_filter = "Test Script (*.pytest)"
            file_path = os.path.join(new_py_dir, "swt_sample_test.pytest")
            file_template = test_template.SAMPLE_TEST_FILE

        # Open the Dialog-box where the user can select location of py-file to create.
        py_file_path, _filter = QtWidgets.QFileDialog.getSaveFileName(
            caption=dialog_caption, filter=type_filter, directory=file_path
        )

        # If user has selected a location
        if str(py_file_path) != "":
            # Open a new file in editing mode
            with open(py_file_path, "w+", encoding="utf-8") as new_py_file:
                # Write sample text inside.
                new_py_file.write(file_template)

            # Inform user about successfull creation of file.
            msg = (
                "New "
                + str(filetype)
                + " created:\n"
                + str(py_file_path)
                + "\nIt will be opened using your default editor."
            )
            ui_helper.pop_up_msg(helper.InfoLevelType.INFO, msg_str=msg)
            # To open the file in editor, check for OS
            if platform.system() == "Windows":
                # For Windows, try to open file with os.startfile
                try:
                    os.startfile(py_file_path)
                # If unable, inform user
                except (AttributeError, FileNotFoundError):
                    ui_helper.pop_up_msg(helper.InfoLevelType.WARN, "Failed to open: \n" + str(py_file_path))
            elif platform.system() == "Linux":
                # For Linux, try to open file with subprocess.call(xdg-open
                try:
                    subprocess.call(("xdg-open", py_file_path))
                # If unable, inform user
                except (AttributeError, FileNotFoundError):
                    ui_helper.pop_up_msg(helper.InfoLevelType.WARN, "Failed to open: \n" + str(py_file_path))
        # If user has not selected a path
        else:
            # Inform about abortion
            ui_helper.pop_up_msg(
                helper.InfoLevelType.INFO, msg_str="Creation of new " + str(type_filter) + " cancelled."
            )

    def __sig_handler_from_run_tests(self, result_data):
        """
        Method for handling the emitted signal from 'ConTest.ptf.ptf_utils.watcher.gui_notifier.GuiNotifier'

        :param dictionary result_data: Dictionary containing test case result information
        """
        testcase_info_obj = result_data["testcase_info_obj"]
        signal_info = result_data["signal_info"]
        # column 1 for execution time
        col_et = 1
        # if testcase failed then save the name to failed testcase list
        if testcase_info_obj.verdict == global_vars.TestVerdicts.FAIL:
            self.__failed_tests.append(testcase_info_obj.name)
        # Find the item on table widget
        test_case_obj = self.output_tablewidget.findItems(
            testcase_info_obj.name, (QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive)
        )
        # only update the ui if the item was found. This might not be the case e.g. for
        # parameterized test cases where we get a lot of triggers for each parameter set,
        # but only show the "root" testcase without parameters.
        if test_case_obj:
            # depending upon the status, change the colour
            if testcase_info_obj.verdict == global_vars.TestVerdicts.PASS and signal_info == "test_finished":
                test_case_obj[0].setIcon(self.status_icon["pass"])
                self.lcd_data["passed_test_cases"] += 1
                # stopping the individual test case timer
                self.tc_timer.stop()
                # test case passed
            elif testcase_info_obj.verdict == global_vars.TestVerdicts.INCONCLUSIVE and signal_info == "test_finished":
                test_case_obj[0].setIcon(self.status_icon["inconclusive"])
                # shan_todo:
                self.lcd_data["inconclusive_test_cases"] += 1
                self.tc_timer.stop()
            elif testcase_info_obj.verdict == global_vars.TestVerdicts.FAIL and signal_info == "test_finished":
                test_case_obj[0].setIcon(self.status_icon["fail"])
                self.lcd_data["failed_test_cases"] += 1
                # stopping the individual test case timer
                self.tc_timer.stop()
            elif testcase_info_obj.verdict == global_vars.TestVerdicts.SKIP and signal_info == "test_finished":
                test_case_obj[0].setIcon(self.status_icon["skip"])
                self.lcd_data["skipped_test_cases"] += 1
                # stopping the individual test case timer
                self.tc_timer.stop()
            elif signal_info == "test_started":
                # resetting the timer to zero
                self.__reset_test_case_timer()
                # currently running test case, undecided status
                test_case_obj[0].setIcon(self.status_icon["no_status"])
                # currently running test case
                self.lcd_data["test_case_running"] = test_case_obj[0]
                # starting the test case counter with resolution defined at TC_TIMER_INCREMENT
                self.tc_timer.start(helper.TC_TIMER_INCREMENT)
                # setting default value for execution time
                row = self.output_tablewidget.row(test_case_obj[0])
                self.output_tablewidget.setItem(
                    row, col_et, QtWidgets.QTableWidgetItem("< 00:00:" + str(helper.TC_TIMER_INCREMENT))
                )
        # finding the item on main tree view
        test_case_obj = self.test_cases_model.findItems(
            testcase_info_obj.name, (QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive)
        )
        if test_case_obj:
            # depending upon the status, set the icon
            if testcase_info_obj.verdict == global_vars.TestVerdicts.PASS and signal_info == "test_finished":
                self.set_tree_status(test_case_obj[0], "pass")
            elif testcase_info_obj.verdict == global_vars.TestVerdicts.INCONCLUSIVE and signal_info == "test_finished":
                self.set_tree_status(test_case_obj[0], "inconclusive")
            elif testcase_info_obj.verdict == global_vars.TestVerdicts.FAIL and signal_info == "test_finished":
                self.set_tree_status(test_case_obj[0], "fail")
            elif testcase_info_obj.verdict == global_vars.TestVerdicts.SKIP and signal_info == "test_finished":
                self.set_tree_status(test_case_obj[0], "skip")
        # updating the output lcd's and progress bars
        self.__update_output_lcds()
        self.__update_progress_bar()

    def __display_tests_to_output(self, test_case_list):
        """
        This method displays test cases in the output table widget at first column.
        :param list test_case_list: test cases to be displayed at the output table widget.
        """
        # resetting the previous results if any
        self.output_tablewidget.clear()
        self.output_console_textedit.clear()

        # First column is reserved for test cases; second for execution time
        col_test_case = 0
        col_exe_time = 1

        # defining default sizes for columns
        col_tc_def_size = 350
        col_et_def_size = 150

        # setting up row count = no. of test cases
        self.output_tablewidget.setRowCount(len(test_case_list))

        # setting up header for test cases
        self.output_tablewidget.setHorizontalHeaderItem(col_test_case, QtWidgets.QTableWidgetItem("Running Test Cases"))

        # setting up header for execution times
        self.output_tablewidget.setHorizontalHeaderItem(
            col_exe_time, QtWidgets.QTableWidgetItem("Execution Time\n[min: sec: msec]")
        )
        # setting default sizes for columns
        self.output_tablewidget.setColumnWidth(col_test_case, col_tc_def_size)
        self.output_tablewidget.setColumnWidth(col_exe_time, col_et_def_size)

        # Setting header view as 'Interactive' which gives user the ability to set widths
        self.output_tablewidget.horizontalHeader().setSectionResizeMode(
            col_test_case, QtWidgets.QHeaderView.Interactive
        )
        self.output_tablewidget.horizontalHeader().setSectionResizeMode(col_exe_time, QtWidgets.QHeaderView.Interactive)

        # loop to add test cases to table one by one.
        row = 0
        for tests in test_case_list:
            table_items = QtWidgets.QTableWidgetItem(tests)
            # added tool tip for the test cases in output window display
            table_items.setToolTip(tests)
            # resize the column size when exceeds the content
            self.output_tablewidget.setItem(row, col_test_case, table_items)
            row = row + 1

        # self.output_tablewidget.resizeRowsToContents()
        # Wraps the text to next line
        self.output_tablewidget.setWordWrap(True)
        # Update test case count lcd
        self.total_running_lcd.display(self.output_tablewidget.rowCount())

    def __setup_search_bar(self):
        """
        This method sets up the search bar for usage and makes connection with
        UI controller methods for selection of searched test case.
        """
        # QCompleter.PopupCompletion completion mode,
        # i.e Current completions are displayed in a pop-up window
        # most matched comes on top and least matched goes to bottom in pop-up
        self.completer.setCompletionMode(0)
        # setting the search as filter mode for match contains (ex: gpio or GPIO)
        self.completer.setFilterMode(Qt.MatchContains)
        # setting the search as case-insensitive
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        # when an item is selected from the pop-up menu, this signal is emitted
        # self.completer.activated.connect(self.select_searched_test)
        self.searchbar_linedit.cursorPositionChanged.connect(self.__search_bar)
        self.searchbar_linedit.returnPressed.connect(lambda: self.__select_searched_test(self.searchbar_linedit.text()))
        # setting up search bar for console output
        self.console_searchbar_linedit.cursorPositionChanged.connect(self.__console_search_bar)
        self.completer.activated.connect(self.__console_search_text)
        self.console_searchbar_linedit.returnPressed.connect(
            lambda: self.__console_search_text(self.console_searchbar_linedit.text())
        )

    # branches are ok as we need to take actions for different cli args
    # pylint: disable=too-many-branches
    @staticmethod
    def __handle_args(cli_args):
        """
        Method for handling CLI options

        :param obj cli_args: Command line arguments
        """
        # setting cli options if given
        if cli_args.r == global_vars.MANUAL_MODE:
            ui_helper.CLI_OPTIONS["auto_mode"] = False
        if cli_args.r == global_vars.AUTO_MODE:
            ui_helper.CLI_OPTIONS["auto_mode"] = True
        if cli_args.r == global_vars.AUTO_GUI_MODE:
            ui_helper.CLI_OPTIONS["auto_gui"] = True
            ui_helper.CLI_OPTIONS["auto_mode"] = True
        if cli_args.n is not None:
            ui_helper.CLI_OPTIONS["no_of_loops"] = cli_args.n
        if cli_args.c is not None:
            ui_helper.CLI_OPTIONS["cfg"] = cli_args.c
        if cli_args.l is not None:
            if cli_args.l[-1] == "\\" or cli_args.l[-1] == "/":
                ui_helper.CLI_OPTIONS["base_loc"] = cli_args.l[:-1]
            else:
                ui_helper.CLI_OPTIONS["base_loc"] = cli_args.l
        if cli_args.random_execution:
            ui_helper.CLI_OPTIONS["random_execution"] = True
        if cli_args.reverse_selection:
            ui_helper.CLI_OPTIONS["reverse_selection"] = True
        if cli_args.dark_mode:
            ui_helper.CLI_OPTIONS["dark_mode"] = True
        if cli_args.setup_file:
            ui_helper.CLI_OPTIONS["setup_file"] = cli_args.setup_file
        if cli_args.filter:
            ui_helper.CLI_OPTIONS["filter"] = cli_args.filter
        if cli_args.report_dir:
            ui_helper.CLI_OPTIONS["report_dir"] = cli_args.report_dir
        # throw back the arguments which will be used later
        return ui_helper.CLI_OPTIONS

    def __take_actions_on_args(self):
        """
        Method for performing action in-case command line arguments are provided
        """
        # reopen last configuration if previous configuration is available and no cfg should be
        # loaded from cmd line
        if (
            self.user_config.reopen_last_configuration
            and self.user_config.last_configurations
            and os.path.exists(self.user_config.last_configurations[-1])
            and not self.args["cfg"]
        ):
            self.args["cfg"] = self.user_config.last_configurations[-1]

        if self.args["random_execution"]:
            self.random_execution.setChecked(True)

        if self.args["cfg"] or self.args["setup_file"] or self.args["filter"]:
            # taking specific actions based on args
            self.handle_arg_actions()

        if self.args["reverse_selection"]:
            self.cb_run_unselected.setChecked(True)
            # calling the method to handle the selection reversals as at this stage the connection of ui items to
            # their respective methods is not activated
            self.handle_tests_reverse_selections()

        if self.args["dark_mode"]:
            self.slider_dark_mode.setSliderPosition(1)
            self.dark_mode()

        # set the value on GUI 'loops_to_run_spinbox' field
        if self.args["no_of_loops"]:
            self.loops_to_run_spinbox.setValue(self.args["no_of_loops"])
        # implementation on enabling GUI on auto mode
        if self.args["auto_gui"]:
            # filter tests based on filter tag or tests in cfg file
            if self.args["filter"]:
                # get the Treeview root item and set the CheckState to Checked
                main_test_item = self.test_cases_model.itemFromIndex(self.test_cases_model.index(0, 0))
                main_test_item.setCheckState(QtCore.Qt.Checked)
                # get the proxy index from the tree view filter model and pass to the items_check_state_handler method
                proxy_ind = self.filter_proxy_model.mapFromSource(self.test_cases_model.index(0, 0))
                self.items_check_state_handler(proxy_ind)
            # run the tests
            self.run_tests()

    @staticmethod
    def __open_user_manual():
        """
        Method for opening user manual
        """
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("How to Access User Manual")
        msg.setWindowIcon(
            QtGui.QIcon(
                os.path.abspath(
                    os.path.join(os.path.dirname(os.path.realpath(__file__)), "gui_images", "logo_icon.png")
                )
            )
        )
        msg.setTextFormat(QtCore.Qt.RichText)
        msg.setText(ui_helper.DOC_ACCESS_MSG)
        msg.addButton(QtWidgets.QPushButton("Already Have Access"), QtWidgets.QMessageBox.YesRole)
        msg.exec_()
        webbrowser.open(ui_helper.USER_MANUAL)

    @staticmethod
    def __open_release_notes():
        """
        Method for opening release notes
        """
        webbrowser.open(ui_helper.RELEASE_NOTES_HTD_LINK)

    def __load_core_configuration(self):
        """
        This method is executed when a shortcut ctrl+l is pressed to load configuration
        """
        # opening a windows dialog to select a ini file restriction are applied to show
        # only .ini files
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            QtWidgets.QFileDialog(), caption="Load a configuration file", filter="*.ini", directory=str(Path.home())
        )
        if file_name:
            self.load_configuration(file_name)

    def __load_core_configuration_recent(self):
        """
        Loads core configuration from "recent configurations" menu
        """
        self.load_configuration(self.sender().text())

    def __create_configuration(self):
        """
        This method is executed when user wants to create a config file. It opens up the
        dialog box for user to create and save a new configuration file.
        """
        # clearing previously loaded fields
        self.configurator_obj.clear_ui()
        # set text color based on the current GUI mode
        self.configurator_obj.text_color = "white;" if self.user_config.darkmode else "black;"
        # showing dialog to user
        self.configurator_obj.show()

    def __update_recent_configurations(self):
        """
        Refreshes the "recent configuration" menu entries on main menu.
        """
        # The separator item to later add new "recent configurations" before this
        separator = None

        # Clean up previously stored recent configurations
        for menu_entry in self.menu_recent_configurations.actions():
            if not menu_entry.isSeparator():
                self.menu_recent_configurations.removeAction(menu_entry)

            # Stop once we found the separator
            else:
                separator = menu_entry
                break

        # Add updated "recent configurations"
        for recent_config in reversed(self.user_config.last_configurations):
            config_action = QAction(recent_config, self)
            config_action.triggered.connect(self.__load_core_configuration_recent)
            self.menu_recent_configurations.insertAction(separator, config_action)

    def __generate_tests(self):
        """
        Method for opening up test generator dialog
        """
        # bring test generator dialogue to initial stage
        self.test_generator_obj.clear_ui()
        # display test generator selection dialogue
        self.test_generator_obj.show()

    def __shortcuts(self):
        """
        Method for opening up short cuts information dialog
        """
        # display shortcut information dialogue
        self.short_cut_info_obj.show()

    def __detecting_selected_tests(self, item, test_case_list):
        """
        Method is to scan and detect the selected items.
        :param QStandardItem item: QStandardItem checked or unchecked by user
        :param list test_case_list: list of test_cases based on filter tag
        """

        # item has children
        if item.hasChildren():
            for num in range(0, item.rowCount()):
                if item.child(num, 0) is not None:
                    # Recursive call to check child item has children
                    self.__detecting_selected_tests(item.child(num, 0), test_case_list)
        # item is not having any children
        # item could be a test case, to make sure below check is performed
        elif item.text() in test_case_list:
            tags = item.parent().child(0, 1).text()
            if item.checkState() == QtCore.Qt.Checked:
                if item.text() not in self.selected_tests_on_gui:
                    self.selected_tests_on_gui.append(item.text())
                    # add or remove selected item in test runner list
                    self.data.add_or_remove_test_for_runner(item.text(), True, tags)
            elif item.checkState() == QtCore.Qt.Unchecked:
                if item.text() in self.selected_tests_on_gui:
                    self.selected_tests_on_gui.remove(item.text())
                    # add or remove selected item in test runner list
                    self.data.add_or_remove_test_for_runner(item.text(), False, tags)

    def __search_bar(self):
        """
        Method for setting up a search bar.
        """
        # declaring model for Q-completer
        test_search_model = self.create_search_bar_model()
        # to give hints to the user based on typed test string
        self.completer.setModel(test_search_model)
        # setting up QtLineEdit as a search bar
        self.searchbar_linedit.setCompleter(self.completer)
        # show search bar with hints on screen
        self.searchbar_linedit.show()

    def __console_search_bar(self):
        """
        Method for setting up a console search bar.
        """
        # declaring model for Q-completer
        console_search_model = self.create_search_console_model()
        # to give hints to the user based on typed string
        self.completer.setModel(console_search_model)
        # setting up QtLineEdit as a search bar
        self.console_searchbar_linedit.setCompleter(self.completer)
        # show search bar with hints on screen
        self.console_searchbar_linedit.show()

    def __select_searched_test(self, search_text):
        """
        This method selects the searched test cases on the main tree view.
        """
        item = self.test_cases_model.findItems(search_text, QtCore.Qt.MatchFixedString | QtCore.Qt.MatchRecursive, 0)
        if item:
            item[0].setCheckState(QtCore.Qt.Checked)
            # updating tree view items check states
            proxy_ind = self.filter_proxy_model.mapFromSource(item[0].index())
            self.items_check_state_handler(proxy_ind)

    def __unselect_searched_test(self, search_text):
        """
        This method un-selects the searched test cases on the main tree view.
        """
        item = self.test_cases_model.findItems(search_text, QtCore.Qt.MatchFixedString | QtCore.Qt.MatchRecursive, 0)
        if item:
            item[0].setCheckState(QtCore.Qt.Unchecked)
            # updating tree view items check states
            proxy_ind = self.filter_proxy_model.mapFromSource(item[0].index())
            self.items_check_state_handler(proxy_ind)

    def __gui_initial_state(self):
        """
        This method initializes the gui state.
        """
        self.initial_state.emit()
        self.__update_recent_configurations()
        LOG.info("Checking ConTest version from artifactory ...")

        version_str, version_tuple = global_vars.check_latest_version()
        if not version_tuple:
            LOG.info("Unable to find the latest version of ConTest")
        else:
            contest_url = global_vars.URL + "v" + version_str
            if global_vars.LOCAL_VERSION_TUPLE:
                if version_tuple > global_vars.LOCAL_VERSION_TUPLE:
                    message_pop_up = (
                        f"Current ConTest version '{global_vars.CONTEST_VERSION}'<br/>"
                        "New version of ConTest is available<br/>"
                        f"Please download latest version 'v{version_str}' from <a href='{contest_url}'>here</a>"
                    )
                    message_log = (
                        f"Current ConTest version '{global_vars.CONTEST_VERSION}'\n"
                        "New version of ConTest is available\n"
                        f"Please download latest version 'v{version_str}' from {contest_url}"
                    )
                    if self.args["auto_gui"]:
                        LOG.info(message_log)
                    else:
                        ui_helper.pop_up_msg(helper.InfoLevelType.INFO, message_pop_up)
            else:
                message_pop_up = (
                    f"Current ConTest version '{global_vars.CONTEST_VERSION}'<br/>"
                    "You're not using official release version of ConTest<br/>"
                    f"Please download latest version 'v{version_str}' version from <a href='{contest_url}'>"
                    "here</a>"
                )
                message_log = (
                    f"Current ConTest version '{global_vars.CONTEST_VERSION}'\n"
                    "You're not using official release version of ConTest\n"
                    f"Please download latest version 'v{version_str}' version from {contest_url}"
                )
                if self.args["auto_gui"]:
                    LOG.info(message_log)
                else:
                    ui_helper.pop_up_msg(helper.InfoLevelType.INFO, message_pop_up)

    def __console_slider_moved(self, slider_action):
        """
        Method for taking action in-case user moved console area vertical slider.

        :param int slider_action: Variable containing value for different slider actions.

        A flag will be set which will communicate to 'console_to_gui' method with the message thatl
        user moved slider therefore stop scrolling vertically automatically.
        """
        # checking if user moved console area vertical slider by any means i.e dragging up/down,
        # mouse wheel scrolling up/down, clicking on arrows etc.
        # this will help to take actions on every possible user action on slider.
        #
        # for slider values descriptions check 'QAbstractSlider' class
        if slider_action in range(
            QtWidgets.QAbstractSlider.SliderSingleStepAdd, QtWidgets.QAbstractSlider.SliderMove + 1
        ):
            self.console_slider_moved = True

    def __stop_tests(self):
        """
        Method for taking action when stop button is pressed
        """
        # changing stop button variable to True state which is read by test runner
        self.stop_state = True
        global_vars.STOP_STATE_GUI = True
        # disabling stop button in order to stop user to press it repeatedly
        self.stop_pushbutton.setEnabled(False)
        # pop-up message to warn user about consequences of stopping
        ui_helper.pop_up_msg(
            helper.InfoLevelType.INFO,
            "Tests Running\nAll tests will be skipped except current running "
            "test and global_teardown.\n\nPlease wait ...\n\nNOTE: The state of "
            "Stop button can be accessed via 'get_gui_stop_state' API in "
            "'global_params' module within your python scripts",
        )

    def __handle_stop_state_after_finish(self):
        """
        Method for changing stop button state when test execution is completed
        """
        # disabling stop button after test execution completed
        self.stop_pushbutton.setDisabled(True)
        # changing stop state variable to it's initial state for next run
        self.stop_state = False
        global_vars.STOP_STATE_GUI = False

    def __gui_test_runner_state(self):
        """
        This method emits a signal defined in UIStates, which takes UI into a state
        where Test are being run and their results are displayed on an output console.
        Moreover, tests run statuses are constantly being updated in real-time.
        """
        self.tests_runner_state.emit()

    def __capturing_expand_state_of_tree_item(self, item):
        """
        Method for capturing expand view state of the main tree view.

        :param QStandardItem item: QStandardItem of the model
        """
        mapped_index = self.filter_proxy_model.mapFromSource(self.test_cases_model.indexFromItem(item))
        if item.hasChildren():
            for num in range(0, item.rowCount()):
                child_item = item.child(num, 0)
                if self.main_treeview.isExpanded(mapped_index):
                    if item.text() not in self.__expanded_state:
                        self.__expanded_state.append(item.text())
                if child_item.hasChildren():
                    # recursive call
                    self.__capturing_expand_state_of_tree_item(child_item)

    def __apply_expand_on_main_tree(self):
        """
        Method for applying expanded state of the tree item.
        """
        for item_name in self.__expanded_state:
            items = self.test_cases_model.findItems(item_name, (QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive))
            for item in items:
                mapped_index = self.filter_proxy_model.mapFromSource(self.test_cases_model.indexFromItem(item))
                self.main_treeview.expand(mapped_index)

    def __select_on_double_click(self, index):
        """
        Method on handling the selection after double clicked on a test case row on main tree view

        :param QModelIndex index: coming from clicking event on main tree view.
        """
        # Converting received index(filter proxy model) to original index(test case model)
        mapped_index = self.filter_proxy_model.mapToSource(index)
        # Getting the item (test_case) at the index
        test_case = self.test_cases_model.itemFromIndex(mapped_index)
        # check if user double-clicked on an empty area
        # test case column is 0 and tags column is 1, But double-clicked on test case
        if test_case.column() == 0:
            # if a test case is already selected then deselect it and vice-versa
            if test_case.checkState():
                test_case.setCheckState(QtCore.Qt.Unchecked)
            else:
                test_case.setCheckState(QtCore.Qt.Checked)
        self.items_check_state_handler(index)

    def __recursive_selection_child2parent(self, item):
        """
        Method is to check or uncheck from the child item to parent recursively
        :param QStandardItem item: item checked or unchecked
        """
        if item.parent():
            # Getting parent item
            parent_item = item.parent()
            # Local variable to know unchecked and checked state count
            temp_check_count = 0
            temp_uncheck_count = 0
            # Looping parent item  row count
            for num in range(0, parent_item.rowCount()):
                child_item = parent_item.child(num, 0)
                # Child item checked == QtCore.Qt.Checked
                if child_item.checkState() == QtCore.Qt.Checked:
                    # count
                    temp_check_count += 1
                elif child_item.checkState() == QtCore.Qt.PartiallyChecked:
                    # child in PartiallyChecked, make parent PartiallyChecked
                    parent_item.setCheckState(QtCore.Qt.PartiallyChecked)
                else:
                    # count
                    temp_uncheck_count += 1
            # Performing check state change
            if temp_check_count == parent_item.rowCount():
                parent_item.setCheckState(QtCore.Qt.Checked)
            elif temp_uncheck_count == parent_item.rowCount():
                parent_item.setCheckState(QtCore.Qt.Unchecked)
            else:
                parent_item.setCheckState(QtCore.Qt.PartiallyChecked)

            # Item has parent
            if parent_item.parent():
                # Recursive call to change state of parent depends on logic above
                self.__recursive_selection_child2parent(parent_item)

    def __recursive_selection_parent2child(self, item):
        """
        Method is to check or uncheck from the parent item to its children recursively
        :param QStandardItem item: item checked or unchecked
        """

        for num in range(0, item.rowCount()):
            child = item.child(num, 0)
            if child is not None:
                if item.checkState() == QtCore.Qt.Checked:
                    child.setCheckState(QtCore.Qt.Checked)
                    if item.hasChildren():
                        # Process event handler to not leave QApplication to not responding
                        QtWidgets.QApplication.processEvents()
                        # recursive call until last child
                        self.__recursive_selection_parent2child(child)
                elif item.checkState() == QtCore.Qt.Unchecked:
                    child.setCheckState(QtCore.Qt.Unchecked)
                    if item.hasChildren():
                        # Process event handler to not leave QApplication to not responding
                        QtWidgets.QApplication.processEvents()
                        # recursive call until last child
                        self.__recursive_selection_parent2child(child)

    def __save_config(self):
        """
        Method for adding selected test cases and no. of iterations to the config file.
        """
        # If a custom base location is selected, use 'save as' screen to avoid saving in temporary
        # configuration
        if self.args["base_loc"]:
            LOG.info("Custom base location selected, show 'Save as...' selector to save configuration.")
            self.__save_as_config()
            return

        if self.project_configuration:
            if not self.get_total_selected_tests():
                LOG.warning("No Test(s) were selected")
                ui_helper.pop_up_msg(helper.InfoLevelType.INFO, "No Test(s) were selected")
            # before saving tests in cfg file update the test dictionary with selections on GUI
            self.tests_for_saving_action = ui_helper.get_tests_for_saving(self.data.test_runner_data)
            # now assign the tests to cfg file entry
            self.project_configuration.selected_tests = self.tests_for_saving_action
            self.project_configuration.num_loops = self.loops_to_run_spinbox.value()
            self.project_configuration.save_config()
            LOG.info("%s updated successfully", self.project_configuration.loaded_config)
            LOG.info("Selected test cases and no. of iterations added")
        else:
            LOG.warning("Please load a configuration file first")

    def __save_as_config(self):
        """
        Method for saving already loaded config file with a different name.
        """
        if not self.get_total_selected_tests():
            LOG.warning("No Test(s) were selected")
            ui_helper.pop_up_msg(helper.InfoLevelType.INFO, "No Test(s) were selected")
        # save directory path
        if self.args["base_loc"]:
            save_dir = self.args["base_loc"]
        else:
            save_dir = self.project_configuration.original_base_path
        # open a dialog box for user to save a new config file
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            QtWidgets.QFileDialog(), "Save data in config file", save_dir, "config files (*.ini)"
        )

        # if user has selected a path
        if path:
            # Load a copy of the current project configuration
            config_to_save = copy.copy(self.project_configuration)

            # if -l option is used
            if self.args["base_loc"]:
                response = ui_helper.pop_up_msg(
                    helper.InfoLevelType.QUEST,
                    "Do you want to save the modified base path?\n\n"
                    "-  Press YES to save with modified base path as mentioned in "
                    "CLI (-l) option (" + self.args["base_loc"] + ")\n\n"
                    "-  Press NO to save with original base path.",
                    self.args["auto_mode"],
                )

                if not response:
                    config_to_save.base_path = self.project_configuration.original_base_path
            self.tests_for_saving_action = ui_helper.get_tests_for_saving(self.data.test_runner_data)
            config_to_save.selected_tests = self.tests_for_saving_action
            config_to_save.num_loops = self.loops_to_run_spinbox.value()

            # writing/updating the config file data
            config_to_save.save_config(path)

            # giving message to main screen regarding save operation
            LOG.info("Config file has been saved as %s", path)
            ui_helper.pop_up_msg(helper.InfoLevelType.INFO, f"Config file has been saved as {path}")

    def __uncheck_test_case_model_based_on_filtering(self):
        """
        Method is to uncheck tree view model items from root item, based on filter tag and clears
        the test runner list
        """
        # get the root item index and set to uncheck state
        main_root_item = self.test_cases_model.itemFromIndex(self.test_cases_model.index(0, 0))
        main_root_item.setCheckState(QtCore.Qt.Unchecked)
        if main_root_item.hasChildren():
            # Based on tag change Recursive all to perform change action
            # from parent to child item is set to Uncheck State
            self.__recursive_selection_parent2child(main_root_item)

        # clear selected test list from test runner for python, cmm, capl
        self.data.clear_test_cases()
        self.selected_tests_on_gui.clear()
        # update the GUI LCD display after cleared tests
        self.update_appear_selected_tests_count()

    def __check_uncheck_parameterized_test_cases(self, gui_parameterized_tc):
        """
        Method for check/uncheck the parameterized test case based on user selection from
        test case parameterized window

        :param tuple gui_parameterized_tc: Contains test case name and bool value
        """
        # In this test case values are not empty then select the test case from tree view
        if gui_parameterized_tc[0]:
            self.__select_searched_test(gui_parameterized_tc[1])
            # else test case values are empty then un-select the test case from tree view
        else:
            self.__unselect_searched_test(gui_parameterized_tc[1])

    @staticmethod
    def __raise_error(err):
        """
        Method for raising error as pop-up, on GUI message area and runtime exception

        :param string err: Error to be raised
        """
        ui_helper.pop_up_msg(helper.InfoLevelType.ERR, err)
        LOG.error(err)
        raise RuntimeError(err)

    def set_tree_status(self, test_case_obj, status):
        """
        Method to set test status icon on main tree view item(QStandardItem)

        :param QStandardItem test_case_obj: Test case item whose status and corresponding parent
            status icons needs to be set
        :param string status: String that represents the status (pass, fail, skip or inconclusive) of the test case item
        """
        if status == "pass":
            test_case_obj.setIcon(self.status_icon["pass"])
        elif status == "fail":
            self.tree_item_failure_list.append(test_case_obj.text())
            test_case_obj.setIcon(self.status_icon["fail"])
        elif status == "inconclusive":
            self.tree_item_inconclusive_list.append(test_case_obj.text())
            test_case_obj.setIcon(self.status_icon["inconclusive"])
        elif status == "skip":
            self.tree_item_inconclusive_list.append(test_case_obj.text())
            test_case_obj.setIcon(self.status_icon["skip"])

    def clear_tree_status(self, main_root_item):
        """
        Method to clear test status icon on main tree view item(QStandardItem)

        :param QStandardItem main_root_item: Main item whose children's status icons needs to be
            cleared
        """
        main_root_item.setIcon(QtGui.QIcon())
        for sub_item in range(main_root_item.rowCount()):
            sub_item_obj = main_root_item.child(sub_item)
            # setting an empty icon returns QIcon object, therefore clears previously set icon
            sub_item_obj.setIcon(QtGui.QIcon())
            self.clear_tree_status(sub_item_obj)
        # after clearing icons from previous runs set icons for test types
        self.set_test_type_icons()

    def test_filter(self):
        """
        Method to filter data on gui based on selected test tag.
        This method is triggered when the user selects a new option on Filter combo box on GUI.
        """
        # set Cursor to wait-option
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        # change tab to select and run if view is on another tab
        if self.select_tests_tabwidget.currentIndex() != self.select_run_tab:
            self.select_tests_tabwidget.setCurrentIndex(self.select_run_tab)
        # now create test model based on test tag filter
        self.load_test_cases()
        # reset cursor to normal
        QtWidgets.QApplication.restoreOverrideCursor()

    def update_filter_combobox(self):
        """
        Method to update the selectable filters based on all found filters in the test-scripts.
        Will update the available filters and their quantity.
        Triggered when loading/reloading the Test cases
        """
        # get the selected filter before cleaning the Combobox
        self.prev_selected_filters.clear()
        self.prev_selected_filters = self.get_checked_filter_tags()

        filter_tag_model = QtGui.QStandardItemModel()
        # clear the combobox before
        self.stage_select_combobox.clear()
        self.cb_all_tags.setCheckState(QtCore.Qt.Checked)
        # start with OR filter in tags
        self.cb_or_tags_filter.setCheckState(QtCore.Qt.Checked)
        self.cb_and_tags_filter.setCheckState(QtCore.Qt.Unchecked)
        # append Tag and quantity to combobox
        index = 0
        all_filter_tags = []
        for key, value in self.data.get_tags().items():
            tag_with_quantity = key + " (" + str(value) + ")"
            item = QtGui.QStandardItem(tag_with_quantity)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            item.setSelectable(QtCore.Qt.Unchecked)
            item.setCheckState(QtCore.Qt.Checked)
            item.setToolTip(key)
            filter_tag_model.setItem(index, 0, item)
            index = index + 1
            all_filter_tags.append(tag_with_quantity)
        # set the filter tag model for combobox to check and uncheck the filter tags
        self.stage_select_combobox.setModel(filter_tag_model)
        # Here the update and apply checked filter tags
        self.apply_filter(self.get_checked_filter_tags())

    def update_filter_combo_box_after_reload(self):
        """
        Method to update filter tags combo box after reloading the test cases
        """
        # update the filter tags check boxes to unchecked state
        self.update_filter_tags_check_boxes(QtCore.Qt.Unchecked)

        # check any previous selected filters are available
        if self.prev_selected_filters:
            for filter_tag in self.prev_selected_filters:
                # Set the "tag" filter
                for i in range(self.stage_select_combobox.model().rowCount()):
                    tag = self.stage_select_combobox.model().item(i).text().split("(")[0].strip()
                    if filter_tag.split("(")[0].strip() == tag:
                        self.stage_select_combobox.model().item(i).setCheckState(QtCore.Qt.Checked)
        self.update_all_tags_check_box()
        # Here the update and apply checked filter tags
        self.apply_filter(self.prev_selected_filters)

    def update_all_tags_check_box(self):
        """
        Method to update all tags check box.
        """
        all_tags_check = True
        for i in range(self.stage_select_combobox.model().rowCount()):
            if self.stage_select_combobox.model().item(i).checkState() != QtCore.Qt.Checked:
                all_tags_check = False
        if all_tags_check:
            self.cb_all_tags.setCheckState(QtCore.Qt.Checked)
        else:
            self.cb_all_tags.setCheckState(QtCore.Qt.Unchecked)

    def update_filter_tags_check_boxes(self, checked):
        """
        Method to update the filter tags check boxes to unchecked/checked state in combo box

        :param QtCore.Qt.Unchecked/QtCore.Qt.Checked checked: Contains checked/unchecked state
        """
        # update the filter tags check boxes in combo box
        for i in range(self.stage_select_combobox.model().rowCount()):
            self.stage_select_combobox.model().item(i).setCheckState(checked)

    def get_checked_filter_tags(self):
        """
        Method to update and apply the selected filter tags to view on the Tree View GUI.

        :return: Returns the list of checked filter tags which is checked by user from GUI
        :rtype: list
        """
        self.stage_select_combobox.lineEdit().clear()
        filter_tags = []
        for i in range(self.stage_select_combobox.model().rowCount()):
            if self.stage_select_combobox.model().item(i).checkState() == Qt.Checked:
                filter_tags.append(self.stage_select_combobox.model().item(i).text())
        # Select symbol to show in the tags tab according the selected filter
        if self.cb_or_tags_filter.isChecked():
            text = " | ".join(filter_tags)
        else:
            text = " & ".join(filter_tags)
        self.test_cases_model.setHorizontalHeaderLabels(["Test_Case Test_Script", f"Tags: {text}"])
        # setting the tool tip to show selected filter tags
        text_with_coma = ", ".join(filter_tags)
        self.test_cases_model.horizontalHeaderItem(1).setToolTip("All Filter Tags: " + text_with_coma.strip())
        self.stage_select_combobox.lineEdit().setText("  -----Tags-----")
        return filter_tags

    def filter_tag_selected(self, index):
        """
        Method triggers when the user pressed the filter tag to select.

        :param int index: selected item from filter tags
        """
        item = self.stage_select_combobox.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)
        # updating the all_tags checkbox
        self.update_all_tags_check_box()
        # apply the filter
        self.apply_filter(self.get_checked_filter_tags())
        # after filter applied expanding the expanding the tree view.
        self.__change_button_text("Collapse All")
        self.main_treeview.expandAll()

    def all_tags_checked_unchecked(self):
        """
        Method triggers when the user checked/unchecked all_tags check box.
        """
        if self.cb_all_tags.isChecked():
            for i in range(self.stage_select_combobox.model().rowCount()):
                self.stage_select_combobox.model().item(i).setCheckState(QtCore.Qt.Checked)
        else:
            for i in range(self.stage_select_combobox.model().rowCount()):
                self.stage_select_combobox.model().item(i).setCheckState(QtCore.Qt.Unchecked)
        self.apply_filter(self.get_checked_filter_tags())
        # after filter applied expanding the expanding the tree view.
        self.__change_button_text("Collapse All")
        self.main_treeview.expandAll()

    def or_tags_filter_logic(self):
        """
        Method triggered when user check/uncheck OR check box in filter tags
        """
        if self.cb_or_tags_filter.isChecked():
            # If OR box is checked then uncheck AND box
            self.cb_and_tags_filter.setCheckState(QtCore.Qt.Unchecked)
        else:
            # If OR box is unchecked then check AND box
            self.cb_and_tags_filter.setCheckState(QtCore.Qt.Checked)
        self.apply_filter(self.get_checked_filter_tags())
        # after filter applied, expand the tree view
        self.__change_button_text("Collapse All")
        self.main_treeview.expandAll()

    def and_tags_filter_logic(self):
        """
        Method triggered when user check/uncheck AND check box in filter tags
        """
        if self.cb_and_tags_filter.isChecked():
            # If AND box is checked then uncheck OR box
            self.cb_or_tags_filter.setCheckState(QtCore.Qt.Unchecked)
        else:
            # If AND box is unchecked then check OR box
            self.cb_or_tags_filter.setCheckState(QtCore.Qt.Checked)
        self.apply_filter(self.get_checked_filter_tags())
        # after filter applied, expand the tree view
        self.__change_button_text("Collapse All")
        self.main_treeview.expandAll()

    def handle_tests_reverse_selections(self):
        """
        Method to reverse the test cases selections
        """
        if not self.args["filter"]:
            # change tab to select and run if view is on another tab
            if self.select_tests_tabwidget.currentIndex() != self.select_run_tab:
                self.select_tests_tabwidget.setCurrentIndex(self.select_run_tab)
            LOG.info("Reversing the tests selections. Please wait ...")
            for selected_test_qt_item in self.tests_q_st_items_objs:
                if selected_test_qt_item.checkState() == QtCore.Qt.Checked:
                    selected_test_qt_item.setCheckState(QtCore.Qt.Unchecked)
                    proxy_ind = self.filter_proxy_model.mapFromSource(selected_test_qt_item.index())
                    self.items_check_state_handler(proxy_ind)
                elif selected_test_qt_item.checkState() == QtCore.Qt.Unchecked:
                    selected_test_qt_item.setCheckState(QtCore.Qt.Checked)
                    proxy_ind = self.filter_proxy_model.mapFromSource(selected_test_qt_item.index())
                    self.items_check_state_handler(proxy_ind)
        else:
            self.cb_run_unselected.setChecked(False)
            if not self.args["auto_gui"]:
                ui_helper.pop_up_msg(
                    helper.InfoLevelType.INFO, "Due to filter input via CLI, reverse selection is ignored"
                )
            LOG.info("Ignoring reverse_selection, due to filter input")

    def update_ui_from_config(self, configuration):
        """
        This method updates the main tree view based on loaded project configuration.

        :param ProjectConfigHandler configuration: currently loaded configuration.
        """
        # for each test type (python, cmm and capl) present in cfg file update gui i.e. make
        # selections on gui
        # get all tests for every test type (python, cmm and capl) in configuration file
        tests_from_config = configuration.selected_tests
        ui_helper.update_ui_with_tests(tests_from_config["selected_tests"], self, LOG, "Python")
        ui_helper.update_ui_with_tests(tests_from_config["cmm_tests"], self, LOG, "T32")
        ui_helper.update_ui_with_tests(tests_from_config["capl_tests"], self, LOG, "CAPL")
        self.loops_to_run_spinbox.setValue(configuration.num_loops)

    def set_total_tests_appearing(self, total_tests_appearing):
        """
        This method sets the list of total tests appearing on screen and updates
        the class variable self.lcd_data (dictionary)

        :param int total_tests_appearing: total tests currently appearing on UI screen
        """
        self.lcd_data["total_tests_appearing"] = total_tests_appearing

    def get_total_tests_appearing(self):
        """
        This method returns a list of total tests appearing on the main tree view.

        :return: Total tests appearing on screen currently
        :rtype: list
        """
        return self.lcd_data["total_tests_appearing"]

    def set_total_selected_tests(self):
        """
        This method sets current selections of test cases and updates the
        class variable self.lcd_data(dictionary)
        """
        self.lcd_data["total_selected_tests"] = self.selected_tests_on_gui

    def get_total_selected_tests(self):
        """
        This method returns a list of total selected tests currently on main tree view.

        :return: total selected test cases
        :rtype: list
        """
        return self.lcd_data["total_selected_tests"]

    def create_search_bar_model(self):
        """
        Creating the string list model for searching from list of test appearing on screen.
        It uses Qt's built-in QStringListModel

        :return: model object in form of list
        :rtype:list
        """
        test_list = self.get_total_tests_appearing()
        test_list_model = QtCore.QStringListModel(test_list)
        return test_list_model

    def create_search_console_model(self):
        """
        Creating the string list model for searching from list of words and sentences on console
        output window.
        It uses Qt's built-in QStringListModel

        :return: model object in form of list
        :rtype:list
        """
        # Getting all text from console
        console_data = self.output_console_textedit.toPlainText()
        # Sorting all words and sentences found in console text into to list. Sorting in such a way
        # that no duplicates, only words(w/ and w/o special(or ignored) characters), only sentences
        # (w/ special characters) to have more possible suggestions to the user
        console_data_list = []
        console_data_ignored_chars = []
        console_data_words = console_data.split()
        console_data_sentences = console_data.split("\n")
        # Words that are in bound with special characters gives no suggestions during search.
        # For example, the word PASSED will not be listed in suggestion as it was printed on console
        # with braces '[PASSED]'. Creating another list of suggestions by ignoring special character
        ignored_chars = ["[", "]", '"', "="]
        for word in console_data_words:
            for char in ignored_chars:
                word = word.replace(char, "")
            console_data_ignored_chars.append(word)
        console_data_list.extend(console_data_words)
        console_data_list.extend(console_data_sentences)
        console_data_list.extend(console_data_ignored_chars)
        # removing duplicates within the list
        console_data_list = list(set(console_data_list))
        # creating QStringListModel
        console_data_list_model = QtCore.QStringListModel(console_data_list)
        return console_data_list_model

    def get_last_failed_tests(self):
        """
        Returns a copy of failed test list of last run.

        :return: A list of failed tests of last run
        :rtype: list
        """
        return self.__failed_tests.copy()

    def clear_last_failed_tests(self):
        """
        Clears the list of failed tests in last run.
        """
        self.__failed_tests.clear()

    def test_completion_print(self):
        """
        Method for printing information on test session completion
        """
        LOG.info("Test run completed")
        LOG.info("Check txt reports at %s", self.data.project_paths[helper.TXT_REPORT])
        LOG.info("Check html reports at %s", self.data.project_paths[helper.HTML_REPORT])
        # assign the last report folder path
        self.last_report_folder_path = self.data.project_paths[helper.TXT_REPORT]
        # assign the last html report path
        self.last_html_report_path = self.data.project_paths[helper.HTML_REPORT]
        # if external report folder path is not None
        if self.data.project_paths[helper.EXTERNAL_REPORT]:
            # assign last external report folder path
            self.last_external_report_folder_path = self.last_report_folder_path.replace(
                self.data.project_paths[helper.BASE_REPORT_DIR], self.data.project_paths[helper.EXTERNAL_REPORT]
            )
        self.slider_dark_mode.setEnabled(True)
        # exit if auto mode mentioned
        if self.args["auto_mode"]:
            QtWidgets.QApplication.quit()
        # exit if auto_gui mode mentioned
        if self.args["auto_gui"]:
            QtWidgets.QApplication.quit()

    def handle_arg_actions(self):
        """
        Method for taking actions based on user provided arguments
        """
        # going to tests selection state
        self.gui_ptf_tests_selection_state()
        # loading of configuration file.
        self.load_configuration(self.args["cfg"], self.args["base_loc"])

        # select custom setup file
        if self.args["setup_file"]:
            setup_filename = self.args["setup_file"]
            if not setup_filename.endswith(".pytest"):
                setup_filename += ".pytest"

            # unify file paths to be always os.path.sep
            setup_filename = setup_filename.replace("/", os.path.sep)
            setup_filename = setup_filename.replace("\\", os.path.sep)

            setup_file_found = False
            for action in self.menu_select_setup_pytest.findChildren(QAction):
                if action.isCheckable() and action.text().endswith(setup_filename):
                    setup_file_found = True
                    action.setChecked(True)
                    self.setup_file = action.text()
                    break

            if not setup_file_found:
                not_found_message = f"Defined setup file '{setup_filename}' not found. Fallback to default setup.pytest"
                LOG.warning(not_found_message)
                ui_helper.pop_up_msg(helper.InfoLevelType.INFO, not_found_message, self.args["auto_mode"])
        # apply available filter
        if self.args["filter"]:
            # valid argument is passed
            # pylint: disable=unsubscriptable-object
            self.filter_tests_with_cli_filter_value(self.args["filter"][0])

    def add_setup_files_in_setup_menu(self):
        """
        Method for checking if same names for setup files exist and creating sub-menu for setup
        file selection menu in-case no duplicate names for setup file found.
        """
        # detect if any setup script are duplicated by name in order to avoid ambiguity during
        # grabbing it's functions objects
        self.data.detect_duplicate_setup_files()
        # grabbing actions in select setup.pytest menu and setup file paths
        setup_list = [setup_path[0] for setup_path in self.data.get_setup_files()]
        action_list = [action.text() for action in self.menu_select_setup_pytest.actions()]
        # removing deleted actions
        for action in self.menu_select_setup_pytest.actions():
            if action.text() not in setup_list:
                self.menu_select_setup_pytest.removeAction(action)
        # add new setup files and make them checkable
        for setup_file in setup_list:
            if setup_file not in action_list:
                added_action = self.menu_select_setup_pytest.addAction(setup_file)
                added_action.setCheckable(True)

    def load_configuration(self, file_name, base_path=None):
        """
        Loads the configuration from a given file and refreshes the UI.

        :param str file_name: The file to load.
        :param str base_path: If this parameter is given, the value will be used as custom base
                                  location
        """
        QtWidgets.QApplication.processEvents()
        LOG.info("-" * 100)
        if base_path:
            LOG.info("Loading your config file %s with custom base location %s", file_name, base_path)
        else:
            LOG.info("Loading your config file %s", file_name)
        if not os.path.exists(file_name):
            if not os.path.isabs(file_name):
                file_name = os.path.join(global_vars.THIS_FILE, file_name)
            err = f"The configuration file {file_name} doesn't exists"
            ui_helper.pop_up_msg(helper.InfoLevelType.ERR, err)
        self.project_configuration = common_utils.store_cfg_data(cfg_file=file_name, new_base_location=base_path)
        # If run_exec_record was requested, replace selected test cases from cfg.ini with the ones requested to be run
        # according to verdict in previous run.
        if self.exec_record_requested:
            selected_test = self.project_configuration.selected_tests
            selected_test["selected_tests"] = self.selected_tests_exec_record
            self.project_configuration.selected_tests = selected_test
        # user info if CAPL test path is saved in cfg which means that user is using an old format
        # of cfg which need to be edited as handling of CANoe tests has been changed in new contest
        # version
        if self.project_configuration.capl_test_path:
            ui_helper.pop_up_msg(helper.InfoLevelType.INFO, ui_helper.CANOE_BACKPORT_MSG)
        try:
            self.project_configuration.post_load_config()
        except RuntimeError as error:
            self.reset_ptf()
            del self.lcd_data["total_selected_tests"][:]
            if self.args["auto_mode"]:
                raise error

            response = ui_helper.pop_up_msg(
                helper.InfoLevelType.QUEST,
                f"{error}\n\nAbove path(s) do not exist!\nWould you like to edit?",
            )
            if response:
                if self.edit_configurator_obj is not None:
                    self.edit_configurator_obj.close()
                self.edit_configuration()
            else:
                # If the user doesn't want to fix the configuration,
                # just continue showing the main screen
                LOG.info("Loading of configuration canceled due to invalid configuration.")
            return
        # resets the test case parameters variables to empty
        if self.test_case_parameter_obj is not None:
            self.test_case_parameter_obj.reset_variables()
        # make a fresh instance of prepare data class (required for each new cfg loading)
        self.data = prepare_test_data.PrepareTestData(gui=self)
        # clearing output tab
        self.clear_output_tab()
        # setting the core configuration
        self.set_core_configuration()
        UserConfigHandler().add_configuration(file_name)
        # setting the text on expand_tree_pushbutton to "Expand All" for any new cfg loaded.
        self.expand_tree_pushbutton.setText("Expand All")
        LOG.info("Configuration file loaded successfully")
        LOG.info("-" * 100)
        self.setWindowTitle(global_vars.gui_window_title + " - " + file_name)
        self.current_loaded_cfg = file_name
        self.gui_ptf_tests_selection_state()

    def edit_configuration(self):
        """
        This method is executed when user wants to edit a loaded config file. It opens up the
        dialog box for user to make changes and update changes to the loaded configuration file.
        """
        # setting the edit config flag to False
        self.edit_config_flag = False
        # defining a PTF Edit configurator object, to load or create a config file
        self.edit_configurator_obj = config_editor.ConfigEditor(self, True, self.project_configuration.loaded_config)
        # Loading the fields with available data
        self.edit_configurator_obj.load_edit_cfg_ui()
        # showing dialog to user
        self.edit_configurator_obj.exec()

    def update_appear_selected_tests_count(self):
        """
        This method is updating total appearing tests and selected into model and display LED.
        Moreover it stores selected items (tests) on UI for save cfg options
        """
        # updating model regarding total tests appearing
        filter_tags = self.get_checked_filter_tags()
        tc_lists = []
        for tag in filter_tags:
            if self.data.get_filtered_tests_list_based_on_tag(tag):
                tc_lists += self.data.get_filtered_tests_list_based_on_tag(tag)
        self.set_total_tests_appearing(list(set(tc_lists)))
        # updating model regarding total selected and storing selected tests for saving purpose
        self.set_total_selected_tests()
        # updating the LCDs display count
        if self.lcd_data["total_tests_appearing"]:
            self.num_sel_tests_lcd.display(len(self.lcd_data["total_selected_tests"]))
            self.num_total_tests_lcd.display(len(self.lcd_data["total_tests_appearing"]))

    def clear_output_tab(self):
        """
        This method will clear the output tab. It will reset the previous results and disable output
        window then take user to select and run window
        """
        self.output_tablewidget.clear()
        self.output_console_textedit.clear()
        self.select_tests_tabwidget.setTabEnabled(self.output_tab, False)

    def set_core_configuration(self):
        """
        This method is called in configuration class. When user loads a config file in configurator
        dialog box, this function is executed and corresponding paths are read and set by
        corresponding core.
        """
        # preparing the test data
        duplication_exist, err = self.data.prepare_test_data_from_cfg(
            configuration=self.project_configuration, setup_file=self.args["setup_file"]
        )
        # edit_configuration triggers only for when import module error occurs.
        if self.edit_config_flag:
            self.edit_configuration()
        # if duplications found then raise error
        if duplication_exist:
            self.__raise_error(err)
        # creating a test tree model and displaying it
        self.load_test_cases()
        # updating the UI.
        self.update_ui_from_config(self.project_configuration)
        # enabling the run test button, randomize execution and run un-selected tests checkboxes
        self.runtest_pushbutton.setDisabled(False)
        self.random_execution.setDisabled(False)
        self.cb_run_unselected.setDisabled(False)

    def gui_ptf_tests_selection_state(self):
        """
        This method emits a signal defined in UIStates, which takes UI into a state
        where PTF test cases can be loaded and selected. Moreover, test filtering based
        on tools, frequency and search bar is enabled too.
        """
        self.post_config_load_state.emit()

    def run_tests(self):
        """
        Method for making arrangements for running tests
        """
        # failed and inconclusive tree items stored during previous run is flushed at start of each run
        del self.tree_item_failure_list[:]
        del self.tree_item_inconclusive_list[:]
        # checking if user selected any test(s) on selection area
        main_test_item = self.test_cases_model.itemFromIndex(self.test_cases_model.index(0, 0))
        if main_test_item.checkState() == QtCore.Qt.Unchecked:
            LOG.error("No Test(s) have been selected ...")
            ui_helper.pop_up_msg(helper.InfoLevelType.ERR, "No Test(s) have been selected ...", self.args["auto_mode"])
            raise RuntimeError("No Test(s) have been selected ...")
        self.clear_tree_status(main_test_item)
        # resetting console slider moving flag to False in-case user moved it previously in order to activate automatic
        # scrolling of console area downwards
        if self.console_slider_moved:
            self.console_slider_moved = False
        # getting setup file data based on selection
        if self.setup_file is None:
            standard_setup_funcs = self.data.filter_and_get_setup_file_data("setup")
        else:
            standard_setup_funcs = self.data.filter_and_get_setup_file_data(os.path.split(self.setup_file)[1])
        # prepare data for test runner stage
        self.data.prepare_runner_data(
            self.random_execution.isChecked(),
            self.args["report_dir"],
            standard_setup_funcs,
            self.loops_to_run_spinbox.value(),
            self.run_mode,
            self.external_paths_cli,
            self.timestamp_en,
        )
        # test runner is triggered from UI therefore update relevant flags
        self.data.test_runner_data["triggered_from_gui"] = True
        self.data.test_runner_data["gui_object"] = [self]
        self.data.test_runner_data["parameterized_tests"] = dict(
            self.data.update_and_get_parameterized_tests_for_test_runner(self.test_case_parameter_obj)
        )
        # connecting 'print_is_called' signal with method 'console_to_gui'
        # this is done to redirect all prints to UI console output tab view
        sys.stdout = EmittingStream(print_is_called=self.console_to_gui)
        sys.stderr = EmittingStream(print_is_called=self.console_to_gui)
        # disabling "Run" button after tests execution started, in order to avoid user pressing
        # this button again during tests running.
        self.runtest_pushbutton.setDisabled(True)
        self.run_only_failed.setDisabled(True)
        self.random_execution.setDisabled(True)
        self.cb_run_unselected.setDisabled(True)
        # enabling "Stop" button after tests execution starts in order to allow user to stop
        # test execution
        self.stop_pushbutton.setEnabled(True)
        # taking UI into output enabled state
        self.__gui_test_runner_state()
        # updating output side of UI and resetting the LCDs (test case count will be updated on
        # test list updates)
        self.tests_progressbar.setValue(0)
        self.passed_running_lcd.display(0)
        self.failed_running_lcd.display(0)
        self.inconclusive_running_lcd.display(0)
        self.skip_running_lcd.display(0)
        self.exe_time_lcd.display(0)
        # resetting the background color of status lcd
        self.passed_running_lcd.setStyleSheet(ui_helper.NON_RUNNING_LCD_NUM)
        self.failed_running_lcd.setStyleSheet(ui_helper.NON_RUNNING_LCD_NUM)
        self.inconclusive_running_lcd.setStyleSheet(ui_helper.NON_RUNNING_LCD_NUM)
        self.skip_running_lcd.setStyleSheet(ui_helper.NON_RUNNING_LCD_NUM)
        self.thread_class.start()
        # starting the timer (timer increments 1000 msecs)
        self.timer.start(1000)

    def reload_test_cases(self):
        """
        Method is to handle the operation of reload/load button properly

        In this method following steps are performed:

        1. Storing the root item of main tree view and capturing the current state of main tree view
        2. Storing GUI settings (selected tests and tests runs value)
        3. Storing object of test data for restoring purpose in-case of duplications
        4. Read fresh paths from loaded cfg file (helpful in-case paths changed in edit cfg option)
        5. Reload normal python scripts (.py) in additional paths in config in-case of updates
        6. Ask user to if canoe cfg data need to be reloaded
        7. Preparing data to add or remove items (test scripts and test cases) on main tree view
        8. If duplication found then assign data container previously saved test data otherwise
           load newly grabbed data to display added items or remove deleted items
        9. Now expand main tree view as per Step 1
        10. Now restore saved test cases and test runs value
        11. Reload normal python scripts (.py) at python test location in-case some update happens
            in them
        12. After reload update the parameterized values for the selected parameter sets for
            test runner
        """
        try:
            # first disable run button and main tree view so user doesn't misuse them during
            # reloading time period
            self.main_treeview.setEnabled(False)
            self.runtest_pushbutton.setEnabled(False)
            QtWidgets.QApplication.processEvents()
            # --> Step 1.
            # Getting the root item of the test case model
            root_item = self.test_cases_model.itemFromIndex(self.test_cases_model.index(0, 0))
            # capturing the tree expand item state
            self.__expanded_state.clear()
            self.__capturing_expand_state_of_tree_item(root_item)
            # moving view to select and run tab
            self.select_tests_tabwidget.setCurrentIndex(self.select_run_tab)
            # --> Step 2.
            # here deepcopy is performed to keep list before load_test_cases or else will lose
            # info of selected_tests and iterations
            selected_tests = copy.deepcopy(self.get_total_selected_tests())
            iterations = copy.deepcopy(self.loops_to_run_spinbox.value())
            # --> Step 3.
            # save test data class object which might be required in case duplications of
            # test scripts or test cases are found
            saved_object_of_test_data = self.data
            # --> Step 4.
            # Read fresh paths from loaded cfg file (helpful in-case paths changed in edit
            # cfg option)
            user_cfg = common_utils.store_cfg_data(cfg_file=self.current_loaded_cfg)
            user_cfg.post_load_config()
            # --> Step 5. reload external scripts only if external/additional paths given and user
            # agrees it to be done
            # Before preparation of TestData external paths scripts to be reloaded
            if self.project_configuration.additional_paths:
                response = ui_helper.pop_up_msg(
                    helper.InfoLevelType.QUEST,
                    ui_helper.EXT_SCRIPTS_RELOAD_MSG.format(self.project_configuration.additional_paths),
                )
                if response:
                    for add_paths in self.project_configuration.additional_paths:
                        reload_status = helper.reload_py_scripts(add_paths)
                        if reload_status:
                            ui_helper.pop_up_msg(helper.InfoLevelType.ERR, reload_status)
                            LOG.error(reload_status)
                        else:
                            LOG.info("Successfully reloaded .py scripts at %s", add_paths)
            # --> Step 6.
            canoe_response = False
            if bool(saved_object_of_test_data.data["canoe_test_data"]):
                canoe_response = ui_helper.pop_up_msg(
                    helper.InfoLevelType.QUEST,
                    "CANoe cfg data is already loaded. "
                    "Do you want to reload CANoe cfg data also (in-case something changed in CANoe "
                    "cfg)?",
                )
            # --> Step 7.
            # make a fresh instance of prepare data class (required during reloading button action)
            self.data = prepare_test_data.PrepareTestData(gui=self)
            # assigning previously saved canoe data in-case user didn't opted to reload it
            # this will help in creating tree view of canoe tests
            if not canoe_response:
                self.data.data["canoe_test_data"] = saved_object_of_test_data.data["canoe_test_data"]
                self.data.data["canoe_test_names"] = saved_object_of_test_data.data["canoe_test_names"]
                self.data.tags.extend([ui_helper.CANOE_FILTER_NAME] * len(self.data.data["canoe_test_names"]))
            # preparing the test data
            duplication_exist, err = self.data.prepare_test_data_from_cfg(
                configuration=user_cfg, load_canoe=canoe_response, setup_file=self.setup_file
            )
            # edit_configuration triggers only for when import module error occurs. when reload
            # button pressed.
            if self.edit_config_flag:
                self.edit_configuration()
            # --> Step 8.
            # if duplications found then prompt user about the duplications and do not reload
            # tests i.e. to display duplicated test scripts and or test cases
            if duplication_exist:
                ui_helper.pop_up_msg(helper.InfoLevelType.ERR, err)
                LOG.error(err)
                # assign data container saved object of test data class in order to avoid
                # overloading of existing test data
                self.data = saved_object_of_test_data
            # if no duplications found then reload tests to display added or removed test scripts
            # and or test cases
            else:
                self.load_test_cases()
                #  update the combobox filter with previous selected tags
                self.update_filter_combo_box_after_reload()
                # clearing up the selections which were done previously on GUI
                # new selections will be done based on previously selected data
                self.selected_tests_on_gui.clear()
            # --> Step 9.
            # after reloading, retrieving the expand state of the tree
            self.__apply_expand_on_main_tree()
            LOG.info("%s test(s) are selected before run or reload button pressed", len(selected_tests))
            # --> Step 10.
            # below to retain state of selected_tests and iteration after reload
            if selected_tests is not None:
                # Selecting tests on UI
                for test in selected_tests:
                    item = self.test_cases_model.findItems(
                        test, QtCore.Qt.MatchFixedString | QtCore.Qt.MatchRecursive, 0
                    )
                    if item:
                        item[0].setCheckState(QtCore.Qt.Checked)
                        # only make additions to test data runner dictionary via
                        # 'items_check_state_handler' if duplications not found otherwise saved test
                        # data will be used
                        if not duplication_exist:
                            # updating tree view items check states
                            proxy_ind = self.filter_proxy_model.mapFromSource(item[0].index())
                            self.items_check_state_handler(proxy_ind)
                    else:
                        # showing missing tests on status window
                        LOG.warning("%s not found after run or reload button pressed. Might be removed by user!", test)
            self.loops_to_run_spinbox.setValue(iterations)
            # --> Step 11.
            reload_status = helper.reload_py_scripts(self.data.get_ptf_path())
            if reload_status:
                ui_helper.pop_up_msg(helper.InfoLevelType.ERR, reload_status)
                LOG.error(reload_status)
            else:
                LOG.info("Successfully reloaded .py scripts at %s", self.data.get_ptf_path())
            # --> Step 12
            if self.test_case_parameter_obj is not None:
                self.test_case_parameter_obj.after_reload_update_stored_test_parameter_values(
                    self.data.get_python_test_data()
                )
        # have to capture any error occurred in reloading phase and do a pop-up
        # pylint: disable=broad-except
        except Exception as error:
            ui_helper.pop_up_msg(helper.InfoLevelType.ERR, str(error))
            LOG.error(error)
        # and in the end enable run button and main tree view again
        finally:
            self.runtest_pushbutton.setEnabled(True)
            self.main_treeview.setEnabled(True)

    def set_test_type_icons(self):
        """
        Method for setting icons for different test types
        """
        test_type_icon_data = {
            ui_helper.PYTHON_TESTS_QT_STR: "python",
            ui_helper.T32_TESTS_QT_STR: "t32",
            ui_helper.CANOE_TESTS_QT_STR: "canoe",
        }
        for type_qt_str, type_name in test_type_icon_data.items():
            test_obj = self.test_cases_model.findItems(
                type_qt_str, (QtCore.Qt.MatchRecursive | QtCore.Qt.MatchContains)
            )
            if test_obj:
                test_obj[0].setIcon(self.test_type_icons[type_name])

    def load_test_cases(self):
        """
        Method for loading test cases on the UI using test case model and tree view of UI.
        Moreover, it makes the loaded test cases compatible with other widgets for sorting and
        filtering of test case. Other widgets includes 'tools checkbox', 'test frequency' and
        'search bar'.
        """
        # cleaning up selected test case is needed here to keep clean while loading/reloading
        self.selected_tests_on_gui.clear()
        self.main_treeview.setUniformRowHeights(True)
        # checking duplication for setup files and adding sub-menu items in setup selection menu
        self.add_setup_files_in_setup_menu()
        # Showing list of test cases on tree view
        main_parent_item = QtGui.QStandardItem(
            "All Test Modules- " + os.path.basename(self.data.get_base_path()) + " (" + self.data.get_base_path() + ")"
        )
        main_parent_item.setCheckable(True)
        main_parent_item.setTristate(True)
        main_parent_item.setToolTip(f"Base Location: {self.data.get_base_path()}")
        self.create_tree_view(main_parent_item)
        # Setting the heading
        self.test_cases_model = QtGui.QStandardItemModel()
        self.test_cases_model.setHorizontalHeaderLabels(["Tests", "Tags"])
        self.test_cases_model.appendRow(main_parent_item)
        # Setting up a proxy model for filtering and  sorting of data
        # ------ VIEW (UI) <----> PROXY MODEL (Sort/Filter) <-----> MODEL (Data)
        # Setting source model as test_case_model (a tree)
        self.filter_proxy_model.setSourceModel(self.test_cases_model)
        # Enabling dynamic filtering of data
        self.filter_proxy_model.setDynamicSortFilter(True)
        # Enabling case-insensitive filtering
        self.filter_proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseSensitive)
        self.filter_proxy_model.setFilterKeyColumn(1)
        self.filter_proxy_model.setFilterWildcard("*,*")
        # Enabling filtering on children items of our test case tree view
        self.filter_proxy_model.setRecursiveFilteringEnabled(True)
        # Tree View will use proxy model for filtering
        self.main_treeview.setModel(self.filter_proxy_model)
        self.main_treeview.setColumnWidth(0, 700)
        # Showing test on screen
        self.main_treeview.show()
        # get header to resize the contents
        header = self.main_treeview.header()
        # resize the viewing area according to the contents.
        # this will also enable scroll bars (if required)
        header.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        header.setStretchLastSection(True)
        # load configuration with selected test is none, then need
        # to update the model and display LED about appearing and selected count
        self.update_appear_selected_tests_count()
        # update the test filters
        self.update_filter_combobox()
        # set icons for different test types
        self.set_test_type_icons()
        main_parent_item.setIcon(self.test_type_icons["contest"])

    def items_check_state_handler(self, index):
        """
        This method is a receiver method for a clicking event on main tree view of GUI.
        This method deals with states of checkboxes of parent and child item. E.g. When a
        parent item is selected all of its children are selected. OR when a child item is
        selected, its parent is partially selected.

        :param QModelIndex index: coming from clicking event on main tree view.
        """
        # changing cursor type to waiting cursor
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        # Converting received index(filter proxy model) to original index(test case model)
        mapped_index = self.filter_proxy_model.mapToSource(index)
        # Getting the item at the index
        item = self.test_cases_model.itemFromIndex(mapped_index)
        filter_tags = self.get_checked_filter_tags()
        # getting the list of test cases based on filter tag
        tc_list = []
        for tag in filter_tags:
            tc_list += self.data.get_filtered_tests_list_based_on_tag(tag)
        test_case_list = list(set(tc_list))
        if test_case_list is not None:
            if item is not None:
                # Item has children
                if item.hasChildren():
                    # Disabling main_tree view while selecting parent2child to make sure user not to
                    # perform another state change
                    self.main_treeview.setEnabled(False)
                    # Recursive all to perform change action from parent to child item
                    self.__recursive_selection_parent2child(item)
                    # Enabling main tree view once change state completed
                    self.main_treeview.setEnabled(True)
                    # scanning and detecting the selected test case count from the selected item
                    self.__detecting_selected_tests(item, test_case_list)
                    # Item has parent
                    if item.parent():
                        # Recursive call to perform change update from child to parent item
                        self.__recursive_selection_child2parent(item)
                        # scanning and detecting the selected test case count from the selected item
                        self.__detecting_selected_tests(item, test_case_list)
                # Item has not children
                else:
                    # Recursive call to perform change update from child to parent item
                    self.__recursive_selection_child2parent(item)
                    # scanning and detecting the selected test case count from the selected item
                    self.__detecting_selected_tests(item, test_case_list)
        # to update display LED about appearing and selected count
        self.update_appear_selected_tests_count()
        # Putting back normal cursor once state change completed
        QtWidgets.QApplication.restoreOverrideCursor()

    def console_to_gui(self, text):
        """Printing text from console to GUI Output widget QPlainTextEdit"""
        error_string_list = [
            "--> ERROR:",
            "--> Failure(s) :",
            "[FAILED]",
            "[Failing Tests]",
            "[Failed Tests]",
            "--> Testcase failed",
            "Traceback (most recent call last):",
        ]
        # if user has not moved the slider then scroll down vertically
        if not self.console_slider_moved:
            # making sure console cursor is visible
            self.output_console_textedit.ensureCursorVisible()
            # checking for failures and errors, turing those text lines 'red'
            if [err for err in error_string_list if text.startswith(err)]:
                self.output_console_textedit.setTextColor(ui_helper.RED)
            elif text.startswith("[PASSED]") or text.startswith("[Passed Tests]"):
                self.output_console_textedit.setTextColor(ui_helper.GREEN)
            elif (
                text.startswith("[Inconclusive Tests]")
                or text.startswith("[INCONCLUSIVE]")
                or text.startswith("--> Testcase Warning:")
                or text.startswith("--> WARNING:")
            ):
                self.output_console_textedit.setTextColor(ui_helper.YELLOW)
            elif text.startswith("[Skipped Tests]") or text.startswith("[SKIPPED]"):
                self.output_console_textedit.setTextColor(ui_helper.GREY)
            else:
                self.output_console_textedit.setTextColor(QtGui.QColor("white"))
            # inserting text to console area
            self.output_console_textedit.append(text)
        # if user moved slider then don't scroll automatically and just insert text to console
        else:
            self.output_console_textedit.append(text)

    def test_completion_task(self):
        """
        Method for resetting the controlling variables after test runner ends
        """
        # re-initialization of LCD data
        self.lcd_data["passed_test_cases"] = 0
        self.lcd_data["failed_test_cases"] = 0
        self.lcd_data["inconclusive_test_cases"] = 0
        self.lcd_data["skipped_test_cases"] = 0
        self.lcd_data["progress_bar_value"] = float(0)
        # stopping the timer
        self.timer.stop()
        self.lcd_data["total_execution_time"]["hours"] = 0
        self.lcd_data["total_execution_time"]["mins"] = 0
        self.lcd_data["total_execution_time"]["secs"] = 0
        # re-enabling "Run" button after all tests execution
        self.runtest_pushbutton.setDisabled(False)
        self.random_execution.setDisabled(False)
        self.cb_run_unselected.setDisabled(False)
        # change stop button state when test execution completed
        self.__handle_stop_state_after_finish()
        # enabling the report button
        self.action_report_open.setEnabled(True)
        # if external report path is not None then enable the action
        if self.data.project_paths[helper.EXTERNAL_REPORT]:
            self.action_external_report_open.setEnabled(True)
        self.action_open_html_report.setEnabled(True)
        self.action_open_txt_report.setEnabled(True)
        self.action_open_json_report.setEnabled(True)
        self.action_open_xml_report.setEnabled(True)
        self.action_open_cathat_xml_report.setEnabled(True)
        self.test_completion_print()
        # enabling the checkbox to run only failed tests
        self.run_only_failed.setEnabled(True)
        # changing test execution state to False
        self.tests_running = False
        # enabling reload button after completion of test
        self.reload_pushbutton.setEnabled(True)
        # enable filter tags and filter check box
        self.stage_select_combobox.setEnabled(True)
        self.cb_all_tags.setEnabled(True)

    def open_folder(self, loc):
        """
        Method for opening up of different requested locations

        :param str loc: String telling which location to open
        """
        path_open = None
        if loc == "report":
            # going back to parent folder to show user html and txt folders
            path_open = os.path.abspath(os.path.join(self.last_report_folder_path, os.pardir))
        elif loc == "base_loc":
            path_open = self.project_configuration.base_path
        elif loc == "py_loc":
            path_open = self.project_configuration.ptf_test_path
        elif loc == "external_report":
            # going back to parent external report folder to show user html and txt folders
            path_open = os.path.abspath(os.path.join(self.last_external_report_folder_path, os.pardir))
        if path_open:
            # this condition added for demo tests in repository since they contain relative path
            if not os.path.isabs(path_open):
                path_open = os.path.join(global_vars.THIS_FILE, path_open)
        # opening up report folder
        if sys.platform == "win32":
            # Pylint is not intelligent enough to recognize that this code is only
            # executed on windows systems.
            # pylint: disable=no-member,useless-suppression
            os.startfile(path_open)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, path_open])

    def open_html_report(self):
        """
        Method for opening HTML summary report
        """
        webbrowser.open(os.path.join(self.last_html_report_path, "TESTS_SUMMARY.html"))

    def open_txt_report(self):
        """
        Method for opening TXT summary report
        """
        webbrowser.open(os.path.join(self.last_report_folder_path, "TESTS_SUMMARY.txt"))

    def open_json_report(self):
        """
        Method for opening JSON report
        """
        webbrowser.open(os.path.join(self.last_report_folder_path, "TEST_RESULT.json"))

    def open_xml_report(self):
        """
        Method for opening XML summary report
        """
        webbrowser.open(os.path.join(self.last_report_folder_path, "TEST_RESULT.xml"))

    def open_cathat_xml_report(self):
        """
        Method for opening CatHat XML report
        """
        webbrowser.open(os.path.join(self.last_report_folder_path, "CATHAT_TEST_RESULT.xml"))

    def open_setup_file(self):
        """
        Method for opening currently selected setup.pytest file
        """
        webbrowser.open(self.setup_file)

    def expand_collapse_tree(self):
        """
        Method for expanding or collapsing the view of main tree view items
        """
        text = self.expand_tree_pushbutton.text()
        if text == "Expand All":
            self.main_treeview.expandAll()
        else:
            self.main_treeview.collapseAll()

    def clear_status_msg(self):
        """
        Method for clearing out status messages area when 'clear' push button
        is pressed.
        """
        icon = QtGui.QIcon(ui_helper.ICON)
        self.message_plaintextedit.clear()
        LOG.info("Message area cleared")
        self.msg_toolButton.setIcon(icon)

    # pylint: disable=invalid-name
    # this is built-in name of main window
    def closeEvent(self, event):
        """
        Default Qt method which is called when main GUI window is closed

        :param QCloseEvent event: QCloseEvent object for handling closure events
        """
        position = self.pos()
        size = self.frameGeometry()
        self.user_config.last_position = (position.x(), position.y())
        self.user_config.last_size = (size.width(), size.height())
        if self.tests_running:
            self.__stop_tests()
        event.accept()

    def view_config_data(self):
        """
        Method for viewing the data of loaded config file
        """
        data = (
            "<b>Continental Software Testing Tool (ConTest)</b><br/><br/><br/>"
            f"<b>Config File: </b>{self.project_configuration.loaded_config}<br/><br/>"
            f"<b>FW Version: </b>{self.project_configuration.fw_name}<br/><br/>"
            f"<b>Base Path: </b>{self.project_configuration.base_path}<br/>"
            f"<b>Python Path: </b>{self.project_configuration.ptf_test_path}<br/>"
            f"<b>T32 Path: </b>{self.project_configuration.cmm_test_path}<br/>"
            f"<b>CANoe Cfg Path: </b>{self.project_configuration.canoe_cfg_path}<br/>"
            f"<b>CTF Flag: </b>{self.project_configuration.use_cte_checkbox}<br/>"
            f"<b>CTF Zip Path: </b>{self.project_configuration.cte_location}<br/>"
            f"<b>CTF Cfg Path: </b>{self.project_configuration.cte_cfg}<br/>"
            f"<b>Report Path: </b>{self.project_configuration.report_path}<br/>"
            f"<b>T32 Exe Path: </b>{self.project_configuration.t32_executable_name}<br/>"
            f"<b>Additional Paths: </b>{self.project_configuration.additional_paths}<br/>"
        )
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Config File Data")
        msg.setWindowIcon(
            QtGui.QIcon(
                os.path.abspath(
                    os.path.join(os.path.dirname(os.path.realpath(__file__)), "gui_images", "logo_icon.png")
                )
            )
        )
        msg.setTextFormat(QtCore.Qt.RichText)
        msg.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        msg.setText(data)
        msg.exec_()

    def line_wrap_log_prints(self):
        """
        Method for enabling and disabling line wrap of output log print on console
        """
        self.user_config.line_wrap = self.action_Line_wrap_output_log.isChecked()
        if self.action_Line_wrap_output_log.isChecked():
            self.output_console_textedit.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        else:
            self.output_console_textedit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

    def create_subtree_view(self, parent_item, test_type_dict):
        """
        Method for creating nested tree view recursively based on loading of test_type dictionary

        :param QStandardItem parent_item :  this QStandard item is used to create the tree view based on input as
            test_type_dict
        :param dict test_type_dict : final test type dictionary is used to tree_view
        """
        # checks test_type_dict is dictionary or not if it is dict then enter into for loop and get
        # key and value. key = folder. sub folder and  value =  test_file_cases
        if isinstance(test_type_dict, dict):
            for folder_subfolder, test_file_cases in test_type_dict.items():
                # Process event handler to not leave QApplication to not responding
                QtWidgets.QApplication.processEvents()
                folder_obj_item = QtGui.QStandardItem(folder_subfolder)
                folder_obj_item.setCheckable(True)
                folder_obj_item.setTristate(True)
                # column 1 is folder_obj_item, here tag information needed for .cmm
                if folder_subfolder.endswith(".cmm"):
                    tags_list = self.data.get_test_case_tags()[folder_subfolder]
                    folder_tag_obj_item = QtGui.QStandardItem(", ".join(tags_list))
                    self.tests_q_st_items_objs.append(folder_obj_item)
                else:
                    folder_tag_obj_item = QtGui.QStandardItem(" ")
                parent_item.appendRow([folder_obj_item, folder_tag_obj_item])
                # call recursively folder_obj_item,test_file_cases
                self.create_subtree_view(folder_obj_item, test_file_cases)
        # checks test_type_dict is list type enter into for loop  and value is  test_case
        elif isinstance(test_type_dict, list):
            for test_case in test_type_dict:
                # Process event handler to not leave QApplication to not responding
                QtWidgets.QApplication.processEvents()
                test_case_obj_item = QtGui.QStandardItem(test_case)
                test_case_obj_item.setCheckable(True)
                test_case_obj_item.setTristate(True)
                self.tests_q_st_items_objs.append(test_case_obj_item)
                # get the tags_list base on test_case key
                tags_list = self.data.get_test_case_tags()[test_case]
                # if tags_list is not None then add tag_list to the particular test_case_obj
                # else no tag is added only the test case
                if tags_list is not None:
                    test_tag_obj_item = QtGui.QStandardItem(", ".join(tags_list))
                    # column 1 is test_case_obj ---> column2 is tag info append to parent_item
                    parent_item.appendRow([test_case_obj_item, test_tag_obj_item])
                else:
                    # column 1 is test_case_obj, No tag info
                    testcase_else_tag_obj_item = QtGui.QStandardItem(" ")
                    parent_item.appendRow([test_case_obj_item, testcase_else_tag_obj_item])

    def create_canoe_subtree_view(self, canoe_parent_item, test_data):
        """
        Method for creating CANoe tests tree/sub-tree view with gathered data from canoe cfg

        :param QStandardItem canoe_parent_item: Parent QStandardItem
        :param dict test_data: Test modules hierarchy data dictionary
        """
        for module, module_info in test_data.items():
            # Process event handler to not leave QApplication to not responding
            QtWidgets.QApplication.processEvents()
            module_obj_item = QtGui.QStandardItem(module)
            module_obj_item.setCheckable(True)
            module_obj_item.setTristate(True)
            if isinstance(module_info, dict):
                canoe_parent_item.appendRow([module_obj_item, QtGui.QStandardItem(" ")])
                for sub_module, sub_module_info in module_info.items():
                    sub_module_obj_item = QtGui.QStandardItem(sub_module)
                    sub_module_obj_item.setCheckable(True)
                    sub_module_obj_item.setTristate(True)
                    if isinstance(sub_module_info, dict):
                        module_obj_item.appendRow([sub_module_obj_item, QtGui.QStandardItem(" ")])
                        self.create_canoe_subtree_view(sub_module_obj_item, sub_module_info)
                    else:
                        module_obj_item.appendRow(
                            [sub_module_obj_item, QtGui.QStandardItem(ui_helper.CANOE_FILTER_NAME)]
                        )
                        self.data.tag_filter_tests[ui_helper.CANOE_FILTER_NAME].append(sub_module)
                        self.data.appearing_overall_tests.append(sub_module)
                        self.tests_q_st_items_objs.append(sub_module_obj_item)
            else:
                canoe_parent_item.appendRow([module_obj_item, QtGui.QStandardItem(ui_helper.CANOE_FILTER_NAME)])
                self.data.tag_filter_tests[ui_helper.CANOE_FILTER_NAME].append(module)
                self.data.appearing_overall_tests.append(module)
                self.tests_q_st_items_objs.append(module_obj_item)

    def create_tree_view(self, main_parent_item):
        """
        Method for creating nested final tree view recursively

        :param QStandardItem main_parent_item:  QStandard item is used to create the final tree view
        """
        # clearing the list containing the objects of all tests which were saved during the last attempt of
        # contest configuration loading, this is done in order to store new and fresh tests qtstandarditem objects
        self.tests_q_st_items_objs.clear()
        # creation of python tests with QStandard item column 0  test cases
        if self.data.get_pytest_files():
            python_tests_item = QtGui.QStandardItem(ui_helper.PYTHON_TESTS_QT_STR)
            python_tests_item.setCheckable(True)
            python_tests_item.setTristate(True)
            python_tests_item.setToolTip(f"Tests Location: {self.project_configuration.ptf_test_path}")
            self.create_subtree_view(
                python_tests_item, self.data.get_directory_structure(self.data.get_ptf_path(), "swt_*.pytest")
            )
            # column 1 tags information
            python_tags_item = QtGui.QStandardItem(" ")
            main_parent_item.appendRow([python_tests_item, python_tags_item])
        # creation of trace32 tests with QStandard item column 0  test cases
        if self.data.get_cmm_files():
            trace32_tests_item = QtGui.QStandardItem(ui_helper.T32_TESTS_QT_STR)
            trace32_tests_item.setCheckable(True)
            trace32_tests_item.setTristate(True)
            trace32_tests_item.setToolTip(f"Tests Location: {self.project_configuration.cmm_test_path}")
            self.create_subtree_view(
                trace32_tests_item, self.data.get_directory_structure(self.data.get_cmm_path(), "SWT_*.cmm")
            )
            # column 1 tags information
            trace32_tags_item = QtGui.QStandardItem(" ")
            main_parent_item.appendRow([trace32_tests_item, trace32_tags_item])
        if bool(self.data.data["canoe_test_data"]):
            self.data.tag_filter_tests[ui_helper.CANOE_FILTER_NAME] = []
            canoe_cfg_item = QtGui.QStandardItem(ui_helper.CANOE_TESTS_QT_STR)
            canoe_cfg_item.setCheckable(True)
            canoe_cfg_item.setTristate(True)
            canoe_cfg_item.setToolTip(f"Cfg Containing Tests: {self.project_configuration.canoe_cfg_path}")
            self.create_canoe_subtree_view(canoe_cfg_item, self.data.data["canoe_test_data"])
            # column 1 tags information
            canoe_cfg_tags_item = QtGui.QStandardItem(" ")
            main_parent_item.appendRow([canoe_cfg_item, canoe_cfg_tags_item])

    def test_case_parameter_view(self, test_data):
        """
        This method is executed when user selected parameterized test case from context menu of
        tree view,  the Table view pop up with available parameters of test case and its values

        :param object test_data: contains test case information
        """
        self.test_case_parameter_obj = test_case_parameterized.TestCaseParametersView(self, test_data)
        self.test_case_parameter_obj.exec()

    def filter_tests_with_cli_filter_value(self, cli_filter):
        """
        Method to filter data on gui based on selected test tag.
        This method is triggered when the user selects a new option on Filter combo box on GUI.

        :param list cli_filter: Filter list from cli
        """

        # updating the filter tags check boxes in combo box to unchecked state
        self.update_filter_tags_check_boxes(QtCore.Qt.Unchecked)
        list_filter_tags = list(self.data.get_tags().keys())
        filter_type = cli_filter[0]
        filter_values = cli_filter[1:]
        check_filter_tags_flag = False
        invalid_filter_tags = []
        for filter_value in filter_values:
            # Set the "tag" filter
            if filter_type.upper() == global_vars.ValidFilter.TAG.name:
                for i in range(self.stage_select_combobox.model().rowCount()):
                    tag = self.stage_select_combobox.model().item(i).text().split("(")[0].strip()
                    if filter_value == tag:
                        self.stage_select_combobox.model().item(i).setCheckState(QtCore.Qt.Checked)
            # this if case is for valid tags else invalid case
            if filter_value in list_filter_tags:
                # Here the update and apply checked filter tags
                self.update_all_tags_check_box()
                self.apply_filter(self.get_checked_filter_tags())
                check_filter_tags_flag = True
            else:
                # adding the invalid tags
                invalid_filter_tags.append(filter_value)
        # this use case is invalid tags provided by user with valid tags or only invalid tags
        # from cmd line
        if invalid_filter_tags:
            not_found_message = f"Found Invalid Tags: {invalid_filter_tags}. Invalid Tags are ignored."
            LOG.warning(not_found_message)
            ui_helper.pop_up_msg(helper.InfoLevelType.INFO, not_found_message, self.args["auto_mode"])
        # this use case is when user provided invalid tags only from command line
        if not check_filter_tags_flag:
            empty_tags = []
            self.cb_all_tags.setCheckState(QtCore.Qt.Unchecked)
            self.apply_filter(empty_tags)

    def apply_filter(self, filter_tags):
        """
        Method is triggered when filter tags/all tags check boxes are set to checked/unchecked state

        :param list filter_tags: list contains selected filter tags
        """

        self.clear_tree_status(self.test_cases_model.itemFromIndex(self.test_cases_model.index(0, 0)))
        # change tab to select and run if view is on another tab
        if self.select_tests_tabwidget.currentIndex() != self.select_run_tab:
            self.select_tests_tabwidget.setCurrentIndex(self.select_run_tab)
        # IF case, all tags/ filter tags are selected then apply for the selected
        # filters, other wise else no tags are selected case
        if filter_tags:
            selected_tags = []
            for filter_tag in filter_tags:
                selected_tags.append(filter_tag.split("(")[0].strip())
            # this regular expression with OR operation for the filter selection combinations
            # example:  integration | sil | 7 | req
            if self.cb_or_tags_filter.isChecked():
                text_tag = "|".join(selected_tags)
            # this regular expression with AND operation for the filter selection combinations
            # example:  integration & sil & 7 & req
            if self.cb_and_tags_filter.isChecked():
                text_tag = "\\b)(?=.*\\b".join(selected_tags)
                text_tag = "(?=.*\\b" + text_tag + "\\b)"
            # this regular expression matches exactly the same tag in tags column
            # which is being selected in the combo-box in gui
            text_tag = "\\b(" + text_tag + ")\\b"
            # test case filter pattern set as RegExp by default
            syntax = QtCore.QRegExp.PatternSyntax(QRegExp.RegExp)
            regexp = QRegExp(text_tag, Qt.CaseSensitive, syntax)
            self.filter_proxy_model.setFilterKeyColumn(1)
            self.filter_proxy_model.setFilterRegExp(regexp)
            # change tab to select and run if view is on another tab
            if self.select_tests_tabwidget.currentIndex() != self.select_run_tab:
                self.select_tests_tabwidget.setCurrentIndex(self.select_run_tab)
            # uncheck test case model based on filter tag change
            self.__uncheck_test_case_model_based_on_filtering()
        else:
            syntax = QtCore.QRegExp.PatternSyntax(QRegExp.RegExp)
            # No filter tags  are selected just provided "!" operator
            regexp = QRegExp("!", Qt.CaseSensitive, syntax)
            self.filter_proxy_model.setFilterKeyColumn(1)
            self.filter_proxy_model.setFilterRegExp(regexp)
            # uncheck test case model based on filter tag change
            self.__uncheck_test_case_model_based_on_filtering()

    @staticmethod
    def report_error_from_data_reporter(error):
        """
        Method for reporting error coming from data reporter
        """
        LOG.error(error)
        # Add 3rd argument to disable error pop up when auto_gui or auto mode
        ui_helper.pop_up_msg(
            helper.InfoLevelType.ERR,
            f"Error happened during data preparation step {error}" "\n\nPlease check console for details",
            ui_helper.CLI_OPTIONS["auto_gui"],
        )

    def event_log(self):
        """
        Method for displaying message box when message icon is pressed
        """
        if self.dockWidget.isVisible():
            self.dockWidget.hide()
        else:
            self.dockWidget.show()

    def event_log_handler(self, icon_color):
        """
        Method for changing the icon color for different events messages. The latest level of the
        message is displayed
        """
        err_icon = QtGui.QIcon(ui_helper.ERR_ICON)
        warn_icon = QtGui.QIcon(ui_helper.WARN_ICON)
        info_icon = QtGui.QIcon(ui_helper.INFO_ICON)
        if icon_color == "#E74C3C":
            self.msg_toolButton.setIcon(err_icon)
        elif icon_color == "#E67E22":
            self.msg_toolButton.setIcon(warn_icon)
        else:
            self.msg_toolButton.setIcon(info_icon)

    def show_what_is_new(self):
        """
        Method shows what is new on the latest release of Contest
        """
        # User downloads the latest version and run the Contest
        config_version = tuple(map(int, (self.user_config.version.split("."))))
        if global_vars.LOCAL_VERSION_TUPLE:
            # if the contest version is less than downloaded version
            if config_version < global_vars.LOCAL_VERSION_TUPLE:
                self.user_config.show_whats_new = True
                self.user_config.version = global_vars.VERSION
            # if the contest version is greater than downloaded version
            elif config_version > global_vars.LOCAL_VERSION_TUPLE:
                self.user_config.show_whats_new = True
                self.user_config.version = global_vars.VERSION

        # This will be shown when ever the contest is started, Until user checked the Don't show
        # check box
        if self.user_config.show_whats_new:
            self.what_new_window_obj.exec()
            self.user_config.show_whats_new = self.what_new_window_obj.donot_show_checked


class EmittingStream(QtCore.QObject):
    """
    Custom class defined here for the purpose to re-route the stdout stream
    to GUI.
    """

    # Defining a pyqt signal. Signal name is 'print_is_called'
    print_is_called = QtCore.pyqtSignal(str)

    def __init__(self, print_is_called):
        """
        Creates a new console emitting stream object. Will call the given slot once a full line
        is received.

        :param func print_is_called: The function to call once a full line is written
        """
        super().__init__()
        # The buffer to store intermediate lines
        self.buffer = ""
        # connect the signal with our function given as parameter
        self.print_is_called.connect(print_is_called)

    # This write function will be assigned to stdout.write later in MainGUI class
    def write(self, text):
        """
        This method replaces 'sys.stdout.write' to make print statement compatible to write on GUI
        console. It also print's statements to console using original 'sys.stdout' object.

        :param string text: Information to be printed on console as well as on GUI output area
        """
        # display 'text' to console
        ui_helper.STD_OUT_ORIGINAL.write(text)

        # If we have a newline in text, we need to emit the current buffer plus the text
        if "\n" in text:
            # Always print all lines before the last newline
            for line in text.split("\n")[:-1]:
                self.print_is_called.emit(self.buffer + line)
                self.buffer = ""

            # If the text doesn't end with newline, we need to store the rest of the line
            # in the buffer
            if not text.endswith("\n"):
                self.buffer = text.rsplit("\n", 1)[1]

        # If we don't have a newline in current received text, store it in buffer
        else:
            self.buffer = self.buffer + text

    def flush(self):
        """
        This method replaces stdout.flush, not defining it will raise an error here.
        """
        pass  # pylint: disable=unnecessary-pass


# no need for public methods in the utility install manager thread class
# pylint: disable=too-few-public-methods
class UimInfoThread(QtCore.QThread):
    """
    Class for running UIM (Utility Install Manager) actions or functionalities
    """

    uim_info_result = QtCore.pyqtSignal(dict)
    add_data = QtCore.pyqtSignal(dict)
    ready_state = QtCore.pyqtSignal()
    network_error = QtCore.pyqtSignal(bool)
    general_error = QtCore.pyqtSignal(str)

    def __init__(self, gui_obj):
        """
        Constructor

        :param object gui_obj: UIController class object
        """
        QtCore.QThread.__init__(self)
        self.gui_obj = gui_obj
        self.add_data.connect(gui_obj.uim_manager.add_data)
        self.ready_state.connect(gui_obj.uim_manager.ready_state)
        self.network_error.connect(gui_obj.uim_manager.report_network_error)
        self.general_error.connect(gui_obj.uim_manager.report_general_error)
        self.uim_signals = {
            "uim_info_result": self.uim_info_result,
            "add_data": self.add_data,
            "ready_state": self.ready_state,
            "network_error": self.network_error,
            "general_error": self.general_error,
        }

    def run(self):
        """
        Method to run contest packages fetching code in a QThread
        """
        if not uim.check_artifactory_connection():
            self.uim_signals["network_error"].emit(False)
        else:
            uim.get_contest_pkgs_from_remote(with_versions=True, ui_signals=self.uim_signals)


class ThreadClass(QtCore.QThread):
    """
    Main testing code of framework is ran in a separate thread class to avoid
    blocking of GUI
    """

    complete_sig = QtCore.pyqtSignal(name="Test_Execution_Completion")

    def __init__(self, gui_obj):
        """constructor"""
        QtCore.QThread.__init__(self)
        self.gui_obj = gui_obj
        self.complete_sig.connect(gui_obj.test_completion_task)

    def run(self):
        """
        Method for triggering test runner in this separate thread class
        """
        # ok to use global here
        # pylint: disable=global-statement
        global RETURN_CODE
        # importing test_runner here because before this step the ptf related paths will be
        # added to sys.path. This change is done specifically for importing "report" in
        # "test_watcher.py" file directly which solves report generation issue
        # pylint: disable=import-outside-toplevel
        from ptf.ptf_utils import test_runner

        LOG.info("Triggering test runner ...")
        # check if only failed tests should be executed
        if self.gui_obj.run_only_failed.isChecked():
            test_filter = self.gui_obj.get_last_failed_tests()
            self.gui_obj.clear_last_failed_tests()
        else:
            test_filter = None
        # changing test execution flag to True
        self.gui_obj.tests_running = True
        # creating an instance of PTF test runner by passing controlling specs
        test_runner = test_runner.TestRunner(self.gui_obj.data, test_filter)
        # triggering test runner
        RETURN_CODE = test_runner.run()
        # emitting a custom signal to perform tasks at end of test execution
        # this signal is connected with test_completion_task() method
        self.complete_sig.emit()


# the return is in finally block to return code to main module and error are captured and logged
# pylint: disable=inconsistent-return-statements
# main function to run GUI
def run_gui(args=None, selected_tests_exec_record=None):
    """
    Function for calling main GUI for loading of test cases and triggering test runner based on
    selected options from tester

    :param argparser args: Command line arguments if any
    :param list selected_tests_exec_record: Selected test cases that needs to be run based on selected verdict,
                when run_exec_record was requested on CLI
    """
    # ok to use global here
    # pylint: disable=global-statement
    global RETURN_CODE
    start = time.time()
    logo = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "gui_images", "splash_scr.png"))
    # if environment or system is windows then change taskbar icon
    if platform.system() == "Windows":
        # Setting up an arbitrary string as app user model ID
        # This ID is used as registry key to tell Windows that Python.exe is just a host rather
        # than an application in its own right and hence allow GUI to display its own icon on
        # taskbar
        app_id = "Continental.SoftwareTestingTool.ConTest"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    try:
        app = QtWidgets.QApplication(sys.argv)
        splash = None
        if args.r != "auto":
            splash = QtWidgets.QSplashScreen(QtGui.QPixmap(logo), QtCore.Qt.WindowStaysOnTopHint)
            splash.show()
            splash.showMessage(
                "Version " + global_vars.CONTEST_VERSION + "\nDeveloped by A AM ENP TEPM TPT\n"
                "Test Platform Tools & Innovation Team\n"
                "© Copyright " + time.strftime("%Y") + " Continental Corporation",
                alignment=QtCore.Qt.AlignHorizontal_Mask | QtCore.Qt.AlignBottom,
                color=QtCore.Qt.darkBlue,
            )

            while time.time() - start < 2:
                time.sleep(0.1)
                app.processEvents()

        # closing the advertisement splash screen before UI main controller takes any action
        if splash:
            splash.finish(None)

        gui_app = UIController(args=args, selected_tests_exec_record=selected_tests_exec_record)
        gui_app.setWindowTitle(global_vars.gui_window_title)
        gui_app.show()

        # show what is new with latest release information only when run mode is not auto_gui
        if not args.r == global_vars.AUTO_GUI_MODE:
            gui_app.show_what_is_new()

        app.exec_()

    except RuntimeError as error:
        RETURN_CODE = global_vars.GENERAL_ERR
        LOG.error("ERROR during UI stage ...")
        LOG.error("-" * 150)
        sys.stdout = sys.__stdout__
        LOG.error(error)
        LOG.error("-" * 150)
    except BaseException as exception:  # pylint: disable=broad-except
        RETURN_CODE = global_vars.GENERAL_ERR
        LOG.error("Base Exception is raised")
        LOG.error("-" * 150)
        sys.stdout = sys.__stdout__
        LOG.exception(exception)
        LOG.error("-" * 150)
    finally:
        sys.stdout = sys.__stdout__
        # all exceptions will be captured in above 'BaseException' and logged
        # pylint: disable=lost-exception, return-in-finally
        return RETURN_CODE
