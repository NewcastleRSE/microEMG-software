#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main window toolbars and widgets placed in toolbars (e.g., logo button)
"""
import os
import subprocess

from PySide6.QtWidgets import (
    QToolBar,
    QLabel,
    QPushButton,
    QButtonGroup,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon

import microemggui
from microemggui.widgets.base import (
    AnalysisToolbarButton,
    AnalysisToolbarLabel,
)
from microemggui.icons import icons  # noqa - import allows icon references

# --- Widgets in toolbars ---


class MicroEMGLogo(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Button icon
        logo_icon = "microemg"

        self.setIcon(QIcon(":/logo/" + logo_icon))
        self.setStatusTip("Home")
        self.setCheckable(True)


class RecordingLabel(QLabel):
    # Widget for recording label in top toolbar
    # Separate class so easy to style

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# --- Toolbars ---


class AnalysisToolbar(QToolBar):
    # Toolbar on left of window for navigating analysis steps

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Info about widgets to add to toolbar
        toolbar_w_text = {
            "preptext": "Prepare EMG",
            "load": "1. Load",
            "preprocess": "2. Preprocess",
            "channels": "3. Select channels",
            "analysetext": "Analyse EMG",
            "findmu": "4. Find motor units",
            "selectmu": "5. Select motor units",
            "localise": "6. Localise fibres",
            "jitter": "7. Analyse jitter",
            "exporttext": "Export results",
            "export": "Export",
        }

        toolbar_w_is_button = [
            False,
            True,
            True,
            True,
            False,
            True,
            True,
            True,
            True,
            False,
            True,
        ]

        # Create and add widgets
        self.widgets = {}
        button_group = QButtonGroup(self)  # group so can only click one at a time

        # First add logo button for home page
        self.widgets["home"] = MicroEMGLogo(parent=self)
        self.addWidget(self.widgets["home"])
        button_group.addButton(self.widgets["home"])

        # Add analysis step buttons and section labels
        for (w_name, text), button in zip(toolbar_w_text.items(), toolbar_w_is_button):
            if button:  # Create buttons
                self.widgets[w_name] = AnalysisToolbarButton(text, parent=self)
                self.widgets[w_name].setEnabled(False)  # Disable buttons at start
                self.widgets[w_name].setCheckable(True)  # Add checked state
                button_group.addButton(self.widgets[w_name])  # Add to button group
            else:  # Create section labels
                self.widgets[w_name] = AnalysisToolbarLabel(text, parent=self)
            self.addWidget(self.widgets[w_name])  # Add widget to toolbar

        # Initial button states
        self.widgets["load"].setEnabled(True)  # Enable first step (loading)
        self.widgets["home"].toggle()

        # Toolbar properties
        self.setMovable(False)
        self.setOrientation(Qt.Vertical)


class TopToolbar(QToolBar):
    # Toolbar on top of page for settings, info, and help links
    # Also has label for recording

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add placehold label for recording
        self.widgets = {"recording": RecordingLabel("", parent=self)}
        size_policy = self.widgets["recording"].sizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Expanding)
        self.widgets["recording"].setSizePolicy(size_policy)

        for w in self.widgets.values():
            self.addWidget(w)

        # Icons for actions
        my_icons = ["question-circle"]

        tips = ["Help"]

        for ic, tip in zip(my_icons, tips):
            action = QAction(QIcon(":/bootstrap/" + ic), tip, self)
            action.setStatusTip(tip)
            self.addAction(action)

            # Connect help icon to opening pdf
            if tip == "Help":
                action.triggered.connect(self.open_help_guide_pdf)

        # Properties
        self.setIconSize(QSize(16, 16))

    def change_recording_label(self, recording: str):
        # Slot for updating recording label

        if recording:
            self.widgets["recording"].setText(f"<b>Recording:</b> {recording}")
        else:  # if label is empty, remove all text from label
            self.widgets["recording"].setText("")

    def open_help_guide_pdf(self):
        """
        Open help guide for microEMG GUI.
        File must have specified name and file path.
        """

        # Get path to module
        module_path = os.path.dirname(microemggui.__file__)

        # Path to PDF
        pdf_file_path = os.path.join(module_path, "docs", "microemg_help_guide.pdf")

        # Open
        subprocess.Popen(["open", pdf_file_path])
