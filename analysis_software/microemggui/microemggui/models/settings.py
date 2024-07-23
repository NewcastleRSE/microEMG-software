"""
Models for settings for EMG data analysis.

Note: does not use Qt classes for model/view framework. Purpose is to provide an
interface to pymicroemg data classes for settings:
    - EMGPreprocSettings
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pymicroemg.emg_preproc_settings import EMGPreprocSettings


class EMGSettingsModel:
    # Model for all EMG settings. Each settings object is stored as a separate
    # attribute. Note that the pymicroemg settings class (not the microemggui model
    # classes) are used for each attribute - the corresponding models will be created
    # by the GUI as needed.
    # TODO: consider passing in object that contains all settings instead of individual
    # groups of settings.

    def __init__(self, preprocess_settings: EMGPreprocSettings):
        self.preprocess_settings = preprocess_settings

    def get_formatted_settings_text(self) -> str:
        # Formatted settings text with breaks and bold section headers, for display in
        # GUI

        # Preprocessing
        remove_mains_str = f"Remove mains: {self.preprocess_settings.remove_mains}"
        filter_str = f"Filter: {self.preprocess_settings.butterworth_filter}"
        if self.preprocess_settings.butterworth_filter:
            filter_type = self.preprocess_settings.butterworth_filter_settings["filter_type"]
            order = self.preprocess_settings.butterworth_filter_settings["order"]
            cutoff1 = self.preprocess_settings.butterworth_filter_settings["cutoff1"]
            if filter_type == "bandpass":
                cutoff2 = self.preprocess_settings.butterworth_filter_settings["cutoff2"]
                cutoff_str = f"cutoff frequencies: {cutoff1} to {cutoff2} Hz"
            else:
                cutoff_str = f"cutoff frequency: {cutoff1} Hz"
            filter_str = (
                filter_str + f" ({filter_type} Butterworth filter, {cutoff_str}, order: {order})"
            )

        preprocess_str = f"<b>Preprocessing settings</b><br>{remove_mains_str}<br>{filter_str}"

        # TODO: add remaining settings
        settings_text = preprocess_str
        return settings_text


class EMGPreprocSettingsModel:
    # Model for the EMG preprocessing settings

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

    def filter_cutoff_changed(self, cutoff_freq, cutoff, is_valid_input):
        # Slot for filter cutoff line edit
        # Value only changed if input is valid

        if is_valid_input:
            self.settings.butterworth_filter_settings[cutoff] = float(cutoff_freq)
