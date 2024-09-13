#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGAnalysisReconstruct for localisation.

For use with preprocessed EMG data.

"""

from __future__ import annotations

import numpy.typing as npt
from typing import Optional, Any
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
from matplotlib import colormaps
from sklearn.cluster import KMeans
import scipy.stats

import seaborn as sns
import warnings
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms

from sklearn.mixture import GaussianMixture
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import silhouette_score
from sklearn.cluster import DBSCAN

from pymicroemg.emg_reconstruct_settings import EMGAnalysisMotorUnitClusterSettings
from pymicroemg.emg_reconstruct_settings import EMGAnalysisMotorUnitJitterSettings


class EMGMotorUnit:
    """
    Class for storing data for one motor unit
    returned from reconstruction analysis.

    """

    def __init__(
        self,
        number: int,
        potentials_t_idx: npt.NDArray[np.int64],
        fs: float,
        chan_xy: npt.NDArray[np.float64],
    ):
        """
        Initialise EMGMotorUnit object.

        Parameters
        ----------
        number: int
            This is the motor unit index (0, 1, 2, ...), returned from TK_filter,
            which corresponds to the index position of "motor_units" in the
            EMGMotorUnits class. When displayed to the user the motor unit label
            is displayed which is +1 this number, e.g. motor_unit_number 0 is the
            motor unit labelled as "1".
        potentials_t_idx: npt.NDArray[np.int64]
            Time indices of the motor unit's potentials in the EMG recording.
        fs : float
            Sampling frequency (Hz) of the data.
        chan_xy : npt.NDArray[np.float64]
            Channel (electrode) (x,y) coordinates; saved as attribute to facilitate
            visualisations.

        Returns
        -------
        None.

        """

        self.motor_unit_number = number

        # Number of potentials (firings) assigned to MU.
        self.n_potentials = len(potentials_t_idx)
        # Time indices of potentials in EMG.
        self.potentials_t_idx = potentials_t_idx

        # Set sampling frequency.
        self.fs = fs

        # Channel/electrode coordinates of the needle.
        self.chan_xy = chan_xy

        # Store information about analysis that has been performed for this MU
        # Note: even if true, may not be results if data was not suitable for analysis
        self.analysis_performed = {
            "fibres_localised": False,  # localisation step
            "fibres_clustered": False,  # clustering fibres step
            "fibres_jitter_computed": False,  # jitter analysis step
        }

        # Localisation attributes.
        # Number of fibre potentials (peaks) found across all MUPs.
        self.n_fibre_potentials = 0

        # Size of window used for localisation.
        self.n_samples_window = 0

        # Estimated fibre x, y coordinate at each time (size n peaks x 2).
        self.fibre_centres = np.array([])

        # Onset indices of MUPs that each fibre potential (peak) belongs to.
        # One for each fibre potential.
        self.mup_onsets = np.array([])

        # Fibre potential peak times relative to the onset time
        # of the corresponding MUP that it belongs to (in indices units, not seconds).
        self.fibre_potential_times = np.array([])

        # The channel in which each fibre potential has peak amplitude (may be min or max).
        self.fibre_potential_peak_chan = np.array([])

        # Time series for each MUP and channel
        # (size: n MU potentials x n chan x time).
        self.all_spikes = np.array([])

        # Generator potential, represents true underlying potential.
        self.generator_potential = np.array([])

        # Results for comparing number of clusters for GMM or k-means.
        self.cluster_scores = None

        # Dictionaries for storing results of clustering and jitter analysis.
        self.fibre_clustering_results: dict = {}
        self.fibre_jitter_results: dict = {}

    def __str__(self) -> str:
        """
        Return a string for the object

        Parameters
        ----------
        None.

        Returns
        -------
        str

        """

        ans = "EMG Motor Unit"
        ans += "\nMotor unit number: "
        ans += str(self.motor_unit_number + 1)
        ans += "\nNumber of potentials: "
        ans += str(self.n_potentials)
        ans += "\nFibre centres dimensions: "
        ans += str(self.fibre_centres.shape)
        ans += "\nMUP onsets dimensions: "
        ans += str(self.mup_onsets.shape)
        ans += "\nFibre potential times dimensions: "
        ans += str(self.fibre_potential_times.shape)
        ans += "\nAll spikes dimensions: "
        ans += str(self.all_spikes.shape)
        ans += "\nGenerator potential dimensions: "
        ans += str(self.generator_potential.shape)

        ans += "\n"

        return ans

    def add_fibre_localisation(
        self,
        fibre_centres: npt.NDArray[np.float64],
        mup_onsets: npt.NDArray[np.int64],
        fibre_potential_times: npt.NDArray[np.int64],
        fibre_potential_peak_chan: npt.NDArray[np.int64],
        all_spikes: npt.NDArray[np.float64],
        generator_potential: npt.NDArray[np.float64],
    ):
        """
        Add results of the fibre localisation step to the motor unit object. Computes
        additional attributes and stores that analysis has been performed.

        Called during EMGAnalysisReconstruct method, reconstruct_fibres

        Parameters
        ----------
        fibre_centres : npt.NDArray[np.float64]
            Estimated location of fibres.
        mup_onsets : npt.NDArray[np.int64]
            Onset indices of the MUPs (firings) relative to the overall time
        fibre_potential_times : npt.NDArray[np.int64]
            Fibre potential peak times relative to the onset (overall) time
            of the corresponding MUP (listed above in mup_onsets)
        fibre_potential_peak_chan : npt.NDArray[np.int64]
            The channel with the peak amplitude for each fibre potential.
        all_spikes : npt.NDArray[np.float64]
            All peaks from surrounding channels.
        generator_potential : npt.NDArray[np.float64]
            Represents true underlying potential. Used to find MUPs.

        Returns
        -------
        None.

        """

        # Note analysis performed.
        self.analysis_performed["fibres_localised"] = True

        # Store number of fibre potentials (i.e., peaks in the MUPs) found.
        self.n_fibre_potentials = fibre_centres.shape[0]

        # Store provided attributes.
        self.fibre_centres = fibre_centres
        self.mup_onsets = mup_onsets
        self.fibre_potential_times = fibre_potential_times
        self.fibre_potential_peak_chan = fibre_potential_peak_chan
        self.all_spikes = all_spikes
        self.generator_potential = generator_potential

        # Save the size of the window in number of indices, used later for plots.
        # So that all_spikes does not need to be saved with the results, and this
        # value can be saved and loaded instead.
        self.n_samples_window = self.all_spikes.shape[2]

    def get_fibre_localisation_dict(self, save_all_spikes: bool = False) -> dict:
        """
        Returns dictionary of fibre localisation so that it can be saved

        Parameters
        ----------
        save_all_spikes : bool, optional
            Whether to save all_spikes. Uses a lot of data and is not necessary.
            The default is False.

        Returns
        -------
        dict

        """

        # Convert to lists to store as dictionary.
        fibre_local_dict = {
            "n_fibre_potentials": self.n_fibre_potentials,
            "fibre_centres": self.fibre_centres.tolist(),
            "mup_onsets": self.mup_onsets.tolist(),
            "fibre_potential_times": self.fibre_potential_times.tolist(),
            "all_spikes": [],
            "n_samples_window": self.n_samples_window,
            # "generator_potential" : self.generator_potential.tolist()
        }

        if save_all_spikes:
            fibre_local_dict["all_spikes"] = self.all_spikes.tolist()

        return fibre_local_dict

    def set_fibre_localisation_from_dict(self, fibre_local_dict: dict):
        """
        Sets fibre localisation results from loaded dictionary.

        Parameters
        ----------
        fibre_local_dict : dict
            Dictionary containing saved results of clustering.

        Returns
        -------
        None.

        """

        # Convert data back to arrays.
        self.n_fibre_potentials = fibre_local_dict["n_fibre_potentials"]
        self.fibre_centres = np.array(fibre_local_dict["fibre_centres"])
        self.mup_onsets = np.array(fibre_local_dict["mup_onsets"])
        self.fibre_potential_times = np.array(fibre_local_dict["fibre_potential_times"])
        self.all_spikes = np.array(fibre_local_dict["all_spikes"])
        self.n_samples_window = fibre_local_dict["n_samples_window"]
        # self.generator_potential = np.array(fibre_local_dict["generator_potential"])

        # Note analysis performed.
        if self.n_fibre_potentials is not None and len(self.fibre_centres) > 0:
            self.analysis_performed["fibres_localised"] = True

    def _cluster_silhouette_score(self, estimator, X: npt.NDArray[np.float64]) -> float:
        """
        Callable to pass to GridSearchCV that will use the silhouette score.

        Parameters
        ----------
        estimator: Any
            Estimator class, which will include a "predict" method.

        X : npt.NDArray[np.float64]
            Array of fibre potential data to assign to clusters.

        Returns
        -------
        float

        """

        return silhouette_score(X, estimator.predict(X))

    def _gmm_selection(
        self, X: npt.NDArray[np.float64], min_n_clusters: int, max_n_clusters: int
    ) -> GridSearchCV:
        """
        Gaussian Mixture Model Selection.
        https://scikit-learn.org/stable/auto_examples/mixture/plot_gmm_selection.html#sphx-glr-auto-examples-mixture-plot-gmm-selection-py
        Fit data to clusters from the minimum number of clusters to the maximum number of clusters.

        Parameters
        ----------
        X : npt.NDArray[np.float64]
            Array of fibre potential data to assign to clusters.
        min_n_clusters : int
            Minimum number of clusters to try.
        max_n_clusters : int
            Maximum number of clusters to try.

        Returns
        -------
        float
        """

        param_grid = {
            "n_components": range(min_n_clusters, max_n_clusters + 1),
            "covariance_type": [self.mu_cluster_settings.gmm_covariance_type],
        }

        grid_search = GridSearchCV(
            GaussianMixture(), param_grid=param_grid, scoring=self._cluster_silhouette_score
        )

        grid_search.fit(X)

        return grid_search

    def _k_means_selection(
        self, X: npt.NDArray[np.float64], min_n_clusters: int, max_n_clusters: int
    ) -> GridSearchCV:
        """
        Try out k-means clustering for different numbers of clusters.
        Fit data to clusters from the minimum number of clusters to the maximum number of clusters.

        """

        param_grid = {
            "n_clusters": range(min_n_clusters, max_n_clusters + 1),
            "random_state": [self.mu_cluster_settings.k_means_random_state],
            "n_init": ["auto"],
        }

        grid_search = GridSearchCV(
            KMeans(), param_grid=param_grid, scoring=self._cluster_silhouette_score
        )

        grid_search.fit(X)

        return grid_search

    def cluster_fibre_potentials(self, mu_cluster_settings: EMGAnalysisMotorUnitClusterSettings):
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
        mu_cluster_settings: EMGAnalysisMotorUnitClusterSettings
            Contains all settings for clustering.

        Raises
        ------
        RuntimeError
            Raised if localisation analysis has not been performed on requested motor
            unit.

        Returns
        -------
        None.

        """

        # Set settings for cluster analysis.
        self.mu_cluster_settings = mu_cluster_settings

        # Check that localisation has been run.
        if not self.analysis_performed["fibres_localised"]:
            raise RuntimeError(
                "Localisation analysis has not been performed; cannot cluster fibres."
            )

        # Arrays to store results for median and GMM clustering.
        fibre_centres_median = np.array([])
        fibre_centres_gmm_mean = np.array([])
        fibre_centres_gmm_covariance = np.array([])

        # Onset indices of all MUPs that have fibre potentials.
        unique_mup_onsets = np.unique(self.mup_onsets)
        n_unique_mup_onsets = len(unique_mup_onsets)
        mean_n_fps = round(len(self.mup_onsets) / n_unique_mup_onsets)

        # Set up data to use for clustering.
        if self.mu_cluster_settings.time_scale > 0:
            # Scale time column.
            # Values in (0, 20] for self.mu_cluster_settings.time_scale
            # are suitable for scaling.
            # Do not scale fibre locations as they are in the same units (mm).
            time_min = np.min(self.fibre_potential_times)
            time_max = np.max(self.fibre_potential_times)

            data_to_cluster = np.hstack(
                (
                    self.fibre_centres,
                    (
                        (np.atleast_2d(self.fibre_potential_times).T - time_min)
                        / (time_max - time_min)
                    )
                    * self.mu_cluster_settings.time_scale,
                )
            )

        else:
            data_to_cluster = self.fibre_centres

        # Choose clustering method.
        if self.mu_cluster_settings.clustering_method == "dbscan":
            # Use Density-based spatial clustering of applications with noise (DBSCAN).
            clustering = DBSCAN(
                eps=self.mu_cluster_settings.dbscan_eps,
                min_samples=self.mu_cluster_settings.dbscan_min_samples,
            ).fit(data_to_cluster)
            n_fibre_clusters = np.max(clustering.labels_) + 1
            fibre_clusters = clustering.labels_

        elif self.mu_cluster_settings.clustering_method == "k-means":
            # k for clustering.
            k = self.mu_cluster_settings.k_means_k

            # Use a range if no values of k if not given.
            if k == 0:
                min_n_clusters = np.max([2, mean_n_fps - 2])
                max_n_clusters = mean_n_fps + 2
            else:
                min_n_clusters = k
                max_n_clusters = k

            grid_search = self._k_means_selection(data_to_cluster, min_n_clusters, max_n_clusters)

            # fibre cluster assignments.
            fibre_clusters = grid_search.predict(data_to_cluster)
            n_fibre_clusters = np.max(fibre_clusters) + 1

            # Record results for graph plotting.
            self.cluster_scores = grid_search.cv_results_

        elif self.mu_cluster_settings.clustering_method == "gmm":
            # Use Gaussian Mixture Model Selection.
            min_n_clusters = np.max([2, mean_n_fps - 2])
            max_n_clusters = mean_n_fps + 2

            grid_search = self._gmm_selection(data_to_cluster, min_n_clusters, max_n_clusters)

            # Record results for graph plotting.
            self.cluster_scores = grid_search.cv_results_

            # Fibre cluster assignments.
            fibre_clusters = grid_search.predict(data_to_cluster)
            n_fibre_clusters = np.max(fibre_clusters) + 1

            fibre_centres_gmm_mean = grid_search.best_estimator_.means_
            fibre_centres_gmm_covariance = grid_search.best_estimator_.covariances_

        else:
            # If no valid clustering method given.
            raise Exception(
                "Clustering method,"
                + str(self.mu_cluster_settings.clustering_method)
                + ", not found!"
                + "Valid options are: dbscan, k-means or gmm."
            )

        # Initialise arrays for storing results.

        # Number of fibre potentials (FPs) in each MUP that belong to the same
        # cluster.
        n_fps_per_mup_and_cluster = np.zeros((self.n_potentials, n_fibre_clusters))

        # Location estimates of each fibre based on each MUP.
        # Note: unlike original code, data stored so indices match the
        # self.potentials_t_idx array.
        mup_fibre_pos = np.full((self.n_potentials, 2, n_fibre_clusters), np.nan)

        # Find median location of each fibre.
        for cluster_num in np.arange(n_fibre_clusters):
            # Sometimes multiple fibre potentials in the same MUP are assigned to
            # the same fibre clusters. One of these will be chosen later as the "best"
            # to compute the jitter. (One nearest the median over all MUPs)
            # If no fibres with that cluster num appear in the MUP, position is
            # stored as np.nan.

            # Iterate through all MUPs (not just ones
            # present in "mup_onsets") so dimensions align to other MUP features.
            for mup_num in np.arange(self.n_potentials):
                mup_onset = self.potentials_t_idx[mup_num]

                # Fibre potentials that belong to the specified onset and cluster.
                idx = np.flatnonzero(
                    np.all(
                        (
                            (self.mup_onsets == mup_onset),
                            (fibre_clusters == cluster_num),
                        ),
                        axis=0,
                    )
                )

                # Store number of fibre potentials found.
                n_idx = len(idx)
                n_fps_per_mup_and_cluster[mup_num, cluster_num] = n_idx

                # Compute average position of the fibre based on the specified MUP.
                if n_idx > 0:
                    pos = self.fibre_centres[idx, :]
                    mup_fibre_pos[mup_num, :, cluster_num] = np.mean(pos, axis=0)

            # Compute median fibre positions.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                fibre_centres_median = np.transpose(np.nanmedian(mup_fibre_pos, axis=0))

        # Store results as dictionary.
        self.fibre_clustering_results = {
            "mean_n_fps": mean_n_fps,
            "n_fibre_clusters": n_fibre_clusters,
            "fibre_clusters": fibre_clusters,
            "n_fps_per_mup_and_cluster": n_fps_per_mup_and_cluster,
            "mup_fibre_pos": mup_fibre_pos,
            "fibre_centres_median": fibre_centres_median,
            "fibre_centres_gmm_mean": fibre_centres_gmm_mean,
            "fibre_centres_gmm_covariance": fibre_centres_gmm_covariance,
        }
        self.analysis_performed["fibres_clustered"] = True

    def get_fibre_clusters_dict(self) -> dict:
        """
        Returns dictionary of fibre clusters so that it can be saved.

        Parameters
        ----------
        None.

        Returns
        -------
        dict
            Dictionary containing clustering results.

        """

        # Get clustering results if they exist and put in a dictionary
        # with arrays stored as lists so they can be save in a json format file.
        if self.analysis_performed["fibres_clustered"]:
            fibre_clusters_dict = {
                "mean_n_fps": int(self.fibre_clustering_results["mean_n_fps"]),
                "n_fibre_clusters": int(self.fibre_clustering_results["n_fibre_clusters"]),
                "fibre_clusters": self.fibre_clustering_results["fibre_clusters"].tolist(),
                "n_fps_per_mup_and_cluster": self.fibre_clustering_results[
                    "n_fps_per_mup_and_cluster"
                ].tolist(),
                "mup_fibre_pos": self.fibre_clustering_results["mup_fibre_pos"].tolist(),
                "fibre_centres_median": self.fibre_clustering_results[
                    "fibre_centres_median"
                ].tolist(),
                "fibre_centres_gmm_mean": self.fibre_clustering_results[
                    "fibre_centres_gmm_mean"
                ].tolist(),
                "fibre_centres_gmm_covariance": self.fibre_clustering_results[
                    "fibre_centres_gmm_covariance"
                ].tolist(),
            }
        else:
            fibre_clusters_dict = {}

        return fibre_clusters_dict

    def set_fibre_clusters_from_dict(
        self, fibre_clusters_dict: dict, mu_cluster_settings: EMGAnalysisMotorUnitClusterSettings
    ):
        """
        Sets fibre localisation results from loaded dictionary.

        Parameters
        ----------
        fibre_clusters_dict : dict
            Dictionary containing saved results of clustering

        mu_cluster_settings : EMGAnalysisMotorUnitClusterSettings
            Copy of settings used to do clustering.

        Returns
        -------
        None.

        """

        # If clustering not done for this MU then do not set anything.
        if fibre_clusters_dict:
            # Convert lists back to arrays to store results.
            self.fibre_clustering_results = {
                "mean_n_fps": fibre_clusters_dict["mean_n_fps"],
                "n_fibre_clusters": fibre_clusters_dict["n_fibre_clusters"],
                "fibre_clusters": np.array(fibre_clusters_dict["fibre_clusters"]),
                "n_fps_per_mup_and_cluster": np.array(
                    fibre_clusters_dict["n_fps_per_mup_and_cluster"]
                ),
                "mup_fibre_pos": np.array(fibre_clusters_dict["mup_fibre_pos"]),
                "fibre_centres_median": np.array(fibre_clusters_dict["fibre_centres_median"]),
                "fibre_centres_gmm_mean": np.array(fibre_clusters_dict["fibre_centres_gmm_mean"]),
                "fibre_centres_gmm_covariance": np.array(
                    fibre_clusters_dict["fibre_centres_gmm_covariance"]
                ),
            }

            # Note analysis performed.
            self.analysis_performed["fibres_clustered"] = True

            # Set clustering settings also.
            self.mu_cluster_settings = mu_cluster_settings

    def plot_compare_cluster_scores(self) -> sns.FacetGrid:
        """

        Parameters
        ----------
        None.

        Returns
        -------
        sns.FacetGrid
            Returns the FacetGrid object with the plot on it for further tweaking.

        """

        # Set variable name of data to retrieve.
        if self.mu_cluster_settings.clustering_method == "gmm":
            cluster_str = "param_n_components"
        elif self.mu_cluster_settings.clustering_method == "k-means":
            cluster_str = "param_n_clusters"
        else:
            cluster_str = ""

        # Return blank plot if no data.
        if cluster_str == "" or self.cluster_scores is None:
            return sns.catplot(kind="bar")

        # Create bar plot.
        grid = sns.catplot(
            kind="bar",
            x=self.cluster_scores[cluster_str],
            y=self.cluster_scores["mean_test_score"],
            legend_out=False,
        )

        # Set limits and layout.
        plt.ylim((0, 1))
        plt.tight_layout(pad=5.0)

        grid.set_axis_labels("number of clusters", "silhouette score")

        return grid

    def plot_fibre_locations_setup(
        self,
        figsize: tuple[float, float] = (10.0, 5.0),
        axis_label_size: float = 14,
        tick_label_size: float = 12,
        dpi: int = 100,
        threeD: bool = False,
    ) -> tuple[Figure, Axes]:
        """
        Sets up plot for showing fibre locations, possibly from different motor units.

        Parameters
        ----------
        figsize : tuple[int, int], optional
            Size of the figure. The default is (10, 5).
        axis_label_size : int, optional
            Size of axis labels. The default is 14.
        tick_label_size : int, optional
            Size of the tick labels. The default is 12.
        dpi : int, optional
            Dots per inch. The default is 100.
        threeD : bool, optional
            Create 3D plot if true. The default is False.

        Returns
        -------
        fig : Figure
            The figure to which the plot belongs.
        ax : Axes
            The axes to which the plot belongs.

        """

        # Create new figure with specified size.
        if threeD:
            fig = Figure(figsize=figsize)
            ax = fig.add_subplot(projection="3d")
        else:
            fig, ax = plt.subplots(figsize=figsize)

        fig.dpi = dpi

        # Add axis and tick labels.
        ax.set_xlabel("position (mm)", fontsize=axis_label_size)
        ax.set_ylabel("position (mm)", fontsize=axis_label_size)
        ax.tick_params(axis="x", which="major", labelsize=tick_label_size)
        ax.tick_params(axis="y", which="major", labelsize=tick_label_size)

        # Add time axis if 3D plot.
        # Type checking complains for 3D but it is fine.
        if threeD:
            ax.set_zlabel("time (\u03bc seconds)", fontsize=axis_label_size, labelpad=8.0)
            ax.tick_params(axis="z", which="major", labelsize=tick_label_size)

        plt.title(f"Motor Unit {self.motor_unit_number+1}")

        return fig, ax

    def _plot_electrodes(
        self,
        ax: Axes,
        marker: str = "s",
        marker_size: float = 20,
        clr: str = "silver",
        z: float = None,
    ):
        """
        Plot electrode locations using their (x,y) coordinates.

        Electrodes are symbolised by grey squares by default.

        Parameters
        ----------
        ax : Axes
            Axes to plot the electrodes onto.
        marker : str, optional
            The kind of marker to use. The default is "s", square.
        marker_size : float, optional
            The size of the markers. The default is 20.
        clr : str, optional
            The colour of the electrodes. Default is "silver".
        z : float, optional
            z value of electrodes for 3D plot. Default is None.

        Returns
        -------
        None.

        """

        # Plot electrodes.
        if z is None:
            ax.scatter(
                self.chan_xy[:, 0], self.chan_xy[:, 1], s=marker_size, marker=marker, color=clr
            )
        else:
            # Plot electrodes on 3D graph at set z distance.
            ax.scatter(
                self.chan_xy[:, 0],
                self.chan_xy[:, 1],
                np.full(len(self.chan_xy[:, 0]), z),
                s=marker_size,
                marker=marker,
                color=clr,
            )

    def plot_fibre_potential_clustering(
        self,
        plot_electrodes: bool = True,
        pt_potentials_size: float = 10,
        pt_potentials_alpha: float = 0.4,
        pt_mean_size: float = 50,
        n_sigma: int = 2,
        axis_equal: bool = True,
        lw: float = 0.5,
        figsize: tuple[float, float] = (10.2, 5.0),
        axis_label_size: float = 14,
        tick_label_size: float = 12,
        dpi: int = 100,
        cmap=None,
        max_x: float = 22,
        max_y: float = 1,
        plot_legend: bool = True,
        legend_pt_size: float = 50,
        legend_label_size: float = 12,
    ):
        """
        Create scatter plot of fibre localisations estimated from all fibre potentials
        with the location of each fibre overlaid. Ellipse confidence regions are plotted
        around te fibre locations
        Plots results from one motor unit at a time.

        Default point colour depends on the fibre cluster.

        Parameters
        ----------
        plot_electrodes : bool, optional
            Whether to plot electrodes or not. The default is True.
        pt_potentials_size : float, optional
            Size of the points for the fibre potentials. The default is 10.
        pt_potentials_alpha : float, optional
            Alpha value for the points, [0, 1] (transparency). The default is 0.4.
        pt_mean_size : float, optional
            Size of points for means. The fibre centres. The default is 50.
        n_sigma : float, optional
            Number of St. Dev. to plot around the fibre centres. The Default is 2.
        axis_equal : bool, optional
            Whether aspect ratio should be plotted equal. The default is True.
        lw : float, optional
            Line weight. The default is 0.5.
        figsize tuple[float, float], optional
            Size of figure. The default is (10, 5).
        axis_label_size : float, optional
            size of axis label. The default is 14.
        tick_label_size : float, optional
            Size of tick labels. The default is 12.
        dpi : int, optional
            Dots per inch. The default is 100.
        cmap : Any, optional
            Colour map to use. The default is None.
        max_x : float, optional
            Maximum of x axis. The default is 22.
        max_y : float, optional
            Maximum of y axis. The default is 1.
        plot_legend : bool, optional
            Plot the legend or not. The default is True.
        legend_pt_size : float, optional
            Size of points in legend. The default is 50.
        legend_label_size: float, optional
            Size of labels in legend. The default is 12.

        Returns
        -------
        None.

        """

        # Setup plot
        fig, ax = self.plot_fibre_locations_setup(
            figsize=figsize,
            axis_label_size=axis_label_size,
            tick_label_size=tick_label_size,
            dpi=dpi,
        )

        # Add electrodes to plot
        if plot_electrodes:
            self._plot_electrodes(ax=ax)

        n_clusters = self.fibre_clustering_results["n_fibre_clusters"]

        # Plot clusters
        for cluster_no in range(n_clusters):
            self._plot_cluster_points(
                cluster_no,
                n_clusters,
                ax,
                pt_size=pt_potentials_size,
                pt_alpha=pt_potentials_alpha,
                cmap=cmap,
                lw=lw,
            )

        # Plot centres and covariance regions (if not GMM).
        for cluster_no in range(n_clusters):
            self._plot_fibre_location(
                cluster_no,
                n_clusters,
                ax,
                (self.mu_cluster_settings.clustering_method == "gmm"),
                pt_mean_size,
                n_sigma,
            )

        # Plot fitted covariance regions for GMM.
        if self.mu_cluster_settings.clustering_method == "gmm":
            self._plot_fitted_gmms(ax, n_sigma)

        # Plot legend.
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
                h.set_alpha(1)

        # Set y axis limits.
        ax.set_ylim(-max_y, max_y)

        # Set x axis limits.
        ax.set_xlim(-1, max_x)

        # Equal aspect ratio, (this can mess up the axis limits in Windows)
        if axis_equal:
            ax.axis("equal")

    def get_cluster_colour(self, cluster_no: int, n_clusters: int, cmap=None):
        """
        Return the colour of a cluster depending on the cluster number and
        how many total clusters.

        Parameters
        ----------
        cluster_no : int
            Number of the cluster.
        n_clusters : int
            Total number of clusters.
        cmap : Colourmap, optional
            Use this colour map if given. The default is None.

        Returns
        -------
        Colour

        """

        if cmap is None:
            if n_clusters <= 10:
                cmap = colormaps["tab10"].colors
            elif n_clusters <= 20:
                cmap = colormaps["tab20"].colors
            else:
                cmap = plt.cm.rainbow(np.linspace(0, 1, n_clusters))
        else:  # if colourmap is specified, check that sufficient colours; if not, repeat
            if len(cmap) < n_clusters:
                cmap = cmap * int(np.ceil(n_clusters / len(cmap)))

        return cmap[cluster_no]

    def _plot_cluster_points(
        self,
        cluster_no: int,
        n_clusters: int,
        ax: Axes,
        pt_size: float,
        pt_alpha: float,
        cmap=None,
        lw: float = 0,
        threeD: bool = False,
    ):
        """
        Plot all the points for fibre potentials beloging to the same cluster.

        Parameters
        ----------
        cluster_no : int
            Number of the cluster.
        n_clusters : int
            Total number of clusters.
        ax : Axes, optional
            Plot to add to. The default is None.
        pt_alpha : float, optional
            Alpha value for the points, [0, 1] (transparency). The default is 0.4.
        cmap : Colourmap, optional
            Use this colour map if given. The default is None.
        lw : float, optional
            Line weight. The default is 0.
        threeD : bool, optional
            If points are plotted on a 3D axis or not (z axis = time in ms). The default
            is False.

        Returns
        -------
        None.

        """

        # Get x and y coords to plot.
        x = self.fibre_centres[(self.fibre_clustering_results["fibre_clusters"] == cluster_no), 0]
        y = self.fibre_centres[(self.fibre_clustering_results["fibre_clusters"] == cluster_no), 1]

        # Get z coords to plot if a 3D plot.
        if threeD:
            N_MS_PER_SEC = 1000
            # Determine shift needed to plot MUP onset at t = 0
            n_ms = ((self.n_samples_window - 1) / 2) / self.fs * N_MS_PER_SEC

            # Fibre potential times
            z = (
                self.fibre_potential_times[
                    (self.fibre_clustering_results["fibre_clusters"] == cluster_no)
                ]
                / self.fs
            ) * N_MS_PER_SEC
            z = z - n_ms

        # Get colour of points.
        pt_facecolor = self.get_cluster_colour(cluster_no, n_clusters, cmap)

        # Plot points for this cluster.
        if threeD:
            ax.scatter(
                x,
                y,
                z,
                s=pt_size,
                alpha=pt_alpha,
                facecolors=pt_facecolor,
                linewidth=lw,
                label=f"fibre {cluster_no + 1}",
            )
        else:
            ax.scatter(x, y, pt_size, alpha=pt_alpha, facecolors=pt_facecolor, linewidth=lw)

    def _plot_fitted_gmms(self, ax: Axes, n_sigma: float):
        """
        Plot all the points for fibre potentials beloging to the same cluster.

        Parameters
        ----------
        ax : Axes
            Plot to add to.
        n_sigma : float
            Number of standard deviations to plot confidence ellipses.

        Returns
        -------
        None.

        """

        # Set up covariance matrix depending on which covariance model was used.
        cv = self.fibre_clustering_results["fibre_centres_gmm_covariance"]

        # Covariance the same for every cluster if "tied".
        if self.mu_cluster_settings.gmm_covariance_type == "tied":
            cov = np.array([[cv[0, 0], cv[0, 1]], [cv[1, 0], cv[1, 1]]])

        for i, mean in enumerate(self.fibre_clustering_results["fibre_centres_gmm_mean"]):
            # Set covariance matrix from fitted GMM.
            if self.mu_cluster_settings.gmm_covariance_type == "diag":
                cov = np.array([[cv[i, 0], 0], [0, cv[i, 1]]])
            elif self.mu_cluster_settings.gmm_covariance_type == "spherical":
                cov = np.array([[cv[i], 0], [0, cv[i]]])
            elif self.mu_cluster_settings.gmm_covariance_type == "full":
                cov = np.array(cv[i])

            v, w = np.linalg.eigh(cov)

            angle = np.arctan2(w[0][1], w[0][0])
            # Convert to degrees
            angle = 180.0 * angle / np.pi
            # Multiply radius by 2 to get diameter.
            v = n_sigma * 2 * np.sqrt(v)
            # Define the ellipse and plot it.
            ellipse = Ellipse(
                mean, v[0], v[1], angle=180.0 + angle, edgecolor="black", facecolor="none"
            )
            ax.add_artist(ellipse)

    def _confidence_ellipse(
        self,
        x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
        ax: Axes,
        n_std: float = 3.0,
        facecolor="none",
        **kwargs,
    ):
        """
        Taken from matplotlib documentation
        https://matplotlib.org/stable/gallery/statistics/confidence_ellipse.html

        Create a plot of the covariance confidence ellipse of *x* and *y*.

        Parameters
        ----------
        x, y : npt.NDArray[np.float64], shape (n, )
            Input data.
        ax : Axes
            The Axes object to draw the ellipse into.
        n_std : float, optional
            The number of standard deviations to determine the ellipse's radiuses.
            The default is 3.
        facecolor : Any, optional
            Face color of ellipse. The default is "none".
        **kwargs
            Forwarded to `~matplotlib.patches.Ellipse`

        Returns
        -------
        None.
        """

        if x.size != y.size:
            raise ValueError("x and y must be the same size")

        # No data to do anything with so return!
        if len(x) == 0:
            return

        cov = np.cov(x, y)
        pearson = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
        # Using a special case to obtain the eigenvalues of this
        # two-dimensional dataset.
        ell_radius_x = np.sqrt(1 + pearson)
        ell_radius_y = np.sqrt(1 - pearson)
        ellipse = Ellipse(
            (0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2, facecolor=facecolor, **kwargs
        )

        # Calculate the scale of x from
        # the standard deviation and multiply
        # with the given number of standard deviations.
        scale_x = np.sqrt(cov[0, 0]) * n_std
        mean_x = np.mean(x)

        # Calculate the scale of y.
        scale_y = np.sqrt(cov[1, 1]) * n_std
        mean_y = np.mean(y)

        transf = (
            transforms.Affine2D().rotate_deg(45).scale(scale_x, scale_y).translate(mean_x, mean_y)
        )

        # Return the Axes object with the ellipse drawn on it.
        ellipse.set_transform(transf + ax.transData)
        ax.add_patch(ellipse)

    def _plot_fibre_location(
        self,
        cluster_no: int,
        n_clusters: int,
        ax: Axes,
        gmm: bool,
        pt_mean_size: float = 10,
        n_sigma: float = 1,
        pt_facecolor=None,
    ):
        """
        Plots estimated fibre location and confidence ellipse.

        Parameters
        ----------
        cluster_no : int
            Number of the cluster.
        n_clusters : int
            Total number of clusters.
        ax : Axes
            Plot to add to.
        gmm : bool
            True if clustering method is GMM.
        pt_mean_size : float, optional
            Size of mean points. The default is 10.
        n_sigma : float, optional
            Number of standard deviations for confidence ellipse. The default is 1.
        pt_facecolor : Any, optional
            Face colour of points, The default is None.

        Returns
        -------
        None.

        """

        if gmm:
            center = self.fibre_clustering_results["fibre_centres_gmm_mean"][cluster_no]
        else:
            x = np.array(
                self.fibre_centres[
                    (self.fibre_clustering_results["fibre_clusters"] == cluster_no), 0
                ]
            )
            y = np.array(
                self.fibre_centres[
                    (self.fibre_clustering_results["fibre_clusters"] == cluster_no), 1
                ]
            )
            center = np.array([[np.mean(x)], [np.mean(y)]])

        if pt_facecolor is None:
            pt_facecolor = self.get_cluster_colour(cluster_no, n_clusters)

        ax.scatter(
            center[0],
            center[1],
            pt_mean_size,
            color=pt_facecolor,
            edgecolors="black",
            label=f"fibre {cluster_no + 1}",
        )

        if not gmm:
            self._confidence_ellipse(x, y, ax, n_sigma, edgecolor="black")

    def plot_3D_fibre_potential_clustering(
        self,
        plot_electrodes: bool = True,
        pt_potentials_size: float = 10,
        pt_potentials_alpha: float = 0.4,
        axis_equal: bool = True,
        lw: float = 0.5,
        figsize: tuple[float, float] = (10.0, 5.0),
        axis_label_size: float = 12,
        tick_label_size: float = 10,
        dpi: int = 100,
        cmap=None,
        max_y: float = 1,
        y_buff: float = 1.75,
        plot_legend: bool = True,
        legend_pt_size: float = 50,
        legend_label_size: float = 10,
        ax: plt.axes.Axes | None = None,
    ) -> tuple[Figure | None, Axes]:
        """
        Create scatter plot of fibre localisations estimated from all fibre potentials
        (one point per potential) with z-axis corresponding to the time of each fibre
        potential in the motor unit potential (t = 0 ms is MUP onset).

        Plots results from one motor unit at a time.

        Default point colour depends on the fibre cluster.

        Parameters
        ----------
        plot_electrodes : bool, optional
            Whether to plot electrodes or not. The default is True.
        pt_potentials_size : float, optional
            Size of the points for the fibre potentials. The default is 10.
        pt_potentials_alpha : float, optional
            Alpha value for the points, [0, 1] (transparency). The default is 0.4.
        axis_equal : bool, optional
            Whether aspect ratio should be plotted equal. The default is True.
        lw : float, optional
            Line weight. The default is 0.5.
        figsize tuple[float, float], optional
            Size of figure. The default is (10, 5).
        axis_label_size : float, optional
            size of axis label. The default is 12.
        tick_label_size : float, optional
            Size of tick labels. The default is 10.
        dpi : int, optional
            Dots per inch. The default is 100.
        cmap : Any, optional
            Colour map to use. The default is None.
        max_y : float, optional
            The minimum positive and negative limits for the y-axis. The max absolute
            y axis location * y_buff is used instead if it exceeds this value to ensure
            that data points are not cut out of the plot. The default is 1.
        y_buff: float, optional
            Factor by which to multiple the max absolute y axis location in order to
            determine y-axis limits (see max_y argument). Controls buffer around points
            along the y-axis. The default is 1.75, which provides room for larger points.
        plot_legend : bool, optional
            Plot the legend or not. The default is True.
        legend_pt_size : float, optional
            Size of points in legend. The default is 50.
        legend_label_size: float, optional
            Size of labels in legend. The default is 10.
        ax : plt.axes.Axes, optional
            Plot to add to. The default is None, in which case new axes are created.

        Returns
        -------
        None.

        """

        # Setup plot.
        if ax is None:
            fig, ax = self.plot_fibre_locations_setup(
                figsize=figsize,
                axis_label_size=axis_label_size,
                tick_label_size=tick_label_size,
                dpi=dpi,
                threeD=True,
            )
        else:
            fig = None

            # Add axis and tick labels.
            ax.set_xlabel("position (mm)", fontsize=axis_label_size)
            ax.set_ylabel("position (mm)", fontsize=axis_label_size)
            ax.tick_params(axis="x", which="major", labelsize=tick_label_size)
            ax.tick_params(axis="y", which="major", labelsize=tick_label_size)
            ax.set_zlabel("time (ms)", fontsize=axis_label_size, labelpad=8.0)
            ax.tick_params(axis="z", which="major", labelsize=tick_label_size)

        # Determine z axis limits based on window used to compute motor unit potentials.
        N_MS_PER_SEC = 1000
        n_ms = (
            ((self.n_samples_window - 1) / 2) / self.fs * N_MS_PER_SEC
        )  # shift to plot MUP onset at t=0
        max_z = n_ms

        # Add electrodes to plot at bottom.
        if plot_electrodes:
            self._plot_electrodes(ax=ax, z=-max_z, clr="grey", marker_size=5)

        n_clusters = self.fibre_clustering_results["n_fibre_clusters"]

        # Keep track of max absolute y position to ensure data is not cut off by axis limits.
        fibre_max_y = 0

        # Plot each cluster.
        for cluster_no in range(n_clusters):
            self._plot_cluster_points(
                cluster_no,
                n_clusters,
                ax,
                pt_size=pt_potentials_size,
                pt_alpha=pt_potentials_alpha,
                cmap=cmap,
                lw=lw,
                threeD=True,
            )
            # Max y
            mu_max_y = np.max(
                np.abs(
                    self.fibre_centres[
                        (self.fibre_clustering_results["fibre_clusters"] == cluster_no), 1
                    ]
                )
            )
            fibre_max_y = max(fibre_max_y, mu_max_y)

        # Add legend.
        if plot_legend:
            lgnd = ax.legend(
                bbox_to_anchor=(1.2, 1.0),
                loc="upper left",
                frameon=False,
                handletextpad=0.25,
                fontsize=legend_label_size,
            )
            for h in lgnd.legend_handles:
                h._sizes = [legend_pt_size]
                h.set_alpha(1)

        # Set y axis and z-axis limits.
        max_y = max(fibre_max_y * y_buff, max_y)  # Adjust max_y based on data
        ax.set_ylim(-max_y, max_y)
        ax.set_zlim(-max_z, max_z)

        # Equal aspect ratio for x and y coordinates
        if axis_equal:
            ax.set_aspect("equalxy", adjustable="box")

        return fig, ax

    def remove_outliers_iqr(
        self, intervals: npt.NDArray[np.int64]
    ) -> tuple[npt.NDArray[np.int64], int]:
        """
        Parameters
        ----------
        intervals: npt.NDArray[np.int]
            Array of time intervals.

        Returns
        -------
        npt.NDArray[np.int64]
            Array of time intervals with outliers removed.

        """

        # Calculate interquartile range.
        q25, q75 = np.nanpercentile(intervals, 25), np.nanpercentile(intervals, 75)
        iqr = q75 - q25

        # Calculate the outlier cutoff.
        cut_off = iqr * 1.5
        lower, upper = q25 - cut_off, q75 + cut_off

        # Replace outliers with nan.
        ans = np.array([np.nan if x < lower or x > upper else x for x in intervals])
        num_of_outliers = np.count_nonzero(((intervals < lower) | (intervals > upper)))

        return ans, num_of_outliers

    def _calculate_fibre_potentials_time_diff(self, fib_pot_pos1: int, fib_pot_pos2: int) -> int:
        """
        Parameters
        ----------
        fib_pot_pos1: int
            Index of the first fibre potential in fibre_potential_times.
        fib_pot_pos2: int
            Index of the second fibre potential in fibre_potential_times.

        Returns
        -------
        int
            Length of time interval between the two fibre potentials
            returned as a multiple of the number of time steps i.e. indices.

        """

        return np.abs(
            self.fibre_potential_times[fib_pot_pos2] - self.fibre_potential_times[fib_pot_pos1]
        )

    def _jitter_analysis_between_two_fibres(
        self, fibre1_num: int, fibre2_num: int
    ) -> tuple[
        float,
        float,
        npt.NDArray[np.int64],
        npt.NDArray[np.int64],
        int,
        int,
        npt.NDArray[np.int64],
        npt.NDArray[np.int64],
    ]:
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

        The median value of D_k is also recorded to hopefully better account for
        the poor quality of data.

        Parameters
        ----------
        fibre1_num : int
            Fibre number for the first fibre, given previously from cluster analysis (0,1,2,...).
        fibre2_num : int
            Fibre number for the second fibre.
        remove_outliers: bool
            Remove outliers in fibre potential times to avoid probable miss-classifications

        Returns
        -------
        tuple[float,
            float,
            npt.NDArray[np.int64],
            npt.NDArray[np.int64],
            int,
            int,
            npt.NDArray[np.int64],
            npt.NDArray[np.int64]]

        """

        # Calculate medians of all the fibre potentials for fibre 1 and fibre 2.
        all_fibre1_potentials_idx = np.flatnonzero(
            (self.fibre_clustering_results["fibre_clusters"] == fibre1_num)
        )
        median_time1 = np.median(self.fibre_potential_times[all_fibre1_potentials_idx])

        all_fibre2_potentials_idx = np.flatnonzero(
            (self.fibre_clustering_results["fibre_clusters"] == fibre2_num)
        )
        median_time2 = np.median(self.fibre_potential_times[all_fibre2_potentials_idx])

        # Length of time intervals between fibre potentials in the two different fibres.
        fibre_potential_time_diffs = np.full(self.n_potentials, np.nan)

        # Taken note of how many outliers there are and which fibre potentials
        # were used.
        number_of_differences_outliers = 0
        number_of_cons_diffs_outliers = 0
        fibre1_pots_used_idx = np.full(self.n_potentials, np.nan)
        fibre2_pots_used_idx = np.full(self.n_potentials, np.nan)

        # Compute length of time intervals between fibre potentials.
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
                # Pick fibre potentials closest to the medians.
                fibre1_potential_to_use = np.argmin(
                    np.abs(median_time1 - self.fibre_potential_times[fibre1_potentials_idx])
                )
                fibre2_potential_to_use = np.argmin(
                    np.abs(median_time2 - self.fibre_potential_times[fibre2_potentials_idx])
                )

                # Get time difference for this MUP between fibre potentials.
                fib_pot_pos1 = fibre1_potentials_idx[fibre1_potential_to_use]
                fib_pot_pos2 = fibre2_potentials_idx[fibre2_potential_to_use]
                fibre_potential_time_diffs[mup_num] = self._calculate_fibre_potentials_time_diff(
                    fib_pot_pos1, fib_pot_pos2
                )

                # Record which fibre potentials were used to look into later, if desired.
                # Note that these fibres include outliers
                fibre1_pots_used_idx[mup_num] = fib_pot_pos1
                fibre2_pots_used_idx[mup_num] = fib_pot_pos2

        # Remove outliers in time intervals.
        if self.mu_jitter_settings.remove_outliers:
            fibre_potential_time_diffs, number_of_differences_outliers = self.remove_outliers_iqr(
                fibre_potential_time_diffs
            )

        # Compute consecutive differences.
        consecutive_diffs = np.full((self.n_potentials - 1), np.nan)

        # Loop thro' MUPs.
        for mup_num in range(self.n_potentials - 1):
            if not np.isnan(fibre_potential_time_diffs[mup_num]) and not np.isnan(
                fibre_potential_time_diffs[mup_num + 1]
            ):
                consecutive_diffs[mup_num] = np.abs(
                    fibre_potential_time_diffs[mup_num] - fibre_potential_time_diffs[mup_num + 1]
                )

        # Remove outliers.
        if self.mu_jitter_settings.remove_outliers:
            consecutive_diffs, number_of_cons_diffs_outliers = self.remove_outliers_iqr(
                consecutive_diffs
            )

        # Compute mean consecutive difference.
        mean_consecutive_diff = np.nanmean(consecutive_diffs)

        # Compute median of consecutive differences.
        median_consecutive_diff = np.nanmedian(consecutive_diffs)

        # Return many results for the jitter analysis.
        return (
            mean_consecutive_diff,
            median_consecutive_diff,
            fibre_potential_time_diffs,
            consecutive_diffs,
            number_of_differences_outliers,
            number_of_cons_diffs_outliers,
            fibre1_pots_used_idx,
            fibre2_pots_used_idx,
        )

    def jitter_analysis(self, mu_jitter_settings: EMGAnalysisMotorUnitJitterSettings):
        """
        Calculate jitter between all pairs of fibres.
        For each fibre pair:
        Firstly a vector of time differences (intervals) are
        calculated, one interval for each MUP. If there is more than one fibre
        potential assigned to a fibre for a MUP then the one that is closest to the
        median (over all fibre potentials in that fibre) is chose. If there are no
        fibre potentials for that fibre and MUP then an interval cannot be record so
        is NAN.
        Secondly, the consecutive differences are calculated, the difference
        between intervals that are in adjacent MUPs. If an interval does not exist
        then NAN is recorded.
        Finally, the mean consecutive differences is calculated to measure the jitter.
        The median consecutive differences is also calculated to try and account
        for poor data.

        Parameters
        ----------
        mu_jitter_settings: EMGAnalysisMotorUnitJitterSettings
            The setting to use for the jitter analysis.

        Returns
        -------
        None.

        """

        # Set jitter settings.
        self.mu_jitter_settings = mu_jitter_settings

        # Check that localisation and fibre clustering has been run.
        if (
            not self.analysis_performed["fibres_localised"]
            or not self.analysis_performed["fibres_clustered"]
        ):
            raise RuntimeError(
                "Localisation analysis and fibre cluster analysis"
                + "must be performed before jitter analysis!"
            )

        # Check there is data to do the calculation.
        if self.n_potentials < 2:
            raise RuntimeError("Not enough MUPs to perform jitter analysis!")

        # Get the number of clusters.
        n_fibre_clusters = self.fibre_clustering_results["n_fibre_clusters"]

        # The number of jitter calculations to do between fibres.
        number_of_jitter_calcs = int(n_fibre_clusters * (n_fibre_clusters - 1) / 2)

        # Calculations to report.
        fibre1_numbers = np.full(number_of_jitter_calcs, 0)
        fibre2_numbers = np.full(number_of_jitter_calcs, 0)
        mean_consecutive_diffs = np.zeros(number_of_jitter_calcs)
        median_consecutive_diffs = np.zeros(number_of_jitter_calcs)
        fibre_potential_time_diffs = np.zeros((number_of_jitter_calcs, self.n_potentials))
        consecutive_diffs = np.zeros((number_of_jitter_calcs, self.n_potentials - 1))
        number_of_differences = np.zeros(number_of_jitter_calcs)
        number_of_cons_diffs = np.zeros(number_of_jitter_calcs)
        number_of_differences_outliers = np.zeros(number_of_jitter_calcs)
        number_of_cons_diffs_outliers = np.zeros(number_of_jitter_calcs)
        fibre1_pots_used_idx = np.zeros((number_of_jitter_calcs, self.n_potentials))
        fibre2_pots_used_idx = np.zeros((number_of_jitter_calcs, self.n_potentials))

        # Loop thro' each fibre pair and perform the jitter analysis.
        # Fibre pair count.
        count = 0
        for fibre1_num in range(n_fibre_clusters - 1):
            for fibre2_num in np.arange(fibre1_num + 1, n_fibre_clusters):
                # Do jitter analysis between fibre1 and fibre2.
                (
                    mean_consecutive_diffs[count],
                    median_consecutive_diffs[count],
                    fibre_potential_time_diffs[count, :],
                    consecutive_diffs[count, :],
                    number_of_differences_outliers[count],
                    number_of_cons_diffs_outliers[count],
                    fibre1_pots_used_idx[count, :],
                    fibre2_pots_used_idx[count, :],
                ) = self._jitter_analysis_between_two_fibres(fibre1_num, fibre2_num)

                # Record fibres analysed and some data counts.
                fibre1_numbers[count] = fibre1_num
                fibre2_numbers[count] = fibre2_num
                number_of_differences[count] = np.count_nonzero(
                    ~np.isnan(fibre_potential_time_diffs[count, :])
                )
                number_of_cons_diffs[count] = np.count_nonzero(
                    ~np.isnan(consecutive_diffs[count, :])
                )
                count += 1

        # Record final jitter analysis results in dictionary.
        self.fibre_jitter_results = {
            "fibre1_numbers": fibre1_numbers,
            "fibre2_numbers": fibre2_numbers,
            "mean_consecutive_diffs": mean_consecutive_diffs,
            "median_consecutive_diffs": median_consecutive_diffs,
            "differences": fibre_potential_time_diffs,
            "consecutive_diffs": consecutive_diffs,
            "number_of_differences": number_of_differences,
            "number_of_differences_outliers": number_of_differences_outliers,
            "number_of_cons_diffs": number_of_cons_diffs,
            "number_of_cons_diffs_outliers": number_of_cons_diffs_outliers,
            "fibre1_pots_used_idx": fibre1_pots_used_idx,
            "fibre2_pots_used_idx": fibre2_pots_used_idx,
        }

        # Record that the jitter analysis has been performed for this motor unit.
        self.analysis_performed["fibres_jitter_computed"] = True

    def get_fibre_jitter_dict(self) -> dict:
        """
        Returns dictionary of fibre jitter results so that it can be saved.

        Parameters
        ----------
        None.

        Returns
        -------
        dict

        """

        # If jitter analysis is not done then return empty dictionary.
        if self.analysis_performed["fibres_jitter_computed"]:
            fibre_jitter_dict = {
                "fibre1_numbers": self.fibre_jitter_results["fibre1_numbers"].tolist(),
                "fibre2_numbers": self.fibre_jitter_results["fibre2_numbers"].tolist(),
                "mean_consecutive_diffs": self.fibre_jitter_results[
                    "mean_consecutive_diffs"
                ].tolist(),
                "median_consecutive_diffs": self.fibre_jitter_results[
                    "median_consecutive_diffs"
                ].tolist(),
                "differences": self.fibre_jitter_results["differences"].tolist(),
                "consecutive_diffs": self.fibre_jitter_results["consecutive_diffs"].tolist(),
                "number_of_differences": self.fibre_jitter_results[
                    "number_of_differences"
                ].tolist(),
                "number_of_differences_outliers": self.fibre_jitter_results[
                    "number_of_differences_outliers"
                ].tolist(),
                "number_of_cons_diffs": self.fibre_jitter_results["number_of_cons_diffs"].tolist(),
                "number_of_cons_diffs_outliers": self.fibre_jitter_results[
                    "number_of_cons_diffs_outliers"
                ].tolist(),
                "fibre1_pots_used_idx": self.fibre_jitter_results["fibre1_pots_used_idx"].tolist(),
                "fibre2_pots_used_idx": self.fibre_jitter_results["fibre2_pots_used_idx"].tolist(),
            }
        else:
            fibre_jitter_dict = {}

        return fibre_jitter_dict

    def set_fibre_jitter_from_dict(
        self, fibre_jitter_dict: dict, mu_jitter_settings: EMGAnalysisMotorUnitJitterSettings
    ):
        """
        Sets fibre jitter results from loaded jitter results.

        Parameters
        ----------
        fibre_jitter_dict : dict
            Dictionary containing saved results of jitter analysis.

        mu_jitter_settings : EMGAnalysisMotorUnitJitterSettings
            Copy of settings used to do jitter analysis.

        Returns
        -------
        None.

        """

        # Check jitter analysis results are saved.
        if fibre_jitter_dict:
            self.fibre_jitter_results = {
                "fibre1_numbers": np.array(fibre_jitter_dict["fibre1_numbers"]),
                "fibre2_numbers": np.array(fibre_jitter_dict["fibre2_numbers"]),
                "mean_consecutive_diffs": np.array(fibre_jitter_dict["mean_consecutive_diffs"]),
                "median_consecutive_diffs": np.array(
                    fibre_jitter_dict["median_consecutive_diffs"]
                ),
                "differences": np.array(fibre_jitter_dict["differences"]),
                "consecutive_diffs": np.array(fibre_jitter_dict["consecutive_diffs"]),
                "number_of_differences": np.array(fibre_jitter_dict["number_of_differences"]),
                "number_of_differences_outliers": np.array(
                    fibre_jitter_dict["number_of_differences_outliers"]
                ),
                "number_of_cons_diffs": np.array(fibre_jitter_dict["number_of_cons_diffs"]),
                "number_of_cons_diffs_outliers": np.array(
                    fibre_jitter_dict["number_of_cons_diffs_outliers"]
                ),
                "fibre1_pots_used_idx": np.array(fibre_jitter_dict["fibre1_pots_used_idx"]),
                "fibre2_pots_used_idx": np.array(fibre_jitter_dict["fibre2_pots_used_idx"]),
            }

            # Note analysis performed.
            self.analysis_performed["fibres_jitter_computed"] = True

            self.mu_jitter_settings = mu_jitter_settings

    def plot_fibre_potential_time_diffs(
        self, fibre1_num: int, fibre2_num: int, display_counts: bool = True
    ) -> tuple[Figure, Axes]:
        """
        Plot a histogram for time differences between fibre potentials.

        Parameters
        ----------
        fibre1_num : int
            Fibre number for the first fibre, given previously from cluster analysis (0,1,2,...).
        fibre2_num : int
            Fibre number for the second fibre.
        display_counts : bool, optional
            Display amount of non nan data used in histograms on plot. The default is True.

        Returns
        -------
        fig : Figure
            The figure to which the plot belongs.
        ax : Axes
            The axes to which the plot belongs.

        """

        # Get index for this pair of fibres so that the results can be retreived.
        res_idx0 = np.where(
            np.all(
                (
                    (self.fibre_jitter_results["fibre1_numbers"] == fibre1_num),
                    (self.fibre_jitter_results["fibre2_numbers"] == fibre2_num),
                ),
                axis=0,
            )
        )

        # Create plot.
        fig, ax = plt.subplots()

        if len(res_idx0) > 0:
            res_idx = res_idx0[0]
        else:
            print(f"Jitter results not found for fibres {fibre1_num + 1} and {fibre2_num + 1}!")
            return fig, ax

        # Get fibre differences and convert to time in seconds.
        fibre_pot_diffs = self.fibre_jitter_results["differences"][res_idx, :] / self.fs
        fibre_pot_diffs = fibre_pot_diffs.flatten()

        # Plot histogram.
        if not np.isnan(fibre_pot_diffs).all():
            ax.hist(
                fibre_pot_diffs,
                bins=30,
                density=True,
                color="lightgrey",
                edgecolor="k",
                linewidth=0.5,
            )

        plt.title(
            f"Fibre Potential Intervals (Motor Unit {self.motor_unit_number+1}"
            + f", Fibres {fibre1_num+1} and {fibre2_num+1})"
        )

        # Add mean and standard deviation info to plot.
        mean = np.nanmean(fibre_pot_diffs)
        st_dev = np.nanstd(fibre_pot_diffs, ddof=1)
        textstr = "\n".join(
            (
                r"Mean $= %.0f$ " % (mean * 1e6,) + "\u03bcs",
                r"St. dev. $=%.0f$ " % (st_dev * 1e6,) + "\u03bcs",
            )
        )

        # These are matplotlib.patch.Patch properties.
        props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)

        # Place a text box in upper left in axes coords.
        ax.text(
            0.05,
            0.95,
            textstr,
            transform=ax.transAxes,
            fontsize=14,
            verticalalignment="top",
            bbox=props,
        )

        # Display counts and percent.
        if display_counts:
            total_diffs = len(fibre_pot_diffs)
            total_non_nan_diffs = np.count_nonzero(~np.isnan(fibre_pot_diffs))
            percent = (total_non_nan_diffs / total_diffs) * 100
            textstr = (
                r"MUPs $= %d$" % (total_diffs,)
                + "\n"
                + r"Used $=%d (%0.2f$"
                % (
                    total_non_nan_diffs,
                    percent,
                )
                + r"$\%$)"
            )

            # Place a text box in upper right in axes coords.
            ax.text(
                0.95,
                0.95,
                textstr,
                transform=ax.transAxes,
                fontsize=14,
                verticalalignment="top",
                horizontalalignment="right",
                bbox=props,
            )

        return fig, ax

    def plot_fibre_consecutive_diffs(
        self, fibre1_num: int, fibre2_num: int, display_counts: bool = True
    ) -> tuple[Figure, Axes]:
        """
        Plot a histogram for the consecutive differences (from one MUP to the next)
        between the length of time intervals of timings between fibre potentials.

        Parameters
        ----------
        fibre1_num : int
            Fibre number for the first fibre, given previously from cluster analysis (0,1,2,...).
        fibre2_num : int
            Fibre number for the second fibre.
        display_counts : int, optional
            Display amount of non nan data used in histograms on plot. The default is True.

        Returns
        -------
        fig : Figure
            The figure to which the plot belongs.
        ax : Axes
            The axes to which the plot belongs.

        """

        # Create plot.
        fig, ax = plt.subplots()

        # Get index for this pair of fibres so that the results can be retreived.
        res_idx0 = np.where(
            np.all(
                (
                    (self.fibre_jitter_results["fibre1_numbers"] == fibre1_num),
                    (self.fibre_jitter_results["fibre2_numbers"] == fibre2_num),
                ),
                axis=0,
            )
        )

        if len(res_idx0) > 0:
            res_idx = res_idx0[0]
        else:
            print(f"Jitter results not found for fibres {fibre1_num + 1} and {fibre2_num + 1}!")
            return fig, ax

        # Get consecutive_diffs and convert to time in seconds.
        consecutive_diffs = self.fibre_jitter_results["consecutive_diffs"][res_idx, :] / self.fs
        consecutive_diffs = consecutive_diffs.flatten()

        # Plot histogram of consecutive differences.
        if not np.isnan(consecutive_diffs).all():
            ax.hist(
                consecutive_diffs,
                bins=30,
                density=True,
                color="lightgrey",
                edgecolor="k",
                linewidth=0.5,
            )

        plt.title(
            f"Consecutive Differences (Motor Unit {self.motor_unit_number+1}"
            + f", Fibres {fibre1_num+1} and {fibre2_num+1})"
        )

        # Add mean and standard deviation info to plot.
        mean = np.nanmean(consecutive_diffs)
        st_dev = np.nanstd(consecutive_diffs, ddof=1)
        textstr = "\n".join(
            (
                r"Mean $= %.0f$ " % (mean * 1e6,) + "\u03bcs",
                r"St. dev. $=%.0f$ " % (st_dev * 1e6,) + "\u03bcs",
            )
        )

        # These are matplotlib.patch.Patch properties.
        props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)

        # Place a text box in upper left in axes coords.
        ax.text(
            0.05,
            0.95,
            textstr,
            transform=ax.transAxes,
            fontsize=14,
            verticalalignment="top",
            bbox=props,
        )

        # Display counts and percent.
        if display_counts:
            con_diffs = len(consecutive_diffs)
            total_non_nan_diffs = np.count_nonzero(~np.isnan(consecutive_diffs))
            percent = (total_non_nan_diffs / con_diffs) * 100
            textstr = (
                r"MUPs $= %d$" % (con_diffs + 1,)
                + "\n"
                + r"Used $=%d (%0.2f$"
                % (
                    total_non_nan_diffs,
                    percent,
                )
                + r"$\%$)"
            )

            # Place a text box in upper right in axes coords.
            ax.text(
                0.95,
                0.95,
                textstr,
                transform=ax.transAxes,
                fontsize=14,
                verticalalignment="top",
                horizontalalignment="right",
                bbox=props,
            )

        return fig, ax

    def plot_jitter_heat_plot(
        self,
        median: bool = False,
        cmap: Any = "magma",
        vmax: float = 100,
        clr_background: Any = "dimgrey",
        axis_label_size: float = 12,
        title_size: float = 12,
        tick_label_size: float = 10,
        ax: plt.axes.Axes | None = None,
    ) -> tuple[Figure | None, Axes]:
        """
        Plot a heat map of mean consecutive differences (MCDs) between fibres.
        (Or medians of consecutive differences)

        Parameters
        ----------
        median : bool, optional
            Plot medians instead of mean consecutive differences. The default is False.
        cmap : matplotlib colormap name or object, or list of colors, optional
            Colourmap. The default is matplotlib colourmap "magma".
        vmax : float, optional
            The upper limit for the colourmap, in microseconds. This argument ensures
            that outliers do not dramatically skew the colourmap and that colours are
            easily comparable across motor units. The default is 100.
        clr_background: colour specification, optional
            Colour for plot background (recommend similar darkness to low values of the
            colourmap). The default is "dimgrey".
        axis_label_size : float, optional
            Font size of the axis labels. The default is 12.
        title_size : float, optional
            Font size the titles. The default is 12.
        tick_label_size : float, optional
            Font size the axis tick labels. The default is 10.
        ax : plt.axes.Axes, optional
            Plot to add to. The default is None, in which case new axes are created.

        Returns
        -------
        fig : Figure | None
            The figure to which the plot belongs.
        ax : matplotlib Axes
            Axes object with the heatmap.
        """

        # Create new figure with specified size if no axis provided.
        if ax is None:
            fig, ax = plt.subplots()
        else:
            fig = None

        # Get number of fibre pairs; return early if none.
        n_fibre_pairs = len(self.fibre_jitter_results["fibre2_numbers"])
        if n_fibre_pairs == 0:
            ax.set_axis_off()  # remove plot axes
            return fig, ax

        n_fibres = int(np.max(self.fibre_jitter_results["fibre2_numbers"]) + 1)

        # Create data array for the heat plot.
        data = np.full((n_fibres, n_fibres), np.nan)

        for i in range(n_fibre_pairs):
            fib1 = int(self.fibre_jitter_results["fibre1_numbers"][i])
            fib2 = int(self.fibre_jitter_results["fibre2_numbers"][i])

            if median:
                val = self.fibre_jitter_results["median_consecutive_diffs"][i]
            else:
                val = self.fibre_jitter_results["mean_consecutive_diffs"][i]

            # Convert indices to micro seconds.
            if not np.isnan(val):
                val = int((val / self.fs) * 1e6 + 0.5)

            # Make heat plot symetrical.
            data[fib1, fib2] = val
            data[fib2, fib1] = val

        # Plotting the heatmap.
        str_fibres = [str(x) for x in np.arange(1, n_fibres + 1)]

        ax = sns.heatmap(
            data=data,
            vmin=0,
            vmax=vmax,
            cmap=cmap,
            annot=True,
            xticklabels=str_fibres,
            yticklabels=str_fibres,
            cbar_kws={"label": "\u03bc seconds"},
            fmt="g",
            ax=ax,
        )

        ax.set_xlabel("fibre number", fontsize=axis_label_size)
        ax.set_ylabel("fibre number", fontsize=axis_label_size)

        # Titles (line break ensures that plot is the same size as plot_jitter_heat_plot,
        # which has a two line title)
        if median:
            ax.set_title(
                f"Motor unit {self.motor_unit_number + 1}\nMedian Consecutive Differences",
                fontweight="bold",
                fontsize=title_size,
            )
        else:
            ax.set_title(
                f"Motor unit {self.motor_unit_number + 1}\nMean Consecutive Differences",
                fontweight="bold",
                fontsize=title_size,
            )

        # Tick label sizes
        ax.tick_params(labelsize=tick_label_size)

        # Ensure square, change background colour, and add frame
        ax.set_aspect("equal")
        ax.set_facecolor(clr_background)
        for _, spine in ax.spines.items():
            spine.set_visible(True)

        return fig, ax

    def _get_jitter_totals(self, fibre1: int, fibre2: int) -> tuple[int, float, int, float]:
        """
        Gets counts (and percentage) of non nan time intervals (between fibre potentials)
        and consecutive differences between fibres fibre1 and fibre2

        Parameters
        ----------
        fibre1 : int
            Index of fibre1.
        fibre2 : int
            Index of fibre2.

        Returns
        -------
        tuple[int, float, int, float]

        """

        # Get index for this pair of fibres so that the results can be retreived.
        res_idx0 = np.where(
            np.all(
                (
                    (self.fibre_jitter_results["fibre1_numbers"] == fibre1),
                    (self.fibre_jitter_results["fibre2_numbers"] == fibre2),
                ),
                axis=0,
            )
        )

        if len(res_idx0) > 0:
            res_idx = res_idx0[0]
        else:
            print(f"Jitter results not found for fibres {fibre1 + 1} and {fibre2 + 1}!")
            return 0, 0, 0, 0

        # Get fibre differences.
        fibre_pot_diffs = self.fibre_jitter_results["differences"][res_idx, :]
        fibre_pot_diffs = fibre_pot_diffs.flatten()

        total_diffs = len(fibre_pot_diffs)
        total_non_nan_diffs = np.count_nonzero(~np.isnan(fibre_pot_diffs))
        percent_df = round((total_non_nan_diffs / total_diffs) * 100, 2)

        # Get consecutive differences.
        consecutive_diffs = self.fibre_jitter_results["consecutive_diffs"][res_idx, :]
        consecutive_diffs = consecutive_diffs.flatten()

        con_diffs = len(consecutive_diffs)
        total_non_nan_cd = np.count_nonzero(~np.isnan(consecutive_diffs))
        percent_cd = round((total_non_nan_cd / con_diffs) * 100, 2)

        return total_non_nan_diffs, percent_df, total_non_nan_cd, percent_cd

    def plot_jitter_totals_heat_plot(
        self,
        percent: bool = False,
        cmap: Any = "viridis",
        clr_background: Any = "dimgrey",
        axis_label_size: float = 12,
        title_size: float = 12,
        tick_label_size: float = 10,
        ax: plt.axes.Axes | None = None,
    ) -> tuple[Figure | None, Axes]:
        """
        Plot a heat map of counts (= number of consecutive differences) used for jitter
        analysis.

        Parameters
        ----------
        percent: bool, optional
            Plot percentage of non-nan counts of consecutive differences, otherwise plot
            the counts. The default is False.
        cmap : matplotlib colormap name or object, or list of colors, optional
            Colourmap. The default is matplotlib colourmap "viridis".
        clr_background: colour specification, optional
            Colour for plot background (recommend similar darkness to low values of the
            colourmap). The default is "dimgrey".
        axis_label_size : float, optional
            Font size of the axis labels. The default is 12.
        title_size : float, optional
            Font size the titles. The default is 12.
        tick_label_size : float, optional
            Font size the axis tick labels. The default is 10.
        ax : plt.axes.Axes, optional
            Plot to add to. The default is None, in which case new axes are created.

        Returns
        -------

        fig : Figure | None
            The figure to which the plot belongs.
        ax : matplotlib Axes
            Axes object with the heatmap.

        """

        # Create new figure with specified size if no axis provided.
        if ax is None:
            fig, ax = plt.subplots()
        else:
            fig = None

        # Get number of fibre pairs; return early if none.
        n_fibre_pairs = len(self.fibre_jitter_results["fibre2_numbers"])
        if n_fibre_pairs == 0:
            ax.set_axis_off()  # remove plot axes
            return fig, ax

        n_fibres = int(np.max(self.fibre_jitter_results["fibre2_numbers"]) + 1)

        # Create array for heat plot.
        data = np.full((n_fibres, n_fibres), np.nan)

        for i in range(n_fibre_pairs):
            fib1 = int(self.fibre_jitter_results["fibre1_numbers"][i])
            fib2 = int(self.fibre_jitter_results["fibre2_numbers"][i])

            (
                _,
                _,
                total_non_nan_cd,
                percent_cd,
            ) = self._get_jitter_totals(fib1, fib2)

            # Set values for heat plot (symmetric)
            if percent:
                data[fib1, fib2] = percent_cd
                data[fib2, fib1] = percent_cd
            else:
                data[fib1, fib2] = total_non_nan_cd  # number of consecutive differences
                data[fib2, fib1] = total_non_nan_cd

        # Plotting the heatmap.
        str_fibres = [str(x) for x in np.arange(1, n_fibres + 1)]

        if percent:
            bar_str = "percent"
        else:
            bar_str = "count"

        ax = sns.heatmap(
            data=data,
            vmin=0,
            cmap=cmap,
            annot=True,
            xticklabels=str_fibres,
            yticklabels=str_fibres,
            cbar_kws={"label": bar_str},
            fmt="g",
            ax=ax,
        )

        ax.set_xlabel("fibre number", fontsize=axis_label_size)
        ax.set_ylabel("fibre number", fontsize=axis_label_size)

        if percent:
            ax.set_title(
                f"Motor unit {self.motor_unit_number + 1}\n"
                + "Sample sizes (% of consecutive differences)",
                fontweight="bold",
                fontsize=title_size,
            )
        else:
            ax.set_title(
                f"Motor unit {self.motor_unit_number + 1}\n"
                + "Sample sizes (# consecutive differences)",
                fontweight="bold",
                fontsize=title_size,
            )

        # Tick label sizes
        ax.tick_params(labelsize=tick_label_size)

        # Ensure square, change background colour, and add frame
        ax.set_aspect("equal")
        ax.set_facecolor(clr_background)
        for _, spine in ax.spines.items():
            spine.set_visible(True)

        return fig, ax

    def get_jitter_fibre_pair_idx(self, fibre1: int, fibre2: int) -> int | None:
        """
        Get index of requested fibre pair in the motor unit's jitter results
        (fibre_jitter_results attribute). Will return None if the fibre pair is not an
        option or if there are multiple matches for that fibre pair in the jitter
        results (which should only arrise if there is an error in the analysis code).

        Fibre1 and fibre2 do not need to be in ascending order.

        Parameters
        ----------
        fibre1 : int
            Number of the first fibre (counting from 0).
        fibre2 : int
            Number of the second fibre (counting from 0).

        Raises
        ------
        ValueError
            Raised if jitter analysis has not yet been performed for this motor unit.

        Returns
        -------
        fibre_pair_idx : int | None
            Index of the specified fibre; can use for extracting the corresponding
            results in the motor unit's jitter analysis results. Is None if fibre pair
            is not a valid option.
        """

        # First check that jitter analysis has been performed
        if not self.analysis_performed["fibres_jitter_computed"]:
            raise ValueError("Jitter has not yet been computed for this motor unit.")
        else:
            # Jitter results
            jitter_results = self.fibre_jitter_results

        # Determine which fields in jitter_results to use for each fibre
        # Lower fibre number is stored in fibre1 results, while higher value is fibre2
        if fibre1 < fibre2:
            fibre1_numbers_field = "fibre1_numbers"
            fibre2_numbers_field = "fibre2_numbers"
        else:
            fibre2_numbers_field = "fibre1_numbers"
            fibre1_numbers_field = "fibre2_numbers"

        # Determine index of results for that fibre pair
        fibre_pair_idx_bool = np.all(
            [
                jitter_results[fibre1_numbers_field] == fibre1,
                jitter_results[fibre2_numbers_field] == fibre2,
            ],
            axis=0,
        )

        # Compute number of matches; if not exactly 1, return None
        n_fibre_pair_matches = sum(fibre_pair_idx_bool)
        if n_fibre_pair_matches == 1:
            fibre_pair_idx = np.flatnonzero(fibre_pair_idx_bool)[0]
        else:
            fibre_pair_idx = None

        # Return fibre pair index
        return fibre_pair_idx

    def _get_jitter_analysed_mups_and_fibres(
        self, fibre1: int, fibre2: int
    ) -> (npt.NDArray[np.bool_], npt.NDArray[np.float64]):
        """
        Returns

        1) boolean array of which motor unit potentials were included in the jitter
           computation for the specified fibre pair

        and

        2) float array of the indices (in self.fibre_potential_times)
           of the fibre potentials in each motor unit that were used to compute the
           jitter of that fibre pair. Float array is used so the indices are nan if that
           motor unit potential was not analysed.

        Note that MUPs that may have been removed by outlier detection are still marked
        as True (= analysed).

        Fibre1 and fibre2 do not need to be in ascending order.

        Parameters
        ----------
        fibre1 : int
            Number of the first fibre (counting from 0).
        fibre2 : int
            Number of the second fibre (counting from 0).

        Raises
        ------
        ValueError
            Raised if jitter analysis has not yet been performed for this motor unit.

        Returns
        -------
        analysed_mup : npt.NDArray[np.bool_]
            Boolean numpy array of which motor unit potentials were included in the
            jitter analysis for this fibre pair. MUPs that produced outlier values are
            still included. Shape is (self.n_potentials,).

        analysed_fibres_idx : npt.NDArray[np.float64]
            Float array of the indices (in self.fibre_potential_times)
            of the fibre potentials in each motor unit that were used to compute the
            jitter of that fibre pair. The index is set to nan if that motor unit
            potential was not analysed. Shape is (2, self.n_potentials), with row 1
            corresponding to fibre1 and row 2 corresponding to fibre2.

        """

        # First check that jitter analysis has been performed
        if not self.analysis_performed["fibres_jitter_computed"]:
            raise ValueError("Jitter has not yet been computed for this motor unit.")
        else:
            jitter_results = self.fibre_jitter_results  # jitter results dictionary

        # Get fibre pair index in jitter results
        fibre_pair_idx = self.get_jitter_fibre_pair_idx(fibre1, fibre2)

        # Initialise array for storing which MUPs were analysed
        analysed_mup = np.full(self.n_potentials, False)

        # Need to append and prepend NaN to consecutive differences array to determine which
        # MUPs are used (since each consecutive difference corresponds to two MUPs)
        nan1 = np.isnan(np.append(jitter_results["consecutive_diffs"][fibre_pair_idx, :], np.nan))
        nan2 = np.isnan(
            np.append(np.array(np.nan), jitter_results["consecutive_diffs"][fibre_pair_idx, :])
        )

        # If not nan in at least one, that MUP was analysed
        analysed_mup[np.any([~nan1, ~nan2], axis=0)] = True

        # Get indices of fibre 1 and fibre 2 (in fibre_potential_times/fibre_potential_peak_chan)
        # for each MUP that was analysed.
        # First need to determine which fields in jitter_results to use for each fibre
        # Lower fibre number is stored in fibre1 results, while higher value is fibre2
        if fibre1 < fibre2:
            fibre1_pots_used_idx_field = "fibre1_pots_used_idx"
            fibre2_pots_used_idx_field = "fibre2_pots_used_idx"
        else:
            fibre2_pots_used_idx_field = "fibre1_pots_used_idx"
            fibre1_pots_used_idx_field = "fibre2_pots_used_idx"

        analysed_fibres_idx = np.vstack(
            (
                jitter_results[fibre1_pots_used_idx_field][fibre_pair_idx, :],
                jitter_results[fibre2_pots_used_idx_field][fibre_pair_idx, :],
            )
        )
        analysed_fibres_idx[:, ~analysed_mup] = np.nan  # Set to nan if fibre not analysed

        return analysed_mup, analysed_fibres_idx

    def plot_jitter_fibre_pair_EMG_and_times(
        self,
        fibre1: int,
        fibre2: int,
        fibre_clrs: list[Any] | None = None,
        emg_line_lw: float = 1,
        emg_line_alpha: float = 0.25,
        emg_y_perc: float = 95,
        emg_y_buff_prop: float = 0.2,
        time_marker_size: float = 2,
        align_times_to_fibre1: bool = True,
        figsize: tuple[float, float] = (10, 10),
        axis_label_size: float = 12,
        title_size: float = 12,
        tick_label_size: float = 10,
        dpi: int = 100,
        downsample_factor: int = 1,
    ) -> tuple[Figure | None, Axes | None]:
        """
        Creates a figure that visualises the jitter analysis of the specified fibre
        pair, fibre1 and fibre2. The figure contains three subplots: the EMG traces of
        fibre1's and fibre2's potentials (in separate plots) and a raster plot of the
        times of the potentials in each motor unit potential. The x-axes of the plots
        are aligned.

        By default, all times are relative to the timing of fibre1's
        potentials in each motor unit.

        If there are no jitter results for that fibre pair (e.g., if there were no
        consecutive motor unit potentials containing potentials for both fibres),
        returns (None, None) instead of the figure and axes.

        Fibre1 and fibre2 do not need to be in ascending order.

        Note that these plots still visualise outlier differences that may be removed
        from the final mean consecutive difference calculation.

        Parameters
        ----------
        fibre1 : int
            Number of the first fibre (counting from 0).
        fibre2 : int
            Number of the second fibre (counting from 0).
        fibre_clrs : list[Any] | None, optional
            List, length two, indicate the colour for the EMG traces for each fibre.
            The default is None, in which case default colours (using CartoColor's
            "Geyser" palette) are set.
        emg_line_lw : float, optional
            Linewidth of the EMG traces. The default is 1.
        emg_line_alpha : float, optional
            Alpha of the EMG traces. The default is 0.25.
        emg_y_perc : float, optional
            The percentile (across MUPs) of the min and max EMG values to use for
            determining the y-axis range for the EMG plots (so outlier values are
            ignored). 100 - emg_y_perc is used to find the min value. Must be between
            0 and 100 inclusive. The default is 95.
        emg_y_buff_prop : float, optional
            The buffer to add around the min and max y values computed using emg_y_perc.
            The final y axis limits for the EMG traces are computed by multiplying the
            difference of those values by emg_y_buff_prop. The default is 0.2.
        time_marker_size : float, optional
            Size of the markers for the fibre potential times. The default is 2.
        align_times_to_fibre1 : bool, optional
            Whether to re-align the times so fibre1's potentials always occur at 0. If
            false, times are instead relative to each MUP's onset. The default is True.
        figsize : tuple[float, float], optional
            Size of the figure, in inches. The default is (10, 10).
        axis_label_size : float, optional
            Font size of the axis labels. The default is 12.
        title_size : float, optional
            Font size the titles. The default is 12.
        tick_label_size : float, optional
            Font size the axis tick labels. The default is 10.
        dpi : int, optional
            Plot resolution (dots per inch). The default is 100.
        downsample_factor : int, optional
            How much to downsample the EMG traces (recommend max of 2). The default is 1.

        Raises
        ------
        ValueError
            Raised if jitter analysis has not yet been performed for this motor unit or
            if the requested fibre pair is not a valid option.

        Returns
        -------
        fig : Figure | None
            The figure to which the plot belongs.
        ax : Axes | None
            The axes to which the plot belongs.

        """

        # First check that jitter analysis has been performed
        if not self.analysis_performed["fibres_jitter_computed"]:
            raise ValueError("Jitter has not yet been computed for this motor unit.")
        else:
            jitter_results = self.fibre_jitter_results  # jitter results dictionary

        # Default colours for fibre EMG traces
        if fibre_clrs is None:
            fibre_clrs = ["#008080", "#ca562c"]

        # Get index of the fibre pair in the jitter results
        fibre_pair_idx = self.get_jitter_fibre_pair_idx(fibre1, fibre2)
        if fibre_pair_idx is None:
            raise ValueError("Requested fibre pair is not an option.")

        # Get mean consecutive difference of that fibre pair
        # If doesn't exist, return early with no figure
        mcd = jitter_results["mean_consecutive_diffs"][fibre_pair_idx]
        if np.isnan(mcd):
            return None, None
        else:  # convert to microseconds
            mcd = int((mcd / self.fs) * 1e6 + 0.5)

        # Boolean array of which MUPs were analysed and the indices (in
        # fibre_potential_times) of the corresponding fibre potentials
        analysed_mup, analysed_fibres_idx = self._get_jitter_analysed_mups_and_fibres(
            fibre1, fibre2
        )

        # Get
        # 1) mode of the peak channels of fibre 1 and fibre 2 and
        # 2) times of the fibre potentials in the each MUP (nan if not analysed)
        n_fibres = 2
        fibres_peak_chan = np.full(n_fibres, 0)
        analysed_fibre_t = np.full((self.n_potentials, n_fibres), np.nan)
        for i in range(n_fibres):  # for each fibre
            # int indices of the analysed fibres, without nan (so can use for indexing)
            idx = analysed_fibres_idx[i, :]
            idx_no_nan = idx[~np.isnan(idx)]
            idx_no_nan = idx_no_nan.astype(int)

            # Peak channel for each fibre and mode of peak channels
            chan = self.fibre_potential_peak_chan[idx_no_nan]
            mode_i = scipy.stats.mode(chan)
            fibres_peak_chan[i] = int(mode_i[0])

            # Fibre times for each mup if mup was analysed (i.e., idx is not nan)
            # Otherwise, set to nan
            analysed_fibre_t[~np.isnan(idx), i] = self.fibre_potential_times[idx_no_nan]

        # Convert fibre times to ms
        MS_MULTIPLIER = 1000
        analysed_fibre_t = (analysed_fibre_t / self.fs) * MS_MULTIPLIER

        # Create time vectors for EMG traces

        # Create time vectors (ms) for x-axis of MUP EMG traces (analysed MUP only)
        # Will create a separate column for each trace so can align based on fibre potential
        # times if requested
        mup_t = (np.arange(1, self.n_samples_window + 1) / self.fs) * MS_MULTIPLIER
        mup_t = np.transpose(
            np.tile(mup_t, [self.n_potentials, 1])
        )  # repeat and transpose (column = mup)

        # If requested, re-align times so fibre1 times = 0 ms
        if align_times_to_fibre1:
            # Subtract fibre1 times from MUP times
            n_t = mup_t.shape[0]
            mup_t = mup_t - np.tile(analysed_fibre_t[:, 0], [n_t, 1])

            # Subtract fibre1 times from analysed fibre times
            # (must be done second since need original fibres times for changing MUP times)
            analysed_fibre_t = analysed_fibre_t - np.transpose(
                np.tile(analysed_fibre_t[:, 0], [n_fibres, 1])
            )

        # Plot EMG traces

        # Set up plot
        fig, axs = plt.subplots(3, 1, figsize=figsize, height_ratios=[1, 1, 4], sharex=True)
        fig.dpi = dpi

        # Labels for fibres (add 1 to count from 1)
        fibre_labels = [fibre1 + 1, fibre2 + 1]

        # Arrays for storing a percentile of the min max values of each EMG trace in
        # each fibre
        perc_of_max_y = np.zeros(n_fibres)
        perc_of_min_y = np.zeros(n_fibres)

        # Plot MUPs of each fibre in each fibre's "peak" channel
        for i in range(n_fibres):
            fibre_mups = np.squeeze(
                self.all_spikes[analysed_mup, fibres_peak_chan[i], 0::downsample_factor]
            )
            axs[i].plot(
                mup_t[0::downsample_factor, analysed_mup],
                np.transpose(fibre_mups),
                lw=emg_line_lw,
                color=fibre_clrs[i],
                alpha=emg_line_alpha,
            )

            # Compute min and max and the specified percentiles
            perc_of_max_y[i] = np.percentile(np.max(fibre_mups, axis=1), emg_y_perc)
            perc_of_min_y[i] = np.percentile(np.min(fibre_mups, axis=1), 100 - emg_y_perc)

            # Title/axis labels (add one to channel indices so count is from 1)
            # No x-axis label since shared across all plots
            axs[i].set_title(
                f"Motor unit {self.motor_unit_number + 1}, "
                + f"fibre {fibre_labels[i]}, channel {fibres_peak_chan[i] + 1}",
                fontsize=title_size,
                fontweight="bold",
            )
            axs[i].set_ylabel("\u03bcV", fontsize=axis_label_size)
            axs[i].tick_params(labelsize=tick_label_size)

        # Link y-axes of two EMG plots
        axs[1].sharey(axs[0])

        # Set limits based on percentiles of min/max
        emg_y_min = np.min(perc_of_min_y)
        emg_y_max = np.max(perc_of_max_y)
        emg_y_buff = (emg_y_max - emg_y_min) * emg_y_buff_prop
        axs[0].set_ylim([emg_y_min - emg_y_buff, emg_y_max + emg_y_buff])

        # Fibre timing

        # Plot times of the two fibre potentials in each MUP
        mup_number = np.arange(self.n_potentials) + 1  # sets y axis location of each tick
        ax_times = 2  # axis to use for plot
        for i in range(n_fibres):
            axs[ax_times].scatter(
                analysed_fibre_t[:, i],
                mup_number,
                s=time_marker_size,
                marker="|",
                color=fibre_clrs[i],
            )

        # Axes (x-axis changes will apply to all plots)
        axs[ax_times].set_ylim([1, max(mup_number)])
        axs[ax_times].set_yticks([])  # no ticks
        axs[ax_times].invert_yaxis()  # first MUP at the top of the plot
        axs[ax_times].set_xlim([np.nanmin(mup_t), np.nanmax(mup_t)])  # tight x-axis limits

        # Labels
        axs[ax_times].set_title(
            f"Fibre potential times (mean consecutive difference: {round(mcd, 2)} \u03bcs)",
            fontsize=title_size,
            fontweight="bold",
        )
        axs[ax_times].set_xlabel("time (ms)", fontsize=axis_label_size)
        axs[ax_times].tick_params(labelsize=tick_label_size)

        return fig, axs

    def delete_fibre_localisation(self):
        """
        Deletes fibre localisation results (added by add_fibre_localisation method) and
        marks that fibre localisation analysis has not been performed.

        Also removes downstream analysis (fibre clustering and jitter).

        Returns
        -------
        None.

        """
        print("Removing localisation results")

        # Note analysis not performed.
        self.analysis_performed["fibres_localised"] = False

        # Set number of fibre potentials to zero.
        self.n_fibre_potentials = 0

        # Store provided attributes.
        self.fibre_centres = np.array([])
        self.mup_onsets = np.array([])
        self.fibre_potential_times = np.array([])
        self.fibre_potential_peak_chan = np.array([])
        self.all_spikes = np.array([])
        self.generator_potential = np.array([])

        # Also remove any downstream analysis.
        self.delete_fibre_clustering()  # will also delete jitter

    def delete_fibre_clustering(self):
        """
        Deletes fibre clustering results (added by cluster_fibre_potentials method) and
        marks that fibre clustering analysis has not been performed.

        Also removes downstream analysis (fibre jitter).

        Returns
        -------
        None.

        """
        print("Removing clustering results")

        # Mark analysis as not performed.
        self.analysis_performed["fibres_clustered"] = False

        # Delete results.
        self.fibre_clustering_results: dict = {}

        # Also remove downstream analysis (jitter)
        self.delete_fibre_jitter()

    def delete_fibre_jitter(self):
        """
        Deletes fibre jitter results (added by jitter_analysis method) and
        marks that fibre jitter analysis has not been performed.

        Returns
        -------
        None.

        """
        print("Removing jitter results")

        # Mark analysis as not performed.
        self.analysis_performed["fibres_jitter_computed"] = False

        self.fibre_jitter_results: dict = {}


class EMGMotorUnits:
    """
    Class for storing and visualising all motor unit data returned from reconstruction
    analysis.

    Only includes visualisations that do not require the recording time series.

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

        # Get and store number of potentials of each motor unit.
        self.n_potentials = [mu.n_potentials for mu in self.motor_units]

    def __str__(self):
        """
        Return a string for the object.

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

    def plot_fibre_locations(
        self,
        location_type: str,
        motor_unit_idx: Optional[int] = None,
        plot_electrodes: bool = True,
        pt_size: float | None = None,
        pt_alpha: float | None = None,
        pt_facecolor=None,
        pt_edgecolor=None,
        pt_linewidth: float = 3,
        axis_equal: bool = True,
        figsize: tuple[float, float] = (10.0, 5.0),
        axis_label_size: float = 12,
        tick_label_size: float = 10,
        plot_legend: bool = True,
        min_legend_pt_size: float = 30,
        legend_label_size: float = 10,
        dpi: int = 100,
        cmap=None,
        max_y: float = 1,
        y_buff: float = 1.75,
        ax: plt.axes.Axes | None = None,
    ) -> tuple[Figure | None, Axes]:
        """
        Create 2D scatter plot of either

        1) fibre localisations estimated from all fibre potentials (i.e., before
        clustering step).

        or

        2) fibre locations (median locations determined by clustering step, with one
        location per fibre).

        The data plotted is determined by location_type: location_type = "potentials"
        returns the fibre potential localisations, while location_type = "fibres"
        returns the final estimated location of each fibre.

        Can either plot fibre locations of all motor units or one, specified motor unit
        potential.

        Default point colour depends on the motor unit number.

        Parameters
        ----------
        location_type : str
            Either "potentials" or "fibres" (see above).
        motor_unit_idx : int, optional
            Motor unit index. The default is None.
        plot_electrodes : bool, optional
            Whether to plot electrodes or not. The default is True.
        pt_size : float, optional
            Size of the points for the fibre locations. The default is 10 for potentials
            and 75 for fibres.
        pt_alpha : float, optional
            Alpha value for the points, [0, 1] (transparency). The default is 0.5 for
            potentials and 1 for fibres.
        pt_facecolor : Any, optional
            Colour of point centres. The default is None. If fibre potential locations
            are plotted, the default colour scheme or given cmap is used.
        pt_edgecolor : Any, optional
            Colour of point outlines. The default is None. If fibre locations are
            plotted, the default colour scheme or given cmap is used.
        pt_linewidth : float, optional
            Linewidth of points. Only used if pt_edgecolor is not None. The default is
            3.
        axis_equal : bool, optional
            Whether aspect ratio should be plotted equal. The default is True.
        figsize tuple[float, float], optional
            Size of figure. The default is (10, 5).
        axis_label_size : float, optional
            size of axis label. The default is 12.
        tick_label_size : float, optional
            Size of tick labels. The default is 10.
        plot_legend : bool, optional
            Plot the legend or not. The default is True.
        min_legend_pt_size : float, optional
            Minimum size of points in legend - if pt_size is less
            than min_legend_pt_size, this value will be used for the legend point size.
            The default is 30.
        legend_label_size: float, optional
            Size of labels in legend. The default is 10.
        dpi : int, optional, optional
            Dots per inch. The default is 300.
        cmap : Any, optional, optional
            Colour map to use. The default is None.
        max_y : float, optional
            The minimum positive and negative limits for the y-axis. The max absolute
            y axis location * y_buff is used instead if it exceeds this value to ensure
            that data points are not cut out of the plot. The default is 1.
        y_buff: float, optional
            Factor by which to multiple the max absolute y axis location in order to
            determine y-axis limits (see max_y argument). Controls buffer around points
            along the y-axis. The default is 1.75, which provides room for larger points.
        ax : plt.axes.Axes, optional
            Plot to add to. The default is None, in which case new axes are created.

        Returns
        -------
        fig : Figure
            The figure to which the plot belongs.
        ax : Axes
            The axes to which the plot belongs.

        """

        # Check value of location_type is valid
        if location_type not in ["potentials", "fibres"]:
            raise ValueError(
                f"location_type of {location_type} is not valid - must be 'potentials' or 'fibres'"
            )

        # If not specified, determine point style based on location_type
        match location_type:
            case "potentials":
                if not pt_size:
                    pt_size = 10
                if not pt_alpha:
                    pt_alpha = 0.5
            case "fibres":
                if not pt_size:
                    pt_size = 75
                if not pt_alpha:
                    pt_alpha = 1

        # Default colormap - will use if colors not specified.
        if cmap is None:
            cmap = colormaps["tab10"].colors

        # Create new figure with specified size if no axis provided.
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
            fig.dpi = dpi
        else:
            fig = None

        # Motor unit(s) to plot.
        if motor_unit_idx is not None:
            if motor_unit_idx < 0:
                motor_units = []
            else:
                motor_units = [self.motor_units[motor_unit_idx]]
        else:
            motor_units = self.motor_units

        # Add electrodes to plot.
        if plot_electrodes and len(motor_units) > 0:
            motor_units[0]._plot_electrodes(ax=ax)

        # Keep track of max absolute y position to ensure data is not cut off by axis limits
        fibre_max_y = 0

        for mu in motor_units:
            # Colour for motor unit - differs depending on motor unit.
            # Face colour: default only used for plotting potentials
            if (pt_facecolor is None) and (location_type == "potentials"):
                # Use same colour scheme as cluster colours for motor units.
                mu_pt_facecolor = mu.get_cluster_colour(
                    mu.motor_unit_number, self.n_motor_units, cmap
                )
            elif not pt_facecolor:
                mu_pt_facecolor = "none"
            else:
                mu_pt_facecolor = pt_facecolor

            # Edge colour: default only used for plotting fibres
            if (pt_edgecolor is None) and (location_type == "fibres"):
                # Use same colour scheme as cluster colours for motor units.
                mu_pt_edgecolor = mu.get_cluster_colour(
                    mu.motor_unit_number, self.n_motor_units, cmap
                )
            elif not pt_facecolor:
                mu_pt_edgecolor = "none"
            else:
                mu_pt_edgecolor = pt_edgecolor

            # Data to plot
            if (location_type == "potentials") and (mu.analysis_performed["fibres_localised"]):
                # Use fibre potential locations
                mu_fibre_locations = mu.fibre_centres

            elif (location_type == "fibres") and (mu.analysis_performed["fibres_clustered"]):
                # Use fibre locations
                mu_fibre_locations = mu.fibre_clustering_results["fibre_centres_median"]

            else:
                # if analyses have not been performed, no fibres locations
                mu_fibre_locations = None

            # Plot locations and compute max absolute y location
            # Must also check that fibres were found  before plotting
            if (mu_fibre_locations is not None) and (len(mu_fibre_locations) > 0):
                ax.scatter(
                    mu_fibre_locations[:, 0],
                    mu_fibre_locations[:, 1],
                    pt_size,
                    alpha=pt_alpha,
                    linewidth=pt_linewidth,
                    facecolor=mu_pt_facecolor,
                    edgecolor=mu_pt_edgecolor,
                    label=f"motor unit {mu.motor_unit_number + 1}",
                )

                # Max absolute y location
                mu_max_y = np.max(np.abs(mu_fibre_locations[:, 1]))
                fibre_max_y = max(fibre_max_y, mu_max_y)

        # Plot legend
        if plot_legend:
            lgnd = ax.legend(
                bbox_to_anchor=(1, 1),
                loc="upper left",
                frameon=False,
                handletextpad=0.25,
                fontsize=legend_label_size,
            )
            for h in lgnd.legend_handles:
                h._sizes = [max(min_legend_pt_size, pt_size)]
                h.set_alpha(1)

        # Axis and tick labels.
        ax.set_xlabel("position (mm)", fontsize=axis_label_size)
        ax.set_ylabel("position (mm)", fontsize=axis_label_size)
        ax.tick_params(axis="x", which="major", labelsize=tick_label_size)
        ax.tick_params(axis="y", which="major", labelsize=tick_label_size)
        max_y = max(fibre_max_y * y_buff, max_y)  # Adjust max_y based on data
        ax.set_ylim(-max_y, max_y)

        # Equal aspect ratio.
        if axis_equal:
            ax.set_aspect("equal", adjustable="box")

        return fig, ax
