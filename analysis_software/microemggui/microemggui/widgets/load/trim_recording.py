#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for trimming EMG recording during the load step
"""

from typing import Any
import logging

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMainWindow

# from PySide6.QtCore import Signal


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

        self.setText("View EMG")
        self.setToolTip("Open EMG viewer")

        self.viewer = EMGViewerWindow(raw_emg_model, emg_clrs)

        # Connections
        self.clicked.connect(self.button_clicked)

    def button_clicked(self):
        """
        Slot for when button is clicked to show EMG viewer.

        """
        self.viewer.show()


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

        # Validate input
        # set default text

    # def set_default_trim_text(self):


# --- Trim widget ---


class TrimRecordingSection(QWidget):
    """
    Widget for trimming the loaded recording, with section header.
    """

    def __init__(self, raw_emg_model: EMGDataRawModel, emg_clrs: list[str], parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "title": SubsectionTitle("Trim recording (optional)", self),
            "fields": TrimFields(raw_emg_model, emg_clrs, parent=self),
            "warning": InputWarningLabel("", parent=self),
            "trim_button": TrimRecordingButton(parent=self),
            "success_message": MessageLabel("Recording trimmed!", parent=self),
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
