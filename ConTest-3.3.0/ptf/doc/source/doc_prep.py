"""
    Copyright Continental Corporation and subsidiaries. All rights reserved.

    :platform: Windows, Linux

    :synopsis:
        File for building ConTest doc
        Execute with following commands command :
        - cd <path_to_this_script>
        - python build_doc.py
"""
# disabling all pylint checks as documentation generation strategy will change heavily in future
# pylint: disable-all

import os
import shutil
import subprocess
import inspect
import sys
import site


CURRENT_WORK_SPACE = os.path.dirname(os.path.realpath(__file__))
# setting ConTest documentation directories
CONTEST_WORK_SPACE = os.path.join(CURRENT_WORK_SPACE, "..", "..")
DOC_BUILD_DIR = os.path.join(CURRENT_WORK_SPACE, "..")
VERIFY_DOC_DIR = os.path.join(DOC_BUILD_DIR, "source", "verify_doc")
API_DOC_DIR = os.path.join(DOC_BUILD_DIR, "source", "api_doc")
GLOBAL_PARAM_DOC_DIR = os.path.join(DOC_BUILD_DIR, "source", "global_param_doc")
BUILD_DIR = os.path.join(DOC_BUILD_DIR, "build")

GLOBAL_PARAM_API_RST = """
.. Global APIs file

Global APIs
===========

.. toctree::
    :maxdepth: 1

    global_param_doc/ptf_utils

"""

TOOL_API_RST = """
.. Tools APIs file

Tool APIs
=========

.. toctree::
    :maxdepth: 1

    api_doc/tools_utils

"""

#
VERIFY_API_RST = """
.. Verification APIs file

Verify APIs
===========

.. toctree::
    :maxdepth: 1

    verify_doc/modules

"""

GLOBAL_PARAM_API_RST_DICT = {"global_params": "ptf.ptf_utils"}


# todo: enter class names with path whose methods extraction is required (for API listing)
TOOL_API_RST_DICT = {
    "ArxmlReader": ["ptf.tools_utils.arxml.arxml_reader", "contest_arxml.arxml.arxml_reader"],
    "Canoe": ["ptf.tools_utils.canoe.canoe", "contest_canoe.canoe"],
    "CarMaker": ["ptf.tools_utils.carmaker.carmaker_utils", "contest_carmaker.carmaker.carmaker_utils"],
    "Chilis": ["ptf.tools_utils.chilis.chilis", "contest_chilis.chilis.chilis"],
    "ConradRlyCtrl": ["ptf.tools_utils.relay_control.conrad_rly", "contest_relay.relay_control.conrad_rly"],
    "Conrad4ChRlyCtrl": ["ptf.tools_utils.relay_control.conrad_4ch_rly", "contest_relay.relay_control.conrad_4ch_rly"],
    "CreateTable": ["ptf.tools_utils.create_table.create_table", "contest_create_table.create_table.create_table"],
    "DbcReader": ["ptf.tools_utils.dbc.dbc_reader", "contest_dbc.dbc.dbc_reader"],
    "DoIP": ["ptf.tools_utils.doip.doip", "contest_doip.doip.doip"],
    "DtsApp": "ptf.tools_utils.dts.dts",
    "DTSsdaApp": ["ptf.tools_utils.dts.dts_sda", "contest_dts.dts.dts_sda"],
    "EDIABAS": ["ptf.tools_utils.ediabas.ediabas", "contest_ediabas.ediabas"],
    "EnvChamber": ["ptf.tools_utils.env_chamber.env_chamber", "contest_env_chamber.env_chamber.env_chamber"],
    "ESys": ["ptf.tools_utils.esys.esys_tool", "contest_esys.esys_tool"],
    "GenSigEval": "ptf.tools_utils.gen_sig_eval.gen_sig_eval",
    "GoepelCan": "ptf.tools_utils.goepel.goepel_can",
    "GoepelCanTp": "ptf.tools_utils.goepel.goepel_can_tp",
    "GoepelCommon": "ptf.tools_utils.goepel.goepel_common",
    "GoepelIO": "ptf.tools_utils.goepel.goepel_io",
    "GoepelLVDS": "ptf.tools_utils.goepel.goepel_lvds",
    "GmPsu240": "ptf.tools_utils.psu_ssp_240.psu_ssp_240",
    "ImageUtils": ["ptf.tools_utils.visu.image.image_utils", "contest_visu.visu.image.image_utils"],
    "Lauterbach": ["ptf.tools_utils.lauterbach.lauterbach", "contest_lauterbach.lauterbach"],
    "MtsCtrl": ["ptf.tools_utils.mts.mts_ctrl", "contest_mts.mts.mts_ctrl"],
    "MTSSynergyCli": ["ptf.tools_utils.mts.mts_synergycli_ctrl", "contest_mts.mts.mts_synergycli_ctrl"],
    "Odis": ["ptf.tools_utils.odis.odis", "contest_odis.odis"],
    "Pico3000A": [
        "ptf.tools_utils.picoscope.pico_3000a.pico_3000a",
        "contest_picoscope.picoscope.pico_3000a.pico_3000a",
    ],
    "PowerControl": ["ptf.tools_utils.gude.power_control", "contest_pwr_ctrls.pwr_ctrls.gude_pwr"],
    "Psu": ["ptf.tools_utils.psu.psu", "contest_psu.psu.psu"],
    "PsuBk168xx": ["ptf.tools_utils.psu_bk_precision.bk_168xx", "contest_psu_bk_precision.bk_168xx"],
    "PSUviaRPC": ["ptf.tools_utils.psu_via_rpc.psu_rpc", "contest_psu_via_rpc.psu_rpc"],
    "RtaUtils": "ptf.tools_utils.rta.rta_mts",
    "RaLib": ["ptf.tools_utils.ralib.ralib_tool", "contest_ralib.ralib.ralib_tool"],
    "SerialComm": ["ptf.tools_utils.serial_util.serial_util", "contest_serial_util.serial_util"],
    "TafHelper": "ptf.tools_utils.taf.taf_helpers",
    "AcrUsbHub3p": ["ptf.tools_utils.acroname.usb_devices", "contest_usb_ctrls.usb_ctrls.acroname"],
    "XcpDownload": ["ptf.tools_utils.xcp_download.xcp_download", "contest_xcp_download.xcp_download.xcp_download"],
    "ZenZefi": ["ptf.tools_utils.zenzefi.zenzefi", "contest_zenzefi.zenzefi.zenzefi"],
}


def run_subprocess(cmd_to_run):
    """
    Method to running a command via subprocess

    :param str cmd_to_run: Command to run via subprocess
    """
    # opening a pipe process for documentation build
    process = subprocess.Popen(
        cmd_to_run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    # start process and fetch process output and error
    output, error = process.communicate()
    # throw back output and error
    return output, error


def create_api_rst_file():
    """
    Function for creating .rst file including tools APIs
    """
    global TOOL_API_RST
    global GLOBAL_PARAM_API_RST

    # extract class names and their paths to create tools api data
    for module_name, module_path in TOOL_API_RST_DICT.items():
        if isinstance(module_path, str):
            if module_path.startswith("ptf"):
                exec("from " + module_path + " import " + module_name)
                module_path = module_path.split("ptf.tools_utils.")[1]
                api_list = [
                    attr
                    for attr in dir(eval(module_name))
                    if not inspect.isfunction(attr) and not (attr.startswith("__") or attr.startswith("_"))
                ]
                module_link = "\n.. _{}: api_doc/tools_utils.{}.html\n".format(module_name, module_path)
                TOOL_API_RST = "{}\n\n{}_\n{}\n\n".format(TOOL_API_RST, module_name, "-" * (len(module_name) + 1))
                tool_api_link = ""
                for api_name in api_list:
                    TOOL_API_RST = "{}\t- {}.{}_\n".format(TOOL_API_RST, module_name, api_name)
                    tool_api_link = "{} \n.. _{}.{}: api_doc/tools_utils.{}.html#tools_utils.{}.{}.{}".format(
                        tool_api_link, module_name, api_name, module_path, module_path, module_name, api_name
                    )
                TOOL_API_RST = TOOL_API_RST + tool_api_link + module_link
        else:
            exec("from " + module_path[0] + " import " + module_name)
            api_list = [
                attr
                for attr in dir(eval(module_name))
                if not inspect.isfunction(attr) and not (attr.startswith("__") or attr.startswith("_"))
            ]
            module_link = "\n.. _{}: api_doc/{}.html\n".format(module_name, module_path[1])
            TOOL_API_RST = "{}\n\n{}_\n{}\n\n".format(TOOL_API_RST, module_name, "-" * (len(module_name) + 1))
            tool_api_link = ""
            for api_name in api_list:
                TOOL_API_RST = "{}\t- {}.{}_\n".format(TOOL_API_RST, module_name, api_name)
                tool_api_link = "{} \n.. _{}.{}: api_doc/{}.html#{}.{}.{}".format(
                    tool_api_link, module_name, api_name, module_path[1], module_path[1], module_name, api_name
                )
            TOOL_API_RST = TOOL_API_RST + tool_api_link + module_link

    with open(os.path.join(DOC_BUILD_DIR, "source", "tool_api_auto.rst"), "w") as outfile:
        outfile.write(TOOL_API_RST)

    # extract class names and their paths to create global params api data
    for module_name, module_path in GLOBAL_PARAM_API_RST_DICT.items():
        exec("from " + module_path + " import " + module_name)
        # preparing list of all APIs in global_params.py file excluding imports etc.
        api_list = list()
        for attr in inspect.getmembers(eval(module_name), inspect.isfunction):
            if (
                attr[1].__module__ == eval(module_name).__name__
                and not attr[0].startswith("clear")
                and not attr[0].startswith("_")
            ):
                api_list.append(attr[0])
        # string for heading link
        module_link = "\n.. _{}: global_param_doc/ptf_utils.{}.html\n".format("GlobalParam", "global_params")
        # rst file header string
        GLOBAL_PARAM_API_RST = "{}\n\n{}_\n{}\n\n".format(
            GLOBAL_PARAM_API_RST, "GlobalParam", "-" * (len(module_name) + 1)
        )
        global_param_api_link = ""
        # loop for adding all APIs sun-headings to main heading and adding their links
        for api_name in api_list:
            GLOBAL_PARAM_API_RST = "{}\t- {}.{}_\n".format(GLOBAL_PARAM_API_RST, "GlobalParam", api_name)
            global_param_api_link = "{} \n.. _{}.{}: global_param_doc/ptf_utils.{}.html#ptf_utils.{}.{}".format(
                global_param_api_link, "GlobalParam", api_name, "global_params", "global_params", api_name
            )
        GLOBAL_PARAM_API_RST = GLOBAL_PARAM_API_RST + global_param_api_link + module_link

    with open(os.path.join(DOC_BUILD_DIR, "source", "global_param_auto.rst"), "w") as outfile:
        outfile.write(GLOBAL_PARAM_API_RST)


def create_verify_api_rst_file():
    """
    Function for creating .rst file including verification APIs
    """

    def prepare_data(module, api_list):
        """
        Local function to prepare verification API data to be included in .rst file

        :param string module: Verification module (contest_asserts, contest_expects)
        :param list api_list: API list of 'module'

        :return: Data in string format to be dumped into .rst file
        :rtype: string
        """
        links = "\n"
        data = "{}_\n{}\n\n".format(module.upper(), "-" * (len(module) + 1))
        for api in api_list:
            if not api[0].startswith("_"):
                data = data + "\t- {}.{}_\n".format(module, api[0])
                links = "{}.. _{}.{}: verify_doc/contest_verify.verify.html#contest_verify.verify.{}.{}\n".format(
                    links, module, api[0], module, api[0]
                )
        links = links + ".. _{}: verify_doc/contest_verify.verify.html#module-contest_verify.{}\n\n".format(
            module.upper(), module
        )
        return data + links

    global VERIFY_API_RST
    # importing verification modules
    from contest_verify.verify import contest_asserts, contest_expects, contest_warn

    # preparing data for 'contest_asserts' and 'contest_expects' modules and including in final data string
    VERIFY_API_RST = VERIFY_API_RST + prepare_data(
        "contest_asserts", inspect.getmembers(contest_asserts, inspect.isfunction)
    )
    VERIFY_API_RST = VERIFY_API_RST + prepare_data("contest_warn", inspect.getmembers(contest_warn, inspect.isfunction))
    VERIFY_API_RST = VERIFY_API_RST + prepare_data(
        "contest_expects", inspect.getmembers(contest_expects, inspect.isfunction)
    )
    # creating verify api .rst file with prepared data
    with open(os.path.join(DOC_BUILD_DIR, "source", "verify_api_auto.rst"), "w") as outfile:
        outfile.write(VERIFY_API_RST)


def generate_global_param_api_call():
    """
    Function for generating command for global params api call

    :return: None
    """
    scripts_folder = os.path.join(CONTEST_WORK_SPACE, "ptf_utils")
    call_str = "sphinx-apidoc -o {} {}".format(GLOBAL_PARAM_DOC_DIR, scripts_folder)
    scripts = os.listdir(scripts_folder)

    for script_name in scripts:
        if ("__" not in script_name) and ("global_params" not in script_name):
            # print(os.path.join(scripts_folder, script_name))
            call_str = call_str + " " + os.path.join(scripts_folder, script_name)

    return call_str + " -d 2 -feMT"


def build_contest_documentation():
    """
    Function for building ConTest documentation.
    """
    # checking if required modules for Sphinx documentation build are installed
    try:
        import sphinx
        import sphinx_rtd_theme

        print(
            "Sphinx found : Version - " + sphinx.__version__,
            "Sphinx rtd theme found : Version - " + sphinx_rtd_theme.__version__,
        )
    except ImportError as error:
        err_str = (
            "Error --> {}\n\nMake sure you have following Python modules installed\n"
            "1. Sphinx\n2. sphinx_rtd_theme\n".format(str(error))
        )
        print(err_str)
        raise error
    # deleting tools API doc and Verify API doc folders if they already exist in order to avoid
    # any errors from previous builds
    if os.path.exists(VERIFY_DOC_DIR):
        print("Deleting Verify Doc folder since it exists already")
        shutil.rmtree(VERIFY_DOC_DIR)
    if os.path.exists(API_DOC_DIR):
        print("Deleting API Doc folder since it exists already")
        shutil.rmtree(API_DOC_DIR)
    if os.path.exists(BUILD_DIR):
        print("Deleting build folder since it exists already")
        shutil.rmtree(BUILD_DIR)
    # create sphinx auto API doc. generator command
    global_param_api_doc_build_cmd = generate_global_param_api_call()
    # create sphinx auto API doc. generator command
    tools_api_doc_build_cmd = "{} -o {} {} ..\\*mfile* -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(CONTEST_WORK_SPACE, "tools_utils"), 2
    )
    canoe_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_canoe"), 2
    )
    relay_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_relay"), 2
    )
    carmaker_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_carmaker"), 2
    )
    env_chamber_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_env_chamber"), 2
    )
    ediabas_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_ediabas"), 2
    )
    esys_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_esys"), 2
    )
    odis_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_odis"), 2
    )
    picoscope_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_picoscope"), 2
    )
    psu_via_rpc_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_psu_via_rpc"), 2
    )
    ralib_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_ralib"), 2
    )
    serial_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_serial_util"), 2
    )
    visu_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_visu"), 2
    )
    zenzefi_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_zenzefi"), 2
    )
    chilis_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_chilis"), 2
    )
    table_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_create_table"), 2
    )
    ltb_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_lauterbach"), 2
    )
    psu_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_psu"), 2
    )
    mts_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_mts"), 2
    )
    psu_bk_tools_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_psu_bk_precision"), 2
    )
    xcp_download_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_xcp_download"), 2
    )
    usb_ctrls_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_usb_ctrls"), 2
    )
    arxml_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_arxml"), 2
    )
    dbc_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_dbc"), 2
    )
    dts_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_dts"), 2
    )
    doip_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_doip"), 2
    )
    pwr_ctrl_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_pwr_ctrls"), 2
    )
    rta_api_doc_build_cmd = "{} -o {} {} -d {} -feMT".format(
        "sphinx-apidoc", API_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_rta"), 2
    )
    # create sphinx auto verify doc. generator command
    verify_doc_build_cmd = "{} -o {} {} -d {} -f".format(
        "sphinx-apidoc", VERIFY_DOC_DIR, os.path.join(site.getsitepackages()[1], "contest_verify"), 2
    )
    # creating .rst file for verification and tool APIs
    create_verify_api_rst_file()
    create_api_rst_file()

    # sphinx build doc. list
    script_doc_list = [
        ["global_params", global_param_api_doc_build_cmd],
        ["tools_utils", tools_api_doc_build_cmd],
        ["tools_utils", canoe_tools_api_doc_build_cmd],
        ["tools_utils", relay_tools_api_doc_build_cmd],
        ["tools_utils", carmaker_tools_api_doc_build_cmd],
        ["tools_utils", env_chamber_tools_api_doc_build_cmd],
        ["tools_utils", ediabas_tools_api_doc_build_cmd],
        ["tools_utils", esys_tools_api_doc_build_cmd],
        ["tools_utils", odis_tools_api_doc_build_cmd],
        ["tools_utils", picoscope_tools_api_doc_build_cmd],
        ["tools_utils", psu_via_rpc_tools_api_doc_build_cmd],
        ["tools_utils", ralib_tools_api_doc_build_cmd],
        ["tools_utils", serial_tools_api_doc_build_cmd],
        ["tools_utils", visu_tools_api_doc_build_cmd],
        ["tools_utils", zenzefi_tools_api_doc_build_cmd],
        ["tools_utils", chilis_tools_api_doc_build_cmd],
        ["tools_utils", table_tools_api_doc_build_cmd],
        ["tools_utils", ltb_tools_api_doc_build_cmd],
        ["tools_utils", psu_tools_api_doc_build_cmd],
        ["tools_utils", mts_tools_api_doc_build_cmd],
        ["tools_utils", psu_bk_tools_api_doc_build_cmd],
        ["tools_utils", xcp_download_api_doc_build_cmd],
        ["tools_utils", arxml_api_doc_build_cmd],
        ["tools_utils", usb_ctrls_api_doc_build_cmd],
        ["tools_utils", dbc_api_doc_build_cmd],
        ["tools_utils", dts_api_doc_build_cmd],
        ["tools_utils", doip_api_doc_build_cmd],
        ["tools_utils", rta_api_doc_build_cmd],
        ["tools_utils", pwr_ctrl_api_doc_build_cmd],
        ["verify_utils", verify_doc_build_cmd],
    ]
    # run doc. commands
    for build_info in script_doc_list:
        # start doc. build
        print(build_info[1])
        output, error = run_subprocess(build_info[1])
        if error:
            # NOTE: This is temporary fix for ignoring a deprecated warning produced by
            # sphinx_rtd_theme module. They module developers have a fix but not in their latest
            # release. Once they do a new release we will remove this fix.
            if "Please insert a <script> tag directly in your theme instead." not in error:
                # error reported by documentation build
                print("Error occurred during " + build_info[0] + " doc. build, see console ...")
                if build_info[0] == "ConTest_Doc":
                    if os.path.exists(os.path.join(DOC_BUILD_DIR, "doc", "build")):
                        shutil.rmtree(os.path.join(DOC_BUILD_DIR, "doc", "build"))
                raise RuntimeError(error)
        else:
            print(output)
            # doc. build was successful
            if build_info[0] == "ConTest_Doc":
                to_open = os.path.join(DOC_BUILD_DIR, "doc", "build", "html", "index.html")
                print("Open " + to_open)
            print("ConTest " + build_info[0] + " Doc. Build Ended")
            print("-" * 100)


def doc_build_pre_steps():
    """
    Doc preparation function
    """
    # introducing an env variable "CONTEST_DOC_BUILDER" for document build support in-case when there is an import
    # error raised which can be ignored for documentation build
    os.environ["CONTEST_DOC_BUILDER"] = "True"
    sys.path.append(os.path.join(CONTEST_WORK_SPACE, ".."))
    sys.path.append(os.path.join(CONTEST_WORK_SPACE, "ptf_utils"))
    build_contest_documentation()
