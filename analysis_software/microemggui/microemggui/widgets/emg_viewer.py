"""
Widget for viewing EMG time series.

Current icons from https://icons.getbootstrap.com/

TODO: make model for EMGData; pass to widgets
TODO: voltage controls
TODO: amend time controls
TODO: signals and slots
TODO: layout in final widget
"""

import os

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QIcon

from microemggui.widgets.base import (
    InputInlineLabel,
    # InputWarningLabel,
    InputComboBox,
    InputLineEdit,
    InputInlineText,
    ExpandingSpacer,
)

# --- Plot ---


class EMGPlot(FigureCanvasQTAgg):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# --- Widgets for controlling time window ---


class StartTimeWidget(QWidget):
    # Widget for specifying start time of window for viewing EMG data

    # TODO: add validation and warning for time based on size of EMG data

    def __init__(self, parent=None):
        super().__init__(parent)

        self.widgets = {
            "start_label": InputInlineLabel("Start: ", self),  # Widget label
            "time_lineedit": InputLineEdit(self),  # Line edit box
            "s_label": InputInlineText("seconds", self),  # Label for units
        }

        # Add widgets to horizontal layout
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.addItem(ExpandingSpacer())  # add spacer
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class WindowSizeWidget(QWidget):
    # Widget for specifying the window size (i.e., time segment duration) for viewing
    # EMG data

    def __init__(self, parent=None):
        super().__init__(parent)

        self.widgets = {
            "window_label": InputInlineLabel("Window size: ", self),
            "window_combobox": InputComboBox(self),
            "s_label": InputInlineText("seconds", self),
        }

        # Add options for combobox
        window_options = ["0.01", "0.1", "1", "10", "100"]
        self.widgets["window_combobox"].addItems(window_options)

        # Add to layout
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.addItem(ExpandingSpacer())  # add spacer
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class EMGScrollWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Buttons for moving backwards and forwards through time series plot

        # TODO: create class for icon buttons

        self.widgets = {
            "skip_start_button": QPushButton(self),
            "previous_button": QPushButton(self),
            "next_button": QPushButton(self),
            "skip_end_button": QPushButton(self),
        }

        # Icons for buttons
        # TODO: set resource path or otherwise define path for icons
        icon_dir = os.path.join(
            "analysis_software",
            "microemggui",
            "microemggui",
            "icons",
            "bootstrap-icons-1.11.3",
        )
        icons = [
            "chevron-bar-left.svg",
            "chevron-left.svg",
            "chevron-right.svg",
            "chevron-bar-right.svg",
        ]
        for w, ic in zip(self.widgets.values(), icons):
            w.setIcon(QIcon(os.path.join(icon_dir, ic)))

        # Add to layout
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.addItem(ExpandingSpacer())  # add spacer
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


# --- Widget for viewer ---


class EMGViewerWidget(QWidget):
    def __init__(self, fig, parent=None):
        super().__init__(parent)

        self.widgets = {
            "plot": EMGPlot(fig),
            "start": StartTimeWidget(parent=self),
            "window": WindowSizeWidget(parent=self),
            "scroll": EMGScrollWidget(parent=self),
        }
        layout = QVBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)

        self.setLayout(layout)
