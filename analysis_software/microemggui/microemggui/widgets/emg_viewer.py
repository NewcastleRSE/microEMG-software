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

from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QSlider,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QSizePolicy,
)
from PySide6.QtGui import QIcon

from PySide6.QtCore import Qt

from microemggui.widgets.base import (
    InputInlineLabel,
    # InputWarningLabel,
    InputComboBox,
    # InputLineEdit,
    InputInlineText,
    # ExpandingSpacer,
    ExpandingVSpacer,
)

# --- Plot ---


class EMGPlot(FigureCanvasQTAgg):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EMGPlotWidget(QWidget):
    def __init__(self, fig, parent=None):
        super().__init__(parent)
        self.plot = EMGPlot(fig)

        layout = QVBoxLayout()
        layout.addWidget(self.plot)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


# --- Widgets for controlling time window ---

"""
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
"""


class EMGWindowSizeWidget(QWidget):
    # Widget for specifying the window size (i.e., time segment duration) for viewing
    # EMG data

    def __init__(self, parent=None):
        super().__init__(parent)

        self.widgets = {
            # "window_label": InputInlineLabel("Window size: ", self),
            "window_combobox": InputComboBox(self),
            # "s_label": InputInlineText("seconds", self),
        }

        # Add options for combobox
        self.options = {}
        self.options["values"] = [10, 100, 1, 2, 10]
        self.options["units"] = ["ms", "ms", "s", "s", "s"]
        div_text = "divisions"
        self.options["text"] = [
            " ".join([str(val), unit, div_text])
            for (val, unit) in zip(self.options["values"], self.options["units"])
        ]
        self.widgets["window_combobox"].addItems(self.options["text"])

        # Add to layout
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class EMGArrowsWidget(QWidget):
    # Arrow buttons for moving backwards and forwards through time series plot

    def __init__(self, parent=None):
        super().__init__(parent)
        # TODO: create class for icon buttons

        """
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
        """
        self.widgets = {
            "previous_fast": QPushButton(self),
            "previous": QPushButton(self),
            "next": QPushButton(self),
            "next_fast": QPushButton(self),
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
            "rewind.svg",
            "caret-left.svg",
            "caret-right.svg",
            "fast-forward.svg",
        ]

        # button_skip = [-10, -1, 1, 10]
        for w, ic in zip(self.widgets.values(), icons):
            w.setIcon(QIcon(os.path.join(icon_dir, ic)))

        # Add to layout
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)


class EMGStartTimeWidget(QWidget):
    # Slider for changing time in EMG Viewer
    # TODO: consider custom slider class if need multiple sliders with different styles
    def __init__(self, parent=None):
        super().__init__(parent)

        self.widgets = {
            "label": InputInlineLabel("Start time: ", self),
            "time": InputInlineText("00:00", self),
            "slider": QSlider(Qt.Horizontal, self),
        }

        self.widgets["slider"].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Add to layout
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class EMGTimeControlsWidget(QWidget):
    # Controls for changing time in EMG Viewer
    def __init__(self, parent=None):
        super().__init__(parent)

        self.widgets = {
            "arrows": EMGArrowsWidget(parent=self),
            "window": EMGWindowSizeWidget(parent=self),
            "starttime": EMGStartTimeWidget(parent=self),
        }
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        self.setLayout(layout)


# --- Widgets for controlling plotted signal amplitude ---


class EMGGainWidget(QWidget):
    # Controls for controlling plotted signal amplitude (gain)

    def __init__(self, parent=None):
        super().__init__(parent)

        # TODO: button class
        # TODO: path to icons

        self.widgets = {
            "zoomin": QPushButton(self),
            "zoomout": QPushButton(self),
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
            "zoom-in.svg",
            "zoom-out.svg",
        ]

        for w, ic in zip(self.widgets.values(), icons):
            w.setIcon(QIcon(os.path.join(icon_dir, ic)))

        # Add to layout
        layout = QVBoxLayout()
        layout.addItem(ExpandingVSpacer())  # add vertical spacer
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)


# --- Widget for viewer ---


class EMGViewerWidget(QWidget):
    def __init__(self, fig, parent=None):
        super().__init__(parent)

        self.widgets = {
            "plot": EMGPlotWidget(fig),
            "timecontrols": EMGTimeControlsWidget(parent=self),
            "gaincontrols": EMGGainWidget(parent=self),
        }

        layout = QGridLayout()

        layout.addWidget(self.widgets["gaincontrols"], 0, 0)
        layout.addWidget(self.widgets["plot"], 0, 1)
        layout.addWidget(self.widgets["timecontrols"], 1, 1)

        self.setLayout(layout)
