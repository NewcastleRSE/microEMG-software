#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for finding motor units
"""

from typing import Any

from PySide6.QtWidgets import QWidget, QHBoxLayout, QGridLayout
from PySide6.QtCore import Qt

from microemggui.models.emg import EMGAnalysisReconstructModel
from microemggui.models.settings import EMGAnalysisMotorUnitSettingsModel
from microemggui.widgets.base import LargePushButton, SectionTitle
from microemggui.widgets.findmu.mu_settings import MUSettingsWidget
from microemggui.widgets.findmu.mu_results import MUResultsWidget


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

    def enable(self):
        # Slot for enable button when settings are changed.

        self.setEnabled(True)


class NextButton(LargePushButton):
    # Button for proceeding to the next step

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Next")
        self.setToolTip("Proceed to next step")

        self.hide()  # hide initially

        # Retain size if hidden
        size_policy = self.sizePolicy()
        # size_policy.setHorizontalPolicy(QSizePolicy.Maximum)
        size_policy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(size_policy)

    def show_button(self, mu_found: bool):
        # Slot for showing/hiding next button depending on whether motor units are found
        if mu_found:
            self.show()
        else:
            self.hide()


class MainButtons(QWidget):
    # Buttons for applying analysis step and continuing the analysis
    # TODO: consider making part of base class so reusable

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

    def __init__(
        self,
        reconstruct_model: EMGAnalysisReconstructModel,
        mu_settings: EMGAnalysisMotorUnitSettingsModel,
        parent=None,
    ):
        super().__init__(parent)

        # EMG reconstruction analysis object and settings for finding motor units
        self.reconstruct_model = reconstruct_model
        self.mu_settings = mu_settings  # settings model: settings stored in mu_settings.settings

        # Create widgets in first column
        self.widgets: dict[str, Any] = {
            "title": SectionTitle("Find motor units", self),
            "settings": MUSettingsWidget(mu_settings, parent=self),
            "buttons": MainButtons(self),
        }

        # Add to layout
        # Use grid layout with results to right
        layout = QGridLayout()
        row = 0
        col = 0
        for w in self.widgets.values():
            layout.addWidget(w, row, col)
            row += 1

        # Add results widget in second column
        self.widgets["results"] = MUResultsWidget(reconstruct_model, parent=self)
        layout.addWidget(self.widgets["results"], 1, 1)

        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        # Connections

        # Connect apply button to find_motor_units
        self.widgets["buttons"].widgets["apply"].clicked.connect(self.find_motor_units)

        # Enable re-apply if settings changed
        w_name_list = ["sensitivity", "similarity"]
        for w_name in w_name_list:
            w = self.widgets["settings"].widgets[w_name].widgets["combobox"]
            w.currentTextChanged.connect(
                lambda text: self.widgets["buttons"].widgets["apply"].enable()
            )

    def find_motor_units(self):
        """
        Find motor units using specified settings and update widget with results.
        """

        # Update settings
        self.reconstruct_model.reconstruct.mu_settings = self.mu_settings.settings
        print(self.reconstruct_model.reconstruct.mu_settings)

        # Find motor units
        self.reconstruct_model.find_motor_units()

        # Update results plot
        self.widgets["results"].update_reconstruct(self.reconstruct_model)

        # Only show next button if MU found
        # TODO: probably change to signal since also need to disable next step on toolbar
        n_mu = self.reconstruct_model.reconstruct.found_motor_units.n_motor_units
        self.widgets["buttons"].widgets["next"].show_button(n_mu > 0)
