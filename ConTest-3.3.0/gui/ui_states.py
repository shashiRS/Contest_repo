"""
    File for controlling ConTest GUI states
    Copyright 2018 Continental Corporation

    :file: gui_state_controller.py
    :platform: Windows, Linux
    :synopsis:
        This file contains control class for the ConTest GUI state-machine which handles the
        states of GUI at each different level.

    :authors:
        - Christopher Mirajkar <Christopher.Charles.Mirajkar@continental-corporation.com>
        - M. F. Ali Khan <muhammad.fakhar.ali.khan@continental-corporation.com>
"""
import os
import sys

import qdarkstyle
from PyQt5 import QtCore
from gui.design_files.common_gui import Ui_MainWindow

from PyQt5.QtWidgets import QApplication, QMainWindow

from .gui_utils.user_config_handler import UserConfigHandler
from . import ui_helper

# Adding current directory to system path so that UI could access resource module
# Command for converting .qrc to .py: 'pyrcc5 resource.qrc -o resource_rc.py'
sys.path.append(os.path.dirname(__file__))


class UIStates(QMainWindow, Ui_MainWindow):
    """
    Control class for ConTest GUI state-machine. It inherits all GUI data
    from BASE, FORM class of UI.
    """
    # signals are emitted from the controller, on fulfilling the conditions to make a transition
    # from one state to another
    initial_state = QtCore.pyqtSignal(name="state_start")
    post_config_load_state = QtCore.pyqtSignal(name="state_ptf_test")
    tests_runner_state = QtCore.pyqtSignal(name="state_tests_runner")

    def __init__(self):
        super().__init__()

        # ----------------------------CLASS VARIABLES--------------------------
        self.select_run_tab = 0
        self.select_fw_tab = 1
        self.set_base_loc_tab = 1
        self.output_tab = 1
        self.tools_tab = 2
        self.save_load_tab = 3
        self.console_slider_moved = False
        self.user_config = UserConfigHandler()

        # --------------------------------SIGNALS------------------------------
        # if 'state_start' signal is emitted, execute 'initial_state_actions' function
        self.initial_state.connect(self.initial_state_actions)
        # if 'state_ptf_test' signal is emitted, execute 'post_config_load_state_actions' function
        self.post_config_load_state.connect(self.post_config_load_state_actions)
        # if 'tests_runner_state' signal is emitted, execute 'state_runner_start' function
        self.tests_runner_state.connect(self.state_runner_start)

    def initial_state_actions(self):
        """
        This method is called at the start up of the UI. Sets up initial state for the ConTest GUI
        """
        # disabling items
        self.select_tests_tabwidget.setTabEnabled(self.output_tab, False)
        self.total_running_lcd.setEnabled(False)
        self.passed_running_lcd.setEnabled(False)
        self.failed_running_lcd.setEnabled(False)
        self.skip_running_lcd.setEnabled(False)
        self.inconclusive_running_lcd.setEnabled(False)
        self.exe_time_lcd.setEnabled(False)
        self.main_treeview.setEnabled(False)
        self.runtest_pushbutton.setEnabled(False)
        self.stop_pushbutton.setEnabled(False)
        self.reload_pushbutton.setEnabled(False)
        self.searchbar_linedit.setEnabled(False)
        self.expand_tree_pushbutton.setEnabled(False)
        self.expand_tree_pushbutton.setEnabled(False)
        self.filter_groupbox.setEnabled(False)
        self.loopstorun_groupbox.setEnabled(False)
        self.num_sel_tests_lcd.setEnabled(False)
        self.num_total_tests_lcd.setEnabled(False)
        self.actionReset.setEnabled(False)
        self.action_report_open.setEnabled(False)
        self.action_open_html_report.setEnabled(False)
        self.action_open_txt_report.setEnabled(False)
        self.action_open_json_report.setEnabled(False)
        self.action_open_xml_report.setEnabled(False)
        self.action_open_cathat_xml_report.setEnabled(False)
        self.action_config_file_data.setEnabled(False)
        self.actionEdit_Config.setEnabled(False)
        self.actionSave_Config.setEnabled(False)
        self.actionSave_as_config.setEnabled(False)
        self.menuCreate_new_py_file.setEnabled(False)
        self.action_open_setup_file.setEnabled(False)
        self.action_open_base_loc.setEnabled(False)
        self.action_open_pytest_loc.setEnabled(False)
        self.action_external_report_open.setEnabled(False)
        # Load settings
        self.action_reopen_last_opened_configuration.setChecked(
            self.user_config.reopen_last_configuration)
        self.action_Line_wrap_output_log.setChecked(self.user_config.line_wrap)
        if self.user_config.darkmode:
            self.slider_dark_mode.setSliderPosition(1)
        else:
            self.slider_dark_mode.setSliderPosition(0)
        self.dark_mode()

    def dark_mode(self):
        """
        This method enables and disables the UI Dark Mode, based on the state of the dark_mode
        """
        # Get the currently running QApplication object (GUI)
        app = QApplication.instance()
        # If User switched on to Dark Mode, load the stylesheet from qdarkstyle.
        if self.slider_dark_mode.sliderPosition() == 1:
            self.user_config.darkmode = True
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        # If User switched off Dark Mode, load an "empty" stylesheet to restore default color value
        else:
            self.user_config.darkmode = False
            app.setStyleSheet('')

    def post_config_load_state_actions(self):
        """
        This state will be triggered when Project Base Location and all directories in prj config
        is verified
        GUI shall be put into this state only when the conditions for the transition is fulfilled
        """
        self.actionReset.setEnabled(True)
        self.main_treeview.setEnabled(True)
        self.actionEdit_Config.setEnabled(True)
        self.searchbar_linedit.setEnabled(True)
        self.expand_tree_pushbutton.setEnabled(True)
        self.filter_groupbox.setEnabled(True)
        self.loopstorun_groupbox.setEnabled(True)
        self.num_sel_tests_lcd.setEnabled(True)
        self.num_total_tests_lcd.setEnabled(True)
        self.reload_pushbutton.setEnabled(True)
        self.actionSave_Config.setEnabled(True)
        self.actionSave_as_config.setEnabled(True)
        self.action_report_open.setEnabled(False)
        self.action_external_report_open.setEnabled(False)
        self.action_open_html_report.setEnabled(False)
        self.action_open_txt_report.setEnabled(False)
        self.action_open_json_report.setEnabled(False)
        self.action_open_xml_report.setEnabled(False)
        self.action_open_cathat_xml_report.setEnabled(False)
        self.action_config_file_data.setEnabled(True)
        self.menuCreate_new_py_file.setEnabled(True)
        self.action_open_setup_file.setEnabled(True)
        self.action_open_base_loc.setEnabled(True)
        self.action_open_pytest_loc.setEnabled(True)
        self.total_running_lcd.setEnabled(False)
        self.passed_running_lcd.setEnabled(False)
        self.failed_running_lcd.setEnabled(False)
        self.skip_running_lcd.setEnabled(False)
        self.inconclusive_running_lcd.setEnabled(False)
        self.exe_time_lcd.setEnabled(False)
        self.total_running_lcd.display(0)
        self.passed_running_lcd.display(0)
        self.failed_running_lcd.display(0)
        self.skip_running_lcd.display(0)
        self.inconclusive_running_lcd.display(0)
        self.exe_time_lcd.display(0)
        self.passed_running_lcd.setStyleSheet(ui_helper.NON_RUNNING_LCD_NUM)
        self.failed_running_lcd.setStyleSheet(ui_helper.NON_RUNNING_LCD_NUM)
        self.inconclusive_running_lcd.setStyleSheet(ui_helper.NON_RUNNING_LCD_NUM)
        self.skip_running_lcd.setStyleSheet(ui_helper.NON_RUNNING_LCD_NUM)

    def state_runner_start(self):
        """
        GUI enters this state when test execution is started i.e. when RUN button is pressed
        GUI shall be put into this state only when the conditions for the transition is fulfilled
        """
        self.select_tests_tabwidget.setTabEnabled(self.output_tab, True)
        self.select_tests_tabwidget.setCurrentIndex(self.output_tab)
        self.total_running_lcd.setEnabled(True)
        self.passed_running_lcd.setEnabled(True)
        self.failed_running_lcd.setEnabled(True)
        self.inconclusive_running_lcd.setEnabled(True)
        self.skip_running_lcd.setEnabled(True)
        self.exe_time_lcd.setEnabled(True)
        self.action_report_open.setEnabled(False)
        self.action_external_report_open.setEnabled(False)
        self.action_open_html_report.setEnabled(False)
        self.action_open_txt_report.setEnabled(False)
        self.action_open_json_report.setEnabled(False)
        self.action_open_xml_report.setEnabled(False)
        self.action_open_cathat_xml_report.setEnabled(False)
        self.reload_pushbutton.setEnabled(False)
        # enable filter tags and filter check box
        self.stage_select_combobox.setDisabled(True)
        self.cb_all_tags.setDisabled(True)

    def reset_ptf(self):
        """
        This method resets UI whenever user selects a new PTF project
        """
        # Clearing main tree view by setting its model to None
        self.main_treeview.setModel(None)
        # Resetting loops to run
        self.loops_to_run_spinbox.setValue(1)
        # Disabling all other UI widgets:
        self.main_treeview.setEnabled(True)
        self.runtest_pushbutton.setEnabled(False)
        self.stop_pushbutton.setEnabled(False)
        self.reload_pushbutton.setEnabled(False)
        self.searchbar_linedit.setEnabled(False)
        self.expand_tree_pushbutton.setEnabled(False)
        self.searchbar_linedit.clear()
        self.filter_groupbox.setEnabled(False)
        self.stage_select_combobox.setCurrentIndex(0)
        self.loopstorun_groupbox.setEnabled(False)
        self.num_sel_tests_lcd.setEnabled(False)
        self.num_total_tests_lcd.setEnabled(False)
        self.actionCreate_config.setEnabled(True)
        self.actionEdit_Config.setEnabled(False)
        self.actionSave_Config.setEnabled(False)
        self.actionSave_as_config.setEnabled(False)
        self.action_report_open.setEnabled(False)
        self.action_external_report_open.setEnabled(False)
        self.action_open_html_report.setEnabled(False)
        self.action_open_txt_report.setEnabled(False)
        self.action_open_json_report.setEnabled(False)
        self.action_open_xml_report.setEnabled(False)
        self.action_open_cathat_xml_report.setEnabled(False)
        self.action_config_file_data.setEnabled(False)
        self.run_only_failed.setEnabled(False)
        self.run_only_failed.setChecked(False)
        self.random_execution.setEnabled(False)
        self.random_execution.setChecked(False)
        self.cb_run_unselected.setEnabled(False)
        self.cb_run_unselected.setChecked(False)
        self.select_tests_tabwidget.setTabEnabled(self.output_tab, False)
        self.total_running_lcd.setEnabled(False)
        self.passed_running_lcd.setEnabled(False)
        self.failed_running_lcd.setEnabled(False)
        self.inconclusive_running_lcd.setEnabled(False)
        self.skip_running_lcd.setEnabled(False)
        self.exe_time_lcd.setEnabled(False)
        # reset proxy filter to default value
        self.filter_proxy_model.setFilterRegExp('')
        # Clearing output side of UI
        self.output_tablewidget.clear()
        self.tests_progressbar.setValue(0)
        self.total_running_lcd.display(0)
        self.passed_running_lcd.display(0)
        self.failed_running_lcd.display(0)
        self.inconclusive_running_lcd.display(0)
        self.skip_running_lcd.display(0)
        self.exe_time_lcd.display(0)
        self.passed_running_lcd.setStyleSheet(ui_helper.NON_RUNNING_LCD_NUM)
        self.failed_running_lcd.setStyleSheet(ui_helper.NON_RUNNING_LCD_NUM)
        self.inconclusive_running_lcd.setStyleSheet(ui_helper.NON_RUNNING_LCD_NUM)
        self.skip_running_lcd.setStyleSheet(ui_helper.NON_RUNNING_LCD_NUM)
        self.output_console_textedit.clear()
        self.menuCreate_new_py_file.setEnabled(False)
        self.action_open_setup_file.setEnabled(False)
        self.action_open_base_loc.setEnabled(False)
        self.action_open_pytest_loc.setEnabled(False)
        self.initial_state_actions()
        # Clearing the LCDs
        self.num_sel_tests_lcd.display(0)
        self.num_total_tests_lcd.display(0)
