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
        # Initialise preprocessing settings
        # Default is no preprocessing settings applied
        # TODO: documentation (once other preprocessing settings are added to initialisation)

        # Remove mains noise
        self.remove_mains = False
        self.remove_mains_settings = {}

        # Butterworth filter
        self.butterworth_filter = False
        self.butterworth_filter_settings = {}

    def add_filter(
        self,
        cutoff_freq: None | list[float] | float = None,
        order: int = 6,
        filter_type: str = "bandpass",
    ):
        # Add filter settings
        # TODO: amend/finish documentation

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
        # Add settings for removing mains noise
        # TODO: documentation

        # Save settings
        self.remove_mains = True
        self.remove_mains_settings = {
            "freq_remove": freq_remove,
            "n_win_avg": n_win_avg,
        }
