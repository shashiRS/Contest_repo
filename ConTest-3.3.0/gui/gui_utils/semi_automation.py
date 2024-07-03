"""
    Copyright 2021 Continental Corporation

    :file: semi_automation.py
    :platform: Windows, Linux
    :synopsis:
        This module contains the implementation to generate a pop up window for user to
        input text or values during semi automated test cases.

    :author:
        - Ganga Prabhakar G <Ganga.Prabhakar.Guntamukkala@continental-corporation.com>
"""

import os
from enum import Enum
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QDialog
from gui.design_files.manual_verification import Ui_manual_verification


class ManualVerifyReturns(Enum):
    """
    Return values in case of manual verification
    """
    YES = 'Yes'
    NO = 'No'


class SemiAutomation(QDialog, Ui_manual_verification):
    """
    Class for interacting with user for SemiAutomation instructions.
    """
    def __init__(self, main_ui):
        """
        Constructor
        """
        # super initialization to access parent or base class method or data
        super().__init__()
        # assigning "SemiAutomation" object to "setupUi" that is designer interface
        self.setupUi(self)
        # assigning argument(s) in to a variable
        self.main_ui_obj = main_ui
        # making UI connections
        self.__make_ui_connections()
        # declaring class variable user_text for accessing the data in global_params.py
        self.user_text = list()
        # set modal as true (i.e blocks background UI until dialog box execution completes)
        self.setModal(True)
        # setting up window icon
        self.setWindowIcon(QtGui.QIcon(os.path.abspath(os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '..', 'gui_images', 'logo_icon.png'))))
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

    def __make_ui_connections(self):
        """
        This method connects pyqt signals coming from semi_auto_input options
        to methods in this class
        """
        self.yes_button.clicked.connect(self.__yes_button_text)
        self.no_button.clicked.connect(self.__no_button_text)

    def __yes_button_text(self):
        """
        method to capture user input data upon clicking button_1
        """
        self.user_text.append(ManualVerifyReturns.YES.value)
        self.user_text.append(self.user_explanation.toPlainText())
        self.close()

    def __no_button_text(self):
        """
        method to capture user input data upon clicking button_2
        """
        self.user_text.append(ManualVerifyReturns.NO.value)
        self.user_text.append(self.user_explanation.toPlainText())
        self.close()
