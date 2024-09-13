#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widgets for visualising motor unit EMG traces.

For matplotlib figures: note that changing the dpi will distort the plot rather than
simply changing the plot's resolution (e.g., plot markers and font sizes will greatly
change). These plots are all designed for dpi = 100.
"""

from typing import Any

from palettable.cartocolors.qualitative import Prism_10
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
from PySide6.QtCore import Qt, Signal

from microemggui.models.emg import EMGAnalysisReconstructModel
from microemggui.widgets.base import SubsectionTitle, MatplotlibToolbar, WidgetControlButton
from microemggui.widgets.emg_viewer import EMGGainWidget
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
        self.fig.set_tight_layout(True)
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
            motor_unit_idx, ax=self.ax, dpi=100
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

        # Original settings for plot
        self.offset = 300
        self.motor_unit_idx = motor_unit_idx

        # Initialise blank plot
        self.fig, self.ax = plt.subplots()
        self.fig.set_tight_layout(True)
        canvas = FigureCanvasQTAgg(self.fig)
        self.widgets: dict[str, Any] = {
            "toolbar": MatplotlibToolbar(canvas, parent=self),
            "canvas": canvas,
        }

        # Update plot with motor unit and offset
        self.update_plot()

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

        # Update motor unit
        self.motor_unit_idx = motor_unit_idx

        # Update plot
        self.update_plot()

    def scale_offset(self, scale: float):
        """
        Slot for buttons that scale amplitude of plotted lines (via offset parameter).
        """

        # Update offset by scaling by scale value
        self.offset = self.offset / scale

        # Update plot
        self.update_plot()

    def update_plot(self):
        """
        Update plot using specified motor unit and offset.
        """

        # Create plot and replace existing axes
        self.ax.cla()  # clear axes
        _, self.ax = self.reconstruct_model.reconstruct.plot_average_motor_unit_potential(
            self.motor_unit_idx, ax=self.ax, dpi=100, clrs=Prism_10.mpl_colors, offset=self.offset
        )
        self.fig.canvas.draw_idle()  # redraw


class MUEMGAllChannelsWithGainWidget(QWidget):
    """
    MUEMGAllChannelsWidget with controls for modifying signal gain (amplitude).
    """

    def __init__(
        self, reconstruct_model: EMGAnalysisReconstructModel, motor_unit_idx: int = 0, parent=None
    ):
        super().__init__(parent)

        # Widgets
        self.plot_widget = MUEMGAllChannelsWidget(reconstruct_model, motor_unit_idx, parent=self)
        self.gain_widget = EMGGainWidget(self.plot_widget)

        # Add to layout
        layout = QHBoxLayout()
        layout.addWidget(self.gain_widget)
        layout.addWidget(self.plot_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Connections are create in gain widget
        # Plot widget needs to have a scale_offset method for these connections

    def update_motor_unit(self, motor_unit_idx: int):
        """
        Update plot to display the EMG traces of the specified motor unit.
        Motor unit index starts at 0.
        """

        # Handled by method in plot widget
        self.plot_widget.update_motor_unit(motor_unit_idx)


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
            "all": MUEMGAllChannelsWithGainWidget(reconstruct_model, motor_unit_idx, parent=self),
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
    """
    Arrow buttons for navigating through motor units.
    """

    # Signal for when an arrow is clicked with the amount that the motor unit number
    # should be incremented (-1 if left arrow, +1 if right arrow)
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

        # Shortcut keys
        shortcuts = [Qt.Key.Key_Left, Qt.Key.Key_Right]

        # Increment for each button
        self.button_increments = [-1, 1]

        # Set button icons and tooltip text
        for w, ic, txt, sc in zip(self.widgets.values(), my_icons, tooltip_text, shortcuts):
            w.setIcon(QIcon(":/bootstrap/" + ic))
            w.setToolTip(txt)
            w.setShortcut(sc)

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

        # Reconstruction data and number of motor units
        self.reconstruct_model = reconstruct_model
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

        # Number of potentials
        mu = self.reconstruct_model.reconstruct.found_motor_units.motor_units[self.motor_unit_idx]
        n_potentials = mu.n_potentials

        # Update title with number of motor units and potentials
        self.widgets["title"].setText(
            f"Motor unit {self.motor_unit_idx + 1} " + f"({n_potentials} potentials)"
        )

        # Update visualisations
        self.widgets["vis"].update_motor_unit(self.motor_unit_idx)
