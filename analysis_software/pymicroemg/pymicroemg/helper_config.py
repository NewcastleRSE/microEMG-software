#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper functions for getting config settings/info.
"""

import os


def get_recording_path_and_id(recording_num: int) -> (str, str):
    """
    Get an EMG recording's path and string ID using a numeric label.

    Parameters
    ----------
    recording_num : int
        Numeric label for the recording (arbitrarily assigned). Current options are 0 to
        1.

    Raises
    ------
    ValueError
        Raised if recording number is not a valid option (no recordings with that
        numeric label).

    Returns
    -------
    (str, str)
        Path to recording data and string ID.

    """
    data_dir = "recordings"
    chan64_dir = "64-channel"

    if recording_num == 0:
        recording_path = os.path.join(data_dir, chan64_dir, "Stuart_E2", "raw")
        recording_id = "Stuart_E2"
    elif recording_num == 1:
        recording_path = os.path.join(
            data_dir,
            chan64_dir,
            "Stuart_RVI_64CH-00_Right TA_Exp_1",
            "Stuart_RVI_64CH-00_Right TA_Exp_1_161104_142040",
        )
        recording_id = "Stuart RVI Exp 1"
    else:
        raise ValueError("Invalid recording number")

    return recording_path, recording_id
