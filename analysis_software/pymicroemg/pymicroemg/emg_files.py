#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class for representing EMG Files

@author: Gabrielle
"""

from __future__ import annotations

import os
import numpy as np

import intanutil.header as intan_header
from pymicroemg.emg_recording import EMGData 

class EMGFiles:
    '''
    EMG recording files.

    File format documentation:
    https://intantech.com/files/Intan_RHD2000_data_file_formats.pdf
    We use the "One File Per Channel" format (pg. 10)

    Intan provides Python software for reading RHD header files:
    https://intantech.com/downloads.html?tabSelect=Software&yPos=212


    '''

    def __init__(self, emg_dir: str):
        '''
        Initialise EMGFiles object.

        Parameters
        ----------
        emg_dir : str
            Directory (including path to directory) containing Intan recording 
            outputs. Must include amplifier .dat files and a header file 
            'info.rhd'.

        Returns
        -------
        None.

        '''
        
        self.emg_dir = emg_dir
        self.header_fname = 'info.rhd'

        # Get names of files from amplifier channels, which contain the EMG data
        self._get_chan_fnames()

    def _get_chan_fnames(self):
        '''
        Gets the names of the Intan .dat files for all amplifier channels and
        adds the file names as an attribute. These files will have the prefix 
        'amp'.
        
        Note that this method assumes that the channels were not renamed during
        the recording session.

        Returns
        -------
        None.

        '''
        # TODO: add check that channel name numbers go from 0 to n channels

        chan_prefix = 'amp'  # recorded data is from amplifier channels
        chan_fnames = [f for f in os.listdir(
            self.emg_dir) if f.startswith(chan_prefix)]
        chan_fnames.sort()  # order by channel name to ensure imported in the correct order

        self.chan_fnames = chan_fnames

    def read_header(self) -> dict:
        '''
        Reads the Intan header file 'info.rhd' using the intanutil package 
        provided by Intan.

        Returns
        -------
        emg_header : dict
            Dictionary of all information contained in the Intan header file.

        '''

        # Full path to header file
        header_path = os.path.join(self.emg_dir, self.header_fname)

        # Load header file as dictionary using intanutils header module
        with open(header_path, 'rb') as fid:
            emg_header = intan_header.read_header(fid)

        return emg_header

    def load_emg_data(self) -> EMGData:
        '''
        Load the EMG time series data and corresponding attributes from the
        EMG files.

        Returns
        -------
        emg_data : EMGData
            EMG time series and corresponding attributes.

        '''

        # Multiplier to convert from Intan units to microvolts
        INTAN2uV = 0.195

        # Get number of channels ( = number of files)
        n_chan = len(self.chan_fnames)

        # Get number of samples (assume same across all channels)
        # TODO: consider adding check that number of samples is the same for all files
        chan_path = os.path.join(self.emg_dir, self.chan_fnames[0])
        finfo = os.stat(chan_path)
        n_samples = finfo.st_size // 2  # int16 data --> 2 bytes per sample

        # Create n_chan x n_samples numpy array for storing channel time series
        emg_ts = np.zeros((n_chan, n_samples))

        # Load data
        for i in range(n_chan):
            chan_path = os.path.join(self.emg_dir, self.chan_fnames[i])
            emg_ts[i, :] = np.fromfile(chan_path, dtype=np.int16,
                                       count=n_samples)

        # Convert to microvolts
        emg_ts *= INTAN2uV

        # Load header for additional attributes to save with time series data
        # (e.g., sampling frequency)
        emg_header = self.read_header()

        # Get Intan channel names by removing file extensions from chan_fnames
        intan_chan_names = [os.path.splitext(f)[0] for f in self.chan_fnames]

        # Create EMGData object with EMG time series and associated metadata
        emg_data = EMGData(emg_ts=emg_ts,
                           fs=emg_header['sample_rate'],
                           intan_chan_names=intan_chan_names)

        return emg_data


