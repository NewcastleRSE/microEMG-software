"""
Models for settings for EMG data analysis.

Note: does not use Qt classes for model/view framework. Purpose is to provide an
interface to pymicroemg data classes for settings:
    - EMGPreprocSettings
"""

from pymicroemg.emg_preproc_settings import EMGPreprocSettings


class EMGPreprocSettingsModel:
    def __init__(self, settings: EMGPreprocSettings):
        self.settings = settings

    def mains_checkbox_toggled(self, checked):
        # Slot for mains removal checkbox

        # Uses add_remove_mains and remove_remove_mains method so associated parameters
        # are also updated.
        # The associated parameters are fixed for the GUI, so do not need to be
        # separately modified; add_remove_mains method sets the default parameters.
        if checked:
            self.settings.add_remove_mains()
        else:
            self.settings.remove_remove_mains()

    def filter_checkbox_toggled(self, checked: bool):
        # Slot for filter checkbox

        self.settings.butterworth_filter = checked

    def filter_type_text_changed(self, filter_type: str):
        # Slot for filter type combobox

        # Set filter type
        self.settings.butterworth_filter_settings["filter_type"] = filter_type

        # Change cutoff2 frequency to None if filter type only requires one frequency
        filter_n_freq = self.settings._get_n_freq_per_filter_type()
        if filter_n_freq[filter_type] == 1:
            self.settings.butterworth_filter_settings["cutoff2"] = None

    def filter_order_changed(self, order: int):
        # Slot for filter order spinbox

        self.settings.butterworth_filter_settings["order"] = order

    def filter_cutoff_changed(self, cutoff_freq, cutoff_type):
        # Slot for filter cutoff line edit, first cutoff

        self.settings.butterworth_filter_settings[cutoff_type] = cutoff_freq
