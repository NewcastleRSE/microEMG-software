#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for the preprocessing step in the EMG data analysis pipeline.
"""

from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QSizePolicy,
)
from PySide6.QtCore import Qt

from microemggui.widgets.preproc.preproc_settings import PreprocSettingsWidget
from microemggui.widgets.emg_viewer import EMGViewerWidget
from microemggui.models.emg import EMGDataModel
from microemggui.models.settings import EMGPreprocSettingsModel
from microemggui.widgets.base import SectionTitle, LargePushButton

# --- Component widgets ---


class ApplyPreprocButton(LargePushButton):
    # Button for applying preprocessing settings to EMG data

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Apply")
        self.setToolTip("Apply preprocessing settings")


class NextButton(LargePushButton):
    # Button for proceeding to the next step
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Next")
        self.setToolTip("Proceed to next step")


class MainButtons(QWidget):
    # Buttons for applying analysis step and continuing the analysis

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets = {"apply": ApplyPreprocButton(self), "next": NextButton(self)}

        # Add to layout
        layout = QHBoxLayout()
        layout.addWidget(self.widgets["apply"], alignment=Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.widgets["next"], alignment=Qt.AlignRight | Qt.AlignTop)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)


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
        emg_clrs: list[str],
        parent=None,
    ):
        super().__init__(parent)

        self.raw_emg_data_model = raw_emg_data_model
        self.settings_model = settings_model

        # Create widgets
        self.widgets = {
            "title": SectionTitle("Preprocessing", self),
            "settings": PreprocSettingsWidget(self.settings_model, parent=self),
            "viewer": EMGViewerWidget(
                self.raw_emg_data_model, emg_clrs=emg_clrs, parent=self
            ),
            "buttons": MainButtons(self),
        }

        # Set viewer to expand to fill extra space
        self.widgets["viewer"].setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )

        # Add to layout
        layout = QGridLayout()
        layout.addWidget(self.widgets["title"], 0, 0)
        layout.addWidget(self.widgets["settings"], 1, 0)
        layout.addWidget(self.widgets["buttons"], 2, 0)
        layout.addWidget(self.widgets["viewer"], 0, 1, 3, 1)
        self.setLayout(layout)
