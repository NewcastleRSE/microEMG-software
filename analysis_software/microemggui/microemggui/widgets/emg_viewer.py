"""
Widget for viewing EMG time series.

Current icons from https://icons.getbootstrap.com/

"""

from math import ceil

import numpy as np

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QSlider,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QSizePolicy,
)
from PySide6.QtGui import QIcon, QPen, QFont, QPixmap
from PySide6.QtCore import Qt, Signal
import pyqtgraph as pg

from microemggui.widgets.base import (
    InputInlineLabel,
    InputComboBox,
    InputInlineText,
    InputInlineHighlightedText,
    ExpandingVSpacer,
    WidgetControlButton,
)
from microemggui.widgets.base_pyqtgraph import EMGYAxisItem
from microemggui.icons import icons  # noqa - import allows icon references


# --- Local helper functions ----


def convert_seconds_to_time_label(time_s: float, with_ms: bool = False, n_dec=4) -> str:
    # Convert time in seconds to a mm:ss string
    # TODO: check for any floating point issues

    S_TO_MIN = 60

    n_min = int(time_s / S_TO_MIN)
    n_sec = time_s - (n_min * S_TO_MIN)

    if with_ms:  # include ms
        time_label = f"{n_min:02d}:{round(n_sec,4):0{n_dec+3}.{n_dec}f}"
        return time_label

    # ignoring ms
    time_label = f"{n_min:02d}:{int(n_sec):02d}"
    return time_label


# --- Plot ---


class EMGPlotWidget(QWidget):
    """
    Widget for plotting EMG time series data in EMG viewer widget.
    """

    # Signal to emit when start time is incremented
    start_time_incremented = Signal(float)

    # Signals for whether EMG time series is at start or end (stop)
    at_start = Signal(bool)
    at_stop = Signal(bool)

    # Signal when division size is changed
    div_size_changed = Signal()

    def __init__(self, emg_model, emg_clrs: list[str], parent=None):
        super().__init__(parent)

        self.emg_model = emg_model

        # EMG data segment options
        self.start_t = 0  # start time (in seconds)
        self.div_size = 0.1  # division size (in seconds)
        self.ds_factor = self.compute_ds_factor()  # downsampling factor
        self.offset = 1000  # initial vertical offset between signals
        self.n_div = 10  # number of divisions per "page"

        # Style options
        self.emg_clrs = emg_clrs  # colors for plot
        self.n_clr_rep = 1  # times each colour will be repeated in adjacent channels
        self.y_font_size = 12  # font size for y-tick labels
        self.x_font_size = 12  # font size for x-tick labels

        # Initial plot
        self.make_fig()
        self.plot_w.plotItem.setMouseEnabled(x=False, y=False)
        self.plot_w.viewport().installEventFilter(self)  # to catch wheel events

        # Add figure to layout and set figure to expand to fill available space
        layout = QVBoxLayout()
        layout.addWidget(self.plot_w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Flags for whether time series can be progressed forward/backwards
        self.can_move_forward = True
        self.can_move_backward = False  # Cannot move backwards initially since at t = 0

    def compute_stop_time(self) -> float:
        # Compute stop time of plotted data based on start time and division size

        stop_t = self.start_t + (self.div_size * self.n_div)
        return stop_t

    def make_plot_pens(self) -> list[QPen]:
        # Make a pen for drawing each EMG signal in the pyqtgraph plot

        n_chan = self.emg_model.emg_data.n_chan  # number of channels

        # Repeat provided colours to meet required number of colours
        n_clrs = ceil(n_chan / self.n_clr_rep)  # number of colours needed
        n_emg_clrs = len(self.emg_clrs)  # number of colours provided
        self.emg_clrs = self.emg_clrs * ceil(n_clrs / n_emg_clrs)
        self.emg_clrs = self.emg_clrs[:n_clrs]

        # Make pens, repeating each colour n_clr_rep times
        self.emg_clrs = [clr for clr in self.emg_clrs for i in range(self.n_clr_rep)]

        # Make pens
        pens = [pg.mkPen(color=clr, width=1.5) for clr in self.emg_clrs]
        return pens

    def make_fig(self):
        # Make figure

        # Compute stop time
        stop_t = self.compute_stop_time()

        # Make figure and axes

        # Compute section of data to plot
        emg_t = self.emg_model.emg_data.get_emg_t()
        plot_idx = self.emg_model.emg_data._get_t_idx(self.start_t, stop_t)
        plot_idx = plot_idx[0 :: self.ds_factor]

        # Make pens
        pens = self.make_plot_pens()

        # Make plot widget and plot
        self.plot_w = pg.PlotWidget()
        self.line_ref = list()
        for i in range(self.emg_model.emg_data.n_chan):
            line_ref = self.plot_w.plot(
                emg_t[plot_idx],
                self.emg_model.emg_data.emg_ts[i, plot_idx] - self.offset * i,
                pen=pens[i],
            )
            self.line_ref.append(line_ref)
        self.plot_w.setBackground("w")
        self.plot_w.hideButtons()  # to remove autoscale option

        # Axes and ticks
        self.plot_w.showGrid(x=True, y=False)  # only keep x-axis (vertical) grid
        y_ax = EMGYAxisItem(pens, orientation="left", maxTickLength=-2)
        self.plot_w.setAxisItems({"left": y_ax})
        x_ax = self.plot_w.getAxis("bottom")
        x_ax.setGrid(False)
        x_ax.setStyle(hideOverlappingLabels=False, autoExpandTextSpace=True)
        self.plot_w.showAxis("top")  # Show grid via top axis (prevents text clipping)
        self.set_y_ticks_and_range()
        self.set_x_ticks_and_range()

        # Tick label fonts
        # TODO: consider other fonts
        # TODO: consider setting font size as an option
        font = QFont("Lucida Sans Typewriter", self.y_font_size)
        self.plot_w.getAxis("left").setStyle(tickFont=font)
        font = QFont("Lucida Sans Typewriter", self.x_font_size)
        self.plot_w.getAxis("bottom").setStyle(tickFont=font)

    def update_plot(self):
        # Update plotted data using existing axes

        # Compute stop time
        stop_t = self.compute_stop_time()

        # If requested stop time > EMG duration, change to EMG duration
        if stop_t > self.emg_model.emg_data.emg_dur:
            stop_t = self.emg_model.emg_data.emg_dur

            # Stop further progression
            self.can_move_forward = False
            self.at_stop.emit(self.can_move_forward)

        # If not at end of EMG time series, check if need to re-activate forward buttons
        elif self.can_move_forward is False:
            self.can_move_forward = True
            self.at_stop.emit(self.can_move_forward)

        # Update data in plot
        emg_t = self.emg_model.emg_data.get_emg_t()
        plot_idx = self.emg_model.emg_data._get_t_idx(self.start_t, stop_t)
        plot_idx = plot_idx[0 :: self.ds_factor]
        for i in range(len(self.line_ref)):
            self.line_ref[i].setData(
                emg_t[plot_idx],
                self.emg_model.emg_data.emg_ts[i, plot_idx] - self.offset * i,
            )
        self.set_x_ticks_and_range()  # update x-axis

    def replace_emg_model(self, emg_model):
        # Replace EMG model with a new model (and new EMG data).
        # Assumes the number of channels is the same (e.g., the new data is a
        # transformed version of the original data).
        # TODO: consider adding check for number of channels

        self.emg_model = emg_model
        self.update_plot()

    def set_y_ticks_and_range(self):
        # Fix y-axis ticks and range of pyqtgraph plot based on offset value and
        # number of channels

        # Compute y-tick locations
        y_ticks = list(
            np.linspace(
                0,
                (self.emg_model.emg_data.n_chan - 1) * self.offset * -1,
                self.emg_model.emg_data.n_chan,
            )
        )

        # Apply to y-axis
        chan_names = self.emg_model.emg_data.chan.chan_names
        y_ax = self.plot_w.getAxis("left")
        y_ax.setTicks([[(tick, chan) for (tick, chan) in zip(y_ticks, chan_names)]])

        # Set y axis range
        y_buff = self.offset * 2  # Extra space at top and bottom
        self.plot_w.setYRange(y_ticks[0] + y_buff, y_ticks[len(y_ticks) - 1] - y_buff, padding=0)

    def set_x_ticks_and_range(self):
        # Set x-axis ticks and range of pyqtgraph plot based on the plotted time segment
        # Set the x-axis ticks to form 10 divisions
        # Label with recording time in minutes and seconds

        # Compute x-tick locations
        stop_t = self.compute_stop_time()
        x_ticks = list(np.linspace(self.start_t, stop_t, self.n_div + 1))

        # Make labels
        with_ms = self.div_size < 1
        n_dec = int(np.floor(np.log10(self.div_size))) * -1
        t_list = list(np.linspace(self.start_t, stop_t, 11))
        t_labels = [convert_seconds_to_time_label(t, with_ms, n_dec) for t in t_list]

        # Apply to x-axis and "top" axis (latter is for grid lines)
        x_ax = self.plot_w.getAxis("bottom")
        x_ax.setTicks([[(tick, t) for [tick, t] in zip(x_ticks, t_labels)]])
        top_ax = self.plot_w.getAxis("top")
        top_ax.setTicks([[(tick, "") for tick in x_ticks]])

        # set range (leave buffer so all x-tick labels are visible)
        x_buff = self.div_size / 5
        self.plot_w.setXRange(self.start_t - x_buff, stop_t + (x_buff * 1.5), padding=0)

    def compute_ds_factor(self) -> int:
        # Compute downsampling factor based on division size
        # Downsampling prevents slow plotting when large time interval is plotted
        # Set to divison size * 50, with min of 1 and max of 100

        ds_factor = min(self.div_size * 50, 100)
        ds_factor = max(ds_factor, 1)
        ds_factor = int(ds_factor)

        return ds_factor

    def update_div_size(self, div_size: float):
        # Update division size (includes updated downsampling factor correspondingly)

        self.div_size = div_size  # new division size
        self.ds_factor = self.compute_ds_factor()  # update downsample factor
        self.update_plot()  # update plot
        self.div_size_changed.emit()  # emit signal for slider

    def update_start_time(self, start_t: float):
        # Update start time of plotted data
        # Used as slot for slider and also called by increment_start_time()

        self.start_t = start_t
        self.update_plot()

        # Disable/enable buttons depending on start time
        if start_t == 0:
            # Send signal that at start to disable buttons
            self.can_move_backward = False
            self.at_start.emit(self.can_move_backward)

        elif self.can_move_backward is False:
            # If previously at start, enable backwards buttons
            self.can_move_backward = True
            self.at_start.emit(self.can_move_backward)

    def get_max_start_time(self) -> float:
        # Compute maximum allowed start time given division size and number of
        # divisions

        max_start = self.emg_model.emg_data.emg_dur - (self.div_size * (self.n_div - 1))
        max_start = max(max_start, 0)  # Ensures min possible value is zero
        return max_start

    def increment_start_time(self, n_div: int):
        # Slot for arrow buttons for incrementing start time
        # n_div = number of divisions to move

        # Increment by n div
        start_t = self.start_t + (n_div * self.div_size)

        # Restrict to valid times
        if start_t <= 0:
            start_t = 0  # force start_t to be >= 0

        start_t = min(start_t, self.get_max_start_time())  # force < duration - div_size

        # Update start time for plot
        self.update_start_time(start_t)

        # Send signal to update start time of slider
        self.start_time_incremented.emit(start_t)

    def scale_offset(self, scale: float):
        # Slot for buttons that scale amplitude of plotted lines (via offset
        # parameter)
        # Also updates y-axis ticks and range

        self.offset = self.offset / scale  # scale offset
        self.update_plot()  # update plot
        self.set_y_ticks_and_range()  # update y-axis ticks

    def eventFilter(self, obj, event):
        # Catch wheel events on pyqtgraph plot
        # TODO: check that works as expected using mouse and WindowsOS

        if "QWheelEvent" in str(event):
            wheel_delta = event.angleDelta().y()
            self.increment_start_time(int(wheel_delta / 8))
            return True
        else:
            return super().eventFilter(obj, event)


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
        # TODO: ensure initial division size is included in options

        MS_TO_S = 1000

        # Info about each option
        options = {}

        # Options in ms
        # (using ms so can ensure are integers for text conversion)
        options["values_ms"] = [1, 2, 5, 10, 25, 50, 100, 500, 1000, 10000]

        # Set units to seconds if 1+ seconds (1000 ms); otherwise, keep as ms
        ms_cutoff = 1000
        options["units"] = ["ms" if v < ms_cutoff else "s" for v in options["values_ms"]]

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

        # Reference to widget with plot
        self.plot_widget = plot_widget

        # Create button widgets
        self.widgets = {
            "previous_fast": WidgetControlButton(self),
            "previous": WidgetControlButton(self),
            "next": WidgetControlButton(self),
            "next_fast": WidgetControlButton(self),
        }

        # Icons for buttons
        my_icons = [
            "rewind",
            "caret-left",
            "caret-right",
            "fast-forward",
        ]

        # Tooltip text for each button
        tooltip_text = [
            "Previous 10 divisions",
            "Previous division",
            "Next division",
            "Next 10 divisions",
        ]

        # Set button icons and tooltip text
        for w, ic, txt in zip(self.widgets.values(), my_icons, tooltip_text):
            w.setIcon(QIcon(":/bootstrap/" + ic))
            w.setToolTip(txt)

        # Number of divisions moved by each button
        # (will send with button clicked signals)
        # Disable buttons for moving backwards
        self.button_n_div = [-10, -1, 1, 10]
        self.toggle_previous_buttons(False)

        # Add to layout
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)

        # Connections
        self.connect_start_time()
        self.plot_widget.at_stop.connect(self.toggle_next_buttons)
        self.plot_widget.at_start.connect(self.toggle_previous_buttons)

    def connect_start_time(self):
        # Connect button clicked signal to start time of EMG plot.
        # Will increment start time by the number of divisions moved by the button

        for w, n in zip(self.widgets.values(), self.button_n_div):
            w.clicked.connect(lambda checked=None, n=n: self.plot_widget.increment_start_time(n))

    def toggle_next_buttons(self, can_move_forward):
        # Enable/disable buttons for progressing time series.
        # Slot for self.plot_widget "at_stop" signal.

        for w, n in zip(self.widgets.values(), self.button_n_div):
            if n > 0:  # widgets that move forward through EMG time series
                w.setEnabled(can_move_forward)

    def toggle_previous_buttons(self, can_move_backward):
        # Enable/disable buttons for progressing time series.
        # Slot for self.plot_widget "at_stop" signal.

        for w, n in zip(self.widgets.values(), self.button_n_div):
            if n < 0:  # widgets that move backward through EMG time series
                w.setEnabled(can_move_backward)


class EMGStartTimeWidget(QWidget):
    # Slider for changing time in EMG Viewer.
    # Intervals are determined by division size.
    # Provides mm:ss label for start time.
    # TODO: consider custom slider class if need multiple sliders with different styles

    def __init__(self, plot_widget, parent=None):
        super().__init__(parent)

        # EMG plot and duration
        self.plot_widget = plot_widget
        self.emg_dur = plot_widget.emg_model.emg_data.emg_dur

        # Create widgets
        self.widgets = {
            "label": InputInlineLabel("Start time: ", self),
            "time": InputInlineHighlightedText("00:00", self),
            "slider": QSlider(Qt.Horizontal, self),
            "maxtime": InputInlineText("00:00", self),
        }

        # Set slider to expand to fill space
        self.widgets["slider"].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Set slider limits
        self.widgets["slider"].setMinimum(0)
        self.set_slider_maximum()  # also updates max time label

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
        self.plot_widget.div_size_changed.connect(self.set_slider_maximum)

    def set_slider_maximum(self):
        # Set slider maximum match number of divisions in data
        # Correspondingly adjust current slider value to match current start time

        # Get current plot time (may be changed when change slider max)
        start_t = self.plot_widget.start_t

        # Set max start division and set slider to correct corresponding start time
        max_start = int(self.emg_dur / self.plot_widget.div_size) - (self.plot_widget.n_div - 1)
        max_start = max(max_start, 0)  # Ensures min possible value is zero
        self.widgets["slider"].setMaximum(max_start)  # Set maximum
        self.update_slider(start_t)
        self.update_max_time_label()

    def convert_slider_value_to_start_time(self) -> float:
        # Converts slider value (number of divisions) to start time in seconds

        start_t = self.widgets["slider"].value() * self.plot_widget.div_size
        return start_t

    def update_time_label(self, slider_value: int):
        # Updates time label from slider value

        # Start time in seconds
        start_t = self.convert_slider_value_to_start_time()

        # Compute and set time label
        t_label = convert_seconds_to_time_label(start_t)
        self.widgets["time"].setText(t_label)

    def update_max_time_label(self):
        # Update the max time label for the slider based on the interval size
        # (max time is the maximal start time that the slider can be set to)

        # Convert max slider value to seconds
        max_t = self.widgets["slider"].maximum() * self.plot_widget.div_size

        # Compute and set max time label
        t_label = convert_seconds_to_time_label(max_t)
        self.widgets["maxtime"].setText(t_label)

    def connect_slider_value_to_time_label(self):
        # Connection for changes in slider value to change start time label

        self.widgets["slider"].valueChanged.connect(self.update_time_label)

    def connect_slider_value_to_start_time(self):
        # Connection for changes in slider value to change start time in plot

        self.widgets["slider"].valueChanged.connect(
            lambda value: self.plot_widget.update_start_time(
                self.convert_slider_value_to_start_time()
            )
        )

    def update_slider(self, start_time: float):
        # Slot for changing slider when plot start time is incremented (via arrows).
        # Also used when updating slider maximum (which also changes slider interval
        # size)

        # Multiply by 1/div_size rather than divide by div_size to reduce (prevent?)
        # floating point precision errors; also round as a back-up
        self.widgets["slider"].setValue(int(round(start_time * (1 / self.plot_widget.div_size))))


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


# --- Widgets for controlling plotted signal amplitude ---


class EMGGainWidget(QWidget):
    # Controls for controlling plotted signal amplitude (gain)

    def __init__(self, plot_widget, parent=None):
        super().__init__(parent)

        # Reference to plot widget
        self.plot_widget = plot_widget

        # Create button widgets for changing signal amplitude
        self.widgets = {
            "increase": WidgetControlButton(self),
            "decrease": WidgetControlButton(self),
        }

        # Set scaling factor of each button
        scale_factor = 0.75
        self.widget_scale = [1 / scale_factor, scale_factor]

        # Icons and tooltips for buttons
        my_icons = [
            "caret-up",
            "caret-down",
        ]
        tooltip_text = ["Increase signal amplitude", "Decrease signal amplitude"]

        for w, ic, txt in zip(self.widgets.values(), my_icons, tooltip_text):
            w.setIcon(QIcon(":/bootstrap/" + ic))
            w.setToolTip(txt)

        # Additional widget for amplitude image
        # Defined separately since will not need to iterate through for connections, etc.
        self.amp_image = QLabel(self)
        self.amp_image.setPixmap(QPixmap(":/amplitude/amp1"))
        self.amp_image.setScaledContents(True)
        self.amp_image.setObjectName("amp")  # name so can control size via style sheet

        # Add to layout
        layout = QVBoxLayout()
        layout.addItem(ExpandingVSpacer())  # add vertical spacer
        layout.addWidget(self.widgets["increase"])
        layout.addWidget(self.amp_image)
        layout.addWidget(self.widgets["decrease"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)

        # Connections
        self.connect_scale_to_plot_offset()

    def connect_scale_to_plot_offset(self):
        # Connect button clicked signal of buttons to offset of EMG plot.
        # Will scale offset by widget_scale value

        for w, scale in zip(self.widgets.values(), self.widget_scale):
            w.clicked.connect(
                lambda checked=None, scale=scale: self.plot_widget.scale_offset(scale)
            )


# --- Widget for viewer ---


class EMGViewerWidget(QWidget):
    # Widget for viewing EMG time series data

    def __init__(self, emg_model, emg_clrs: list[str], parent=None):
        super().__init__(parent)

        # Create plot widget for provided EMG data
        plot_widget = EMGPlotWidget(emg_model, emg_clrs, parent=self)

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
        self.setContentsMargins(0, 0, 0, 0)

        # Change widget properties so will be drawn using styled background
        self.setAttribute(Qt.WA_StyledBackground, True)
