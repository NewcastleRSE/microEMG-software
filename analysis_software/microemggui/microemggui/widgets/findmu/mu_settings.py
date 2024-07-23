#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for specifying settings for finding motor units.
"""
from typing import Any

from PySide6.QtWidgets import QWidget, QVBoxLayout

from microemggui.widgets.base import (
    InputLabel,
    InputExplanationLabel,
    InputComboBox,
    SubsectionTitle,
    ExpandingVSpacer,
)

# --- Widgets for settings --- #


class MUSensitivityWidget(QWidget):
    # Widget for setting detection sensitivity for "find motor units" step

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "label": InputLabel("Detection sensitivity", self),
            "explanation": InputExplanationLabel(
                "Increasing the sensitivity threshold captures more motor units, "
                + "but may increase false positives.",
                self,
            ),
            "combobox": InputComboBox(self),
        }

        # Mapping of combobox terms to values
        # TODO: set reasonable defaults
        # TODO: have options as text or numbers?
        self.combobox_values = {"low": 0.05, "medium (default)": 0.1, "high": 0.15}

        # Add combobox options
        self.widgets["combobox"].addItems(list(self.combobox_values.keys()))

        # Layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class MUSimilarityWidget(QWidget):
    # Widget for setting similarity threshold for "find motor units" step

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "label": InputLabel("Motor unit similarity", self),
            "explanation": InputExplanationLabel(
                "Increasing the similarity threshold means potentials "
                + "assigned to the same motor unit must be more similar.",
                self,
            ),
            "combobox": InputComboBox(self),
        }

        # Mapping of combobox terms to values
        # MUPs are assigned to same MU if pseudocorrelation is above the threshold
        # TODO: set reasonable defaults
        # TODO: have options as text or numbers?
        self.combobox_values = {"low": 0.05, "medium (default)": 0.1, "high": 0.15}

        # Add combobox options
        self.widgets["combobox"].addItems(list(self.combobox_values.keys()))

        # Layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


# --- All settings ---


class MUSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "title": SubsectionTitle("Settings"),
            "sensitivity": MUSensitivityWidget(parent=self),
            "similarity": MUSimilarityWidget(parent=self),
        }

        # Add to layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)

        # Spacer at end so extra space is added below settings widgets if window resized
        end_space = ExpandingVSpacer()
        layout.addItem(end_space)

        self.setLayout(layout)
