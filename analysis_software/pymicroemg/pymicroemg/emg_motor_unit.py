#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGAnalysisReconstruct for localisation.

For use with preprocessed EMG data.

"""

from __future__ import annotations
from tkinter import N  # for type hints - must be at beginning of file

import numpy as np
import numpy.typing as npt  # for type hints

import matplotlib.pyplot as plt
from matplotlib import colormaps
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
import seaborn as sns

from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms

from sklearn.mixture import GaussianMixture
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import silhouette_score
import pandas as pd

# TODO: add csv and cv2 to poetry dependency management
# Need to remove try/except block - temporary fix since functions not needed for
# example pipeline
try:
    import csv
#    import cv2
except Exception as e:
    print(e)
import os

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

    def load_test_data(self, filename):
        # Importing csv module
        with open(filename, "r") as x:
            some_data = list(
                csv.reader(x, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
            )

        return np.array(some_data)
    
    def gmm_bic_score(self, estimator, X):
        """Callable to pass to GridSearchCV that will use the BIC score."""
        #
        # Make it negative since GridSearchCV expects a score to maximize
        return -estimator.bic(X)
       

    def gmm_silhouette_score(self, estimator, X):
        """Callable to pass to GridSearchCV that will use the BIC score."""
        #       
        return silhouette_score(X, estimator.predict(X))
    
    def GMM_selection(self, X, min_n_clusters, max_n_clusters):
        """
        Gaussian Mixture Model Selection
        https://scikit-learn.org/stable/auto_examples/mixture/plot_gmm_selection.html#sphx-glr-auto-examples-mixture-plot-gmm-selection-py      
        """
        
        param_grid = {
            "n_components": range(min_n_clusters, max_n_clusters+1),
            "covariance_type": ["tied"] #["diag"] #["spherical"] #["full"] #["spherical", "tied", "diag", "full"], #returns different variance format if not full
        }
        
        grid_search = GridSearchCV(
            GaussianMixture(), param_grid=param_grid, scoring=self.gmm_silhouette_score
        )
        
        grid_search.fit(X)
        
        return grid_search

    def cluster_fibre_potentials(self, random_state: int = 0, k : int = 0, time_scale = 0, use_gmm = True):
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
        random_state : int
            Determines random number generation for centroid initialization; passed to
            k-means algorithm
        k : int
            the of clusters to fit, if set to 0 uses default of (rounded) mean number of fibre
            potentials (FPs) per motor unit potential
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

        # Check that localisation has been run
        if not self.analysis_performed["fibres_localised"]:
            raise RuntimeError(
                "Localisation analysis has not been performed; cannot cluster fibres."
            )

        fibre_centres_gmm_mean = []
        fibre_centres_gmm_covariance = []
        
        # Onset indices of all MUPs that have fibre potentials
        unique_mup_onsets = np.unique(self.mup_onsets)
        n_unique_mup_onsets = len(unique_mup_onsets)
        mean_n_fps = round(len(self.mup_onsets) / n_unique_mup_onsets)
        
        # Set up data to use to fit
        if time_scale > 0:
            # scale time column
            # do not scale fibre locations as they are in the same units (mm)
            time_min = np.min(self.fibre_potential_times)
            time_max = np.max(self.fibre_potential_times)
            # Choose a value that is about half the length of the needle
                           
            data_to_cluster = np.hstack((self.fibre_centres, ((np.atleast_2d(self.fibre_potential_times).T - time_min)/(time_max - time_min))*time_scale ))
                       
        else:
            data_to_cluster = self.fibre_centres
         
        # Choose clustering method
        if not use_gmm:
            # Use rounded mean number of fibre potentials (FPs) per motor unit potential as
            # k for clustering
            
            if k == 0:
                k = mean_n_fps

            if k == 0:
                return
                         
            fibre_kmeans = KMeans(n_clusters=k, random_state=random_state).fit(data_to_cluster)
            
            # fibre cluster assignments
            n_fibre_clusters = np.max(fibre_kmeans.labels_) + 1
            fibre_clusters = fibre_kmeans.labels_
            
        else:
            # Use Gaussian Mixture Model Selection
            min_n_clusters = np.max([2, mean_n_fps - 2])
            max_n_clusters = mean_n_fps + 2
            
            time_min = np.min(self.fibre_potential_times)
            time_max = np.max(self.fibre_potential_times)
                      
            grid_search = self.GMM_selection(data_to_cluster, min_n_clusters, max_n_clusters)
            
            df = pd.DataFrame(grid_search.cv_results_)[
                ["param_n_components", "param_covariance_type", "mean_test_score"]
            ]
            #df["mean_test_score"] = -df["mean_test_score"]
            df = df.rename(
                columns={
                    "param_n_components": "Number of components",
                    "param_covariance_type": "Type of covariance",
                    #"mean_test_score": "BIC score",
                    "mean_test_score": "silhouette score",
                }
            )
            #df.sort_values(by="BIC score")
            print(df)

            sns.catplot(
            data=df,
            kind="bar",
            x="Number of components",
            y="silhouette score",
            hue="Type of covariance")
            plt.ylim((0, 1))
            plt.show()

            
            
            #probs = grid_search.predict_proba(data_for_gmm)
            #print("probs")
            #print(probs)
            #name = 'nrajh'
            #filename = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\probsMU5.csv'
            #df = pd.DataFrame(probs) 
            # save the dataframe as a csv file 
            #df.to_csv(filename, header= False, index=False, na_rep='nan')

            # fibre cluster assignments
            fibre_clusters = grid_search.predict(data_to_cluster)
            n_fibre_clusters = np.max(fibre_clusters) + 1
                  
            fibre_centres_gmm_mean = grid_search.best_estimator_.means_
            #print("grid_search.best_estimator_._estimator_type")
            #print(grid_search.best_estimator_)
            fibre_centres_gmm_covariance = grid_search.best_estimator_.covariances_
       

        print("mean_n_fps")
        print(mean_n_fps)
        # Initialise arrays for storing results

        # Number of fibre potentials (FPs) in each MUP that belong to the same
        # cluster
        n_fps_per_mup_and_cluster = np.zeros((self.n_potentials, n_fibre_clusters))

        # Location estimates of each fibre based on each MUP
        # Note: unlike original code, data stored so indices match the
        # self.potentials_t_idx array
        mup_fibre_pos = np.full((self.n_potentials, 2, n_fibre_clusters), np.nan)
        fibre_centres_covariance = []
            
        # Find median location of each fibre
        for cluster_num in np.arange(n_fibre_clusters):
            # Sometimes multiple fibre potentials in the same MUP are assigned to
            # the same fibre clusters. Therefore, first compute average (mean)
            # position in each MUP in which the fibre cluster appears.
            # If no fibres with that cluster num appear in the MUP, position is
            # stored as np.nan.

            # Note: unlike original code, iterate through all MUPs (not just ones
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

                # Store number of fibre potentials found
                n_idx = len(idx)
                n_fps_per_mup_and_cluster[mup_num, cluster_num] = n_idx

                # Compute average position of the fibre based on the specified MUP
                if n_idx > 0:
                    pos = self.fibre_centres[idx, :]
                    mup_fibre_pos[mup_num, :, cluster_num] = np.mean(pos, axis=0)

            # Compute covariance of fibre positions               
            #covariance = np.cov(mup_fibre_pos[~np.isnan(mup_fibre_pos[:, 0, cluster_num]), :, cluster_num].T)
            #fibre_centres_covariance.append(covariance)

            # Compute median fibre positions
            fibre_centres_median = np.transpose(np.nanmedian(mup_fibre_pos, axis=0))
           
        # Store results as dictionary
        self.fibre_clustering_results = {
            "mean_n_fps": mean_n_fps,
            "n_fibre_clusters": n_fibre_clusters,
            "fibre_clusters": fibre_clusters,
            "n_fps_per_mup_and_cluster": n_fps_per_mup_and_cluster,
            "mup_fibre_pos": mup_fibre_pos,
            "fibre_centres_median": fibre_centres_median,
            "fibre_centres_gmm_mean": fibre_centres_gmm_mean,
            "fibre_centres_gmm_covariance": fibre_centres_gmm_covariance
        }
        self.analysis_performed["fibres_clustered"] = True
    
    def plot_fibre_locations_setup(
        self,        
        figsize=(10, 5),
        axis_label_size=14,
        tick_label_size=12,
        dpi=100,
        threeD = False
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
        figsize : TYPE, optional
            DESCRIPTION. The default is (10, 5).
        axis_label_size : TYPE, optional
            DESCRIPTION. The default is 14.
        tick_label_size : TYPE, optional
            DESCRIPTION. The default is 12.
        dpi : TYPE, optional
            DESCRIPTION. The default is 100.
        threeD : boolean
            Create 3D plot if true

        Returns
        -------
        None.

        TODO: finish docstring once vis is finalised
        TODO: consider adding outline for needle

        """

        # Create new figure with specified size
        if threeD:   
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(projection='3d')
        else:
            fig, ax = plt.subplots(figsize=figsize)
        
        
        fig.dpi = dpi
                     
        # Axis and tick labels
        ax.set_xlabel("position (mm)", fontsize=axis_label_size)
        ax.set_ylabel("position (mm)", fontsize=axis_label_size)
        ax.tick_params(axis="x", which="major", labelsize=tick_label_size)
        ax.tick_params(axis="y", which="major", labelsize=tick_label_size)

        if threeD:
            ax.set_zlabel(r'Time ($\mu$ seconds)', fontsize=axis_label_size, labelpad=8.0)
            ax.tick_params(axis="z", which="major", labelsize=tick_label_size)
            
        plt.title(f"Motor Unit {self.motor_unit_number+1}")   

        return fig, ax
    
    def plot_electrodes(
        self,
        motor_units,
        ax,
        marker="s",
        clr="silver",
        z = None
    ):
        """
        Plot electrode locations using their (x,y) coordinates.

        Electrodes are symbolised by grey squares by default.

        Parameters
        ----------
        ax : TYPE, optional
            DESCRIPTION. The default is None.
        marker : TYPE, optional
            DESCRIPTION. The default is "s".
        clr : TYPE, optional
            DESCRIPTION. The default is "silver".
        z : float
            z value for 3D plot
        Returns
        -------
        None.

        TODO: finish docstring once vis is finalised
        TODO: consider adding outline for needle

        """

        # Plot electrodes
        if z is None:        
            ax.scatter(motor_units.chan_xy[:, 0], motor_units.chan_xy[:, 1], marker=marker, color=clr)
        else:
            ax.scatter(motor_units.chan_xy[:, 0], motor_units.chan_xy[:, 1], np.full(len(motor_units.chan_xy[:, 0]), z), marker=marker, color=clr)

             
    def plot_fibre_potential_clustering(
        self,
        motor_units,
        plot_electrodes=True,
        pt_potentials_size=10,
        pt_potentials_alpha=0.4,        
        pt_mean_size = 50,
        n_sigma = 1,        
        axis_equal=True,
        ax=None,
        lw=0.5,
        figsize=(10, 5),
        axis_label_size=14,
        tick_label_size=12,
        dpi=100,
        cmap=None,
        max_x = 22,
        max_y = 2,
        plot_legend=True,
        legend_pt_size=50,
        legend_label_size=12,
        gmm=True
    ):
        """
        Create scatter plot of fibre localisations estimated from all fibre potentials
        with the location of each fibre overlaid. Ellipse confidence regions are plotted around te fibre locations
        Plots results from one motor unit at a time.

        Default point colour depends on the fibre cluster.

        Parameters
        ----------
        motor_units : TYPE
            DESCRIPTION.
        plot_electrodes : TYPE, optional
            DESCRIPTION. The default is True.
        pt_potentials_size : TYPE, optional
            DESCRIPTION. The default is 10.
        pt_potentials_alpha : TYPE, optional
            DESCRIPTION. The default is 0.5.    
        pt_mean_size : TYPE, optional
            DESCRIPTION. The default is 50.
        nsigma : float
            Number of St. Dev. to plot around the fibre centres
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
        max_x : float
            Maximum of x axis
        max_y : float
            Maximum of y axis
        plot_legend : boolean
            Plot the legend or not
        legend_pt_size : float
            Size of points in legend
        legend_label_size: float
            Size of labels in legend
        
        Returns
        -------
        None.

        TODO: finish docstring
        TODO: add option for fixing axis limits across different motor units.

        """
                    
        # Setup plot
        fig, ax = self.plot_fibre_locations_setup(figsize=figsize,
        axis_label_size=axis_label_size,
        tick_label_size=tick_label_size,
        dpi=dpi
        )
              
        # Add electrodes to plot
        if plot_electrodes:
            self.plot_electrodes(motor_units, ax)
       
        n_clusters = self.fibre_clustering_results["n_fibre_clusters"]
        
        # Plot clusters
        for cluster_no in range(n_clusters):
            self._plot_cluster_points(cluster_no, n_clusters, ax, pt_size=pt_potentials_size,
            pt_alpha=pt_potentials_alpha, cmap = cmap, lw=lw)
       
        # Plot centres and covariance regions (if not GMM)
        for cluster_no in range(n_clusters):
            self._plot_fibre_location(cluster_no, n_clusters, ax, gmm, pt_mean_size, n_sigma)
        
        if gmm:
            self._plot_fitted_gmms(ax, n_sigma)
        
        # Plot larger markers for median fibre locations, Not much difference to medians
        #ax.scatter(
        #    self.fibre_clustering_results["fibre_centres_median"][:, 0],
        #    self.fibre_clustering_results["fibre_centres_median"][:, 1],
        #    50,
        #    marker='*',
        #    facecolors='k',
        #    edgecolors='k',
        #    linewidths=1,
        #)
                    
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
         
        # y axis limits    
        ax.set_ylim(-max_y, max_y)
        
        # Set x axis limits              
        ax.set_xlim(-1, max_x)
            
        # Equal aspect ratio, (this can mess up the axis limits)
        if axis_equal:
            ax.axis("equal")
            
             
    def get_cluster_colour(self, cluster_no, n_clusters, cmap = None): 
        if cmap is None:
            if n_clusters <= 10:
                cmap = colormaps["tab10"].colors
            elif n_clusters <= 20:
                cmap = colormaps["tab20"].colors
            else:
                cmap = plt.cm.rainbow(np.linspace(0, 1, n_clusters))
            
        return cmap[cluster_no]    
     
    def _plot_cluster_points(self, cluster_no, n_clusters, ax, pt_size, pt_alpha, cmap = None, lw = 0, threeD = False, sampling_freq = 1):
          
        x = self.fibre_centres[(self.fibre_clustering_results["fibre_clusters"] == cluster_no), 0]
        y = self.fibre_centres[(self.fibre_clustering_results["fibre_clusters"] == cluster_no), 1]
        
        if threeD:            
            z = (self.fibre_potential_times[(self.fibre_clustering_results["fibre_clusters"] == cluster_no)] / sampling_freq)*1e6
           
                 
        # Get colour of points
        pt_facecolor = self.get_cluster_colour(cluster_no, n_clusters, cmap)
        
        # Plot points for this cluster
        if threeD:
            ax.scatter(x, y, z,
                   s = pt_size,
                   alpha=pt_alpha,
                   facecolors=pt_facecolor,                               
                   linewidth=lw,
                   label=f"fibre {cluster_no + 1}"
                   )
        else:
            ax.scatter(x, y,
                   pt_size,
                   alpha=pt_alpha,
                   facecolors=pt_facecolor,                               
                   linewidth=lw
                   )
            
    def _plot_fitted_gmms(self, ax, n_sigma):
        #color_iter = sns.color_palette("tab10", 2)[::-1]
        #Y_ = grid_search.predict(X)

        #n_clusters = len(self.fibre_clustering_results["fibre_centres_gmm_mean"])
        #if tied, define and save earlier in results - find out which cov model and adapt earlier...
        cov = self.fibre_clustering_results["fibre_centres_gmm_covariance"] 
        cov = np.array( [[cov[0,0], cov[0,1]], [cov[1,0], cov[1,1]]] )
        
        #print(i)
        #print("cov")
        #print(cov)
        #if cov.ndim < 2:
        #    cov = np.array([[cov[0], 0], [0, cov[1]]]) # diag
        print("cov-end")
        print(cov)
        print("\n")
        
        #for i, (mean, covX) in enumerate(
        #for i, (mean) in enumerate(
        #    zip(
        #        self.fibre_clustering_results["fibre_centres_gmm_mean"],
        #        #self.fibre_clustering_results["fibre_centres_gmm_covariance"]                
        #    )
        #):
        for i, mean in enumerate(self.fibre_clustering_results["fibre_centres_gmm_mean"]):    
            print(i)
            v, w = np.linalg.eigh(cov)           

            angle = np.arctan2(w[0][1], w[0][0])
            angle = 180.0 * angle / np.pi  # convert to degrees
            # Radius so times by 2 for diameter
            v = n_sigma * 2 * np.sqrt(v)
            ellipse = Ellipse(mean, v[0], v[1], angle=180.0 + angle, edgecolor="black", facecolor='none') #color=self.get_cluster_colour(i, n_clusters))
            #ellipse.set_clip_box(fig.bbox)
            #ellipse.set_alpha(0.5)
            ax.add_artist(ellipse)

    def confidence_ellipse(self, x, y, ax, n_std=3.0, facecolor='none', **kwargs):
        """
        Taken from matplotlib documentation
        https://matplotlib.org/stable/gallery/statistics/confidence_ellipse.html
        
        Create a plot of the covariance confidence ellipse of *x* and *y*.

        Parameters
        ----------
        x, y : array-like, shape (n, )
            Input data.

        ax : matplotlib.axes.Axes
            The Axes object to draw the ellipse into.

        n_std : float
            The number of standard deviations to determine the ellipse's radiuses.

        **kwargs
            Forwarded to `~matplotlib.patches.Ellipse`

        Returns
        -------
        matplotlib.patches.Ellipse
        """
        if x.size != y.size:
            raise ValueError("x and y must be the same size")

        cov = np.cov(x, y)
        pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
        # Using a special case to obtain the eigenvalues of this
        # two-dimensional dataset.
        ell_radius_x = np.sqrt(1 + pearson)
        ell_radius_y = np.sqrt(1 - pearson)
        ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                          facecolor=facecolor, **kwargs)

        # Calculating the standard deviation of x from
        # the squareroot of the variance and multiplying
        # with the given number of standard deviations.
        scale_x = np.sqrt(cov[0, 0]) * n_std
        mean_x = np.mean(x)

        # calculating the standard deviation of y ...
        scale_y = np.sqrt(cov[1, 1]) * n_std
        mean_y = np.mean(y)

        transf = transforms.Affine2D() \
            .rotate_deg(45) \
            .scale(scale_x, scale_y) \
            .translate(mean_x, mean_y)

        ellipse.set_transform(transf + ax.transData)
        return ax.add_patch(ellipse)   

    def _plot_fibre_location(self, cluster_no, n_clusters, ax, gmm, pt_mean_size = 10, n_sigma = 1, pt_facecolor = None):
        
        if gmm:
            center = self.fibre_clustering_results["fibre_centres_gmm_mean"][cluster_no]
        else:
            x = np.array(self.fibre_centres[(self.fibre_clustering_results["fibre_clusters"] == cluster_no), 0])
            y = np.array(self.fibre_centres[(self.fibre_clustering_results["fibre_clusters"] == cluster_no), 1])      
            center = np.array([[np.mean(x)], [np.mean(y)]])
        
        print("center")
        print(center)
        
        if pt_facecolor is None:
            pt_facecolor = self.get_cluster_colour(cluster_no, n_clusters)
                
        ax.scatter(center[0], center[1], pt_mean_size, color=pt_facecolor, edgecolors='black',
                   label=f"fibre {cluster_no + 1}")
        
        if not gmm:
            self.confidence_ellipse(x, y, ax, n_sigma, edgecolor="black")
    

    def plot_3D_fibre_potential_clustering(
        self,
        motor_units,
        plot_electrodes=True,
        pt_potentials_size=10,
        pt_potentials_alpha=0.4,        
        pt_mean_size = 50,
        nsigma = 1,        
        axis_equal=True,
        ax=None,
        lw=0.5,
        figsize=(10, 5),
        axis_label_size=14,
        tick_label_size=12,
        dpi=100,
        cmap=None,
        max_x = 22,
        max_y = 2,
        plot_legend=True,
        legend_pt_size=50,
        legend_label_size=12,
        sampling_feq=20000
    ):
        """
        Create scatter plot of fibre localisations estimated from all fibre potentials
        with the location of each fibre overlaid. Ellipse confidence regions are plotted around te fibre locations
        Plots results from one motor unit at a time.

        Default point colour depends on the fibre cluster.

        Parameters
        ----------
        motor_units : TYPE
            DESCRIPTION.
        plot_electrodes : TYPE, optional
            DESCRIPTION. The default is True.
        pt_potentials_size : TYPE, optional
            DESCRIPTION. The default is 10.
        pt_potentials_alpha : TYPE, optional
            DESCRIPTION. The default is 0.5.    
        pt_mean_size : TYPE, optional
            DESCRIPTION. The default is 50.
        nsigma : float
            Number of St. Dev. to plot around the fibre centres
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
        max_x : float
            Maximum of x axis
        max_y : float
            Maximum of y axis
        plot_legend : boolean
            Plot the legend or not
        legend_pt_size : float
            Size of points in legend
        legend_label_size: float
            Size of labels in legend
        
        Returns
        -------
        None.

        TODO: finish docstring
        TODO: add option for fixing axis limits across different motor units.

        """
                    
        # Setup plot
        fig, ax = self.plot_fibre_locations_setup(figsize=figsize,
        axis_label_size=axis_label_size,
        tick_label_size=tick_label_size,
        dpi=dpi,
        threeD = True
        )
        
        # Add electrodes to plot at botton z = 0
        if plot_electrodes:
            self.plot_electrodes(motor_units, ax, z=0)
       
        n_clusters = self.fibre_clustering_results["n_fibre_clusters"]
        
        # Plot clusters
        for cluster_no in range(n_clusters):
            self._plot_cluster_points(cluster_no, n_clusters, ax, pt_size=pt_potentials_size,
            pt_alpha=pt_potentials_alpha, cmap = cmap, lw=lw, threeD = True, sampling_freq = sampling_feq)
       
        # Plot centres and covariance regions
        #for cluster_no in range(n_clusters):
        #    self._plot_covariance_region(cluster_no, n_clusters, ax, pt_mean_size, nsigma)
            
                    
        # Legend
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
  
        # y axis limits    
        ax.set_ylim(-max_y, max_y)
        
        # Set x axis limits              
        ax.set_xlim(-1, max_x)
            
        # Equal aspect ratio, (this can mess up the axis limits if true when displaying as pop up plot in Windows)
        if axis_equal:
            ax.axis("equal")
    
    def remove_outliers_iqr(self, intervals):
        """      
        Parameters
        ----------
        intervals: npt.NDArray[npt.int]
            array of time intervals
            
        Returns
        -------
        npt.NDArray[npt.int]
            array of time intervals with outliears removed
            
        """
        
        # calculate interquartile range
        q25, q75 = np.nanpercentile(intervals, 25), np.nanpercentile(intervals, 75)
        iqr = q75 - q25
        
        print('Percentiles: 25th=%.3f, 75th=%.3f, IQR=%.3f' % (q25, q75, iqr))
        # calculate the outlier cutoff
        cut_off = iqr * 1.5
        lower, upper = q25 - cut_off, q75 + cut_off
        
        # Replace outliers with nan
        return [np.nan if x < lower or x > upper else x for x in intervals] 

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
        
    def jitter_analysis_between_two_fibres(self, fibre1_num, fibre2_num, remove_outliers):
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
             
        Parameters
        ----------
        fibre1_num : int
            Fibre number for the first fibre, given previously from cluster analysis (0,1,2,...)
        fibre2_num : int
            Fibre number for the second fibre
        remove_outliers: boolean
            Remove outliers in fibre potential times to avoid probable miss-classifications
            
        Returns
        -------
        None.

        """
               
        # Calculate medians of all the fibre potentials for fibre 1 and fibre 2
        all_fibre1_potentials_idx = np.flatnonzero((self.fibre_clustering_results["fibre_clusters"] == fibre1_num))                 
        median_time1 = np.median(self.fibre_potential_times[all_fibre1_potentials_idx])
        
        all_fibre2_potentials_idx = np.flatnonzero((self.fibre_clustering_results["fibre_clusters"] == fibre2_num))                 
        median_time2 = np.median(self.fibre_potential_times[all_fibre2_potentials_idx])
             
        # Length of time intervals between fibre potentials in the two different fibres
        fibre_potential_time_diffs = np.full(len(self.mup_onsets), np.nan)
        
        print("Jitter between 2")
        #print()
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
                # Pick fibre potentials closest to the median
                fibre1_potential_to_use = np.argmin(np.abs(median_time1 - self.fibre_potential_times[fibre1_potentials_idx]))
                fibre2_potential_to_use = np.argmin(np.abs(median_time2 - self.fibre_potential_times[fibre2_potentials_idx]))
                
                #Get time difference for this MUP between fibre potentials
                fib_pot_pos1 = fibre1_potentials_idx[fibre1_potential_to_use]
                fib_pot_pos2 = fibre2_potentials_idx[fibre2_potential_to_use]
                fibre_potential_time_diffs[mup_num] = self._calculate_fibre_potentials_time_diff(fib_pot_pos1, fib_pot_pos2)
        
        # Remove outliers in time intervals
        if remove_outliers:
            #print("before")
            #print(fibre_potential_time_diffs)
            fibre_potential_time_diffs = self.remove_outliers_iqr(fibre_potential_time_diffs)
            #print("after")
            #print(fibre_potential_time_diffs)
            
        # Compute consecutive differences       
        consecutive_diffs = np.full((len(self.mup_onsets) - 1), np.nan)
           
        for mup_num in range(self.n_potentials - 1):            
            if not np.isnan(fibre_potential_time_diffs[mup_num]) and not np.isnan(fibre_potential_time_diffs[mup_num + 1]):
                consecutive_diffs[mup_num] = np.abs(fibre_potential_time_diffs[mup_num] - fibre_potential_time_diffs[mup_num + 1])
         
        if remove_outliers:
            consecutive_diffs = self.remove_outliers_iqr(consecutive_diffs)
            
        # Compute mean consecutive difference
        mean_consecutive_diff = np.nanmean(consecutive_diffs)

        return mean_consecutive_diff, fibre_potential_time_diffs, consecutive_diffs

    def jitter_analysis(self, remove_outliers = True):
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
        n_fibre_clusters = self.fibre_clustering_results["n_fibre_clusters"]
        
        number_of_jitter_calcs = int(n_fibre_clusters * (n_fibre_clusters - 1) / 2)
        fibre1_numbers = np.zeros(number_of_jitter_calcs)
        fibre2_numbers = np.zeros(number_of_jitter_calcs)
        mean_consecutive_diffs = np.zeros(number_of_jitter_calcs)
        fibre_potential_time_diffs = np.zeros((number_of_jitter_calcs, len(self.mup_onsets)))
        consecutive_diffs = np.zeros((number_of_jitter_calcs, len(self.mup_onsets) - 1))
        
        count = 0
        print("Num fibre clusters")
        print(n_fibre_clusters)
        for fibre1_num in range(n_fibre_clusters - 1):
            for fibre2_num in np.arange(fibre1_num + 1, n_fibre_clusters):               
                mean_consecutive_diffs[count], fibre_potential_time_diffs[count,:], consecutive_diffs[count,:] = self.jitter_analysis_between_two_fibres(fibre1_num, fibre2_num, remove_outliers)
                fibre1_numbers[count] = fibre1_num
                fibre2_numbers[count] = fibre2_num
                count += 1
                print(f"MCD between fibres {fibre1_num} and {fibre2_num} is {mean_consecutive_diffs[count-1]}")
        
        self.fibre_jitter_results = {
                "fibre1_numbers": fibre1_numbers,
                "fibre2_numbers": fibre2_numbers,
                "mean_consecutive_diffs": mean_consecutive_diffs,
                "differences": fibre_potential_time_diffs,
                "consecutive_diffs": consecutive_diffs
            }
        
        self.analysis_performed["fibres_jitter_computed"] = True
 
    def plot_fibre_potential_time_diffs(self, fibre1_num, fibre2_num, sampling_freq, show = False):
        """
        Plot a histogram for time differences between fibre potentials
            
        Parameters
        ----------
        fibre1_num : int
            Fibre number for the first fibre, given previously from cluster analysis (0,1,2,...)
        fibre2_num : int
            Fibre number for the second fibre
        sampling_freq: float
            Sampling frequency
            
        Returns
        -------
        None.

        """
        
        # Get index for this pair of fibres so that the results can be retreived
        res_idx = np.where( 
         np.all(
                            (
                                (self.fibre_jitter_results["fibre1_numbers"] == fibre1_num),
                                (self.fibre_jitter_results["fibre2_numbers"] == fibre2_num),
                            ),
                    axis=0,
         ))
                
        if len(res_idx) > 0:
            res_idx = res_idx[0]
        else:
            print(f"Jitter results not found for fibres {fibre1_num + 1} and {fibre2_num + 1}!")
            return
        
        # Get fibre differences and convert to time in seconds
        fibre_pot_diffs = self.fibre_jitter_results["differences"][res_idx, :] / sampling_freq
        fibre_pot_diffs = fibre_pot_diffs.flatten()
        
        print(fibre_pot_diffs.shape)
        _, ax = plt.subplots()
        
        if not np.isnan(fibre_pot_diffs).all():
            ax.hist(fibre_pot_diffs, bins=30, density=True, color = "lightgrey", edgecolor='k', linewidth=0.5)

        plt.title(f"Fibre potential intervals (motor unit {self.motor_unit_number+1}, fibres {fibre1_num+1} and {fibre2_num+1})")        
        #mean_consecutive_diff = self.fibre_jitter_results["mean_consecutive_diffs"][res_idx]

        mean = np.nanmean(fibre_pot_diffs)
        st_dev = np.nanstd(fibre_pot_diffs, ddof=1)
        textstr = '\n'.join((
        r'Mean $= %.0f \mu$s' % (mean*1e6, ),     
        r'St. dev. $=%.0f \mu$s' % (st_dev*1e6, )))

        # these are matplotlib.patch.Patch properties
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

        # place a text box in upper left in axes coords
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
                verticalalignment='top', bbox=props)

        # Show plot on screen now if requested
        if show:
            plt.show() 

    def plot_fibre_consecutive_diffs(self, fibre1_num, fibre2_num, sampling_freq, show = False):
        """
        Plot a histogram for the consecutive differences (from one MUP to the next)
        between the length of time intervals of timings between fibre potentials
            
        Parameters
        ----------
        fibre1_num : int
            Fibre number for the first fibre, given previously from cluster analysis (0,1,2,...)
        fibre2_num : int
            Fibre number for the second fibre
        sampling_freq: float
            Sampling frequency
        show : boolean
            Show plot if true
            
        Returns
        -------
        None.

        """
        
        # Get index for this pair of fibres so that the results can be retreived
        res_idx = np.where( 
         np.all(
                            (
                                (self.fibre_jitter_results["fibre1_numbers"] == fibre1_num),
                                (self.fibre_jitter_results["fibre2_numbers"] == fibre2_num),
                            ),
                    axis=0,
         ))
        
        if len(res_idx) > 0:
            res_idx = res_idx[0]
        else:
            print(f"Jitter results not found for fibres {fibre1_num + 1} and {fibre2_num + 1}!")
            return
        
        # Get consecutive_diffs and convert to time in seconds
        consecutive_diffs = self.fibre_jitter_results["consecutive_diffs"][res_idx, :] / sampling_freq
        consecutive_diffs = consecutive_diffs.flatten()
        
        print(consecutive_diffs.shape)
        _, ax = plt.subplots()
        
        if not np.isnan(consecutive_diffs).all():
            ax.hist(consecutive_diffs, bins=30, density=True, color = "lightgrey", edgecolor='k', linewidth=0.5)

        plt.title(f"Consecutive differences (motor unit {self.motor_unit_number+1}, fibres {fibre1_num+1} and {fibre2_num+1})")        
        mean_consecutive_diff = self.fibre_jitter_results["mean_consecutive_diffs"][res_idx] / sampling_freq
        
        mean = np.nanmean(consecutive_diffs)
        st_dev = np.nanstd(consecutive_diffs, ddof=1)
        textstr = '\n'.join((
        r'Mean $= %.0f \mu$s' % (mean*1e6, ),     
        r'St. dev. $=%.0f \mu$s' % (st_dev*1e6, )))

        print(mean_consecutive_diff)
        print(mean)
        # these are matplotlib.patch.Patch properties
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

        # place a text box in upper left in axes coords
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
                verticalalignment='top', bbox=props)

        # Show plot on screen now if requested
        if show:
            plt.show() 
        
    def plot_jitter_heat_plot(self, sampling_freq, show = False):
        """
        Plot a heat map of MCDs between fibres
            
        Parameters
        ----------
        show : boolean
            Show plot if true
            
        Returns
        -------
        None.

        """
        n_fibre_pairs = len(self.fibre_jitter_results["fibre2_numbers"])
        if n_fibre_pairs == 0:
            return
        
        n_fibres = int(np.max(self.fibre_jitter_results["fibre2_numbers"]) + 1)
        
        data = np.full((n_fibres, n_fibres), np.nan)
        print(data.shape)
        print(self.fibre_jitter_results["fibre1_numbers"])
        print(self.fibre_jitter_results["fibre2_numbers"])
        for i in range(n_fibre_pairs):
            fib1 = int(self.fibre_jitter_results["fibre1_numbers"][i])
            fib2 = int(self.fibre_jitter_results["fibre2_numbers"][i])
            val = self.fibre_jitter_results["mean_consecutive_diffs"][i]
            if not np.isnan(val):
                val = int((val / sampling_freq) * 1e6 + 0.5)
                
            data[fib1, fib2] = val
            data[fib2, fib1] = val
                      
        # plotting the heatmap
        str_fibres = [str(x) for x in np.arange(1, n_fibres + 1)]
        print(str_fibres)
        print(data)
        hm = sns.heatmap(data=data, annot=True, xticklabels=str_fibres, yticklabels=str_fibres, cbar_kws={'label': r'$\mu$ seconds'}, fmt='g') 
    
        hm.set_xlabel("Fibre number")
        hm.set_ylabel("Fibre number")
        hm.set_title("Mean Consecutive Differences")
        
        # Show plot on screen now if requested
        if show:
            plt.show()
        
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
        motor_unit_idx = None,
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
            if motor_unit_idx < 0:
                motor_units = []
            else:
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
   
