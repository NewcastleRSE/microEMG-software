"""
Widget for viewing EMG time series.

Current icons from https://icons.getbootstrap.com/

TODO: consider fixing yaxis limits so labels do not move
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

from PySide6.QtCore import Qt, Signal

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


class EMGPlotWidget(QWidget):
    """
    Widget for plotting EMG time series data in EMG viewer widget
    TODO: consider using pyqtgraph for potentially better performance
    """

    # Signal to emit when start time is incremented
    start_time_incremented = Signal(float)

    def __init__(self, emg_data_model, parent=None):
        super().__init__(parent)

        self.emg_data_model = emg_data_model

        self.start_t = 0  # start time (in seconds)
        self.div_size = 0.1  # division size (in seconds)
        self.ds_factor = self.compute_ds_factor()  # downsampling factor
        self.offset = 1000  # initial vertical offset between signals
        self.n_div = 10  # number of divisions per "page"

        # Initial plot
        self.make_fig()
        self.plot = FigureCanvasQTAgg(self.fig)

        # Add figure to layout and set figure to expand to fill available space
        layout = QVBoxLayout()
        layout.addWidget(self.plot)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Connect scroll (wheel) event on canvas to incrementing start time
        self.fig.canvas.mpl_connect("scroll_event", self.on_scroll)

    def compute_stop_time(self) -> float:
        # Compute stop time of plotted data based on start time and division size

        stop_t = self.start_t + (self.div_size * self.n_div)
        return stop_t

    def make_fig(self):
        # Make figure

        # Compute stop time
        stop_t = self.compute_stop_time()

        # Make figure and axes
        self.fig, self.ax = self.emg_data_model.emg_data.plot_emg_ts(
            start_t=self.start_t,
            stop_t=stop_t,
            downsample_factor=self.ds_factor,
            offset=self.offset,
        )

    def update_plot(self):
        # Update plot using existing axes

        # clear axis
        self.ax.cla()

        # Compute stop time
        stop_t = self.compute_stop_time()

        # Make figure using existing axes
        _, self.ax = self.emg_data_model.emg_data.plot_emg_ts(
            start_t=self.start_t,
            stop_t=stop_t,
            downsample_factor=self.ds_factor,
            offset=self.offset,
            ax=self.ax,
        )

        # redraw
        self.fig.canvas.draw_idle()

    def compute_ds_factor(self) -> int:
        # Compute downsampling factor based on division size
        # Downsampling prevents slow plotting when large time interval is plotted
        # Set to divison size * 50, with min of 1 and max of 80

        ds_factor = min(self.div_size * 50, 80)
        ds_factor = max(ds_factor, 1)
        ds_factor = int(ds_factor)

        return ds_factor

    def update_div_size(self, div_size: float):
        # Update division size (includes updated downsampling factor correspondingly)
        # TODO: consider best relationship between div size and downsample factor

        self.div_size = div_size  # new division size
        self.ds_factor = self.compute_ds_factor()  # update downsample factor
        self.update_plot()  # update plot

    def update_start_time(self, start_t: float):
        # Update start time of plotted data
        # Used as slot for slider and also called by increment_start_time()

        self.start_t = start_t
        self.update_plot()

    def get_max_start_time(self) -> float:
        # Compute maximum allowed start time given division size and number of
        # divisions

        max_start = self.emg_data_model.emg_data.emg_dur - self.n_div * self.div_size
        return max_start

    def increment_start_time(self, n_div: int):
        # Slot for arrow buttons for incrementing start time

        # n_div = number of divisions to move
        start_t = self.start_t + (n_div * self.div_size)  # increment by n div

        # Restrict to valid times
        start_t = max(start_t, 0)  # force start_t to be >= 0
        start_t = min(start_t, self.get_max_start_time())  # force <= duration

        # Update start time for plot
        self.update_start_time(start_t)

        # Send signal to update start time of slider
        self.start_time_incremented.emit(start_t)

    def scale_offset(self, scale):
        # Slot for zoom buttons to scale amplitude of plotted lines (via offset
        # parameter)

        self.offset = self.offset / scale  # scale offset
        self.update_plot()  # update plot

    def on_scroll(self, event):
        # Slot for scroll event on plot canvas.
        # Matplotlib event returns whether scroll is up (on Mac trackpad, moving towards
        # user) or down (moving away from user). Up scrolls progress EMG time series
        # forward; down scrolls progress backwards.
        # Note this type of event is called a wheel event in Qt.

        match event.button:
            case "up":
                n_div = 1
            case "down":
                n_div = -1
        self.increment_start_time(n_div)


# --- Widgets for controlling time window ---


class EMGDivSizeWidget(QWidget):
    # Widget for specifying the window size (i.e., time segment duration) for viewing
    # EMG data in terms of division size (with 10 divisions per "page")

    def __init__(self, plot_widget, parent=None):
        super().__init__(parent)

        # Reference to widget with plot
        self.plot_widget = plot_widget

        # Create combobox widget
        self.widgets = {
            "div_combobox": InputComboBox(self),
        }

        # Add options for combobox
        self.options = self.make_combobox_options()
        self.widgets["div_combobox"].addItems(self.options["text"])

        # Match initial combobox setting to div size in initial plot
        idx = self.options["values_s"].index(plot_widget.div_size)
        self.widgets["div_combobox"].setCurrentIndex(idx)

        # Add widget to layout
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Connect signals
        self.connect_div_size()

    @staticmethod
    def make_combobox_options():
        # Make division options for combobox.
        # Includes combobox text and corresponding division values in seconds; the
        # latter will be used for signals.
        # TODO: remove options that would exceed duration of EMG segment (or pad time
        # series so it is possible)
        # TODO: ensure initial division size is included in options

        MS_TO_S = 1000

        # Info about each option
        options = {}

        # Options in ms
        # (using ms so can ensure are integers for text conversion)
        options["values_ms"] = [1, 2, 5, 10, 25, 50, 100, 500, 1000, 10000]

        # Set units to seconds if 1+ seconds (1000 ms); otherwise, keep as ms
        ms_cutoff = 1000
        options["units"] = [
            "ms" if v < ms_cutoff else "s" for v in options["values_ms"]
        ]

        # Value for combobox as a string, converted to match units in options["units"]
        options["values_text"] = []
        for v in options["values_ms"]:
            if v >= ms_cutoff:
                v_text = v / MS_TO_S
                if abs(int(v_text) - v_text) < 10e-10:
                    v_text = int(v_text)  # convert to int if integer value

            else:
                v_text = v
            options["values_text"].append(str(v_text))

        # Final text for combobox
        div_text = "divisions"
        options["text"] = [
            " ".join([v, unit, div_text])
            for (v, unit) in zip(options["values_text"], options["units"])
        ]

        # Second version of values (asa float) for signals to send to plot and other
        # widgets
        options["values_s"] = [v / MS_TO_S for v in options["values_ms"]]

        return options

    def connect_div_size(self):
        # Sends division size in seconds (stored in self.options["values_s"]) that
        # corresponds to the combobox index.
        # Connected to plot widget method for updating the division size.

        w = self.widgets["div_combobox"]
        w.currentIndexChanged.connect(
            lambda idx: self.plot_widget.update_div_size(self.options["values_s"][idx])
        )


class EMGArrowsWidget(QWidget):
    # Arrow buttons for moving backwards and forwards through time series plot

    def __init__(self, plot_widget, parent=None):
        super().__init__(parent)
        # TODO: create class for icon buttons
        # TODO: consider disabling button if no longer possible to increment
        # TODO: consider plotting blank space if partial over-increment ?

        # Reference to widget with plot
        self.plot_widget = plot_widget

        # Create button widgets
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

        # Tooltip text for each button
        tooltip_text = [
            "Previous 10 divisions",
            "Previous division",
            "Next division",
            "Next 10 divisions",
        ]

        # Set button icons and tooltip text
        for w, ic, txt in zip(self.widgets.values(), icons, tooltip_text):
            w.setIcon(QIcon(os.path.join(icon_dir, ic)))
            w.setToolTip(txt)

        # Number of divisions moved by each button
        # (will send with button pressed signals)
        self.button_n_div = [-10, -1, 1, 10]

        # Add to layout
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)

        # Connections
        self.connect_start_time()

    def connect_start_time(self):
        # Connect button clicked signal to start time of EMG plot.
        # Will increment start time by the number of divisions moved by the button

        for w, n in zip(self.widgets.values(), self.button_n_div):
            w.pressed.connect(lambda n=n: self.plot_widget.increment_start_time(n))


class EMGStartTimeWidget(QWidget):
    # Slider for changing time in EMG Viewer
    # TODO: consider custom slider class if need multiple sliders with different styles

    def __init__(self, plot_widget, parent=None):
        super().__init__(parent)

        # EMG plot and duration
        self.plot_widget = plot_widget
        self.emg_dur = plot_widget.emg_data_model.emg_data.emg_dur

        # Create widgets
        self.widgets = {
            "label": InputInlineLabel("Start time: ", self),
            "time": InputInlineText("00:00", self),
            "slider": QSlider(Qt.Horizontal, self),
        }

        # Set slider to expand to fill space
        self.widgets["slider"].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Set slider limits
        self.widgets["slider"].setMinimum(0)
        self.set_slider_maximum(self.plot_widget.div_size)

        # TODO: consider slider units (sec or ms)

        # Add to layout
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Connections
        self.connect_slider_value_to_time_label()
        self.connect_slider_value_to_start_time()
        self.plot_widget.start_time_incremented.connect(self.update_slider)

    def set_slider_maximum(self, div_size):
        # Set slider maximum to maximum allowed start time, given division size
        # Will truncate if not integer

        max_start = self.emg_dur - (self.plot_widget.n_div * self.plot_widget.div_size)
        self.widgets["slider"].setMaximum(int(max_start))  # units: s

    def update_time_label(self, slider_time: int):
        # Updates time label (from slider time in seconds)

        n_min = int(slider_time / 60)
        n_sec = int(slider_time - (n_min * 60))
        time_label = f"{n_min:02d}:{n_sec:02d}"
        self.widgets["time"].setText(time_label)

    def connect_slider_value_to_time_label(self):
        # Connection for changes in slider value to change start time label

        self.widgets["slider"].valueChanged.connect(self.update_time_label)

    def connect_slider_value_to_start_time(self):
        # Connection for changes in slider value to change start time in plot

        self.widgets["slider"].valueChanged.connect(self.plot_widget.update_start_time)

    def update_slider(self, start_time: float):
        # Slot for changing slider when plot start time is incremented (via arrows)

        self.widgets["slider"].setValue(int(start_time))


class EMGTimeControlsWidget(QWidget):
    # Controls for changing time in EMG Viewer

    def __init__(self, plot_widget, parent=None):
        super().__init__(parent)

        # Create widgets; plot_widget is passed to each one for connections
        self.widgets = {
            "arrows": EMGArrowsWidget(plot_widget, parent=self),
            "div": EMGDivSizeWidget(plot_widget, parent=self),
            "starttime": EMGStartTimeWidget(plot_widget, parent=self),
        }
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        self.setLayout(layout)

        # Connections between widgets
        self.connect_div_size_to_start_time_slider()

    def connect_div_size_to_start_time_slider(self):
        # Connects div size to max slider time

        div_w = self.widgets["div"].widgets["div_combobox"]
        div_values = self.widgets["div"].options["values_s"]
        div_w.currentIndexChanged.connect(
            lambda idx: self.widgets["starttime"].set_slider_maximum(div_values[idx])
        )


# --- Widgets for controlling plotted signal amplitude ---


class EMGGainWidget(QWidget):
    # Controls for controlling plotted signal amplitude (gain)

    def __init__(self, plot_widget, parent=None):
        super().__init__(parent)

        # TODO: button class

        # Reference to plot widget
        self.plot_widget = plot_widget

        # Create button widgets for zooming
        self.widgets = {
            "zoomin": QPushButton(self),
            "zoomout": QPushButton(self),
        }

        # Set scaling factor of each button
        scale_factor = 0.75
        self.widget_zoom = [1 / scale_factor, scale_factor]

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

        # Connections
        self.connect_zoom_to_plot_offset()

    def connect_zoom_to_plot_offset(self):
        # Connect button clicked signal of zoom buttons to offset of EMG plot.
        # Will scale offset by widget_zoom value

        for w, scale in zip(self.widgets.values(), self.widget_zoom):
            w.pressed.connect(lambda scale=scale: self.plot_widget.scale_offset(scale))


# --- Widget for viewer ---


class EMGViewerWidget(QWidget):
    # Widget for viewing EMG time series data

    def __init__(self, emg_data_model, parent=None):
        super().__init__(parent)

        # Create plot widget for provided EMG data
        plot_widget = EMGPlotWidget(emg_data_model, parent=self)

        # Create widgets for viewer
        self.widgets = {
            "plot": plot_widget,
            "timecontrols": EMGTimeControlsWidget(plot_widget, parent=self),
            "gaincontrols": EMGGainWidget(plot_widget, parent=self),
        }

        # Add widgets to layout
        # Gain controls along left side of plot
        # Time controls below plot
        layout = QGridLayout()
        layout.addWidget(self.widgets["gaincontrols"], 0, 0)
        layout.addWidget(self.widgets["plot"], 0, 1)
        layout.addWidget(self.widgets["timecontrols"], 1, 1)
        self.setLayout(layout)
