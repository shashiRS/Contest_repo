"""
    File for displaying a table widget with test case parameter's information
    Copyright 2021 Continental Corporation

    :file: test_case_parameterized.py
    :platform: Windows, Linux
    :synopsis:
        This file contains table widget with test case parameter's information.

    :author:
        - <ravi.kumar.vanama@continental-corporation.com>
"""

# standard Python imports
import logging
import os
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog
from gui.design_files.test_case_parameterized_view import Ui_testcase_parameterized_widget
import inspect
# custom imports
from gui import ui_helper
from data_handling import helper

LOG = logging.getLogger("TC Parameter's View")


# pylint: disable=too-few-public-methods
# public methods are not required at the moment
class TestCaseParametersView(QDialog, Ui_testcase_parameterized_widget):
    """
    Class for displaying a pop up for showing information about test case parameter's view
    """
    # this variable used to check any invalid test case
    check_invalid_tc = False
    # used to store the object data as memory address and other is object name in string format
    store_object_data = list()
    store_object_name = list()
    # used to store the user added set index info
    store_user_set_index = dict()
    # store the latest values of the rows of columns modified by user which is used to show on GUI
    store_modified_param_set_data = dict()
    # dictionary contains the selected parameters with row index from GUI test case parameter window
    # which is used for test runner
    store_selected_param_set_data = dict()

    store_user_added_set_data = dict()
    error_info = "Error: Invalid Test case Written. Please check it! " \
                 "Number of test case parameter values must be equal to Number of test case " \
                 "arguments. "

    def __init__(self, gui_object, test_case_parameter_data):
        """
        Constructor

        :param object gui_object: Object of GUI which helps to communicate information (errors,
                                  warnings etc.) with GUI.
        :param object test_case_parameter_data: Object of test case data which contains
                                                test_case name, parameters and values.
                                                which is used to show on TestCaseParametersView.
        """
        # super initialization to access parent or base class method or data
        super().__init__()
        # assigning "test case parameters view" object to "setupUi" that is designer interface
        self.setupUi(self)
        self.gui_object = gui_object
        # making UI connections
        self.__make_ui_connections()
        # set modal as true (i.e blocks background UI until dialog box execution completes)
        self.setModal(True)
        self.setWindowIcon(QtGui.QIcon(os.path.abspath(os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '..', 'gui_images', 'logo_icon.png'))))
        # assigning the test case parameter and its values
        # very important to use dict() below in order to just do a copy of value not memory sharing
        self.tc_parameter_values = dict(test_case_parameter_data.test_case_parameters_values)
        # assigning the test case parameters names list
        self.tc_parameters = test_case_parameter_data.test_case_parameters
        # assigning the test case name
        self.tc_name = test_case_parameter_data.name
        # storing the test case parameter for test runner
        self.test_runner_parameters = dict()
        # storing the valid row index for select all purpose
        self.valid_row_index = list()
        self.user_set_index_Info = list()
        # adding the test case parameter information to view it
        self.__add_table_view()

        self.lbl_info.setText("<b>Tip:</b> After editing the values, Press the enter "
                              "button and select parameter sets")
        self.reset_pb.setToolTip("Resetting all parameter value fields to default values.")
        self.apply_pb.setToolTip("Applying for selected parameter sets for test runner.")
        self.pb_addrow.setToolTip("Adding new parameter set of row in the table widget.")

    def __make_ui_connections(self):
        """
        This method connects pyqt signals coming from test case parameter view options
        to methods in this class
        """
        self.reset_pb.clicked.connect(self.__reset_to_default_values)
        self.apply_pb.clicked.connect(self.__save_values)
        self.cb_select_all.clicked.connect(self.select_all_rows)
        self.table_widget_parameter_view.cellClicked.connect(self.update_select_all_check_box)
        self.pb_addrow.clicked.connect(self.__insert_row)

    def update_select_all_check_box(self):
        """
        This method is triggered when user clicked set of rows check box items
        """
        # Here it updates select all items, based on user check/uncheck set of rows with
        # check box items
        all_items_selected = True
        for row_index in self.valid_row_index:
            item = self.table_widget_parameter_view.item(row_index, 0)
            if item is not None and item .checkState() != QtCore.Qt.Checked:
                all_items_selected = False
        if all_items_selected:
            self.cb_select_all.setCheckState(QtCore.Qt.Checked)
        else:
            self.cb_select_all.setCheckState(QtCore.Qt.Unchecked)

    def select_all_rows(self):
        """
        This method is triggered when user clicked on the select all check box from GUI
        """
        # if select all check box is clicked checked all valid rows in table widget
        if self.cb_select_all.isChecked():
            for row in self.valid_row_index:
                item = self.table_widget_parameter_view.item(row, 0)
                item.setCheckState(QtCore.Qt.Checked)
        # else unchecked
        else:
            for row in self.valid_row_index:
                item = self.table_widget_parameter_view.item(row, 0)
                item.setCheckState(QtCore.Qt.Unchecked)

    def __save_values(self):
        """
        This method saves the values requested by user in GUI table view.
        Saved data is used for test runner
        """
        # storing the selected test parameters from GUI for test runner purpose
        store_row_index_test_runner = dict()
        # storing the selected test parameters from GUI to restore the data
        modified_test_parameter_values = list()
        # flag to check
        param_selected = False
        # From the number of rows with range check,  get the selected row index
        no_of_rows = self.table_widget_parameter_view.rowCount()
        for row_index in range(no_of_rows):
            # selected row is checked
            updated_row_data = dict()
            if self.table_widget_parameter_view.item(row_index, 0).checkState() == \
                    QtCore.Qt.Checked:
                param_selected = True
                # storing the data into dictionary.
                test_runner_param_value = dict()
                # storing the data into dictionary.
                modified_test_param_value = dict()
                # getting the column data base on row
                no_of_columns = self.table_widget_parameter_view.columnCount()
                for column in range(no_of_columns - 1):
                    item = self.table_widget_parameter_view.item(row_index, column + 1)
                    if item is not None and item.text() != '':
                        value = item.data(QtCore.Qt.DisplayRole)
                    # here checking string type to handle float and string type data
                    if isinstance(value, str):
                        check, val = self.is_float(value)
                        if check:
                            test_runner_param_value[self.tc_parameters[column]] = val
                            modified_test_param_value[self.tc_parameters[column]] = val
                        else:
                            test_runner_param_value[self.tc_parameters[column]] = value
                            modified_test_param_value[self.tc_parameters[column]] = value
                    else:
                        test_runner_param_value[self.tc_parameters[column]] = value
                        modified_test_param_value[self.tc_parameters[column]] = value
                # row is selected and its values might updated.
                updated_row_data[row_index] = modified_test_param_value
                modified_test_parameter_values.append(updated_row_data)
                # this is a special case to handle the object type data for test runner
                if self.store_object_data:
                    for object_item in self.store_object_data:
                        if row_index in object_item:
                            object_item_at_row_index = object_item[row_index]
                            for key in object_item_at_row_index.keys():
                                test_runner_param_value[key] = object_item_at_row_index[key]
                # dictionary contains key as selected row index and value as test_runner_param_value
                store_row_index_test_runner[row_index] = test_runner_param_value

        if modified_test_parameter_values:
            # assign the selected row data to retrieve when user opened the test case parameter
            # window
            self.store_modified_param_set_data[self.tc_name] = \
                modified_test_parameter_values
        else:
            if self.tc_name in self.store_modified_param_set_data:
                self.store_modified_param_set_data.pop(self.tc_name)

        self.store_selected_param_set_data[self.tc_name] = store_row_index_test_runner

        if self.tc_name in self.store_selected_param_set_data:
            # values = key_check[key] + value
            # Remove the test_name from the dict
            self.store_selected_param_set_data.pop(self.tc_name)
        # if test case values not empty then select the test case from tree view and
        # append the test case parameters and their values for test runner
        if store_row_index_test_runner:
            # emit the signal of test_case_parameters connected to a
            # self.test_runner_parameters slot.
            # add the selected parameterized tests for test runner
            self.store_selected_param_set_data[self.tc_name] = store_row_index_test_runner

            self.gui_object.emit_sig('parameterized_tc_from_gui', (True, self.tc_name))
        # else test case values are empty then un-select the test case from tree view
        else:
            self.gui_object.emit_sig('parameterized_tc_from_gui', (False, self.tc_name))

        # if no parameters are selected then pop up window appears with information
        if param_selected is False:
            ui_helper.pop_up_msg(helper.InfoLevelType.INFO,
                                 "Please select at least one set!")
        # close the window when parameters are selected and apply button is pressed.
        if param_selected:
            self.close()

    def __update_values(self):
        """
        This method update the values on GUI table view which modified by user previously
        """
        # check given test case name  exits or not
        if self.tc_name in self.store_modified_param_set_data:
            # get the previous stored data
            updated_row_data = self.store_modified_param_set_data[self.tc_name]
            # getting the list of rows information
            for item in updated_row_data:
                # getting the single row information data
                for row, values in item.items():
                    # first column is check box
                    item = self.table_widget_parameter_view.item(row, 0)
                    item.setCheckState(QtCore.Qt.Checked)
                    column = 0
                    # updating the other columns with modified data
                    for key, value in values.items():
                        column = column + 1
                        item = self.table_widget_parameter_view.item(row, column)
                        if isinstance(value, float):
                            # setting the item value in the data field for float with .9 decimals
                            value_str = "{:.9f}".format(value)
                            item.setData(QtCore.Qt.DisplayRole, value_str)
                        else:
                            item.setData(QtCore.Qt.DisplayRole, value)
                        # this is a special case to handle it for object type only to show on GUI
                        if self.store_object_name:
                            for object_name in self.store_object_name:
                                if row in object_name:
                                    object_name_at_row_index = object_name[row]
                                    if key in object_name_at_row_index.keys():
                                        item.setData(QtCore.Qt.DisplayRole,
                                                     object_name_at_row_index[key])
                        else:
                            item.setData(QtCore.Qt.DisplayRole, value)
        self.update_select_all_check_box()

    def __reset_to_default_values(self):
        """
        This method resets the GUI table view to default values.
        """
        # check given test case name exits or not
        # getting the dictionary of parameter set of rows information
        for row_index, value in self.tc_parameter_values.items():
            # tuple first parameter is bool 'True/False' is valid/invalid
            valid_data = value[0]
            # tuple second parameter as dictionary contains parameters and values
            parameter_value = value[1]
            if valid_data is True:
                for index, key in enumerate(self.tc_parameters):
                    value = parameter_value[key]
                    item = self.table_widget_parameter_view.item(row_index, index + 1)
                    if isinstance(value, float):
                        # setting the item value in the data field for float with .9 decimals
                        value_str = "{:.9f}".format(value)
                        item.setData(QtCore.Qt.DisplayRole, value_str)
                    else:
                        item.setData(QtCore.Qt.DisplayRole, value)
                    # this is a special case to handle it for object type only to show on GUI
                    if self.store_object_name:
                        for object_name in self.store_object_name:
                            if row_index in object_name:
                                object_name_at_row_index = object_name[row_index]
                                if key in object_name_at_row_index.keys():
                                    item.setData(QtCore.Qt.DisplayRole,
                                                 object_name_at_row_index[key])

    def __add_table_view(self):
        """
        Method to create a table view with test case parameter's values
        """
        # used to store the object data as memory address and other is object name in string format
        self.store_object_data.clear()
        self.store_object_name.clear()
        # check the test case parameter_values are empty or not
        if self.tc_parameter_values:
            # tc_parameters(columns) are greater than zero
            if len(list(self.tc_parameters)) > 0:
                # get the column count from test case parameters
                # here one is added for "SET" column purpose
                column_count = len(list(self.tc_parameters)) + 1

            # For empty columns at least one column required to show the error message
            else:
                column_count = 1
            # default values to show on the table view
            if self.tc_name in self.store_user_added_set_data:
                default_user_set = self.store_user_added_set_data[self.tc_name]
                for userItems in default_user_set:
                    for row_index, value in userItems.items():
                        if row_index in self.tc_parameter_values:
                            pass
                        else:
                            self.tc_parameter_values[row_index] = (True, value, True)
            # get the row count from tc_parameter_values which is tuple type
            row_count = len(self.tc_parameter_values)
            # setting the row and column count
            self.table_widget_parameter_view.setColumnCount(column_count)
            self.table_widget_parameter_view.setRowCount(row_count)
            # setting total row count
            self.le_total_sets.setText(str(row_count))
            self.table_widget_parameter_view.horizontalHeader().setFixedHeight(30)
            self.table_widget_parameter_view.horizontalHeader().setMinimumSectionSize(100)
            self.table_widget_parameter_view.horizontalHeader().setFrameStyle(
                QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)
            self.table_widget_parameter_view.horizontalHeader().setLineWidth(1)
            # setting the test case parameters for column header labels
            self.table_widget_parameter_view.setHorizontalHeaderLabels(
                ['set'] + list(self.tc_parameters))
            # setting the header with interactive mode
            self.table_widget_parameter_view.horizontalHeader().setSectionResizeMode(
                QtWidgets.QHeaderView.Interactive)
            # self.table_widget_parameter_view.horizontalHeader().setStyleSheet(
            #   "QHeaderView { font-size:  10pt};")
            # self.table_widget_parameter_view.horizontalHeader().setStyleSheet(
            # "::section {background-color : lightGray;font-size:10pt;}")
            self.table_widget_parameter_view.setSizeAdjustPolicy(
                QtWidgets.QAbstractScrollArea.AdjustToContents)
            # self.table_widget_parameter_view.resizeColumnsToContents()
            self.table_widget_parameter_view.horizontalHeader().setStretchLastSection(True)
            # self.table_widget_parameter_view.horizontalHeader().setSectionsMovable(True)
            self.lbl_tc_name.setText(str(self.tc_name))
            # get tc parameters and values from dictionary of tuple {key: (bool, dictionary, bool)}
            # tuple first parameter as bool True or False, Valid/Invalid
            # tuple second parameter as dictionary contains parameters and values
            # tuple third parameter as bool True or False. which is used in execution of param set
            # in test runner
            for row_index, value in self.tc_parameter_values.items():
                # tuple second parameter as dictionary contains parameters and values
                parameter_value = value[1]
                # tuple first parameter as bool valid or not
                valid_param_set = value[0]
                # parameter_value is dictionary type
                if valid_param_set:
                    self.check_invalid_tc = True
                    col = 1
                    # show the user added previous set row with row index as '*'
                    user_set_index = list()
                    if self.tc_name in self.store_user_set_index:
                        user_set_index = self.store_user_set_index[self.tc_name]

                    if row_index in user_set_index:
                        checkbox_item = QtWidgets.QTableWidgetItem(str(row_index) + "*")
                    else:
                        checkbox_item = QtWidgets.QTableWidgetItem(str(row_index))

                    checkbox_item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    checkbox_item.setCheckState(QtCore.Qt.Unchecked)
                    self.table_widget_parameter_view.setItem(
                        row_index, 0, QtWidgets.QTableWidgetItem(checkbox_item))
                    # store valid row index value
                    self.valid_row_index.append(row_index)
                    # from test case parameters get the value from parameter_value
                    for key in self.tc_parameters:
                        # check the test case parameters key in parameter_value exits or not
                        # if exits then get the value. other wise assign the value with None
                        item = QtWidgets.QTableWidgetItem()
                        item.setToolTip(str(parameter_value))
                        column_value = parameter_value[key]
                        item.setTextAlignment(QtCore.Qt.AlignHCenter)
                        # checking the data types of int, float, str, bool
                        if isinstance(column_value, (int, str, bool)):
                            # setting the item value in the data field
                            item.setData(QtCore.Qt.DisplayRole, column_value)
                        elif isinstance(column_value, float):
                            # setting the item value in the data field for float with .9 decimals
                            value_str = "{:.9f}".format(column_value)
                            item.setData(QtCore.Qt.DisplayRole, value_str)
                        # TODO
                        # Currently the below data types are read only.
                        # list, dict, tuple, set, bytes, bytearray, memoryview types are read only
                        elif isinstance(column_value, (list, dict, tuple, set, complex, bytes,
                                                       bytearray, memoryview)):
                            # set item flag to non-editable mode
                            item.setFlags(QtCore.Qt.ItemIsEnabled)
                            item.setData(QtCore.Qt.DisplayRole, str(column_value))
                            item.setBackground(QtGui.QColor(125, 125, 125))
                            self.store_object_name.append(
                                {row_index: {key: str(column_value)}})
                            self.store_object_data.append({row_index: {key: column_value}})
                        # check given type has a class or not
                        elif isinstance(column_value, column_value.__class__):
                            # set item flag to non-editable mode
                            item.setFlags(QtCore.Qt.ItemIsEnabled)
                            item.setBackground(QtGui.QColor(125, 125, 125))
                            # checking class method contains '__str__'
                            if inspect.ismethod(column_value.__str__):
                                # setting the item value in the data field
                                item.setData(QtCore.Qt.DisplayRole, column_value.__str__())
                                self.store_object_name.append(
                                    {row_index: {key: column_value.__str__()}})
                                self.store_object_data.append({row_index: {key: column_value}})
                            # checking function type or not outside of class
                            elif inspect.isfunction(column_value):
                                # setting the item value in the data field
                                LOG.info("Function Object Type: {}".format(column_value.__name__))
                                item.setData(QtCore.Qt.DisplayRole, "Function Object : "
                                             + column_value.__name__)
                                self.store_object_name.append({
                                    row_index: {key: "Function Object : " + column_value.__name__}})
                                self.store_object_data.append({row_index: {key: column_value}})
                            else:
                                item.setData(QtCore.Qt.DisplayRole, "Class Object : "
                                             + "".join(type(column_value).__name__))
                                LOG.error("Method '__str__' Not Exits Inside a Class: {}".format
                                          (type(column_value).__name__))
                                self.store_object_name.append(
                                    {row_index: {key: "Class Object : " + "".join(type(
                                        column_value).__name__)}})
                                self.store_object_data.append({row_index: {key: column_value}})
                        else:
                            LOG.error("Data Type: {} is invalid. Please check it!".format(
                                column_value))
                        # setting the item to table widget
                        self.table_widget_parameter_view.setItem(
                            row_index, col, QtWidgets.QTableWidgetItem(item))
                        col = col + 1
                # Invalid case error message to show on GUI table view rows
                else:
                    # check_box item is created to show on GUI row item
                    item_0 = QtWidgets.QTableWidgetItem(str(row_index))
                    item_0.setFlags(QtCore.Qt.NoItemFlags)
                    item_0.setBackground(QtGui.QColor(255, 0, 0, 100))
                    self.table_widget_parameter_view.setItem(row_index, 0,
                                                             QtWidgets.QTableWidgetItem(item_0))
                    item = QtWidgets.QTableWidgetItem()
                    item.setTextAlignment(QtCore.Qt.AlignVCenter)
                    item.setData(QtCore.Qt.DisplayRole, self.error_info)
                    # invalid parameter and values are disabled and display with red colour
                    item.setFlags(QtCore.Qt.NoItemFlags)
                    # setting the red colour with transparent
                    item.setBackground(QtGui.QColor(255, 0, 0, 100))
                    # test case parameters are greater than zero contains valid and invalid cases
                    if len(list(self.tc_parameters)) > 0:
                        # setting the span from which column position the error text to display
                        self.table_widget_parameter_view.setSpan(row_index, 1, 1, column_count)
                        # setting the error message from second column to show on table view
                        self.table_widget_parameter_view.setItem(row_index, 1,
                                                                 QtWidgets.QTableWidgetItem(item))
                    # Zero test case parameters are invalid cases
                    else:
                        # setting the error message from second column to show on table view
                        self.table_widget_parameter_view.setItem(row_index, 0,
                                                                 QtWidgets.QTableWidgetItem(item))
            # resizing columns to the text contents
            self.table_widget_parameter_view.resizeColumnsToContents()
            # disable if there is any invalid case.
            if self.check_invalid_tc is False:
                self.cb_select_all.setEnabled(False)
                self.reset_pb.setEnabled(False)
                self.apply_pb.setEnabled(False)
                self.pb_addrow.setEnabled(False)
            # update the table view with previous values which modified by user.
            self.__update_values()
            LOG.info("Loaded Test Case Parameters On Table View.")

    def __insert_row(self):
        """
        This method to insert the row on GUI table view
        """

        user_added_set_data = dict()
        # Here inserting the user set row index and first column as checkbox with '*'
        no_of_rows = self.table_widget_parameter_view.rowCount()
        no_of_columns = self.table_widget_parameter_view.columnCount()
        self.table_widget_parameter_view.insertRow(no_of_rows)
        checkbox_item = QtWidgets.QTableWidgetItem(str(no_of_rows) + "*")
        checkbox_item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        checkbox_item.setCheckState(QtCore.Qt.Unchecked)
        checkbox_item.setToolTip("Set is added by user")
        self.table_widget_parameter_view.setItem(
            no_of_rows, 0, QtWidgets.QTableWidgetItem(checkbox_item))
        # It stores the user set index Info and used to show on gui, when it is reopened
        if self.tc_name in self.store_user_set_index:
            user_set_index_info = self.store_user_set_index[self.tc_name]
            user_set_index_info.append(no_of_rows)
        else:
            self.store_user_set_index[self.tc_name] = [no_of_rows]
        # Here last row data column is used in the next row
        for col_index in range(no_of_columns - 1):
            item = self.table_widget_parameter_view.item(no_of_rows - 1, col_index + 1)
            if item is not None and item.text() != '':
                value = item.data(QtCore.Qt.DisplayRole)
                if isinstance(value, str):
                    check, val = self.is_float(value)
                    if check:
                        user_added_set_data[self.tc_parameters[col_index]] = val
                    else:
                        user_added_set_data[self.tc_parameters[col_index]] = value
                else:
                    user_added_set_data[self.tc_parameters[col_index]] = value
            self.table_widget_parameter_view.setItem(
                no_of_rows, col_index + 1, QtWidgets.QTableWidgetItem(item))
        # adding the user set data into store_user_added_set_data and will be used for further purpose.
        if self.tc_name in self.store_user_added_set_data:
            previous_added_user_set_info = self.store_user_added_set_data[self.tc_name]
            previous_added_user_set_info.append({no_of_rows: user_added_set_data})
            self.store_user_added_set_data[self.tc_name] = previous_added_user_set_info
        else:
            self.store_user_added_set_data[self.tc_name] = [{no_of_rows: user_added_set_data}]
        # Valid row index is appending to list.
        self.valid_row_index.append(no_of_rows)
        self.le_total_sets.setText(str(no_of_rows + 1))

    def after_reload_update_stored_test_parameter_values(self, test_data_dict):
        """
        This method is used to update all the test case parameters with default values.

        :param dict test_data_dict: Contains python tests extracted data.
        """
        # assign to local variable and update the data to store_modified_test_parameter_values
        copy_store_modified_param_set = dict(self.store_modified_param_set_data)
        self.store_modified_param_set_data.clear()
        self.store_selected_param_set_data.clear()
        for tc_name, param_values in copy_store_modified_param_set.items():
            test_data = test_data_dict[tc_name]
            updated_row_data = dict()
            # storing the default parameter values for test runner and to show on gui.
            default_test_parameter_values = list()
            # Merging the sets from scripts and user added sets to default.
            temp_store_user_script_sets = dict(test_data.test_case_parameters_values)
            if tc_name in self.store_user_added_set_data:
                user_added_set = self.store_user_added_set_data[tc_name]
                for value in user_added_set:
                    for index, data in value.items():
                        temp_store_user_script_sets.update({index: (True, data)})
            for row_index, value in temp_store_user_script_sets.items():
                # tuple first parameter is bool 'True/False' is valid/invalid
                valid_data = value[0]
                # tuple second parameter as dictionary contains parameters and values
                parameter_value = value[1]
                if valid_data is True:
                    if any(row_index in modified_test_data for modified_test_data in param_values):
                        # row is selected and its values might updated.
                        updated_row_data[row_index] = parameter_value
            # store the default parameter values which shall be used for test runner purpose.
            default_test_parameter_values.append(updated_row_data)
            self.store_modified_param_set_data[tc_name] = default_test_parameter_values
            self.store_selected_param_set_data[tc_name] = updated_row_data

    def get_selected_param_sets_for_test_runner(self):
        """
        Method returns the selected parameters with param set data used for test runner
        """
        return self.store_selected_param_set_data

    def reset_variables(self):
        """
        Method resets the variables to empty
        """
        # store the latest values of the rows of columns modified by user
        self.store_modified_param_set_data.clear()
        # list contains the selected parameters from GUI test case parameter window which is
        # used for test runner
        self.store_selected_param_set_data.clear()

    def update_selected_check_box(self, row, col):
        """
        Method for updating the checkbox for selection/deselection
        :param int row: QTableWidgetItem row index
        :param int col: QTableWidgetItem column index
        """
        if row >= 0 and col == 0:
            item = self.table_widget_parameter_view.item(row, col)
            if item.checkState() == QtCore.Qt.Unchecked:
                if row in self.check_set_row_index:
                    self.check_set_row_index.remove(row)
                    self.cb_select_all.setCheckState(QtCore.Qt.Unchecked)
            else:
                self.check_set_row_index.add(row)
                if len(self.check_set_row_index) == len(self.valid_row_index):
                    self.cb_select_all.setCheckState(QtCore.Qt.Checked)

        self.table_widget_parameter_view.cellClicked.connect(self.update_selected_check_box)

        # store/remove set row index when check/uncheck is done

    check_set_row_index = set()
    # storing the valid row index for select all purpose
    valid_row_index = set()

    def is_float(self, param_value):
        """
        Method to convert given float value in string format to float value
        """
        try:
            # this convert string to int or float
            # "23"->23
            # "456.6768600000"->456.67686
            val = float(param_value)
            return True, val
        except ValueError as exc:
            return False, 0
