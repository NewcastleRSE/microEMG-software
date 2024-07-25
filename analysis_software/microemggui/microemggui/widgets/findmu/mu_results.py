#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for plot of results of the find motor units analysis step.
Analysis results in a raster plot of the MUP times for each found MU.
"""

from typing import Any

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from microemggui.models.emg import EMGAnalysisReconstructModel
from microemggui.widgets.base import SubsectionTitle, MatplotlibToolbar


# --- Plot widget ---


# TODO: fix axis limits and tick mark locations when only one MU
class MURasterWidget(QWidget):
    def __init__(self, reconstruct_model: EMGAnalysisReconstructModel, parent=None):
        super().__init__(parent)

        # Initialise blank plot
        self.fig, self.ax = plt.subplots()
        canvas = FigureCanvasQTAgg(self.fig)
        self.widgets: dict[str, Any] = {
            "toolbar": MatplotlibToolbar(canvas, parent=self),
            "canvas": canvas,
        }

        # Update plot using MU data (or hide plot if no MU)
        self.update_reconstruct(reconstruct_model)

        # Add plot to layout and set to expand to fill the available space
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def update_reconstruct(self, reconstruct_model):
        """
        Update reconstruction analysis data used to make plot and the corresponding plot.
        """

        if reconstruct_model.reconstruct.found_motor_units:  # if MU analysis has been run
            # Number of motor units
            n_mu = reconstruct_model.reconstruct.found_motor_units.n_motor_units

            if n_mu == 0:  # If no MU, hide widget
                self.hide()

            else:  # Otherwise, update plot
                self.show()  # show widget
                self.ax.cla()  # clear axes

                # Make new plot
                _, self.ax = reconstruct_model.reconstruct.plot_motor_units_raster(ax=self.ax)

                self.fig.canvas.draw_idle()  # redraw
        else:
            self.hide()  # hide if analysis has not been run


# --- Results with title ---


class MUResultsWidget(QWidget):
    def __init__(self, reconstruct_model: EMGAnalysisReconstructModel, parent=None):
        super().__init__(parent)

        # Initial widget: placeholder for title
        self.widgets: dict[str, Any] = {
            "title": SubsectionTitle("", parent=self),
            "plot": MURasterWidget(reconstruct_model, parent=self),
        }

        # Layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Expand to fill available space
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def update_reconstruct(self, reconstruct_model):
        """
        Update title and plot with reconstruction analysis results.
        """

        # Number of motor units found
        n_mu = reconstruct_model.reconstruct.found_motor_units.n_motor_units

        # Update title text
        self.widgets["title"].setText(f"Found {n_mu} motor units.")

        # Update plot
        self.widgets["plot"].update_reconstruct(reconstruct_model)
