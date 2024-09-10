#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGDataPreproc for representing preprocessed EMG data.

Inherits from the class EMGData.

Use for downstream analysis of the preprocessed EMG data.

"""
from __future__ import annotations
from typing import TYPE_CHECKING

from pymicroemg.emg_reconstruct_settings import EMGAnalysisMotorUnitClusterSettings
from pymicroemg.emg_reconstruct_settings import EMGAnalysisMotorUnitJitterSettings

import json
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
        mu_cluster_settings: EMGAnalysisMotorUnitClusterSettings,
        mu_jitter_settings: EMGAnalysisMotorUnitJitterSettings,
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
        mu_cluster_settings: EMGAnalysisMotorUnitClusterSettings
            Settings used to perform cluster analysis of fibre potentials, to estimate
            fibre positions.
        mu_jitter_settings: EMGAnalysisMotorUnitJitterSettings
            Setting used to perform jitter analysis.

        Returns
        -------
        reconstruct : EMGAnalysisReconstruct
            Object with methods for motor unit identification and fibre reconstruction.

        """

        reconstruct = EMGAnalysisReconstruct(
            emg_data_preproc=self,
            mu_settings=mu_settings,
            recon_settings=recon_settings,
            mu_cluster_settings=mu_cluster_settings,
            mu_jitter_settings=mu_jitter_settings,
        )

        return reconstruct

    def get_preprocess_dict(self) -> dict:
        """
        Returns EMG info used for preprocessing.

        Parameters
        ----------
        None.

        Returns
        -------
        dict

        """

        # Define settings dictionary.
        preproc_dict = {
            "fs": self.fs,
            "analyse_chan": self.chan.analyse_chan.tolist(),
            "segment_of_recording": self.segment_of_recording.tolist(),
        }

        return preproc_dict

    def set_preprocess_from_dict(self, settings_dict: dict):
        """
        Sets EMG info used for preprocessing.

        Parameters
        ----------
        settings_dict: Dictionary
            Dictionary with all the settings saved in it.

        Returns
        -------
        None

        """

        self.fs = settings_dict["fs"]
        self.chan.analyse_chan = np.array(settings_dict["analyse_chan"])
        self.segment_of_recording = np.array(settings_dict["segment_of_recording"])

    def save_preprocess(self, filename: str):
        """
        Saves prepocessing EMG info and settings.

        Parameters
        ----------
        filename: str
            Name of file to save in.

        Returns
        -------
        None

        """

        # Define dictionary to save results.
        preproc_dict = self.get_preprocess_dict()

        # Add settings used for preprocessing.
        preproc_dict["preproc_settings"] = self.preproc_settings.get_settings_dict()

        # Convert and write JSON object to file.
        with open(filename, "w") as outfile:
            json.dump(preproc_dict, outfile)

    def load_preprocess(self, filename: str):
        """
        Loads preprocessing EMG info and settings.

        Parameters
        ----------
        filename: str
            Name of file to load data from.

        Returns
        -------
        None

        """

        # Opening JSON file.
        with open(filename) as json_file:
            preproc_dict = json.load(json_file)

        # Set preprocessing info and settings.
        self.set_preprocess_from_dict(preproc_dict)
        self.preproc_settings.set_settings_from_dict(preproc_dict["preproc_settings"])
