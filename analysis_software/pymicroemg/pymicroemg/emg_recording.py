#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A set of classes for representing EMG recordings

@author: Gabrielle
"""
# TODO: add class, method docstrings (see numpy, google, pep8 styles)
# TODO: consider making each class a separate file

import os # see pathlib as alternative for 
import numpy as np
import intanutil.header as intan_header

class EMGFiles:
    '''
    EMG recording files.
    
    File format documentation:
    https://intantech.com/files/Intan_RHD2000_data_file_formats.pdf
    We use the "One File Per Channel" format (pg. 10)
    
    Intan provides Python software for reading RHD header files:
    https://intantech.com/downloads.html?tabSelect=Software&yPos=212
    
    
    '''
    
    def __init__(self, emg_dir):
        # initialise
        
        
        self.emg_dir = emg_dir;
        self.header_fname = 'info.rhd'
        
        # Get names of files from amplifier channels, which contain the EMG data
        self._get_chan_fnames()
    
    def _get_chan_fnames(self):
        # get channel file names (amplifier channels only)
        
        # TODO: generalise for other chan_types? depends if other files needed
        # TODO: add check that channel name numbers go from 0 to n channels
        # Note: assumes channels are not renamed/relabelled during recording

        chan_prefix = 'amp' # recorded data is from amplifier channels
        chan_fnames = [f for f in os.listdir(self.emg_dir) if f.startswith(chan_prefix)]
        chan_fnames.sort() # order by channel name to ensure imported in the correct order
        
        self.chan_fnames = chan_fnames
        
    def read_header(self):

        # read header file (creates dict)
        
        # Full path to header file
        header_path = os.path.join(self.emg_dir, self.header_fname)

        # Load header file as dictionary using intanutils header module
        with open(header_path, 'rb') as fid:
            emg_header = intan_header.read_header(fid)
            
        return emg_header    
        
    def load_emg_data(self):
        # load emg time series data; creates instance of EMGData class
        
        # Multiplier to convert from Intan units to microvolts
        INTAN2uV = 0.195
      
        # Get number of channels ( = number of files)
        n_chan = len(self.chan_fnames)
        
        # Get number of samples (assume same across all channels)
        # TODO: consider adding check that number of samples is the same for all files
        chan_path = os.path.join(self.emg_dir, self.chan_fnames[0])
        finfo = os.stat(chan_path)
        n_samples = finfo.st_size // 2 # int16 data --> 2 bytes per sample
        
        # Create n_chan x n_samples numpy array for storing channel time series
        emg_ts = np.zeros((n_chan, n_samples))
        
        # Load data
        for i in range(n_chan):
            chan_path = os.path.join(self.emg_dir, self.chan_fnames[i])
            with open(chan_path, 'rb') as fid:
                emg_ts[i,:] = np.fromfile(chan_path, dtype=np.int16, 
                                           count=n_samples)

        # Convert to microvolts
        emg_ts *= INTAN2uV
        
        # Load header for additional attributes to save with time series data 
        # (e.g., sampling frequency)
        emg_header = self.read_header()
        
        # Get channel names by removing file extensions from chan_fnames
        chan_names = [os.path.splitext(f)[0] for f in self.chan_fnames]

        # Create EMGData object with EMG time series and associated metadata
        emg_data = EMGData(emg_ts=emg_ts, 
                           fs=emg_header['sample_rate'], 
                           chan_names=chan_names)
        
        return emg_data
        
class EMGData:
    
    def __init__(self, emg_ts, fs, chan_names):
        # initialise (time series, sampling frequency, and channel names)
        # TODO: add check that length of channel names matches ts dimensions
        # TODO: reorder channels (emg_ts and chan_names)
        
        self.n_chan, self.n_samples = emg_ts.shape
        
        '''
        # re-order channels to match electrode design (TODO)
        match self.n_chan:
            case 32:

            case 64:

            case _:
                # throw error - only 32 or 64 channels
        '''
        # TODO: reorder emg_ts and chan_names
        
        self.emg_ts = emg_ts 
        self.fs = fs
        
        self.chan = EMGChannels(chan_names) 
    
    '''
    
    channels (object)
    bandpass filter (none)
    removemains (false)
   
    methods:
    remove mains noise
    bandpass filter
    detect low amplitude channels
    detect high frequency noise
    mark bad channels (based on visual inspection)
    
    
    plot (staggered vertically)
    '''

class EMGChannels:
    
    def __init__(self, chan_names):
        self.chan_names = chan_names
    
    #def get_chan_xy(self):
        # get channel xy coordinates based on number of channels 
        
        
    # names
    # x,y coordinates
    
    # low quality (automatic) 
    # low quality (visual inspection)
