#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widgets for jitter analysis visualisations
"""

from typing import Any

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)

from microemggui.models.emg import EMGAnalysisReconstructModel
from microemggui.widgets.base import (
    MatplotlibToolbar,
    InputComboBox,
    InputInlineLabel,
    ExpandingHSpacer,
)

# --- All fibres ---

# TODO: colormaps
# TODO: move fibre comboboxes to same row


class JitterAllFibrePlotsWidget(QWidget):
    """
    Widget for displaying heatmaps of jitter MCD and sample sizes of all fibre pairs
    for the specified motor unit.
    """

    def __init__(
        self, reconstruct_model: EMGAnalysisReconstructModel, motor_unit_idx: int, parent=None
    ):
        super().__init__(parent)

        self.reconstruct_model = reconstruct_model

        # Create plot with two suplots and corresponding canvas
        self.fig, self.axs = plt.subplots(2, 1, figsize=(5, 10))
        self.fig.dpi = 100
        self.fig.set_tight_layout(True)  # prevents overlap in subplots
        self.update_motor_unit(motor_unit_idx)  # add plots for specified motor unit
        canvas = FigureCanvasQTAgg(self.fig)

        # Create widgets: toolbar and canvas
        self.widgets: dict[str, Any] = {
            "toolbar": MatplotlibToolbar(canvas, parent=self),
            "canvas": canvas,
        }

        # Add widgets to layout and set to expand to fill the available space
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def update_motor_unit(self, motor_unit_idx: int):
        """
        Update plots to display the jitter heatmaps for the specified motor unit.
        Motor unit index counts from 0.
        """

        # Motor unit
        mu = self.reconstruct_model.reconstruct.found_motor_units.motor_units[motor_unit_idx]

        # First plot is MCD
        if self.axs[0].collections:
            self.axs[0].collections[0].colorbar.remove()  # have to remove colorbar separately
        self.axs[0].cla()
        _, self.axs[0] = mu.plot_jitter_heat_plot(median=False, ax=self.axs[0])

        # Second plot is sample sizes
        if self.axs[1].collections:
            self.axs[1].collections[0].colorbar.remove()  # have to remove colorbar separately
        self.axs[1].cla()
        _, self.axs[1] = mu.plot_jitter_totals_heat_plot(percent=False, ax=self.axs[1])

        self.fig.canvas.draw_idle()  # redraw


# --- Fibre pair ---


class JitterFibrePairPlotWidget(QWidget):
    """
    Widget for visualising jitter of one fibre pair
    """

    def __init__(
        self, reconstruct_model: EMGAnalysisReconstructModel, motor_unit_idx: int, parent=None
    ):
        super().__init__(parent)

        # Reconstruct model and initial motor unit
        self.reconstruct_model = reconstruct_model
        self.motor_unit_idx = motor_unit_idx

        # Initial fibres to plot (none)
        self.fibres: list[None | int] = [None, None]

        # Initial layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Make plot and associated widgets, and add to layout
        # (do not update axes in this widget since figure has multiple axes)
        self.widgets: dict[str, Any] = {}  # initial dictionary for widgets
        self.update_plot()

    def update_motor_unit(self, motor_unit_idx: int):
        """
        Update motor unit.
        """

        self.motor_unit_idx = motor_unit_idx  # update motor unit
        self.fibres = [None, None]  # reset fibres
        self.update_plot()  # trigger plot update

    def update_fibre(self, fibre: str, fibre_idx: int):
        """
        Update the plotted fibres.
        fibre is the text from the combobox, and fibre_idx is 0 or 1 (for first or
        second fibre of the fibre pair)
        """

        if fibre:  # if not an empty string, convert to int and store
            self.fibres[fibre_idx] = int(fibre) - 1  # subtract 1 to convert back to indices
            print(self.fibres)
        else:
            self.fibres[fibre_idx] = None
            print(self.fibres)

        # Trigger plot update
        self.update_plot()

    def update_plot(self):
        """
        Update plot after changing motor unit and/or fibre pair.

        """

        figsize = (5, 10)  # to prevent plot from changing size

        # Get motor unit
        mu = self.reconstruct_model.reconstruct.found_motor_units.motor_units[self.motor_unit_idx]

        # Plot jitter of specified fibre pair if a valid pair (not None and not equal)
        if (
            (self.fibres[0] is not None)
            and (self.fibres[1] is not None)
            and (self.fibres[0] != self.fibres[1])
        ):
            fig, _ = mu.plot_jitter_fibre_pair_EMG_and_times(
                self.fibres[0], self.fibres[1], figsize=figsize
            )

            # Check if plotted (will not plot if jitter not computed for that pair)
            if fig:
                self.fig = fig
                self.fig.set_tight_layout(True)
            else:  # otherwise, blank plot
                self.fig, ax = plt.subplots(figsize=figsize)
                ax.set_axis_off()
        else:  # otherwise, blank plot
            self.fig, ax = plt.subplots(figsize=figsize)
            ax.set_axis_off()

        # Delete existing figure
        for w in self.widgets.values():
            w.deleteLater()

        # New figure
        canvas = FigureCanvasQTAgg(self.fig)
        self.widgets: dict[str, Any] = {
            "toolbar": MatplotlibToolbar(canvas, parent=self),
            "canvas": canvas,
        }

        # Add plot to layout and set to expand to fill the available space
        for w in self.widgets.values():
            self.layout.addWidget(w)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


class JitterFibrePairComboboxWidget(QWidget):
    """
    Comboboxes for choosing fibre pair to visualise.
    """

    def __init__(
        self, reconstruct_model: EMGAnalysisReconstructModel, motor_unit_idx: int, parent=None
    ):
        super().__init__(parent)

        self.reconstruct_model = reconstruct_model

        # Create widgets
        self.widgets: dict[str, Any] = {
            "label1": InputInlineLabel("1st fibre (trigger):", parent=self),
            "combobox1": InputComboBox(parent=self),
            "label2": InputInlineLabel("2nd fibre:", parent=self),
            "combobox2": InputComboBox(parent=self),
        }

        # Update to initial motor unit
        self.update_motor_unit(motor_unit_idx)

        # Add to layout
        layout = QHBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.addItem(ExpandingHSpacer())  # spacer to push to left
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def update_motor_unit(self, motor_unit_idx: int):
        """
        Update motor unit (will change fibre combobox options).
        """

        # Get fibre options for that motor unit
        mu = self.reconstruct_model.reconstruct.found_motor_units.motor_units[motor_unit_idx]
        n_fibres = mu.fibre_clustering_results["n_fibre_clusters"]
        fibre_list = list(range(n_fibres))
        fibre_list = [str(i + 1) for i in fibre_list]  # + 1 for labels
        fibre_list = [""] + fibre_list  # include no selection - will be default

        # Add options to comboboxes
        combobox_w_names = ["combobox1", "combobox2"]
        for name in combobox_w_names:
            self.widgets[name].clear()  # remove existing options
            self.widgets[name].addItems(fibre_list)
            self.widgets[name].setCurrentText("")


class JitterFibrePairVisWidget(QWidget):
    """
    Widget for selecting fibre pair and visualising jitter results of that fibre pair.
    """

    def __init__(
        self, reconstruct_model: EMGAnalysisReconstructModel, motor_unit_idx: int, parent=None
    ):
        super().__init__(parent)

        self.reconstruct_model = reconstruct_model

        # Create widgets
        self.widgets: dict[str, Any] = {
            "comboboxes": JitterFibrePairComboboxWidget(
                self.reconstruct_model, motor_unit_idx, parent=self
            ),
            "plot": JitterFibrePairPlotWidget(self.reconstruct_model, motor_unit_idx, parent=self),
        }

        # Add to layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Connect fibre comboboxes to visualisation
        combobox_w_names = ["combobox1", "combobox2"]
        fibre_idx = [0, 1]  # corresponding fibre
        for name, idx in zip(combobox_w_names, fibre_idx):
            self.widgets["comboboxes"].widgets[name].currentTextChanged.connect(
                lambda text, idx=idx: self.widgets["plot"].update_fibre(text, idx)
            )

    def update_motor_unit(self, motor_unit_idx):
        """
        Update the visualised motor unit.
        """
        for w in self.widgets.values():
            w.update_motor_unit(motor_unit_idx)
