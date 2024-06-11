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
        self.mavg_length = 1
        self.mavg_all = False
        self.localise_first = False
        self.spike_dur = 20
        self.half_subsample_size = 200
        self.max_opt_iterations = 200
        self.xtol = 0.01
        self.ftol = 1

    def __str__(self):
        """
        Return a string for the object

        Returns
        -------
        String

        """

        ans = "EMG Analysis Reconstruct Settings"
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
        ans += "\n"

        return ans


class EMGAnalysisMotorUnitSettings:
    """
    Class for storing settings for finding motor units.

    """

    def __init__(self):
        """
        Initialise settings.

        Returns
        -------
        None.

        """

        # Default settings
        self.tk_filt_thres_spike = 0.1
        self.tk_filt_thres_PsC = 0.1

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
        ans += "\n"

        return ans
