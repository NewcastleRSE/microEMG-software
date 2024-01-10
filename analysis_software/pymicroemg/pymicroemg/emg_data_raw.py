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
            correspondings to the signal from one EMG channel.
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
        

    def butterworth_filter(self, cutoff_freq: None|list[float]|float=None,
                           order: int=6, filter_type: str = 'bandpass'):
        '''
        Filters each channel's signal in the EMG time series using a 
        Butterworth filter. See scipy.signal.butter for filter details.
        
        Overwrites the original time series and saves the filter settings as 
        attributes.
        
        Only one filter can only be applied to a given instance of EMGDataRaw.

        Parameters
        ----------
        cutoff_freq : None|list[float]|float, optional
            Filter cutoff frequencies. The default is [500, 200] if filter_type
            is bandpass; otherwise, must be specified.
        order : int, optional
            Filter order - must be even to allow zero-phase filtering. The 
            default is 6.
        filter_type : str, optional
            Filter type - see scipy.signal.butter options. The default is 
            'bandpass'.

        Raises
        ------
        Exception
            Raises exception if the EMG signal has already been filtered.
        
        Exception
            Raises exception if cutoff_freq is not specified when filter_type 
            is not 'bandpass'.

        Returns
        -------
        None.

        '''
        
        assert order % 2 == 0, 'The filter order must be an even integer.'
        
        # Only allow filtering once - currently do not have way to create 
        # record of repeated filters. 
        # If need to change filter settings, load and filter original data.
        # if self.preproc_settings.filtered:
        #     raise Exception(
        #         'The EMG signal has already been filtered - cannot filter again.'
        #         )
        
        # Default cutoff frequencies - only for bandpass filter
        if cutoff_freq is None:
            if filter_type == 'bandpass':
                cutoff_freq = [500, 2000]
            else:
                raise Exception(
                    'Cutoff frequencies cutoff_freq must be specified if '
                    'filter_type is not bandpass'
                    )
        
        # Design filter
        sos = scipy.signal.butter(N = order//2, Wn = cutoff_freq, 
                                  btype = filter_type, analog = False,
                                  output = "sos", fs = self.fs)
        
        # Filter each channel's signal
        for i in range(self.n_chan):
            self.emg_ts[i,:] = scipy.signal.sosfiltfilt(sos, self.emg_ts[i,:])

        # # Save filter settings
        # self.preproc_settings.filtered = True
        # self.preproc_settings.filter_settings = {
        #     'filter_name': 'Butterworth',
        #     'cutoff_freq': cutoff_freq, 
        #     'order': order,
        #     'filter_type': filter_type
        #     }
        
        

        
    
