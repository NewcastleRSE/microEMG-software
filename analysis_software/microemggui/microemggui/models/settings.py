"""
Models for settings for EMG data analysis.

Note: does not use Qt classes for model/view framework. Purpose is to provide an
interface to pymicroemg data classes for settings:
    - EMGPreprocSettings
"""

import json

from pymicroemg.emg_preproc_settings import EMGPreprocSettings


class EMGPreprocSettingsModel:
    # TODO: remove print statements or change to logging output

    def __init__(self, settings: EMGPreprocSettings):
        self.settings = settings

    def mains_checkbox_toggled(self, checked):
        # Slot for mains removal checkbox

        print(f"MAINS REMOVAL: Is checkbox checked? : {checked}")

        # Uses add_remove_mains and remove_remove_mains method so associated parameters
        # are also updated.
        # The associated parameters are fixed for the GUI, so do not need to be
        # separately modified; add_remove_mains method sets the default parameters.
        if checked:
            self.settings.add_remove_mains()
        else:
            self.settings.remove_remove_mains()

        print(f"updated mains setting: {self.settings.remove_mains}")

    def filter_checkbox_toggled(self, checked):
        # Slot for filter checkbox

        print(f"FILTER: Is checkbox checked? : {checked}")
        self.settings.butterworth_filter = checked
        print(f"updated filter setting: {self.settings.butterworth_filter}")

    def print_settings(self):
        # Print settings - currently used to verify data updates
        print(json.dumps(vars(self.settings), indent=4))
        print("\n")
