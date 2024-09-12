#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for exporting results of the microEMG analysis.
"""
from typing import Any
import logging
import os
from datetime import datetime

from PySide6.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from PySide6.QtCore import Qt

from microemggui.models.emg import EMGAnalysisReconstructModel

from microemggui.widgets.base import (
    SmallPushButton,
    LargePushButton,
    InputWarningLabel,
    MessageLabel,
    HighlightedLabel,
    SubsectionTitle,
    SectionTitle,
    ExpandingVSpacer,
    CheckBoxRegular,
)

# Logger
logger = logging.getLogger("microemggui.export")

# --- Button for export ---


class ExportButton(LargePushButton):
    """
    Button for exporting results and settings.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Export")


# --- Widgets in export widget ---


class ExportSettingsWidget(QWidget):
    """
    Widget for specifying export settings:
        Checkbox for whether to save motor unit potential EMG.
        Button for choosing location.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "title": SubsectionTitle("Export options", self),
            "checkbox_mups": CheckBoxRegular(
                "Save EMG of motor unit potentials (will create a large file!)", self
            ),
            "button_folder": SmallPushButton(self),
            "text_path": MessageLabel("", self),
        }

        # Button settings
        self.widgets["button_folder"].setText("Choose folder")
        self.widgets["button_folder"].setToolTip("Choose folder for storing results")

        # Add to layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.addItem(ExpandingVSpacer())  # spacer
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)  # increase spacing between widgets
        layout.setAlignment(Qt.AlignLeft)
        self.setLayout(layout)


# --- Export widget ----


class ExportWidget(QWidget):
    """
    Widget for exporting the results and settings of the microEMG analysis.

    Results can be exported at any point once a EMGAnalysisReconstructModel instance is
    created, regardless of whether all analyses have been performed. In the main GUI,
    this export widget is provided once motor units have been found. Note that the
    settings will be included for all analysis steps, regardless of whether those steps
    have been run, because settings are added when EMGAnalysisReconstruct is created.
    """

    def __init__(self, reconstruct_model: EMGAnalysisReconstructModel, parent=None):
        super().__init__(parent)

        # Analysis results
        self.reconstruct_model = reconstruct_model

        # Folder in which to save results (none specified initially)
        self.export_path = ""
        self.export_folder = ""

        # Whether to save motor unit potential EMG
        self.save_mup_emg = False

        # Create widgets
        self.widgets: dict[str, Any] = {
            "title": SectionTitle("Export", self),
            "settings": ExportSettingsWidget(self),
            "success": HighlightedLabel("Results saved!", self),
            "fail": InputWarningLabel("", self),
            "button": ExportButton(self),
        }

        # Button initially disabled (need to choose folder)
        self.widgets["button"].setEnabled(False)

        # Hide success/fail messages
        self.widgets["success"].hide()
        self.widgets["fail"].hide()

        # Update text for export location
        self.update_path_text()

        # Add to layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(20, 5, 20, 20)
        self.setLayout(layout)

        # Connections
        self.widgets["settings"].widgets["button_folder"].clicked.connect(
            self.browse_for_export_folder
        )
        self.widgets["settings"].widgets["checkbox_mups"].toggled.connect(self.update_save_mup_emg)
        self.widgets["button"].clicked.connect(self.export_results)

    def browse_for_export_folder(self):
        """
        Choose folder in which to save results using file browser.
        """

        self.export_path = QFileDialog.getExistingDirectory(
            self, "Select folder for storing results", ""
        )

        # Update widgets that depend on export path
        if self.export_path:
            logger.info(f"Export path choosen: {self.export_path}")

            # Create name of export folder (will be saved as export_folder attribute)
            self.create_name_of_export_folder()

            # Enable export button
            self.widgets["button"].setEnabled(True)

        else:  # if cancel, path is empty
            # Disable export button
            self.widgets["button"].setEnabled(False)

        # Update message about export location
        self.update_path_text()

    def update_path_text(self):
        """
        Update message with export location (or hide if no location specified).
        """

        if self.export_path:
            # Show save location
            self.widgets["settings"].widgets["text_path"].setText(
                f"Results will be saved in {os.path.join(self.export_path, self.export_folder)}"
            )
            self.widgets["settings"].widgets["text_path"].show()

            # Hide success and fail messages
            self.widgets["success"].hide()
            self.widgets["fail"].hide()

        else:
            # Hide message with save location
            self.widgets["settings"].widgets["text_path"].hide()

    def create_name_of_export_folder(self):
        """
        Create and save name for export folder with timestamp.
        """

        export_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.export_folder = f"microEMG_{export_time}"

    def update_save_mup_emg(self, checked: bool):
        """
        Change attribute indicating whether motor unit potential EMG should be saved.
        Slot for checkbox.

        """

        self.save_mup_emg = checked

        # Also enable export button since settings have been changed
        self.widgets["button"].setEnabled(True)
        self.widgets["success"].hide()
        self.widgets["fail"].hide()

    def export_results(self):
        """
        Export microEMG analysis results and settings to specified folder.
        Slot for export button.
        """

        # Create folder for results
        full_export_path = os.path.join(self.export_path, self.export_folder)
        os.makedirs(full_export_path, exist_ok=True)

        # File name for json export
        json_filename = "microEMG_results_and_settings.json"

        # Try to save
        # Note that save failed message will be shown if either json or figure save fails.
        # We try saving the json first as that is the most likely to fail.
        try:
            # Export results/settings as JSON
            json_path = os.path.join(full_export_path, json_filename)
            self.reconstruct_model.reconstruct.save_all_results_and_settings(
                filename=json_path, save_all_spikes=self.save_mup_emg
            )

            # Log
            logger.info(f"Saved microEMG results and settings in JSON file {json_path}")

            # Create figure of fibre localisation
            motor_units = self.reconstruct_model.reconstruct.found_motor_units
            fig, ax = motor_units.plot_fibre_locations(
                "fibres", motor_unit_idx=None, figsize=(10, 2)
            )
            fig.set_tight_layout(True)
            ax.set_title("Fibre locations in all motor units", fontsize=14, fontweight="bold")

            # Export figure as png (high res) and svg
            png_dpi = 600  # png resolution
            plot_filename = "fibre_localisation"
            plot_path = os.path.join(full_export_path, plot_filename)

            fig.savefig(plot_path + ".png", dpi=png_dpi)
            logger.info(f"Exported fibre localisation plot ({plot_path + '.png'})")

            fig.savefig(plot_path + ".svg")
            logger.info(f"Exported fibre localisation plot ({plot_path + '.svg'})")

            # More exports can be added here if needed - recommend adding logs for each one.
            # May need to check that results have been added before trying to plot certain
            # figures.

            # Show message that save was successful
            self.widgets["success"].show()

            # Disable export button
            self.widgets["button"].setEnabled(False)

        except Exception as e:
            # Update fail message with error
            self.widgets["fail"].setText(f"Save failed: {e}")
            self.widgets["fail"].show()
            logger.exception("Could not save microEMG results and settings.")

            # Remove folder if empty
            try:
                os.rmdir(full_export_path)
                logger.info("Deleted empty export folder.")

            except Exception:
                logger.exception(
                    "Could not delete export folder (folder not empty - partial save)."
                )
