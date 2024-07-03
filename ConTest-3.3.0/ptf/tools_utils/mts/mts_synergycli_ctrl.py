"""
    Copyright 2021 Continental Corporation

    :file: mts_synergycli_ctrl.py
    :platform: Windows
    :synopsis:
        This module contains APIs to control MTS using MTS synergycli.com.
        Synergycli.com can start recording, stop recording, collect status of the recording
        and retrieve the recording statistics without opening the MTS Measapp.exe.

    :author:
        - G. Ganga Prabhakar <ganga.prabhakar.guntamukkala@continental-corporation.com>
"""

# disabling all pylint and flake8 checks as this file is just for backward compatibility import
# pylint: disable-all
# flake8: noqa
from contest_mts.mts.mts_synergycli_ctrl import MTSSynergyCli
