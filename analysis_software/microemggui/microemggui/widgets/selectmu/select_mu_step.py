#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for selecting motor units to further analyse.
"""

from typing import Any

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QButtonGroup
from PySide6.QtCore import Qt

from microemggui.models.emg import EMGAnalysisReconstructModel
from microemggui.widgets.selectmu.mu_vis import MUEMGViewerWidget
from microemggui.widgets.base import (
    CheckBoxMain,
    MotorUnitButton,
    LargePushButton,
    SectionTitle,
    HighlightedLabel,
    ExpandingVSpacer,
)

# --- Component widgets ---


class MotorUnitCheckBox(QWidget):
    """
    Checkbox widget for motor unit with button for label. Button will allow navigation
    to the visualisations of the corresponding motor unit.

    Adds one to the motor unit number for the displayed label.
    """

    def __init__(self, motor_unit_num: int, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "checkbox": CheckBoxMain(parent=self),
            "button": MotorUnitButton(f"Motor unit {motor_unit_num + 1}", parent=self),
        }

        # Make button checkable
        self.widgets["button"].setCheckable(True)

        # Add to layout
        layout = QHBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)


class MotorUnitCheckBoxes(QWidget):
    """
    All checkboxes for selecting motor units to analyse, with buttons for labels for
    navigating to the visualisations of each motor unit.
    """

    def __init__(self, n_motor_units: int, parent=None):
        super().__init__(parent)

        self.n_motor_units = n_motor_units

        # Create widgets (checkboxes)
        # Key for each motor unit is its index (counting from 0), but one will be added
        # by MotorUnitCheckBox for the button's label
        self.widgets = {i: MotorUnitCheckBox(i, parent=self) for i in range(n_motor_units)}

        # Add all buttons to button group
        button_group = QButtonGroup(parent=self)
        for i in range(n_motor_units):
            button_group.addButton(self.widgets[i].widgets["button"])

        # Add to layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addItem(ExpandingVSpacer())  # vertical spacer to fill space beneath
        self.setLayout(layout)


class NextButton(LargePushButton):
    """
    Button for proceeding to the next analysis step.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Next")
        self.setToolTip("Proceed to next step")

    def change_enabled(self, enabled: bool):
        """
        Method for enable/disabling button based on whether at least one motor unit
        is selected.
        """

        self.setEnabled(enabled)


# --- Motor unit selection widget ---


class SelectMUWidget(QWidget):
    """
    Widget for selecting motor units to include in the downstream analysis. Also
    displays visualisations of individual motor units.
    """

    def __init__(self, reconstruct_model: EMGAnalysisReconstructModel, parent=None):
        super().__init__(parent)

        # Reconstruction analysis data
        self.reconstruct_model = reconstruct_model
        self.n_motor_units = reconstruct_model.reconstruct.found_motor_units.n_motor_units

        # Visualised motor unit at start
        self.mu_vis_num = 0

        # Create widgets for first column
        self.widgets: dict[str, Any] = {
            "title": SectionTitle("Select motor units", parent=self),
            "checkboxes": MotorUnitCheckBoxes(self.n_motor_units, parent=self),
            "message": HighlightedLabel("", parent=self),
            "next": NextButton(parent=self),
        }

        # Add to layout
        # Will first add widgets in first column
        layout = QGridLayout()
        row = 0
        col = 0
        for k, w in self.widgets.items():
            if k == "next":
                layout.addWidget(w, row, col, alignment=Qt.AlignRight | Qt.AlignTop)
            layout.addWidget(w, row, col)
            row += 1
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setHorizontalSpacing(50)
        self.setLayout(layout)

        # Add motor unit visualisations in second column
        self.widgets["vis"] = MUEMGViewerWidget(reconstruct_model, self.mu_vis_num, parent=self)
        layout.addWidget(self.widgets["vis"], 0, 1, 3, 1)  # span 3 rows

        # Connections
