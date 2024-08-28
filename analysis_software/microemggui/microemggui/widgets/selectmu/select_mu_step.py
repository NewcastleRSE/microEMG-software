#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for selecting motor units to further analyse.
"""

from typing import Any

from PySide6.QtWidgets import QWidget, QHBoxLayout, QGridLayout, QButtonGroup, QSizePolicy
from PySide6.QtCore import Qt, Signal

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
        layout.setSpacing(15)
        self.setLayout(layout)


class MotorUnitCheckBoxes(QWidget):
    """
    All checkboxes for selecting motor units to analyse, with buttons for labels for
    navigating to the visualisations of each motor unit.
    """

    # Signal for when motor unit checkbox is toggled
    motor_unit_toggled = Signal(bool, int)

    def __init__(self, n_motor_units: int, parent=None):
        super().__init__(parent)

        self.n_motor_units = n_motor_units

        # Create widgets (checkboxes)
        # Key for each motor unit is its index (counting from 0), but one will be added
        # by MotorUnitCheckBox for the button's label
        self.widgets = {i: MotorUnitCheckBox(i, parent=self) for i in range(self.n_motor_units)}

        # Add all buttons to button group
        button_group = QButtonGroup(parent=self)
        for i in range(self.n_motor_units):
            button_group.addButton(self.widgets[i].widgets["button"])

        # Add to layout
        layout = QGridLayout()
        row = 0
        max_row = 15
        col = 0
        for w in self.widgets.values():
            layout.addWidget(w, row, col, alignment=Qt.AlignLeft | Qt.AlignCenter)
            row += 1
            if row == max_row:  # start new column if reach max number of rows
                row = 0
                col += 1
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(25)
        layout.setVerticalSpacing(0)
        layout.addItem(ExpandingVSpacer())  # vertical spacer to fill space beneath
        self.setLayout(layout)

        # Connections

        # Send index of motor unit with check state when its checkbox is toggled
        for idx, w in self.widgets.items():
            w_checkbox = w.widgets["checkbox"]
            w_checkbox.toggled.connect(
                lambda checked, idx=idx: self.motor_unit_toggled.emit(checked, idx)
            )

    def check_button(self, motor_unit_idx):
        """
        Slot for checking (= highlighting) button that matches motor unit index.
        Used when displayed motor unit is changed using another widget.

        """

        self.widgets[motor_unit_idx].widgets["button"].setChecked(True)


class NextButton(LargePushButton):
    """
    Button for proceeding to the next analysis step.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Next")
        self.setToolTip("Proceed to next step")


# --- Motor unit selection widget ---


class SelectMUWidget(QWidget):
    """
    Widget for selecting motor units to include in the downstream analysis. Also
    displays visualisations of individual motor units.
    """

    # Signal for sending updated list of motor units to analyse
    motor_units_updated = Signal(list)

    def __init__(self, reconstruct_model: EMGAnalysisReconstructModel, parent=None):
        super().__init__(parent)

        # Reconstruction analysis data
        self.reconstruct_model = reconstruct_model
        self.n_motor_units = reconstruct_model.reconstruct.found_motor_units.n_motor_units

        # Boolean and indices of which motor units are checked (none initially)
        # Specifies motor units to analyse
        self.motor_units_checked = [False for i in range(self.n_motor_units)]  # bool
        self.motor_units_checked_idx: list[int] = []

        # Visualised motor unit at start
        motor_unit_idx = 0

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
        for w in self.widgets.values():
            layout.addWidget(w, row, col)
            row += 1
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setHorizontalSpacing(50)
        self.setLayout(layout)

        # Next button is initially disabled since no motor units selected
        self.widgets["next"].setEnabled(False)

        # Update message and set properties - word wrap, fixed height
        self.widgets["message"].setWordWrap(True)
        self.widgets["message"].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.widgets["message"].setObjectName("select_mu_widget_message")
        self.update_message()  # based on number of motor units checked (initially none)

        # Add motor unit visualisations in second column
        self.widgets["vis"] = MUEMGViewerWidget(reconstruct_model, motor_unit_idx, parent=self)
        layout.addWidget(self.widgets["vis"], 0, 1, 3, 1)  # span 3 rows

        # Select motor unit that is initially visualised
        self.widgets["checkboxes"].widgets[motor_unit_idx].widgets["button"].setChecked(True)

        # Connections

        # Connect motor unit buttons to vis displayed
        for i in range(self.n_motor_units):
            self.widgets["checkboxes"].widgets[i].widgets["button"].clicked.connect(
                lambda checked=None, motor_unit_idx=i: self.widgets["vis"].update_motor_unit_idx(
                    motor_unit_idx
                )
            )

        # Connect changes in motor unit arrow keys to which motor unit button is selected
        self.widgets["vis"].motor_unit_idx_changed_from_increment.connect(
            self.widgets["checkboxes"].check_button
        )

        # Connect checkboxes to list of checked motor units
        self.widgets["checkboxes"].motor_unit_toggled.connect(self.update_motor_units_checked)

    def update_motor_units_checked(self, checked: bool, idx: int):
        """
        Update boolean and indices of motor units that are checked.
        Also trigger downstream updates of message text (which motor units will be
        analysed) and enable/disable next button (enable if at least one motor unit).
        Slot for motor_unit_toggled.
        """

        # Update motor units that will be analysed
        self.motor_units_checked[idx] = checked
        self.motor_units_checked_idx = [
            i for i in range(self.n_motor_units) if self.motor_units_checked[i]
        ]

        # Emit motor units - will connect to slot in main GUI
        self.motor_units_updated.emit(self.motor_units_checked_idx)

        # Update message text
        self.update_message()

        # Only enable next button if at least one motor unit is checked
        self.widgets["next"].setEnabled(len(self.motor_units_checked_idx) > 0)

    def update_message(self):
        """
        Update displayed message based on the selected (checked) motor units.

        """

        # Determine message text based on number of motor units checked
        n_checked = len(self.motor_units_checked_idx)
        if n_checked > 0:
            # Labels for checked motor units (+1 from index)
            motor_units_labels = [str(i + 1) for i in self.motor_units_checked_idx]

            if n_checked == 1:
                text = "Will analyse motor unit " + motor_units_labels[0] + "."
            else:
                text = "Will analyse motor units " + ", ".join(motor_units_labels) + "."
        else:
            text = "Select (check) at least one motor unit."

        # Set text
        self.widgets["message"].setText(text)
