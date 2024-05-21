#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper functions for getting config settings/info.
TODO: consider creating class for saving recording info, esp. if add additional
features (e.g., bad channels or plot settings)
"""

import os


# Data that can be used for demos/testing
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


# Control data
def get_control_recording_path_and_id(recording_num: int) -> (str, str):
    """
    Get a control EMG recording's path and string ID using a numeric label.

    Parameters
    ----------
    recording_num : int
        Numeric label for the recording (arbitrarily assigned). Current options are 1 to
        5.

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

    if recording_num == 1:
        recording_path = os.path.join(data_dir, chan64_dir, "Stuart_E2", "raw")
        recording_id = f"Control Recording {recording_num}"

    elif recording_num == 2:
        recording_path = os.path.join(data_dir, chan64_dir, "S1_LTA_RVI_1", "raw")
        # recording ids are specified separately for each so can add case-specific
        # text
        recording_id = f"Control Recording {recording_num}"

    elif recording_num == 3:
        recording_path = os.path.join(
            data_dir,
            chan64_dir,
            "EE_TA_1",
            "S3_RVI_64CH-A5_Right TA_Session3",
            "S3_RVI_64CH-A5_Right TA_Session3_170413_151936",
        )
        recording_id = f"Control Recording {recording_num}"

    elif recording_num == 4:
        recording_path = os.path.join(
            data_dir, chan64_dir, "EE_TA_2", "EE_TA_2_150320_102808"
        )
        recording_id = f"Control Recording {recording_num}"

    elif recording_num == 5:
        recording_path = os.path.join(
            data_dir, chan64_dir, "EE_TA_3", "EE_TA_3_150320_105822"
        )
        recording_id = f"Control Recording {recording_num}"

    else:
        raise ValueError("Invalid recording number")

    return recording_path, recording_id
