#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widgets for specifying settings for localising fibres
"""

from typing import Any

from PySide6.QtWidgets import QWidget, QVBoxLayout

from microemggui.models.settings import EMGAnalysisMotorUnitClusterSettingsModel
from microemggui.widgets.base import (
    InputLabel,
    InputExplanationLabel,
    InputComboBox,
    SubsectionTitle,
    ExpandingVSpacer,
)

# --- Widgets for settings --- #


class TimeWeightingCombobox(QWidget):
    """
    Combobox and associated labels for setting time weighting ( = time_scale setting)
    when identifying fibres by clustering fibre potential features (location and timing).

    Developer note: If need to add more comboboxes in the future and/or map text options
    to values, see the MUSettingsWidget in findmu.mu_settings and
    EMGAnalysisMotorUnitSettingsModel classes for a more generic approach.
    """

    def __init__(self, cluster_settings: EMGAnalysisMotorUnitClusterSettingsModel, parent=None):
        super().__init__(parent)

        self.setting_name = "time_scale"  # name of setting in cluster settings class

        # Create widgets
        self.widgets: dict[str, Any] = {
            "label": InputLabel("Time weighting", self),
            "explanation": InputExplanationLabel(
                "How much fibre potential timing (in addition to estimate locations) "
                + "contributes to identifying different fibres",
                self,
            ),
            "combobox": InputComboBox(self),
        }

        # Get combobox options from settings model
        self.combobox_values = cluster_settings.options[self.setting_name]
        self.widgets["combobox"].addItems(self.combobox_values)

        # TODO: set to current settings value

        # Layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # TODO: Connect combobox text to settings


# --- All settings ---


class LocaliseSettingsWidget(QWidget):
    """
    Widget for specifying settings for localising muscle fibres.

    Note that this analysis step depends on two groups of settings: the fibre
    reconstruction settings (used for peak finding to identify fibre potentials) and the
    clustering settings (used to cluster the identified fibre potentials and assign them
    to different fibres). At present, only one of the clustering settings is modifiable
    in the GUI and as such, only these settings are passed to this class.

    """

    def __init__(self, cluster_settings: EMGAnalysisMotorUnitClusterSettingsModel, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "title": SubsectionTitle("Settings", parent=self),
            "timeweighting": TimeWeightingCombobox(cluster_settings, parent=self),
        }

        # Layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Spacer at end so extra space is added below settings widgets if window resized
        end_space = ExpandingVSpacer()
        layout.addItem(end_space)

        self.setLayout(layout)
