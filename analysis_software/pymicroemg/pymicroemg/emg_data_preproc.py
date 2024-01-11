#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGDataPreproc for representing preprocessed EMG data.

Inherits from the class EMGData.

Use for downstream analysis of the preprocessed EMG data.

"""
import numpy as np
import numpy.typing as npt

from pymicroemg.emg_data import EMGData
from pymicroemg.emg_channels import EMGChannels
from pymicroemg.emg_preproc_settings import EMGPreprocSettings

class EMGDataPreproc(EMGData):
    '''
    Class for representing preprocessed EMG times series data as a multivariate 
    time series.
    
    Inherits from EMGData.
    
    Methods to add:
    analysis of motor units

    '''

    def __init__(self, 
                 emg_ts: npt.NDArray[np.float64], 
                 fs: float, 
                 chan: EMGChannels,
                 segment_of_recording: npt.NDArray[np.float64],
                 preproc_settings: EMGPreprocSettings):
        '''
        Initialise EMGDataPreproc object.

        Parameters
        ----------
        emg_ts : npt.NDArray[np.float64]
            2D array containing the multivariate EMG time series. Each row
            corresponds to the signal from one EMG channel.
        fs : float
            Sampling frequency (Hz).
        chan : EMGChannels
            EMGChannels object with information about channels, including names
            and locations.
        segment_of_recording : npt.NDArray[np.float64]
            Segment of the original recording that the EMG time series 
            corresponds to, stored as 
            (start time in seconds, stop time in seconds). (-inf, inf) 
            indicates that the time series corresponds to the entire original 
            recording.
        preproc_settings : EMGPreprocSettings
            Object containing the preprocessing settings used to generate the
            preprocessed EMG time series from the raw EMG time series.

        Returns
        -------
        None.

        '''
        super().__init__(emg_ts, fs, chan, segment_of_recording)
        self.preproc_settings = preproc_settings


