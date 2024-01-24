#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A Class, EMGPreprocSettings, for configuring and storing EMG preprocessing
settings (applied to EMGData)

"""


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

    def add_butterworth_filter(
        self,
        cutoff_freq: None | list[float] | float = None,
        order: int = 6,
        filter_type: str = "bandpass",
    ):
        """
        Add filter settings for a zero-phase Butterworth filter. See scipy.signal.butter
        for parameter details.

        Parameters
        ----------
        cutoff_freq : None | list[float] | float, optional
            Cutoff frequency or frequencies to pass to scipy.signal.butter. The default
            is [500, 2000] if the filter type is "bandpass". The cutoff frequency must
            be specified for other filter types.
        order : int, optional
            Filter order; must be even. The default is 6.
        filter_type : str, optional
            Type of filter - see scipy.signal.butter for options. The default is
            "bandpass".

        Raises
        ------
        ValueError
            Raised if filter order is not even.
        Exception
            Raised if cutoff frequency is not provided when the filter type is not
            bandpass.

        Returns
        -------
        None.

        """

        if order % 2 != 0:
            raise ValueError("The filter order must be an even integer.")

        # Default cutoff frequencies - only for bandpass filter
        if cutoff_freq is None:
            if filter_type == "bandpass":
                cutoff_freq = [500, 2000]
            else:
                raise Exception(
                    "Cutoff frequencies cutoff_freq must be specified if "
                    "filter_type is not bandpass"
                )

        # Save filter settings
        self.butterworth_filter = True
        self.butterworth_filter_settings = {
            "cutoff_freq": cutoff_freq,
            "order": order,
            "filter_type": filter_type,
        }

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
