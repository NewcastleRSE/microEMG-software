#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for finding motor units
"""

from typing import Any

from PySide6.QtWidgets import QWidget, QHBoxLayout, QGridLayout, QProgressDialog, QProgressBar
from PySide6.QtCore import Qt, Signal

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


class NextButton(LargePushButton):
    # Button for proceeding to the next step

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Next")
        self.setToolTip("Proceed to next step")

        self.hide()  # hide initially

        # Retain size if hidden
        size_policy = self.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(size_policy)

    def show_button(self, mu_found: bool):
        # Slot for showing/hiding next button depending on whether motor units are found
        if mu_found:
            self.show()
            self.setEnabled(True)  # ensure enabled, too
        else:
            self.hide()


class MainButtons(QWidget):
    # Buttons for applying analysis step and continuing the analysis

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

    # Signal for whether motor units have been found
    motor_units_found = Signal(bool)

    # Signal to indicate that settings have been changed
    settings_changed = Signal()

    def __init__(
        self,
        reconstruct_model: EMGAnalysisReconstructModel,
        parent=None,
    ):
        super().__init__(parent)

        # EMG reconstruction analysis object
        self.reconstruct_model = reconstruct_model

        # Motor units settings model (settings will be stored in mu_settings_model.settings)
        self.mu_settings_model = EMGAnalysisMotorUnitSettingsModel(
            reconstruct_model.reconstruct.mu_settings
        )

        # Create widgets in first column
        self.widgets: dict[str, Any] = {
            "title": SectionTitle("Find motor units", self),
            "settings": MUSettingsWidget(self.mu_settings_model, parent=self),
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

        layout.setContentsMargins(20, 5, 20, 20)
        self.setLayout(layout)

        # Connections

        # Connect apply button to find_motor_units
        self.widgets["buttons"].widgets["apply"].clicked.connect(self.find_motor_units)

        # Trigger events if settings changed
        w_name_list = ["sensitivity", "similarity"]
        for w_name in w_name_list:
            w = self.widgets["settings"].widgets[w_name].widgets["combobox"]
            w.currentTextChanged.connect(lambda text: self.settings_changed_events())

    def find_motor_units(self):
        """
        Find motor units using specified settings and update widget with results.
        """

        # Create dialog box to indicate step may be slow
        # Note: ideal set up would be to set min and max to 0 to create busy indicator,
        # but animation only works if use multithreading (had issues implementing for
        # finding motor units, so using this simpler implementation of empty bar)
        self.progress = QProgressDialog("Finding motor units...", None, 0, 100, parent=self)
        bar = QProgressBar(self.progress)
        bar.setMinimum(0)
        bar.setMaximum(100)
        bar.setTextVisible(False)
        bar.setObjectName("findmuprogress")  # to hide in style sheet
        self.progress.setBar(bar)
        # Ensure that progress dialog closes if GUI window is minimised
        # GUI window will pop up when process finishes and the progress bar closes
        self.progress.setAttribute(Qt.WA_DeleteOnClose, True)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setMinimumDuration(0)

        # Show progress bar
        self.progress.show()

        # Update settings
        self.reconstruct_model.reconstruct.mu_settings = self.mu_settings_model.settings

        # Find motor units
        self.reconstruct_model.find_motor_units()

        # Close dialog window when analysis is finished
        self.progress.setValue(100)
        self.progress.cancel()

        # Update results plot
        self.widgets["results"].update_reconstruct(self.reconstruct_model)

        # Only show next button if MU found
        n_mu = self.reconstruct_model.reconstruct.found_motor_units.n_motor_units
        self.widgets["buttons"].widgets["next"].show_button(n_mu > 0)
        self.motor_units_found.emit(
            n_mu > 0
        )  # emit signal to enable/disable next steps in main GUI

    def settings_changed_events(self):
        """
        When any settings changed, 1) enable re-apply button, 2) disable next button,
        and 3) send signal that settings have been changed (for main GUI)

        """

        self.widgets["buttons"].widgets["apply"].setEnabled(True)
        self.widgets["buttons"].widgets["next"].setEnabled(False)
        self.settings_changed.emit()
