#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for loading recording and analysis settings, then starting the analysis.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Signal

import pymicroemg.helper_config as emg_cfg

from microemggui.widgets.base import (
    SmallPushButton,
    LargePushButton,
    InputInlineText,
    InputInlineLabel,
    InputInlineHighlightedText,
    InputComboBox,
    SubsectionTitle,
    ExpandingHSpacer,
)

# --- Widgets for selecting a recording ---


class SelectRecordingWidget(QWidget):
    # Widget for selecting recording to load
    # TODO: implement specifying recording by choosing directory (or Intan header file)

    # Signal for when recording file path is changed
    recording_path_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets = {
            "button": SmallPushButton(self),
            "or": InputInlineText("or", self),
            "label": InputInlineLabel("select demo recording:"),
            "combobox": InputComboBox(parent=self),
        }

        # Button text
        self.widgets["button"].setText("Choose files")
        self.widgets["button"].setToolTip("Choose Intan recording files")

        # Demo options
        # TODO: move to config file?
        self.demo_names = ["", "Demo Recording 1 (healthy)"]
        self.demo_recording_num = [-1, 0]  # < 0 = not a recording
        self.widgets["combobox"].addItems(self.demo_names)

        # Add to layout
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.widgets["combobox"].currentIndexChanged.connect(self.demo_recording_changed)

    def demo_recording_changed(self, idx: int):
        # Slot for when combobox option is changed; receives index of current selection.
        # Uses index to determine demo recording number, then emits signal with file
        # path.

        recording_num = self.demo_recording_num[idx]

        if recording_num < 0:  # Signifies that no recording is selected
            recording_path = ""
        else:  # Otherwise, use recording number to retrieve path to recording
            recording_path, _ = emg_cfg.get_recording_path_and_id(recording_num)

        # Emit signal with new recording path
        self.recording_path_changed.emit(recording_path)


class RecordingLabel(QWidget):
    # Text indicating what data will be analysed

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets = {
            "data": InputInlineLabel("Data: ", self),
            "recording": InputInlineHighlightedText("", self),
        }

        # Add to layout
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.addItem(ExpandingHSpacer())
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def update_recording(self, text: str):
        # Update the recording name
        self.widgets["recording"].setText(text)


class LoadRecordingButton(LargePushButton):
    # Button for loading data

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Load")


class LoadRecordingSection(QWidget):
    # Widget for selecting a recording to analyse, with section headers and recording label

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets = {
            "title": SubsectionTitle("Load recording", self),
            "recording": SelectRecordingWidget(parent=self),
            "label": RecordingLabel(parent=self),
            "load": LoadRecordingButton(parent=self),
        }

        # Add to layout
        layout = QVBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Connections
        self.widgets["recording"].widgets["combobox"].currentTextChanged.connect(
            self.widgets["label"].update_recording
        )

        self.widgets["recording"].recording_path_changed.connect(self.update_recording_path)

        # Creates attribute "recording_path" for path to files to load
        # Will be set by other widgets
        self.update_recording_path("")

    def update_recording_path(self, recording_path: str):
        # Slot for updating recording path

        self.recording_path = recording_path
        print(self.recording_path)

        # only allow loading if path is not empty
        if recording_path:
            self.widgets["load"].setEnabled(True)
        else:
            self.widgets["load"].setEnabled(False)


# --- Widgets for selecting preprocessing settings ---


class ChooseSettingsSection(QWidget):
    # Widget for selecting analysis settings
    # TODO: consider adding option to add new settings
    # TODO: add settings
    # TODO: display settings when selected?

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets = {"title": SubsectionTitle("Choose analysis settings", self)}

        # Add to layout
        layout = QVBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


# --- Widgets running the analysis ---


class RunAnalysisSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets = {"title": SubsectionTitle("Run microEMG analysis", self)}

        # Add to layout
        layout = QVBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


# --- Widget with all initial steps ---


class LoadWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets = {
            "recording": LoadRecordingSection(parent=self),
            "preprocessing": ChooseSettingsSection(parent=self),
            "run": RunAnalysisSection(parent=self),
        }

        # Add to layout
        layout = QVBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
