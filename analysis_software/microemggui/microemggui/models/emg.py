#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Models for EMG data for EMG data analysis.

Note: does not use Qt classes for model/view framework. Purpose is to provide an
interface to pymicroemg data classes for EMG data:
    - EMGData child classes (EMGDataRaw/EMGDataPreprocessed)
"""

from pymicroemg.emg_data_preproc import EMGDataPreproc
from pymicroemg.emg_data_raw import EMGDataRaw


class EMGDataModel:
    """
    Model for EMG data. Used as an interface between the pymicroemg data classes and the
    microemggui.
    Can be used to model raw or preprocessed EMG data (EMGDataRaw or EMGDataPreproc
    classes).

    """

    def __init__(self, emg_data: EMGDataRaw | EMGDataPreproc):
        self.emg_data = emg_data
