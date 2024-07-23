#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGAnalysisReconstructSettings for localisation.

For use with EMGAnalysisReconstruct.

"""


class EMGAnalysisReconstructSettings:
    """
    Class for storing EMG analysis reconstruct settings.

    """

    def __init__(self):
        """
        Initialise settings.

        Returns
        -------
        None.

        """

        # Default settings
        self.n_electrodes = 64
        self.mavg_length = 1
        self.mavg_all = False
        self.spike_dur = 20
        self.half_subsample_size = 200
        self.max_opt_iterations = 200
        self.xtol = 0.01
        self.ftol = 1
        self.y_scaling_factor = 1.0

        # 2D peak finding options for localisation
        self.find_peaks_2d_sigma_mups = 2
        self.find_peaks_2d_sigma_time = 2
        self.find_peaks_2d_truncate = 2
        self.find_peaks_2d_use_tophat = False
        # Integer
        self.find_peaks_2d_tophat_disk_radius = 1
        self.find_peaks_2d_min_peaks = 1
        self.find_peaks_2d_max_peaks = 5
        self.find_peaks_2d_neighbour_mups = 5
        self.find_peaks_2d_neighbour_time = 5

    def get_settings_dict(self):
        """
        Saves settings for analysis

        Parameters
        ----------
        None.

        Returns
        -------
        None

        """

        # Define settings dictionary
        settings_dict = {
            "n_electrodes": self.n_electrodes,
            "mavg_length": self.mavg_length,
            "mavg_all": self.mavg_all,
            "spike_dur": self.spike_dur,
            "half_subsample_size": self.half_subsample_size,
            "max_opt_iterations": self.max_opt_iterations,
            "xtol": self.xtol,
            "ftol": self.ftol,
            "y_scaling_factor": self.y_scaling_factor,
            "find_peaks_2d_sigma_mups": self.find_peaks_2d_sigma_mups,
            "find_peaks_2d_sigma_time": self.find_peaks_2d_sigma_time,
            "find_peaks_2d_truncate": self.find_peaks_2d_truncate,
            "find_peaks_2d_use_tophat": self.find_peaks_2d_use_tophat,
            "find_peaks_2d_tophat_disk_radius": self.find_peaks_2d_tophat_disk_radius,
            "find_peaks_2d_min_peaks": self.find_peaks_2d_min_peaks,
            "find_peaks_2d_max_peaks": self.find_peaks_2d_max_peaks,
            "find_peaks_2d_neighbour_mups": self.find_peaks_2d_neighbour_mups,
            "find_peaks_2d_neighbour_time": self.find_peaks_2d_neighbour_time,
        }

        return settings_dict

    def set_settings_from_dict(self, settings_dict):
        """
        Saves settings for analysis

        Parameters
        ----------
        settings_dict: Dictionary
            Dictionary with all the settings save in it

        Returns
        -------
        None

        """

        self.n_electrodes = settings_dict["n_electrodes"]
        self.mavg_length = settings_dict["mavg_length"]
        self.mavg_all = settings_dict["mavg_all"]
        self.spike_dur = settings_dict["spike_dur"]
        self.half_subsample_size = settings_dict["half_subsample_size"]
        self.max_opt_iterations = settings_dict["max_opt_iterations"]
        self.xtol = settings_dict["xtol"]
        self.ftol = settings_dict["ftol"]
        self.y_scaling_factor = settings_dict["y_scaling_factor"]
        self.find_peaks_2d_sigma_mups = settings_dict["find_peaks_2d_sigma_mups"]
        self.find_peaks_2d_sigma_time = settings_dict["find_peaks_2d_sigma_time"]
        self.find_peaks_2d_truncate = settings_dict["find_peaks_2d_truncate"]
        self.find_peaks_2d_use_tophat = settings_dict["find_peaks_2d_use_tophat"]
        self.find_peaks_2d_tophat_disk_radius = settings_dict["find_peaks_2d_tophat_disk_radius"]
        self.find_peaks_2d_min_peaks = settings_dict["find_peaks_2d_min_peaks"]
        self.find_peaks_2d_max_peaks = settings_dict["find_peaks_2d_max_peaks"]
        self.find_peaks_2d_neighbour_mups = settings_dict["find_peaks_2d_neighbour_mups"]
        self.find_peaks_2d_neighbour_time = settings_dict["find_peaks_2d_neighbour_time"]

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
        ans += "\nMoving average length: "
        ans += str(self.mavg_length)
        ans += "\nMoving average all: "
        ans += str(self.mavg_all)
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
        ans += "\nScaling factor, y: "
        ans += str(self.y_scaling_factor)
        ans += "\n"
        ans += "\n2D Peak Finding Options"
        ans += "\nGaussian filter, sigma MUPs: "
        ans += str(self.find_peaks_2d_sigma_mups)
        ans += "\nGaussian filter, sigma time (indices): "
        ans += str(self.find_peaks_2d_sigma_time)
        ans += "\nGaussian filter, truncate: "
        ans += str(self.find_peaks_2d_truncate)
        ans += "\nUse tophat filter: "
        ans += str(self.find_peaks_2d_use_tophat)
        if self.find_peaks_2d_use_tophat:
            ans += "\nTophat filter, disk radius (integer): "
            ans += str(self.find_peaks_2d_tophat_disk_radius)
        ans += "\nMinimum number of peaks (if possible): "
        ans += str(self.find_peaks_2d_min_peaks)
        ans += "\nMaximum number of peaks: "
        ans += str(self.find_peaks_2d_max_peaks)
        ans += "\nNeighbourhood size, MUPs: "
        ans += str(self.find_peaks_2d_neighbour_mups)
        ans += "\nNeighbourhood size, time (indices): "
        ans += str(self.find_peaks_2d_neighbour_time)

        return ans


class EMGAnalysisMotorUnitSettings:
    """
    Class for storing settings for finding motor units.

    """

    def __init__(self):
        """
       
        Returns
        -------
        None.

        """

        # Default settings
        # TK Filter options
        self.tk_filt_thres_spike = 0.1
        self.tk_filt_thres_PsC = 0.1

    def get_settings_dict(self):
        """
        Saves settings for analysis

        Parameters
        ----------
        None.

        Returns
        -------
        None

        """

        # Define settings dictionary
        settings_dict = {
            "tk_filt_thres_spike": self.tk_filt_thres_spike,
            "tk_filt_thres_PsC": self.tk_filt_thres_PsC           
        }

        return settings_dict

    def set_settings_from_dict(self, settings_dict):
        """
        Saves settings for analysis

        Parameters
        ----------
        settings_dict: Dictionary
            Dictionary with all the settings save in it

        Returns
        -------
        None

        """

        self.tk_filt_thres_spike = settings_dict["tk_filt_thres_spike"]
        self.tk_filt_thres_PsC = settings_dict["tk_filt_thres_PsC"]

    def __str__(self):
        """
        Return a string for the object

        Returns
        -------
        String

        """

        ans = "Find Motor Units EMG Analysis Settings"
        ans += "\nTeager-Kaiser filter spike detection threshold: "
        ans += str(self.tk_filt_thres_spike)
        ans += "\nTeager-Kaiser filter pseudo-correlation threshold: "
        ans += str(self.tk_filt_thres_PsC)

        return ans

class EMGAnalysisMotorUnitClusterSettings:
    """
    Class for storing settings for motor unit cluster analysis.

    """

    def __init__(self):
        """
        Initialise settings.

        clustering_method : string
            Options are 'k_means', 'gmm' and 'dbscan'
        time_scale : float
            if greater than 0 then time is used as a 3rd dimension to cluster the points and
            is scaled by this amount
        k_means_random_state : int
            Determines random number generation for centroid initialization; passed to
            k-means algorithm
        k_means_k : int
            the of clusters to fit, if set to 0 uses default of (rounded) mean number of fibre
            potentials (FPs) per motor unit potential

        Returns
        -------
        None.

        """

        # Default settings
        # Clustering options, k-means, dbscan or gmm
        self.clustering_method = "dbscan"
        # If time_scale > 0 then time is included as a 3rd dimension and scaled as given
        # between 0 and 20 is probably suitable
        self.time_scale = 0
        self.k_means_random_state = 0
        self.k_means_k = 0
        self.dbscan_eps = 0.1
        self.dbscan_min_samples = 10
        # Covariance type for GMM clustering, options are: "spherical", "tied", "diag" and "full"        
        self.gmm_covariance_type = "tied"        

    def get_settings_dict(self):
        """
        Saves settings for analysis

        Parameters
        ----------
        None.

        Returns
        -------
        None

        """

        # Define settings dictionary
        settings_dict = {           
            "clustering_method": self.clustering_method,
            "time_scale": self.time_scale,
            "k_means_random_state": self.k_means_random_state,
            "k_means_k": self.k_means_k,
            "dbscan_eps": self.dbscan_eps,
            "dbscan_min_samples": self.dbscan_min_samples,
            "gmm_covariance_type": self.gmm_covariance_type            
        }

        return settings_dict

    def set_settings_from_dict(self, settings_dict):
        """
        Saves settings for analysis

        Parameters
        ----------
        settings_dict: Dictionary
            Dictionary with all the settings save in it

        Returns
        -------
        None

        """

        self.clustering_method = settings_dict["clustering_method"]
        self.time_scale = settings_dict["time_scale"]
        self.k_means_random_state = settings_dict["k_means_random_state"]
        self.k_means_k = settings_dict["k_means_k"]
        self.dbscan_eps = settings_dict["dbscan_eps"]
        self.dbscan_min_samples = settings_dict["dbscan_min_samples"]
        self.gmm_covariance_type = settings_dict["gmm_covariance_type"]        

    def __str__(self):
        """
        Return a string for the object

        Returns
        -------
        String

        """

        ans = "\nCluster Fibre Potentials EMG Analysis Settings"
        ans += "\nClustering Method: "
        ans += str(self.clustering_method)
        ans += "\nTime Scale (indices): "
        ans += str(self.time_scale)
        if self.time_scale == 0:
            ans += " (time not used to cluster)"
        if self.clustering_method == "k-means":
            ans += "\nK-Means, Random State: "
            ans += str(self.k_means_random_state)
            ans += "\nK-Means, k: "
            ans += str(self.k_means_k)
            if self.time_scale == 0:
                ans += " (number of clusters given by silhouette score)"
        elif self.clustering_method == "dbscan":
            ans += "\nDBSCAN, epsilson: "
            ans += str(self.dbscan_eps)
            ans += "\nDBSCAN, minimum samples: "
            ans += str(self.dbscan_min_samples)
        elif self.clustering_method == "gmm":
            ans += "\nGMM, GMM covariance type: "
            ans += str(self.gmm_covariance_type)        

        return ans
    
class EMGAnalysisMotorUnitJitterSettings:
    """
    Class for storing settings for motor unit jitter analysis.

    """

    def __init__(self):
        """
       
        Returns
        -------
        None.

        """

        # Default settings
        self.remove_outliers = True

    def get_settings_dict(self):
        """
        Saves settings for analysis

        Parameters
        ----------
        None.

        Returns
        -------
        None

        """

        # Define settings dictionary
        settings_dict = {
            "remove_outliers": self.remove_outliers,
        }

        return settings_dict

    def set_settings_from_dict(self, settings_dict):
        """
        Saves settings for analysis

        Parameters
        ----------
        settings_dict: Dictionary
            Dictionary with all the settings save in it

        Returns
        -------
        None

        """

        self.remove_outliers = settings_dict["remove_outliers"]

    def __str__(self):
        """
        Return a string for the object

        Returns
        -------
        String

        """

        ans = "\nJitter EMG Analysis Settings: "
        ans += "\nRemove outliers: "
        ans += str(self.remove_outliers)

        return ans