#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for the preprocessing step in the EMG data analysis pipeline.
"""
from typing import Any
import logging

from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
    QProgressDialog,
    QTabBar,
)
from PySide6.QtCore import Qt, Signal

from pymicroemg.emg_data_raw import EMGDataRawLoggerAdapter

from microemggui.widgets.preproc.preproc_settings import PreprocSettingsWidget
from microemggui.widgets.emg_viewer import EMGViewerWidget
from microemggui.models.emg import EMGDataRawModel, EMGDataPreprocModel
from microemggui.models.settings import EMGPreprocSettingsModel
from microemggui.widgets.base import (
    SectionTitle,
    LargePushButton,
)
from microemggui.gui_logger import QtHandler

# --- Component widgets ---


class ApplyPreprocButton(LargePushButton):
    # Button for applying preprocessing settings to EMG data

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Apply")
        self.setToolTip("Apply preprocessing settings")

        # Connections
        self.clicked.connect(self.button_clicked)

        # Connections for preprocessing data are added in main preprocessing widget

    def button_clicked(self):
        # Update text and disable (will re-enable if settings updated)

        self.setText("Re-apply")
        self.setEnabled(False)

    def change_enabled(self, settings_valid: bool):
        # Slot for enable/disabling button based on whether settings are valid.
        # This approach is also used to re-enable the button if the preprocessing
        # settings are changed after the initial preprocessing.

        self.setEnabled(settings_valid)


class NextButton(LargePushButton):
    # Button for proceeding to the next step

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Next")
        self.setToolTip("Proceed to next step")

        self.hide()  # hide initially

    def show_button(self):
        # Slot for revealing and enabling next button after preprocessing
        self.show()
        self.setEnabled(True)


class MainButtons(QWidget):
    # Buttons for applying analysis step and continuing the analysis

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "apply": ApplyPreprocButton(self),
            "next": NextButton(self),
        }

        # Add to layout
        layout = QHBoxLayout()
        layout.addWidget(self.widgets["apply"], alignment=Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.widgets["next"], alignment=Qt.AlignRight | Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class EMGViewerTabbedWidget(QWidget):
    # EMG viewer with tabs for switching between raw and preprocessed time series.
    # Initialised without preprocessed data; added later via a method.
    # The tab functionality is mimicked by swapping the data in the EMG viewer - the
    # EMG viewer widget remains the same in all tabs.

    def __init__(
        self,
        raw_emg_model: EMGDataRawModel,
        emg_clrs: list[str],
        parent=None,
    ):
        super().__init__(parent)

        self.emg_model: dict[str, Any] = {"raw": raw_emg_model}

        self.emg_clrs = emg_clrs

        # Tabs
        self.tab_text = ["Raw EMG", "Preprocessed EMG"]  # text
        self.tab_data = ["raw", "preproc"]  # so can convert between tab indices and data

        # All widgets - start viewer with raw EMG data
        self.widgets: dict[str, Any] = {
            "tabs": QTabBar(parent=self),
            "viewer": EMGViewerWidget(self.emg_model["raw"], self.emg_clrs),
        }
        # Update colours with repeated version - makes easily accessible for text
        # colours in channel selection widget
        self.emg_clrs = self.widgets["viewer"].widgets["plot"].emg_clrs

        # Add tabs to tabs widget
        for txt in self.tab_text:
            self.widgets["tabs"].addTab(txt)

        # Tab properties
        self.widgets["tabs"].setExpanding(False)
        self.widgets["tabs"].setDrawBase(False)  # removes bar beneath tabs (difficult to style)

        # Layout
        layout = QVBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Set current tab to raw EMG tab and disable preproc EMG tab until preprocessing
        self.widgets["tabs"].setCurrentIndex(self.tab_data.index("raw"))
        self.widgets["tabs"].setTabEnabled(self.tab_data.index("preproc"), False)

        # Connect tab clicks to changing data
        self.widgets["tabs"].currentChanged.connect(self.switch_emg_model)

    def add_preproc_emg_model(self, preproc_emg_model: EMGDataPreprocModel):
        # Add preprocessed EMG data model and set to data in viewer

        data = "preproc"
        self.emg_model[data] = preproc_emg_model
        self.widgets["tabs"].setTabEnabled(self.tab_data.index(data), True)
        self.switch_emg_model(self.tab_data.index(data))

    def switch_emg_model(self, tab_idx: int):
        # Switch EMG data in viewer (slot for tab clicks)
        # Also changes adtive tab

        data = self.tab_data[tab_idx]
        self.widgets["viewer"].widgets["plot"].replace_emg_model(self.emg_model[data])
        self.widgets["tabs"].setCurrentIndex(tab_idx)  # change tab


# --- Preprocessing widget ----


class PreprocWidget(QWidget):
    # Widget for preprocessing step

    # Signal for sending data from preprocessing step to main window
    preproc_data_changed = Signal(EMGDataPreprocModel, EMGPreprocSettingsModel)

    def __init__(
        self,
        raw_emg_model: EMGDataRawModel,
        settings_model: EMGPreprocSettingsModel,
        emg_clrs: list[str],
        parent=None,
    ):
        super().__init__(parent)

        self.emg_model: dict[str, Any] = {"raw": raw_emg_model}
        self.settings_model = settings_model
        self.emg_clrs = emg_clrs

        # Create widgets
        self.widgets: dict[str, Any] = {
            "title": SectionTitle("Preprocessing", self),
            "settings": PreprocSettingsWidget(self.settings_model, parent=self),
            "tabbedviewer": EMGViewerTabbedWidget(
                self.emg_model["raw"], self.emg_clrs, parent=self
            ),
            "buttons": MainButtons(self),
        }

        # Set viewer to expand to fill extra space
        self.widgets["tabbedviewer"].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add to layout
        layout = QGridLayout()
        layout.addWidget(self.widgets["title"], 0, 0)
        layout.addWidget(self.widgets["settings"], 1, 0)
        layout.addWidget(self.widgets["buttons"], 2, 0)
        layout.addWidget(self.widgets["tabbedviewer"], 0, 1, 3, 1)
        layout.setContentsMargins(20, 5, 20, 20)
        self.setLayout(layout)

        # Connections

        # For applying preprocessing
        self.widgets["buttons"].widgets["apply"].clicked.connect(self.apply_preproc)

        # For showing and enabling next button
        self.widgets["buttons"].widgets["apply"].clicked.connect(
            self.widgets["buttons"].widgets["next"].show_button
        )

        # For enabling/disabling preprocessing based on settings validity
        self.widgets["settings"].settings_valid.connect(
            self.widgets["buttons"].widgets["apply"].change_enabled
        )

        # Disable next button if settings are changed
        self.widgets["settings"].settings_valid.connect(
            lambda settings_valid: self.widgets["buttons"].widgets["next"].setEnabled(False)
        )

        # Check if initial settings are valid
        self.widgets["settings"].settings_changed()

        # Set the focus of the EMG viewer so it is the default processer of arrow key presses
        self.widgets["tabbedviewer"].setFocus()
        self.setFocusPolicy(Qt.StrongFocus)  # results in focus returning to EMG viewer by default

    def apply_preproc(self):
        # Apply preprocessing settings to raw data to generate preprocessed data.
        # Add preprocessed data to viewer.
        # Will overwrite any previously computed preprocessed data.

        # Create handler for processing logger; create connections to log records
        self.handler = QtHandler(self.update_progress_bar_from_log)
        logging.getLogger("EMGDataRawLogger").addHandler(self.handler)

        # Create progress bar
        n_chan = self.emg_model["raw"].emg_data.n_chan
        self.progress = QProgressDialog("Preprocessing", None, 0, n_chan, parent=self)
        # Ensure that progress dialog closes if GUI window is minimised
        # GUI window will pop up when process finishes and the progress bar closes
        self.progress.setAttribute(Qt.WA_DeleteOnClose, True)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setMinimumDuration(0)

        # Preprocess; logs from analysis will be output to GUI using connection
        self.emg_model["preproc"] = self.emg_model["raw"].apply_preproc(
            self.settings_model.settings
        )

        # Set progress bar to max value to close dialog window
        self.progress.setValue(n_chan)
        self.progress.hide()  # Forces to bar to disappear regardless of value

        # Add preprocessed data to viewer
        self.widgets["tabbedviewer"].add_preproc_emg_model(self.emg_model["preproc"])

        # Emit signal with preprocessed data
        self.preproc_data_changed.emit(self.emg_model["preproc"], self.settings_model)

    def update_progress_bar_from_log(self, record: EMGDataRawLoggerAdapter):
        # Slot for logs from EMGDataRaw; used to update progress bar for preprocessing
        # steps.

        # If start of a new analysis step, change progress bar label and reset bar to 0
        if record.record_context.analysis_start:
            # Format text
            analysis_step = record.record_context.analysis_step
            analysis_step = analysis_step.replace("_", " ")
            analysis_step = analysis_step[:1].upper() + analysis_step[1:].lower()
            bar_label = f"{analysis_step}..."

            # Add text to progress bar
            self.progress.setLabelText(bar_label)

            # Set bar to zero
            self.progress.setValue(0)

        # Otherwise, use loop iterator to change progress bar
        # Note i will never reach the max value of the progress bar - this allows the
        # bar to be reset for different analysis steps
        elif record.record_context.loop_i:
            self.progress.setValue(record.record_context.loop_i)
