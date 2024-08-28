#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for displaying jitter analysis.
"""

from typing import Any

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QGridLayout,
)

from microemggui.models.emg import EMGAnalysisReconstructModel
from microemggui.widgets.base import (
    TitleInputLabel,
    SubsectionTitle,
    SectionTitle,
    ExpandingHSpacer,
    InputComboBox,
)

from microemggui.widgets.jitter.jitter_vis import (
    JitterFibrePairVisWidget,
    JitterAllFibrePlotsWidget,
)

# --- Widget for changing motor unit ---


class MUComboBox(QWidget):
    """
    Widget for select the motor unit results that should displayed.
    """

    def __init__(self, motor_units_to_analyse: list[int], parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "label": TitleInputLabel("Motor unit", parent=self),
            "combobox": InputComboBox(parent=self),
        }

        # Add motor units to combobox
        motor_unit_labels = [str(i + 1) for i in motor_units_to_analyse]  # +1 for labels
        self.widgets["combobox"].addItems(motor_unit_labels)
        self.widgets["combobox"].setCurrentText(motor_unit_labels[0])  # set to first motor unit

        # Add to layout
        layout = QHBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.addItem(ExpandingHSpacer())  # spacer to push to left
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


# --- Widget for jitter results ---


class JitterWidget(QWidget):
    """
    Widget for displaying jitter results for the analysed motor units.

    No jitter settings are modified in the GUI, so the analysis is performed when the
    widget is created.
    """

    def __init__(
        self,
        reconstruct_model: EMGAnalysisReconstructModel,
        motor_units_to_analyse: list[int],
        parent=None,
    ):
        super().__init__(parent)

        # EMG reconstruction analysis object
        self.reconstruct_model = reconstruct_model

        # List of the indices of the motor units to analyse
        self.motor_units_to_analyse = motor_units_to_analyse

        # Start by displaying first motor unit in list to analyse
        self.motor_unit_idx = self.motor_units_to_analyse[0]

        # Create widgets
        self.widgets: dict[str, Any] = {
            "title": SectionTitle("Jitter analysis", self),
            "mucombobox": MUComboBox(self.motor_units_to_analyse, parent=self),
            "alltitle": SubsectionTitle("All fibre pairs", parent=self),
            "allvis": JitterAllFibrePlotsWidget(self.reconstruct_model, self.motor_unit_idx),
            "pairvis": JitterFibrePairVisWidget(
                self.reconstruct_model, self.motor_unit_idx, parent=self
            ),
        }

        # Add to grid layout
        layout = QGridLayout()
        layout.addWidget(self.widgets["title"], 0, 0)
        layout.addWidget(self.widgets["mucombobox"], 1, 0)
        layout.addWidget(self.widgets["alltitle"], 2, 0)
        layout.addWidget(self.widgets["allvis"], 3, 0)
        layout.addWidget(self.widgets["pairvis"], 2, 1, 2, 1)  # span 2 rows
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setVerticalSpacing(13)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 3)  # second column wider than first (2:3 ratio)

        self.setLayout(layout)

        # Connect motor unit combobox to update_motor_unit
        # (subtract 1 to go from text label to index, counting from 0)
        self.widgets["mucombobox"].widgets["combobox"].currentTextChanged.connect(
            lambda text: self.update_motor_unit(int(text) - 1)
        )

    def update_motor_unit(self, motor_unit_idx: int):
        """
        Update displayed motor unit in all visualisations.
        """

        self.widgets["pairvis"].update_motor_unit(motor_unit_idx)
        self.widgets["allvis"].update_motor_unit(motor_unit_idx)
