#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 11:41:14 2024

@author: Gabrielle
"""
from typing import Any

from PySide6.QtWidgets import QWidget, QHBoxLayout, QGridLayout
from PySide6.QtCore import Qt, Signal

from microemggui.models.emg import EMGAnalysisReconstructModel
from microemggui.models.settings import EMGAnalysisMotorUnitClusterSettingsModel
from microemggui.widgets.base import LargePushButton, SectionTitle
from microemggui.widgets.localise.localise_settings import LocaliseSettingsWidget

# TODO: add results widget


# --- Buttons ---


class ApplyLocaliseFibressButton(LargePushButton):
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

    def enable(self):
        """
        Slot to enable button when settings are changed.
        """

        self.setEnabled(True)


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
        # TODO: what is the format of the data if no fibres are found?
        """
        if fibres_found:
            self.show()
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
            "apply": ApplyLocaliseFibressButton(self),
            "next": NextButton(self),
        }

        # Add to layout
        layout = QHBoxLayout()
        layout.addWidget(self.widgets["apply"], alignment=Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.widgets["next"], alignment=Qt.AlignRight | Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


# --- Localise fibres widget ---


class LocaliseFibresWidget(QWidget):
    """
    Widgets for localising fibres step.

    Note that this step combines the "peak finding" and clustering parts of the fibre
    reconstruction analysis. While this approach simplifies the GUI, the downside is
    that trying out different clustering approaches will require re-running the
    fibre reconstruction step.
    TODO: could check if the peak finding step has already been performed and only
    re-run that part if it hasn't?
    """

    # Signal for whether fibres have been found
    fibres_found = Signal(bool)

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
        # Use grid layout with results to right
        layout = QGridLayout()
        row = 0
        col = 0
        for w in self.widgets.values():
            layout.addWidget(w, row, col)
            row += 1

        # Add results widget in second column
        # TODO

        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        # Connections

        # TODO
        # connections to update cluster settings
        # connections to trigger fibre localisation

    def localise_fibres(self):
        """
        Localise fibres by running peak finding step (fibre reconstruction) and
        clustering the fibre-potential-level estimates of fibre locations to identify
        different fibres.

        The localise settings widget allows the user to determine whether fibre
        potential timing is also considered when clustering the fibre potentials.
        """

        # Update cluster settings in fibre reconstruction class
        self.reconstruct_model.reconstruct.mu_cluster_settings = (
            self.cluster_settings_model.settings
        )

        # Run analysis for each motor unit
        for mu_idx in self.motor_units_to_analyse:
            # Fibre reconstruction (= peak finding)
            # TODO: first check if this analysis has already been performed
            self.reconstruct_model.reconstruct.reconstruct_fibres(mu_idx)

            # Clustering
            # TODO: check that existing clustering results will be overwritten by
            # re-running the analysis. If not, need to manually delete first.
            self.reconstruct_model.reconstruct.mu_cluster_fibre_potentials(mu_idx)

            # TODO: check number of fibres found for each MU
