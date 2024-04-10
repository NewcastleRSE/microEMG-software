#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for the preprocessing step in the EMG data analysis pipeline.
"""

from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QSizePolicy,
)

from microemggui.widgets.preproc.preproc_settings import PreprocSettingsWidget
from microemggui.widgets.emg_viewer import EMGViewerWidget
from microemggui.models.emg import EMGDataModel
from microemggui.models.settings import EMGPreprocSettingsModel
from microemggui.widgets.base import SectionTitle

# --- Component widgets ---


# Button for applying settings

# Buttons for applying step and proceeding


class EMGViewerMultiWidget(QWidget):
    # EMG viewer with tabs for switching between raw and preprocessed time series

    def __init__(
        self,
        raw_emg_data_model: EMGDataModel,
        preproc_emg_data_model: EMGDataModel,
        parent=None,
    ):
        super().__init__(parent)


# --- Preprocessing widget ----


class PreprocWidget(QWidget):
    # Widget for preprocessing step

    def __init__(
        self,
        raw_emg_data_model: EMGDataModel,
        settings_model: EMGPreprocSettingsModel,
        parent=None,
    ):
        super().__init__(parent)

        self.raw_emg_data_model = raw_emg_data_model
        self.settings_model = settings_model

        # Create widgets
        self.widgets = {
            "title": SectionTitle("Preprocessing", self),
            "settings": PreprocSettingsWidget(self.settings_model, parent=self),
            "viewer": EMGViewerWidget(self.raw_emg_data_model),
        }

        # Set viewer to expand to fill extra space
        self.widgets["viewer"].setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )

        # Add to layout
        layout = QGridLayout()
        layout.addWidget(self.widgets["title"], 0, 0)
        layout.addWidget(self.widgets["settings"], 1, 0)
        layout.addWidget(self.widgets["viewer"], 0, 1, 2, 1)
        self.setLayout(layout)
