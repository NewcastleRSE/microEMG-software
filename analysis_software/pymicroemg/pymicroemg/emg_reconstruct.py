#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGAnalysisReconstruct for localisation.

For use with preprocessed EMG data.

"""

from __future__ import annotations  # for type hints - must be at beginning of file

import numpy as np
import numpy.typing as npt  # for type hints

import scipy.signal as sg
import scipy.optimize as opt
from scipy.linalg import toeplitz
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt

# TODO: add csv and cv2 to poetry dependency management
# Need to remove try/except block - temporary fix since functions not needed for
# example pipeline
try:
    import csv
#    import cv2
except Exception as e:
    print(e)
import os

import pymicroemg.emg_tk_filter as tk
from pymicroemg.emg_constants import QUICK_VERSION

import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
from pymicroemg.emg_data_preproc import EMGDataPreproc

from pymicroemg.emg_reconstruct_settings import EMGAnalysisReconstructSettings
from pymicroemg.emg_reconstruct_settings import EMGAnalysisMotorUnitSettings
from pymicroemg.emg_motor_unit import EMGMotorUnit
from pymicroemg.emg_motor_unit import EMGMotorUnits


class EMGAnalysisReconstruct:
    """
    Class for performing reconstruct analysis

    """

    def __init__(
        self,
        emg_data_preproc: EMGDataPreproc,
        mu_settings: EMGAnalysisMotorUnitSettings,
        recon_settings: EMGAnalysisReconstructSettings,
    ):
        """
        Initialise EMGAnalysisReconstruct object.

        Parameters
        ----------
        emg_data_preproc: EMGDataPreproc
            Preprocessed EMG time series data

        Returns
        -------
        None

        """

        self.emg_data_preproc = emg_data_preproc
        self.mu_settings = mu_settings
        self.recon_settings = recon_settings
        self.n_chan = self.emg_data_preproc.n_chan

        # Needle model pos in mm
        self.needle = self.emg_data_preproc.chan.chan_xy

        # SNRs: The SNR values for each channel
        self.signal_noise_ratios = np.array([])
        # ranks: The rank of each channel on highest SNR
        self.signal_noise_ratios_ranks = np.array([])

        # Space for motor unit results
        # Initialise in find_motor_units
        # Fill in additional motor unit data by running fibre_reconstruction
        self.found_motor_units = None
        self.chan_for_find_motor_units = None

        # Initial threshold for 2D peak detection,
        # when decting multiple peaks
        self.threshold = 0.15

    def load_data(self, filename):
        """
        Load data - most likely just for testing.

        Parameters
        ----------
        filename: string
            file name and path of csv file

        Returns
        -------
        None

        """

        # Importing csv module
        with open(filename, "r") as x:
            self.emg_data_preproc.emg_ts = list(
                csv.reader(x, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
            )

        self.emg_data_preproc.emg_ts = np.array(self.emg_data_preproc.emg_ts)

    def load_motor_unit_data_from_matlab(self, filename_indices, filename_locs, set_unbroken=True):
        """
        Load data for motor units from MATLAB, so take 1 away from index locations
        - most likely to be used just for testing.

        Parameters
        ----------
        filename_indices: string
            file name and path of csv file of indices.
            Indices refer to positions in self.emg_data_preproc.emg_ts

        filename_locs: string
            file name and path of csv file of motor unit labels,
            which are positive integers
            These labels correspond to the indices above

        set_unbroken: bool
            Sets all channels to unbroken

        Returns
        -------
        None

        """

        # Importing csv module
        with open(filename_indices, "r") as x:
            mup_t_idx = list(csv.reader(x, delimiter=",", quoting=csv.QUOTE_NONNUMERIC))

        with open(filename_locs, "r") as x:
            mu_numbers = list(csv.reader(x, delimiter=",", quoting=csv.QUOTE_NONNUMERIC))

        mu_numbers = (np.array(mu_numbers)).flatten()
        mup_t_idx = (np.array(mup_t_idx)).flatten()
        mup_t_idx = (np.round(mup_t_idx - 1)).astype(int)
        mu_numbers = (np.round(mu_numbers - 1)).astype(int)

        # Add motor unit objects
        self.add_motor_units(mup_t_idx, mu_numbers)

        if set_unbroken:
            # Set all to non broken like MATLAB analysis for this data
            self.emg_data_preproc.chan.analyse_chan = np.full(self.n_chan, True)

    def load_mup_data_from_matlab(
        self, motor_unit_number, filename_fibre_centres, filename_mup_onsets
    ):
        """
        Load fibre centre and onset data for one motor unit from MATLAB,
        - so take 1 away from index locations
        - most likely to be used just for testing, esp clustering of MUPs

        Parameters
        ----------
        motor_unit_number: int
            number of the motor unit (starting from 0)

        filename_fibre_centres: string
            file name and path of csv file of fibre centres
            Indices refer to positions in self.emg_data_preproc.emg_ts

        filename_mup_onsets: string
            file name and path of csv file of motor unit labels,
            which are positive integers


        Returns
        -------
        None

        """

        # Importing csv module
        with open(filename_fibre_centres, "r") as x:
            fibre_centres = list(csv.reader(x, delimiter=",", quoting=csv.QUOTE_NONNUMERIC))

        with open(filename_mup_onsets, "r") as x:
            mup_onsets = list(csv.reader(x, delimiter=",", quoting=csv.QUOTE_NONNUMERIC))

        motor_unit = self.found_motor_units.motor_units[motor_unit_number]

        motor_unit.fibre_centres = np.array(fibre_centres, dtype=float)
        motor_unit.mup_onsets = np.array(mup_onsets).astype(int)
        motor_unit.mup_onsets = (motor_unit.mup_onsets[0, :] - 1).flatten()
        motor_unit.analysis_performed["fibres_localised"] = True

    def load_mup_data(self, motor_unit_number, filename_fibre_centres, filename_mup_onsets, filename_fibre_pot_times):
        """
        Load fibre centre and onset data for one motor unit
        - most likely to be used just for testing, esp clustering of MUPs

        Parameters
        ----------
        motor_unit_number: int
            number of the motor unit (starting from 0)

        filename_fibre_centres: string
            file name and path of csv file of fibre centres
            Indices refer to positions in self.emg_data_preproc.emg_ts

        filename_mup_onsets: string
            file name and path of csv file of motor unit labels,
            which are positive integers


        Returns
        -------
        None

        """

        # Importing csv module
        with open(filename_fibre_centres, "r") as x:
            fibre_centres = list(csv.reader(x, delimiter=",", quoting=csv.QUOTE_NONNUMERIC))

        with open(filename_mup_onsets, "r") as x:
            mup_onsets = list(csv.reader(x, delimiter=",", quoting=csv.QUOTE_NONNUMERIC))
            
        with open(filename_fibre_pot_times, "r") as x:
            fibre_pot_times = list(csv.reader(x, delimiter=",", quoting=csv.QUOTE_NONNUMERIC))

        motor_unit = self.found_motor_units.motor_units[motor_unit_number]

        motor_unit.fibre_centres = np.array(fibre_centres, dtype=float)
        motor_unit.mup_onsets = np.array(mup_onsets).astype(int).flatten()   
        motor_unit.n_fibre_potentials = len(motor_unit.fibre_centres)
        motor_unit.fibre_potential_times = np.array(fibre_pot_times).astype(int).flatten()
        
        print(motor_unit.fibre_centres)
        print(motor_unit.mup_onsets)
        motor_unit.analysis_performed["fibres_localised"] = True

    def calculate_SNR_ranks(self):
        """
        Calculate the signal to noise ratios and rank them

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        # Set up vector for signal to noise ratios for each channel
        self.signal_noise_ratios = np.zeros(self.n_chan)

        for channel in range(self.n_chan):
            # Skip "bad" channels
            if self.emg_data_preproc.chan.analyse_chan[channel]:
                temp = self.emg_data_preproc.emg_ts[channel, :]
                self.signal_noise_ratios[channel] = np.mean(temp[temp > 0])

        # Sort SNRs in decending order
        self.signal_noise_ratios_ranks = np.argsort(-self.signal_noise_ratios)

    def find_motor_units(self):
        """
        Finds the motor units and records results in mup_t_idx and mu_numbers
        mu_numbers are the motor unit labels, 0, 1, 2, ...
          these numbers are also the indices used when the motor units are stored in
          the EMGMotorUnits object
        mup_t_idx are the motor unit potential time indices to retreive data
          from the used signal data

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        # Order by highest Signal to Noise Ratio
        self.calculate_SNR_ranks()

        sampling_freq = self.emg_data_preproc.fs

        # Find all MUAPs in channel with best signal
        if self.signal_noise_ratios[self.signal_noise_ratios_ranks[0]] > 0:
            sig_ind = self.signal_noise_ratios_ranks[0]
        else:
            raise Exception("Sorry, no channels with a calculable signal to noise ratio!")

        self.chan_for_find_motor_units = sig_ind  # store channel for plots

        # Apply Multi-dimensional TK operator (Teager-Kaiser)
        # to return MUAPs in channel

        # Deep copy to ensure processing in TK_filter is not stored
        used_data = self.emg_data_preproc.emg_ts[sig_ind, :].copy()

        mup_t_idx, mu_numbers = tk.TK_filter(
            used_data,
            sampling_freq,
            self.mu_settings.tk_filt_thres_spike,
            self.mu_settings.tk_filt_thres_PsC,
        )

        print(
            "Motor Units found: " + str(np.max(mu_numbers) + 1) + " via channel: " + str(sig_ind)
        )

        # Add motor unit objects
        self.add_motor_units(mup_t_idx, mu_numbers)

    def add_motor_units(self, mup_t_idx, mu_numbers):
        """
        Adds the motor units

        Parameters
        ----------
        motor_unit_number: int
            motor unit number used as a label

        Returns
        -------
        None

        """

        # Create motor unit objects for each motor unit
        all_motor_units = []
        for i in range(np.max(mu_numbers) + 1):
            motor_unit = EMGMotorUnit(number=i, potentials_t_idx=mup_t_idx[mu_numbers == i])
            all_motor_units.append(motor_unit)

        self.found_motor_units = EMGMotorUnits(
            all_motor_units, chan_xy=self.emg_data_preproc.chan.chan_xy
        )

    def plot_motor_units_raster(
        self,
        linelengths: float = 0.9,
        linewidths: float = 0.75,
        ax=None,
        figsize=(10, 5),
        dpi: int = 100,
        axis_label_size: float = 14,
        xtick_label_size: float = 12,
        ytick_label_size: float = 12,
        sort_by: str = "default",
    ):
        """
        Create a raster plot of the potentials of each motor unit in the recording.
        Each motor unit is a row in the visualisation, and vertical lines are drawn at
        the times of the motor unit's potentials.

        Parameters
        ----------
        linelengths : float, optional
            DESCRIPTION. The default is 0.9.
        linewidths : float, optional
            DESCRIPTION. The default is 0.75.
        ax : TYPE, optional
            DESCRIPTION. The default is None.
        figsize : TYPE, optional
            DESCRIPTION. The default is (10, 5).
        dpi : int, optional
            DESCRIPTION. The default is 100.
        axis_label_size : float, optional
            DESCRIPTION. The default is 14.
        xtick_label_size : float, optional
            DESCRIPTION. The default is 12.
        ytick_label_size : float, optional
            DESCRIPTION. The default is 12.
        sort_by : str, optional
            DESCRIPTION. The default is "default".
         : TYPE
            DESCRIPTION.

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        fig : TYPE
            DESCRIPTION.
        ax : TYPE
            DESCRIPTION.

        TODO: finish docstring once inputs are finalised
        TODO: update error message to distinguish between cases 1) localisation analysis
        hasn't been run, and 2) analysis run, but no MUPs found.

        """
        if not self.found_motor_units:
            raise ValueError("No motor units identified - confirm that analysis has been run.")

        # Get motor units and sort if requested
        motor_units = self.found_motor_units.motor_units
        sort_options = ["default", "n_potentials"]
        if sort_by not in sort_options:
            raise ValueError(f"sort_by must be one of these options: {sort_options}")
        elif sort_by == "n_potentials":
            sort_idx = np.argsort(self.found_motor_units.n_potentials)
            sort_idx = sort_idx[::-1]  # descending order
            motor_units = [motor_units[i] for i in sort_idx]

        # Labels for motor units - plus 1 to count from 1, rather than 0, for vis
        motor_units_numbers = [mu.motor_unit_number + 1 for mu in motor_units]

        # Create new figure with specified size if no axis provided
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
            fig.dpi = dpi
        else:
            fig = None

        # Time vector for x axis
        emg_t = self.emg_data_preproc.get_emg_t()

        # Create list of times of MUPs
        # Each entry is an array of the potential times for one motor unit
        potential_t = []
        for mu in motor_units:
            potential_t.append(emg_t[mu.potentials_t_idx])

        # Raster plot
        ax.invert_yaxis()  # places first motor unit at the top of the plot
        ax.eventplot(potential_t, linelengths=linelengths, linewidths=linewidths)

        # Axis ticks and labels
        # y axis
        ax.set_yticks(np.arange(self.found_motor_units.n_motor_units))
        ax.set_yticklabels(motor_units_numbers)
        ax.tick_params(axis="y", which="major", labelsize=ytick_label_size)
        ax.set_ylabel("motor unit", fontsize=axis_label_size)
        # x axis
        ax.tick_params(axis="x", which="major", labelsize=xtick_label_size)
        ax.set_xlabel("time (seconds)", fontsize=axis_label_size)
        ax.set_xlim(min(emg_t) - 1 / self.emg_data_preproc.fs, max(emg_t))

        # TODO: change time tick labels to mm:ss format

        return fig, ax

    def get_potentials_data_of_one_motor_unit(
        self, motor_unit_idx: int, n_ms: int = 20
    ) -> npt.NDArray[np.float64]:
        """
        Extract the time series of each motor unit potential of the specified motor
        unit.

        Symmetrical data is extracted around each MUP's onset; total length of each
        segment is approximately n_ms milliseconds (may be rounded if cannot match time
        exactly given the recording's sampling rate).

        If requested segment length overlaps with the ends of the EMG recording, NaNs
        are instead returned for that segment.

        Parameters
        ----------
        motor_unit_idx : int
            Index of motor unit in EMGMotorUnits class for which to extract the
            potential time series data.
        n_ms : int, optional
            Number of milliseconds of data to extract. The data will be centered on the
            motor unit potential's onset. The default is 20.

        Raises
        ------
        RuntimeError
            Raised if no motor units are stored in the EMGAnalysisReconstruct object.

        Returns
        -------
        potentials_data : npt.NDArray[np.float64]
            Time series of each motor unit potential, size number of EMG channels x
            time x number of potentials.

        """

        if not self.found_motor_units:
            raise RuntimeError("No motor units identified - confirm that analysis has been run.")

        # Calculate number of samples to get before and after MUP onset
        n_samples = int(np.ceil(self.emg_data_preproc.fs / 1000 * n_ms) / 2)

        # Motor unit
        motor_unit = self.found_motor_units.motor_units[motor_unit_idx]
        motor_unit.potentials_t_idx

        # Get potentials from EMG recording data
        # dimensions are channels x time x MUP
        potentials_data = np.full(
            (self.n_chan, n_samples * 2, motor_unit.n_potentials),
            np.nan,
        )

        for i in np.arange(motor_unit.n_potentials):
            # Note that index excludes stop_t sample, which keeps the length to n_ms
            start_t = motor_unit.potentials_t_idx[i] - n_samples
            stop_t = motor_unit.potentials_t_idx[i] + n_samples

            # Only add potentials within boundaries of the time series
            if (start_t > 0) and (stop_t < self.emg_data_preproc.emg_ts.shape[1]):
                potentials_data[:, :, i] = self.emg_data_preproc.emg_ts[:, start_t:stop_t].copy()

        return potentials_data

    def plot_average_motor_unit_potential(
        self,
        motor_unit_idx: int,
        n_ms: int = 20,
        offset: float = 500,
        ax=None,
        lw: float = 0.5,
        figsize=(7, 7),
        axis_label_size: float = 10,
        ytick_label_size: float = 6,
        xtick_label_size: float = 8,
        dpi: int = 100,
    ):
        """
        Plot the average (mean) time series of the motor unit's potential.

        Parameters
        ----------
        motor_unit_idx : int
            DESCRIPTION.
        n_ms : int, optional
            DESCRIPTION. The default is 20.
        offset : float, optional
            DESCRIPTION. The default is 500.
        ax : TYPE, optional
            DESCRIPTION. The default is None.
        lw : float, optional
            DESCRIPTION. The default is 0.5.
        figsize : TYPE, optional
            DESCRIPTION. The default is (7, 7).
        axis_label_size : float, optional
            DESCRIPTION. The default is 10.
        ytick_label_size : float, optional
            DESCRIPTION. The default is 6.
        xtick_label_size : float, optional
            DESCRIPTION. The default is 8.
        dpi : int, optional
            DESCRIPTION. The default is 100.

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        fig : TYPE
            DESCRIPTION.
        ax : TYPE
            DESCRIPTION.

        TODO: finish docstring once vis arguments are finalised

        """

        if not self.found_motor_units:
            raise ValueError("No motor units identified - confirm that analysis has been run.")

        # Offset must be positive to ensure that channels are correctly labelled.
        if offset < 0:
            raise ValueError("The vertical spacing, offset, must be positive")

        # Create new figure with specified size if no axis provided
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
            fig.dpi = dpi
        else:
            fig = None

        # Get motor unit potentials and average (mean)
        potentials_data = self.get_potentials_data_of_one_motor_unit(motor_unit_idx, n_ms)
        potentials_avg = np.nanmean(potentials_data, axis=2)
        n_samples = potentials_avg.shape[1]

        # Time vector for x axis (ms)
        potentials_t = (np.arange(1, n_samples + 1) / self.emg_data_preproc.fs) * 1000

        # Plot each channel's MUP, staggered by the specified offset
        for i in range(self.n_chan):
            ax.plot(potentials_t, potentials_avg[i, :] - offset * i, lw=lw)

        # Channel labels
        chan_y = np.arange(0, self.n_chan * offset * -1, offset * -1)
        ax.set_yticks(chan_y)
        ax.set_yticklabels(self.emg_data_preproc.chan.chan_names)
        ax.tick_params(axis="y", which="major", labelsize=ytick_label_size)
        ax.set_ylabel("channel", fontsize=axis_label_size)

        # x axis labels and font size
        ax.set_xlabel("time (ms)", fontsize=axis_label_size)
        ax.tick_params(axis="x", which="major", labelsize=xtick_label_size)
        ax.set_xlim(0, max(potentials_t))

        return fig, ax

    def plot_all_potentials_one_channel(
        self,
        motor_unit_idx: int,
        chan_idx: int = None,
        n_ms: int = 20,
        ax=None,
        lw: float = 0.2,
        lw_mean: float = 0.5,
        figsize=(7, 7),
        axis_label_size: float = 10,
        ytick_label_size: float = 10,
        xtick_label_size: float = 10,
        dpi: int = 100,
    ):
        """

        Plots the time series of all motor unit potentials of one motor unit in one
        channel, with the mean time series overlaid.

        If channel is not specified, the channel used for detecting motor unit
        potentials is plotted.

        Note that the channel is specified using the channel index (counting from 0),
        not the channel numeric label (counting from 1)


        Parameters
        ----------
        motor_unit_idx : int
            DESCRIPTION.
        chan_idx : int, optional
            DESCRIPTION. The default is None.
        n_ms : int, optional
            DESCRIPTION. The default is 20.
        ax : TYPE, optional
            DESCRIPTION. The default is None.
        lw : float, optional
            DESCRIPTION. The default is 0.2.
        lw_mean : float, optional
            DESCRIPTION. The default is 0.5.
        figsize : TYPE, optional
            DESCRIPTION. The default is (7, 7).
        axis_label_size : float, optional
            DESCRIPTION. The default is 10.
        ytick_label_size : float, optional
            DESCRIPTION. The default is 10.
        xtick_label_size : float, optional
            DESCRIPTION. The default is 10.
        dpi : int, optional
            DESCRIPTION. The default is 100.
         : TYPE
            DESCRIPTION.

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        fig : TYPE
            DESCRIPTION.
        ax : TYPE
            DESCRIPTION.
        chan_idx : TYPE
            DESCRIPTION.

        TODO: finish docstring once vis arguments are finalised

        """

        if not self.found_motor_units:
            raise ValueError("No motor units identified - confirm that analysis has been run.")

        if not chan_idx:
            chan_idx = self.chan_for_find_motor_units

        # Create new figure with specified size if no axis provided
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
            fig.dpi = dpi
        else:
            fig = None

        # Get motor unit potentials and average (mean)
        potentials_data = self.get_potentials_data_of_one_motor_unit(motor_unit_idx, n_ms)
        potentials_avg = np.nanmean(potentials_data, axis=2)
        n_samples = potentials_avg.shape[1]

        # Time vector for x axis (ms)
        potentials_t = (np.arange(1, n_samples + 1) / self.emg_data_preproc.fs) * 1000

        # Plot each MUP in specified channel
        ax.plot(
            potentials_t,
            np.squeeze(potentials_data[chan_idx, :, :]),
            lw=lw,
            color="silver",
        )
        ax.plot(potentials_t, potentials_avg[chan_idx, :], lw=lw_mean, color="black")

        # Labels
        ax.tick_params(axis="y", which="major", labelsize=ytick_label_size)
        ax.set_ylabel("\u03bcV", fontsize=axis_label_size)
        # TODO: check that label should be uV

        # x axis labels and font size
        ax.set_xlabel("time (ms)", fontsize=axis_label_size)
        ax.tick_params(axis="x", which="major", labelsize=xtick_label_size)
        ax.set_xlim(0, max(potentials_t))

        return fig, ax, chan_idx

    def reconstruct_fibres(self, motor_unit_number):
        """
        Fills in fibre construction data and stores it
        in the corresponding motor unit object.

        Parameters
        ----------
        motor_unit_number: int
            motor unit number used as a label

        Returns
        -------
        None

        """

        # Motor unit for this number
        motor_unit = self.found_motor_units.motor_units[motor_unit_number]

        # Save the concurrent signal from all other channels for each spike
        all_spikes = np.zeros(
            (
                len(motor_unit.potentials_t_idx),
                self.n_chan,
                self.recon_settings.half_subsample_size * 2 + 1,
            )
        )

        # Zero reused vars
        t = 0
        # self.opr = []

        for t_idx in motor_unit.potentials_t_idx:
            # exclude spikes right at the edge of the recording
            if t_idx < (self.recon_settings.half_subsample_size + 1) or t_idx > (
                self.emg_data_preproc.emg_ts.shape[1]
                - self.recon_settings.half_subsample_size
                - 1
                - 1
            ):
                continue

            for channel in range(self.n_chan):
                # Skip bad channels
                if not self.emg_data_preproc.chan.analyse_chan[channel]:
                    continue

                all_spikes[t, channel, :] = self.emg_data_preproc.emg_ts[
                    channel,
                    int(t_idx - self.recon_settings.half_subsample_size) : int(
                        t_idx + self.recon_settings.half_subsample_size + 1
                    ),
                ]

            t += 1

        print("Motor Unit " + str(motor_unit_number + 1) + ": firings: " + str(t))

        if self.recon_settings.mavg_all:
            self.recon_settings.mavg_length = all_spikes.shape[0] - 1
        elif t < self.recon_settings.mavg_length or t < 2:
            # if there aren't enough spikes to model the MU, skip it
            print("Too few firings found to model this motor unit")
            return

        # The x, y coordinates of the fibre potential 
        pos = np.zeros((0, 2))
        # Onset indices of the MUPs (firings) relative to the overall time
        mup_onsets = np.array([])
        # Fibre potential peak times relative to the onset time
        # of the corresponding MUP (in indices units)  
        fibre_potential_times = np.array([])
        
        max_signal_id = all_spikes.shape[0] - self.recon_settings.mavg_length

        for signal_id in range(max_signal_id):

            sig = np.squeeze(
                np.mean(
                    all_spikes[
                        signal_id : (signal_id + self.recon_settings.mavg_length + 1),
                        :,
                        :,
                    ],
                    axis=0,
                )
            )

            sub_clusters = self.find_peaks_2d(sig)

            if sub_clusters.shape[0] == 0:
                continue

            for sub_cluster_index in range(sub_clusters.shape[0]):
                # Ensure we don't get spikes outside of recording duration
                time_peak = np.max(
                    np.hstack(
                        (
                            sub_clusters[sub_cluster_index, 0],
                            self.recon_settings.spike_dur + 1,
                        )
                    )
                )
                time_peak = np.min(
                    np.hstack(
                        (
                            time_peak,
                            self.recon_settings.half_subsample_size * 2
                            - self.recon_settings.spike_dur,
                        )
                    )
                )

                # Get the mean spikes for the fibre peak amplitude
                peak_electrode = sub_clusters[sub_cluster_index, 1]
                peak_start = np.max(np.hstack((peak_electrode - 3, 0)))
                peak_stop = np.min(np.hstack((peak_electrode + 3, self.n_chan - 1)))

                included_electrodes = np.arange(peak_start, peak_stop + 1, dtype="int")

                # Remove bad channels
                good_channels = (
                    np.arange(0, self.n_chan, dtype="int")
                    * self.emg_data_preproc.chan.analyse_chan
                )
                included_electrodes = np.intersect1d(included_electrodes, good_channels)

                if included_electrodes.shape[0] == 0:
                    continue

                self.sn = (
                    sig[
                        included_electrodes,
                        int(time_peak - self.recon_settings.spike_dur) : int(
                            time_peak + self.recon_settings.spike_dur + 1
                        ),
                    ]
                ).T

                self.needle = self.emg_data_preproc.chan.chan_xy

                # Scaling factor from mm to scaled AU
                # self.needle = self.needle * 4
                x0 = self.needle[int(peak_electrode), :]
                self.needle = self.needle[included_electrodes, :]

                # Non-linear optimisation algorithm for fibre positioning
                opt_paras = opt.fmin(
                    self.deconv_wrapper,
                    x0=x0,
                    maxiter=self.recon_settings.max_opt_iterations,
                    full_output=False,
                    xtol=self.recon_settings.xtol,
                    ftol=self.recon_settings.ftol,
                    disp=False,
                )

                pos = np.vstack((pos, opt_paras))

                mup_onsets = np.append(mup_onsets, motor_unit.potentials_t_idx[signal_id])
                
                # Add fibre potential times, these are already adjusted and relative to the MUP onset times    
                fibre_potential_times = np.append(fibre_potential_times, time_peak)
                
        # End of signal_id loop

        # TODO remove this line and self.needle scaling above
        # (pending SM's final decision about the scaling)
        # pos[:, 0] = pos[:, 0] / 4

        # Add the results to the motor unit object
        if pos.shape[0] > 0:
            motor_unit.add_fibre_localisation(
                fibre_centres=pos,
                mup_onsets=mup_onsets,
                fibre_potential_times=fibre_potential_times,
                all_spikes=all_spikes,
                generator_potential=np.array(np.transpose(self.opr)),
            )

        # Restore needle to full needle, rather than subset of the needle
        self.needle = self.emg_data_preproc.chan.chan_xy

    def find_peaks(self, data, distance=1, min_peak_height=None):
        """
        Try to return as near as possible the same answer
        as findpeaks in MatLab if not QUICK VERSION
        """

        if QUICK_VERSION:
            peaks, _ = sg.find_peaks(data, height=min_peak_height, distance=distance)
            return peaks
        else:
            return tk.detect_peaks(data, mph=min_peak_height, mpd=distance)

    def peak_group(self, signal):
        """
        Function to group electrodes by related signal
        Identifies peaks in the signal, and then adjacent rows are assigned into
        groups related to that signal.

        Parameters
        ----------
        signal: 1D numpy NDArray[float], for example the SNRs across the electrodes


        Returns
        -------
        groups: 1D numpy NDArray[int]
            array of integers & zeros reflecting the signal groups that
            the electrodes are placed into
        """

        locs = self.find_peaks(signal, 4, np.max(signal) / 3)

        # Create list of empty lists
        groups = [[] for _ in range(len(signal))]

        for peak in range(len(locs)):
            left_index = np.max([0, locs[peak] - 3])
            right_index = np.min([len(signal) - 1, locs[peak] + 3])

            for index in range(left_index, (right_index + 1)):
                groups[index].append(peak)

        return groups

    def find_peaks_2d_filters(self, image, threshold):
        neighborhood_size = 5

        data_max = filters.maximum_filter(image, neighborhood_size)
        maxima = image == data_max
        data_min = filters.minimum_filter(image, neighborhood_size)
        diff = (data_max - data_min) > threshold
        maxima[diff == 0] = 0

        labeled, _ = ndimage.label(maxima)
        slices = ndimage.find_objects(labeled)
        x, y = [], []

        for dy, dx in slices:
            x_center = (dx.start + dx.stop - 1) / 2
            x.append(x_center)
            y_center = (dy.start + dy.stop - 1) / 2
            y.append(y_center)

        ans = np.vstack((x, y)).T

        return ans

    def find_peaks_2d(self, sig):
        """
        Finds local maxima of a 2-dimensional image area
        Dependent on findpeaks algorithm from findpeaks package

        Parameters
        ----------
        signal: 2D numpy NDArray[float, float]
                n*m array of signal data

        Returns
        -------
        locs: 2D numpy NDArray[int, int]
            2D array of location of peaks
        """

        threshold = self.threshold
        base = sig
        # remove negative deflection to discount 'doubling peaks'
        # from negative initial deflection of SFAP
        base[base < 0] = 0

        sigma = 2
        im2 = np.abs(gaussian_filter(base, sigma, truncate=np.ceil(2 * sigma) / sigma))

        # Extract each blob
        locs = np.array([])
        found = False
        parse_limit = 0
        im2_max = np.max(im2)
        max_number_of_peaks = 22

        while not found:
            parse_limit = parse_limit + 1
            locs = self.find_peaks_2d_filters(im2, im2_max * threshold)

            if locs.shape[0] < 1:
                threshold = threshold - 0.02
            elif locs.shape[0] > max_number_of_peaks:
                threshold = threshold + 0.02
            else:
                found = True
                # save nice threshold for next time to perhaps speed it up
                self.threshold = threshold

            if threshold <= 0.05 or threshold > 1 or parse_limit > 20:
                locs = np.array([])
                found = True

        if locs.shape[0] > 0:
            locs[locs[:, 1] < 0, 1] = 0

        return locs

    def deconv_wrapper(self, loc):
        """
        Deconvolution
        Now reconstruct without using gn!
        Calculate deconvolution for each channel in a 50x50 grid
        Region is 0-1000u (Y) and 100-500u (X)
        Error is abs mismatch across the reconstructions of 'gn'
        Calculated as the max variance across the centre of the 5 reconstructions.
        This example is a blind hunt across 2500 locations near the needle.
        Here, cn is 400 samples long so that a Toeplitz matrix can be created.

        Parameters
        ----------
        loc

        Returns
        -------
        total_var:
        """

        self.no_needle_channels = self.needle.shape[0]

        cn = self.calc_cn(loc[0], loc[1], self.recon_settings.half_subsample_size * 2)

        iterable = (
            self.tconv(cn[:, k], self.sn[:, k], self.recon_settings.spike_dur * 2 + 1)
            for k in range(self.no_needle_channels)
        )
        self.opr = np.fromiter(iterable, dtype=np.ndarray)

        total_var = -np.reciprocal(np.max(np.var(self.opr, axis=0, ddof=1)))

        return total_var

    def cn_element(self, z, channel):
        """
        Generate element of the cn matrix, row 'z', column 'channel'

        Parameters
        ----------
        z: float
            distance along fibre
        channel: int
            channel

        Returns
        -------
        float

        """

        dx = np.fabs(self.fbx - self.needle[channel, 0])  # X offset
        dy = np.fabs(self.fby - self.needle[channel, 1])  # Y offset of channel i
        dz = np.fabs(z - self.isz_half)  # Z distance along fibre

        return np.reciprocal(np.sqrt(dx * dx + dy * dy + dz * dz))

    def calc_cn(self, fbx, fby, isz):
        """
        Channel functions
        Generate 1/r conv functions for coords fbx, fby for each channel.

        Parameters
        ----------
        fbx:

        fby:

        isz:

        Returns
        -------
        cn: 2D numpy NDArray[int, int]

        """

        self.isz_half = isz / 2
        self.fbx = fbx
        self.fby = fby
        cn = np.fromfunction(
            lambda i, j: self.cn_element(i, j),
            (isz, self.no_needle_channels),
            dtype=int,
        )

        return cn

    def tconv(self, ifn, sig, isz):
        """
        Deconvolution method function
        Create a Toeplitz matrix using the trailing 200 samples of cn
        First row will have the maximum at index 0, 2nd at 1 .....
        Use a Parzen window on the signal. See FFT deconvolution as to why!
        Then deconvolve sig by solving least squares problem.

        Parameters
        ----------
        ifn:

        sig:

        isz:

        Returns
        -------
        rsl
        """

        wsig = sg.windows.parzen(isz) * sig
        start_pos = len(ifn) - isz - 1
        end_pos = len(ifn) - 1
        tpl = toeplitz(ifn[start_pos:end_pos])

        rsl = (np.linalg.lstsq(tpl, wsig, rcond=None))[0]

        return rsl
