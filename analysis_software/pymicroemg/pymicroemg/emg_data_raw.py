#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGDataRaw for representing raw (not preprocessed) EMG data.

Inherits from the class EMGData.

Used to perform initial preprocessing steps and visualisations. 

"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt
import scipy.signal
from typing import Union

from pymicroemg.emg_data import EMGData
from pymicroemg.emg_channels import EMGChannels
from pymicroemg.emg_pxx import EMGPxx
from pymicroemg.emg_preproc_settings import EMGPreprocSettings
from pymicroemg.emg_data_preproc import EMGDataPreproc

class EMGDataRaw(EMGData):
    '''
    Class for representing raw EMG times series data as a multivariate time 
    series.
    
    Inherits from EMGData.
    
    Methods to add:
    remove mains noise
    detect low amplitude channels
    detect high frequency noise
    mark bad channels (based on visual inspection)

    '''

    def __init__(self, emg_ts: npt.NDArray[np.float64], fs: float, 
                 chan: EMGChannels,
                 segment_of_recording: npt.NDArray[np.float64],
                 preproc_settings: None|EMGPreprocSettings=None):
        '''
        Initialise EMGDataRaw object.

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
        preproc_settings : None|EMGPreprocSettings, optional
            Object containing the preprocessing settings. The default is None
            (e.g., for raw data that has not been preprocessed).

        Returns
        -------
        None.

        '''
        super().__init__(emg_ts, fs, chan, segment_of_recording,
                         preproc_settings)
        

    def preprocess(self, preproc_settings) -> EMGDataPreproc:
        # Creates preprocessed EMG data (EMGDataPreproc object) by applying 
        # preprocessing settings to raw EMG data
        
        # Deep copy of EMG time series so that original time series is retained
        emg_ts = self.emg_ts.copy()
        
        # Apply Butterworth filter
        if preproc_settings.butterworth_filter:
            config = preproc_settings.butterworth_filter_settings
            emg_ts = self._butterworth_filter(emg_ts, 
                                              config['cutoff_freq'],
                                              config['order'],
                                              config['filter_type'])
        # TODO: create EMGDataPreproc object from new time series and relevant EMGDataRaw attributes
        # TODO: remove preproc_settings attribute from EMGData and EMGDataRaw
        
        
    def _butterworth_filter(self, emg_ts: npt.NDArray[np.float64],
                            cutoff_freq: None|list[float]|float=None,
                            order: int=6, filter_type: str = 'bandpass'
                            ) -> npt.NDArray[np.float64]:
        '''
        Filters each channel's signal in the EMG time series using a 
        Butterworth filter. See scipy.signal.butter for filter details.
        
        Validity of filter settings are checked when they are added to a 
        PreprocSettings object in preparation for preprocessing.
        
        The time series is not passed as an attribute so that the original, raw
        time series is retained in the EMGDataRaw object.
        
        Parameters
        ----------
        emg_ts : npt.NDArray[np.float64]
            2D array containing the multivariate EMG time series. Each row
            corresponds to the signal from one EMG channel.
        cutoff_freq : None|list[float]|float, optional
            Filter cutoff frequencies. The default is [500, 200] if filter_type
            is bandpass; otherwise, must be specified.
        order : int, optional
            Filter order - must be even to allow zero-phase filtering. The 
            default is 6.
        filter_type : str, optional
            Filter type - see scipy.signal.butter options. The default is 
            'bandpass'.
        
        Returns
        -------        
        emg_ts : npt.NDArray[np.float64]
            2D array containing the filtered multivariate EMG time series.

        '''

        # Design filter
        sos = scipy.signal.butter(N = order//2, Wn = cutoff_freq, 
                                  btype = filter_type, analog = False,
                                  output = "sos", fs = self.fs)
        
        # Filter each channel's signal
        for i in range(self.n_chan):
            emg_ts[i,:] = scipy.signal.sosfiltfilt(sos, emg_ts[i,:])
            
        return emg_ts


        
        

        
    
