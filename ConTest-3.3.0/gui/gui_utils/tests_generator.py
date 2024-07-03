"""
    File for generating PTF test cases automatically from template
    Copyright 2019 Continental Corporation

    :file: test_generator.py
    :platform: Windows, Linux
    :synopsis:
        This file contains implementation for generating PTF specific test cases automatically.

    :author:
        - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
"""

# standard Python imports
import logging
import os
import csv
import re
import string
import subprocess
import platform
import collections
from pathlib import Path
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog
from gui.design_files.tests_generator import Ui_test_generator_dialog

# custom Python module imports
from data_handling import helper
from .. import ui_helper
from . import test_template

LOG = logging.getLogger("tests_generator")


# pylint: disable=too-few-public-methods
# public methods are not required at the moment
class TestGenerator(QDialog, Ui_test_generator_dialog):
    """
    Class for interacting with user for test generator form filling and generating test cases.
    """
    DELIMITER = ";"

    def __init__(self, main_ui):
        """
        Constructor

        :param object main_ui: Main GUI class 'UIController' object
        """
        # super initialization to access parent or base class method or data
        super().__init__()
        # assigning "TestGenerator" object to "setupUi" that is designer interface
        self.setupUi(self)
        # assigning argument(s) in to a variable
        self.main_ui_obj = main_ui
        # making UI connections
        self.__make_ui_connections()
        # test generator data
        self.generator_data = {
            "template_path": "",
            "csv_file_path": "",
            "test_case_file": ""
        }
        # set modal as true (i.e blocks background UI until dialog box execution completes)
        self.setModal(True)
        # setting up window icon
        self.setWindowIcon(QtGui.QIcon(os.path.abspath(os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '..', 'gui_images', 'logo_icon.png'))))
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

    def __make_ui_connections(self):
        """
        This method connects pyqt signals coming from test generator options to methods in this
        class
        """
        self.template_button.clicked.connect(self.__select_template)
        self.csv_file_button.clicked.connect(self.__select_csv_file)
        self.generate_csv_button.clicked.connect(self.__generate_csv)
        self.generate_tests_button.clicked.connect(self.__generate_ptf_tests)
        self.test_addition_checkbox.stateChanged.connect(self.__handle_test_addition)

    def __handle_test_addition(self):
        """
        Method for taking action based on test addition checkbox
        """
        if self.test_addition_checkbox.isChecked():
            self.num_of_tests_spinbox.setEnabled(True)
        else:
            self.num_of_tests_spinbox.setEnabled(False)

    def __select_template(self):
        """
        Method for handling selection of template file
        """
        # getting template file from user
        self.generator_data["template_path"], _ = QtWidgets.QFileDialog.getOpenFileName(
            QtWidgets.QFileDialog(), caption='Select ConTest Test Template (.tpl)',
            directory=str(Path.home()), filter='*.tpl')
        # checking if user has selected any template file or not
        if self.generator_data["template_path"] != '':
            self.template_line_edit.setText(self.generator_data["template_path"])

    def __select_csv_file(self):
        """
        Method for handling selection of CSV file
        """
        # getting csv file from user
        self.generator_data["csv_file_path"], _ = QtWidgets.QFileDialog.getOpenFileName(
            QtWidgets.QFileDialog(), caption='Select CSV file (Template Marker Filler)',
            directory=str(Path.home()), filter='*.csv')
        # checking if user has selected any csv file or not
        if self.generator_data["csv_file_path"] != '':
            self.csv_line_edit.setText(self.generator_data["csv_file_path"])

    def __check_delimiter(self):
        """
        Method to detect and raise error in-case machine's list separator character is not
        semi-colon in regional and language settings.

        This is required to align all csv files created via test generator utility.
        """
        if platform.system() == 'Windows':
            # running command to fetch list separator character on windows machine
            process = subprocess.Popen("powershell.exe (Get-Culture).TextInfo.ListSeparator",
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            output, error = process.communicate()
            if process.wait() != 0:
                self.__raise_error(
                    "powershell command to fetch list separater character"
                    " un-successfull.\nError: " + error)
            if TestGenerator.DELIMITER not in output.decode("utf-8"):
                err_str = \
                    "List Separator character is not {} on your machine.\nKindly " \
                    "change it to {}\n\nYou can change this by opening " \
                    "'Control Panel-->Clock, Language, and Region-->Region and " \
                    "Language-->Format-->Additional settings'".format(
                        TestGenerator.DELIMITER, TestGenerator.DELIMITER)
                self.__raise_error(err_str)
        elif platform.system() == 'Linux':
            # since there is no proper way to fetch list separator character in linux therefore
            # prompting user to check it manually
            info_str = \
                "Please make sure your separator option on your default CSV opener " \
                "application e.g. LibreOffice is selected as {} only. Since " \
                "generation and parsing of CSV is done with {} separator. " \
                "Otherwise errors might occur.".format(
                    TestGenerator.DELIMITER, TestGenerator.DELIMITER)
            ui_helper.pop_up_msg(helper.InfoLevelType.INFO, info_str)

    # disabling pylint issue since code is well documented
    # pylint: disable=too-many-branches
    def __generate_csv(self):
        """
        Method for taking action when user presses "Generate CSV" button

        Following are action points:
            1. check for relevant inputs (template file, csv file) and checks
            2. grab all markers from template file
            3. get csv file name for creation or get existing csv file name
            4. generate csv with markers name
            5. open csv for editing
        """
        # Step 1.
        # checking if user entered template file
        if not self.template_line_edit.text():
            self.__raise_error("Hey, you have not entered Template.\n")
        # checking if user entered or selecting csv file, if not then raise error
        if not self.csv_line_edit.text():
            self.__raise_error("Hey, you have not entered CSV file name.\n"
                               "Enter file name to be created or select an existing one.")
        # check if machine/pc line separator is semi-colon or not
        self.__check_delimiter()

        # Step 2.
        # reading ptf test template file and grabbing all markers inside it
        with open(self.generator_data["template_path"]) as template_file:
            line = ''.join(template_file.readlines())
            # using ordered dictionary to support Python 3.5
            marker_list = list(
                collections.OrderedDict().fromkeys(
                    re.findall(r'\${([A-Za-z0-9_]+)}', line, re.MULTILINE)))

        # Step 3.
        existing_csv_data = list()
        existing_tests = 0
        # if user selected an existing file
        if "\\" in self.csv_line_edit.text() or "/" in self.csv_line_edit.text():
            self.generator_data["csv_file_path"] = self.csv_line_edit.text()
            if not os.path.exists(self.csv_line_edit.text()):
                self.__raise_error("CSV file " + self.csv_line_edit.text() + " doesn't exist.")
            # opening the existing file to extract data
            with open(self.generator_data["csv_file_path"], 'r') as csv_file:
                # reading csv file data as list
                csv_data = list(csv.reader(csv_file))
                if csv_data:
                    # if data exists in csv file then grab markers
                    csv_markers = csv_data[0][0].split(TestGenerator.DELIMITER)[1:]
                    # checking if template and csv markers are matching
                    if set(marker_list) != set(csv_markers):
                        self.__raise_error(
                            "Markers in template file and csv file differs. Please select "
                            "correct template or csv file.\n\nTemplate Markers : "
                            + str(marker_list) + "\n\nCSV Markers : " + str(csv_markers))
                    # saving number of existing tests, subtracting 1 for excluding first marker line
                    existing_tests = len(csv_data) - 1
                    # adding existing markers data into list
                    for data in csv_data[1:]:
                        existing_csv_data.append(data[0].split(TestGenerator.DELIMITER))
        # if user enter name of csv file to be created
        else:
            # checking is user entered file name with correct extension, if not then raise error
            if not self.csv_line_edit.text().endswith(".csv"):
                self.__raise_error("Hey, you have not entered CSV file name with proper "
                                   "extension.\nUse proper extension e.g. marker_filler.csv")
            # asking for directory for storing new csv file
            directory = QtWidgets.QFileDialog.getExistingDirectory(
                QtWidgets.QFileDialog(), "Select CSV file creation directory",
                directory=str(self.generator_data["template_path"]))
            # if user cancelled the selection then don't need to do anything and return
            if not directory:
                return
            self.generator_data["csv_file_path"] = os.path.join(
                directory, self.csv_line_edit.text())
            self.csv_line_edit.setText(self.generator_data["csv_file_path"])

        # Step 4.
        if self.test_addition_checkbox.isChecked():
            marker_list.insert(
                0, "Tests=" + str(self.num_of_tests_spinbox.value() + existing_tests))
        else:
            marker_list.insert(
                0, "Tests=" + str(existing_tests))
        with open(self.generator_data["csv_file_path"], 'w') as csv_file:
            csv_writer = csv.writer(
                csv_file, delimiter=TestGenerator.DELIMITER, lineterminator='\n')
            csv_writer.writerow(marker_list)
            # writing existing data to csv (if available)
            for existing_data in existing_csv_data:
                csv_writer.writerow(existing_data)
            if self.test_addition_checkbox.isChecked():
                for test_index in range(self.num_of_tests_spinbox.value()):
                    csv_writer.writerow([existing_tests + test_index + 1])
        # throw info to user
        ui_helper.pop_up_msg(helper.InfoLevelType.INFO,
                             "Opening CSV file for editing.\n\n"
                             "- Fill markers with data\n"
                             "- Save data (don't change name of file)\n")

        # Step 5.
        #  open csv file for user to edit
        if platform.system() == 'Windows':
            # ignoring no-member pylint issue since it occurs only on linux
            # pylint: disable = useless-suppression, no-member
            os.startfile(self.generator_data["csv_file_path"])
        elif platform.system() == 'Linux':
            subprocess.call(('xdg-open', self.generator_data["csv_file_path"]))

    def __generate_ptf_tests(self):
        """
        Method for taking action when user presses "Generate Tests" button

        Following are action points:
            1. check for relevant inputs (template file, csv file, test script)
            2. get test script name for creation
            3. save template as string
            4. open csv, grab marker values, update final test string
            5. write updated test string with markers values in test script file
        """
        # Step 1.
        # checking if user entered template file
        if not self.template_line_edit.text():
            self.__raise_error("Hey, you have not entered Template.\n")
        # checking if user entered or selecting csv file, if not then raise error
        if not self.csv_line_edit.text():
            self.__raise_error("Hey, you have not entered CSV file name.\n"
                               "Enter file name to be created or select an existing one.")
        else:
            # checking is user entered file name with correct extension, if not then raise error
            if not self.csv_line_edit.text().endswith(".csv"):
                self.__raise_error("Hey, you have not entered CSV file name with proper "
                                   "extension.\nUse proper extension e.g. marker_filler.csv")
            # check if csv file exists
            if not os.path.exists(self.csv_line_edit.text()):
                self.__raise_error(
                    self.csv_line_edit.text() + " doesn't exist. Check if you created csv file.")
        # checking if user name of test script
        if not self.pytest_line_edit.text():
            self.__raise_error("Hey, you have not entered Test Script name.\n")

        # Step 2.
        # check if file exists if path was added earlier
        if "\\" in self.pytest_line_edit.text() or "/" in self.pytest_line_edit.text():
            if not os.path.exists(self.pytest_line_edit.text()):
                self.__raise_error(self.pytest_line_edit.text() + " doesn't exist.")
            # extracting test script name from path
            if "\\" in self.pytest_line_edit.text():
                test_file_name = self.pytest_line_edit.text().split("\\")[-1]
            elif "/" in self.pytest_line_edit.text():
                test_file_name = self.pytest_line_edit.text().split("/")[-1]
            self.generator_data["test_case_file"] = self.pytest_line_edit.text()
        else:
            test_file_name = self.pytest_line_edit.text()
            # asking for directory for storing new csv file
            directory = QtWidgets.QFileDialog.getExistingDirectory(
                QtWidgets.QFileDialog(), "Select Test Script creation directory",
                directory=str(self.generator_data["template_path"]))
            self.generator_data["test_case_file"] = os.path.join(
                directory, self.pytest_line_edit.text())
        # raise error if user selected test script with wrong naming
        if not test_file_name.endswith(".pytest") or not test_file_name.startswith("swt_"):
            self.__raise_error(
                "Hey, you have not named test script with proper naming convention.\n"
                "Use proper naming format e.g. swt_<meaningful_name>.pytest")
        # update name on line editor
        self.pytest_line_edit.setText(self.generator_data["test_case_file"])

        # Step 3.
        # opening template file and saving it's content to use later
        with open(self.generator_data["template_path"]) as template_file:
            template_str = ''.join(template_file.readlines())
            tpl_markers = [item[1] for item in string.Formatter().parse(template_str) if item[1]]
            tpl_markers = list(dict.fromkeys(tpl_markers))

        # Step 4.
        # generating test data by opening csv, grabbing marker values and
        # updating final test string
        final_data, num_of_tests = self.__prepare_test_data(template_str, tpl_markers)

        # Step 5.
        # dumping the final test generator string into test script
        with open(self.generator_data["test_case_file"], "w") as test_file:
            test_file.write(final_data)
        # throw info to user
        ui_helper.pop_up_msg(helper.InfoLevelType.INFO, str(num_of_tests)
                             + " Tests generated.\n\nLocation : "
                             + self.generator_data["test_case_file"])

    def __prepare_test_data(self, template_str, tpl_markers):
        """
        Method for preparing test data

        :param string template_str: Template data as sting
        :param list tpl_markers: List containing markers in template

        :return: Tuple containing final data and number of tests
        :rtype: tuple
        """
        # grabbing template as string template which makes the replacement of markers easy at later
        # stage
        template_data = string.Template(template_str)
        test_generator_str = test_template.PYTEST_STARTER
        # opening csv file, reading it's content and assigning values to template markers
        with open(self.generator_data["csv_file_path"], 'r') as csv_file:
            # reading csv file data as list
            csv_data_list = list(csv.reader(csv_file))
            # grabbing all marker names which are in first row of csv and starting from 2nd column
            test_marker_names = csv_data_list[0][0].split(TestGenerator.DELIMITER)[1:]
            # checking if user given csv and template files contains same markers
            if set(test_marker_names) != set(tpl_markers):
                self.__raise_error(
                    "Markers in template file and csv file differs. Please select correct template "
                    "or csv file.\n\nTemplate Markers : "
                    + str(tpl_markers) + "\n\nCSV Markers : " + str(test_marker_names))
            # now grabbing all rows in csv containing markers values
            # discarding 1st row since it contains marker names
            test_marker_values = csv_data_list[1:]
            # creating a dictionary with keys as marker names and assigning empty string as value
            # creating ordered dictionary to support Python 3.5
            marker_filler_dict = collections.OrderedDict()
            for marker in test_marker_names:
                marker_filler_dict[marker] = ""
            # loop for assigning values to marker names inside marker dictionary created above
            for marker_data in test_marker_values:
                # grabbing marker value in each element of marker value list
                # discarding 1st element since it's just a number
                marker_value = marker_data[0].split(TestGenerator.DELIMITER)[1:]
                # condition for handling with empty test case values
                if marker_value:
                    # now filling marker dictionary keys with respective values
                    for key, value in zip(marker_filler_dict.keys(), marker_value):
                        marker_filler_dict[key] = value
                else:
                    marker_filler_dict = dict.fromkeys(marker_filler_dict.keys(), "")
                # now replacing the markers with their values as captured above and then
                # concatenating into final test generator string to be dumped in test script later
                test_generator_str = \
                    test_generator_str + template_data.substitute(**marker_filler_dict)
                if not test_generator_str.endswith("\n\n"):
                    test_generator_str = test_generator_str + "\n\n"
            return test_generator_str, len(test_marker_values)

    @staticmethod
    def __raise_error(err):
        """
        Method for raising error as pop-up, on GUI message area and runtime exception

        :param string err: Error to be raised
        """
        ui_helper.pop_up_msg(helper.InfoLevelType.ERR, err)
        LOG.error(err)
        raise RuntimeError(err)

    def clear_ui(self):
        """
        This method clears all the fields in test generator dialog and resetting of values
        """
        # resetting all generator data to their initial value
        for key in self.generator_data:
            self.generator_data[key] = ""
        # clearing all line edit areas
        self.template_line_edit.clear()
        self.csv_line_edit.clear()
        self.pytest_line_edit.clear()
        # resetting spin box value and test addition checkbox
        self.num_of_tests_spinbox.setValue(self.num_of_tests_spinbox.minimum())
        self.test_addition_checkbox.setCheckState(QtCore.Qt.Unchecked)
