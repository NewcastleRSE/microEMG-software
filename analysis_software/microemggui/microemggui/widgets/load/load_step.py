#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for loading recording and analysis settings, then starting the analysis.
"""

import re

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFileDialog
from PySide6.QtCore import Signal

from pymicroemg.emg_files import EMGFiles
from pymicroemg.emg_preproc_settings import EMGPreprocSettings
import pymicroemg.helper_config as emg_cfg

from microemggui.models.emg import EMGDataRawModel
from microemggui.models.settings import EMGSettingsModel

from microemggui.widgets.base import (
    SmallPushButton,
    LargePushButton,
    InputInlineText,
    InputInlineLabel,
    InputInlineHighlightedText,
    InputWarningLabel,
    InputComboBox,
    SectionTitle,
    SubsectionTitle,
    ExpandingHSpacer,
    ExpandingVSpacer,
)

# --- Widgets for selecting a recording ---


class SelectRecordingWidget(QWidget):
    # Widget for selecting recording to load

    # Signals for when recording file path and label are changed
    recording_path_changed = Signal(str)
    recording_label_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets = {
            "button": SmallPushButton(self),
            "label": InputInlineLabel("or select demo recording:"),
            "combobox": InputComboBox(parent=self),
        }

        # Button text
        self.widgets["button"].setText("Choose files")
        self.widgets["button"].setToolTip("Choose Intan recording files")

        # Demo options
        # TODO: move to config file?
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
        self.widgets["combobox"].currentIndexChanged.connect(
            self.demo_recording_changed
        )
        self.widgets["button"].clicked.connect(self.browse_for_recording_file)

    def demo_recording_changed(self, idx: int):
        # Slot for when combobox option is changed; receives index of current selection.
        # Uses index to determine demo recording number, then emits signal with
        # recording file path and label.

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
        # Slot for button for choosing recording files; gets path to files
        # TODO: best default location to open file browser?
        # TODO: select folder or header file? currently select folder
        # TODO: handle if file dialog is cancelled (instead of selecting folder)

        recording_path = QFileDialog.getExistingDirectory(
            self, "Select Intan recording files", ""
        )

        # Change combobox to empty (need to do first so does not disable load button)
        self.widgets["combobox"].setCurrentIndex(0)

        # Emit new recording path
        self.recording_path_changed.emit(recording_path)

        # Get label based on file name and emit
        recording_label_match = re.search(r"/[^/]*$", recording_path)
        recording_label = recording_path[recording_label_match.start() + 1 :]
        self.recording_label_changed.emit(recording_label)


class RecordingLabel(QWidget):
    # Text indicating what data will be analysed

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets = {
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
        # Update the recording name
        self.widgets["recording"].setText(text)


class LoadRecordingButton(LargePushButton):
    # Button for loading data

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Load")


class LoadRecordingSection(QWidget):
    # Widget for selecting a recording to analyse, with section headers and recording label

    # Signal for whether recording is loaded
    recording_loaded = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Attribute for storing EMG model to load and label for recording
        self.emg_model = None
        self.emg_label = ""

        # Create widgets
        self.widgets = {
            "title": SubsectionTitle("Load recording", self),
            "selectrecording": SelectRecordingWidget(parent=self),
            "label": RecordingLabel(parent=self),
            "load": LoadRecordingButton(parent=self),
            "message": InputInlineHighlightedText("", self),
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
        self.widgets["selectrecording"].recording_path_changed.connect(
            self.update_recording_path
        )
        self.widgets["load"].clicked.connect(self.load_data)

        # Creates attribute "recording_path" for path to files to load
        # Will be set by other widgets
        self.update_recording_path("")

    def update_recording_label(self, recording_label: str):
        # Slot for updating recording label (attribute and label widget)

        self.emg_label = recording_label
        self.widgets["label"].update_recording(recording_label)

    def update_recording_path(self, recording_path: str):
        # Slot for updating recording path

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
        # Load EMG data (slot for load button)
        # TODO: continue adding to specific errors that can be caught (e.g., no header file)
        # TODO: loading spinner or pop up window during loading
        # TODO: send emg data to main window

        try:
            emg_files = EMGFiles(self.recording_path)
            emg_data = emg_files.load_emg_data()
        except FileNotFoundError as e:
            self.widgets["errormessage"].show()
            self.widgets["errormessage"].setText(
                f"Could not load recording: recording files not found.\n{e}"
            )
        except Exception as e:
            self.widgets["errormessage"].show()
            self.widgets["errormessage"].setText(f"Could not load recording.\n{e}")
        else:
            self.emg_model = EMGDataRawModel(emg_data)
            self.recording_loaded.emit(True)

            # Message about data
            n_chan = self.emg_model.emg_data.n_chan
            emg_dur = self.emg_model.emg_data.emg_dur
            self.widgets["message"].setText(
                f"Recording loaded! The recording has {n_chan} channels and is {round(emg_dur/60, 2)} minutes."
            )


# --- Widgets for selecting preprocessing settings ---


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
    # TODO: display settings when selected?

    # Signal for whether settings have been loaded
    settings_loaded = Signal(bool)

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
        self.widgets["load"].widgets["combobox"].currentTextChanged.connect(
            self.load_settings
        )

    def load_settings(self, settings_name: str):
        # Add correct settings as attribute when settings combobox is changed
        # TODO: Update to get from config file and use all settings (not just preproc)

        if not settings_name:  # No settings selected
            self.settings = None
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
            self.settings_model = EMGSettingsModel(
                preprocess_settings=preprocess_settings
            )
            self.settings_loaded.emit(True)
        self.display_settings()

    def display_settings(self):
        if not self.settings_model:
            self.widgets["settingstext"].setText("")
        else:
            settings_text = self.settings_model.get_formatted_settings_text()
            self.widgets["settingstext"].setText(settings_text)


# --- Widgets running the analysis ---


class NextButton(LargePushButton):
    # Button for going to next analysis step
    # Also triggers data to be sent to main window

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Next")


class RunAnalysisSection(QWidget):
    # Section in loading widget for running the analysis
    # TODO: add buttons for running analysis either step-by-step or all steps

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets = {
            "title": SubsectionTitle("Run microEMG analysis", self),
            "next": NextButton(parent=self),
        }

        # Add to layout
        layout = QVBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


# --- Widgets with all initial steps ---


class LoadSteps(QWidget):
    # Widget containing all load steps (loading recording, loading settings, running
    # analysis)
    # Separate from full widget with title to make it easier to set spacing between
    # sections.

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets = {
            "recording": LoadRecordingSection(parent=self),
            "settings": LoadSettingsSection(parent=self),
            "run": RunAnalysisSection(parent=self),
        }

        # Keep size when hidden
        for _, w in self.widgets.items():
            size_policy = w.sizePolicy()
            size_policy.setRetainSizeWhenHidden(True)
            w.setSizePolicy(size_policy)

        # Add to layout
        layout = QVBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.addItem(ExpandingVSpacer())
        layout.setSpacing(50)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Connections
        self.widgets["recording"].recording_loaded.connect(
            self.show_and_hide_steps_after_loading_emg
        )
        self.widgets["settings"].settings_loaded.connect(
            self.show_and_hide_steps_after_loading_settings
        )

        # Signal that recording has not been loaded
        self.widgets["recording"].recording_loaded.emit(False)

    def show_and_hide_steps_after_loading_emg(self, recording_loaded: bool):
        # Show/hide steps after loading depend on if data has been loaded
        # Slot for recording_loaded signal

        if recording_loaded:
            self.widgets["settings"].show()
        else:
            self.widgets["settings"].hide()
            # Remove any previously selected settings
            self.widgets["settings"].widgets["load"].widgets[
                "combobox"
            ].setCurrentIndex(0)
            self.widgets["run"].hide()

    def show_and_hide_steps_after_loading_settings(self, settings_loaded: bool):
        # Show/hide steps after loading depend on if data has been loaded
        # Slot for settings_loaded signal

        if settings_loaded:
            self.widgets["run"].show()
        else:
            self.widgets["run"].hide()


class LoadWidget(QWidget):
    # Full widget for loading recording and setting up analysis

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets = {
            "title": SectionTitle("MicroEMG analysis set-up", self),
            "steps": LoadSteps(parent=self),
        }

        # Add to layout
        layout = QVBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.addItem(ExpandingVSpacer())
        layout.setContentsMargins(20, 0, 0, 0)
        self.setLayout(layout)
