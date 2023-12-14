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
import matplotlib.pyplot as plt
import intanutil.header as intan_header
import scipy.signal

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

        self.emg_dir = emg_dir
        self.header_fname = 'info.rhd'

        # Get names of files from amplifier channels, which contain the EMG data
        self._get_chan_fnames()

    def _get_chan_fnames(self):
        # get channel file names (amplifier channels only)

        # TODO: generalise for other chan_types? depends if other files needed
        # TODO: add check that channel name numbers go from 0 to n channels
        # Note: assumes channels are not renamed/relabelled during recording

        chan_prefix = 'amp'  # recorded data is from amplifier channels
        chan_fnames = [f for f in os.listdir(
            self.emg_dir) if f.startswith(chan_prefix)]
        chan_fnames.sort()  # order by channel name to ensure imported in the correct order

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
        self.fs = fs

        # Compute duration of EMG segment
        self.emg_dur = self.n_samples/self.fs

        # Reorder channels (in emg_ts and chan_names) based on electrode design
        # Will make it easier to set x,y coordinates
        sort_idx = self._reorder_chan_idx()
        self.emg_ts = emg_ts[sort_idx, :]
        chan_names = [chan_names[i] for i in sort_idx]
        self.chan = EMGChannels(chan_names)

        # TODO: are different channel names needed after the re-ordering?

        # Initial preprocessing settings (none)
        self.filtered = False
        self.filter_settings = {}
        
    def _reorder_chan_idx(self):
        # indices for reordering channels


        # Indices depend on the electrode design, which can be determined by
        # they number of channels.
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

    def get_emg_t(self):
        # Creates time vector from 1/fs to emg_dur (useful for plots)
        # Not stored as an attribute (for now) to conserve memory
        emg_t = np.arange(1, self.n_samples+1)/self.fs
        return emg_t

    def plot_emg_ts(self, start_t=0, stop_t=None,
                    offset=1000, ax=None, lw=0.5, figsize=(7, 7),
                    yticklabel_size=6, xticklabel_size=8):
        # plot multivariate time series
        # TODO: put offset in terms of gain (at least for GUI)
        # TODO: design alterations (e.g., default colors and color options)

        # default end (stop) time is the segment's duration
        if stop_t is None:
            stop_t = self.emg_dur
        else:
            # confirm that end (stop) time is not longer than segment duration
            assert stop_t <= self.emg_dur, (
                'The end of the time range, stop_t, must be less than or '
                f'equal to the duration of the segment, {self.emg_dur} seconds'
            )

        # confirm that start time is before stop time
        assert start_t < stop_t, (
            'The start of the time range, start_t, must be less than the end '
            'of the time range, stop_t'
        )

        # create new figure with specified size if no axis provided
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = None

        # time vector for x axis
        emg_t = self.get_emg_t()

        # get indices corresponding to requested time segment
        plot_idx = np.arange(np.round(start_t*self.fs),
                             np.round(stop_t*self.fs))
        plot_idx = plot_idx.astype('int')

        # plot each channel's signal, staggered by the specified offset
        for i in range(self.n_chan):
            ax.plot(emg_t[plot_idx], self.emg_ts[i, plot_idx] - offset*i,
                    lw=lw)

        # channel labels
        chan_y = np.arange(0, self.n_chan*offset*-1, offset*-1)
        ax.set_yticks(chan_y)
        ax.set_yticklabels(self.chan.chan_names)
        ax.tick_params(axis='y', which='major', labelsize=yticklabel_size)

        # x axis labels and font size
        ax.set_xlabel('time (seconds)')
        ax.tick_params(axis='x', which='major', labelsize=xticklabel_size)

        return fig, ax

    def butterworth_filter(self, cutoff_freq = None, order = 6, 
                        filter_type = 'bandpass'):
        # TODO: add checks for inputs
        # Note - overwrites original time series, emg_ts
        # zero-phase butterworth filter (default is bandpass)
        
        assert order % 2 == 0, 'The filter order must be an even integer.'
        
        # Only allow filtering once - currently do not have way to create 
        # record of repeated filters. 
        # If need to change filter settings, load and filter original data.
        if self.filtered:
            raise Exception(
                'The EMG signal has already been filtered - cannot filter again.'
                )
        
        # Default cutoff frequencies 
        # TODO: different defaults depending on filter type
        # may also want to check that frequencies are compatible with sampling frequency
        if cutoff_freq is None:
            cutoff_freq = [500, 2000]
        
        # Design filter
        sos = scipy.signal.butter(N = order//2, Wn = cutoff_freq, 
                                  btype = filter_type, analog = False,
                                  output = "sos", fs = self.fs)
        
        # Filter each channel's signal
        for i in range(self.n_chan):
            self.emg_ts[i,:] = scipy.signal.sosfiltfilt(sos, self.emg_ts[i,:])

        # Save filter settings
        self.filtered = True
        self.filter_settings = {'filter_name': 'Butterworth',
                                'cutoff_freq': cutoff_freq, 
                                'order': order,
                                'filter_type': filter_type}
    
    def compute_pxx(self, window_size):
        # compute power spectral density using Welch's method
        # window size in seconds
        # default overlap (50%) between windows
        # Not stored as attribute since used for exploratory data analysis/
        # visual confirmation of preprocessing - not used for downstream analysis
        
        freq, pxx = scipy.signal.welch(x=self.emg_ts, fs=self.fs,
                                       nperseg=self.fs*window_size, axis=1)
        
        # store output as EMGPxx class
        emg_pxx = EMGPxx(freq=freq, pxx=pxx, chan = self.chan,
                         window_size=window_size)
        
        return emg_pxx
          
    '''
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
        self._get_chan_xy() # x, y coordinates
        
        
    def _get_chan_xy(self):
        # get channel xy coordinates based on number of channels
        # TODO: confirm needle spacing is the same for 32 and 64 channel designs

        # Channel layout (in mm)
        CHAN_SPACING_X = 0.3    # spacing along length (defined as x axis)
        CHAN_SPACING_Y = 0.36   # spacing along width (defined as y axis)
        CHAN_SHIFT_X = 0.3      # value used to shift x axis positions
        
        n_chan = len(self.chan_names)
        
        # First column will be x coordinates (position along length)
        # Second column will be y coordinates (position along width)
        self.chan_xy = np.zeros((n_chan, 2))

        # Set x - evenly spaced, and shifted by CHAN_SHIFT_X
        self.chan_xy[:,0] = np.arange(
            CHAN_SPACING_X, 
            CHAN_SPACING_X*(n_chan+1), 
            CHAN_SPACING_X
            ) + CHAN_SHIFT_X

        # Set y - alternating positive and negative to form zig-zag
        self.chan_xy[:,1] = CHAN_SPACING_Y/2
        self.chan_xy[np.arange(1,n_chan+1,2),1] *= -1
        
        # names
        # low quality (automatic)
        # low quality (visual inspection)

        
class EMGPxx:
    
    def __init__(self, freq, pxx, chan, window_size):
        self.freq = freq
        self.pxx = pxx
        self.chan = chan
        self.window_size = window_size
        self.n_chan = len(self.chan.chan_names)
        
    def plot_pxx(self, start_freq, stop_freq, ax=None, plot_chan=None,
                 figsize=(5,5), lw=0.5):
        
        # Check validity of start and stop frequencies
        assert start_freq < stop_freq, (
            'The first frequency to plot, start_freq, must be less than '
            'the final frequency to plot, stop_freq'
            )
        
        # Check validity of channel to plot
        if plot_chan:
            assert plot_chan <= self.n_chan, (
                f'Cannot plot channel {plot_chan}: the EMG data only contains '
                f'{self.n_chan} channels'
                )
        
        # create new figure with specified size if no axis provided
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = None

        # Find frequencies to plot
        plot_bool = np.all([self.freq >= start_freq, 
                            self.freq <= stop_freq], 
                           axis=0)
        
        # Plot all channels or specified channel
        if plot_chan is None:
            for i in range(self.n_chan):
                ax.plot(self.freq[plot_bool], self.pxx[i,plot_bool],
                        lw=lw)
        else:
            ax.plot(self.freq[plot_bool], self.pxx[plot_chan-1,plot_bool],
                    lw=lw)
            ax.set_title(f'Channel {self.chan.chan_names[plot_chan-1]}')
        
        # Axis labels
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('PSD')
        
    
