#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widgets for selecting and loading analysis settings in load step.
"""
from typing import Any

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Signal

from pymicroemg.emg_preproc_settings import EMGPreprocSettings
from pymicroemg.emg_reconstruct_settings import (
    EMGAnalysisMotorUnitSettings,
    EMGAnalysisReconstructSettings,
    EMGAnalysisMotorUnitClusterSettings,
    EMGAnalysisMotorUnitJitterSettings,
)

from microemggui.models.settings import EMGSettingsModel

from microemggui.widgets.base import (
    InputInlineLabel,
    InputComboBox,
    SubsectionTitle,
    ExpandingHSpacer,
    InputInlineText,
)


# --- Widgets for selecting and loading analysis settings ---


class LoadSettingsWidget(QWidget):
    # Labelled dropdown box for choosing settings for analysis
    # Currently only implemented preprocessing settings

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets: dict[str, Any] = {
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

    # Signal for whether settings have been loaded
    settings_loaded = Signal(bool)

    # Signal for sending updated settings
    settings_changed = Signal(EMGSettingsModel)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialise attribute for storing settings
        self.settings_model = None

        # Create widgets
        self.widgets: dict[str, Any] = {
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
                    # All settings depend on defaults in pymicroemg module

                    # Preprocessing settings
                    preprocess_settings = EMGPreprocSettings()
                    preprocess_settings.add_butterworth_filter()
                    preprocess_settings.add_remove_mains()

                    # Motor unit settings
                    mu_settings = EMGAnalysisMotorUnitSettings()

                    # Fibre reconstruction settings
                    recon_settings = EMGAnalysisReconstructSettings()

                    # Clustering
                    mu_cluster_settings = EMGAnalysisMotorUnitClusterSettings()

                    # Jitter
                    mu_jitter_settings = EMGAnalysisMotorUnitJitterSettings()

            self.settings_model = EMGSettingsModel(
                preprocess_settings=preprocess_settings,
                mu_settings=mu_settings,
                recon_settings=recon_settings,
                mu_cluster_settings=mu_cluster_settings,
                mu_jitter_settings=mu_jitter_settings,
            )
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
