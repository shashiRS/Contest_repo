"""
    Copyright 2019 Continental Corporation

    :file: user_config_handler_test.py
    :platform: Windows, Linux
    :synopsis:
        Testcases for user config handler.

    :author:
        - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""
import os
import sys
import unittest

from PyQt5.QtCore import QStandardPaths

# Adding path of the modules used in ptf_asserts to system path for running the test externally
try:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..', '..'))
    sys.path.append(BASE_DIR)
    from gui.gui_utils import user_config_handler
    from gui.gui_utils.user_config_handler import UserConfigHandler
finally:
    pass

class TestUserConfigHandler(unittest.TestCase):
    """ Class for testing user config handler """

    @classmethod
    def setUpClass(cls):
        """
        Initialisation before all testcases.
        """
        # Don't mess up with the normal user configuration, use test paths instead
        QStandardPaths.enableTestMode(True)

    @classmethod
    def tearDownClass(cls):
        """
        Cleaning up after all testcases.
        """
        # Switch back to use the normal user configuration
        QStandardPaths.enableTestMode(False)

    def setUp(self):
        """
        Initialize clean user config for each test
        """
        self.userconfig = UserConfigHandler()
        self.userconfig.reset()

    def test_initial_configuration(self):
        """
        Verifies the initial configuration for each configuration attribute
        """

        for attribute, default_value in [
                ["darkmode", False],
                ["line_wrap", True],
                ["reopen_last_configuration", False],
                ["last_configurations", ()]
        ]:
            with self.subTest(attribute):
                self.assertEqual(getattr(self.userconfig, attribute), default_value,
                                 "Unexpected default value of {}".format(attribute))

    def test_reload_configuration(self):
        """
        Verifies that loading for each configuration attribute from persisted storage works fine.
        """

        for attribute, new_value in [
                ["darkmode", True],
                ["line_wrap", False],
                ["reopen_last_configuration", True],
                ["last_configurations", ("foo",)]
        ]:
            with self.subTest(attribute):
                setattr(self.userconfig, attribute, new_value)

                # Clean up userconfig and create a new object to make sure the data is persisted
                del self.userconfig
                self.userconfig = UserConfigHandler()
                self.assertEqual(getattr(self.userconfig, attribute), new_value,
                                 "{} not persisted".format(attribute))

    def test_consistency_over_multiple_instances(self):
        """
        Ensures that attributes are consistent over multiple instances of user config handler.
        """
        for attribute, old_value, new_value in [
                ["darkmode", False, True],
                ["line_wrap", True, False],
                ["reopen_last_configuration", False, True],
                ["last_configurations", ("foo",), ("bar", "baz")]
        ]:
            with self.subTest(attribute):
                setattr(self.userconfig, attribute, old_value)

                second_userconfig = UserConfigHandler()
                self.assertEqual(getattr(second_userconfig, attribute), old_value,
                                 "Invalid setting for {} after loading from file".format(attribute))

                setattr(self.userconfig, attribute, new_value)
                self.assertEqual(getattr(second_userconfig, attribute), new_value,
                                 "Invalid setting for {} after setting it in other instance"
                                 .format(attribute))

    def test_add_configuration_empty(self):
        """
        Ensures that adding a new configuration to an empty configuration works fine
        """
        self.assertEqual((), self.userconfig.last_configurations,
                         "Last opened configurations not empty")

        self.userconfig.add_configuration("foo")
        self.assertEqual(("foo",), self.userconfig.last_configurations,
                         "Did not add new configuration 'foo'")

    def test_add_configuration_limit(self):
        """
        Ensures that adding new configurations is limited to configured limit.
        """
        for counter in range(user_config_handler.MOST_RECENT_CONFIGURATIONS_COUNT):
            self.userconfig.add_configuration("foo{}".format(str(counter)))

        self.assertEqual(user_config_handler.MOST_RECENT_CONFIGURATIONS_COUNT,
                         len(self.userconfig.last_configurations),
                         "Did not fully fill up the last configuration list")

        self.userconfig.add_configuration("Foo")
        self.assertEqual(user_config_handler.MOST_RECENT_CONFIGURATIONS_COUNT,
                         len(self.userconfig.last_configurations),
                         "Did not truncate the last configuration list")
        self.assertEqual("Foo", self.userconfig.last_configurations[-1],
                         "Removed elements from end of list instead of beginning")

    def test_set_configuration_limit(self):
        """
        Ensures that the limit is also not exceeded if a really long list is added
        """
        configurations = []
        for counter in range(user_config_handler.MOST_RECENT_CONFIGURATIONS_COUNT + 1):
            configurations.append("foo{}".format(str(counter)))

        self.userconfig.last_configurations = configurations

        self.assertEqual(user_config_handler.MOST_RECENT_CONFIGURATIONS_COUNT,
                         len(self.userconfig.last_configurations),
                         "Did not truncate the last configuration list")
        self.assertEqual("foo{}".format(user_config_handler.MOST_RECENT_CONFIGURATIONS_COUNT),
                         self.userconfig.last_configurations[-1],
                         "Removed elements from end of list instead of beginning")

    def test_add_same_configuration_multiple_times(self):
        """
        Tests if adding the same configuration multiple times results in only one entry per
        configuration. The latest added configuration should be at the end of the list.
        """
        # Try to add the same entry twice
        self.userconfig.add_configuration("foo")
        self.userconfig.add_configuration("foo")
        self.assertEqual(1, len(self.userconfig.last_configurations),
                         "Configuration added multiple times")

        # Now add a different entry
        self.userconfig.add_configuration("bar")
        self.assertEqual(('foo', 'bar'), self.userconfig.last_configurations,
                         "Unexpected user config list")

        # Now add 'foo' again. The entries should switch the order
        self.userconfig.add_configuration("foo")
        self.assertEqual(('bar', 'foo'), self.userconfig.last_configurations,
                         "Unexpected user config list")


if __name__ == '__main__':
    unittest.main(verbosity=2)
