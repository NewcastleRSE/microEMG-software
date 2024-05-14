#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGAnalysisReconstruct for localisation.

For use with preprocessed EMG data.

"""
# TODO: remove noqa
# flake8: noqa

from __future__ import annotations  # for type hints - must be at beginning of file

# from xml.etree.ElementInclude import include
import numpy as np
import numpy.typing as npt  # for type hints


# import numpy.typing as npt
import scipy.signal as sg
import scipy.optimize as opt
from scipy.linalg import toeplitz
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt

# TODO: add csv and cv2 to poetry dependency management
# import csv
# import cv2
import os
import emg_analyser_python.emg_analyser_functions as tk
from emg_analyser_python.constants import QUICK_VERSION

# TODO: add findpeaks to poetry dependency managment if kept as dependency
# from findpeaks import findpeaks

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
        self.potentials_t_idx = potentials_t_idx  # Time indices of potentials in EMG
        self.n_potentials = len(potentials_t_idx)  # Number of potentials assigned to MU
        self.fibre_centres = np.array([])
        self.mean_spikes = np.array([])
        self.onsets = np.array([])
        self.all_spikes = np.array([])
        self.gn_potential = np.array([])

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


class EMGMotorUnits:
    """
    Class for storing all motor unit data
    returned from reconstruction analysis

    """

    def __init__(self, motor_units: list[EMGMotorUnit]):
        """
        Initialise EMGMotorUnits object.

        Parameters
        ----------
        motor_units : list[EMGMotorUnit]
            List of motor units (class EMGMotorUnit) to add to the EMGMotorUnits object.

        Returns
        -------
        None.

        """

        self.motor_units = motor_units
        self.n_motor_units = len(motor_units)

        # Get and store number of potentials of each motor unit
        self.n_potentials = [mu.n_potentials for mu in self.motor_units]

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
        self.n_electrodes = 0
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
        ans += "\nNumber of electrodes: "
        ans += str(self.n_electrodes)
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
        self.number_of_channels = self.emg_data_preproc.emg_ts.shape[0]

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
        self.found_motor_units = []

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
            self.emg_data_preproc.chan.analyse_chan = np.full(
                self.number_of_channels, True
            )

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
        self.signal_noise_ratios = np.zeros(self.number_of_channels)

        for channel in range(self.number_of_channels):
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

        # Apply Multi-dimensional TK operator (Teager-Kaiser)
        # to return MUAPs in channel
        used_data = self.emg_data_preproc.emg_ts[sig_ind, :]

        self.indices, self.locs = tk.TK_filter(used_data, sampling_freq)

        print(
            "MUs found: " + str(np.max(self.locs) + 1) + " via channel: " + str(sig_ind)
        )

        # Create motor unit objects for each motor unit
        all_motor_units = []
        for i in range(np.max(self.locs)):
            motor_unit = EMGMotorUnit(
                number=i, potentials_t_idx=self.indices[self.locs == i]
            )
            all_motor_units.append(motor_unit)
        self.found_motor_units = EMGMotorUnits(all_motor_units)

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
                self.settings.n_electrodes,
                self.settings.half_subsample_size * 2 + 1,
            )
        )

        all_onsets = self.indices[self.locs == motor_unit_number]

        # Zero reused vars
        t = 0
        self.opr = []

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

                for channel in range(self.settings.n_electrodes):
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

        print("MU" + str(motor_unit_number) + ": firings: " + str(t + 1))

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
                peak_stop = np.min(
                    np.hstack((peak_electrode + 3, self.settings.n_electrodes - 1))
                )

                included_electrodes = np.arange(peak_start, peak_stop + 1, dtype="int")

                # Remove bad channels
                good_channels = (
                    np.arange(0, self.settings.n_electrodes, dtype="int")
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
            motor_unit.fibre_centres = pos
            motor_unit.mean_spikes = mean_spikes
            motor_unit.onsets = onsets
            motor_unit.all_spikes = all_spikes
            motor_unit.gn_potential = self.opr

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

    def findpeaks_2d_package_1(self, image, threshold):
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

    def findpeaks_2d_package_0(self, image, threshold):
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

    def find_peaks_2d_0(self, sig):
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
        im = np.abs(
            gaussian_filter(base, sigma, truncate=np.ceil(2 * sigma) / sigma)
        )  # imgaussfilt(b, 3))

        # tophat transform
        # Applying the Top-Hat operation
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6))
        im2 = cv2.morphologyEx(im, cv2.MORPH_TOPHAT, kernel)

        # Extract each blob
        locs = np.array([])
        found = False
        parse_limit = 0
        im2_max = np.max(im2)
        max_number_of_peaks = 22

        while not found:
            parse_limit = parse_limit + 1
            locs = self.find_peaks_2d_package_0(im2, im2_max * threshold)

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

    def find_peaks_2d(self, sig):
        """
        Finds local maxima of a 2-dimensional image area
        Dependent on findpeaks algorithm from findpeaks package

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


        Returns
        -------

        """

        self.needle = np.zeros((self.settings.n_electrodes, 2))
        nwidth = 0.36

        if self.settings.needle_type == "nonlinear":
            # the tip of the needle is assumed to be 1 mm far from
            # the first electrode on the x axis
            baseX = 0.3
            baseY = 0
            for i in range(self.settings.n_electrodes):
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

            for i in range(self.settings.n_electrodes):
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
        self.opr = np.zeros((self.settings.spike_dur * 2 + 1, self.no_needle_channels))

        cn = self.calc_cn(loc[0], loc[1], self.settings.half_subsample_size * 2)

        for k in range(self.no_needle_channels):
            self.opr[:, k] = self.tconv(
                cn[:, k], self.sn[:, k], self.settings.spike_dur * 2 + 1
            )

        total_var = -np.reciprocal(np.max(np.var(self.opr, axis=1, ddof=1)))

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
