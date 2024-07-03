"""
    Copyright 2020 Continental Corporation

    :file: common_utils.py
    :platform: Windows, Linux
    :synopsis:
        Script containing some common utilities which can be used for gui and non-gui purposes

    :author:
        - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
"""

import logging


from gui.gui_utils.project_config_handler import ProjectConfigHandler

LOG = logging.getLogger('COMMON')


def store_cfg_data(cfg_file=None, new_base_location=None, no_of_loops=None):
    """
    Function to load contest configuration file, extracting paths, storing paths

    :param string cfg_file: Configuration file given from ui or via command line argument
    :param string new_base_location: If user mentioned a new base location via command line argument
    :param int no_of_loops: No of times the test cases to run given from command line argument
    :return: returns back the 'ProjectConfigHandler' object
    :rtype: object
    """
    user_cfg = ProjectConfigHandler(cfg_file)
    LOG.info("Data read from configuration file")
    # assign no of loops to user configuration.
    # Checking no_of_loops is not None
    if no_of_loops is not None:
        user_cfg.num_loops = no_of_loops
        LOG.info("Read No. of Iterations")
    if new_base_location:
        user_cfg.base_path = new_base_location
        LOG.info("Locations changed to base location given via command line")
        LOG.info("Custom base location: %s", new_base_location)
    # throw back 'ProjectConfigHandler' object
    return user_cfg
