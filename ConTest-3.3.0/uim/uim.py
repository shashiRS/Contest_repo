"""
    Copyright 2023 Continental Corporation

    :file: uim.py
    :synopsis:
        ConTest Utility Install Manager (UIM) implementation script

    :author:
        - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
"""

import subprocess
import sys
import re
import urllib.request
import logging
from distutils.version import LooseVersion
from http import HTTPStatus
import requests

from contest_verify.verify import contest_asserts


PIP_INDEX_URL = "https://artifactory.geo.conti.de/artifactory/api/pypi/c_adas_cip_pypi_v/simple/"
PIP_TRUSTED_HOST = "artifactory.geo.conti.de"
HINT = "Please contact ConTest team"
# this version will be changed at the moment it's for testing
INITIAL_VERSION = "3.0.0"
CONNECTION_ERR = (
    f"Python packages artifactory URL {PIP_INDEX_URL} is not accessible.\n" f"*** HINT: Please contact ConTest team."
)
LOG = logging.getLogger("UIM")


def get_all_available_versions(pkg_name):
    """
    Function to fetch all available versions from remote link

    :param str pkg_name: Name of the package whose versions need to be fetched

    :returns: tuple (status, versions list)
    :rtype: tuple
    """
    status = True
    version_list = []
    try:
        with urllib.request.urlopen(PIP_INDEX_URL + pkg_name, timeout=3) as response:
            data = response.read().decode().split("\n")
            wheel_name_pattern = r">(.*?).whl"
            version_pattern = r"(\d+\.\d+\.\d+)"
            for version_str in data:
                wheel_name = re.search(wheel_name_pattern, version_str)
                if wheel_name:
                    wheel_name = wheel_name.group(1)
                    version_match = re.search(version_pattern, wheel_name)
                    if version_match:
                        version = version_match.group(1)
                        version_list.append(version)
    # disabling too broad exception for catching any error raised
    # pylint: disable=W0718
    except Exception:
        status = False
    return status, version_list


# disabling invalid-name as used name is explanatory
# pylint: disable=C0103
def install_contest_pkg_for_backward_compatibility_support(util_name):
    """
    Function to install a contest tool utilities which are available as wheel package from the artifactory
    path:https://artifactory.geo.conti.de/artifactory/api/pypi/c_adas_cip_pypi_v/simple/

    Source Tool Utilities Repo: https://github-am.geo.conti.de/ADAS/contest_tools_utils

    This function will be used in `__init__.py` file of `ptf/tools_utils/<util_name>` folder for backward compatibility
    support

    :param string util_name: Name of contest tool utility available as wheel package
    """
    LOG.info("ConTest tool utility '%s' is now available as wheel package", util_name)
    LOG.info("Trying to install '%s'. Please wait... ", util_name)
    contest_asserts.verify(
        check_artifactory_connection(),
        True,
        f"Error while trying to install ConTest tool utility '{util_name}' which is now available as "
        f"python wheel package.\n{CONNECTION_ERR}",
    )
    install_cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-i",
        PIP_INDEX_URL,
        "--trusted-host",
        PIP_TRUSTED_HOST,
        util_name,
    ]
    try:
        subprocess.run(install_cmd, shell=False, stderr=subprocess.PIPE, check=True, universal_newlines=True)
    except subprocess.CalledProcessError as process_err:
        contest_asserts.fail(
            f"Error in installing {util_name}\nError: {process_err.stderr}\n*** HINT: Please contact ConTest Team"
        )
    # disabling too broad exception for catching any error raised
    # pylint: disable=W0718
    except Exception as gen_err:
        contest_asserts.fail(
            f"Error in installing {util_name}\nError: {gen_err}\n*** HINT: Please contact ConTest Team"
        )
    else:
        LOG.info("Successfully installed ConTest tool utility '%s'", util_name)


def check_artifactory_connection():
    """
    Function to check if user can access artifactory link where packages are placed

    :returns: ``True`` if user can access artifactory link ``False``
    :rtype: bool
    """
    ret_val = True
    try:
        # trying to access contest_verify package url in order to validate the user connection to packages artifactory
        # link
        connection = requests.get(PIP_INDEX_URL + "contest_verify", timeout=5)
    # disabling too broad exception for catching any error raised
    # pylint: disable=W0718
    except Exception:
        ret_val = False
    else:
        if connection.status_code != HTTPStatus.OK:
            ret_val = False
    return ret_val


# disabling inconsistent-return-statements as the dictionary need to be returned based non-ui usage and ui signal
# containing dictionary need to be emitted in-case of ui usage
# disabling too-many-branches and too-many-statements as they are necessary for the logic to be at one place
# pylint: disable=R1710
# pylint: disable=R0912
# pylint: disable=R0915
def get_contest_pkgs_from_remote(with_versions=False, ui_signals=None):
    """
    Function to get all contest tool packages from remote `PIP_INDEX_URL`

    :param bool with_versions: Flag for fetching each tool pacakge available versions
    :param dict ui_signals: Dictionary containing ui signals to be emitted in-case of UI calls

    :returns: dictionary containing keys as tool packages names and value as their version's info, errors (if any) etc.
    :rtype: dict
    """
    # disabling too-many-locals as they are required
    # pylint: disable=R0914
    contest_pkgs_on_remote_info = {}
    error_info = None
    LOG.info("Getting all ConTest tool utilities packages from remote. Please wait ...")
    try:
        pip_search_ret = subprocess.run(
            [sys.executable, "-m", "pip", "search", "-i", PIP_INDEX_URL, "contest"],
            shell=False,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            check=True,
            universal_newlines=True,
        )
    except subprocess.CalledProcessError as process_error:
        error_info = (
            f"Error in fetching ConTest tool utilities packages from remote.\nError: {process_error.stderr}.\n"
            "*** HINT: Please contact ConTest team."
        )
    # disabling too broad exception for catching any error raised
    # pylint: disable=W0718
    except Exception as gen_err:
        error_info = (
            f"Error in fetching ConTest tool utilities packages from remote.\nError: {gen_err}.\n"
            "*** HINT: Please contact ConTest team."
        )
    if error_info:
        if ui_signals:
            LOG.info("ERR: %s", error_info)
            ui_signals["general_error"].emit(error_info)
        return contest_pkgs_on_remote_info, error_info
    pkgs_on_remote_list = pip_search_ret.stdout.split("\n")
    # creating a list with unique packages names, this has been added after observing that on remote the packages
    # can duplicate e.g. contest-canoe and contest_canoe, therefore in below lines a unique list is created, removing
    # duplicates after replacing '_' with '-'
    contest_pkgs = [pkgs.split(" ")[0].replace("_", "-") for pkgs in pkgs_on_remote_list if pkgs.startswith("contest")]
    contest_pkgs_on_remote = sorted(list(set(contest_pkgs)))

    if with_versions:
        LOG.info("Getting all ConTest tool utilities versions from remote. Please wait ...")
    for pkg_name in contest_pkgs_on_remote:
        all_versions = ["none"]
        latest_version = None
        to_update = False
        error = None
        result = get_pip_show(pkg_name)
        if result["pip_show_err"]:
            local_version = "Not-Available"
            to_update = True
        else:
            local_version = result["pkg_version"]
        if with_versions:
            status, versions = get_all_available_versions(pkg_name)
            if status:
                filtered_versions = [
                    version for version in versions if LooseVersion(version) >= LooseVersion(INITIAL_VERSION)
                ]
                if filtered_versions:
                    all_versions = filtered_versions
                    latest_version = max(filtered_versions, key=lambda x: tuple(map(int, (x.split(".")))))
                    if latest_version > local_version:
                        to_update = True
                else:
                    all_versions = ["NA"]
            else:
                all_versions = ["none"]
                error = (
                    f"Error in fetching ConTest tool utility '{pkg_name}' versions from remote.\n"
                    "*** HINT: Please contact ConTest team."
                )
        else:
            all_versions = ["skipped"]
        # excluding the packages whose versions are not > 'INITIAL_VERSION'
        if all_versions != ["NA"]:
            contest_pkgs_on_remote_info[pkg_name] = {}
            contest_pkgs_on_remote_info[pkg_name]["all_versions"] = all_versions
            contest_pkgs_on_remote_info[pkg_name]["latest_version"] = latest_version
            contest_pkgs_on_remote_info[pkg_name]["to_update"] = to_update
            contest_pkgs_on_remote_info[pkg_name]["error"] = error
            contest_pkgs_on_remote_info[pkg_name]["local_version"] = local_version
            if ui_signals:
                ui_signals["add_data"].emit(contest_pkgs_on_remote_info)
    LOG.info("Packages information fetched.")
    if ui_signals:
        ui_signals["ready_state"].emit()
    else:
        return contest_pkgs_on_remote_info, error_info


def get_pip_show(pkg_name):
    """
    Function to return the output of "pip show <pkg_name>" command

    :param string pkg_name: Name of the package (contest python tool utility library)

    :returns: output of "pip show <pkg_name>" command
    :rtype: dict
    """
    show_info = {
        "pip_show_err": None,
        "pip_show_stdout": None,
        "pkg_version": None,
        "pkg_url": None,
    }
    cmd = [sys.executable, "-m", "pip", "show", pkg_name]
    try:
        ret = subprocess.run(
            cmd, shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True, universal_newlines=True
        )
    except subprocess.CalledProcessError as error:
        error_str = error.stderr
        show_info["pip_show_err"] = error_str
    # disabling too broad exception for catching any error raised
    # pylint: disable=W0718
    except Exception as error:
        show_info["pip_show_err"] = error
    else:
        show_info["pip_show_stdout"] = ret.stdout
        pattern = r"\s*(.*?)\s*(\d+\.\d+\.\d+)\s*"
        matches = re.findall(pattern, show_info["pip_show_stdout"])
        for _, version in matches:
            show_info["pkg_version"] = version
    return show_info


# disabling inconsistent-return-statements as the dictionary need to be returned based non-ui usage and ui signal
# containing dictionary need to be emitted in-case of ui usage
# pylint: disable=R1710
def install_package_version(pkg_name, pkg_version, ui_sig=None):
    """
    Function for installing all latest versions of contest tool packages from remote `PIP_INDEX_URL`

    :param string pkg_name: Name of contest tool util
    :param string pkg_version: Version of contest tool util
    :param object ui_sig: UI signal object

    :returns: a dictionary containing all necessary information
    :rtype: dict
    """
    pkg_install_info = {"install_result": False, "install_err": "None", "pkg_info": None, "install_stdout": None}
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-i",
        PIP_INDEX_URL,
        "--trusted-host",
        PIP_TRUSTED_HOST,
        pkg_name + "==" + pkg_version,
    ]
    if pkg_version == "NA":
        pkg_install_info["install_result"] = False
        pkg_install_info["install_err"] = f"{pkg_name} package official version is not available"
    else:
        try:
            ret = subprocess.run(
                cmd, shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True, universal_newlines=True
            )
        except subprocess.CalledProcessError as error:
            error_str = error.stderr
            pkg_install_info["install_result"] = False
            pkg_install_info["install_err"] = error_str
        # disabling too broad exception for catching any error raised
        # pylint: disable=W0718
        except Exception as error:
            pkg_install_info["install_result"] = False
            pkg_install_info["install_err"] = error
        else:
            pkg_install_info["install_result"] = True
            pkg_install_info["install_stdout"] = ret.stdout
            print(ret.stdout)
    if ui_sig:
        ui_sig.emit(pkg_install_info)
    else:
        return pkg_install_info


def install_all_contest_latest_packages():
    """
    Function for installing all latest versions of contest tool packages from remote `PIP_INDEX_URL`

    :returns: a dictionary containing all necessary information
    :rtype: dict
    """
    col_names = ["ConTest Tool Utility", "Version To Install", "Available Versions", "Installation Status", "Hint"]
    pkg_installation_status = {}
    pkg_installation_status_list = []
    return_dictionary = {
        "pkg_info_list": pkg_installation_status_list,
        "table_col_names": col_names,
        "connection_err": str(),
    }
    if not check_artifactory_connection():
        return_dictionary["connection_err"] = CONNECTION_ERR
    else:
        contest_remote_pkgs, return_dictionary["connection_err"] = get_contest_pkgs_from_remote(with_versions=True)
        if return_dictionary["connection_err"]:
            return return_dictionary
        for pkg, pkg_info in contest_remote_pkgs.items():
            pkg_installation_status[pkg] = {}
            status_list = [pkg, pkg_info["latest_version"], pkg_info["all_versions"]]
            LOG.info("Installing latest '%s' version (%s). Please wait ...", pkg, pkg_info["latest_version"])
            cmd = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-i",
                PIP_INDEX_URL,
                "--trusted-host",
                PIP_TRUSTED_HOST,
                pkg + "==" + pkg_info["latest_version"],
            ]
            try:
                subprocess.run(
                    cmd,
                    shell=False,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    check=True,
                    universal_newlines=True,
                )
            except subprocess.CalledProcessError as error:
                # return_dictionary["error_occurred"] = True
                error_str = error.stderr
                pkg_installation_status[pkg]["status"] = False
                pkg_installation_status[pkg]["error"] = error_str
                pkg_installation_status[pkg]["hint"] = HINT
                status_list.append(pkg_installation_status[pkg]["status"])
                status_list.append(pkg_installation_status[pkg]["hint"])
            # disabling too broad exception for catching any error raised
            # pylint: disable=W0718
            except Exception as error:
                # return_dictionary["error_occurred"] = True
                pkg_installation_status[pkg]["status"] = False
                pkg_installation_status[pkg]["error"] = error
                pkg_installation_status[pkg]["hint"] = HINT
                status_list.append(pkg_installation_status[pkg]["status"])
                status_list.append(pkg_installation_status[pkg]["hint"])
            else:
                pkg_installation_status[pkg]["status"] = True
                pkg_installation_status[pkg]["error"] = None
                pkg_installation_status[pkg]["hint"] = "All Good"
                status_list.append(pkg_installation_status[pkg]["status"])
                status_list.append(pkg_installation_status[pkg]["hint"])
            pkg_installation_status_list.append(status_list)
    return return_dictionary


# def install_latest_remote_pkgs_not_available_locally():
#     """
#     TBD
#     """
#     if not check_artifactory_connection():
#         contest_asserts.fail(
#             "You're not on Continental network. Please make sure your on Continental Company Network.")
#     contest_remote_pkgs = get_contest_pkgs_from_remote()
#     contest_installed_pkgs = get_installed_contest_pkgs()
#     remote_pkgs_list = list(contest_remote_pkgs.keys())
#     installed_pkgs_list = list(contest_installed_pkgs.keys())
#     LOG.info("Checking if all available packages existing remotely are installed in '{}'".format(sys.executable))
#     missing_pkgs = dict()
#     if sorted(remote_pkgs_list) == sorted(installed_pkgs_list):
#         LOG.info("All available packages existing remotely are already installed. Great !")
#     else:
#         LOG.info("It has been observed that some ConTest tool packages are missing, which shall be installed")
#         for pkg, pkg_info in contest_remote_pkgs.items():
#             if pkg not in contest_installed_pkgs.keys():
#                 missing_pkgs[pkg] = pkg_info
#     pkg_installation_status = dict()
#     pkg_installation_status_list = list()
#     for pkg, pkg_info in missing_pkgs.items():
#         pkg_installation_status[pkg] = dict()
#         status_list = [pkg, pkg_info["latest_version"], pkg_info["all_versions"]]
#         LOG.info("Installing '{}'. Please wait ...".format(pkg))
#         cmd = [sys.executable, "-m", "pip", "install", '-i', PIP_INDEX_URL, '--trusted-host', PIP_TRUSTED_HOST, pkg]
#         try:
#             subprocess.run(
#                 cmd, shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True, universal_newlines=True)
#         except subprocess.CalledProcessError as error:
#             error_str = error.stderr
#             pkg_installation_status[pkg]["status"] = False
#             pkg_installation_status[pkg]["error"] = error_str
#             status_list.append(pkg_installation_status[pkg]["status"])
#             status_list.append(pkg_installation_status[pkg]["error"])
#         except Exception as error:
#             pkg_installation_status[pkg]["status"] = False
#             pkg_installation_status[pkg]["error"] = error
#             status_list.append(pkg_installation_status[pkg]["status"])
#             status_list.append(pkg_installation_status[pkg]["error"])
#         else:
#             pkg_installation_status[pkg]["status"] = True
#             pkg_installation_status[pkg]["error"] = None
#             status_list.append(pkg_installation_status[pkg]["status"])
#             status_list.append(pkg_installation_status[pkg]["error"])
#         pkg_installation_status_list.append(status_list)
#
#     if pkg_installation_status_list:
#         col_names = [
#             "ConTest Tool Utility", "Version To Install", "Available Versions", "Installation Status", "Error"]
#         print(tabulate(pkg_installation_status_list, headers=col_names, tablefmt="pretty"))
