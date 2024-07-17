#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widgets for running analysis in load step.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout

from microemggui.widgets.base import (
    LargePushButton,
    SubsectionTitle,
)

# --- Widgets for running the analysis ---


class NextButton(LargePushButton):
    # Button for going to next analysis step
    # Also triggers data to be sent to main window

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Next")


class RunAnalysisSection(QWidget):
    # Section in loading widget for running the analysis
    # TODO: add button for running multiple/all steps of analysis without user input

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
