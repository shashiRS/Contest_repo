"""
    File for displaying latest release information on What's New Window
    Copyright 2022 Continental Corporation

    :file: what_new_window.py
    :platform: Windows, Linux
    :synopsis:
        This file contains latest release information on What's New Window

    :author:
        - <ravi.kumar.vanama@continental-corporation.com>

"""

# standard Python imports
import logging
import os
from PyQt5 import QtGui
from PyQt5.QtWidgets import QDialog
from gui.design_files.what_new_window import Ui_Dialog

# framework related imports
import global_vars
from gui import ui_helper


LOG = logging.getLogger("What New Window")


class WhatNewWindow(QDialog, Ui_Dialog):
    """
    Class for displaying a pop up window with latest release information
    """
    def __init__(self):
        """
        Constructor
        """
        # super initialization to access parent or base class method or data
        super(WhatNewWindow, self).__init__()
        # assigning "WhatNewWindow" object to "setupUi" that is designer interface
        self.setupUi(self)
        # set modal as true (i.e blocks background UI until dialog box execution completes)
        self.setModal(True)
        self.setWindowTitle("Feature List [Release {}]".format(global_vars.CONTEST_VERSION))
        self.donot_show_checked = True
        self.setWindowIcon(QtGui.QIcon(os.path.abspath(os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '..', 'gui_images', 'logo_icon.png'))))
        self.cb_dont_show.toggled.connect(lambda: self.donot_show(self.cb_dont_show))
        self.pb_close.clicked.connect(self.window_close)
        self.release_more_details.setOpenExternalLinks(True)
        self.update_latest_release_info()
        self.pt_info.moveCursor(QtGui.QTextCursor.Start)

    def update_latest_release_info(self):
        """
        Method to update latest release information to show on gui
        """
        self.pt_info.appendHtml(global_vars.RELEASE_MAIN_POINTS)
        self.release_more_details.setText(
            "For more details check <a href='{}'>Release Notes</a>".format(
                ui_helper.RELEASE_NOTES_HTD_LINK))

    def donot_show(self, check_object):
        """
        Method is checking that Don't show check is checked or not
        """
        if check_object.isChecked():
            self.donot_show_checked = False
        else:
            self.donot_show_checked = True

    def window_close(self):
        """
        Method to close What's New Window
        """
        self.close()
