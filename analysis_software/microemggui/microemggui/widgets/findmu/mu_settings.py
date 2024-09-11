#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for specifying settings for finding motor units.
"""
from typing import Any

from PySide6.QtWidgets import QWidget, QVBoxLayout

from microemggui.models.settings import EMGAnalysisMotorUnitSettingsModel
from microemggui.widgets.base import (
    InputLabel,
    InputExplanationLabel,
    InputComboBox,
    SubsectionTitle,
    ExpandingVSpacer,
)

# --- Widgets for settings --- #


class MUSettingComboboxWidget(QWidget):
    """
    Generic class for motor unit settings input with combobox and labels.
    """

    def __init__(
        self,
        mu_settings: EMGAnalysisMotorUnitSettingsModel,
        setting_name: str,  # setting modified by this widget
        label: str,
        explanation: str,
        parent=None,
    ):
        super().__init__(parent)

        # Setting modified by this widget
        self.setting_name = setting_name

        # Create widgets
        self.widgets: dict[str, Any] = {
            "label": InputLabel(label, self),
            "explanation": InputExplanationLabel(explanation, self),
            "combobox": InputComboBox(self),
        }

        # Get possible combobox values from settings model
        mapping = mu_settings.mapping[self.setting_name]
        self.combobox_values = list(mapping["text2values"].keys())

        # Add combobox options and set current value
        self.widgets["combobox"].addItems(self.combobox_values)
        current_text = mu_settings.get_setting_current_text(self.setting_name)
        self.widgets["combobox"].setCurrentText(current_text)

        # Layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Connect combobox text to settings
        self.widgets["combobox"].currentTextChanged.connect(
            lambda text, setting=self.setting_name: mu_settings.change_setting(setting, text)
        )


# --- All settings ---


class MUSettingsWidget(QWidget):
    """
    Widget for modifying settings for finding motor units.
    """

    def __init__(self, mu_settings: EMGAnalysisMotorUnitSettingsModel, parent=None):
        super().__init__(parent)

        # Create widgets

        mu_sensitivity_w = MUSettingComboboxWidget(
            mu_settings,
            setting_name="sensitivity",
            label="Detection sensitivity",
            explanation="Increasing the sensitivity threshold captures more "
            + "motor units, but may increase false positives.",
            parent=self,
        )

        mu_similarity_w = MUSettingComboboxWidget(
            mu_settings,
            setting_name="similarity",
            label="Motor unit similarity",
            explanation="Increasing the similarity threshold means potentials "
            + "assigned to the same motor unit must be more similar.",
            parent=self,
        )

        self.widgets: dict[str, Any] = {
            "title": SubsectionTitle("Settings"),
            "sensitivity": mu_sensitivity_w,
            "similarity": mu_similarity_w,
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
