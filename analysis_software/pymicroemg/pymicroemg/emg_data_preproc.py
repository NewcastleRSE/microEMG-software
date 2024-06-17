#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGDataPreproc for representing preprocessed EMG data.

Inherits from the class EMGData.

Use for downstream analysis of the preprocessed EMG data.

"""
from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt

from pymicroemg.emg_data import EMGData
from pymicroemg.emg_reconstruct import EMGAnalysisReconstruct

if TYPE_CHECKING:
    from pymicroemg.emg_channels import EMGChannels
    from pymicroemg.emg_preproc_settings import EMGPreprocSettings
    from pymicroemg.emg_reconstruct_settings import (
        EMGAnalysisReconstructSettings,
        EMGAnalysisMotorUnitSettings,
    )


class EMGDataPreproc(EMGData):
    """
    Class for representing preprocessed EMG times series data as a multivariate
    time series.

    Inherits from EMGData.

    Methods to add:
    analysis of motor units

    """

    def __init__(
        self,
        emg_ts: npt.NDArray[np.float64],
        fs: float,
        chan: EMGChannels,
        segment_of_recording: npt.NDArray[np.float64],
        preproc_settings: EMGPreprocSettings,
    ):
        """
        Initialise EMGDataPreproc object.

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
        preproc_settings : EMGPreprocSettings
            Object containing the preprocessing settings used to generate the
            preprocessed EMG time series from the raw EMG time series.

        Returns
        -------
        None.

        """
        super().__init__(emg_ts, fs, chan, segment_of_recording)
        self.preproc_settings = preproc_settings

    def set_analyse_t(self, start_t: float, stop_t: float):
        """
        Set time window of EMG time series to use in downstream analysis using specified
        start and stop times of the desired time window. This method changes the
        analyse_t attribute to mark which timepoints to use - no data is discarded.

        Note that the number of samples and duration of the EMGDataPreproc instance are
        still computed from full segment so that the time segment selected for the
        analysis can easily be changed.

        Parameters
        ----------
        start_t : float
            Start of the time window to use for the analysis (in seconds).
        stop_t : float
            End of the time window to use for the analysis (in seconds).

        Returns
        -------
        None.

        """

        # Validate requested time segment.
        self._validate_t_range(start_t, stop_t)

        # Get indices in time series corresponding to requested time segment.
        t_idx = self._get_t_idx(start_t, stop_t)

        # Store as boolean using analyse_t attribute for easy subsetting.
        # Note that original analyse_t values are not used (reset each time method is
        # called).
        self.analyse_t = np.full(self.n_samples, False)
        self.analyse_t[t_idx] = True

    def set_bad_chan(self, bad_chan: list[int]):
        """
        Mark "bad" channels that should be excluded from the analysis. Changes the
        chan.analyse_chan attribute to mark which channels to use - no data is
        discarded.

        Note that the number of channels attribute of the EMGDataPreproc instance is
        not changed so that the channels to omit from the analysis can easily be
        changed.

        Parameters
        ----------
        bad_chan : list[int]
            Indices of "bad" channels that should not be used for the analysis.

        Returns
        -------
        None.

        TODO: consider adding method to Channels class that is called by this method.
        """

        # Mark bad channels that should not be analysed.
        # Note that original chan.analyse_chan values are not used (reset each time
        # method is called).
        self.chan.analyse_chan = np.full(self.n_chan, True)
        self.chan.analyse_chan[bad_chan] = False

    def set_up_reconstruct_analysis(
        self,
        mu_settings: EMGAnalysisMotorUnitSettings,
        recon_settings: EMGAnalysisReconstructSettings,
    ) -> EMGAnalysisReconstruct:
        """
        Set up fibre reconstruction (i.e., localisation) analysis. The preprocessed EMG
        data object will be an attribute of the created EMGAnalysisReconstruct object.

        Parameters
        ----------
        mu_settings : EMGAnalysisMotorUnitSettings
            Settings to use for motor unit identification.
        recon_settings : EMGAnalysisReconstructSettings
            Settings to use for fibre reconstruction.

        Returns
        -------
        reconstruct : EMGAnalysisReconstruct
            Object with methods for motor unit identification and fibre reconstruction.

        """

        reconstruct = EMGAnalysisReconstruct(
            emg_data_preproc=self, mu_settings=mu_settings, recon_settings=recon_settings
        )

        return reconstruct
