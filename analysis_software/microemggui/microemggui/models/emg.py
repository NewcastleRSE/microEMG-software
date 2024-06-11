#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Models for EMG data for EMG data analysis.

Note: does not use Qt classes for model/view framework. Purpose is to provide an
interface to pymicroemg data classes for EMG data:
    - EMGData child classes (EMGDataRaw/EMGDataPreprocessed)
"""

from __future__ import annotations

from pymicroemg.emg_data_preproc import EMGDataPreproc
from pymicroemg.emg_data_raw import EMGDataRaw
from pymicroemg.emg_preproc_settings import EMGPreprocSettings


# TODO: consider creating abstract base class if any shared methods for EMG models


class EMGDataRawModel:
    """
    Model for raw EMG data. Used as an interface between the pymicroemg data class,
    EMGDataRaw, and the GUI.

    """

    def __init__(self, emg_data: EMGDataRaw):
        self.emg_data = emg_data

    def apply_preproc(self, preproc_settings: EMGPreprocSettings) -> EMGDataPreprocModel:
        # Apply preprocessing settings to EMG data and return model for preprocessed
        # EMG data.

        emg_data_preproc = self.emg_data.preprocess(preproc_settings)
        emg_preproc_model = EMGDataPreprocModel(emg_data_preproc)
        return emg_preproc_model


class EMGDataPreprocModel:
    """
    Model for preprocessed EMG data. Used as an interface between the pymicroemg data
    class, EMGDataPreproc, and the GUI.

    """

    def __init__(self, emg_data: EMGDataPreproc):
        self.emg_data = emg_data
