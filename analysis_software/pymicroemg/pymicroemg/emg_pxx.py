#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGPxx, for representing EMG power spectral densities.

"""
from __future__ import annotations

import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt

from pymicroemg.emg_channels import EMGChannels

class EMGPxx:
    '''
    Class for representing power spectral density (PSD) computed from EMG 
    recording.
    '''
    
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
            ax.set_title(self.chan.chan_names[plot_chan-1])
        
        # Axis labels
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('PSD')
        
        return fig, ax