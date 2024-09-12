#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for loading recording and analysis settings, then starting the analysis.
"""
from typing import Any

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal

from microemggui.models.emg import EMGDataRawModel
from microemggui.models.settings import EMGSettingsModel

from microemggui.widgets.base import (
    SectionTitle,
    ExpandingVSpacer,
)

from microemggui.widgets.load.load_recording import LoadRecordingSection
from microemggui.widgets.load.trim_recording import TrimRecordingSection
from microemggui.widgets.load.load_settings import LoadSettingsSection
from microemggui.widgets.load.run_analysis import RunAnalysisSection


# --- Widgets with all initial steps ---


class LoadWidget(QWidget):
    """
    Full widget for all load steps (loading recording, loading settings, running
    analysis).
    """

    # Signal for whether all loading steps are finished
    load_finished = Signal(bool)

    # Signal for sending data from load step to main window
    load_data_changed = Signal(EMGDataRawModel, EMGSettingsModel)

    def __init__(self, emg_clrs: list[str], parent=None):
        super().__init__(parent)

        # Attributes for storing EMG recording and settings
        self.emg_model = None
        self.settings_model = None

        # Colors for EMG viewer
        self.emg_clrs = emg_clrs

        # Create widgets
        self.title = SectionTitle("Load microEMG recording", self)

        self.widgets: dict[str, Any] = {
            "recording": LoadRecordingSection(parent=self),
            "trim": QWidget(self),  # placeholder - need EMG to create
            "settings": LoadSettingsSection(parent=self),
            "run": RunAnalysisSection(parent=self),
        }

        # Add to section widgets layout
        # Separate layout for sections so easier to control spacing
        self.sections_layout = QVBoxLayout()
        for _, w in self.widgets.items():
            self.sections_layout.addWidget(w)
        self.sections_layout.addItem(ExpandingVSpacer())
        self.sections_layout.setSpacing(30)
        self.sections_layout.setContentsMargins(0, 0, 0, 0)

        sections_widget = QWidget(parent=self)
        sections_widget.setLayout(self.sections_layout)

        # Full layout
        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(sections_widget)
        layout.addItem(ExpandingVSpacer())
        layout.setContentsMargins(20, 5, 20, 20)
        self.setLayout(layout)

        # Connections
        # Note connection for trim widget is set up in method that updates the trim widget
        self.widgets["recording"].recording_loaded.connect(self.updates_after_loading_emg)
        self.widgets["recording"].recording_changed.connect(self.update_emg_model)
        self.widgets["settings"].settings_loaded.connect(self.updates_after_loading_settings)
        self.widgets["settings"].settings_changed.connect(self.update_settings_model)

        # Send signal that recording has not yet been loaded to set correct states
        self.widgets["recording"].recording_loaded.emit(False)

    def updates_after_loading_emg(self, recording_loaded: bool):
        """
        Show/hide steps after loading depend on if data has been loaded.
        Remove emg_model saved if recording not loaded.
        Slot for recording_loaded signal.
        """

        if recording_loaded:
            # Update trim widget - first delete existing, then make new widget with
            # updated EMG
            self.sections_layout.removeWidget(self.widgets["trim"])  # remove from layout
            self.widgets["trim"].deleteLater()  # delete
            self.widgets["trim"] = TrimRecordingSection(self.emg_model, self.emg_clrs, parent=self)
            self.sections_layout.insertWidget(1, self.widgets["trim"])  # add to layout
            self.widgets["trim"].show()  # show

            self.widgets["trim"].recording_trimmed.connect(self.updates_after_recording_trimmed)

            # Ensure other widgets are hidden (may be shown by previous load) and set
            # to default state
            self.widgets["settings"].widgets["load"].widgets["combobox"].setCurrentIndex(0)
            self.widgets["settings"].hide()
            self.widgets["run"].hide()

        else:
            self.widgets["trim"].hide()
            self.widgets["settings"].hide()
            self.widgets["run"].hide()

            # Remove any previously saved EMG data and settings
            self.emg_model = None
            self.settings_model = None

            # Remove any previously selected settings in combobox
            self.widgets["settings"].widgets["load"].widgets["combobox"].setCurrentIndex(0)

            # Signal to prevent next analysis steps
            self.load_finished.emit(False)

    def updates_after_recording_trimmed(self):
        """
        Updates after trimming EMG (--> show settings selection section).
        Slot for recording_trimmed signal.
        """

        # Show settings
        self.widgets["settings"].show()

    def updates_after_loading_settings(self, settings_loaded: bool):
        """
        Show/hide steps after loading depending on if data has been loaded.
        Slot for settings_loaded signal.
        """

        if settings_loaded:
            self.widgets["run"].show()

            # Since this is the last load step, send data to main window and allow
            # next steps
            self.load_data_changed.emit(self.emg_model, self.settings_model)
            self.load_finished.emit(True)

        else:
            self.widgets["run"].hide()

            # Remove any previously saved EMG data and settings
            self.settings_model = None

            # Prevent next analysis steps
            self.load_finished.emit(False)

    def update_emg_model(self, emg_model: EMGDataRawModel):
        """
        Update EMG data model (raw data).
        Slot for recording_changed signal.
        """

        self.emg_model = emg_model

    def update_settings_model(self, settings_model: EMGSettingsModel):
        """
        Update EMG settings model.
        Slot for settings_changed signal.
        """

        self.settings_model = settings_model
