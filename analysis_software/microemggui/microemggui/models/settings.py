"""
Models for settings for EMG data analysis.

Note: does not use Qt classes for model/view framework. Purpose is to provide an
interface to pymicroemg data classes for settings:
    - EMGPreprocSettings
    - EMGAnalysisMotorUnitSettings

EMGSettingsModel also stores all settings as attributes (without the interface for each
settings - the interface is created as needed to interact with the settings)
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pymicroemg.emg_preproc_settings import EMGPreprocSettings
    from pymicroemg.emg_reconstruct_settings import EMGAnalysisMotorUnitSettings


class EMGSettingsModel:
    # Model for all EMG settings. Each settings object is stored as a separate
    # attribute. Note that the pymicroemg settings class (not the microemggui model
    # classes) are used for each attribute - the corresponding models will be created
    # by the GUI as needed.
    # TODO: consider passing in object that contains all settings instead of individual
    # groups of settings.

    def __init__(
        self, preprocess_settings: EMGPreprocSettings, mu_settings: EMGAnalysisMotorUnitSettings
    ):
        self.preprocess_settings = preprocess_settings
        self.mu_settings = mu_settings

    def get_formatted_settings_text(self) -> str:
        # Formatted settings text with breaks and bold section headers, for display in
        # GUI

        preprocess_str = self.get_formatted_preprocess_settings_text()
        mu_str = self.get_formatted_mu_settings_text()

        # TODO: add remaining settings
        settings_text = f"{preprocess_str}<br><br>{mu_str}"
        return settings_text

    def get_formatted_preprocess_settings_text(self) -> str:
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

        return preprocess_str

    def get_formatted_mu_settings_text(self) -> str:
        # Motor unit identification
        # TODO: add text aliases; create model to access value/text conversion methods
        sensitivity_str = f"Detection sensitivity: {self.mu_settings.tk_filt_thres_spike}"
        similarity_str = f"Motor unit similarity: {self.mu_settings.tk_filt_thres_PsC}"
        mu_str = (
            f"<b>Settings for finding motor units</b><br>{sensitivity_str}<br>{similarity_str}"
        )

        return mu_str


# --- Preprocessing ---


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


# --- Motor unit identification settings ---


class EMGAnalysisMotorUnitSettingsModel:
    """
    Model for the motor unit identification settings.

    Includes slot for changing detection sensitivity (tk_filt_thres_spike) and motor
    unit similarity (tk_filt_thres_PsC).

    Also specifies valid settings text options for the GUI and the mapping to float
    values.
    """

    def __init__(self, settings: EMGAnalysisMotorUnitSettings):
        self.settings = settings

        # GUI options for settings values with mapping of text (e.g., "low") to value
        # and vice versa
        # TODO: review options
        sensitivity_text2values = {"low": 0.05, "medium (default)": 0.1, "high": 0.15}
        sensitivity_values2text = {v: k for k, v in sensitivity_text2values.items()}

        similarity_text2values = {"low": 0.05, "medium (default)": 0.1, "high": 0.15}
        similarity_values2text = {v: k for k, v in similarity_text2values.items()}

        # Store mapping by GUI setting name so easier to request each setting's mapping
        # Also include attribute name ("alias") for each setting
        self.mapping: dict[str, dict[str, Any]] = {
            "sensitivity": {
                "alias": "tk_filt_thres_spike",
                "text2values": sensitivity_text2values,
                "values2text": sensitivity_values2text,
            },
            "similarity": {
                "alias": "tk_filt_thres_PsC",
                "text2values": similarity_text2values,
                "values2text": similarity_values2text,
            },
        }

        # Check that current settings are valid GUI options
        settings_names = ["sensitivity", "similarity"]
        for name in settings_names:
            value = self.get_setting_current_value(name)
            text = self.map_values2text(name, value)
            alias = self.mapping[name]["alias"]
            if not text:
                raise ValueError(f"Value for {name} ({alias}) is not a valid GUI option")

    def map_text2values(self, setting: str, text: str) -> float:
        """
        Get setting value that corresponds to GUI text.
        """

        value = self.mapping[setting]["text2values"].get(text)
        if not value:
            raise ValueError(f"{text} is not a GUI option for {setting}")
        return value

    def map_values2text(self, setting: str, value: float) -> str:
        """
        Get text that corresponds to settings value.
        """

        text = self.mapping[setting]["values2text"].get(value)
        if not text:
            raise ValueError(f"{value} does not have a corresponding GUI option for {setting}")
        return text

    def get_setting_current_value(self, setting: str) -> float:
        """
        Get the current value for
        - detection sensitivity ("sensitivity") (stored as tk_filt_thres_spike)
        - motor unit similarity ("similarity") (stored as tk_filt_thres_PsC)

        """

        value = getattr(self.settings, self.mapping[setting]["alias"])
        if not value:
            raise ValueError("Setting is not part of motor unit settings GUI options.")

        return value

    def get_setting_current_text(self, setting: str) -> str:
        """
        Get the text that corresponds to a setting's current value.
        """

        value = getattr(self.settings, self.mapping[setting]["alias"])
        if not value:
            raise ValueError("Setting is not part of motor unit settings GUI options.")
        text = self.map_values2text(setting, value)

        return text

    def change_setting(self, setting: str, combobox_text: str):
        """
        Slot for detection sensitivity and motor unit similarity comboboxes.
        "sensitivity" is the term the GUI uses for tk_filt_thres_spike.
        "similarity" is the term the GUI uses for tk_filt_thres_PsC.
        Use mapping to convert the combobox text to the setting's corresponding value.
        """

        value = self.map_text2values(setting, combobox_text)
        setattr(self.settings, self.mapping[setting]["alias"], value)
        print(f"{setting} changed:")
        print(self.get_setting_current_text(setting))
        print(self.get_setting_current_value(setting))
