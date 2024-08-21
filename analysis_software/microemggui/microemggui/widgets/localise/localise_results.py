#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widgets for displaying results (including visualisations) of fibre localisation step.

For matplotlib figures: note that changing the dpi will distort the plot rather than
simply changing the plot's resolution (e.g., plot markers and font sizes will greatly
change). These plots are all designed for dpi = 100.
"""

from typing import Any

# import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    # QGridLayout,
    # QHBoxLayout,
    QSizePolicy,
    # QTabWidget,
)

from microemggui.models.emg import EMGAnalysisReconstructModel
from microemggui.widgets.base import MatplotlibToolbar  # , SubsectionTitle


# --- Plot widgets ---


class AllFibreLocationsWidgets(QWidget):
    """
    Widget for visualising the locations of all fibres across all analysed motor units.
    """

    def __init__(self, reconstruct_model: EMGAnalysisReconstructModel, parent=None):
        super().__init__(parent)
        # TODO: fix size issue (too big)
        self.reconstruct_model = reconstruct_model

        # Create plot and corresponding canvas
        motor_units = self.reconstruct_model.reconstruct.found_motor_units
        self.fig, self.ax = motor_units.plot_fibre_locations(
            "fibres", motor_unit_idx=None, dpi=100
        )
        self.fig.set_tight_layout(True)  # Prevents window from cutting off legend
        canvas = FigureCanvasQTAgg(self.fig)

        # Create widgets: toolbar and canvas
        self.widgets: dict[str, Any] = {
            "toolbar": MatplotlibToolbar(canvas, parent=self),
            "canvas": canvas,
        }

        # Add plot to layout and set to expand to fill the available space
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
