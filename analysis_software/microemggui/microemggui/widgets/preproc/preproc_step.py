#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for the preprocessing step in the EMG data analysis pipeline.
"""

from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal

from microemggui.widgets.preproc.preproc_settings import PreprocSettingsWidget
from microemggui.widgets.emg_viewer import EMGViewerWidget
from microemggui.models.emg import EMGDataRawModel, EMGDataPreprocModel
from microemggui.models.settings import EMGPreprocSettingsModel
from microemggui.widgets.base import (
    SectionTitle,
    LargePushButton,
    TabButton,
    ExpandingHSpacer,
)

# --- Component widgets ---


class ApplyPreprocButton(LargePushButton):
    # Button for applying preprocessing settings to EMG data

    # Signal to emit when "apply" button is clicked
    apply_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Apply")
        self.setToolTip("Apply preprocessing settings")

        # Connections
        self.clicked.connect(self.button_clicked)

    def button_clicked(self):
        # Send signal to preprocess data
        self.apply_clicked.emit()

        # Update text and disable (will only change if settings updated)
        self.setText("Re-apply")
        self.setEnabled(False)

    def change_enabled(self, freq_values_valid):
        # Enable/disable button based on whether filter frequency values are valid

        self.setEnabled(freq_values_valid)


class NextButton(LargePushButton):
    # Button for proceeding to the next step

    # TODO: Signal when "next" button is clicked

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
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class EMGViewerTabbedWidget(QWidget):
    # EMG viewer with "tabs" for switching between raw and preprocessed time series.
    # Initialised without preprocessed data; added later via a method.
    # The tab functionality is mimicked by swapping the data in the EMG viewer - the
    # EMG viewer widget remains the same.

    # TODO: change color/style of tab based on whether it is active

    def __init__(
        self,
        raw_emg_model: EMGDataRawModel,
        emg_clrs: list[str],
        parent=None,
    ):
        super().__init__(parent)

        self.emg_model = {"raw": raw_emg_model}

        self.emg_clrs = emg_clrs

        # Tab widgets
        self.widgets_tabs = {
            "raw": TabButton("Raw EMG", parent=self),
            "preproc": TabButton("Preprocessed EMG", parent=self),
        }
        layout_tabs = QHBoxLayout()
        for _, w in self.widgets_tabs.items():
            layout_tabs.addWidget(w, alignment=Qt.AlignLeft)
        layout_tabs.addItem(ExpandingHSpacer())  # Spacer to push tabs to left
        layout_tabs.setContentsMargins(0, 0, 0, 0)

        # All widgets - start viewer with raw EMG data
        self.widgets = {
            "tabs": QWidget(parent=self),
            "viewer": EMGViewerWidget(self.emg_model["raw"], self.emg_clrs),
        }
        self.widgets["tabs"].setLayout(layout_tabs)  # add tabs to tabs widget

        layout = QVBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        self.setLayout(layout)

        self.widgets_tabs["preproc"].hide()  # Hide preproc tab until preprocessing
        self.widgets_tabs["raw"].setEnabled(False)  # Disable raw EMG tab

        # Connections
        self.connect_tabs_to_data()

    def add_preproc_emg_model(self, preproc_emg_model: EMGDataPreprocModel):
        # Add preprocessed EMG data model and set to data in viewer

        self.emg_model["preproc"] = preproc_emg_model
        self.widgets_tabs["preproc"].show()
        self.switch_emg_model("preproc")

    def connect_tabs_to_data(self):
        # Set up connections between tabs and the data in the viewer
        # TODO: try to change to clicked signal

        for k, w in self.widgets_tabs.items():
            w.pressed.connect(lambda data=k: self.switch_emg_model(data))

    def switch_emg_model(self, data: str):
        # Switch EMG data in viewer (slot for tab clicks)
        # Also changes appearance of tab buttons by enabling/disabling them

        self.widgets["viewer"].widgets["plot"].replace_emg_model(self.emg_model[data])
        for k, w in self.widgets_tabs.items():
            # Disable if key matches EMG model key; otherwise, enable
            w.setEnabled(k != data)


# --- Preprocessing widget ----


class PreprocWidget(QWidget):
    # Widget for preprocessing step

    def __init__(
        self,
        raw_emg_model: EMGDataRawModel,
        settings_model: EMGPreprocSettingsModel,
        emg_clrs: list[str],
        parent=None,
    ):
        super().__init__(parent)

        self.emg_model = {"raw": raw_emg_model}
        self.settings_model = settings_model
        self.emg_clrs = emg_clrs

        # Create widgets
        self.widgets = {
            "title": SectionTitle("Preprocessing", self),
            "settings": PreprocSettingsWidget(self.settings_model, parent=self),
            "tabbedviewer": EMGViewerTabbedWidget(
                self.emg_model["raw"], self.emg_clrs, parent=self
            ),
            "buttons": MainButtons(self),
        }

        # Set viewer to expand to fill extra space
        self.widgets["tabbedviewer"].setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )

        # Add to layout
        layout = QGridLayout()
        layout.addWidget(self.widgets["title"], 0, 0)
        layout.addWidget(self.widgets["settings"], 1, 0)
        layout.addWidget(self.widgets["buttons"], 2, 0)
        layout.addWidget(self.widgets["tabbedviewer"], 0, 1, 3, 1)
        self.layout = layout
        self.setLayout(self.layout)

        # Connections
        self.widgets["buttons"].widgets["apply"].apply_clicked.connect(
            self.apply_preproc
        )
        freq_w = self.widgets["settings"].widgets["filter_spec"].widgets["filter_freq"]
        freq_w.validity_checked.connect(
            self.widgets["buttons"].widgets["apply"].change_enabled
        )

    def apply_preproc(self):
        # Apply preprocessing settings to raw data to generate preprocessed data.
        # Add preprocessed data to viewer.
        # Will overwrite any previously computed preprocessed data.
        # TODO: also send preprocessed data to main window for downstream steps
        # TODO: pop up while preprocessing is happening

        self.emg_model["preproc"] = self.emg_model["raw"].apply_preproc(
            self.settings_model.settings
        )
        self.widgets["tabbedviewer"].add_preproc_emg_model(self.emg_model["preproc"])
