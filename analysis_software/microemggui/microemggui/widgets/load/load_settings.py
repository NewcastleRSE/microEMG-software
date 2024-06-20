#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widgets for selecting and loading analysis settings in load step.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Signal

from pymicroemg.emg_preproc_settings import EMGPreprocSettings

from microemggui.models.settings import EMGSettingsModel

from microemggui.widgets.base import (
    InputInlineText,
    InputInlineLabel,
    InputComboBox,
    SubsectionTitle,
    ExpandingHSpacer,
)


# --- Widgets for selecting and loading analysis settings ---


class LoadSettingsWidget(QWidget):
    # Labelled dropdown box for choosing settings for analysis
    # Currently only implemented preprocessing settings
    # TODO: change to overall settings, not just preprocessing
    # TODO: pull setting options from config file instead of defining here
    # TODO: add saved settings? need to figure out how to load

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets = {
            "label": InputInlineLabel("Settings: ", parent=self),
            "combobox": InputComboBox(parent=self),
        }

        # List of settings options
        self.settings_options = ["", "Default"]
        self.widgets["combobox"].addItems(self.settings_options)

        # Add to layout
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.addItem(ExpandingHSpacer())
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class LoadSettingsSection(QWidget):
    # Widget for selecting analysis settings
    # TODO: consider adding option to add new settings

    # Signal for whether settings have been loaded
    settings_loaded = Signal(bool)

    # Signal for sending updated settings
    settings_changed = Signal(EMGSettingsModel)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialise attribute for storing settings
        self.settings_model = None

        # Create widgets
        self.widgets = {
            "title": SubsectionTitle("Choose initial analysis settings", self),
            "load": LoadSettingsWidget(parent=self),
            "settingstext": InputInlineText("", parent=self),
        }

        # Add to layout
        layout = QVBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Connections
        self.widgets["load"].widgets["combobox"].currentTextChanged.connect(self.load_settings)

    def load_settings(self, settings_name: str):
        # Add correct settings as attribute when settings combobox is changed
        # TODO: Update to get from config file and use all settings (not just preproc)

        if not settings_name:  # No settings selected
            self.settings_model = None
            self.settings_loaded.emit(False)
        else:  # Settings selected
            match settings_name:
                case "Default":
                    preprocess_settings = EMGPreprocSettings()
                    preprocess_settings.add_butterworth_filter(
                        cutoff_freq=[100, 2000], order=6, filter_type="bandpass"
                    )
                    preprocess_settings.add_remove_mains()

            # TODO: update to all settings
            self.settings_model = EMGSettingsModel(preprocess_settings=preprocess_settings)
            self.settings_changed.emit(self.settings_model)  # Must emit first
            self.settings_loaded.emit(True)

        self.display_settings()

    def display_settings(self):
        # Update settingstext widget to display summary of EMG settings that have been
        # selected

        if not self.settings_model:
            self.widgets["settingstext"].setText("")
        else:
            settings_text = self.settings_model.get_formatted_settings_text()
            self.widgets["settingstext"].setText(settings_text)
