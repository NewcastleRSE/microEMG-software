#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 11:41:14 2024

@author: Gabrielle
"""
from typing import Any

from PySide6.QtWidgets import QWidget, QHBoxLayout, QGridLayout, QProgressDialog, QApplication
from PySide6.QtCore import Qt, Signal

from microemggui.models.emg import EMGAnalysisReconstructModel
from microemggui.models.settings import EMGAnalysisMotorUnitClusterSettingsModel
from microemggui.widgets.base import LargePushButton, SectionTitle, SubsectionTitle
from microemggui.widgets.localise.localise_settings import LocaliseSettingsWidget
from microemggui.widgets.localise.localise_results import FibreLocalisationResultsWidget


# --- Buttons ---


class ApplyLocaliseFibresButton(LargePushButton):
    """
    Button for applying settings settings for localising fibres and triggering this step
    of the analysis.

    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Apply")
        self.setToolTip("Apply settings and localise fibres")

        # Connections
        self.clicked.connect(self.button_clicked)

    def button_clicked(self):
        """
        Update text and disable (will re-enable if settings updated)
        """

        self.setText("Re-apply")
        self.setEnabled(False)


class NextButton(LargePushButton):
    """
    Button for proceeding to the next step
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Next")
        self.setToolTip("Proceed to next step")

        self.hide()  # hide initially

        # Retain size if hidden
        size_policy = self.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(size_policy)

    def show_button(self, fibres_found: bool):
        """
        Slot for showing next button depending on whether fibres are found.
        """
        if fibres_found:
            self.show()
            self.setEnabled(True)  # ensure enabled
        else:
            self.hide()


class MainButtons(QWidget):
    """
    Buttons for applying analysis step and continuing the analysis.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "apply": ApplyLocaliseFibresButton(self),
            "next": NextButton(self),
        }

        # Add to layout
        layout = QHBoxLayout()
        layout.addWidget(self.widgets["apply"], alignment=Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.widgets["next"], alignment=Qt.AlignRight | Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


# --- Localise fibres widget ---


class LocaliseWidget(QWidget):
    """
    Widgets for localising fibres step.

    Note that this step combines the "peak finding" and clustering parts of the fibre
    reconstruction analysis. Only (one of) the clustering settings can be modified in
    by the GUI user. As such, results of the first step (fibre reconstruction) are not
    changed if the clustering settings are changed. To reduce the analysis runtime, this
    widget therefore skips the fibre reconstruction step if it has already been
    performed. This approach allows the user to change the clustering settings without
    having to re-run the entire localisation analysis.
    """

    # Signal for whether fibres have been found
    fibres_found = Signal(bool)

    # Signal to indicate that settings have been changed
    settings_changed = Signal()

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

        # Localisation requires two settings classes: the fibre reconstruction settings
        # (EMGAnalysisReconstructSettings) and the cluster settings
        # (EMGAnalysisMotorUnitClusterSettings).
        # Only the cluster settings can be modified by the user, so we only need to make
        # a model (i.e., interface) for that settings class. The settings are stored in
        # self.cluster_settings_model.settings.
        # The fibre reconstruction settings are already an attribute of the reconstruct
        # class and will not be modified here.
        self.cluster_settings_model = EMGAnalysisMotorUnitClusterSettingsModel(
            reconstruct_model.reconstruct.mu_cluster_settings
        )

        # Create widgets in first column
        self.widgets: dict[str, Any] = {
            "title": SectionTitle("Localise fibres", self),
            "settings": LocaliseSettingsWidget(self.cluster_settings_model, parent=self),
            "buttons": MainButtons(self),
        }

        # Add to layout
        # Use grid layout; results will be added to the right
        self.layout = QGridLayout()
        row = 0
        col = 0
        for w in self.widgets.values():
            self.layout.addWidget(w, row, col, alignment=Qt.AlignLeft)
            row += 1

        self.layout.setContentsMargins(20, 5, 20, 20)
        self.setLayout(self.layout)

        # Connections

        # Connect apply button to localise_fibres
        self.widgets["buttons"].widgets["apply"].clicked.connect(self.localise_fibres)

        # Trigger events for when settings are changed
        w = self.widgets["settings"].widgets["timeweighting"].widgets["combobox"]
        w.currentTextChanged.connect(lambda text: self.settings_changed_events())

        # Show/hide next button based on whether fibres are found
        self.fibres_found.connect(self.widgets["buttons"].widgets["next"].show_button)

    def localise_fibres(self):
        """
        Localise fibres by running peak finding step (fibre reconstruction) and
        clustering the fibre-potential-level estimates of fibre locations to identify
        different fibres.

        The localise settings widget allows the user to determine whether fibre
        potential timing is also considered when clustering the fibre potentials.
        """

        # Create progress bar for showing localisation progress
        n_mu = len(self.motor_units_to_analyse)
        self.progress = QProgressDialog("Localising fibres", None, 0, n_mu, parent=self)
        # Ensure that progress dialog closes if GUI window is minimised
        # GUI window will pop up when process finishes and the progress bar closes
        self.progress.setAttribute(Qt.WA_DeleteOnClose, True)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setMinimumDuration(0)

        # Update cluster settings in fibre reconstruction class
        self.reconstruct_model.reconstruct.mu_cluster_settings = (
            self.cluster_settings_model.settings
        )

        # Store number of fibres found
        self.n_fibres: list[int] = []

        # Counter for progress bar
        mu_count = 0

        # Run analysis for each motor unit
        for mu_idx in self.motor_units_to_analyse:
            # Update progress bar label and count
            self.progress.setLabelText(
                f"Localising fibres\nMotor unit {mu_idx + 1} ({mu_count+1}/{n_mu})"
            )
            self.progress.setValue(mu_count)
            QApplication.processEvents()  # Force progress bar to update before proceeding
            mu_count += 1  # Update bar counter value

            # Motor unit
            mu = self.reconstruct_model.reconstruct.found_motor_units.motor_units[mu_idx]

            # Fibre reconstruction (= peak finding)
            # Only run if this analysis has not already been performed (since these
            # settings cannot be modified in the GUI, the results will not change).
            if not mu.analysis_performed["fibres_localised"]:
                print("reconstructing fibres")
                self.reconstruct_model.reconstruct.reconstruct_fibres(mu_idx)
            else:
                print("fibres already reconstructed - skipping")

            # Clustering
            # The implementation of this analysis means that any earlier results will
            # be over-written - do not need to manually delete.
            self.reconstruct_model.reconstruct.mu_cluster_fibre_potentials(mu_idx)

            # Number of fibres found in this motor unit
            self.n_fibres.append(mu.fibre_clustering_results["n_fibre_clusters"])

        # Ensure progress bar closed
        self.progress.setValue(n_mu)
        self.progress.hide()  # Forces to bar to disappear regardless of value

        # Update results
        self.update_results()

        # Emit signal for whether fibres are found
        # Will also update next button
        self.fibres_found.emit(sum(self.n_fibres) > 0)

    def update_results(self):
        """
        Add widgets for displaying results of fibre localisation step.

        """

        # Delete if already present
        w = self.widgets.pop("results", None)
        if w:
            w.deleteLater()

        # If fibres found, add new vis
        if sum(self.n_fibres) > 0:
            # Add results widget (including vis)
            # Start by displaying first motor unit that was analysed
            self.widgets["results"] = FibreLocalisationResultsWidget(
                self.reconstruct_model, self.motor_units_to_analyse, parent=self
            )

            # Add to layout
            self.layout.addWidget(self.widgets["results"], 0, 1, 3, 1)  # span 3 rows

        else:  # If no fibres, display text indicating none found
            self.widgets["results"] = SubsectionTitle("No fibres found", parent=self)

            # Add to layout
            self.layout.addWidget(self.widgets["results"], 0, 1)

    def settings_changed_events(self):
        """
        When any settings changed, 1) enable re-apply button, 2) disable next button,
        and 3) send signal that settings have been changed (for main GUI)

        """

        self.widgets["buttons"].widgets["apply"].setEnabled(True)
        self.widgets["buttons"].widgets["next"].setEnabled(False)
        self.settings_changed.emit()
