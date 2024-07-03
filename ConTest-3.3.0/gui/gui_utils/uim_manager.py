"""
    Copyright Continental Corporation and subsidiaries. All rights reserved.

    :platform: Windows, Linux

    :synopsis:
        ConTest Utility Install Manager (UIM) GUI implementation script
"""

# disabling import error as they are installed at start of framework
# pylint: disable=import-error, no-name-in-module
import os
import logging
from enum import Enum
import webbrowser
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QTableWidgetItem, QComboBox, QCheckBox, QPushButton, QDialog
from gui.design_files.uim import Ui_uim_main
from gui import ui_helper
from uim.uim import install_package_version, get_pip_show, CONNECTION_ERR
from data_handling import helper

LOG = logging.getLogger("UIM_UI")


class UimTableColumns(Enum):
    """
    Enum class containing QTableWidget column names and their column index values
    """

    SELECT = 0
    CONTEST_PACKAGES = 1
    AVAILABLE_VERSIONS = 2
    INSTALLED_VERSION = 3
    DOC = 4
    INSTALL_STATUS = 5
    INFO = 6
    ERROR = 7


class UimGui(QDialog, Ui_uim_main):
    """
    Utility Install Manager (UIM) GUI implementation class
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.setupUi(self)
        self.__make_ui_connections()
        self.column_headers = [col.name for col in UimTableColumns]
        self.uim_table_widget.setColumnCount(len(self.column_headers))
        self.uim_table_widget.setHorizontalHeaderLabels(self.column_headers)
        self.data = {}
        self.setModal(True)
        self.setWindowIcon(
            QtGui.QIcon(
                os.path.abspath(
                    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "gui_images", "logo_icon.png")
                )
            )
        )
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.install_pkg_thread = InstallPackagesThread(self)
        self.pkgs_to_install = {}
        self.data_ready = False
        self.libs_to_update = []

    def __make_ui_connections(self):
        """
        Method for making UI items connections
        """
        self.install_selected_button.clicked.connect(self.__install_selected)
        self.install_all_latest_button.clicked.connect(self.__install_all_latest)
        self.select_all_utils_checkbox.stateChanged.connect(self.__toggle_select_all)

    def __install_selected(self):
        """
        Method to be executed when user pressed install selected items button
        """
        self.install_pkg_thread.install_latest = False
        self.install_pkg_thread.start()

    def __install_all_latest(self):
        """
        Method to be executed when user pressed install all available items button
        """
        self.select_all_utils_checkbox.setChecked(True)
        self.install_pkg_thread.install_latest = True
        self.install_pkg_thread.start()

    def __toggle_select_all(self, state):
        """
        Method to be executed when user change state of "select all" checkbox

        :param int state: "select all" checkbox state
        """
        for row in range(self.uim_table_widget.rowCount()):
            checkbox_item = self.uim_table_widget.cellWidget(row, 0)
            if checkbox_item:
                checkbox_item.setCheckState(state)

    def __inform_users_about_pkgs_updates(self):
        """
        Method to inform users about new versions installations
        """
        pkgs_to_update = [pkg for pkg, data in self.data.items() if data["to_update"]]
        if pkgs_to_update:
            for pkg in pkgs_to_update:
                self.data[pkg]["versions_cell_item"].setStyleSheet("QComboBox {background-color: #3399ff;}")
            msg = (
                f"New version of the following ConTest tool libraries are available for installation via UIM."
                f"\n\n{pkgs_to_update}\n\nDo you like to open UIM for installations?"
            )
            ret = ui_helper.pop_up_msg(helper.InfoLevelType.QUEST, msg_str=msg)
            if ret:
                self.init_state()

    def row_selector(self, row):
        """
        Method to select or deselect a package for installation process. Connected to checkbox item of each package row

        :param int row: Row number of selected/un-selected package row
        """
        row_checkbox = self.uim_table_widget.cellWidget(row, UimTableColumns.SELECT.value)
        package_name = self.uim_table_widget.item(row, UimTableColumns.CONTEST_PACKAGES.value).text()
        if row_checkbox.checkState() == QtCore.Qt.Checked:
            self.data[package_name]["install"] = True
            self.pkgs_to_install[package_name] = self.data[package_name]
        else:
            self.data[package_name]["install"] = False
            del self.pkgs_to_install[package_name]

    def installer_in_progress_sig(self, pkg_data):
        """
        Method connected to `InstallPackagesThread` class `in_progress_sig` signal

        :param dict pkg_data: Dictionary containing contest packages data
        """
        pkg_name = pkg_data["pkg_name"]
        pkg_version = pkg_data["pkg_version"]
        self.pkgs_to_install[pkg_name]["status_cell_item"].setText("In-Progress")
        self.pkgs_to_install[pkg_name]["status_cell_item"].setBackground(QtGui.QColor(240, 230, 125))
        self.pkgs_to_install[pkg_name]["error_cell_item"].setText("")
        info_str = f"Installing package '{pkg_name}=={pkg_version}'"
        LOG.info(info_str)
        self.uim_status_label.setText(info_str)

    def installer_error_sig(self, pkg_data):
        """
        Method connected to `InstallPackagesThread` class `error_sig` signal

        :param dict pkg_data: Dictionary containing contest packages data
        """
        pkg_name = pkg_data["pkg_name"]
        pkg_err = pkg_data["pkg_err"]
        self.pkgs_to_install[pkg_name]["status_cell_item"].setText("Install Error")
        self.pkgs_to_install[pkg_name]["error_cell_item"].setDisabled(False)
        self.data[pkg_name]["error"] = pkg_err
        self.pkgs_to_install[pkg_name]["error_cell_item"].setText("View Error")
        self.pkgs_to_install[pkg_name]["local_version_cell_item"].setText("Not Available")
        self.pkgs_to_install[pkg_name]["status_cell_item"].setBackground(QtGui.QColor(235, 153, 113))

    def installer_success_sig(self, pkg_data):
        """
        Method connected to `InstallPackagesThread` class `success_sig` signal

        :param dict pkg_data: Dictionary containing contest packages data
        """
        pkg_name = pkg_data["pkg_name"]
        pkg_version = pkg_data["pkg_version"]
        self.pkgs_to_install[pkg_name]["info_cell_item"].setDisabled(False)
        self.pkgs_to_install[pkg_name]["status_cell_item"].setText("Success")
        self.pkgs_to_install[pkg_name]["local_version_cell_item"].setText(pkg_version)
        self.pkgs_to_install[pkg_name]["status_cell_item"].setBackground(QtGui.QColor(0, 204, 102))

    # pylint: disable=too-many-locals, too-many-statements
    def add_to_table(self, data):
        """
        Method to add data to QTableWidget

        :param dict data: Dictionary containing contest packages data
        """
        rows = len(data)
        self.uim_table_widget.setRowCount(rows)
        for row, (row_key, row_data) in enumerate(data.items()):
            self.data[row_key] = row_data
            self.data[row_key]["row"] = row
            self.data[row_key]["install"] = False
            self.data[row_key]["status_cell_item"] = None
            self.data[row_key]["error_cell_item"] = None
            self.data[row_key]["info_cell_item"] = None
            self.data[row_key]["versions_cell_item"] = None
            self.data[row_key]["local_version_cell_item"] = None
            for col, col_key in enumerate(self.column_headers):
                if col_key == UimTableColumns.SELECT.name:
                    check_box = QCheckBox()
                    check_box.stateChanged.connect(lambda _, r=row: self.row_selector(r))
                    self.uim_table_widget.setCellWidget(row, col, check_box)
                elif col_key == UimTableColumns.CONTEST_PACKAGES.name:
                    self.uim_table_widget.setItem(row, col, QTableWidgetItem(row_key))
                elif col_key == UimTableColumns.AVAILABLE_VERSIONS.name:
                    versions = row_data.get("all_versions", [])
                    versions.sort(reverse=True)  # Sort versions in reverse (most recent first)
                    combo_box = QComboBox()
                    self.data[row_key]["versions_cell_item"] = combo_box
                    combo_box.addItems(versions)
                    self.uim_table_widget.setCellWidget(row, col, combo_box)  # all_versions column combobox
                elif col_key == UimTableColumns.INSTALLED_VERSION.name:
                    local_version = row_data.get("local_version", None)
                    local_version_item = QTableWidgetItem(local_version)
                    self.data[row_key]["local_version_cell_item"] = local_version_item
                    self.uim_table_widget.setItem(row, col, local_version_item)
                elif col_key == UimTableColumns.INSTALL_STATUS.name:
                    status_item = QTableWidgetItem("")
                    self.data[row_key]["status_cell_item"] = status_item
                    self.uim_table_widget.setItem(row, col, status_item)
                elif col_key == UimTableColumns.INFO.name:
                    info_button = QPushButton("View Info")
                    self.data[row_key]["info_cell_item"] = info_button
                    info_button.setDisabled(True)
                    info_button.clicked.connect(lambda _, r=row: self.view_info(r))
                    self.uim_table_widget.setCellWidget(row, col, info_button)
                elif col_key == UimTableColumns.DOC.name:
                    doc_button = QPushButton("Open Doc")
                    doc_button.setDisabled(False)
                    doc_button.clicked.connect(self.view_doc)
                    self.uim_table_widget.setCellWidget(row, col, doc_button)
                elif col_key == UimTableColumns.ERROR.name:
                    err = row_data.get("error", None)
                    if err:
                        err_view_button = QPushButton("Version Error")
                        err_view_button.setDisabled(False)
                    else:
                        err_view_button = QPushButton("View Error")
                        err_view_button.setDisabled(True)
                    self.data[row_key]["error_cell_item"] = err_view_button
                    err_view_button.clicked.connect(lambda _, r=row: self.view_error(r))
                    self.uim_table_widget.setCellWidget(row, col, err_view_button)
        self.uim_table_widget.resizeColumnsToContents()

    def view_error(self, row):
        """
        Method connected to view error button

        :param int row: Row number of package having error in installation
        """
        err_item = self.uim_table_widget.cellWidget(row, UimTableColumns.ERROR.value)
        package_name = self.uim_table_widget.item(row, UimTableColumns.CONTEST_PACKAGES.value).text()
        if err_item.text():
            ui_helper.pop_up_msg(helper.InfoLevelType.ERR, msg_str=self.data[package_name]["error"])

    def view_info(self, row):
        """
        Method connected to view info button

        :param int row: Row number of package whose information is requested
        """
        result = get_pip_show(self.uim_table_widget.item(row, UimTableColumns.CONTEST_PACKAGES.value).text())
        if result["pip_show_err"]:
            ui_helper.pop_up_msg(helper.InfoLevelType.ERR, msg_str=result["pip_show_err"])
        else:
            ui_helper.pop_up_msg(helper.InfoLevelType.INFO, msg_str=result["pip_show_stdout"])

    def view_doc(self):
        """
        Method connected to view documentation button
        """
        ui_helper.pop_up_msg(
            helper.InfoLevelType.INFO,
            msg_str="Opening Tool APIs Link.\n"
            "Please navigate to the intended Tool on the webpage.\n\n"
            "The navigation to the intended tool will be improved in future.",
        )
        webbrowser.open(ui_helper.TOOL_APIS_LINK)

    def init_state(self):
        """
        Method to bring UIM UI to initialization state.
        """
        self.libs_to_update.clear()
        if not self.data_ready:
            self.main_widget.setDisabled(True)
        self.select_all_utils_checkbox.setCheckState(QtCore.Qt.Unchecked)
        self.uim_status_label.setText("UIM is fetching data from artifactory. Please wait ...")
        self.show()

    def ready_state(self):
        """
        Method to bring UIM UI to ready state. Connected to "UimInfoThread" class "ready_state" signal
        """
        self.data_ready = True
        self.main_widget.setDisabled(False)
        self.__inform_users_about_pkgs_updates()
        self.uim_status_label.setText("Please check data below")

    @staticmethod
    def report_network_error():
        """
        Method to show error pop-up when user is not on Continental network. Connected to "UimInfoThread" class
        "network_error" signal
        """
        ui_helper.pop_up_msg(helper.InfoLevelType.ERR, msg_str=CONNECTION_ERR)

    @staticmethod
    def report_general_error(msg):
        """
        Method to show general pop-up when user is not on Continental network. Connected to "UimInfoThread" class
        "general_error" signal

        :param string msg: Error message to be shown in pop-up
        """
        ui_helper.pop_up_msg(helper.InfoLevelType.ERR, msg_str=msg)

    def add_data(self, data):
        """
        Method to trigger adding data method in UIM UI. Connected to "UimInfoThread" class "add_data" signal

        :param dict data: Dictionary containing contest packages data
        """
        self.uim_status_label.setText("UIM is fetching data from artifactory. Please wait ...")
        self.add_to_table(data)


# public methods are not required at the moment
# pylint: disable=too-few-public-methods
class InstallPackagesThread(QtCore.QThread):
    """
    QThread class for running UIM (Utility Install Manager) install action
    """

    in_progress_sig = QtCore.pyqtSignal(dict)
    error_sig = QtCore.pyqtSignal(dict)
    success_sig = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        """
        Constructor

        :param object parent: UimGui class object
        """
        super().__init__(parent)
        self.install_latest = False
        self.in_progress_sig.connect(self.parent().installer_in_progress_sig)
        self.error_sig.connect(self.parent().installer_error_sig)
        self.success_sig.connect(self.parent().installer_success_sig)

    def run(self):
        """
        Method to run packages installation action in a QThread
        """
        self.parent().uim_status_label.setText("UIM is installing packages. Please wait ...")
        self.parent().main_widget.setDisabled(True)
        if len(self.parent().pkgs_to_install.keys()) == 0:
            self.parent().uim_status_label.setText("No packages selected. Please select at-least one package ...")
        else:
            for pkg in self.parent().pkgs_to_install:
                if self.install_latest:
                    self.parent().pkgs_to_install[pkg]["versions_cell_item"].setCurrentText(
                        self.parent().pkgs_to_install[pkg]["latest_version"]
                    )
                package_version = (
                    self.parent()
                    .uim_table_widget.cellWidget(
                        self.parent().pkgs_to_install[pkg]["row"], UimTableColumns.AVAILABLE_VERSIONS.value
                    )
                    .currentText()
                )
                self.in_progress_sig.emit({"pkg_name": pkg, "pkg_version": package_version})
                result = install_package_version(pkg, package_version)
                if not result["install_result"]:
                    self.error_sig.emit({"pkg_name": pkg, "pkg_err": result["install_err"]})
                else:
                    self.success_sig.emit({"pkg_name": pkg, "pkg_version": package_version})
            self.parent().uim_status_label.setText("UIM installation action finished. Please check results")
        self.parent().main_widget.setDisabled(False)
