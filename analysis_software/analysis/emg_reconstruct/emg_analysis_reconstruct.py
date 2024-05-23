#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGAnalysisReconstruct for localisation.

For use with preprocessed EMG data.

"""

from __future__ import annotations  # for type hints - must be at beginning of file

# from xml.etree.ElementInclude import include
# from re import A
import numpy as np
import numpy.typing as npt  # for type hints


# import numpy.typing as npt
import scipy.signal as sg
import scipy.optimize as opt
from scipy.linalg import toeplitz
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# TODO: add csv and cv2 to poetry dependency management
# Need to remove try/except block - temporary fix since functions not needed for
# example pipeline
try:
    import csv
#    import cv2
except Exception as e:
    print(e)
import os

# import math
import emg_analyser_python.emg_analyser_functions as tk
from emg_analyser_python.constants import QUICK_VERSION

# TODO: add findpeaks to poetry dependency managment if kept as dependency
# TODO: remove try/except block - temporary fix
try:
    from findpeaks import findpeaks
except Exception as e:
    print(e)

# from findmaxima2d import find_maxima, find_local_maxima, cfindmaxima2d
# from scipy.interpolate import RegularGridInterpolator
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
from pymicroemg.emg_data_preproc import EMGDataPreproc

# import time

# import pandas as pd


class EMGMotorUnit:
    """
    Class for storing data for one motor unit
    returned from reconstruction analysis

    """

    def __init__(self, number, potentials_t_idx: npt.NDArray[np.int64]):
        """
        Initialise EMGMotorUnit object.

        Parameters
        ----------
        number: int
                number labelling this motor unit
                matches number returned from TK_filter

        potentials_t_idx: npt.NDArray[np.int64]
            Time indices of the motor unit's potentials in the EMG recording

        Returns
        -------
        None

        """

        self.motor_unit_number = number

        self.n_potentials = len(potentials_t_idx)  # Number of potentials assigned to MU
        self.potentials_t_idx = potentials_t_idx  # Time indices of potentials in EMG

        # Store information about analysis that has been performed for this MU
        # Note: even if true, may not be results if data was not suitable for analysis
        self.analysis_performed = {
            "fibres_localised": False,  # localisation step
            "fibres_clustered": False,  # clustering fibres step
            "fibres_jitter_computed": False,  # jitter analysis step
        }

        # TODO: check understanding of each attribute
        # TODO: clean comments and move to docstring for class
        # TODO: update __str__ method once attributes are finalised

        # Localisation attributes

        # Number of fibre potentials (peaks) found across all MUPs
        self.n_fibre_potentials = None

        # Estimated fibre x, y coordinate at each time (size n peaks x 2)
        # TODO: consider renaming something like fibre_xy
        self.fibre_centres = np.array([])

        # average motor unit potential? size n chan x time
        # TODO: consider replacing functionality with
        # get_potentials_data_of_one_motor_unit() method of
        # EMGAnalysisReconstruct if this attribute is only used for plotting (esp.
        # since the plots are needed before this attribute is added!)
        # Otherwise, rename to clarify that it is the MUP
        self.mean_spikes = np.array([])

        # Onset of MUP that each peak belongs to? (size n peaks)
        # TODO: rename to clarify; consider whether MUP label ( = index) would be
        # easier to work with
        self.onsets = np.array([])

        # each MUP time series? size n potentials x n chan x time
        # TODO: rename or consider replacing functionality with
        # get_potentials_data_of_one_motor_unit() method of
        # EMGAnalysisReconstruct if this attribute is only used for plotting
        self.all_spikes = np.array([])

        # ?? not sure what data or how the size relates to other attributes
        self.gn_potential = np.array([])

        # TODO: currently the exact timing of fibre potentials (peaks) are not saved (?)
        # Will need this info for jitter analysis

        # Dictionaries for storing results of clustering and jitter analysis
        self.fibre_clustering_results = {}
        self.fibre_jitter_results = {}

    def __str__(self):
        """
        Return a string for the object

        Returns
        -------
        String

        """

        ans = "EMG Motor Unit"
        ans += "\nMotor unit number: "
        ans += str(self.motor_unit_number)
        ans += "\nNumber of potentials: "
        ans += str(self.n_potentials)
        ans += "\nFibre centres dimensions: "
        ans += str(self.fibre_centres.shape)
        ans += "\nMean spikes dimensions: "
        ans += str(self.mean_spikes.shape)
        ans += "\nOnsets dimensions: "
        ans += str(self.onsets.shape)
        ans += "\nAll spikes dimensions: "
        ans += str(self.all_spikes.shape)
        ans += "\nGN potential dimensions: "
        ans += str(self.gn_potential.shape)

        ans += "\n"

        return ans

    def add_fibre_localisation(
        self, fibre_centres, mean_spikes, onsets, all_spikes, gn_potential
    ):
        # TODO: remove any unnecessary attributes

        # Note analysis performed
        self.analysis_performed["fibres_localised"] = True

        # Store number of fibre potentials (i.e., peaks in the MUPs) found
        self.n_fibre_potentials = fibre_centres.shape[0]

        # Store provided attributes
        self.fibre_centres = fibre_centres
        self.mean_spikes = mean_spikes
        self.onsets = onsets
        self.all_spikes = all_spikes
        self.gn_potential = gn_potential


class EMGMotorUnits:
    """
    Class for storing and visualising all motor unit data returned from reconstruction
    analysis.

    Only includes visualisations that do not require the recording time series.

    """

    def __init__(
        self, motor_units: list[EMGMotorUnit], chan_xy: npt.NDArray[npt.float64]
    ):
        """
        Initialise EMGMotorUnits object.

        Parameters
        ----------
        motor_units : list[EMGMotorUnit]
            List of motor units (class EMGMotorUnit) to add to the EMGMotorUnits object.
        chan_xy : npt.NDArray[npt.float64]
            Channel (electrode) (x,y) coordinates; saved as attribute to facilitate
            visualisations.

        Returns
        -------
        None.

        """

        self.motor_units = motor_units
        self.n_motor_units = len(motor_units)

        # Get and store number of potentials of each motor unit
        self.n_potentials = [mu.n_potentials for mu in self.motor_units]

        self.chan_xy = chan_xy

    def __str__(self):
        """
        Return a string for the object

        Returns
        -------
        String

        """

        ans = "EMG Motor Units"
        ans += "\nNumber of motor units: "
        ans += str(self.n_motor_units)

        ans += "\n"

        return ans

    def __len__(self) -> int:
        """
        Return the number of motor units.

        Returns
        -------
        int
            Number of motor units stored in object.

        """
        return self.n_motor_units

    def plot_electrodes(
        self,
        marker="s",
        clr="silver",
        ax=None,
        figsize=(10, 5),
        axis_label_size=14,
        tick_label_size=12,
        dpi=100,
    ):
        # Scatter plot of electrode positions
        # TODO: add outline for needle?

        # Create new figure with specified size if no axis provided
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
            fig.dpi = dpi
        else:
            fig = None

        # Plot electrodes
        ax.scatter(self.chan_xy[:, 0], self.chan_xy[:, 1], marker=marker, color=clr)

        # If new figure, add axis labels
        if fig:
            ax.set_xlabel("position (mm)", fontsize=axis_label_size)
            ax.set_ylabel("position (mm)", fontsize=axis_label_size)
            ax.tick_params(axis="x", which="major", labelsize=tick_label_size)
            ax.tick_params(axis="y", which="major", labelsize=tick_label_size)

            # y axis limits
            max_y = np.abs(np.max(self.chan_xy[:, 1]))
            ylim_scale = 5
            ax.set_ylim(max_y * ylim_scale * -1, max_y * ylim_scale)

    def plot_fibre_potential_locations(
        self,
        motor_unit_idx=None,  # motor unit index; if None, plot all
        plot_electrodes=True,
        pt_size=10,
        pt_alpha=0.5,
        legend_pt_size=30,
        axis_equal=False,
        ax=None,
        lw=0.5,
        figsize=(10, 5),
        axis_label_size=14,
        tick_label_size=12,
        legend_label_size=12,
        dpi=100,
    ):
        # Scatter plot of all fibre potential locations
        # TODO: docstring, testing
        # TODO: keep axes the same when plotting subset of motor units

        # Create new figure with specified size if no axis provided
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
            fig.dpi = dpi
        else:
            fig = None

        # Add electrodes to plot
        if plot_electrodes:
            self.plot_electrodes(ax=ax)

        # Motor unit(s) to plot
        if motor_unit_idx is not None:
            motor_units = [self.motor_units[motor_unit_idx]]
        else:
            motor_units = self.motor_units

        for mu in motor_units:
            if mu.analysis_performed["fibres_localised"]:
                print(
                    f"Plotting fibre locations of motor unit {mu.motor_unit_number + 1}"
                )
                ax.scatter(
                    mu.fibre_centres[:, 0],
                    mu.fibre_centres[:, 1],
                    pt_size,
                    alpha=pt_alpha,
                    linewidth=0,
                    label=f"motor unit {mu.motor_unit_number + 1}",
                )

        # Legend
        lgnd = ax.legend(
            bbox_to_anchor=(1, 1),
            loc="upper left",
            frameon=False,
            handletextpad=0.25,
            fontsize=legend_label_size,
        )
        for h in lgnd.legend_handles:
            h._sizes = [legend_pt_size]

        # Axis and tick labels
        ax.set_xlabel("position (mm)", fontsize=axis_label_size)
        ax.set_ylabel("position (mm)", fontsize=axis_label_size)
        ax.tick_params(axis="x", which="major", labelsize=tick_label_size)
        ax.tick_params(axis="y", which="major", labelsize=tick_label_size)

        # Equal aspect ratio
        if axis_equal:
            ax.axis("equal")

        return fig, ax

    def cluster_fibre_potentials(self, motor_unit_idx: int, random_state: int = 0):
        """
        Cluster the fibre potentials and compute median fibre locations of the
        specified motor unit.

        Before this analysis is run, the motor unit's fibres potentials must be
        identified and localised using the reconstruct_fibres method of the
        EMGAnalysisReconstruct class.

        Running this method populates the fibre_clustering_results dictionary attribute
        with the following key/value pairs:
            mean_n_fps (int): mean number of fibre potentials across all motor unit
            potentials used in the localisation analysis. Used as input for clustering.

            n_fibre_clusters (int): number of clusters found; may slightly differ from
            mean_n_fps.

            fibre_clusters (npt.NDArray[np.int32], size (self.fibre_potentials,) ):
                cluster assignment of each fibre potential

            n_fps_per_mup_and_cluster (npt.NDArray[np.float64],
                                       size (self.n_potentials, n_fibre_clusters)):
            Number of fibre potentials (FPs) in each motor unit potential (MUP) that
            have the same cluster assignment.

            mup_fibre_pos (npt.NDArray[np.float64],
                           size(self.n_potentials, 2, n_fibre_clusters)):
            Location estimates ((x,y) coordinates) of each fibre based on each MUP. If
            the fibre is not found in the MUP, the coordinates are np.nan.

            fibre_centres_median (npt.NDArray[np.float64], size(n_fibre_clusters, 2)):
            Median coordinates of each fibre.

        Parameters
        ----------
        motor_unit_idx : int
            Index of motor unit to use to perform fibre clustering.
        random_state : int
            Determines random number generation for centroid initialization; passed to
            k-means algorithm

        Raises
        ------
        RuntimeError
            Raised if localisation analysis has not been performed on requested motor
            unit.

        Returns
        -------
        None.

        TODO: test that analysis reproduces original MATLAB code; some variation
        expected since k-means is not deterministic (unless initialisation is fixed),
        but results should be qualitatively the same.

        TODO: add additional measures needed for downstream analysis/reports/vis - check
        with SM before implementing to determine what is needed.
         - position changes (based on position change between consecutive MUPs) to get a
         measure of variability in location estimate (will need to remove nan positions
        in mup_fibre_pos before computing)
         - distances between fibres (can also add as a separate method)

        TODO: check other k-means parameters; determine if any defaults should be
        changed. Also evaluate clustering performance and determine if approach needs to
        be modified (e.g., how number of clusters is determined)


        """

        # Get motor unit
        motor_unit = self.motor_units[motor_unit_idx]

        # Check that localisation has been run
        if not motor_unit.analysis_performed["fibres_localised"]:
            raise RuntimeError(
                "Localisation analysis has not been performed; cannot cluster fibres."
            )

        # Onset indices of all MUPs that have fibre potentials
        unique_onsets = np.unique(motor_unit.onsets)
        n_unique_onsets = len(unique_onsets)

        # Use rounded mean number of fibre potentials (FPs) per motor unit potential as
        # k for clustering
        mean_n_fps = round(len(motor_unit.onsets) / n_unique_onsets)

        if mean_n_fps > 0:
            fibre_kmeans = KMeans(n_clusters=mean_n_fps, random_state=random_state).fit(
                motor_unit.fibre_centres
            )

            # fibre cluster assignments
            n_fibre_clusters = np.max(fibre_kmeans.labels_) + 1
            fibre_clusters = fibre_kmeans.labels_

            # Initialise arrays for storing results

            # Number of fibre potentials (FPs) in each MUP that belong to the same
            # cluster
            n_fps_per_mup_and_cluster = np.zeros(
                (motor_unit.n_potentials, n_fibre_clusters)
            )

            # Location estimates of each fibre based on each MUP
            # Note: unlike original code, data stored so indices match the
            # self.potentials_t_idx array
            mup_fibre_pos = np.full(
                (motor_unit.n_potentials, 2, n_fibre_clusters), np.nan
            )

            # Find median location of each fibre
            for cluster_num in np.arange(n_fibre_clusters):
                # Sometimes multiple fibre potentials in the same MUP are assigned to
                # the same fibre clusters. Therefore, first compute average (mean)
                # position in each MUP in which the fibre cluster appears.
                # If no fibres with that cluster num appear in the MUP, position is
                # stored as np.nan.

                # Note: unlike original code, iterate through all MUPs (not just ones
                # present in "onsets") so dimensions align to other MUP features.
                for mup_num in np.arange(motor_unit.n_potentials):
                    mup_onset = motor_unit.potentials_t_idx[mup_num]

                    # Fibre potentials that belong to the specified onset and cluster.
                    idx = np.flatnonzero(
                        np.all(
                            (
                                (motor_unit.onsets == mup_onset),
                                (fibre_clusters == cluster_num),
                            ),
                            axis=0,
                        )
                    )

                    # Store number of fibre potentials found
                    n_idx = len(idx)
                    n_fps_per_mup_and_cluster[mup_num, cluster_num] = n_idx

                    # Compute average position of the fibre based on the specified MUP
                    if n_idx > 0:
                        pos = motor_unit.fibre_centres[idx, :]
                        mup_fibre_pos[mup_num, :, cluster_num] = np.mean(pos, axis=0)

            # Compute median fibre positions
            fibre_centres_median = np.transpose(np.nanmedian(mup_fibre_pos, axis=0))

            # Store results as dictionary
            motor_unit.fibre_clustering_results = {
                "mean_n_fps": mean_n_fps,
                "n_fibre_clusters": n_fibre_clusters,
                "fibre_clusters": fibre_clusters,
                "n_fps_per_mup_and_cluster": n_fps_per_mup_and_cluster,
                "mup_fibre_pos": mup_fibre_pos,
                "fibre_centres_median": fibre_centres_median,
            }


class EMGAnalysisReconstructSettings:
    """
    Class for storing EMG Analysis reconstruct settings.

    """

    def __init__(self):
        """
        Initialise settings.

        Returns
        -------
        None.

        """

        # Default settings
        self.trigger_channel = -1
        self.exhaustive = False
        self.offset = 0.3000
        self.prune = False
        self.prune_xlim = np.array([-0.5000, 19.2000, 0.5000])
        self.prune_ylim = np.array([-2, 2])
        self.mavg_length = 1
        self.mavg_all = False
        self.localise_first = False
        self.spike_dur = 20
        self.half_subsample_size = 200
        self.max_opt_iterations = 200
        self.xtol = 0.01
        self.ftol = 1
        self.needle_type = "nonlinear"

    def __str__(self):
        """
        Return a string for the object

        Returns
        -------
        String

        """

        ans = "EMG Analysis Reconstruct Settings"
        ans += "\nTrigger channel: "
        ans += str(self.trigger_channel)
        ans += "\nExhaustive: "
        ans += str(self.exhaustive)
        ans += "\nOffset: "
        ans += str(self.offset)
        ans += "\nPrune: "
        ans += str(self.prune)
        ans += "\nPrune x limits: "
        ans += str(self.prune_xlim)
        ans += "\nPrune y limits: "
        ans += str(self.prune_ylim)
        ans += "\nMoving average length: "
        ans += str(self.mavg_length)
        ans += "\nMoving average all: "
        ans += str(self.mavg_all)
        ans += "\nLocalise first: "
        ans += str(self.localise_first)
        ans += "\nSpike duration: "
        ans += str(self.spike_dur)
        ans += "\nHalf subsample size: "
        ans += str(self.half_subsample_size)
        ans += "\nMaximum optimisation steps: "
        ans += str(self.max_opt_iterations)
        ans += "\nOptimisation parameter tolerance: "
        ans += str(self.xtol)
        ans += "\nOptimisation function value tolerance: "
        ans += str(self.ftol)
        ans += "\nNeedle type: "
        ans += str(self.needle_type)

        ans += "\n"

        return ans


class EMGAnalysisReconstruct:
    """
    Class for performing reconstruct analysis

    """

    def __init__(
        self, emg_data_preproc: EMGDataPreproc, settings: EMGAnalysisReconstructSettings
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
        self.settings = settings
        self.n_chan = self.emg_data_preproc.n_chan

        # SNRs: The SNR values for each channel
        self.signal_noise_ratios = np.array([])
        # ranks: The rank of each channel on highest SNR
        self.signal_noise_ratios_ranks = np.array([])

        # Found by running find_motor_units
        # TODO: rename these attributes and/or remove (store in MU class instead)
        self.indices = np.array([])
        self.locs = np.array([])

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

    def load_motor_unit_data_from_matlab(
        self, filename_indices, filename_locs, set_unbroken=True
    ):
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
            self.indices = list(
                csv.reader(x, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
            )

        with open(filename_locs, "r") as x:
            self.locs = list(csv.reader(x, delimiter=",", quoting=csv.QUOTE_NONNUMERIC))

        self.locs = (np.array(self.locs)).flatten()
        self.indices = (np.array(self.indices)).flatten()
        self.indices = np.round(self.indices - 1)
        self.locs = np.round(self.locs - 1)

        if set_unbroken:
            # Set all to non broken like MATLAB analysis for this data
            self.emg_data_preproc.chan.analyse_chan = np.full(self.n_chan, True)

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
        Finds the motor units and records results in self.indices and self.locs
        self.locs motor unit labels, 0, 1, 2, ...
        self.indices indicates which motor unit against the used data

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
        if self.settings.trigger_channel >= 0:
            sig_ind = self.settings.trigger_channel
        else:
            if self.signal_noise_ratios[self.signal_noise_ratios_ranks[0]] > 0:
                sig_ind = self.signal_noise_ratios_ranks[0]
            else:
                raise Exception(
                    "Sorry, no channels with a calculable signal to noise ratio!"
                )
        self.chan_for_find_motor_units = sig_ind  # store channel for plots

        # Apply Multi-dimensional TK operator (Teager-Kaiser)
        # to return MUAPs in channel

        # Deep copy to ensure processing in TK_filter is not stored
        used_data = self.emg_data_preproc.emg_ts[sig_ind, :].copy()

        self.indices, self.locs = tk.TK_filter(used_data, sampling_freq)

        print(
            "MUs found: " + str(np.max(self.locs) + 1) + " via channel: " + str(sig_ind)
        )

        # Add motor unit objects
        self.add_motor_units(np.max(self.locs))

    def add_motor_units(self, no_motor_units):
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
        for i in range(np.max(self.locs)):
            motor_unit = EMGMotorUnit(
                number=i, potentials_t_idx=self.indices[self.locs == i]
            )
            all_motor_units.append(motor_unit)
        self.found_motor_units = EMGMotorUnits(
            all_motor_units, chan_xy=self.emg_data_preproc.chan.chan_xy
        )

    def plot_motor_units_raster(
        self,
        linelengths=0.9,
        linewidths=0.75,
        ax=None,
        figsize=(10, 5),
        dpi: int = 100,
        axis_label_size: float = 14,
        xtick_label_size: float = 12,
        ytick_label_size: float = 12,
        sort_by: str = "default",
    ):
        # Create a raster plot of the potentials of each motor unit in the recording.
        # TODO: full docstring, testing

        # TODO: if save whether analysis has been run, can provide more specific error
        # message (analysis has not been run vs has been run and no MUs found)
        if not self.found_motor_units:
            raise ValueError(
                "No motor units identified - confirm that analysis has been run."
            )

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
        # TODO: do the indices always match motor unit numbers? if not, should add as
        # attribute to EMGMotorUnits class so can easily find and select MUs using
        # their numeric labels
        #
        # TODO: docstring, testing
        #
        # n_ms is the approximate length of time to get for each motor unit (number of
        # samples on each side of onset are rounded up to nearest integer)

        if not self.found_motor_units:
            raise ValueError(
                "No motor units identified - confirm that analysis has been run."
            )

        # Calculate number of samples to get before and after MUP onset
        n_samples = int(np.ceil(self.emg_data_preproc.fs / 1000 * n_ms) / 2)

        # Motor unit
        motor_unit = self.found_motor_units.motor_units[motor_unit_idx]
        motor_unit.potentials_t_idx

        # Get potentials from EMG recording data
        # dimensions are channels x time x MUP
        potentials_data = np.full(
            (self.emg_data_preproc.n_chan, n_samples * 2, motor_unit.n_potentials),
            np.nan,
        )

        for i in np.arange(motor_unit.n_potentials):
            # Note that index excludes stop_t sample, which keeps the length to n_ms
            start_t = motor_unit.potentials_t_idx[i] - n_samples
            stop_t = motor_unit.potentials_t_idx[i] + n_samples

            # Only add potentials within boundaries of the time series
            if (start_t > 0) and (stop_t < self.emg_data_preproc.emg_ts.shape[1]):
                potentials_data[:, :, i] = self.emg_data_preproc.emg_ts[
                    :, start_t:stop_t
                ].copy()

        return potentials_data

    def plot_average_motor_unit_potential(
        self,
        motor_unit_idx: int,
        n_ms: int = 20,
        offset=500,
        ax=None,
        lw=0.5,
        figsize=(7, 7),
        axis_label_size: float = 10,
        ytick_label_size=6,
        xtick_label_size=8,
        dpi=100,
    ):
        # Time series plot of average motor unit potential of one motor unit
        # TODO: documentation, testing
        # TODO: averaging options? (mean vs median)

        if not self.found_motor_units:
            raise ValueError(
                "No motor units identified - confirm that analysis has been run."
            )

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
        potentials_data = self.get_potentials_data_of_one_motor_unit(
            motor_unit_idx, n_ms
        )
        potentials_avg = np.nanmean(potentials_data, axis=2)
        n_samples = potentials_avg.shape[1]

        # Time vector for x axis (ms)
        potentials_t = (np.arange(1, n_samples + 1) / self.emg_data_preproc.fs) * 1000

        # Plot each channel's MUP, staggered by the specified offset
        for i in range(self.emg_data_preproc.n_chan):
            ax.plot(potentials_t, potentials_avg[i, :] - offset * i, lw=lw)

        # Channel labels
        chan_y = np.arange(0, self.emg_data_preproc.n_chan * offset * -1, offset * -1)
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
        chan_idx: int = None,  # if none, uses channel used for finding motor units
        n_ms: int = 20,
        ax=None,
        lw=0.2,
        lw_mean=0.5,
        figsize=(7, 7),
        axis_label_size: float = 10,
        ytick_label_size=10,
        xtick_label_size=10,
        dpi=100,
    ):
        # Time series plot of all motor unit potentials of one motor unit in one channel
        # Average (mean) overlaid
        # TODO: documentation, testing
        # Note using channel index (counting from 0), not numeric label (counting from
        # 1)

        if not self.found_motor_units:
            raise ValueError(
                "No motor units identified - confirm that analysis has been run."
            )

        if not chan_idx:
            chan_idx = self.chan_for_find_motor_units

        # Create new figure with specified size if no axis provided
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
            fig.dpi = dpi
        else:
            fig = None

        # Get motor unit potentials and average (mean)
        potentials_data = self.get_potentials_data_of_one_motor_unit(
            motor_unit_idx, n_ms
        )
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
        # TODO: check label

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

        # Save the concurrent signal from all other channels for each spike
        all_spikes = np.zeros(
            (
                len(self.indices[self.locs == motor_unit_number]),
                self.n_chan,
                self.settings.half_subsample_size * 2 + 1,
            )
        )

        all_onsets = self.indices[self.locs == motor_unit_number]

        # Zero reused vars
        t = 0
        # self.opr = []

        for sample in range(len(self.indices)):
            if self.locs[sample] == motor_unit_number:
                # exclude spikes right at the edge of the recording
                if self.indices[sample] < (
                    self.settings.half_subsample_size + 1
                ) or self.indices[sample] > (
                    self.emg_data_preproc.emg_ts.shape[1]
                    - self.settings.half_subsample_size
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
                        int(
                            self.indices[sample] - self.settings.half_subsample_size
                        ) : int(
                            self.indices[sample] + self.settings.half_subsample_size + 1
                        ),
                    ]

                t += 1

        print("MU" + str(motor_unit_number) + ": firings: " + str(t))

        if self.settings.mavg_all:
            self.settings.mavg_length = all_spikes.shape[0] - 1
        elif t < self.settings.mavg_length or t < 2:
            # if there aren't enough spikes to model the MU, skip it
            print("Too few firings found to model this motor unit")
            return

        mean_spikes = np.squeeze(np.mean(all_spikes, axis=0))
        pos = np.zeros((0, 2))
        onsets = np.array([])

        if self.settings.localise_first:
            max_signal_id = 0
        else:
            max_signal_id = all_spikes.shape[0] - self.settings.mavg_length

        for signal_id in range(max_signal_id):
            if self.settings.localise_first:
                sig = np.squeeze(
                    all_spikes[
                        signal_id : (signal_id + self.settings.mavg_length + 1), :, :
                    ]
                )
            else:
                sig = np.squeeze(
                    np.mean(
                        all_spikes[
                            signal_id : (signal_id + self.settings.mavg_length + 1),
                            :,
                            :,
                        ],
                        axis=0,
                    )
                )

            # sub_clusters = self.find_peaks_2d_highest(sig)
            sub_clusters = self.find_peaks_2d(sig)

            if sub_clusters.shape[0] == 0:
                continue

            for sub_cluster_index in range(sub_clusters.shape[0]):
                # Ensure we don't get spikes outside of recording duration
                time_peak = np.max(
                    np.hstack(
                        (
                            sub_clusters[sub_cluster_index, 0],
                            self.settings.spike_dur + 1,
                        )
                    )
                )
                time_peak = np.min(
                    np.hstack(
                        (
                            time_peak,
                            self.settings.half_subsample_size * 2
                            - self.settings.spike_dur,
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
                        int(time_peak - self.settings.spike_dur) : int(
                            time_peak + self.settings.spike_dur + 1
                        ),
                    ]
                ).T

                # Needle model pos in mm
                self.build_needle_model()

                # Scaling factor from mm to scaled AU
                self.needle = self.needle * 4
                x0 = self.needle[int(peak_electrode), :]
                self.needle = self.needle[included_electrodes, :]

                # Non-linear optimisation algorithm for fibre positioning
                opt_paras = opt.fmin(
                    self.deconv_wrapper,
                    x0=x0,
                    maxiter=self.settings.max_opt_iterations,
                    full_output=False,
                    xtol=self.settings.xtol,
                    ftol=self.settings.ftol,
                    disp=False,
                )

                pos = np.vstack((pos, opt_paras))

                onsets = np.append(onsets, all_onsets[signal_id])

        # End of signal_id loop

        pos[:, 0] = pos[:, 0] / 4

        # Add the results to the motor unit object
        if pos.shape[0] > 0:
            motor_unit = self.found_motor_units.motor_units[motor_unit_number]
            motor_unit.add_fibre_localisation(
                fibre_centres=pos,
                mean_spikes=mean_spikes,
                onsets=onsets,
                all_spikes=all_spikes,
                gn_potential=np.array(np.transpose(self.opr)),
            )

    def plot_MUs(self, used_data, indices, locs):
        """
        Plot MUs for testing purposes

        Parameters
        ----------
        Index : 1D numpy NDArray[int]
                Index of MUAPs clustered
        loc : 1D numpy NDArray[int]
                location of the MUAPs in the signal

        Returns
        -------
        None

        """

        no_MUs = np.max(locs) + 1
        xmax = len(used_data)
        ymin = np.min(used_data)
        ymax = np.max(used_data)

        plt.subplots(no_MUs, 1)

        # Loop thro' MUs
        for one_MU in range(no_MUs):
            # Plot subplot
            plt.subplot(no_MUs, 1, one_MU + 1)
            # Get subset for this MU
            subset_MU = one_MU == locs
            # Get index positions for this MU
            positions = indices[subset_MU]
            plt.plot(indices[subset_MU], used_data[positions], "k-", linewidth=1)
            plt.xlim(0, xmax)
            plt.ylim(ymin, ymax)

        # Save the plot
        # Firstly ensure the execution path is the same as the file path
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)

        # Save all images in the Images folder
        plt.savefig(os.path.join(dname, "MUs.png"), format="png")

        # Close the plot
        plt.close()

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

        data = image  # scipy.misc.imread(fname)

        data_max = filters.maximum_filter(data, neighborhood_size)
        maxima = data == data_max
        data_min = filters.minimum_filter(data, neighborhood_size)
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

    def find_peaks_2d_package(self, image, threshold):
        """
        Finds local maxima of a 2-dimensional image area
        Dependent on findpeaks algorithm from findpeaks package
        See https://erdogant.github.io/findpeaks/pages/html/Topology.html
        Parameters
        ----------
        signal: 2D numpy NDArray[float, float]
                n*m array of signal data
        threshold: float
                cutoff for defining a peak
        Returns
        -------
        locs: 2D numpy NDArray[int, int]
            2D array of location of peaks
        """

        # Initialize
        fp = findpeaks(
            whitelist=["peak"],
            togray=False,
            limit=threshold,
            denoise=None,
            scale=False,
            lookahead=50,
        )

        ans = fp.fit(image)
        ans = ans["persistence"]

        return np.array(ans.loc[ans["peak"], ["x", "y"]])

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

        # Interpolate between the electrodes in order to make gaussian filter
        # have roughly equal effect on distance as time
        # interp_n = 4

        # print(b.shape)
        sigma = 2
        im2 = np.abs(
            gaussian_filter(base, sigma, truncate=np.ceil(2 * sigma) / sigma)
        )  # imgaussfilt(b, 3))

        # tophat transform
        # Applying the Top-Hat operation
        # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6))
        # im2 = cv2.morphologyEx(im, cv2.MORPH_TOPHAT, kernel)

        # im2 = im

        # Extract each blob
        locs = np.array([])
        found = False
        parse_limit = 0
        im2_max = np.max(im2)
        max_number_of_peaks = 22

        while not found:
            parse_limit = parse_limit + 1
            # locs = self.find_peaks_2d_package(im2, im2_max * threshold)
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

    def find_peaks_2d_highest(self, sig):
        """
        Finds only the highest maxima of a 2-dimensional image area
        after applying a filter

        Parameters
        ----------
        signal: 2D numpy NDArray[float, float]
                n*m array of signal data
        threshold: float
                cutoff for defining a peak as a prop
        Returns
        -------
        locs: 2D numpy NDArray[int, int]
            2D array of location of peaks
        """

        base = sig
        # remove negative deflection to discount 'doubling peaks'
        # from negative initial deflection of SFAP
        base[base < 0] = 0

        sigma = 2
        im = np.abs(
            gaussian_filter(base, sigma, truncate=np.ceil(2 * sigma) / sigma)
        )  # imgaussfilt(b, 3))

        # Get coords of maximum in image
        loc = np.unravel_index(np.argmax(im), im.shape)

        # Reverse coords so that they are in the order needed later
        loc = loc[::-1]

        return np.array(loc).reshape(1, 2)

    def plot_2d_peaks(self, im, peak_locs):
        """
        Method to plot 2D image and found peaks from the find_peaks_2d method
        for testing purposes

        Parameters
        ----------
        im: 2D numpy NDArray[float, float]
            2D array of image
        locs: 2D numpy NDArray[int, int]
            2D array of location of peaks

        Returns
        -------
        None
        """

        _, ax = plt.subplots()
        im = ax.imshow(im)
        ax.plot(peak_locs[:, 0], peak_locs[:, 1], "bX")

        plt.show()

    def build_needle_model(self):
        """
        Build model for the needle stored in the object self.needle
        Method to build a needle structure.
        needle_type: 'linear' the electrodes are placed on a line with a spacing of 200
                      mu Meter
                     'nonlinear' the electrodes are placed on either side of the needle
                      in a zig zag way 200mu Meter seperate between the electrodes
        Orignal MATLAB Author: Bashar Awwad ShiekH Hasan, Newcastle University

        all the dimensions are relative to the tip of the needle, all distances
        in mm needle width is set to 0.36 mm (provided by Enrique)

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        self.needle = np.zeros((self.n_chan, 2))
        nwidth = 0.36

        if self.settings.needle_type == "nonlinear":
            # the tip of the needle is assumed to be 1 mm far from
            # the first electrode on the x axis
            baseX = 0.3
            baseY = 0
            for i in range(self.n_chan):
                self.needle[i, 0] = baseX + self.settings.offset

                if baseY <= 0:
                    self.needle[i, 1] = nwidth * 0.5
                else:
                    self.needle[i, 1] = -nwidth * 0.5

                baseX = self.needle[i, 0]
                baseY = self.needle[i, 1]
        else:
            # the tip of the needle is assumed to be 1 mm far
            # from the first electrode on the x axis
            baseX = 0.8

            for i in range(self.n_chan):
                # add interElectrodeDist
                self.needle[i, 0] = baseX + self.settings.offset
                self.needle[i, 1] = 0
                baseX = self.needle[i, 0]

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

        cn = self.calc_cn(loc[0], loc[1], self.settings.half_subsample_size * 2)

        iterable = (
            self.tconv(cn[:, k], self.sn[:, k], self.settings.spike_dur * 2 + 1)
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
