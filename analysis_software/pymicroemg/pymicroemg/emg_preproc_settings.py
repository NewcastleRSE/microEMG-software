#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A Class, EMGPreprocSettings, for configuring and storing EMG preprocessing
settings (applied to EMGData)

"""
import json


class EMGPreprocSettings:
    """
    Class for storing EMG preprocessing settings.

    Attributes to add:
    mains noise removal, automatic bad channel detection
    Consider keeping the channels removed/labelled as "bad" a channel attribute
    (limit this class to settings that can directly be applied to any EMG
     recording)

    """

    def __init__(self):
        """
        Initialise preprocessing settings. When first initialised, the default
        settings are none (i.e., set to false for whether to run each preprocessing
        step).

        Returns
        -------
        None.

        """

        # Remove mains noise
        self.remove_mains = False
        self.remove_mains_settings = {}

        # Butterworth filter
        self.butterworth_filter = False
        self.butterworth_filter_settings = {}
    
    def __str__(self):
        """
        Return a string for the object

        Returns
        -------
        String

        """
        
        ans = "EMG Preprocessing Settings\n"
        ans += "Remove mains noise: "
        if(self.remove_mains):
            ans += "True\n"
        else:
            ans += "False\n"
            
        ans += "Remove mains noise settings:\n"
        ans += str(self.remove_mains_settings)
        ans += "\n"
        
        ans += "Butterworth filter: "
        if(self.butterworth_filter):
            ans += "True\n"
        else:
            ans += "False\n"
        
        ans += "Butterworth filter settings:\n"
        ans += str(self.butterworth_filter_settings)
        ans += "\n"
        
        return ans
    
    @staticmethod
    def _get_filter_types_allowed() -> list[str]:
        """
        Get list of allowed filter types

        Returns
        -------
        list[str]
            List of filter types that are allowed to be used for filtering.

        """
        filter_types_allowed = ["lowpass", "highpass", "bandpass"]
        return filter_types_allowed

    @staticmethod
    def _get_n_freq_per_filter_type() -> dict[str, int]:
        filter_n_freq = {"lowpass": 1, "highpass": 1, "bandpass": 2}

        return filter_n_freq

    def add_butterworth_filter(
        self,
        cutoff_freq: None | list[float] | float = None,
        order: int = 6,
        filter_type: str = "bandpass",
        apply_filter: bool = True,
    ):
        """
        Add filter and settings for a zero-phase Butterworth filter. See
        scipy.signal.butter for parameter details.

        Parameters
        ----------
        cutoff_freq : None | list[float] | float, optional
            Cutoff frequency or frequencies to pass to scipy.signal.butter. The default
            is [500, 2000] if the filter type is "bandpass". The cutoff frequency must
            be specified for other filter types.
        order : int, optional
            Filter order; must be even. The default is 6.
        filter_type : str, optional
            Type of filter - must be "low", "lowpass", "high", "highpass", or
            "bandpass". The default is "bandpass".
        apply_filter: bool, optional
            Whether to apply the specified filter settings during preprocessing. If
            False, the specified filter settings will be stored, but not used during
            preprocessing. This behaviour may be useful when filtering is turned off,
            but may be turned on later (e.g., by a GUI). The default is True.

        Raises
        ------
        ValueError
            Raised if filter order is not even.
            Raised if filter type is not one of the allowed types.
            Raised if filter cutoff frequency is not a list or float.
            Raised if filter cutoff frequency list has length greater than 2.
        Exception
            Raised if cutoff frequency is not provided when the filter type is not
            bandpass.

        Returns
        -------
        None.

        """

        if order % 2 != 0:
            raise ValueError("The filter order must be an even integer.")

        # Check and format filter type string
        filter_type = filter_type.lower()
        if filter_type == "low" or filter_type == "high":
            filter_type = filter_type + "pass"

        filter_types_allowed = self._get_filter_types_allowed()
        if filter_type not in filter_types_allowed:
            raise ValueError(
                "The filter type must be one of the following: "
                f"{filter_types_allowed}"
            )

        # Default cutoff frequencies - only for bandpass filter
        if cutoff_freq is None:
            if filter_type == "bandpass":
                cutoff_freq = [500, 2000]
            else:
                raise Exception(
                    "Cutoff frequencies cutoff_freq must be specified if "
                    "filter_type is not bandpass"
                )

        # Split cutoff frequencies so easier to set in GUI
        if isinstance(cutoff_freq, list):
            # Always store as float to facilitate tests with GUI
            # (easier to check consistency)
            cutoff_freq = [float(i) for i in cutoff_freq]

            # First cutoff frequency
            cutoff1 = cutoff_freq[0]

            # Check for second cutoff frequency
            if len(cutoff_freq) == 2:
                cutoff2 = cutoff_freq[1]
            elif len(cutoff_freq) > 2:
                raise ValueError(
                    "cutoff_freq must be length 1 (for lowpass or highpass filter) or 2"
                    " (for bandpass filter)"
                )
                # Note: Filter function handles checks for filter type and number of
                # cutoff (critical) frequencies
            else:
                cutoff2 = None

        elif isinstance(cutoff_freq, int | float):
            # Only one cutoff frequency; store as float
            cutoff1 = float(cutoff_freq)
            cutoff2 = None
        else:
            raise ValueError("cutoff_freq must be a list or float")

        # Save filter settings
        self.butterworth_filter = apply_filter
        self.butterworth_filter_settings = {
            "cutoff1": cutoff1,
            "cutoff2": cutoff2,
            "order": order,
            "filter_type": filter_type,
        }

    def get_butterworth_filter_cutoff(self) -> float | list[float]:
        """
        Extracts the cutoff frequency or frequencies as a single variable (in format
        suitable to be passed to a filtering function).

        Returns
        -------
        float | list[float]
            Cutoff frequency or frequencies; float if only one frequency, and
            list otherwise.

        """

        # Range if two frequencies specified
        if self.butterworth_filter_settings["cutoff2"] is not None:
            cutoff_freq = [
                self.butterworth_filter_settings["cutoff1"],
                self.butterworth_filter_settings["cutoff2"],
            ]
        else:
            cutoff_freq = self.butterworth_filter_settings["cutoff1"]

        return cutoff_freq

    def remove_butterworth_filter(self):
        """
        Sets "butterworth_filter" to False (filter will not be applied) and removes
        corresponding parameters (in butterworth_filter_settings dictionary) from the
        preprocessing settings.

        Returns
        -------
        None.

        """
        self.butterworth_filter = False
        self.butterworth_filter_settings = {}

    def add_remove_mains(self, freq_remove: int = 50, n_win_avg: int = 51):
        """
        Add settings for removing mains noise. Settings will be passed to EMGDataRaw
        method _remove_mains via the preprocess method.

        Parameters
        ----------
        freq_remove : int, optional
            The frequency to remove in hertz. The default is 50.
        n_win_avg : int, optional
            The number of windows to average to compute the mains noise signal.
            The default is 51.

        Raises
        ------
        ValueError
            Raised if n_win_avg is not odd.

        Returns
        -------
        None.

        """

        # Check that number of windows used to average noise is odd.
        if n_win_avg % 2 == 0:
            raise ValueError(
                "The number of windows used to estimate the noise signal, n_win_avg, "
                "must be odd."
            )

        # Save settings
        self.remove_mains = True
        self.remove_mains_settings = {
            "freq_remove": freq_remove,
            "n_win_avg": n_win_avg,
        }

    def remove_remove_mains(self):
        """
        Sets "remove mains" to False (mains noise will not be removed) and removes
        corresponding parameters (in remove_mains_settings dictionary) from the
        preprocessing settings.

        Returns
        -------
        None.

        """
        self.remove_mains = False
        self.remove_mains_settings = {}

    def print_settings(self):
        print(json.dumps(vars(self), indent=4))
        print("\n")
