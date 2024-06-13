#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGAnalysisReconstruct for localisation.

For use with preprocessed EMG data.

"""

from __future__ import annotations  # for type hints - must be at beginning of file

import numpy as np
import numpy.typing as npt  # for type hints

import matplotlib.pyplot as plt
from matplotlib import colormaps
from sklearn.cluster import KMeans


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
                This is the motor unit index (0, 1, 2, ...), returned from TK_filter,
                which corresponds to the index position of
                "motor_units" in the EMGMotorUnits class. When displayed to the user
                the motor unit label
                is displayed which is +1 this number, e.g. motor_unit_number 0 is the
                motor unit labelled as "1"

        potentials_t_idx: npt.NDArray[np.int64]
                Time indices of the motor unit's potentials in the EMG recording

        Returns
        -------
        None

        """

        self.motor_unit_number = number

        # Number of potentials (firings) assigned to MU
        self.n_potentials = len(potentials_t_idx)
        # Time indices of potentials in EMG
        self.potentials_t_idx = potentials_t_idx

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
        self.fibre_centres = np.array([])

        # Onset indices of MUPs that each fibre potential (peak) belongs to
        # One for each fibre potential     
        self.mup_onsets = np.array([])

        # Fibre potential peak times relative to the onset time
        # of the corresponding MUP that it belongs to (in indices units, not seconds) 
        self.fibre_potential_times = np.array([])
        
        # Time series for each MUP and channel
        # (size: n MU potentials x n chan x time)       
        self.all_spikes = np.array([])

        # Generator potential, represents true underlying potential
        self.generator_potential = np.array([])

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
        ans += str(self.motor_unit_number + 1)
        ans += "\nNumber of potentials: "
        ans += str(self.n_potentials)
        ans += "\nFibre centres dimensions: "
        ans += str(self.fibre_centres.shape)
        ans += "\nmup_onsets dimensions: "
        ans += str(self.mup_onsets.shape)
        ans += "\nFibre potential times dimensions: "
        ans += str(self.fibre_potential_times.shape)
        ans += "\nAll spikes dimensions: "
        ans += str(self.all_spikes.shape)
        ans += "\nGenerator potential dimensions: "
        ans += str(self.generator_potential.shape)

        ans += "\n"

        return ans

    def add_fibre_localisation(self, fibre_centres, mup_onsets, fibre_potential_times, all_spikes, generator_potential):
        """
        Add results of the fibre localisation step to the motor unit object. Computes
        additional attributes and stores that analysis has been performed.

        Called during EMGAnalysisReconstruct method, reconstruct_fibres

        Parameters
        ----------
        fibre_centres : TYPE
            DESCRIPTION.
        mup_onsets : npt.NDArray[np.int64]
            Onset indices of the MUPs (firings) relative to the overall time
        fibre_potential_times : npt.NDArray[np.int64]
            Fibre potential peak times relative to the onset (overall) time
            of the corresponding MUP (listed above in mup_onsets) 
        all_spikes : TYPE
            DESCRIPTION.
        generator_potential : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """

        # Note analysis performed
        self.analysis_performed["fibres_localised"] = True

        # Store number of fibre potentials (i.e., peaks in the MUPs) found
        self.n_fibre_potentials = fibre_centres.shape[0]

        # Store provided attributes
        self.fibre_centres = fibre_centres
        self.mup_onsets = mup_onsets
        self.fibre_potential_times = fibre_potential_times
        self.all_spikes = all_spikes
        self.generator_potential = generator_potential

    def _calculate_fibre_potentials_time_diff(self, fib_pot_pos1, fib_pot_pos2):
        """      
        Parameters
        ----------
        fib_pot_pos1: int
            index of the first fibre potential in fibre_potential_times
        fib_pot_pos2: int
            index of the second fibre potential in fibre_potential_times
            
        Returns
        -------
        int
            length of time interval between the two fibre potentials
            return as a multiple of the number of time steps i.e. indices
            
        """
             
        return np.abs(self.fibre_potential_times[fib_pot_pos2] - self.fibre_potential_times[fib_pot_pos1])
        
    def jitter_analysis_between_two_fibres(self, fibre1_num = 0, fibre2_num = 1):
        """
        Performs jitter analysis for this motor unit (MU). For the identified
        fibres computes the mean consecutive difference (MCD) between each pair
        of fibre. Firstly one fibre potential is chosen for each fibre and
        then the time difference is taken between them for the first MUP.
        This time interval is compared with the time interval for the next MUP
        by taking the absolute difference - and so on until the second last MUP.
        The mean of these differences is the MCD.
        
        MCD = (1/(N-1)) * sum(|D_k - D_{k+1}|) for k = 1 to N-1, where D_k is the kth
        MUP time difference between the fibre potentials for the 2 fibres in question.
       
        self.fibre_clustering_results = {
                "mean_n_fps": mean_n_fps,
                "n_fibre_clusters": n_fibre_clusters,
                "fibre_clusters": fibre_clusters,
                "n_fps_per_mup_and_cluster": n_fps_per_mup_and_cluster,
                "mup_fibre_pos": mup_fibre_pos,
                "fibre_centres_median": fibre_centres_median,
            }
            
        Parameters
        ----------
        fibre1_num : int
            Fibre number for the first fibre, given previously from cluster analysis (0,1,2,...)
        fibre2_num : int
            Fibre number for the second fibre
            
        Returns
        -------
        None.

        """
        
        # TODO add analysis to pick which fibre potentails to use   
        # Which fibre potentials to use for each MUP and fibre
        # Just use first one for now
        fibre1_potential_to_use = 0
        fibre2_potential_to_use = 0
        
        # Length of time intervals between fibre potentials in the two different fibres
        fibre_potential_time_diffs = np.full(len(self.mup_onsets), np.nan)
                          
        # Compute length of time intervals between fibre potentials
        for mup_num in range(self.n_potentials):
            mup_onset_idx = self.potentials_t_idx[mup_num]
            
            # Fibre potentials that belong to the specified MUP and fibre (cluster).
            fibre1_potentials_idx = np.flatnonzero(
                np.all(
                    (
                        (self.mup_onsets == mup_onset_idx),
                        (self.fibre_clustering_results["fibre_clusters"] == fibre1_num),
                    ),
                    axis=0,
                )
            )
            
            fibre2_potentials_idx = np.flatnonzero(
                np.all(
                    (
                        (self.mup_onsets == mup_onset_idx),
                        (self.fibre_clustering_results["fibre_clusters"] == fibre2_num),
                    ),
                    axis=0,
                )
            )
            
            if len(fibre1_potentials_idx) > 0 and len(fibre2_potentials_idx) > 0:
                  
                #Get time difference for this MUP between fibre potentials
                fib_pot_pos1 = fibre1_potentials_idx[fibre1_potential_to_use]
                fib_pot_pos2 = fibre2_potentials_idx[fibre2_potential_to_use]
                fibre_potential_time_diffs[mup_num] = self._calculate_fibre_potentials_time_diff(fib_pot_pos1, fib_pot_pos2)
            
        # Compute consecutive differences
        consecutive_diffs = np.full((len(self.mup_onsets) - 1), np.nan)
        
        for mup_num in range(self.n_potentials - 1):
            if not np.isnan(fibre_potential_time_diffs[mup_num]) and not np.isnan(fibre_potential_time_diffs[mup_num + 1]):
                consecutive_diffs[mup_num] = np.abs(fibre_potential_time_diffs[mup_num] - fibre_potential_time_diffs[mup_num + 1])
            
        # Compute mean consecutive difference and convert to seconds
        mean_consecutive_diff = np.nanmean(consecutive_diffs) / self.emg_data_preproc.fs

        return mean_consecutive_diff

    def jitter_analysis(self):
        """
        Do jitter analysis betwwen all pairs
        """
        
        # Check that localisation and fibre clustering has been run
        if not self.analysis_performed["fibres_localised"] or not self.analysis_performed["fibres_clustered"]:
            raise RuntimeError(
                "Localisation analysis and fibre cluster analysis must be performed before jitter analysis!"
            )
          
        if self.n_potentials < 2:
            raise RuntimeError(
                "Not enough MUPs to perform jitter analysis!"
            )
        
        #if self.n_fibre_clusters < 2:
        #    raise RuntimeError(
        #        "Not enough fibres to perform jitter analysis!"
        #    )
        
        fibre1_numbers = np.array([])
        fibre2_numbers = np.array([])
        mean_consecutive_diffs = np.array([])
        
        n_fibre_clusters = self.fibre_clustering_results["n_fibre_clusters"]
        count = 0
        
        for fibre1_num in range(n_fibre_clusters - 1):
            for fibre2_num in np.arange(fibre1_num + 1, fibre1_num + 2):               
                mean_consecutive_diffs[count] = self.jitter_analysis_between_two_fibres(fibre1_num, fibre2_num)
                fibre1_numbers[count] = fibre1_num
                fibre2_numbers[count] = fibre2_num
                count += 1
        
        self.fibre_jitter_results = {
                "fibre1_numbers": fibre1_numbers,
                "fibre2_numbers": fibre2_numbers,
                "mean_consecutive_diffs": mean_consecutive_diffs,
            }
        
        self.analysis_performed["fibres_jitter_computed"] = True
        

class EMGMotorUnits:
    """
    Class for storing and visualising all motor unit data returned from reconstruction
    analysis.

    Only includes visualisations that do not require the recording time series.

    """

    def __init__(self, motor_units: list[EMGMotorUnit], chan_xy: npt.NDArray[npt.float64]):
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

        # Channel/electrode coordinates of the needle
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
        """
        Plot electrode locations using their (x,y) coordinates.

        Electrodes are symbolised by grey squares by default.

        Parameters
        ----------
        marker : TYPE, optional
            DESCRIPTION. The default is "s".
        clr : TYPE, optional
            DESCRIPTION. The default is "silver".
        ax : TYPE, optional
            DESCRIPTION. The default is None.
        figsize : TYPE, optional
            DESCRIPTION. The default is (10, 5).
        axis_label_size : TYPE, optional
            DESCRIPTION. The default is 14.
        tick_label_size : TYPE, optional
            DESCRIPTION. The default is 12.
        dpi : TYPE, optional
            DESCRIPTION. The default is 100.
         : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        TODO: finish docstring once vis is finalised
        TODO: consider adding outline for needle

        """

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
        pt_facecolor=None,
        axis_equal=True,
        ax=None,
        lw=0.5,
        figsize=(10, 5),
        axis_label_size=14,
        tick_label_size=12,
        plot_legend=True,
        legend_pt_size=30,
        legend_label_size=12,
        dpi=100,
        cmap=None,
    ):
        """
        Create scatter plot of fibre localisations estimated from all fibre potentials
        (i.e., before clustering step). Can either plot fibre locations of all motor
        unit potentials or one, specified motor unit potential.

        Default point colour depends on the motor unit number.

        Parameters
        ----------
        motor_unit_idx : TYPE, optional
            DESCRIPTION. The default is None.
        # motor unit index; if None : TYPE
            DESCRIPTION.
        plot all        plot_electrodes : TYPE, optional
            DESCRIPTION. The default is True.
        pt_size : TYPE, optional
            DESCRIPTION. The default is 10.
        pt_alpha : TYPE, optional
            DESCRIPTION. The default is 0.5.
        pt_facecolor : TYPE, optional
            DESCRIPTION. The default is None.
        axis_equal : TYPE, optional
            DESCRIPTION. The default is True.
        ax : TYPE, optional
            DESCRIPTION. The default is None.
        lw : TYPE, optional
            DESCRIPTION. The default is 0.5.
        figsize : TYPE, optional
            DESCRIPTION. The default is (10, 5).
        axis_label_size : TYPE, optional
            DESCRIPTION. The default is 14.
        tick_label_size : TYPE, optional
            DESCRIPTION. The default is 12.
        plot_legend : TYPE, optional
            DESCRIPTION. The default is True.
        legend_pt_size : TYPE, optional
            DESCRIPTION. The default is 30.
        legend_label_size : TYPE, optional
            DESCRIPTION. The default is 12.
        dpi : TYPE, optional
            DESCRIPTION. The default is 100.
        cmap : TYPE, optional
            DESCRIPTION. The default is None.
         : TYPE
            DESCRIPTION.

        Returns
        -------
        fig : TYPE
            DESCRIPTION.
        ax : TYPE
            DESCRIPTION.

        TODO: finish docstring
        TODO: add option for fixing axis limits across different motor units.

        """

        # Default colormap - will use if colors not specified
        if cmap is None:
            cmap = colormaps["tab10"].colors

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
            # Default color for motor unit - differs depending on motor unit
            if pt_facecolor is None:
                idx = mu.motor_unit_number % (int(len(cmap)))
                mu_pt_facecolor = cmap[idx]
            else:
                mu_pt_facecolor = pt_facecolor

            if mu.analysis_performed["fibres_localised"]:
                print(f"Plotting fibre locations of motor unit {mu.motor_unit_number + 1}")
                ax.scatter(
                    mu.fibre_centres[:, 0],
                    mu.fibre_centres[:, 1],
                    pt_size,
                    alpha=pt_alpha,
                    linewidth=0,
                    facecolor=mu_pt_facecolor,
                    label=f"motor unit {mu.motor_unit_number + 1}",
                )

        # Legend
        if plot_legend:
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


        TODO: add additional measures needed for downstream analysis/reports/vis - check
        with SM before implementing to determine what is needed.
         - position changes (based on position change between consecutive MUPs) to get a
         measure of variability in location estimate (will need to remove nan positions
        in mup_fibre_pos before computing)
         - distances between fibres (can also add as a separate method)

        TODO: check other k-means parameters; determine if any defaults should be
        changed. Also evaluate clustering performance and determine if approach needs to
        be modified (e.g., how number of clusters is determined)

        TODO: why is this method not in the motor unit class? - RH
        """

        # Get motor unit
        motor_unit = self.motor_units[motor_unit_idx]

        # Check that localisation has been run
        if not motor_unit.analysis_performed["fibres_localised"]:
            raise RuntimeError(
                "Localisation analysis has not been performed; cannot cluster fibres."
            )

        # Onset indices of all MUPs that have fibre potentials
        unique_mup_onsets = np.unique(motor_unit.mup_onsets)
        n_unique_mup_onsets = len(unique_mup_onsets)

        # Use rounded mean number of fibre potentials (FPs) per motor unit potential as
        # k for clustering
        mean_n_fps = round(len(motor_unit.mup_onsets) / n_unique_mup_onsets)

        print(len(motor_unit.mup_onsets))
        print(n_unique_mup_onsets)
        print("mean_n_fps")
        print(mean_n_fps)

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
            n_fps_per_mup_and_cluster = np.zeros((motor_unit.n_potentials, n_fibre_clusters))

            # Location estimates of each fibre based on each MUP
            # Note: unlike original code, data stored so indices match the
            # self.potentials_t_idx array
            mup_fibre_pos = np.full((motor_unit.n_potentials, 2, n_fibre_clusters), np.nan)
            print("shape")
            print(motor_unit.mup_onsets.shape)
            # Find median location of each fibre
            for cluster_num in np.arange(n_fibre_clusters):
                # Sometimes multiple fibre potentials in the same MUP are assigned to
                # the same fibre clusters. Therefore, first compute average (mean)
                # position in each MUP in which the fibre cluster appears.
                # If no fibres with that cluster num appear in the MUP, position is
                # stored as np.nan.

                # Note: unlike original code, iterate through all MUPs (not just ones
                # present in "mup_onsets") so dimensions align to other MUP features.
                for mup_num in np.arange(motor_unit.n_potentials):
                    mup_onset = motor_unit.potentials_t_idx[mup_num]

                    # Fibre potentials that belong to the specified onset and cluster.
                    idx = np.flatnonzero(
                        np.all(
                            (
                                (motor_unit.mup_onsets == mup_onset),
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
            motor_unit.analysis_performed["fibres_clustered"] = True

    def plot_fibre_potential_clustering_one_motor_unit(
        self,
        motor_unit_idx,
        plot_electrodes=True,
        pt_potentials_size=10,
        pt_potentials_alpha=0.5,
        pt_potentials_facecolor=None,
        pt_medians_size=50,
        pt_medians_marker="o",
        pt_medians_facecolor="none",
        pt_medians_edgecolor=None,
        pt_medians_lw=2.5,
        axis_equal=True,
        ax=None,
        lw=0.5,
        figsize=(10, 5),
        axis_label_size=14,
        tick_label_size=12,
        dpi=100,
        cmap=None,
    ):
        """
        Create scatter plot of fibre localisations estimated from all fibre potentials
        (i.e., before clustering step), with the location of each fibre (determined
        after clustering) overlaid. Plots results from one motor unit potential at a
        time.

        Default point colour depends on the motor unit number.

        Parameters
        ----------
        motor_unit_idx : TYPE
            DESCRIPTION.
        plot_electrodes : TYPE, optional
            DESCRIPTION. The default is True.
        pt_potentials_size : TYPE, optional
            DESCRIPTION. The default is 10.
        pt_potentials_alpha : TYPE, optional
            DESCRIPTION. The default is 0.5.
        pt_potentials_facecolor : TYPE, optional
            DESCRIPTION. The default is None.
        pt_medians_size : TYPE, optional
            DESCRIPTION. The default is 50.
        pt_medians_marker : TYPE, optional
            DESCRIPTION. The default is "o".
        pt_medians_facecolor : TYPE, optional
            DESCRIPTION. The default is "none".
        pt_medians_edgecolor : TYPE, optional
            DESCRIPTION. The default is None.
        pt_medians_lw : TYPE, optional
            DESCRIPTION. The default is 2.5.
        axis_equal : TYPE, optional
            DESCRIPTION. The default is True.
        ax : TYPE, optional
            DESCRIPTION. The default is None.
        lw : TYPE, optional
            DESCRIPTION. The default is 0.5.
        figsize : TYPE, optional
            DESCRIPTION. The default is (10, 5).
        axis_label_size : TYPE, optional
            DESCRIPTION. The default is 14.
        tick_label_size : TYPE, optional
            DESCRIPTION. The default is 12.
        dpi : TYPE, optional
            DESCRIPTION. The default is 100.
        cmap : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        TODO: finish docstring
        TODO: add option for fixing axis limits across different motor units.

        """

        # Default colors
        if cmap is None:
            cmap = colormaps["tab20"].colors
        idx = motor_unit_idx % (int(len(cmap) / 2))
        if pt_medians_edgecolor is None:
            pt_medians_edgecolor = cmap[2 * idx]
        if pt_medians_facecolor is None:  # note: differs from string 'none' --> no fill
            pt_medians_edgecolor = cmap[2 * idx]
        if pt_potentials_facecolor is None:
            pt_potentials_facecolor = cmap[2 * idx + 1]

        # Plot locations based on all fibre potentials
        fig, ax = self.plot_fibre_potential_locations(
            motor_unit_idx=motor_unit_idx,
            pt_size=pt_potentials_size,
            pt_alpha=pt_potentials_alpha,
            pt_facecolor=pt_potentials_facecolor,
            axis_equal=axis_equal,
            ax=ax,
            lw=lw,
            figsize=figsize,
            axis_label_size=axis_label_size,
            tick_label_size=axis_label_size,
            dpi=dpi,
            plot_legend=False,
        )

        # Plot larger markers for median fibre locations
        mu_clusters = self.motor_units[motor_unit_idx].fibre_clustering_results
        ax.scatter(
            mu_clusters["fibre_centres_median"][:, 0],
            mu_clusters["fibre_centres_median"][:, 1],
            pt_medians_size,
            marker=pt_medians_marker,
            facecolors=pt_medians_facecolor,
            edgecolors=pt_medians_edgecolor,
            linewidths=pt_medians_lw,
        )
