#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for finding motor units
"""

from typing import Any

from PySide6.QtWidgets import QWidget, QHBoxLayout, QGridLayout
from PySide6.QtCore import Qt

from microemggui.models.settings import EMGAnalysisMotorUnitSettingsModel
from microemggui.widgets.findmu.mu_settings import MUSettingsWidget
from microemggui.widgets.base import LargePushButton, SectionTitle

# --- Buttons ---


class ApplyMUSettingsButton(LargePushButton):
    # Button for applying motor unit settings and finding motor units

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Apply")
        self.setToolTip("Apply settings and find motor units")

        # Connections
        self.clicked.connect(self.button_clicked)

    def button_clicked(self):
        # Update text and disable (will re-enable if settings updated)

        self.setText("Re-apply")
        self.setEnabled(False)

    def change_enabled(self):
        # Slot for enable/disabling button when settings are changed.

        self.setEnabled(True)


class NextButton(LargePushButton):
    # Button for proceeding to the next step

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Next")
        self.setToolTip("Proceed to next step")

        self.hide()  # hide initially

    def show_button(self):
        # Slot for revealing next button after motor units are found
        self.show()


class MainButtons(QWidget):
    # Buttons for applying analysis step and continuing the analysis
    # TODO: make part of base class so reusable

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "apply": ApplyMUSettingsButton(self),
            "next": NextButton(self),
        }

        # Add to layout
        layout = QHBoxLayout()
        layout.addWidget(self.widgets["apply"], alignment=Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.widgets["next"], alignment=Qt.AlignRight | Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


# --- Find motor units widget ---


class FindMUWidget(QWidget):
    # Widget for find motor units step

    def __init__(self, mu_settings: EMGAnalysisMotorUnitSettingsModel, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "title": SectionTitle("Find motor units", self),
            "settings": MUSettingsWidget(mu_settings, parent=self),
            "buttons": MainButtons(self),
        }

        # Add to layout
        # Use grid layout so can add results to right
        layout = QGridLayout()
        row = 0
        for w in self.widgets.values():
            layout.addWidget(w, row, 0)
            row += 1
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
