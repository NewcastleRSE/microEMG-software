#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A set of classes for representing EMG recordings

@author: Gabrielle
"""
# TODO: add class, method docstrings (see numpy, google, pep8 styles)
# TODO: consider making each class a separate file
from __future__ import annotations

import os # see pathlib as alternative for
import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt
import scipy.signal
from typing import Union

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
        # TODO: generalise for other chan_types? depends if other files needed
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
        EMGData
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

        # Get channel names by removing file extensions from chan_fnames
        chan_names = [os.path.splitext(f)[0] for f in self.chan_fnames]

        # Create EMGData object with EMG time series and associated metadata
        emg_data = EMGData(emg_ts=emg_ts,
                           fs=emg_header['sample_rate'],
                           chan_names=chan_names)

        return emg_data


class EMGData:

    def __init__(self, emg_ts: npt.NDArray[np.float64], fs: float, 
                 chan_names: list[str]):
        '''
        Initialise EMGData object.

        Parameters
        ----------
        emg_ts : npt.NDArray[np.float64]
            2D array containing the multivariate EMG time series. Each row
            correspondings to the signal from one EMG channel.
        fs : float
            Sampling frequency (Hz).
        chan_names : list[str]
            Channel names that correspond to each row of emg_ts, derived from 
            the channel file names.

        Returns
        -------
        None.

        '''
        # TODO: add check that length of channel names matches ts dimensions

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

    def get_emg_t(self) -> npt.NDArray[np.float64]:
        '''
        Create a vector of the time corresponding to each sample in the EMG
        time series. Time is defined as the number of seconds elapsed since the
        start of the recording. The first time point is defined as 1/Fs, where
        Fs is the sampling frequency, and the last time point is equal to the 
        EMG segment's duration in seconds.

        Returns
        -------
        emg_t : 1D numpy NDArray[np.float64] 
            Vector of the time of each EMG sample, defined as seconds elapsed 
            since the start of the recording.

        '''

        emg_t = np.arange(1, self.n_samples+1)/self.fs
        
        return emg_t

    def plot_emg_ts(self, start_t=0, stop_t=None,
                    offset=1000, ax=None, lw=0.5, figsize=(7, 7),
                    yticklabel_size=6, xticklabel_size=8):
        '''
        Plot the specified segment of the EMG time series, with each channel's
        signal staggered vertically by the specified offset.

        Parameters
        ----------
        start_t : float, optional
            First time point to plot, in seconds. The default is 0.
        stop_t : float, optional
            Last time point to plot, in seconds. The default is the segment's 
            duration.
        offset : float, optional
            Vertical spacing between the EMG signals. Must be positive. The 
            default is 1000.
        ax : matplotlib axes, optional
            Axes in which to plot the figure. If none provided, a new figure is
            generated.
        lw : float, optional
            Linewidth of each signal's line plot. The default is 0.5.
        figsize : tuple, optional
            Figure size in inches (only used if a new figure is created). The 
            default is (7, 7).
        yticklabel_size : float, optional
            Font size of the y-tick labels. The default is 6.
        xticklabel_size : float, optional
            Font size of the x-tick labels. The default is 8.

        Returns
        -------
        fig : matplotlib figure
            Figure handle.
        ax : matplotlib axes
            Axis handle.

        '''
        # TODO: put offset in terms of gain (at least for GUI)
        # TODO: design alterations (e.g., default colors and color options)

        # Default end (stop) time is the segment's duration
        if stop_t is None:
            stop_t = self.emg_dur
        else:
            # Confirm that end (stop) time is not longer than segment duration
            assert stop_t <= self.emg_dur, (
                'The end of the time range, stop_t, must be less than or '
                f'equal to the duration of the segment, {self.emg_dur} seconds'
            )

        # confirm that start time is before stop time
        assert start_t < stop_t, (
            'The start of the time range, start_t, must be less than the end '
            'of the time range, stop_t'
        )
        
        # Offset must be positive to ensure that channels are correctly labelled.
        assert offset > 0, ('The vertical spacing, offset, must be positive')

        # Create new figure with specified size if no axis provided
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = None

        # Time vector for x axis
        emg_t = self.get_emg_t()

        # Get indices corresponding to requested time segment
        plot_idx = np.arange(np.round(start_t*self.fs),
                             np.round(stop_t*self.fs))
        plot_idx = plot_idx.astype('int')

        # Plot each channel's signal, staggered by the specified offset
        for i in range(self.n_chan):
            ax.plot(emg_t[plot_idx], self.emg_ts[i, plot_idx] - offset*i,
                    lw=lw)

        # Channel labels
        chan_y = np.arange(0, self.n_chan*offset*-1, offset*-1)
        ax.set_yticks(chan_y)
        ax.set_yticklabels(self.chan.chan_names)
        ax.tick_params(axis='y', which='major', labelsize=yticklabel_size)

        # x axis labels and font size
        ax.set_xlabel('time (seconds)')
        ax.tick_params(axis='x', which='major', labelsize=xticklabel_size)

        return fig, ax

    def butterworth_filter(self, cutoff_freq: None|list[float]|float=None,
                           order: int=6, filter_type: str = 'bandpass'):
        '''
        Filters each channel's signal in the EMG time series using a 
        Butterworth filter. See scipy.signal.butter for filter details.
        
        Overwrites the original time series and saves the filter settings as 
        attributes.
        
        Only one filter can only be applied to a given instance of EMGData.

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

        # Save filter settings
        self.filtered = True
        self.filter_settings = {'filter_name': 'Butterworth',
                                'cutoff_freq': cutoff_freq, 
                                'order': order,
                                'filter_type': filter_type}
    
    def compute_pxx(self, window_size: float) -> EMGPxx:
        '''
        Computes the power spectral density (PSD) of each channel's signal in
        the EMG time series using Welch's method. See scipy.signal.welch for
        computational details.

        Parameters
        ----------
        window_size : float
            Size of the window to use for Welch's method, in seconds. Windows 
            will overlap 50%.

        Returns
        -------
        EMGPxx
            EMGPxx object containing the PSD, frequencies, and corresponding 
            attributes.

        '''
        
        # Compute PSD
        freq, pxx = scipy.signal.welch(x=self.emg_ts, fs=self.fs,
                                       nperseg=self.fs*window_size, axis=1)
        
        # Store output as EMGPxx class
        emg_pxx = EMGPxx(freq=freq, pxx=pxx, chan = self.chan,
                         window_size=window_size)
        
        # Not stored as an EMGData attribute since not used for downstream 
        # analysis; also allows multiple PSDs to be created at different
        # preprocessing steps.
        return emg_pxx
          
    '''
    removemains (false)
   
    methods:
    remove mains noise
    detect low amplitude channels
    detect high frequency noise
    mark bad channels (based on visual inspection)
    
    '''


class EMGChannels:

    def __init__(self, chan_names: list[str]):
        '''
        Initialise EMGChannels object for modelling EMG channels.

        Parameters
        ----------
        chan_names : list[str]
            List of channel names.

        Returns
        -------
        None.

        '''
        self.chan_names = chan_names
        self._get_chan_xy() # x, y coordinates
        
        
    def _get_chan_xy(self):
        '''
        Get the channel (x, y) coordinates based on the number of channels, 
        which determines the electrode's design.

        Returns
        -------
        None.

        '''
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
    
    def __init__(self, freq: npt.NDArray[np.float64], 
                 pxx: npt.NDArray[np.float64], chan: EMGChannels, 
                 window_size: float):
        '''
        Initialise EMGPxx object for modelling EMG's power spectral density 
        (PSD).

        Parameters
        ----------
        freq : 1D npt.NDArray[np.float64]
            Vector of PSD frequencies.
        pxx : 2D npt.NDArray[np.float64]
            PSD of each channel's signal. Each row corresponds to one channel. 
            Columns correspond to the frequencies in freq.
        chan : EMGChannels
            EMGChannels object for the corresponding EMG channels.
        window_size : float
            Size of window used to compute the PSD using Welch's method.

        Returns
        -------
        None.

        '''
        self.freq = freq
        self.pxx = pxx
        self.chan = chan
        self.window_size = window_size
        self.n_chan = len(self.chan.chan_names)
        
    def plot_pxx(self, start_freq, stop_freq, ax=None, plot_chan=None,
                 figsize=(5,5), lw=0.5):
        '''
        Plot the power spectral density (PSD) of one or all channels. If all
        channels' PSDs are plotted, plots will be overlaid in one figure.

        Parameters
        ----------
        start_freq : float
            Beginning of the frequency range to plot.
        stop_freq : float
            End of the frequency range to plot. If higher than the frequencies
            in the PSD, all frequencies will be plotted.
        ax : matplotlib axes, optional
            Axes in which to plot the figure. If none provided, a new figure is
            generated.
        plot_chan : int, optional
            Channel to plot (counting from 1). The default is None, in which 
            case all channels' PSDs are plotted.
        figsize : tuple, optional
            Figure size in inches (only used if a new figure is created). The 
            default is (5,5).
        lw : float, optional
            Linewidth of each PSD's line plot. The default is 0.5.

        Returns
        -------
        fig : matplotlib figure
            Figure handle.
        ax : matplotlib axes
            Axis handle.

        '''
        
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
        
        return fig, ax
        
    
