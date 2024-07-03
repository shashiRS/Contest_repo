"""
    File for displaying a table widget containing short cuts information
    Copyright 2021 Continental Corporation

    :file: shortcut_information.py
    :platform: Windows, Linux
    :synopsis:
        This file contains table widget containing short cuts information.

    :author:
        - prathamesh.yawalkar@continental-corporation.com>
"""

# standard Python imports
import logging
import os
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog
from gui.design_files.shortcut_info import Ui_table_widget_dialog

# custom Python module imports
from gui.ui_helper import SHORT_CUTS

LOG = logging.getLogger("shortcut")


# pylint: disable=too-few-public-methods
# public methods are not required at the moment
class ShortCutsInfo(QDialog, Ui_table_widget_dialog):
    """
    Class for displaying a pop up for showing information about short cuts
    """

    def __init__(self):
        """
        Constructor
        """
        # super initialization to access parent or base class method or data
        super(ShortCutsInfo, self).__init__()
        # assigning "ShortCutsInfo" object to "setupUi" that is designer interface
        self.setupUi(self)
        # set modal as true (i.e blocks background UI until dialog box execution completes)
        self.setModal(True)
        self.setWindowIcon(QtGui.QIcon(os.path.abspath(os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '..', 'gui_images', 'logo_icon.png'))))
        self.add_table_widget()

        self.table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_widget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

    def add_table_widget(self):
        """
        Method to create a table having short cuts information
        """
        row_count = (len(SHORT_CUTS))
        column_count = (len(SHORT_CUTS[0]))
        self.table_widget.setColumnCount(column_count)
        self.table_widget.setRowCount(row_count)
        self.table_widget.setHorizontalHeaderLabels((list(SHORT_CUTS[0].keys())))
        self.table_widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        for row in range(row_count):
            for column in range(column_count):
                item = (list(SHORT_CUTS[row].values())[column])
                self.table_widget.setItem(row, column, QtWidgets.QTableWidgetItem(item))
