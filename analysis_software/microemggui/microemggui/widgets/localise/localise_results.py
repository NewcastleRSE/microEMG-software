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
    # QHBoxLayout,
    QSizePolicy,
    QTabWidget,
)

from microemggui.models.emg import EMGAnalysisReconstructModel
from microemggui.widgets.base import (
    MatplotlibToolbar,
    ResultsLabel,
    SubsectionTitle,
    ExpandingVSpacer,
)

# --- Plot widgets for results across all motor units ---


class AllFibreLocationsWidget(QWidget):
    """
    Widget for visualising the locations of all fibres across all analysed motor units.
    """

    def __init__(self, reconstruct_model: EMGAnalysisReconstructModel, parent=None):
        super().__init__(parent)

        self.reconstruct_model = reconstruct_model

        # Create plot and corresponding canvas
        motor_units = self.reconstruct_model.reconstruct.found_motor_units
        self.fig, self.ax = motor_units.plot_fibre_locations(
            "fibres", motor_unit_idx=None, dpi=100, figsize=(10, 2)
        )
        self.fig.set_tight_layout(True)  # Prevents window from cutting off legend
        self.ax.set_title("Fibre locations in all motor units", fontsize=14, fontweight="bold")
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


# --- Plot and summary measure widgets for results within each motor unit ---


class MUFibreLocationsSummary(QWidget):
    """
    Widget for displaying summary statistics/measures for the fibre localisation results
    of one motor unit.
    """

    def __init__(
        self, reconstruct_model: EMGAnalysisReconstructModel, motor_unit_idx: int, parent=None
    ):
        super().__init__(parent)

        self.reconstruct_model = reconstruct_model

        # Create placeholder widgets (text will be updated by update_motor_unit)
        self.widgets: dict[str, Any] = {"n_fibres": ResultsLabel(parent=None)}

        # Update text for specified motor unit
        self.update_motor_unit(motor_unit_idx)

        # Add to layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.addItem(ExpandingVSpacer())  # Space so white space is at bottom
        layout.setContentsMargins(10, 0, 0, 0)
        self.setLayout(layout)

    def update_motor_unit(self, motor_unit_idx: int):
        """
        Update text to display results for the specified motor unit.
        """

        # Get relevant labels and statistics from motor unit
        mu = self.reconstruct_model.reconstruct.found_motor_units.motor_units[motor_unit_idx]
        n_fibres = mu.fibre_clustering_results["n_fibre_clusters"]

        # Text
        n_fibres_text = f"<b>Number of fibres:</b> {n_fibres}"

        self.widgets["n_fibres"].setText(n_fibres_text)


# all fibre locations

# 3d: clustered potentials

# 3d: all potentials


class MUFibreLocationsWidget(QWidget):
    """
    Stacked widget for displaying summary measures and visualisations for the fibre
    localisation results of one motor unit.
    """

    def __init__(
        self, reconstruct_model: EMGAnalysisReconstructModel, motor_unit_idx: int = 0, parent=None
    ):
        super().__init__(parent)

        self.reconstruct_model = reconstruct_model

        # Create widgets
        self.widgets: dict[str, Any] = {
            "summary": MUFibreLocationsSummary(self.reconstruct_model, motor_unit_idx, parent=self)
        }

        # Corresponding tab labels
        tab_text = [
            "Summary"
        ]  # , "Fibre locations", "Clustered fibre potentials", "All fibre potentials"]

        # Add to tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("mufibretab")  # name for style sheet
        for w, txt in zip(self.widgets.values(), tab_text):
            self.tab_widget.addTab(w, txt)

        # Add to layout
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def update_motor_unit(self, motor_unit_idx: int):
        """
        Update text and plots to display the results of the specified motor unit.
        Motor unit index starts at 0.
        """

        for w in self.widgets.values():
            w.update_motor_unit(motor_unit_idx)


# --- Widget for changing motor unit ---


# --- Widget for all results (within and across motor units) ---


class FibreLocalisationResultsWidget(QWidget):
    """
    Displays plots and summary measures for fibre localisation.

    The top section visualises results across all motor units, while the bottom section
    is a stacked widget that provides results within one specified motor unit.
    """

    def __init__(
        self, reconstruct_model: EMGAnalysisReconstructModel, motor_unit_idx: int = 0, parent=None
    ):
        super().__init__(parent)

        self.reconstruct_model = reconstruct_model

        # Create widgets
        # TODO: change "onetitle" to dropdown for changing motor unit
        self.widgets: dict[str, Any] = {
            "all_title": SubsectionTitle("All motor units", parent=self),
            "all": AllFibreLocationsWidget(self.reconstruct_model, parent=self),
            "one_title": SubsectionTitle("Motor unit", parent=self),
            "one": MUFibreLocationsWidget(self.reconstruct_model, motor_unit_idx, parent=self),
        }

        # Add to layout
        # Stretch factors so bottom results widgets are twice as high as top results
        layout_stretch = [0, 1, 0, 2]
        layout = QVBoxLayout()
        for w, s in zip(self.widgets.values(), layout_stretch):
            layout.addWidget(w, stretch=s)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # TODO: connection for updating motor unit (will need to subtract one for idx)

    # def update_motor_unit(self, motor_unit_idx: idx)
