#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widgets for selecting and loading recording in load step.
"""
from typing import Any
import re
import logging

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFileDialog
from PySide6.QtCore import Signal

from pymicroemg.emg_files import EMGFiles
import pymicroemg.helper_config as emg_cfg

from microemggui.models.emg import EMGDataRawModel

from microemggui.widgets.base import (
    SmallPushButton,
    LargePushButton,
    InputInlineText,
    InputInlineLabel,
    InputWarningLabel,
    InputComboBox,
    SubsectionTitle,
    ExpandingHSpacer,
)

logger = logging.getLogger("microemggui.load")

# --- Widgets for selecting and loading a recording ---


class SelectRecordingWidget(QWidget):
    """
    Widget for selecting recording to load.
    """

    # Signals for when recording file path and label are changed
    recording_path_changed = Signal(str)
    recording_label_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "button": SmallPushButton(self),
            "label": InputInlineLabel("or select demo recording:"),
            "combobox": InputComboBox(parent=self),
        }

        # Button text
        self.widgets["button"].setText("Choose files")
        self.widgets["button"].setToolTip("Choose Intan recording files")

        # Demo options
        self.demo_names = ["", "Demo Recording 1 (healthy)"]
        self.demo_recording_num = [-1, 0]  # < 0 means it is not a recording
        self.widgets["combobox"].addItems(self.demo_names)

        # Add to layout
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.addItem(ExpandingHSpacer())  # spacer
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Connections
        self.widgets["combobox"].currentIndexChanged.connect(self.demo_recording_changed)
        self.widgets["button"].clicked.connect(self.browse_for_recording_file)

    def demo_recording_changed(self, idx: int):
        """
        Slot for when combobox option is changed; receives index of current selection.
        Uses index to determine demo recording number, then emits signal with
        recording file path and label.
        """

        recording_num = self.demo_recording_num[idx]

        if recording_num < 0:  # Signifies that no recording is selected
            recording_path = ""
        else:  # Otherwise, use recording number to retrieve path to recording
            recording_path, _ = emg_cfg.get_recording_path_and_id(recording_num)

        # Emit signals with new recording path and label
        # Label could also be passed to other widgets using combobox signal, but we use
        # recording_label_changed signal to be consistent with the
        # "browse_for_recording_file" approach.
        self.recording_path_changed.emit(recording_path)
        self.recording_label_changed.emit(self.widgets["combobox"].currentText())

    def browse_for_recording_file(self):
        """
        Slot for button for choosing recording files; gets path to files (select folder
        containing recording files).

        May want to change default location for file browser in future versions.
        """

        recording_path = QFileDialog.getExistingDirectory(self, "Select Intan recording files", "")

        # Change combobox to empty (need to do first so does not disable load button)
        self.widgets["combobox"].setCurrentIndex(0)

        # Emit new recording path
        self.recording_path_changed.emit(recording_path)

        # Get label based on file name (last folder) and emit
        if recording_path:
            recording_label_match = re.search(r"/[^/]*$", recording_path)
            if recording_label_match:
                recording_label = recording_path[recording_label_match.start() + 1 :]
            else:
                recording_label = recording_path
        else:  # If no file name (empty path), send empty string for label
            recording_label = ""
        self.recording_label_changed.emit(recording_label)


class RecordingLabel(QWidget):
    """
    Text indicating what data will be analysed.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "label": InputInlineLabel("Recording: ", self),
            "recording": InputInlineText("", self),
        }

        # Add to layout
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.addItem(ExpandingHSpacer())
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def update_recording(self, text: str):
        """
        Update the recording name.
        """

        self.widgets["recording"].setText(text)


class LoadRecordingButton(LargePushButton):
    """
    Button for loading data.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Load")


class LoadRecordingSection(QWidget):
    """
    Widget for selecting a recording to analyse, with section headers and recording
    label.
    """

    # Signal for whether recording is loaded
    recording_loaded = Signal(bool)

    # Signal for sending new recording
    recording_changed = Signal(EMGDataRawModel)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Attribute for storing EMG model to load and label for recording
        self.emg_model = None
        self.emg_label = ""

        # Create widgets
        self.widgets: dict[str, Any] = {
            "title": SubsectionTitle("Load recording", self),
            "selectrecording": SelectRecordingWidget(parent=self),
            "label": RecordingLabel(parent=self),
            "load": LoadRecordingButton(parent=self),
            "message": InputInlineText("", self),
            "errormessage": InputWarningLabel("", self),
        }

        # Add to layout
        layout = QVBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Connections
        self.widgets["selectrecording"].recording_label_changed.connect(
            self.update_recording_label
        )
        self.widgets["selectrecording"].recording_path_changed.connect(self.update_recording_path)
        self.widgets["load"].clicked.connect(self.load_data)

        # Creates attribute "recording_path" for path to files to load
        # Will be set by other widgets
        self.update_recording_path("")

    def update_recording_label(self, recording_label: str):
        """
        Slot for updating recording label (both the attribute and the label widget).
        """

        self.emg_label = recording_label
        self.widgets["label"].update_recording(recording_label)

    def update_recording_path(self, recording_path: str):
        """
        Slot for updating recording path.
        """

        self.recording_path = recording_path

        # Only allow loading if path is not empty (disables/enables load button)
        if recording_path:
            self.widgets["load"].setEnabled(True)
        else:
            self.widgets["load"].setEnabled(False)

        # Remove any previously loaded data and messages
        self.emg_model = None
        self.recording_loaded.emit(False)
        self.widgets["message"].setText("")
        self.widgets["message"].show()
        self.widgets["errormessage"].setText("")
        self.widgets["errormessage"].hide()

    def load_data(self):
        """
        Load EMG data (slot for load button).
        Also catches and displays specific load errors to help the user correct loading
        problems.
        """

        try:
            emg_files = EMGFiles(self.recording_path)
            emg_data = emg_files.load_emg_data()
        except FileNotFoundError as e:  # If file not found
            self.widgets["errormessage"].show()
            self.widgets["errormessage"].setText(
                f"Could not load recording: recording files not found.\n{e}"
            )
            logger.exception(f"Could not load recording: recording files not found.\n{e}")
        except Exception as e:  # Other errors (don't display specific error message)
            self.widgets["errormessage"].show()
            self.widgets["errormessage"].setText("Could not load recording.")
            logger.exception(f"Could not load recording.\n{e}")
        else:
            self.emg_model = EMGDataRawModel(emg_data)
            self.recording_changed.emit(self.emg_model)  # Must emit first
            self.recording_loaded.emit(True)

            # Message about data
            n_chan = self.emg_model.emg_data.n_chan
            emg_dur = self.emg_model.emg_data.emg_dur
            fs = self.emg_model.emg_data.fs

            msg_chan = f"Channels: {n_chan}"
            msg_dur = f"Duration: {int(emg_dur) // 60:02d}:{int(emg_dur) % 60:02d}"
            msg_fs = f"Sampling frequency: {int(fs):,} Hz"
            self.widgets["message"].setText(
                "<b>Recording loaded</b><br>" + msg_chan + "<br>" + msg_dur + "<br>" + msg_fs
            )

            # log
            logger.info("Recording loaded (" + msg_chan + ", " + msg_dur + ", " + msg_fs + ")")
