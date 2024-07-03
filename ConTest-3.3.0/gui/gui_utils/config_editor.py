"""
    File for handling the configuration editor
    Copyright 2018 Continental Corporation

    :file: config_editor.py
    :platform: Windows, Linux
    :synopsis:
        This file contains project configurator editor class for contest. It provides options
        to the user to store various paths and installation directories.

    :author:
        M. F. Ali Khan <muhammad.fakhar.ali.khan@continental-corporation.com>
        Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""
import logging
import os
import itertools
from pathlib import Path
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog
from gui.design_files.config import Ui_Dialog
from gui.gui_utils.project_config_handler import ProjectConfigHandler
from gui.gui_utils.user_config_handler import UserConfigHandler
from data_handling import helper
from . import test_template
from .. import ui_helper

LOG = logging.getLogger('Config Editor')


class ConfigEditor(QDialog, Ui_Dialog):
    """
    PTF configurator controlling class which inherits from its corresponding ui.
    This class is responsible for filling up, saving and loading of configurator file.
    """

    def __init__(self, controller_obj, edit_mode=False, cfg_file=""):
        """
        Constructor

        :param object controller_obj: passing GUI main controller class as argument
        :param bool edit_mode: True if config has to be set to edit mode. Default value False
        :param string cfg_file: Path of config file that has to be edited. Default empty string
        """
        # super initialization to access parent or base class method or data
        super().__init__()
        # assigning "PTFConfigurator" object to "setupUi" that is designer interface
        self.setupUi(self)
        # assigning argument(s) in to a variable
        self.controller_obj = controller_obj
        self.edit_mode = edit_mode
        self.cfg_file = cfg_file
        self.err_load_file = []

        # setting button icons
        self.set_button_icons()

        # Finalize ui setup
        if self.edit_mode:
            self.__set_edit_configurator()
        else:
            self.save_as_pushbutton.setVisible(False)
            self.gui_set_groupbox.setVisible(False)
            self.sel_test_info_label.setVisible(False)
            self.resize(844, 562)
        # making UI connections
        self.__make_ui_connections()
        # read the config file to be edited
        self.project_config = ProjectConfigHandler()
        if cfg_file:
            self.project_config.load_config(cfg_file)

        # table_widget  init row and column properties settings
        self.selected_test_cases_model = None
        # list which will be populated with tests to delete during edit cfg stage
        self.tests_to_remove = list()
        # creating object of proxy model for live filtering of data i.e. test cases
        self.selected_filter_proxy_model = None
        self.__init_table_view()

        # set modal as true (i.e blocks background UI until dialog box execution completes)
        self.setModal(True)
        # setting up window icon
        self.setWindowIcon(QtGui.QIcon(os.path.abspath(os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '..', 'gui_images', 'logo_icon.png'))))
        self.text_color = "white;" if UserConfigHandler().darkmode else "black;"

    def __set_edit_configurator(self):
        """
        Method for setting up configuration file editing options
        """
        self.setWindowTitle("Edit Configuration")
        self.save_pushbutton.setText("  Save  ")
        self.save_pushbutton.setToolTip("Save changes")
        self.create_groupbox.setTitle("Edit:  " + str(self.cfg_file))

    @staticmethod
    def __create_pytest_files(test_location):
        """
        Method for creating helper file inside test suite location i.e. PTF tests location

        :param string test_location: User selected PTF test location
        """
        create_helper_files = ui_helper.ask_for_helper_files()
        if create_helper_files == QtWidgets.QMessageBox.Yes:
            if not os.path.isfile(os.path.join(test_location, 'setup.pytest')):
                with open(os.path.join(test_location, 'setup.pytest'), 'w+') as setup_file:
                    setup_file.write(test_template.SETUP_PYTEST)
                    LOG.info("setup.pytest file created at %s", test_location)
                with open(os.path.join(test_location, 'swt_sample_test.pytest'), 'w+') as test_file:
                    test_file.write(test_template.SAMPLE_TEST_FILE)
                    LOG.info("swt_sample_test.pytest file created at %s", test_location)
                with open(os.path.join(test_location, 'README.txt'), 'w+') as readme_file:
                    readme_file.write(test_template.READ_ME)
                    LOG.info("README.txt file created at %s", test_location)
                msg = 'Helper files created at {}\nPlease take a look in your base location\n\n' \
                      'Following files are generated:\n' \
                      '- setup.pytest (for setting-up tools or variables)\n' \
                      '- swt_sample_test.pytest (hello-world test case)\n' \
                      '- README.txt (read this for more details)'.format(test_location)
                ui_helper.pop_up_msg(helper.InfoLevelType.INFO, msg)
            else:
                msg = "Python test location already contains test files (setup.pytest, " \
                      "swt_sample_test.pytest, README.txt) therefore helper files creation " \
                      "action is ignored."
                LOG.info(msg)
                ui_helper.pop_up_msg(helper.InfoLevelType.INFO, msg)

    def __init_table_view(self):
        """
        Initializes the table view that contains the testcases in the current configuration
        """
        self.selected_test_cases_model = QtGui.QStandardItemModel()
        self.selected_test_cases_model.setColumnCount(1)
        self.selected_test_cases_model.setColumnCount(0)
        item = QtGui.QStandardItem("Selected_Tests")
        item.setTextAlignment(QtCore.Qt.AlignHCenter)
        self.selected_test_cases_model.setHorizontalHeaderItem(0, item)
        self.select_tests_table_view.horizontalHeader().hide()
        self.select_tests_table_view.horizontalHeader().setStretchLastSection(True)
        self.select_tests_table_view.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        self.selected_filter_proxy_model = QtCore.QSortFilterProxyModel()
        self.selected_filter_proxy_model.setFilterKeyColumn(1)

    def __make_ui_connections(self):
        """
        This method connects pyqt signals coming from various configurator options to the
        configurator methods
        """
        # test scripts section
        self.basepath_pushbutton.clicked.connect(self.base_path_saver)
        self.python_tests_pushbutton.clicked.connect(self.python_test_path_saver)
        self.cmmtests_pushbutton.clicked.connect(self.cmmtests_path_saver)
        self.canoe_cfg_pushbutton.clicked.connect(self.canoe_cfg_path_saver)
        self.cte_location_pushbutton.clicked.connect(self.cte_exe_path_saver)
        self.cte_cfg_pushbutton.clicked.connect(self.cte_cfg_path_saver)
        self.use_cte_checkbox.stateChanged.connect(self.handle_cte_usage)
        # report
        self.report_pushbutton.clicked.connect(self.report_path_saver)
        # misc
        self.additional_path_pushbutton.clicked.connect(self.additional_path_saver)
        # save to ini file
        self.save_pushbutton.clicked.connect(self.save_config)
        # save as ini file
        self.save_as_pushbutton.clicked.connect(self.save_as_config)
        # close the dialog
        self.close_pushbutton.clicked.connect(self.close)
        # context menu for the selected test case
        self.select_tests_table_view.customContextMenuRequested.connect(
            self.__on_custom_context_menu_requested)
        self.search_selected_testcase_lineedit.textChanged.connect(
            self.__text_changed_test_case_search)
        # when changes made to base location path, other paths' existence and within base location
        # checks are made then respective text colors are changed accordingly
        list(map(self.basepath_lineedit.textChanged.connect,
                 [self.__text_changed_base_path, self.__text_changed_ptf_path,
                  self.__text_changed_cmm_path, self.__text_changed_canoe_path,
                  self.__text_changed_report_path]))
        # edit path checks
        self.ptftests_lineedit.textChanged.connect(self.__text_changed_ptf_path)
        self.cmmtests_lineedit.textChanged.connect(self.__text_changed_cmm_path)
        self.report_lineedit.textChanged.connect(self.__text_changed_report_path)

    def __on_custom_context_menu_requested(self, pos):
        """
        Method for deleting the selected test case with right click context menu "Delete Row"
        """
        # mouse position on the table widget on right click provides the context menu
        index = self.select_tests_table_view.indexAt(pos)
        # context menu is created on Right click as "Remove Test Case"
        menu = QtWidgets.QMenu()
        remove_row_action = menu.addAction("Remove Test Case")
        action = menu.exec_(self.select_tests_table_view.viewport().mapToGlobal(pos))
        # action is as type "remove_row_action" check the condition to remove the selected test case
        if action == remove_row_action:
            # appending to remove tests list which will be used for saving purpose
            self.tests_to_remove.append(self.selected_test_cases_model.item(index.row(), 0).text())
            self.selected_test_cases_model.removeRow(index.row(), QtCore.QModelIndex())

    def __text_changed_test_case_search(self, text):
        """
        Method for search the selected test case with right click context menu "Delete Row"
        """
        # text is null after search, move the scroll to top
        if text == '':
            self.select_tests_table_view.scrollToTop()
            return

        self.selected_filter_proxy_model.setFilterFixedString(text)
        # get the start the index
        start_index = self.selected_filter_proxy_model.index(0, 0)
        # with stat index and text get the index_list
        index_list = self.selected_filter_proxy_model.match(start_index,
                                                            QtCore.Qt.DisplayRole, text, -1)
        # scroll to the search text index position
        for index in index_list:
            self.select_tests_table_view.scrollTo(index)

    def __text_changed_base_path(self, text):
        """
        Method for path check and display the color of text
        """
        if os.path.exists(text):
            self.basepath_lineedit.setStyleSheet("color: " + self.text_color)
        else:
            self.basepath_lineedit.setStyleSheet("color: red;")

    def __text_changed_ptf_path(self, text):
        """
         Method for ptf path check and display the color of text
        """
        if os.path.exists(text) and text.find(self.basepath_lineedit.text()) == 0:
            self.ptftests_lineedit.setStyleSheet("color: " + self.text_color)
        else:
            self.ptftests_lineedit.setStyleSheet("color: red;")

    def __text_changed_cmm_path(self, text):
        """
        Method for cmm path check and display the color of text
        """
        if os.path.exists(text) and text.find(self.basepath_lineedit.text()) == 0:
            self.cmmtests_lineedit.setStyleSheet("color: " + self.text_color)
        else:
            self.cmmtests_lineedit.setStyleSheet("color: red;")

    def __text_changed_canoe_path(self, text):
        """
        Method for capl path check and display the color of text
        """
        if os.path.exists(text) and text.find(self.basepath_lineedit.text()) == 0:
            self.canoe_cfg_linedit.setStyleSheet("color: " + self.text_color)
            pass
        else:
            self.canoe_cfg_linedit.setStyleSheet("color: red;")
            pass

    def __text_changed_report_path(self, text):
        """
        Method for report path check and display the color of text
        """
        self.report_lineedit.setStyleSheet("color: " + self.text_color)

    def set_button_icons(self):
        """
        Method to set nice button icons in configuration create/edit window
        """
        self.basepath_pushbutton.setIcon(QtGui.QIcon(ui_helper.BROWSE_ICON))
        self.base_loc_clear_button.setIcon(QtGui.QIcon(ui_helper.CLEAR_ICON))
        self.python_tests_pushbutton.setIcon(QtGui.QIcon(ui_helper.BROWSE_ICON))
        self.python_test_clear_button.setIcon(QtGui.QIcon(ui_helper.CLEAR_ICON))
        self.cmmtests_pushbutton.setIcon(QtGui.QIcon(ui_helper.BROWSE_ICON))
        self.cmm_test_clear_button.setIcon(QtGui.QIcon(ui_helper.CLEAR_ICON))
        self.canoe_cfg_pushbutton.setIcon(QtGui.QIcon(ui_helper.BROWSE_ICON))
        self.canoe_cfg_clear_button.setIcon(QtGui.QIcon(ui_helper.CLEAR_ICON))
        self.cte_location_pushbutton.setIcon(QtGui.QIcon(ui_helper.BROWSE_ICON))
        self.cte_exe_clear_button.setIcon(QtGui.QIcon(ui_helper.CLEAR_ICON))
        self.cte_cfg_pushbutton.setIcon(QtGui.QIcon(ui_helper.BROWSE_ICON))
        self.cte_cfg_clear_button.setIcon(QtGui.QIcon(ui_helper.CLEAR_ICON))
        self.report_pushbutton.setIcon(QtGui.QIcon(ui_helper.BROWSE_ICON))
        self.report_clear_button.setIcon(QtGui.QIcon(ui_helper.CLEAR_ICON))
        self.additional_path_pushbutton.setIcon(QtGui.QIcon(ui_helper.BROWSE_ICON))
        self.additional_path_clear_button.setIcon(QtGui.QIcon(ui_helper.CLEAR_ICON))

    def base_path_saver(self):
        """
        This method saves base path selected by the user.
        """
        base_path = QtWidgets.QFileDialog.getExistingDirectory(
            QtWidgets.QFileDialog(), 'Select Project Base Location', directory=str(Path.home()))
        if base_path:
            self.project_config.base_path = base_path
            self.basepath_lineedit.setText(self.project_config.base_path)
            self.ptftests_lineedit.setText(self.project_config.ptf_test_path)
            self.cmmtests_lineedit.setText(self.project_config.cmm_test_path)
            self.report_lineedit.setText(self.project_config.report_path)

    def python_test_path_saver(self):
        """
        This method saves PTF test path selected and restricts user to select this
        path inside the base location.
        """
        base_path = self.project_config.base_path
        if base_path:
            ptf_test_path = QtWidgets.QFileDialog.getExistingDirectory(
                QtWidgets.QFileDialog(), 'Select Python Tests Location', base_path)
            if ptf_test_path:
                try:
                    self.project_config.ptf_test_path = ptf_test_path
                    self.ptftests_lineedit.setText(ptf_test_path)
                    self.ptftests_lineedit.setCursorPosition(0)
                except RuntimeError as error:
                    self.__display_exception(error)
        else:
            LOG.error("Please, select the base location first")
            ui_helper.pop_up_msg(
                helper.InfoLevelType.ERR, "Please, select the base location first")

    def cmmtests_path_saver(self):
        """
        This method saves CMM test path selected and restricts user to select this
        path inside the base location.
        """
        base_path = self.project_config.base_path
        if base_path:
            cmm_test_path = QtWidgets.QFileDialog.getExistingDirectory(
                QtWidgets.QFileDialog(), 'Select CMM Tests Location', base_path)
            if cmm_test_path:
                try:
                    self.project_config.cmm_test_path = cmm_test_path
                    self.cmmtests_lineedit.setText(cmm_test_path)
                    self.cmmtests_lineedit.setCursorPosition(0)
                except RuntimeError as error:
                    self.__display_exception(error)
        else:
            LOG.error("Please, select the base location first")
            ui_helper.pop_up_msg(
                helper.InfoLevelType.ERR, "Please, select the base location first")

    def canoe_cfg_path_saver(self):
        """
        This method saves CANoe cfg path selected and restricts user to select this
        path inside the base location.
        """
        if not self.edit_mode:
            base_path = self.project_config.base_path
        else:
            base_path = self.basepath_lineedit.text()
        if base_path:
            canoe_cfg_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                QtWidgets.QFileDialog(),
                caption='Select CANoe Cfg Location',
                filter="*.cfg",
                directory=str(self.project_config.base_path))
            if canoe_cfg_path:
                try:
                    self.project_config.canoe_cfg_path = canoe_cfg_path
                    self.canoe_cfg_linedit.setText(canoe_cfg_path)
                    self.canoe_cfg_linedit.setCursorPosition(0)
                except RuntimeError as error:
                    self.__display_exception(error)
        else:
            LOG.error("Please, select the base location first")
            ui_helper.pop_up_msg(
                helper.InfoLevelType.ERR, "Please, select the base location first")

    def cte_exe_path_saver(self):
        """
        Method for saving CTF executable path
        """
        if not self.edit_mode:
            base_path = self.project_config.base_path
        else:
            base_path = self.basepath_lineedit.text()
        if base_path:
            cte_zip_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                QtWidgets.QFileDialog(),
                caption='Select CTF zip path',
                filter="*.zip",
                directory=str(self.project_config.base_path))
            if cte_zip_path:
                try:
                    self.project_config.cte_location = cte_zip_path
                    self.cte_zip_lineedit.setText(cte_zip_path)
                    self.cte_zip_lineedit.setCursorPosition(0)
                except RuntimeError as error:
                    self.__display_exception(error)
        else:
            LOG.error("Please, select the base location first")
            ui_helper.pop_up_msg(
                helper.InfoLevelType.ERR, "Please, select the base location first")

    def cte_cfg_path_saver(self):
        """
        Method for saving CTF cfg path
        """
        if not self.edit_mode:
            base_path = self.project_config.base_path
        else:
            base_path = self.basepath_lineedit.text()
        if base_path:
            cte_cfg_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                QtWidgets.QFileDialog(),
                caption='Select CTF Cfg Path',
                filter="*.ini",
                directory=str(self.project_config.base_path))
            if cte_cfg_path:
                try:
                    self.project_config.cte_cfg = cte_cfg_path
                    self.cte_cfg_lineedit.setText(cte_cfg_path)
                    self.cte_cfg_lineedit.setCursorPosition(0)
                except RuntimeError as error:
                    self.__display_exception(error)
        else:
            LOG.error("Please, select the base location first")
            ui_helper.pop_up_msg(
                helper.InfoLevelType.ERR, "Please, select the base location first")

    def handle_cte_usage(self):
        """
        Method for taking actions when CTF use checkbox is
        checked/un-checked
        """
        if self.use_cte_checkbox.isChecked():
            self.project_config.use_cte_checkbox = True
            self.cte_location_label.setEnabled(True)
            self.cte_cfg_label.setEnabled(True)
            self.cte_zip_lineedit.setEnabled(True)
            self.cte_location_pushbutton.setEnabled(True)
            self.cte_cfg_lineedit.setEnabled(True)
            self.cte_cfg_pushbutton.setEnabled(True)
            self.cte_exe_clear_button.setEnabled(True)
            self.cte_cfg_clear_button.setEnabled(True)
        else:
            self.project_config.use_cte_checkbox = False
            self.cte_location_label.setEnabled(False)
            self.cte_cfg_label.setEnabled(False)
            self.cte_zip_lineedit.setEnabled(False)
            self.cte_location_pushbutton.setEnabled(False)
            self.cte_cfg_lineedit.setEnabled(False)
            self.cte_cfg_pushbutton.setEnabled(False)
            self.cte_exe_clear_button.setEnabled(False)
            self.cte_cfg_clear_button.setEnabled(False)

    def report_path_saver(self):
        """
        This method saves report path set by the user and restricts user to select this
        path inside the base location.
        """
        if not self.edit_mode:
            base_path = self.project_config.base_path
        else:
            base_path = self.basepath_lineedit.text()
        if base_path:
            report_path = QtWidgets.QFileDialog.getExistingDirectory(
                QtWidgets.QFileDialog(), 'Select Report Path', base_path)
            if report_path:
                try:
                    self.project_config.report_path = report_path
                    self.report_lineedit.setText(self.project_config.report_path)
                    self.report_lineedit.setCursorPosition(0)
                except RuntimeError as error:
                    self.__display_exception(error)
        else:
            LOG.error("Please, select the base location first")
            ui_helper.pop_up_msg(
                helper.InfoLevelType.ERR, "Please, select the base location first")

    def additional_path_saver(self):
        """
        This method saves additional paths set by the user. They could be more than one in
        number
        """
        additional_paths = QtWidgets.QFileDialog.getExistingDirectory(
            QtWidgets.QFileDialog(), 'Select Additional Paths', directory=str(Path.home()))

        if additional_paths:
            self.project_config.additional_paths.append(additional_paths)
            self.additional_path_lineedit.insert(additional_paths)
            self.additional_path_lineedit.insert(";")

    @staticmethod
    def __display_exception(exception):
        """
        Displays an exception on the UI.

        :param Exception exception: The exception to display.
        """
        LOG.exception(exception)
        ui_helper.pop_up_msg(
            helper.InfoLevelType.ERR, str(exception))

    def update_config_values(self):
        """
        Will store the configuration entered by the user in the ui into the project configuration
        object.
        """
        self.project_config.base_path = self.basepath_lineedit.text()
        self.project_config.ptf_test_path = self.ptftests_lineedit.text()
        self.project_config.cmm_test_path = self.cmmtests_lineedit.text()
        self.project_config.canoe_cfg_path = self.canoe_cfg_linedit.text()
        self.project_config.cte_location = self.cte_zip_lineedit.text()
        self.project_config.cte_cfg = self.cte_cfg_lineedit.text()
        self.project_config.use_cte_checkbox = True if self.use_cte_checkbox.isChecked() else False
        self.project_config.report_path = self.report_lineedit.text()
        # removing spaces in-front of paths (if any)
        self.project_config.additional_paths = [
            path.strip() for path in self.additional_path_lineedit.text().split(";")]
        tests_for_cfg = ui_helper.TESTS_FOR_CFG
        # if push button text is not create then user open edit cfg window
        # in this case check if saved tests were removed by user or not and based on that update
        # 'tests_for_cfg' which then will be assigned to selected tests section of opened cfg
        # spaces are also kept in comparison of 'create' since its mentioned in config.ui file
        # for better button text display
        if self.save_pushbutton.text() != "  Create  ":
            tests_in_cfg = self.project_config.selected_tests
            tests_for_cfg["selected_tests"] = [
                test for test in tests_in_cfg["selected_tests"] if test not in self.tests_to_remove]
            # exclude cmm removed tests
            tests_for_cfg["cmm_tests"] = [
                test for test in tests_in_cfg["cmm_tests"] if test not in self.tests_to_remove]
            # exclude CANoe removed tests
            tests_for_cfg["capl_tests"] = [
                test for test in tests_in_cfg["capl_tests"] if test not in self.tests_to_remove]
            # clear this list for next time edit window action (if required)
            self.tests_to_remove.clear()
        # update tests to save
        self.project_config.selected_tests = tests_for_cfg
        self.project_config.num_loops = self.num_loops_spinbox.text()

    def save_config(self, file_path=""):
        """
        Method for saving a ConTest configuration based on previously set values.

        :param string file_path: path where file has to be saved. Default empty string
        """
        # update data to save and do some verification
        try:
            self.project_config.pre_save_verify_config()
            self.update_config_values()

            if file_path:
                path = file_path
            elif self.edit_mode:
                # path of loaded file
                path = self.cfg_file
            else:
                # opening a file to save
                path, _ = QtWidgets.QFileDialog.getSaveFileName(
                    QtWidgets.QFileDialog(), 'Save data in config file',
                    str(self.project_config.base_path), "config files (*.ini)"
                )

            # perform saving operations only if user entered a file name
            if path:
                self.project_config.save_config(path)
                if file_path:
                    return
                if self.edit_mode:
                    LOG.info("ConTest configuration %s saved successfully ...", path)
                    # pop up message
                    return_value = ui_helper.pop_up_msg(
                        helper.InfoLevelType.QUEST,
                        "Your ConTest configuration changes has been updated.\n"
                        "Do you want to reload your updated file?"
                    )
                    # close cfg dialog box
                    self.close()
                    if return_value:
                        LOG.info("-" * 100)
                        LOG.info("Reloading your config file %s", path)
                        # TODO Use a signal based approach here
                        self.controller_obj.load_configuration(path)
                else:
                    # pop up message
                    ui_helper.pop_up_msg(helper.InfoLevelType.INFO,
                                         "Your ConTest configuration has been saved")
                    LOG.info("ConTest configuration %s created successfully ...", path)
                    # creating sample test suite files if necessary
                    self.__create_pytest_files(self.project_config.ptf_test_path)
                    # close cfg dialog box
                    self.close()
        except (ValueError, RuntimeError, FileNotFoundError) as error:
            self.__display_exception(error)
            return

    def save_as_config(self):
        """
        Method for saving a copy of PTF configuration updated file.
        """
        # opening a file to save
        path, _filter = QtWidgets.QFileDialog.getSaveFileName(
            QtWidgets.QFileDialog(), 'Save as data in config file',
            str(self.project_config.base_path), "config files (*.ini)")
        if path:
            self.save_config(path)
            # pop up message
            ui_helper.pop_up_msg(
                helper.InfoLevelType.INFO,
                "Data saved in '{}'".format(path))
            LOG.info("ConTest configuration %s saved successfully ...", path)
            # close cfg dialog box
            self.close()

    def clear_ui(self):
        """
        This method clears all the fields in configurator dialog.
        """
        self.basepath_lineedit.clear()
        self.ptftests_lineedit.clear()
        self.cmmtests_lineedit.clear()
        self.canoe_cfg_linedit.clear()
        self.cte_zip_lineedit.clear()
        self.cte_cfg_lineedit.clear()
        self.report_lineedit.clear()
        self.use_cte_checkbox.setChecked(False)
        self.additional_path_lineedit.clear()

    def load_edit_cfg_ui(self):
        """
        Method for initializing the edit dialog box with available info
        """
        self.basepath_lineedit.insert(self.project_config.base_path)
        self.ptftests_lineedit.insert(self.project_config.ptf_test_path)
        self.cmmtests_lineedit.insert(self.project_config.cmm_test_path)
        self.canoe_cfg_linedit.insert(self.project_config.canoe_cfg_path)
        self.cte_zip_lineedit.insert(self.project_config.cte_location)
        self.cte_cfg_lineedit.insert(self.project_config.cte_cfg)
        self.report_lineedit.insert(self.project_config.report_path)
        if self.project_config.use_cte_checkbox == "True":
            self.use_cte_checkbox.setChecked(True)
        else:
            self.use_cte_checkbox.setChecked(False)
        if self.project_config.additional_paths:
            self.additional_path_lineedit.insert(
                ";".join(self.project_config.additional_paths) + ";")
        rowcount = 0
        all_tests_in_cfg = [tests_type_list for _, tests_type_list in
                            self.project_config.selected_tests.items() if len(tests_type_list) != 0]
        if any(list(itertools.chain.from_iterable(all_tests_in_cfg))):
            all_tests = list(itertools.chain.from_iterable(
                [tests for _, tests in self.project_config.selected_tests.items()]))
            self.selected_test_cases_model.setRowCount(len(all_tests))
            for sel_item in all_tests:
                item = QtGui.QStandardItem(sel_item)
                item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                self.selected_test_cases_model.setItem(rowcount, 0, item)
                rowcount += 1
            self.selected_filter_proxy_model.setSourceModel(self.selected_test_cases_model)
            self.select_tests_table_view.setModel(self.selected_filter_proxy_model)
        else:
            LOG.warning("No tests were saved in ConTest configuration file")

        self.num_loops_spinbox.setValue(self.project_config.num_loops)

    # pylint: disable=invalid-name
    def keyPressEvent(self, event):
        """
        Method for deleting the selected test case with key Delete and Backspace in edit config
        """
        if event.key() in (QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete):
            rows = self.select_tests_table_view.selectionModel().selectedRows()
            for i in rows:
                self.selected_test_cases_model.removeRow(i.row(), QtCore.QModelIndex())
