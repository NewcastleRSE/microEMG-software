#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widgets for visualising motor unit EMG traces.
"""

from typing import Any

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QSizePolicy,
    QTabWidget,
)
from PySide6.QtGui import QIcon

from microemggui.models.emg import EMGAnalysisReconstructModel
from microemggui.widgets.base import SubsectionTitle, MatplotlibToolbar, WidgetControlButton
from microemggui.icons import icons  # noqa - import allows icon references


# --- Plot widgets ---


class MUEMGOneChannelWidget(QWidget):
    """
    Widget for visualising EMG traces of one motor unit in one channel.
    """

    def __init__(
        self, reconstruct_model: EMGAnalysisReconstructModel, motor_unit_idx: int = 0, parent=None
    ):
        super().__init__(parent)

        self.reconstruct_model = reconstruct_model

        # Initialise blank plot
        self.fig, self.ax = plt.subplots()
        canvas = FigureCanvasQTAgg(self.fig)
        self.widgets: dict[str, Any] = {
            "toolbar": MatplotlibToolbar(canvas, parent=self),
            "canvas": canvas,
        }

        # Update plot with specified motor unit data
        self.update_motor_unit(motor_unit_idx)

        # Add plot to layout and set to expand to fill the available space
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def update_motor_unit(self, motor_unit_idx: int):
        """
        Update plot to display the EMG traces of the specified motor unit.
        Motor unit number starts at 0.
        """

        # Create plot and replace existing axes
        self.ax.cla()  # clear axes
        _, self.ax, _ = self.reconstruct_model.reconstruct.plot_all_potentials_one_channel(
            motor_unit_idx, ax=self.ax
        )
        self.fig.canvas.draw_idle()  # redraw


class MUEMGAllChannelsWidget(QWidget):
    """
    Widget for visualising average (across time) EMG trace of one motor unit in all EMG
    channels.
    """

    def __init__(
        self, reconstruct_model: EMGAnalysisReconstructModel, motor_unit_idx: int = 0, parent=None
    ):
        super().__init__(parent)

        self.reconstruct_model = reconstruct_model

        # Initialise blank plot
        self.fig, self.ax = plt.subplots()
        canvas = FigureCanvasQTAgg(self.fig)
        self.widgets: dict[str, Any] = {
            "toolbar": MatplotlibToolbar(canvas, parent=self),
            "canvas": canvas,
        }

        # Update plot with specified motor unit data
        self.update_motor_unit(motor_unit_idx)

        # Add plot to layout and set to expand to fill the available space
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def update_motor_unit(self, motor_unit_idx: int):
        """
        Update plot to display the EMG traces of the specified motor unit.
        Motor unit number starts at 0.
        """

        # Create plot and replace existing axes
        self.ax.cla()  # clear axes
        _, self.ax = self.reconstruct_model.reconstruct.plot_average_motor_unit_potential(
            motor_unit_idx, ax=self.ax
        )
        self.fig.canvas.draw_idle()  # redraw


class MUVisWidget(QWidget):
    """
    Tabbed widget with visualisations of one motor unit.
    One tab is for single-channel EMG visualisation, and the other tab is for the all
    all channels EMG visualisation.
    """

    def __init__(
        self, reconstruct_model: EMGAnalysisReconstructModel, motor_unit_idx: int = 0, parent=None
    ):
        super().__init__(parent)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "one": MUEMGOneChannelWidget(reconstruct_model, motor_unit_idx, parent=self),
            "all": MUEMGAllChannelsWidget(reconstruct_model, motor_unit_idx, parent=self),
        }

        tab_text = ["One channel", "All channels"]

        # Add to tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("muvistab")  # name for style sheet
        for w, txt in zip(self.widgets.values(), tab_text):
            self.tab_widget.addTab(w, txt)

        # Add to layout
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


# --- Control buttons for viewer ---


class MUEMGArrowsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create button widgets
        self.widgets = {
            "previous": WidgetControlButton(self),
            "next": WidgetControlButton(self),
        }

        # Icons for buttons
        my_icons = ["chevron-left", "chevron-right"]

        # Tooltip text for each button
        tooltip_text = ["Previous motor unit", "Next motor unit"]

        # Set button icons and tooltip text
        for w, ic, txt in zip(self.widgets.values(), my_icons, tooltip_text):
            w.setIcon(QIcon(":/bootstrap/" + ic))
            w.setToolTip(txt)

        # Add to layout
        layout = QHBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


# --- Viewer for motor unit EMG visualisations ---


class MUEMGViewerWidget(QWidget):
    """
    All visualisations for one motor unit, with controls for navigating between motor
    units.
    """

    def __init__(
        self, reconstruct_model: EMGAnalysisReconstructModel, motor_unit_idx: int = 0, parent=None
    ):
        super().__init__(parent)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "arrows": MUEMGArrowsWidget(parent=self),
            "title": SubsectionTitle(f"Motor unit {motor_unit_idx + 1}", parent=self),
            "vis": MUVisWidget(reconstruct_model, motor_unit_idx, parent=self),
        }

        # Add to layout
        layout = QGridLayout()
        layout.addWidget(self.widgets["arrows"], 0, 0)
        layout.addWidget(self.widgets["title"], 0, 1)
        layout.addWidget(self.widgets["vis"], 1, 0, 1, 2)  # Span two columns
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Set title to fill space
        self.widgets["title"].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # TODO: update motor unit
        # TODO: connections to motor unit (arrows and motor unit buttons)
