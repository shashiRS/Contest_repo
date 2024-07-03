"""
    Copyright 2020 Continental Corporation

    :file: general_config.py
    :platform: Windows
    :synopsis:
        Generic TAF configuration

    :author:
        - Berger, Andras (uib44246) <andras.berger@continental-corporation.com>
"""
import os

# TAF Configuration that is the same for all projects, ported from Robot
GENERAL_CONFIG = dict(
    WORKSPACE=os.environ["WORKSPACE"] if "WORKSPACE" in os.environ else os.path.join(
        os.path.dirname(__file__), "..", "..", ".."),
    REFLASH=False,
    NIGHTLY=True,

    # Taken from the environment
    RESYNCED=[key.upper() for key in ["APPL", "DPU", "BAT"]
              if key in os.environ and os.environ[key].lower() == 'true'],

    # Relative to workspace
    LAST_SUCCESSFUL_COMBINATION="Last_Successful_Combination",
    TEST_ENV_PATH="05_Testing\\05_Test_Environment",
    CANOE_PATH="05_Testing\\05_Test_Environment\\CANOE",
    TRACE32_PATH="05_Testing\\05_Test_Environment\\TRACE32",
    AUTOMATION_UTILS_PATH="05_Testing\\06_Test_Tools\\Automation_Utils",

    # Relative to CANOE_PATH
    CANOE_REPORT_DIR="06_Project\\report",
    A2L_PARSER_PATH="00_Ext_Tools\\A2L_Parser",
    A2L_INIS_DIR="06_Project\\a2l\\inis",
    XML_TESTMODULE_PARSER_PATH="00_Ext_Tools\\xml_Testmodul_Parser",
    XML_TESTMODULE_PARSER_ARCHIVE="xml_Testmodul_Parser.zip",
    XML_TESTMODULE_PARSER_EXE="xml_Testmodul_Parser.exe",
    EXT_TOOLS_SETTINGS="06_Project\\cfg\\Cfg_ExtTools.ini",
    EMPTY_TXT_PATH="",
)
