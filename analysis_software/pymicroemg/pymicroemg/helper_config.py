#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper functions for getting config settings/info for the microEMG analysis.
"""

import os

from pymicroemg.demo_data import (
    DemoDataMissingError,
    demo_data_exists,
    get_demo_data_dir,
)


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
    DemoDataMissingError
        Raised if the demo recording has not been downloaded. Call
        :func:`pymicroemg.demo_data.download_and_extract_demo` to fetch it,
        or launch the GUI (`microemggui`) and accept the prompt.

    Returns
    -------
    tuple[str, str]
        Path to recording data and string ID.
    """
    if recording_num != 0:
        raise ValueError("Invalid recording number")

    if not demo_data_exists():
        raise DemoDataMissingError(
            "Demo recording not present. Run "
            "`python -c 'from pymicroemg.demo_data import download_and_extract_demo; "
            "download_and_extract_demo()'` to download it, or launch the GUI and "
            "accept the download prompt."
        )

    demo_dir = get_demo_data_dir() / "demo1"
    return os.fspath(demo_dir), "demo1"
