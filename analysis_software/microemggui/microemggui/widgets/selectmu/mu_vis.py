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
from PySide6.QtCore import Signal

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
        Motor unit index starts at 0.
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
        Motor unit index starts at 0.
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

    def update_motor_unit(self, motor_unit_idx: int):
        """
        Update plot to display the visualisations of the specified motor unit.
        Motor unit index starts at 0.
        """

        for w in self.widgets.values():
            w.update_motor_unit(motor_unit_idx)


# --- Control buttons for viewer ---


class MUEMGArrowsWidget(QWidget):
    mu_arrow_clicked = Signal(int)

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

        # Increment for each button
        self.button_increments = [-1, 1]

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

        # Connections
        for w, increment in zip(self.widgets.values(), self.button_increments):
            w.clicked.connect(
                lambda checked=None, increment=increment: self.mu_arrow_clicked.emit(increment)
            )

    def emit_increment(self, increment: int):
        """
        When arrow button is clicked, emit signal with the increment for changing the motor
        unit index.

        """
        self.mu_arrow_clicked(increment)


# --- Viewer for motor unit EMG visualisations ---


class MUEMGViewerWidget(QWidget):
    """
    All visualisations for one motor unit, with controls for navigating between motor
    units.
    """

    # Signal for indicating that displayed motor unit has been changed by an increment
    # (i.e., using the arrow buttons)
    motor_unit_idx_changed_from_increment = Signal(int)

    def __init__(
        self, reconstruct_model: EMGAnalysisReconstructModel, motor_unit_idx: int = 0, parent=None
    ):
        super().__init__(parent)

        # Number of motor unit
        self.motor_unit_idx = motor_unit_idx
        self.n_motor_units = reconstruct_model.reconstruct.found_motor_units.n_motor_units

        # Create widgets
        self.widgets: dict[str, Any] = {
            "arrows": MUEMGArrowsWidget(parent=self),
            "title": SubsectionTitle("", parent=self),
            "vis": MUVisWidget(reconstruct_model, motor_unit_idx, parent=self),
        }

        # Update motor unit (will also disable/enable control buttons as needed)
        self.update_motor_unit_idx(motor_unit_idx)

        # Add to layout
        layout = QGridLayout()
        layout.addWidget(self.widgets["arrows"], 0, 0)
        layout.addWidget(self.widgets["title"], 0, 1)
        layout.addWidget(self.widgets["vis"], 1, 0, 1, 2)  # Span two columns
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Set title to fill space
        self.widgets["title"].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Connections
        self.widgets["arrows"].mu_arrow_clicked.connect(self.update_motor_unit_idx_from_increment)

    def update_motor_unit_idx(self, motor_unit_idx: int):
        """
        Slot for signal with new motor unit index.
        Updates the index of the motor unit to visualise. Triggers plot and text updates
        using update_motor_unit.
        """

        self.motor_unit_idx = motor_unit_idx

        # Enable/disable arrow buttons based on index
        # Ensures these buttons never request an out-of-range index
        self.widgets["arrows"].widgets["previous"].setEnabled(self.motor_unit_idx > 0)
        self.widgets["arrows"].widgets["next"].setEnabled(
            self.motor_unit_idx < (self.n_motor_units - 1)
        )

        # Update vis and text
        self.update_motor_unit()

    def update_motor_unit_idx_from_increment(self, increment: int):
        """
        Update the motor unit index based on requested increment and trigger downstream
        updates.
        """
        motor_unit_idx = self.motor_unit_idx + increment  # new index
        self.update_motor_unit_idx(motor_unit_idx)
        self.motor_unit_idx_changed_from_increment.emit(motor_unit_idx)  # signal for MU buttons

    def update_motor_unit(self):
        """
        Update visualised motor unit.

        """

        self.widgets["title"].setText(f"Motor unit {self.motor_unit_idx + 1}")
        self.widgets["vis"].update_motor_unit(self.motor_unit_idx)
