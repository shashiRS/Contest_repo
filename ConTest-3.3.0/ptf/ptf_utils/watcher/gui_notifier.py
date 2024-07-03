"""
    Module for gui notifications.
    Copyright 2019 Continental Corporation

    This module contains a watcher to notify the ui on test status changes.

    :file: gui_notifier.py
    :author:
        - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""
from PyQt5.QtWidgets import QApplication

from ptf.ptf_utils.test_watcher import TestWatcher


class GuiNotifier(TestWatcher):
    """
    Watcher implementation that will notify the UI about test status updates.
    """

    def __init__(self, gui_obj=None):
        """
        Initializes the gui notifier

        :param object gui_obj: The gui object to send out the signal
        """
        self.gui_obj = gui_obj

    def test_run_started(self, test_cases):
        """
        Notifies the ui that a new test run has started.

        :param list test_cases: The list of testcases to be executed
        """
        test_case_names = list()
        for test_case in test_cases:
            # Here testcases contains list of lists [modified_test_name, wrapped_test, verifies_id, tags, test_type,
            # param_tests]
            # 5th position provides information related to parameterized test case of its param set test names which
            # is used to display on output window.
            if test_case[5]:
                for param_test in test_case[5]:
                    test_case_names.append(param_test)
            else:
                test_case_names.append(test_case[0])
        self.gui_obj.emit_sig('test_run_started', test_case_names)

    def test_started(self, testcase):
        """
        Notifies the ui that a new testcase started.

        :param TestCaseInfo testcase: The testcase that started
        """
        self.gui_obj.emit_sig('result', {"testcase_info_obj": testcase, "signal_info": "test_started"})

    def test_finished(self, testcase):
        """
        Notifies the ui that a testcase finished.

        :param TestCaseInfo testcase: The finished testcase.
        """
        # emitting signal to GUI with test's result data will be in form of dictionary
        # GUI thread to be displayed on GUI for the user/tester
        self.gui_obj.emit_sig('result', {"testcase_info_obj": testcase, "signal_info": "test_finished"})

    def test_run_finished(self, _):
        """
        Will notify the user that a testrun has finished. Flashes the taskbar icon on windows.
        """
        QApplication.alert(self.gui_obj, 0)
