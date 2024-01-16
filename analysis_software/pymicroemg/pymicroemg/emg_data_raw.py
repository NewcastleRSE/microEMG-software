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

    def __init__(self, 
                 emg_ts: npt.NDArray[np.float64], 
                 fs: float, 
                 chan: EMGChannels,
                 segment_of_recording: npt.NDArray[np.float64]):
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

        Returns
        -------
        None.

        '''
        super().__init__(emg_ts, fs, chan, segment_of_recording)
        

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
        
        
        # Future preprocessing steps to be added...
        # TODO: add mains removal
        
        # Create EMGDataPreproc object with preprocessed time series and
        # associated metadata
        emg_data_preproc = EMGDataPreproc(emg_ts, self.fs, self.chan, 
                                          self.segment_of_recording, 
                                          preproc_settings)
        
        return emg_data_preproc
    
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


    def remove_mains_noise(self, emg_ts, freq_remove = 50, n_win_avg = 51):
        # Remove mains noise (including harmonics)
        # TODO: documentation

        # Check that number of windows used to average noise is odd.
        # Allows time period used to estimate noise to be centred around the window that is being denoised.
        if n_win_avg%2 == 0:
            raise ValueError(
                'The number of windows used to estimate the noise signal, n_win_avg, must be odd.'
                )

        # Check that sampling frequency is an integer multiple of the frequency to be removed
        if self.fs%freq_remove != 0:
            raise ValueError(
                'The time series sampling frequency must be an integer multiple of the frequency to remove, freq_remove'
                )

        # Number of samples per cycle of the frequency to remove, which determines the 
        # window size. Will be 20 ms when the frequency to remove is 50 Hz.
        # Can convert to integer since we have confirmed that the sampling frequency 
        # is a multiple of freq_remove.
        n_samples_per_win = int(self.fs/freq_remove)

        # Determine number of complete windows in time series.
        n_win = self.n_samples//n_samples_per_win

        # Trim partial window from data
        emg_ts = emg_ts[:, 0:n_win * n_samples_per_win]

        # Start and stop of n_win_avg windows (inclusive endpoints) to use to estimate mains noise.
        # First,  center around window to be denoised.
        start_win = np.arange(0,n_win) - n_win_avg//2
        stop_win = np.arange(0,n_win) + n_win_avg//2 

        # Second, adjust indices at end of time series - instead use nearest n_win_avg windows.
        adjust_idx = start_win < 0              # start indices before first time window
        start_win[adjust_idx] = 0
        stop_win[adjust_idx] = n_win_avg - 1
        adjust_idx = stop_win > n_win  - 1      # stop indices after last time window
        start_win[adjust_idx] = (n_win - 1) - n_win_avg + 1
        stop_win[adjust_idx] = n_win - 1

        # Estimate and remove noise in each recording channel 
        for i in range(self.n_chan):
            
            # Extract channel signal and reshape to form windows (one window per row)
            chan_ts = np.reshape(emg_ts[i,:], (n_win, n_samples_per_win))
            
            # Copy for holding original signal (needed to compute noise) 
            chan_ts_original = chan_ts.copy()
            
            # For each window, estimate noise from surrounding windows; remove noise from signal.
            for w in range(n_win):
                noise_signal = np.mean(chan_ts_original[start_win[w]:(stop_win[w]+1)], axis = 0)
                chan_ts[w,:] -= noise_signal
            
            emg_ts[i,:] = np.reshape(chan_ts, (1, n_win*n_samples_per_win))
        
        return emg_ts

        
    
