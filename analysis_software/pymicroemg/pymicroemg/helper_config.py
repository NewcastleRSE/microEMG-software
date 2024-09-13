#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper functions for getting config settings/info for the microEMG analysis.
"""

import os


# microEMG recordings that can be used for demos/testing
def get_recording_path_and_id(recording_num: int) -> tuple[str, str]:
    """
    Get an EMG recording's path and string ID using a numeric label.

    Parameters
    ----------
    recording_num : int
        Numeric label for the recording (arbitrarily assigned). Currently the only
        valid option is 0.

    Raises
    ------
    ValueError
        Raised if recording number is not a valid option (no recordings with that
        numeric label).

    Returns
    -------
    tuple[str, str]
        Path to recording data and string ID.

    """
    data_dir = "recordings"
    chan64_dir = "64-channel"

    if recording_num == 0:
        recording_path = os.path.join(data_dir, chan64_dir, "Stuart_E2", "raw")
        recording_id = "Stuart_E2"
    else:
        raise ValueError("Invalid recording number")

    return recording_path, recording_id
