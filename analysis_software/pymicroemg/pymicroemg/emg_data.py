#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGData, for representing EMG times series data loaded from Intan
recording files.

Only child classes, EMGDataRaw and EMGDataPreproc, can be instantiated. This
class provides common methods for both child classes (e.g., for visualisation).

"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt
import scipy.signal

from pymicroemg.emg_channels import EMGChannels
from pymicroemg.emg_pxx import EMGPxx


class EMGData:
    """
    Class for representing EMG times series data (as a multivariate time series)

    """

    def __init__(
        self,
        emg_ts: npt.NDArray[np.float64],
        fs: float,
        chan: EMGChannels,
        segment_of_recording: npt.NDArray[np.float64],
    ):
        """
        Initialise EMGData object.

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

        """

        self.emg_ts = emg_ts
        self.n_chan, self.n_samples = emg_ts.shape
        self.fs = fs
        self.emg_dur = self.n_samples / self.fs
        self.segment_of_recording = segment_of_recording
        self.chan = chan

        # default time points to use for the analysis (all timepoints)
        self.analyse_t = np.full(self.n_samples, True)

    def __new__(cls, *args, **kwargs):
        """
        Override "new" method to only allow children of EMGData to be
        instantiated.

        """
        if cls is EMGData:
            raise TypeError(f"Only children of {cls.__name__} may be instantiated.")
        return object.__new__(cls)

    def get_emg_t(self) -> npt.NDArray[np.float64]:
        """
        Create a vector of the time corresponding to each sample in the EMG
        time series. Time is defined as the number of seconds elapsed since the
        start of the recording. The first time point is labelled as 1/Fs, where
        Fs is the sampling frequency, and the last time point is equal to the
        EMG segment's duration in seconds.

        Note that this time vector is only used for labelling.

        Returns
        -------
        emg_t : 1D numpy NDArray[np.float64]
            Vector of the time of each EMG sample, defined as seconds elapsed
            since the start of the recording.

        """

        emg_t = np.arange(1, self.n_samples + 1) / self.fs

        return emg_t

    def _validate_t_range(self, start_t: float, stop_t: float):
        """
        Validate start and stop times used to specify time ranges for EMGData
        methods. Ensures both values are 1) within range [0, emg_dur], where
        emg_dur is the time series duration, and 2) the start time is less than
        the stop time.

        Assumes times units are seconds.

        Parameters
        ----------
        start_t : float
            Start time in seconds.
        stop_t : float
            Stop time in seconds.

        Raises
        ------
        ValueError
            Raised if start_t < 0.
            Raised if stop_t < 0.
            Raised if stop_t > emg_dur.
            Raised if start_t >= stop_t.

        Returns
        -------
        None.

        """

        # Confirm that start time is positive
        if start_t < 0:
            raise ValueError("The start of the time range must be positive.")

        # Confirm that end (stop) time is positive
        if stop_t < 0:
            raise ValueError("The end of the time range must be positive.")

        # Confirm that end (stop) time is not longer than segment duration
        if stop_t > self.emg_dur:
            raise ValueError(
                f"The end of the time range (currently {stop_t} seconds) is "
                "too large. It must be less than or equal to the duration of "
                f"the segment, {self.emg_dur} seconds."
            )

        # Confirm that start time is before stop time
        if start_t >= stop_t:
            raise ValueError(
                f"The start of the time range (currently {start_t} seconds), "
                "must be less than the end of the time range (currently "
                f"{stop_t} seconds)."
            )

    def _get_t_idx(self, start_t: float, stop_t: float) -> npt.NDArray[np.int64]:
        """
        Get indices in EMGData time series that correspond to the requested
        time range.

        Note that although the first time point is labelled as 1/fs seconds,
        time 0 seconds will return the first time point. If the indexing were
        shifted by 1/fs, plot_idx would return an out-of-bounds index when
        stop_t = self.emg_dur.

        Parameters
        ----------
        start_t : float
            First time point to plot, in seconds.
        stop_t : float
            Last time point to plot, in seconds.

        Returns
        -------
        t_idx : 1D numpy NDArray[np.int64]
            Indices for extracting requested time range from EMGData time
            series.

        """

        # TODO: consider moving validation (using _validate_t_range) call to this method

        t_idx = np.arange(np.round(start_t * self.fs), np.round(stop_t * self.fs))
        t_idx = t_idx.astype("int")

        return t_idx

    def trim_emg_ts(self, start_t: float, stop_t: float):
        """
        Trim the EMG time series to the desired time interval.

        Updates the recording's number of samples, duration, and corresponding
        segment in the original recording accordingly.

        Parameters
        ----------
        start_t : float
            First time point to plot, in seconds.
        stop_t : float
            Last time point to plot, in seconds.

        Raises
        ------
        Exception
            Raises exception if EMG time series has already been trimmed.

        Returns
        -------
        None.

        """
        # TODO: determine how to allow segment trimmed to be changed;
        # will depend on when trimming occurs relative to preprocessing.
        # TODO: could also allow time segment to be further trimmed - would need to
        # calculate corresponding segment in original recording.

        # Only allow trimming if time series has not been trimmed yet
        # (i.e., segment_of_recording bounds are inf)
        if sum(np.isinf(self.segment_of_recording)) == 2:
            # Validate start and stop times
            self._validate_t_range(start_t, stop_t)

            # Get indices in time series corresponding to requested time segment
            t_idx = self._get_t_idx(start_t, stop_t)

            # Extract requested time segment
            self.emg_ts = self.emg_ts[:, t_idx]

            # Update corresponding attributes.
            # The time labels, computed from get_emg_t, are not an attribute and
            # therefore do not need to be update.
            self.segment_of_recording = np.array((start_t, stop_t))
            self.n_samples = self.emg_ts.shape[1]
            self.emg_dur = self.n_samples / self.fs

        else:
            raise Exception(
                "The EMG time series has already been trimmed - " "cannot trim again."
            )

    def plot_emg_ts(
        self,
        start_t=0,
        stop_t=None,
        offset=1000,
        ax=None,
        lw=0.5,
        figsize=(7, 7),
        yticklabel_size=6,
        xticklabel_size=8,
        dpi=100,
        downsample_factor=1,
    ):
        """
        TODO: update documentation
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

        """
        # TODO: design alterations (e.g., default colors and color options)

        # Default end (stop) time is the segment's duration
        if stop_t is None:
            stop_t = self.emg_dur

        # Validate start and stop times
        self._validate_t_range(start_t, stop_t)

        # Offset must be positive to ensure that channels are correctly labelled.
        if offset < 0:
            raise ValueError("The vertical spacing, offset, must be positive")

        # Create new figure with specified size if no axis provided
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
            fig.dpi = dpi
        else:
            fig = None

        # Time vector for x axis
        emg_t = self.get_emg_t()

        # Get indices corresponding to requested time segment.
        plot_idx = self._get_t_idx(start_t, stop_t)
        plot_idx = plot_idx[0::downsample_factor]  # downsample

        # Plot each channel's signal, staggered by the specified offset
        for i in range(self.n_chan):
            ax.plot(emg_t[plot_idx], self.emg_ts[i, plot_idx] - offset * i, lw=lw)

        # Channel labels
        chan_y = np.arange(0, self.n_chan * offset * -1, offset * -1)
        ax.set_yticks(chan_y)
        ax.set_yticklabels(self.chan.chan_names)
        ax.tick_params(axis="y", which="major", labelsize=yticklabel_size)

        # x axis labels and font size
        ax.set_xlabel("time (seconds)")
        ax.tick_params(axis="x", which="major", labelsize=xticklabel_size)
        ax.set_xlim(min(emg_t[plot_idx]) - 1 / self.fs, max(emg_t[plot_idx]))
        return fig, ax

    def compute_pxx(self, window_size: float) -> EMGPxx:
        """
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

        """

        # Compute PSD
        freq, pxx = scipy.signal.welch(
            x=self.emg_ts, fs=self.fs, nperseg=self.fs * window_size, axis=1
        )

        # Store output as EMGPxx class
        emg_pxx = EMGPxx(freq=freq, pxx=pxx, chan=self.chan, window_size=window_size)

        # Not stored as an EMGData attribute since not used for downstream
        # analysis; also allows multiple PSDs to be created at different
        # preprocessing steps.
        return emg_pxx
