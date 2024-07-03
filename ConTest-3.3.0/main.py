"""
    Main file for ConTest Framework.
    Copyright 2018 Continental Corporation

    :file: main.py
    :platform: Windows, Linux
    :synopsis:
        Main script

    :author:
        - Christopher Mirajkar <Christopher.Charles.Mirajkar@continental-corporation.com>
        - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""

# standard Python modules imports
import logging
import logging.config
import argparse
import os
import platform
import sys
import itertools
import socket
import subprocess
from threading import Thread

# custom imports
import global_vars


MAIN_FILE_PATH = os.path.dirname(os.path.realpath(__file__))
# Create a logger to be used in this file.
LOG = logging.getLogger("MAIN")

MODULES_LIST = [
    "numpy",
    "PyQt5.QtCore",
    "lxml",
    "qdarkstyle",
    "pandas",
    "psutil",
    "tornado",
    "yaml",
    "requests",
    "tabulate",
    "contest_verify",
    "jinja2",
    "yaml",
]

PLATFORM_TYPE = platform.system()

# setting terminal symbol based on platform
if PLATFORM_TYPE == "Linux":
    TERMINAL_SYMBOL = "$"
    MODULE_INSTALL_FILE = os.path.join(MAIN_FILE_PATH, "install_pip_user_dependencies.sh")
else:
    TERMINAL_SYMBOL = ">"
    MODULE_INSTALL_FILE = os.path.join(MAIN_FILE_PATH, "install_pip_user_dependencies.bat")

# welcome print
DESC_STRING = "======== " + global_vars.FW_NAME + " Testing Framework " + PLATFORM_TYPE + " Platform ========"

# help string
HELP_HINT_PRINT = (
    f"\n{'=' * 30 + ' HELP ' + '=' * 30}\n"
    f"{'See command line options with following commands:'}\n"
    f"{TERMINAL_SYMBOL + ' python3 ' + os.path.basename(__file__) + ' -h (for supported commands)'}\n\n"
    f"{'NOTE: Call Python based on how its installed on your machine'}\n"
    f"{'=' * 30 + ' HELP ' + '=' * 30}"
)
def install_python_pkgs():
    """
    Function to install python modules or libraries required to run the framework automatically
    """
    if sys.platform == "win32":
        process = subprocess.Popen(
            [
                os.path.join(MAIN_FILE_PATH, MODULE_INSTALL_FILE),
                os.sep.join(str(item) for item in sys.executable.split(os.sep)[:-1]),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
    else:
        # pylint: disable=consider-using-with
        process = subprocess.Popen(
            [os.path.join(MAIN_FILE_PATH, MODULE_INSTALL_FILE)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
    output, _ = process.communicate()
    if "All Modules installed successfully" not in output:
        raise RuntimeError(
            f"Error during installing Python packages to run ConTest tool\n{output}\nPlease contact ConTest team"
        )
    logging.info(output)


def modules_checker():
    """
    Function to find out ptf required modules are installed

    :returns: list of not found modules
    """
    not_found_module_list = []
    for module in MODULES_LIST:
        try:
            __import__(module)
        except ImportError:
            not_found_module_list.append(module)
    return not_found_module_list


# disabling 'too-many-branches' warning from pylint because we need to check each cli option
# and raise relevant error(s)
# pylint: disable=too-many-branches
# disabling 'too-many-statements' warning, statements needed as per logic
# pylint: disable=too-many-statements
def args_checker(args):
    """
    Function for checking arguments and raising errors in-case of wrong arguments
    :param obj args: Command line arguments
    """
    # check if cfg file exists
    if args.c is not None:
        if not os.path.exists(args.c):
            raise RuntimeError(
                "Wrong -c option detected: "
                "\nLocation (" + args.c + ") doesn't exist. "
                "Please check if config (.ini) file exists"
            )
    # check if base location exists
    if args.l is not None:
        if not os.path.exists(args.l):
            raise RuntimeError(
                "Wrong -l option detected: \n"
                "Location (" + args.l + ") doesn't exist. Please enter correct base location"
            )
    # check if correct run mode is mentioned
    if args.r.lower() not in global_vars.RUN_MODES:
        raise RuntimeError(
            "Wrong -r option detected: \n" "Please mention run mode name from this list " + str(global_vars.RUN_MODES)
        )
    # check if correct uim values are mentioned
    if args.uim.lower() not in global_vars.UIM_CLI_ARGS:
        if not args.uim.endswith(".txt"):
            raise RuntimeError(
                "\nPlease provide one of following values with '--uim' option.\n\n"
                "'--uim latest'   --> for installing all available latest tool packages from ConTest Team.\n"
                "'--uim pkgs.txt' --> for installing particular ConTest tool or Python packages.\n\n"
                "*** For more information contact ConTest Team."
            )
    # check if correct timestamp is mentioned
    if args.timestamp.lower() not in ["on", "off"]:
        raise RuntimeError(
            "Wrong --timestamp option detected: \n"
            "Please mention timestamp option from this list " + str(["on", "off"])
        )
    # check if run mode is auto and no configuration is mentioned
    if (args.r.lower() == global_vars.AUTO_MODE or args.r.lower() == global_vars.AUTO_GUI_MODE) and args.c is None:
        raise RuntimeError("Configuration is not mentioned with -c option")
    # check if base location is given without configuration mentioned
    if args.l is not None and args.c is None:
        raise RuntimeError("Configuration is not mentioned with -c option")

    # check if No of loops is given without configuration mentioned
    if args.n is not None and args.c is None:
        raise RuntimeError("Configuration is not mentioned with -c option")

    # check if external location is given without configuration mentioned
    if args.e is not None and args.c is None:
        raise RuntimeError("Configuration is not mentioned with -e option")

    # custom setup file only works if configuration is loaded
    if args.setup_file and not args.c:
        raise RuntimeError("Configuration is not mentioned with -c option")

    # check path of setup file if user provide file with path
    if args.setup_file:
        if "\\" in args.setup_file or "/" in args.setup_file:
            if not os.path.exists(args.setup_file):
                raise RuntimeError(f"Given setup file '{args.setup_file}' not found")

    # report directory option only works if configuration is loaded
    if args.report_dir and not args.c:
        raise RuntimeError("Configuration is not mentioned with -c option")

    if args.filter:
        # filtering only works if configuration is loaded
        if not args.c:
            raise RuntimeError("Configuration is not mentioned with -c option")
        if len(args.filter[0]) < 2:
            raise RuntimeError("No filter value given. Please give at least one filter type value.")

        # Check for valid filter types
        filter_type = args.filter[0][0]
        try:
            global_vars.ValidFilter[filter_type.upper()]
        # proper error is raised so raise-missing-from not required
        # pylint: disable=raise-missing-from
        except KeyError:
            valid_types = [valid_filter.name.lower() for valid_filter in global_vars.ValidFilter]
            raise RuntimeError(
                f"Invalid filter provided: '{filter_type}'. Please use one of '{', '.join(valid_types)}'"
            )


# pylint: disable=import-outside-toplevel
def run_in_non_ui_mode(args, selected_tests_exec_record):
    """
    Function for running tests in non-ui mode

    :param argparser args: Command line arguments if any
    :param list selected_tests_exec_record: Selected test cases that needs to be run based on selected verdict,
                when run_exec_record was requested on CLI

    :rtype: int
    :returns: returns 0 in-case all tests are passed else 2
    """
    from data_handling import common_utils
    from data_handling.prepare_test_data import PrepareTestData

    filter_tag_values = None
    # storing paths and no of loops value
    user_cfg = common_utils.store_cfg_data(cfg_file=args.c, new_base_location=args.l, no_of_loops=args.n)
    # If run_exec_record was requested, replace selected test cases from cfg.ini with the ones requested to be run
    # according to verdict in previous run.
    if args.subparser_name == "run_exec_record":
        selected_test = user_cfg.selected_tests
        selected_test["selected_tests"] = selected_tests_exec_record
        user_cfg.selected_tests = selected_test
    # user info if CAPL test path is saved in cfg which means that user is using an old format of cfg which need to be
    # edited as handling of CANoe tests has been changed in new contest version
    if user_cfg.capl_test_path:
        LOG.info(
            "%s %s\nYour ConTest cfg contains path to CAPL tests which is now changed cfg path."
            "\nThis means that you can now mention the path of CANoe cfg directly in ConTest cfg "
            "and all test modules in CANoe cfg will appear on ConTest GUI for selection and "
            "saving purpose.\n Please edit your configuration from ConTest GUI 'Menu->Edit Config' "
            "option by mentioning your CANoe cfg path.\n%s",
            "\n",
            "*" * 200,
            "*" * 200,
        )
    # now verify paths existence
    try:
        user_cfg.post_load_config()
    except RuntimeError as error:
        raise error
    # created a list with test names saved in different test categories in cfg file
    tests_in_cfg = list(
        itertools.chain.from_iterable(
            [tests_type_list for _, tests_type_list in user_cfg.selected_tests.items() if len(tests_type_list) != 0]
        )
    )
    # if no tests found in configuration and no filter provided then raise error
    if not any(tests_in_cfg) and args.filter is None:
        raise RuntimeError("No test cases were saved in configuration '" + args.c + "'")
    # extracting filters tag values
    if args.filter is not None:
        filter_tag_values = list(args.filter[0][1:])
    # create instance of 'PrepareTestData' for data handling
    data_creator = PrepareTestData()
    # prepare test cases data from locations in cfg file
    duplication_exist, error = data_creator.prepare_test_data_from_cfg(
        configuration=user_cfg, filter_values=filter_tag_values, setup_file=args.setup_file
    )
    # if duplications found then raise error
    if duplication_exist:
        raise RuntimeError(error)
    # detect if any setup script are duplicated by name in order to avoid ambiguity during grabbing
    # it's functions objects
    data_creator.detect_duplicate_setup_files()
    # filter tests based on filter tag or tests in cfg file
    data_creator.filter_tests_to_run(user_cfg.selected_tests, filter_tag_values, args.reverse_selection)
    data_creator.test_runner_data[
        "parameterized_tests"
    ] = data_creator.update_and_get_parameterized_tests_for_test_runner()
    # now grab setup file data
    if args.setup_file:
        setup_data = data_creator.filter_and_get_setup_file_data(args.setup_file)
    else:
        setup_data = data_creator.filter_and_get_setup_file_data("setup")
    # now prepare data for test runner stage with given cli options and cfg file data
    data_creator.prepare_runner_data(
        args.random_execution, args.report_dir, setup_data, user_cfg.num_loops, args.r, args.e, args.timestamp
    )
    # creating an instance of test runnerptf.ptf_utils import test_runner
    from ptf.ptf_utils import test_runner

    test_runner = test_runner.TestRunner(data_creator, None)
    # triggering test runner
    return test_runner.run()


def init_and_get_rest_service(port_no, contest_client):
    """
    Function for Initializes and starts the Clients in a thread and returns the rest service client
    object

    :param int port_no: contains the port number which is used to connect the rest server
    :param obj contest_client: ConTest client module object

    :rtype: Client Object
    :returns: returns client object
    """
    # get the ip address of the current host PC
    get_host_name_ip()
    # creating the object of Client and starting the client in a thread
    client_obj = contest_client.Client(f"ws://localhost:{port_no}", 1)
    client_thread = Thread(target=client_obj.start_client)
    client_thread.daemon = True
    client_thread.start()
    return client_obj


def get_host_name_ip():
    """
    Function get the current running host ip address
    """
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        LOG.info("Client Hostname :  {%s}", host_name)
        LOG.info("Client Host IP Address :  {%s}", host_ip)
    # ok to catch general exceptions
    # pylint: disable=broad-exception-caught
    except Exception as error:
        LOG.error("Unable to get Hostname and IP Address.\nError: {%s}", error)


class ConsoleHandler(logging.Handler):
    """
    A console handler for logging framework. It will print the formatted message using
    the print statement - in contrary to the default console handler, which will directly
    print to sys.stdout. Since we redirect sys.stdout during test execution, we need to
    be sure that also logs printed within a test-case are properly redirected.
    """

    def emit(self, record):
        """
        Prints the record using print statement

        :param logging.LogRecord record: The record to print
        """
        print(self.format(record))


def __initialize_logging(time_stamp):
    """
    Will initialize the logging framework for our needs.
    Should be called as first function within the main function.
    :param str time_stamp: Contains ''enable'' or ''disable''
    """

    # Initializes root logger. We cannot use logging.basicConfig here or our prints to stdout
    # will not be redirected properly to the test case output
    root_logger = logging.getLogger()

    if time_stamp.lower() == "on":
        formatter = logging.Formatter(
            fmt="[" + global_vars.FW_NAME + " %(name)s" " %(asctime)s,%(msecs)03d]" " %(message)s", datefmt="%H:%M:%S"
        )
    elif time_stamp.lower() == "off":
        formatter = logging.Formatter("[" + global_vars.FW_NAME + " %(name)s] %(message)s")
    console_handler = ConsoleHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)

    # Silence some loggers from third party libs
    logging.getLogger("canmatrix.formats").setLevel(logging.ERROR)
    logging.getLogger("numexpr.utils").setLevel(logging.ERROR)

    # Overwrite default config with custom log file (e.g. for debugging purpose)
    cfg_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logging.conf")
    if os.path.exists(cfg_file):
        logging.config.fileConfig(cfg_file, disable_existing_loggers=False)


# disabling too-many-statements as it's the main function
# pylint: disable=too-many-statements, import-outside-toplevel, import-error, too-many-locals
def main():
    """
    Main function for handling input arguments
    """
    exit_code = global_vars.SUCCESS
    selected_tests_exec_record = []
    # create argument parser which is used then to parse
    parser = argparse.ArgumentParser(description=DESC_STRING, formatter_class=argparse.RawTextHelpFormatter)
    subparser = parser.add_subparsers(
        help="Run test cases with given verdict from a previous test execution run", dest="subparser_name"
    )

    exec_record_subparser = subparser.add_parser("run_exec_record")

    # adding cfg file argument
    parser.add_argument(
        "-c", help="Enter path of configuration (.ini) file", type=str, required=False, metavar="cfg_file"
    )

    # adding run mode argument
    parser.add_argument(
        "-r",
        help="Enter Run Mode (manual or auto or auto_gui). Default is manual",
        type=str,
        required=False,
        default="manual",
        metavar="run_mode",
    )

    # adding run mode argument
    parser.add_argument(
        "--uim", help="ConTest Utility Install Manager (UIM)", type=str, required=False, default="none", metavar="uim"
    )

    # adding base location argument
    parser.add_argument(
        "-l",
        help="Enter base location if it's different from location in config file",
        type=str,
        required=False,
        metavar="base_loc",
    )

    # adding no of times the test cases shall run
    parser.add_argument(
        "-n",
        help="Enter integer value to run the test cases multiple times",
        type=int,
        required=False,
        metavar="no_of_loops",
    )

    # adding base location argument
    parser.add_argument(
        "-e",
        help="Enter locations which need to be added in sys.path for importing python modules",
        required=False,
        nargs="+",
        action="append",
        metavar="ext_loc",
    )

    # adding randomized execution argument
    parser.add_argument(
        "--random",
        help="If this flag is given, the tests will be executed in random order",
        required=False,
        action="store_true",
        dest="random_execution",
    )

    # add dark mode argument
    parser.add_argument(
        "--dark-mode", help="Start the gui in dark mode", required=False, action="store_true", dest="dark_mode"
    )

    # add setup file selection argument
    parser.add_argument(
        "--setup-file",
        help="If a file is given, this setup file will be used instead of the default setup.pytest",
        required=False,
        metavar="setup_file",
    )

    # add setup file selection argument
    parser.add_argument(
        "--check-pip-mods",
        help="Argument to check if all pip modules required to run framework are installed",
        required=False,
        action="store_true",
    )

    # add report directory option for CI execution
    parser.add_argument(
        "--report-dir", help="Location where reports will be generated.", required=False, metavar="report_dir"
    )

    # add filter argument
    parser.add_argument(
        "--filter",
        help="Filter test execution. A filter is a pair of 'filter_type', 'filter_values'.\n"
        "See documentation for available filter types and values.\n"
        "If multiple filter are provided, or the same filter is provided multiple\n"
        "times, all filters must match for a testcase to be executed",
        required=False,
        nargs="+",
        action="append",
        metavar=("filter_type", "filter_values"),
    )
    # adding rest port argument
    parser.add_argument(
        "--rest-port",
        help="Start Contest with rest client. A Rest Client is provided with port number.\n"
        "The port must be used equal to rest server port, which is running\n"
        "independently on same machine.",
        type=int,
        required=False,
        metavar="rest_port",
    )

    # add timestamp mode argument
    parser.add_argument(
        "--timestamp",
        help="Timestamp (on or off) for logging. Default is 'on'",
        type=str,
        required=False,
        default="on",
        metavar="time_stamp",
    )

    # adding 'run unselected tests' argument
    parser.add_argument(
        "--reverse_selection",
        help="If this flag is given, unselected tests will be executed.\nUser selected tests will be excluded from "
        "test run",
        required=False,
        action="store_true",
        dest="reverse_selection",
    )

    # adding 'execution record path' argument
    exec_record_subparser.add_argument(
        "-y", help="Enter path of execution record dir", type=str, required=False, metavar="execution_record_path"
    )

    # adding 'verdict selection' option
    exec_record_subparser.add_argument(
        "-v",
        help="Enter verdict option to be run: 'pass', 'fail', 'skip', 'inconclusive', 'unknown'."
        "\nMultiple verdicts can be selected",
        type=str,
        required=False,
        action="append",
        nargs="+",
        choices=["pass", "fail", "skip", "inconclusive", "unknown"],
        metavar="exec_record_verdicts",
    )

    # grabbing the configuration file in arguments
    args = parser.parse_args()

    client_obj = None
    try:
        # Contest client object
        client_obj = None
        # check args before passing them to next stage, normal run, run_exec_record was not requested
        if not args.subparser_name:
            args_checker(args)
        # get the default argument of the timestamp
        time_stamp = args.timestamp
        # Initialize logging before anything else
        __initialize_logging(time_stamp)

        # print welcome message
        LOG.info("Starting %s %s Platform", global_vars.FW_NAME, PLATFORM_TYPE)
        # The exit code of the program.
        # Default is 0 (= success), on errors this will be changed to values != 0
        exit_code = global_vars.SUCCESS

        LOG.info("Checking required Python modules ...")
        not_found_modules = modules_checker()
        if not not_found_modules:
            LOG.info("All Python modules exists for running framework")
            # exit with success if pip mods check bool arg was given
            if args.check_pip_mods:
                LOG.info("Exiting as user requested to only check for pip mods installations")
                sys.exit(global_vars.SUCCESS)
        else:
            LOG.info(
                "\n\nFollowing Python module(s) required to run framework not found\n\n--> %s\n\n"
                "Installing above modules automatically. Please wait ...",
                not_found_modules,
            )
            install_python_pkgs()

        from tabulate import tabulate
        from ptf.ptf_utils.exe_record import process_exec_data
        from uim import uim

        # Get exec_record.yml info
        if args.subparser_name == "run_exec_record":
            selected_tests_exec_record = process_exec_data(args)

        if args.uim:
            if args.uim == "latest":
                result = uim.install_all_contest_latest_packages()
                if result["connection_err"]:
                    print("*" * 100)
                    LOG.info(result["connection_err"])
                    print("*" * 100)
                    print(os.linesep)
                else:
                    print(tabulate(result["pkg_info_list"], headers=result["table_col_names"], tablefmt="pretty"))
                if args.r == global_vars.MANUAL_MODE:
                    input("Please check Utility Install Manager Results above. Press enter to continue ...")
            elif args.uim.endswith(".txt"):
                # check for file existence
                if os.path.exists(args.uim):
                    print("*" * 100)
                    LOG.info("Installing Python Packages provide in '%s' via '--uim' option", args.uim)
                    print("*" * 100)
                    result = subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "install",
                            "-r",
                            args.uim,
                            "-i",
                            uim.PIP_INDEX_URL,
                            "--trusted-host",
                            uim.PIP_TRUSTED_HOST,
                        ],
                        check=True,
                    )
                    if result.returncode != 0:
                        raise RuntimeError(
                            f"Failure in installing Python Packages provide in '{args.uim}' via '--uim' option"
                        )
                    print("*" * 100)
                    LOG.info("Success installing Python Packages provide in '%s' via '--uim' option", args.uim)
                    print("*" * 100)
                else:
                    raise RuntimeError(
                        f"File provided for '--uim' option doesn't exist. Please check.\n File: '{args.uim}'"
                    )
        import gui.ui_controller as gui_controller
        from rest_service import contest_client
        from PyQt5.QtCore import QCoreApplication

        # Set the application name to be used e.g. for configuration folders.
        # Must be set as early as possible to be properly recognized by other components.
        QCoreApplication.setApplicationName("ConTest")

        # if external path(s) for python module(s) given via cli option then add them to sys.path
        if args.e:
            non_existing_paths = []
            for path in [item for sub_list in args.e for item in sub_list]:
                if os.path.exists(path):
                    if path not in sys.path:
                        sys.path.append(path)
                        LOG.info("%s added to sys.path", path)
                else:
                    non_existing_paths.append(path)
            if non_existing_paths:
                err_str = f"External paths {non_existing_paths} given via CLI option does not exist."
                LOG.error(err_str)
                raise RuntimeError(err_str)

        # checking the rest service in CLI mode to start
        if args.rest_port is not None:
            # creating the object of Client and starting the client in a thread
            port_no = args.rest_port
            client_obj = init_and_get_rest_service(port_no, contest_client)

        # checking if user requested the automated run
        if args.r.lower() == global_vars.AUTO_MODE:
            LOG.info("Checking ConTest version from artifactory ...")
            version_str, version_tuple = global_vars.check_latest_version()
            if not version_tuple:
                LOG.info("Unable to find the latest version of ConTest")
            else:
                if global_vars.LOCAL_VERSION_TUPLE:
                    if version_tuple > global_vars.LOCAL_VERSION_TUPLE:
                        LOG.info(
                            "New version of ConTest '%s' is available. Please download 'v%s' version from %s",
                            global_vars.CONTEST_VERSION,
                            version_str,
                            global_vars.URL,
                        )
                else:
                    LOG.info("ConTest Version: %s", global_vars.CONTEST_VERSION)
                    LOG.info(
                        "You're not using official release version of ConTest. "
                        "Please download 'v%s' version from %s",
                        version_str,
                        global_vars.URL,
                    )
            exit_code = run_in_non_ui_mode(args, selected_tests_exec_record)
        # user requested GUI mode
        else:
            LOG.info("GUI Started")
            exit_code = gui_controller.run_gui(args=args, selected_tests_exec_record=selected_tests_exec_record)

    # raise run time error
    except RuntimeError as error:
        print("-" * 100)
        print(f"RuntimeError Occurred:\n{error}")
        print("-" * 100)
        exit_code = global_vars.GENERAL_ERR

    # raise basic exception
    except Exception as error:  # pylint: disable=broad-except
        print("-" * 100)
        print(error)
        print("-" * 100)
        exit_code = global_vars.GENERAL_ERR

    # things to do before exiting
    finally:
        # print help
        print(f"\n{HELP_HINT_PRINT}\n")
        print(f"Exiting {global_vars.FW_NAME} {PLATFORM_TYPE} Platform")
        if client_obj is not None:
            client_obj.stop_client()
        # exit the system
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
