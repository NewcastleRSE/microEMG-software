#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGDataRaw for representing raw (not preprocessed) EMG data.

Inherits from the class EMGData.

Used to perform initial preprocessing steps and visualisations.

"""

from __future__ import annotations

import logging
import numpy as np
import numpy.typing as npt
import scipy.signal

from pymicroemg.emg_data import EMGData
from pymicroemg.emg_channels import EMGChannels
from pymicroemg.emg_preproc_settings import EMGPreprocSettings
from pymicroemg.emg_data_preproc import EMGDataPreproc

# Logger - will be used for progress updates for GUI
logger = logging.getLogger("EMGDataRawLogger")
logger.setLevel(logging.INFO)

# --- Classes for custom logging ---


class RecordContext:
    # Class for storing context about the analysis for the logger
    # TODO: docstring
    # TODO: consider changing to a dataclass

    def __init__(
        self,
        analysis_step: str = "",
        analysis_start: bool = False,
        loop_i: int | None = None,
        loop_max: int | None = None,
    ):
        self.analysis_step = analysis_step
        self.analysis_start = analysis_start
        self.loop_i = loop_i
        self.loop_max = loop_max


class EMGDataRawLoggerAdapter(logging.LoggerAdapter):
    # Adapter to add additional, easily accessible context to the logger
    # TODO: add docstring

    def __init__(self, logger, extra=None):
        super().__init__(logger, extra)

        if extra:
            self.record_context = extra.get("record_context")


# --- EMG data class ----


class EMGDataRaw(EMGData):
    """
    Class for representing raw EMG times series data as a multivariate time
    series.

    Inherits from EMGData.

    Methods to add:
    remove mains noise
    detect low amplitude channels
    detect high frequency noise
    mark bad channels (based on visual inspection)

    """

    def __init__(
        self,
        emg_ts: npt.NDArray[np.float64],
        fs: float,
        chan: EMGChannels,
        segment_of_recording: npt.NDArray[np.float64],
    ):
        """
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

        """
        super().__init__(emg_ts, fs, chan, segment_of_recording)

    def preprocess(self, preproc_settings: EMGPreprocSettings) -> EMGDataPreproc:
        # Creates preprocessed EMG data (EMGDataPreproc object) by applying
        # preprocessing settings to raw EMG data

        # Deep copy of EMG time series so that original time series is retained
        emg_ts = self.emg_ts.copy()

        # Remove mains noise
        if preproc_settings.remove_mains:
            config = preproc_settings.remove_mains_settings
            print("Removing mains noise.")
            emg_ts = self._remove_mains(
                emg_ts, freq_remove=config["freq_remove"], n_win_avg=config["n_win_avg"]
            )

        # Note that after mains noise removal, the number of samples in emg_ts
        # may differ from self.emg_ts.
        # Do not use self.emg_dur or self.n_samples in downstream preprocessing
        # steps.

        # Apply Butterworth filter
        if preproc_settings.butterworth_filter:
            config = preproc_settings.butterworth_filter_settings
            print("Applying Butterworth filter.")
            emg_ts = self._butterworth_filter(
                emg_ts,
                preproc_settings.get_butterworth_filter_cutoff(),
                config["order"],
                config["filter_type"],
            )

        # Create EMGDataPreproc object with preprocessed time series and
        # associated metadata
        emg_data_preproc = EMGDataPreproc(
            emg_ts, self.fs, self.chan, self.segment_of_recording, preproc_settings
        )

        return emg_data_preproc

    def _butterworth_filter(
        self,
        emg_ts: npt.NDArray[np.float64],
        cutoff_freq: list[float] | float,
        order: int,
        filter_type: str,
    ) -> npt.NDArray[np.float64]:
        """
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
        cutoff_freq : list[float]|float
            Filter cutoff frequencies.
        order : int
            Filter order - must be even to allow zero-phase filtering.
        filter_type : str
            Filter type - see scipy.signal.butter options.

        Returns
        -------
        emg_ts : npt.NDArray[np.float64]
            2D array containing the filtered multivariate EMG time series.

        """

        # Log
        analysis_step = "filtering"
        record_context = RecordContext(
            analysis_step=analysis_step, analysis_start=True, loop_max=self.n_chan
        )
        adapter = EMGDataRawLoggerAdapter(logger, {"record_context": record_context})
        adapter.info("Started filtering.")

        # Design filter
        sos = scipy.signal.butter(
            N=order // 2,
            Wn=cutoff_freq,
            btype=filter_type,
            analog=False,
            output="sos",
            fs=self.fs,
        )

        # Filter each channel's signal
        for i in range(self.n_chan):
            # Log progress
            record_context = RecordContext(analysis_step=analysis_step, loop_i=i)
            adapter = EMGDataRawLoggerAdapter(
                logger, {"record_context": record_context}
            )
            adapter.info(f"Filtering channel {i}")

            emg_ts[i, :] = scipy.signal.sosfiltfilt(sos, emg_ts[i, :])

        return emg_ts

    def _remove_mains(
        self,
        emg_ts: npt.NDArray[np.float64],
        freq_remove: int = 50,
        n_win_avg: int = 51,
    ) -> npt.NDArray[np.float64]:
        """
        Remove mains noise from the time series.

        The signal is divided into windows containing one cycle of noise (e.g., 20ms for
        50 Hz line noise). For each window, the mains signal is estimated by averaging
        the surrounding n_win_avg windows. This estimate signal is then removed from the
        window's signal. This approach therefore removes any other frequencies that are
        phase-locked to the mains noise frequency (e.g., harmonics).

        This approach is based on Digitimer's Hum Bug Noise Eliminator algorithm.

        Parameters
        ----------
        emg_ts : npt.NDArray[np.float64]
            2D array containing the multivariate EMG time series. Each row corresponds
            to the signal from one EMG channel.
        freq_remove : int, optional
            The frequency to remove from the signal, in hertz (usually the mains
            frequency). The sampling frequency of the time seriesmust be an integer
            multiple of freq_remove. The default is 50.
        n_win_avg : int, optional
            the number of windows to average to estimate the noise signal. The default
            is 51.

        Raises
        ------
        ValueError
            Raised if n_win_avg is not odd.
            Raised if the sampling frequency is not an integer multiple of freq_remove.

        Returns
        -------
        emg_ts : npt.NDArray[np.float64]
            2D array containing the multivariate EMG time series after mains noise has
            been removed.

        """

        # Log
        analysis_step = "removing_mains_noise"
        record_context = RecordContext(
            analysis_step=analysis_step, analysis_start=True, loop_max=self.n_chan
        )
        adapter = EMGDataRawLoggerAdapter(logger, {"record_context": record_context})
        adapter.info("Started removing mains noise.")

        # Check that number of windows used to average noise is odd.
        # Allows time period used to estimate noise to be centred around the window that
        # is being denoised.
        if n_win_avg % 2 == 0:
            raise ValueError(
                "The number of windows used to estimate the noise signal, n_win_avg, "
                "must be odd."
            )

        # Check that sampling frequency is an integer multiple of the frequency to be
        # removed
        if self.fs % freq_remove != 0:
            raise ValueError(
                "The time series sampling frequency must be an integer multiple of the "
                "frequency to remove, freq_remove"
            )

        # Number of samples per cycle of the frequency to remove, which determines the
        # window size. Will be 20 ms when the frequency to remove is 50 Hz.
        # Can convert to integer since we have confirmed that the sampling frequency
        # is a multiple of freq_remove.
        n_samples_per_win = int(self.fs / freq_remove)

        # Determine number of complete windows in time series.
        n_win = self.n_samples // n_samples_per_win

        # Trim partial window from data
        emg_ts = emg_ts[:, 0 : n_win * n_samples_per_win]

        # Start and stop of n_win_avg windows (inclusive endpoints) to use to estimate
        # mains noise.
        # First,  center around window to be denoised.
        start_win = np.arange(0, n_win) - n_win_avg // 2
        stop_win = np.arange(0, n_win) + n_win_avg // 2

        # Second, adjust indices at end of time series - instead use nearest n_win_avg
        # windows.
        adjust_idx = start_win < 0  # start indices before first time window
        start_win[adjust_idx] = 0
        stop_win[adjust_idx] = n_win_avg - 1
        adjust_idx = stop_win > n_win - 1  # stop indices after last time window
        start_win[adjust_idx] = (n_win - 1) - n_win_avg + 1
        stop_win[adjust_idx] = n_win - 1

        # Estimate and remove noise in each recording channel
        for i in range(self.n_chan):
            # Log progress
            record_context = RecordContext(analysis_step=analysis_step, loop_i=i)
            adapter = EMGDataRawLoggerAdapter(
                logger, {"record_context": record_context}
            )
            adapter.info(f"Removing noise from channel {i}")

            # Extract channel signal and reshape to form windows (one window per row)
            chan_ts = np.reshape(emg_ts[i, :], (n_win, n_samples_per_win))

            # Copy for holding original signal (needed to compute noise)
            chan_ts_original = chan_ts.copy()

            # For each window, estimate noise from surrounding windows; remove noise
            # from signal.
            for w in range(n_win):
                noise_signal = np.mean(
                    chan_ts_original[start_win[w] : (stop_win[w] + 1)], axis=0
                )
                chan_ts[w, :] -= noise_signal

            emg_ts[i, :] = np.reshape(chan_ts, (1, n_win * n_samples_per_win))

        return emg_ts
