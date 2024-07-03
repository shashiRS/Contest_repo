"""
    Test file for ConTest execution in CIP pipeline script.
    Copyright 2020 Continental Corporation

    :file: cip_run_tests.py
    :platform: Unix, Windows
    :synopsis:
        This file verifies that the execution of ConTest can be triggered properly.

    :author:
        Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""
import os
import sys
import unittest

# Adding path of the modules used in ptf_asserts to system path for running the test externally
try:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
    sys.path.append(BASE_DIR)
    import cip_run
finally:
    pass


class TestCipRunnerScript(unittest.TestCase):
    """ Class for testing cip runner script """

    def test_parameter_generation_from_valid_config(self):
        """
        Ensures that the parameter generation works correctly from parsing different config files.
        Configuration files are expected to be valid.
        """
        for config_file, expected_output in [
            ["contest_valid_full",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each hil sil -n 2 -e D:\\demo1 D:\\demo2 D:\\demo3 --random "
             "--rest-port 5555 --timestamp off --reverse_selection"],
            ["contest_valid_no_baselocation",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each sil"],
            ["contest_valid_no_baselocation_no_filter",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest"],
            ["contest_valid_no_baselocation_no_setupfile",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--filter tag each sil"],
            ["contest_valid_no_baselocation_no_setupfile_no_filter",
             "-r auto -l {baseloc} -c {config} --report-dir {report}"],
            ["contest_valid_no_filter",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest"],
            ["contest_valid_no_setupfile",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--filter tag each sil"],
            ["contest_valid_no_setupfile_no_filter",
             "-r auto -l {baseloc} -c {config} --report-dir {report}"],
            ["contest_valid_no_loop",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each hil sil"],
            ["contest_valid_no_baselocation_no_loop",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each hil sil"],
            ["contest_valid_no_ext_loc",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each hil sil -n 2"],
            ["contest_valid_no_baselocation_no_ext_loc",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each hil sil -n 2"],
            ["contest_valid_no_random",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each hil sil -n 2 -e D:\\demo1 D:\\demo2 D:\\demo3"],
            ["contest_valid_no_baselocation_no_random",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each hil sil -n 2 -e D:\\demo1 D:\\demo2 D:\\demo3"],
            ["contest_valid_no_rest_port",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each hil sil -n 2 -e D:\\demo1 D:\\demo2 D:\\demo3 --random"],
            ["contest_valid_no_baselocation_no_rest_port",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each hil sil -n 2 -e D:\\demo1 D:\\demo2 D:\\demo3 --random"],
            ["contest_valid_no_time_stamp",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each hil sil -n 2 -e D:\\demo1 D:\\demo2 D:\\demo3 --random "
             "--rest-port 5555"],
            ["contest_valid_no_baselocation_no_time_stamp",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each hil sil -n 2 -e D:\\demo1 D:\\demo2 D:\\demo3 --random "
             "--rest-port 5555"],
            ["contest_valid_no_reverse_selection",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each hil sil -n 2 -e D:\\demo1 D:\\demo2 D:\\demo3 --random "
             "--rest-port 5555 --timestamp off"],
            ["contest_valid_no_baselocation_no_reverse_selection",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each hil sil -n 2 -e D:\\demo1 D:\\demo2 D:\\demo3 --random "
             "--rest-port 5555 --timestamp off"],
            ["contest_valid_no_loops_no_ext_loc_no_random",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each hil sil --rest-port 5555 --timestamp off "
             "--reverse_selection"],
            ["contest_valid_no_baselocation_no_loops_no_ext_loc_no_random",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each hil sil --rest-port 5555 --timestamp off "
             "--reverse_selection"],
            ["contest_valid_no_rest_port_no_time_stamp_no_reverse_selection",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each hil sil -n 2 -e D:\\demo1 D:\\demo2 D:\\demo3 --random"],
            ["contest_valid_no_baselocation_no_rest_port_no_time_stamp_no_reverse_selection",
             "-r auto -l {baseloc} -c {config} --report-dir {report} "
             "--setup-file setup.pytest --filter tag each hil sil -n 2 -e D:\\demo1 D:\\demo2 D:\\demo3 --random"],
        ]:

            with self.subTest(config_file):
                config_file_path = os.path.join(
                    SCRIPT_DIR, "configs", "{}.yml".format(config_file))

                ROOT_DIR = os.path.realpath(
                    os.path.join(SCRIPT_DIR, "..", ".."))

                # Base location in parameter depends if default is used or defined one in config
                if "no_baselocation" in config_file:
                    baseloc = ROOT_DIR
                else:
                    baseloc = os.path.join(ROOT_DIR, "tests", "integration")

                contest_ini = os.path.join(
                    ROOT_DIR, "conf", "contest_config.ini")

                # Build expected output string
                expected_output = expected_output.format(
                    baseloc=baseloc, config=contest_ini,
                    report=os.path.join("dummy_workspace", "conan_workarea", "contest_reports"))

                with open(config_file_path) as yaml_file:
                    self.assertEqual(
                        cip_run.parse_config(yaml_file, "dummy_workspace"),
                        expected_output, "Invalid parameters generated from configuration.")

    def test_parameter_generation_from_invalid_config(self):
        """
        Ensures that error handling for invalid configs works as expected
        """
        for config_file, expected_failure in [
            ["contest_invalid_no_config",
             "No 'config' tag given for stage 'each'."],
            ["contest_invalid_no_each_stage",
             "No config found for stage 'each'."],
            ["contest_invalid_no_stage",
             "'stage' not defined in config."],
        ]:
            with self.subTest(config_file):
                config_file_path = os.path.join(
                    SCRIPT_DIR, "configs", "{}.yml".format(config_file))

                with self.assertLogs("CIP Runner", "ERROR") as logger:
                    with open(config_file_path) as yaml_file:
                        try:
                            cip_run.parse_config(yaml_file, "dummy_workspace")
                            self.fail("This call should fail")
                        except SystemExit as exit_code:
                            self.assertNotEqual(
                                exit_code, 0, "Invalid exit code.")

                        self.assertIn(expected_failure, logger.output[0],
                                      "Unexpected error message.")


if __name__ == '__main__':
    unittest.main(verbosity=2)
