#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for trimming EMG recording during the load step
"""

from typing import Any
import logging

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMainWindow

from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator


from microemggui.models.emg import EMGDataRawModel
from microemggui.widgets.emg_viewer import EMGViewerWidget

from microemggui.widgets.base import (
    SmallPushButton,
    LargePushButton,
    InputInlineText,
    InputWarningLabel,
    MessageLabel,
    InputLineEdit,
    SubsectionTitle,
    ExpandingHSpacer,
)

logger = logging.getLogger("microemggui.load")

# --- Widgets in trim section ---


class EMGViewerWindow(QMainWindow):
    """
    EMG viewer in separate window.
    """

    def __init__(self, raw_emg_model: EMGDataRawModel, emg_clrs: list[str], parent=None):
        super().__init__(parent)

        # Viewer
        widget = EMGViewerWidget(raw_emg_model, emg_clrs)
        self.setCentralWidget(widget)

        # Window size
        self.resize(1100, 700)


class ViewEMGButton(SmallPushButton):
    """
    Button for opening EMG viewer
    """

    def __init__(self, raw_emg_model: EMGDataRawModel, emg_clrs: list[str], parent=None):
        super().__init__(parent)

        # Colours
        self.emg_clrs = emg_clrs

        # Button settings
        self.setText("View EMG")
        self.setToolTip("Open EMG viewer")

        # Create viewer
        self.viewer = EMGViewerWindow(raw_emg_model, emg_clrs)

        # Connections
        self.clicked.connect(self.button_clicked)

    def button_clicked(self):
        """
        Slot for when button is clicked to show EMG viewer.

        """
        self.viewer.show()

    def update_emg(self, raw_emg_model):
        """
        Update EMG and recreate the viewer.
        Ensures correct limits for time slider.
        """

        # Delete existing viewer
        self.viewer.deleteLater()
        self.viewer = EMGViewerWindow(raw_emg_model, self.emg_clrs)


class TrimRecordingButton(LargePushButton):
    """
    Button for trimming EMG data.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Trim")


class TrimFields(QWidget):
    """
    Input fields, with labels, for selecting period of EMG to analyse.
    Also includes button for viewing EMG.
    """

    def __init__(self, raw_emg_model: EMGDataRawModel, emg_clrs: list[str], parent=None):
        super().__init__(parent)

        # EMG
        self.emg_model = raw_emg_model

        # Create widgets
        self.widgets: dict[str, Any] = {
            "text1": InputInlineText("Analyse from", self),
            "start_field": InputLineEdit(parent=self),
            "text2": InputInlineText("to", self),
            "end_field": InputLineEdit(parent=self),
            "text3": InputInlineText("seconds"),
            "emg_button": ViewEMGButton(raw_emg_model, emg_clrs, self),
        }

        self.input_fields = ["start_field", "end_field"]  # keys of text input fields

        # Add to layout
        layout = QHBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.addItem(ExpandingHSpacer())
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Set up for input fields
        self.set_input_validators_and_text()

    def set_input_validators_and_text(self):
        """
        Set default text and create validators for the trim inputs based on length of
        EMG recording.

        Note that the validator does not prevent all out-of-range values, so we also
        check the validity in TrimRecordingSection.trim_emg

        In order to keep the input to integer values, the EMG's duration is rounded down
        to the nearest whole second, which means that <1 second of the recording may be
        removed from the analysis even with the most lenient trim settings.

        """
        start_time = 0
        end_time = int(self.emg_model.emg_data.emg_dur)  # convert duration to int

        # Starting text
        start_text = str(start_time)
        end_text = str(end_time)
        self.widgets["start_field"].setText(start_text)
        self.widgets["end_field"].setText(end_text)

        # Set validators
        start_validator = QIntValidator(start_time, end_time)
        self.widgets["start_field"].setValidator(start_validator)
        end_validator = QIntValidator(start_time, end_time)
        self.widgets["end_field"].setValidator(end_validator)


# --- Trim widget ---


class TrimRecordingSection(QWidget):
    """
    Widget for trimming the loaded recording, with section header.
    """

    # Signal to emit when recording is trimmed
    recording_trimmed = Signal()

    def __init__(self, raw_emg_model: EMGDataRawModel, emg_clrs: list[str], parent=None):
        super().__init__(parent)

        # EMG
        self.emg_model = raw_emg_model

        # Create widgets
        self.widgets: dict[str, Any] = {
            "title": SubsectionTitle("Trim recording segment", self),
            "fields": TrimFields(raw_emg_model, emg_clrs, parent=self),
            "warning": InputWarningLabel("", parent=self),
            "trim_button": TrimRecordingButton(parent=self),
            "success_message": MessageLabel("", parent=self),
        }

        # Hide messages
        self.widgets["warning"].hide()
        self.widgets["success_message"].hide()

        # Add to layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.setLayout(layout)

        # Connections
        self.widgets["trim_button"].clicked.connect(self.trim_emg)

        w_names = self.widgets["fields"].input_fields
        for name in w_names:
            self.widgets["fields"].widgets[name].textChanged.connect(
                lambda text: self.hide_warning_message()
            )

    def trim_emg(self):
        """
        Trim EMG based on widget input.

        Will first check if times are valid (start time must be less than stop time).
        If times are not valid, shows an error message instead.
        """

        # Get start and stop times for trim from input fields
        start_t = int(self.widgets["fields"].widgets["start_field"].text())
        end_t = int(self.widgets["fields"].widgets["end_field"].text())

        # Check if start and stop times are in allowed range
        min_t = 0
        max_t = int(self.emg_model.emg_data.emg_dur)

        start_valid = start_t >= min_t and start_t <= max_t
        end_valid = end_t >= min_t and end_t <= max_t

        if (not start_valid) or (not end_valid):  # Don't trim if not in valid range
            # Show error message
            self.widgets["warning"].setText(
                f"The trim times must be between {min_t} and {max_t} seconds."
            )
            self.widgets["warning"].show()

        elif start_t >= end_t:  # Don't trim if start time is >= end time
            # Show error message
            self.widgets["warning"].setText("The trim start time must be less than the stop time.")
            self.widgets["warning"].show()

        else:  # If valid ranges and relative values, trim
            # Trim
            print(self.emg_model.emg_data.emg_dur)
            self.emg_model.emg_data.trim_emg_ts(start_t, end_t)
            print(self.emg_model.emg_data.emg_dur)

            # Update viewer
            self.widgets["fields"].widgets["emg_button"].update_emg(self.emg_model)

            # Update success message and show
            self.widgets["success_message"].setText(
                f"<b>Recording trimmed</b> to {start_t} to {end_t} seconds "
                + f"({self.format_seconds(start_t)} to {self.format_seconds(end_t)})"
            )
            self.widgets["success_message"].show()

            # Disable trim (can only trim once to make it easier to keep track of segment used)
            self.widgets["trim_button"].setEnabled(False)
            w_names = self.widgets["fields"].input_fields
            for name in w_names:
                self.widgets["fields"].widgets[name].setDisabled(True)

            # Emit signal indicating that trim has been performed
            self.recording_trimmed.emit()

    def hide_warning_message(self):
        """
        Slot for hiding warning (error) message when input is updated.
        """

        self.widgets["warning"].hide()

    @staticmethod
    def format_seconds(time_s: int) -> str:
        """
        Convert time in seconds to a mm:ss string.

        Only use int input, so do not need to account for ms

        """

        S_TO_MIN = 60

        n_min = int(time_s / S_TO_MIN)
        n_sec = time_s - (n_min * S_TO_MIN)

        time_label = f"{n_min:02d}:{int(n_sec):02d}"
        return time_label
