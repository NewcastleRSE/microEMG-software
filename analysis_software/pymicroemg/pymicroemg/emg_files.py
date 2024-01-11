#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGFiles, for representing Intan EMG Files.

Each instance corresponds to the files of one EMG recording.

"""

from __future__ import annotations

import os
import numpy as np

import intanutil.header as intan_header
from pymicroemg.emg_data_raw import EMGDataRaw
from pymicroemg.emg_channels import EMGChannels

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
        self.chan_fnames = self._get_chan_fnames()
        
        # Determine number of channels from number of files
        self.n_chan = len(self.chan_fnames)

    def _get_chan_fnames(self) -> list[str]:
        '''
        Gets the names of the Intan .dat files for all amplifier channels. 
        These files will have the prefix 'amp'.
        
        Note that this method assumes that the channels were not renamed during
        the recording session.

        Returns
        -------
        list[str]
            List of channel file names.

        '''
        # TODO: add check that channel name numbers go from 0 to n channels

        chan_prefix = 'amp'  # recorded data is from amplifier channels
        chan_fnames = [f for f in os.listdir(
            self.emg_dir) if f.startswith(chan_prefix)]
        chan_fnames.sort()  # order by channel name to ensure imported in the correct order

        return chan_fnames

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

    def load_emg_data(self) -> EMGDataRaw:
        '''
        Load the EMG time series data and corresponding attributes from the
        EMG files.

        Returns
        -------
        emg_data : EMGDataRaw
            EMG time series and corresponding attributes.

        '''

        # Multiplier to convert from Intan units to microvolts
        INTAN2uV = 0.195

        # Get number of samples (assume same across all channels)
        # TODO: consider adding check that number of samples is the same for all files
        chan_path = os.path.join(self.emg_dir, self.chan_fnames[0])
        finfo = os.stat(chan_path)
        n_samples = finfo.st_size // 2  # int16 data --> 2 bytes per sample

        # Create n_chan x n_samples numpy array for storing channel time series
        emg_ts = np.zeros((self.n_chan, n_samples))

        # Load data
        for i in range(self.n_chan):
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
        
        # Reorder channels (in emg_ts and intan_chan_names) based on electrode
        # design; will make it easier to set x,y coordinates
        sort_idx = self._reorder_chan_idx()
        emg_ts = emg_ts[sort_idx, :]
        intan_chan_names = [intan_chan_names[i] for i in sort_idx]
        
        # Create channels object for storing channel info
        chan = EMGChannels(intan_chan_names)
        
        # Label segment of original recording that the time series comes from.
        # (-inf, inf) indicates that the time series corresponds to the entire 
        # recording 
        segment_of_recording = np.array((-1*np.inf, np.inf))

        # Create EMGDataRaw object with EMG time series and associated metadata
        emg_data = EMGDataRaw(
            emg_ts = emg_ts, 
            fs = emg_header['sample_rate'], 
            chan = chan, 
            segment_of_recording = segment_of_recording
        )

        return emg_data

    def _reorder_chan_idx(self) -> npt.NDArray[np.int64]:
        '''
        Create indices for reordering channels so that the channel order 
        corresponds to their spatial layout.
        
        Channel order is determined by the electrode design, which varies 
        depending on the number of channels. Only 32 and 64 channel designs are
        provided.

        Raises
        ------
        Exception
            Raises exception if the number of channels is not 32 or 64.

        Returns
        -------
        sort_idx : 1D numpy NDArray[np.int64]
            Indices for reordering channels.

        '''

        # Indices depend on the electrode design, which can be determined by
        # the number of channels.
        match self.n_chan:
            case 32:
                
                sort_idx = np.zeros(self.n_chan).astype(int)

                # even indices are descending from 15 to 0
                sort_idx[np.arange(0, self.n_chan, 2)] = np.arange(
                    (self.n_chan/2)-1, -1, -1
                )

                # odd indices are ascending from 16 to 31
                sort_idx[np.arange(1, self.n_chan, 2)] = np.arange(
                    (self.n_chan/2), self.n_chan
                )
            case 64:
                
                # first quarter is descending from 15 to 0
                idx1 = np.arange(self.n_chan//4 - 1, -1, -1)

                # second quarter + 2 channels is ascending starting at 17,
                # with 2 subtracted from odd indices
                # (e.g., 17 16 19 18...)
                idx2 = np.arange(self.n_chan//4 + 1, self.n_chan//2 + 3)
                idx2[np.arange(1, len(idx2), 2)] = (
                    idx2[np.arange(1, len(idx2), 2)] - 2
                )

                # last half - 2 channels is descending from 63 to 34
                idx3 = (
                    np.arange(self.n_chan - 1, self.n_chan//2 + 1, -1)
                )

                # concatenate together to form full set of indices
                sort_idx = np.concatenate((idx1, idx2, idx3))
                
            case _:
                raise Exception(
                    f'The EMG recording has {self.n_chan} channels; only 32 or'
                    '64 channel recordings are allowed.'
                )
        
        return sort_idx  
