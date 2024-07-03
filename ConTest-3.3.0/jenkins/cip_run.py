"""
    Main file for ConTest execution in CIP pipeline.
    Copyright 2020 Continental Corporation

    :file: cip_run.py
    :platform: Unix
    :synopsis:
        This file is triggered on execution of ConTest in the CI system. It parses the
        conf/contest.yml in the project and calls ConTest on command line accordingly.

    :author:
        Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""
import argparse
import logging
import os
import platform
import re
import subprocess
from subprocess import call
import sys

import yaml

LOG = logging.getLogger("CIP Runner")

# The currently executed stage needs later to be given by CI team
CURR_STAGE = "each"
# returning with 0 code as it's important to return with non-zero code if any error occurs
# as it will halt or break the pipeline progress and stages later than contest e.g. post-reporting
# will not run
CIP_RETURN_CODE = 0


def abort(msg, *args):
    """
    Aborts execution with a given msg. Msg will be passed to logging framework, so all logging
    related formatting options are allowed here.

    :param str msg: The msg to print
    :param Any args: The arguments to replace placeholders in msg.
    """
    if LOG.isEnabledFor(logging.ERROR):
        msg = msg % args
        LOG.error("%s Aborting.", msg)
    exit(CIP_RETURN_CODE)


def parse_args():
    """
    Will parse the cli arguments.

    :return: The parsed arguments
    :rtype: object
    """
    # create argument parser which is used then to parse
    parser = argparse.ArgumentParser(description="ConTest CI runner")
    parser.add_argument(
        '--log',
        help="The log level to use",
        type=str,
        required=False,
        default="INFO",
        dest='loglevel'
    )
    return parser.parse_args()


def initialize_logging(loglevel):
    """
    Initialize logging with given level.

    :param str loglevel: The log level to use for logging
    """
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        abort('Invalid log level: %s.', loglevel)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=numeric_level)


def cleanup_canoe():
    """
    Cleans up previous instances of canoe that might not have been properly cleaned up.
    """

    LOG.info("Close previously running instances of CANoe to make sure "
             "we get a responding executable")

    if platform.system() == 'Windows':
        exec_output = subprocess.getoutput('taskkill.exe /F /IM CANoe32.exe')
        LOG.info("Result: %s", exec_output)

        if not (bool(re.match("ERROR: The process \"CANoe32.exe\" not found.", exec_output))
                or bool(re.match("FEHLER: Der Prozess \"CANoe32.exe\" wurde nicht gefunden.",
                                 exec_output))
                or bool(re.match("SUCCESS: The process \"CANoe32.exe\" with PID .* has been"
                                 "terminated", exec_output))
                or bool(re.match("ERFOLGREICH: Der Prozess \"CANoe32.exe\" mit PID .* wurde"
                                 "beendet.", exec_output))):
            abort("--> Unexpected output of taskkill.")

        exec_output = subprocess.getoutput('taskkill.exe /F /IM CANoe64.exe')
        LOG.info("Result: %s", exec_output)

        if not (bool(re.match("ERROR: The process \"CANoe64.exe\" not found.", exec_output))
                or bool(re.match("FEHLER: Der Prozess \"CANoe64.exe\" wurde nicht gefunden.",
                                 exec_output))
                or bool(re.match("SUCCESS: The process \"CANoe64.exe\" with PID .* has been "
                                 "terminated", exec_output))
                or bool(re.match("ERFOLGREICH: Der Prozess \"CANoe64.exe\" mit PID .* wurde "
                                 "beendet.", exec_output))):
            abort("--> Unexpected output of taskkill.")


def parse_config(file, workspace):
    """
    Parses a given configuration file and generates the parameters out of the parsed data.

    :param TextIO file: The config file to parse.
    :param string workspace: Workspace location on jenkins machine
    :return: A parameter string to be used for execution with ConTest
    :rtype: str
    """
    LOG.info("Reading conf/contest.yml")

    config = yaml.safe_load(file)
    LOG.debug("Parsed config: %s", config)

    # Read out base location
    if not config or "replace_base_location" not in config:
        LOG.info("'replace_base_location' not defined in config."
                 "Fallback to github project root directory.")
        replace_base_location = "."
    else:
        replace_base_location = config["replace_base_location"]
    LOG.debug("Base location: %s", replace_base_location)

    # Read out configuration for our stage
    if not config or "stage" not in config:
        abort("'stage' not defined in config.")
    stages = config["stage"]

    if CURR_STAGE not in stages:
        abort("No config found for stage '%s'.", CURR_STAGE)

    # Get contest configuration for current stage
    if not stages[CURR_STAGE] or "config" not in stages[CURR_STAGE]:
        abort("No 'config' tag given for stage '%s'.", CURR_STAGE)
    contest_config = stages[CURR_STAGE]["config"]
    LOG.debug("ConTest config file: %s", contest_config)

    # Get setup file for current stage
    if "setup_file" in stages[CURR_STAGE]:
        setup_file = stages[CURR_STAGE]["setup_file"]
    else:
        setup_file = None
    LOG.debug("Setup file: %s", setup_file)

    # Adding fix report directory location
    # This location is important for CI reporting tool
    # CI reporting tool will look exactly in this location for reports
    # Change of this location might introduce some errors in reporting tool
    report_dir = os.path.join(workspace, "conan_workarea", "contest_reports")
    LOG.debug("Report directory: %s", report_dir)

    # Read out filters for current stage
    testcase_filter = []
    if "filter" in stages[CURR_STAGE]:
        testcase_filter = stages[CURR_STAGE]["filter"]
        for single_filter in testcase_filter:
            if "type" not in single_filter or "value" not in single_filter:
                abort("Please provide 'type' and 'value' for each filter."
                      "Provided values: '%s'.", single_filter)

            LOG.debug("Filter: '%s' - '%s'",
                      single_filter["type"], single_filter["value"])

    # no_of_loops will run the testcase multiple times based on number given
    no_of_loops = 0
    if "no_of_loops" in stages[CURR_STAGE]:
        no_of_loops = stages[CURR_STAGE]["no_of_loops"]

        LOG.debug("No of loops: %d", no_of_loops)

    # Enter locations which need to be added in sys.path for importing python modules
    ext_loc_list = []
    if "ext_loc" in stages[CURR_STAGE]:
        ext_loc = stages[CURR_STAGE]["ext_loc"]
        for single_ext_loc in ext_loc:
            ext_loc_list.append(single_ext_loc)

        LOG.debug(' '.join(map(str, ext_loc_list)))

    # If this flag is given, the tests will be executed in random order
    random = False
    if "random" in stages[CURR_STAGE]:
        random = stages[CURR_STAGE]["random"]

        LOG.debug("Random flag: %s", (bool(random)))

    # Start Contest with rest client. A Rest Client is provided with port number
    rest_port = None
    if "rest_port" in stages[CURR_STAGE]:
        rest_port = stages[CURR_STAGE]["rest_port"]

        LOG.debug("Rest Port: %d ", rest_port)

    # Timestamp (on or off) for logging. Default is 'on'
    time_stamp_status = "on"
    if "time_stamp" in stages[CURR_STAGE]:
        time_stamp_status = stages[CURR_STAGE]["time_stamp"]

        LOG.debug("Time stamp flag: %s", time_stamp_status)

    # Flag is set to True, unselected tests will be executed
    reverse_selection = False
    if "reverse_selection" in stages[CURR_STAGE]:
        reverse_selection = stages[CURR_STAGE]["reverse_selection"]

        LOG.debug("Reverse selection flag: %s", bool(reverse_selection))

    parameters = generate_parameters(
        replace_base_location,
        contest_config,
        setup_file,
        testcase_filter,
        report_dir,
        no_of_loops,
        ext_loc_list,
        random,
        rest_port,
        time_stamp_status,
        reverse_selection)

    LOG.debug("Command line parameters: '%s'", parameters)

    return parameters


def generate_parameters(
        base_location,
        contest_config,
        setup_file,
        testcase_filter,
        report_dir,
        no_of_loops,
        ext_loc_list,
        random,
        rest_port,
        time_stamp_status,
        reverse_selection):
    """
    Generates the parameter string for ConTest

    :param str base_location: The base location to use
    :param str contest_config: The contest config to use
    :param str setup_file: The setup file to use. Can be None.
    :param list testcase_filter: A list of testcase filters with type and value for each filter.
                            Can be an empty list.
    :param str report_dir: Directory where reports need to be generated
    :param int no_of_loops: The number of time testcase to be exected
    :param list ext_loc_list: The python modules locations which need to be added in sys.path
    :param bool random: The testcase to be executed in random fashion
    :param int rest_port: The Port number to be provided for Rest Client
    :param str time_stamp_status: Enable/Disable time stamp for logging,Default is 'on'
    :param bool reverse_selection: Unselected testcase are executed

    :return: The generated parameter string
    :rtype: str
    """

    # First the mandatory fields
    parameters = "-r auto -l {} -c {} --report-dir {}".format(
        os.path.realpath(base_location), os.path.realpath(contest_config), report_dir)

    # Optional setup file
    if setup_file:
        parameters = parameters + " --setup-file {}".format(setup_file)

    # Optional filter fields
    if testcase_filter:
        filter_tag = []
        # Create list of all tag
        for single_filter in testcase_filter:
            if single_filter["type"] not in filter_tag:
                filter_tag.append(single_filter["type"])
        filter_dict = {}
        # Create a Dict of tag with list of value
        for single_tag in filter_tag:
            filter_value = []
            for single_filter in testcase_filter:
                if single_tag == single_filter["type"]:
                    filter_value.append(single_filter["value"])
            filter_dict[single_tag] = filter_value
        # Create a string format of tag and value
        filter_string_format = ""
        for tag, value in filter_dict.items():
            temp_string_format = ' '.join(map(str, value))
            filter_string_format = tag + " " + temp_string_format
            # --filter string format with appended parameters
            parameters = parameters + " --filter {}".format(filter_string_format)

    # Optional no_of_loops fields
    if no_of_loops:
        parameters = parameters + " -n {}".format(no_of_loops)

    # Optional ext loc fields
    if ext_loc_list:
        ext_loc_format = ' '.join(map(str, ext_loc_list))
        parameters = parameters + " -e {}".format(ext_loc_format)

    # Optional random field
    if random:
        parameters = parameters + " --random"

    # Optional rest_port field
    if rest_port:
        parameters = parameters + " --rest-port {}".format(rest_port)

    # Optional time stamp field
    time_stamp_off = "off"
    if time_stamp_off.lower() == time_stamp_status.lower():
        parameters = parameters + " --timestamp off"

    # Optional Reverse selection testcase field
    if reverse_selection:
        parameters = parameters + " --reverse_selection"

    return parameters


def execute_contest(parameters):
    """
    Will run ConTest.

    :param parameters: The parameters to pass to ConTest
    """
    cmd = "{} {}/../main.py {}".format(sys.executable,
                                       os.path.dirname(__file__), parameters)
    LOG.info("Running ConTest with the command: '%s'", cmd)
    if call(cmd, shell=True) != 0:  # Exit code 0 means no errors
        abort("Error while executing ConTest. Please check log for details.")


def main():
    """
    Main function.
    Parses the configuration and then starts ConTest.
    """
    args = parse_args()
    loglevel = args.loglevel

    initialize_logging(loglevel)

    if "WORKSPACE" not in os.environ:
        abort("Please run this script in Jenkins environment only!")

    # Check for configuration availability
    if not os.path.exists('conf/contest.yml'):
        abort("Please provide a valid configuration in conf/contest.yml.")

    # Parse the config
    with open('conf/contest.yml') as yaml_file:
        parameters = parse_config(yaml_file, os.environ["WORKSPACE"])
        # Clean up canoe before contest execution
        cleanup_canoe()
        execute_contest(parameters)

    exit(CIP_RETURN_CODE)


if __name__ == "__main__":
    main()
