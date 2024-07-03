"""
    Copyright Continental Corporation and subsidiaries. All rights reserved.
    :platform: Windows and Linux
    :synopsis:
        This module contains functions for some common use cases that will be useful for various
        tools.
"""

# disabling import error as they are installed at start of framework
# pylint: disable=import-error, exec-used
import os
import sys
import subprocess
import logging
import platform
import yaml


from contest_verify.verify import contest_asserts
import global_vars

LOGGER_NAME = "COMMON"

LOG = logging.getLogger("COMMON")

PIP_TRUSTED_HOST = "artifactory.geo.conti.de"
PIP_INDEX_URL = "https://artifactory.geo.conti.de/artifactory/api/pypi/c_adas_cip_pypi_v/simple"
PY_MOD_INSTALL_CMD = [
    sys.executable,
    "-m",
    "pip",
    "install",
    "-i",
    PIP_INDEX_URL,
    "--trusted-host",
    PIP_TRUSTED_HOST,
    "",
]
PYTHON_LIBS = os.path.join(global_vars.THIS_FILE, "install_scripts", "python_libraries.yml")
SYS_EXE_DIR_PATH = os.path.dirname(sys.executable)


def is_jenkins():
    """
    Will check if the current execution is done in a jenkins environment.

    :return: True if is running in a jenkins instance, False if not.
    :rtype: bool
    """
    return "JENKINS_URL" in os.environ


def install_pip_pkg(mod, version):
    """
    Function to install given python modules with a specific version (if required)

    :param string mod: Python module to install
    :param string version: Module version to be installed

    :return: the error (if any)
    :rtype: string or None
    """
    error = None
    if version:
        PY_MOD_INSTALL_CMD[-1] = f"{mod}=={version}"
    else:
        PY_MOD_INSTALL_CMD[-1] = mod
    try:
        subprocess.run(PY_MOD_INSTALL_CMD, check=True, env=None, stdout=subprocess.PIPE, shell=False)
    # pylint: disable=broad-exception-caught
    except Exception:
        error = (
            f"Error in installing {mod}\nPIP Command: '{' '.join(PY_MOD_INSTALL_CMD)}'\n"
            f"Please contact ConTest team via PMT Service ticket"
        )
    return error


def pip_pkg_checker_plus_installer(mods):
    """
    Function to check given Python modules given in list and also installing them

    :param list mods: List of modules which need to be installed
    """
    LOG.info("Checking if some Python modules need to be installed ...")
    mods_status = {}
    for mod in mods:
        mods_status[mod[0]] = True
        try:
            exec(f"import {mod[0]}")
        except ImportError:
            LOG.info("'%s' is not installed", mod[0])
            LOG.info("Installing '%s' module via PIP. Please wait ...", mod[0])
            status = install_pip_pkg(mod[0], mod[1])
            if not status:
                try:
                    exec(f"import {mod[0]}")
                except ImportError:
                    LOG.info("%s ERROR %s", "*" * 50, "*" * 50)
                    LOG.info("'%s' module import having issues even after successful installation", mod[0])
                    LOG.info("Please consider restarting ConTest tool")
                    LOG.info("If issue persists contact ConTest team via PMT Service ticket")
                    LOG.info("%s ERROR %s", "*" * 50, "*" * 50)
                    mods_status[mod[0]] = False
                LOG.info("*" * 100)
                LOG.info("'%s' module successfully installed", mod[0])
                LOG.info("*" * 100)
            else:
                LOG.info("%s ERROR %s", "*" * 50, "*" * 50)
                LOG.info(status)
                LOG.info("%s ERROR %s", "*" * 50, "*" * 50)
                mods_status[mod[0]] = False
        else:
            LOG.info("*" * 100)
            LOG.info("'%s' already installed", mod[0])
            LOG.info("*" * 100)
    # checking the failures if any
    failed_mods = []
    for mod, status in mods_status.items():
        if not status:
            failed_mods.append(mod)
    # if any failure occurred then raise error
    if failed_mods:
        contest_asserts.fail(f"Problem is installing following PIP modules.\n{failed_mods}")


def run_pywin32_install_check():
    """
    Function responsible checking installation of pywin32
    """
    try:
        exec("import win32com.client")
    except ImportError:
        error_str = (
            "Error in installing 'pywin32'\n"
            "*** HINT: Please close the ConTest tool and run again\n"
            "          This will hopefully resolve this issue\n"
            "          Apologies for this inconvenience (pywin32 installation is not perfect)\n"
            "          If your issue is not solved even after ConTest restart then please contact ConTest Team"
        )
        contest_asserts.fail(error_str)


def install_mods_via_yaml(util_name):
    """
    Function responsible for checking the installation of python libraries for a contest tool utility.
    The installation of the python library shall also be done in case the library installation is missing.

    :param string util_name: name of the contest tool utility mentioned in `install_scripts/python_libraries.yml`
    """
    try:
        with open(PYTHON_LIBS, encoding="utf-8") as f:
            util_py_libs = yaml.safe_load(f)[util_name]
        for util_py_lib in util_py_libs:
            util_lib = util_py_lib[0]
            util_lib_import_check = util_py_lib[1]
            LOG.info("Checking '%s' installation for '%s'", util_lib, util_name)
            try:
                # checking if the import checker string is not None, if it's None then we need to do force install
                if util_lib_import_check != "None":
                    exec(util_lib_import_check)
                else:
                    raise ImportError
            except ImportError:
                PY_MOD_INSTALL_CMD[-1] = util_lib
                LOG.info("Installing '%s' for '%s'", util_lib, util_name)
                LOG.info("Please wait ...")
                # need to run post install script for pywin32 module only
                if util_lib.split("==")[0] == "pywin32" and platform.system() == "Windows":
                    ret = subprocess.run(
                        PY_MOD_INSTALL_CMD,
                        stderr=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        check=True,
                        universal_newlines=True,
                    )
                    LOG.info(ret.stdout)
                    if "Successfully installed" in ret.stdout and "CONTEST_DOC_BUILDER" not in os.environ:
                        run_pywin32_install_check()
                    else:
                        LOG.info(
                            "%s\n"
                            "Ignoring the post install check for pywin32 as its problematic and its only doc build\n"
                            "%s",
                            "/" * 100,
                            "/" * 100,
                        )
                else:
                    subprocess.run(PY_MOD_INSTALL_CMD, stderr=subprocess.PIPE, check=True, universal_newlines=True)
            else:
                LOG.info("'%s' already installed", util_lib)
    except subprocess.CalledProcessError as error:
        error_str = f"Error in installing {util_lib}\n{error.stderr}*** HINT: Please contact ConTest Team"
        contest_asserts.fail(error_str)
    # pylint: disable=broad-exception-caught
    except Exception as error:
        error_str = f"Error in installing {util_lib}\nError: {error}\n*** HINT: Please contact ConTest Team"
        contest_asserts.fail(error_str)
