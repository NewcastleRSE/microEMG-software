#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper functions for getting config settings/info for the microEMG analysis.
"""

import os
import sys
from importlib.resources import files, as_file


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
    # Resolve demo recording data from the package data directory where possible.
    # When running under PyInstaller, data files are extracted to sys._MEIPASS.
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running as PyInstaller bundle: expect package files to be under _MEIPASS/pymicroemg/...
        data_dir = os.path.join(sys._MEIPASS, "pymicroemg", "data", "recordings")
    else:
        # Prefer importlib.resources so this also works for installed packages
        try:
            pkg_path = files("pymicroemg").joinpath("data", "recordings")
            with as_file(pkg_path) as p:
                data_dir = os.fspath(p)
        except Exception:
            # Fallback to locating the package data relative to this file
            pkg_root = os.path.dirname(__file__)
            data_dir_candidate = os.path.join(pkg_root, "data", "recordings")
            if os.path.exists(data_dir_candidate):
                data_dir = data_dir_candidate
            else:
                raise FileNotFoundError(
                    "Packaged demo data not found. Ensure 'pymicroemg/data/recordings/64-channel/demo1/' is present"
                )

    chan64_dir = os.path.join(data_dir, "64-channel")

    if recording_num == 0:
        # Prefer the packaged demo location if present
        demo_candidate = os.path.join(chan64_dir, "demo1")
        if os.path.exists(demo_candidate):
            recording_path = demo_candidate
            recording_id = "demo1"
        else:
            raise ValueError(
                "Demo recording not found in package data; ensure 'pymicroemg/data/recordings/64-channel/demo1/' is present"
            )
    else:
        raise ValueError("Invalid recording number")

    return recording_path, recording_id
