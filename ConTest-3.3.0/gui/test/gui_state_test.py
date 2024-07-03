"""
    File for Testing ConTest GUI states
    Copyright 2018 Continental Corporation

    :file: gui_state_controller.py
    :synopsis:
        This file contains unit test for testing ConTest GUI state-machine. This emits signals to
        check the state transition

    :author:
        Christopher Mirajkar <Christopher.Charles.Mirajkar@continental-corporation.com>
"""
import sys
from PyQt5 import QtWidgets
from ui_states import UIStates


class StateTest(UIStates):
    """ Class for testing the GUI states """
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # on start up of UI bring it to start up state
        self.unit_test_gui_initial_state()

        # switching to ptf_state when PTF checkbox is checked
        self.ptfcore_checkbox.stateChanged.connect(self.unit_test_gui_ptf_state)

        # switching to ptf_test_state when PBL button pressed
        # for testing purpose we assume that the tests are loaded successfully
        # self.base_loc_pushbutton.clicked.connect(self.unit_test_gui_ptf_test_state)

        # switching to ptf_runner_state when RUN button pressed
        self.runtest_pushbutton.clicked.connect(self.unit_test_gui_ptf_runner_state)

        # --------------FILE MENU ACTIONS-----------------
        self.actionReset.triggered.connect(self.unit_test_gui_initial_state)
        self.actionExit.triggered.connect(self.exit_gui)

    def unit_test_gui_initial_state(self):
        """
        This method is for testing GUI initial state
        """
        self.initial_state.emit()

    def unit_test_gui_ptf_state(self):
        """
        This method is for testing GUI ptf state
        """
        # When PTF check box unchecked bring back to start up state
        # This can be later changed for switching to TASIS mode
        if not self.ptfcore_checkbox.isChecked():
            self.initial_state.emit()
        else:
            self.ptf_state.emit()

    def unit_test_gui_ptf_test_state(self):
        """
        This method is for testing GUI ptf test state
        """
        self.ptf_test_state.emit()

    def unit_test_gui_ptf_runner_state(self):
        """
        This method is for testing GUI ptf runner state
        """
        self.ptf_runner_state.emit()

    @staticmethod
    def exit_gui():
        """ Method for exiting GUI"""
        QtWidgets.QApplication.quit()


# main function to start GUI
if __name__ == '__main__':
    APP = QtWidgets.QApplication(sys.argv)
    GUI_APP = StateTest()
    GUI_APP.show()
    APP.exec_()
