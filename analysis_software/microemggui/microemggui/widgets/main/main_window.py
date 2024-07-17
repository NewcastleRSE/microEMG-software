#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for main window with toolbars and other navigation elements.

"""

from palettable.cartocolors.qualitative import Prism_10

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QStackedLayout,
)
from PySide6.QtCore import Qt

from microemggui.widgets.base import (
    SectionTitle,
    ExpandingVSpacer,
)

# Toolbars
from microemggui.widgets.main.toolbars import AnalysisToolbar, TopToolbar

# Widgets for each step
from microemggui.widgets.load.load_step import LoadWidget
from microemggui.widgets.preproc.preproc_step import PreprocWidget
from microemggui.widgets.channels.channels_step import ChannelsWidget

# Models
from microemggui.models.settings import EMGPreprocSettingsModel


# --- Widgets to put within main window ---


class WelcomeWidget(QWidget):
    # Widget for welcome page

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create widgets
        self.widgets = {"title": SectionTitle("Welcome to the microEMG analysis GUI", parent=self)}

        # Add to layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.addItem(ExpandingVSpacer())  # spacer
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)


class AnalysisStepsWidget(QWidget):
    # Stacked widgets for the different steps of the analysis
    # Also includes Welcome page

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make iniital widgets
        # Will use same names as AnalysisToolbar so easy to link buttons to corresponding pages:
        # "home", "load", "preprocess", "channels", "motorunits", "fibres", "jitter","export"
        self.widgets = {
            "home": WelcomeWidget(parent=self),
            "load": LoadWidget(parent=self),
        }

        # Add to layout
        self.layout = QStackedLayout()
        for w in self.widgets.values():
            self.layout.addWidget(w)
        self.setLayout(self.layout)

    def show_widget(self, widget_name):
        # Slot for signals for changing displayed widget in stacked layout
        self.layout.setCurrentWidget(self.widgets[widget_name])


# --- Main window ---

# Next steps:
# Add recording to label
# text field for recording label?


class MicroEMGMain(QMainWindow):
    # Main window for microEMG GUI

    def __init__(self):
        super().__init__()

        # Initialise attributes for storing data needed for analysis
        self.emg_model = {}
        self.settings_model = None

        # Colours for EMG recordings
        # TODO: make configurable?
        self.emg_clrs = Prism_10.hex_colors

        # Make widgets and toolbars
        self.widgets = {
            "analysistoolbar": AnalysisToolbar("Analysis toolbar"),
            "toptoolbar": TopToolbar(parent=self),
            "analysis": AnalysisStepsWidget(parent=self),
        }

        # Add analysis toolbar to window
        self.addToolBar(Qt.LeftToolBarArea, self.widgets["analysistoolbar"])

        # Add top toolbar and widgets
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.widgets["toptoolbar"])  # Add top toolbar
        layout.addWidget(self.widgets["analysis"])  # Add stacked widgets for analysis
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        # Add widget to center
        self.setCentralWidget(widget)

        # Window properties
        self.resize(1200, 850)

        # Connections

        # Connections between analysis toolbar buttons and stacked analysis widgets
        # Only home and load widgets are connected here
        self.update_toolbar_connections()

        # Connections to signals from loading data
        self.add_load_connections()

    def reset_gui(self):
        # Remove any existing data, widgets with data, and later toolbar activations
        # Should only be able to use home page and load step widget.
        # TODO: remove data added later in the pipeline
        # TODO: add dialog box for confirmation when click on button that would
        # trigger a reset.
        # TODO: remove print statements or add to logger
        # TODO: behaviour if reset settings or (once implemented) trimming

        print("Resetting GUI")

        # Widgets to keep enabled and widgets to remove
        # Only include widgets that have been added so far to avoid key erros
        keep_w = ["home", "load"]
        remove_w = [i for i in self.widgets["analysis"].widgets.keys() if i not in keep_w]
        print(f"Remove widgets {remove_w}")

        for w_name in remove_w:
            # Remove widgets
            # Also delete key in analysis widgets dictionary so do not try to reference
            # deleted widget
            w = self.widgets["analysis"].widgets.pop(w_name, None)
            if w:
                w.deleteLater()
                print(f"Deleted {w_name} widget")

            # Disable toolbar buttons
            self.widgets["analysistoolbar"].widgets[w_name].setEnabled(False)

            # Can leave connections since will not be able to click on buttons until
            # new widgets are added

        # Remove data (precaution - should be overwritten regardless)
        # EMG data is not sent from load widget until settings are added, so this
        # approach will not delete any newly loaded data.
        self.emg_model = {}
        self.settings_model = None

    def add_load_connections(self):
        # Connections to add from load step widget
        # Connections enable/disable preprocess toolbar button and updates data stored
        # in main window

        # Load widget
        load_w = self.widgets["analysis"].widgets["load"]

        # Connection for enabling/disabling next step (preprocessing)
        load_w.load_finished.connect(
            lambda load_finished, w_name="preprocess": self.enable_analysis_toolbar_button(
                load_finished, w_name
            )
        )

        # Connection for updating raw EMG and settings data in main window
        load_w.load_data_changed.connect(self.update_raw_emg_model_and_settings_model)

        # When load buttons are interacted with, reset GUI (regardless of whether
        # load was successful)
        load_w.widgets["recording"].recording_loaded.connect(
            lambda recording_loaded: self.reset_gui()
        )

        # Link recording label to top toolbar
        # TODO: consider storing in main window (e.g., for saving/exports)
        select_recording_w = load_w.widgets["recording"].widgets["selectrecording"]
        select_recording_w.recording_label_changed.connect(
            self.widgets["toptoolbar"].change_recording_label
        )

    def add_preprocess_connections(self):
        # Preprocess widget
        preprocess_w = self.widgets["analysis"].widgets["preprocess"]

        # Connection for updating preprocessed EMG and preprocessing settings in main window
        preprocess_w.preproc_data_changed.connect(
            self.update_preproc_emg_model_and_preprocess_settings
        )

    def update_toolbar_connections(self):
        # Connects toolbar buttons to analysis widgets
        # Will need to call repeatedly as add more analysis widgets

        print("Updating toolbar connections")
        for w_name, _ in self.widgets["analysis"].widgets.items():
            self.widgets["analysistoolbar"].widgets[w_name].clicked.connect(
                lambda checked=None, w_name=w_name: self.widgets["analysis"].show_widget(w_name)
            )
            print(w_name)

    def update_raw_emg_model_and_settings_model(self, raw_emg_model, settings_model):
        # Slot for updating raw EMG model and settings model
        # Also updates preprocessing widget with this data

        self.emg_model["raw"] = raw_emg_model
        self.settings_model = settings_model

        # Use data to make preprocessing widget
        preprocess_settings_model = EMGPreprocSettingsModel(
            self.settings_model.preprocess_settings
        )
        self.add_preprocess_widget(self.emg_model["raw"], preprocess_settings_model, self.emg_clrs)

    def update_preproc_emg_model_and_preprocess_settings(
        self, preproc_emg_model, preprocess_settings_model
    ):
        # Slot for updating preprocess EMG model and the applied preprocessing settings
        # Also updates and channel selection widget with the preprocessed data

        self.emg_model["preproc"] = preproc_emg_model
        self.settings_model.preprocess_settings = preprocess_settings_model.settings

        # Use data to make channels widget
        self.add_channels_widget()

    def connect_next_button_to_analysis_widget(self, next_button, w_name: str):
        # Connect the next button on an analysis step to the corresponding widget for
        # the next analysis step.
        # Also creates connection to update the active button on the analysis toolbar.

        next_button.clicked.connect(
            lambda checked=None, w_name=w_name: self.widgets["analysis"].show_widget(w_name)
        )
        next_button.clicked.connect(
            lambda checked=None, w_name=w_name: self.click_analysis_toolbar_button(w_name)
        )

    def click_analysis_toolbar_button(self, w_name: str):
        # Clicks on the w_name button in the analysis toolbar to make it the active
        # button.
        # Used as a slot for clicking the next buttons on the analysis step widgets (
        # as an alternative to using the toolbar to navigate)

        self.widgets["analysistoolbar"].widgets[w_name].toggle()

    def enable_analysis_toolbar_button(self, previous_step_finished: bool, w_name: str):
        # Enable/disable button in analysis toolbar based on whether previous step is
        # finished
        self.widgets["analysistoolbar"].widgets[w_name].setEnabled(previous_step_finished)

    def add_preprocess_widget(self, raw_emg_model, preprocess_settings_model, emg_clrs):
        # Add preprocessing widget using data stored in main window

        # Create widget and add to stack of analysis step widgets
        w_name = "preprocess"
        analysis_w = self.widgets["analysis"]
        analysis_w.widgets[w_name] = PreprocWidget(
            raw_emg_model, preprocess_settings_model, emg_clrs
        )
        analysis_w.layout.addWidget(analysis_w.widgets[w_name])

        # Update toolbar connections
        self.update_toolbar_connections()

        # Add connection to load step next button
        next_button = self.widgets["analysis"].widgets["load"].widgets["run"].widgets["next"]
        self.connect_next_button_to_analysis_widget(next_button, w_name)

        # Add connections to signals from preprocessing widget
        self.add_preprocess_connections()

    def add_channels_widget(self):
        # Add widget for channel selection once preprocessing is finished/updated

        # Create widget and add to stack of analysis step widgets
        w_name = "channels"
        analysis_w = self.widgets["analysis"]
        analysis_w.widgets[w_name] = ChannelsWidget(
            self.emg_model["raw"], self.emg_model["preproc"], self.emg_clrs
        )
        analysis_w.layout.addWidget(analysis_w.widgets[w_name])

        # Update toolbar connections
        self.update_toolbar_connections()

        # Enable toolbar button
        self.enable_analysis_toolbar_button(True, "channels")

        # Add connection to next button
        next_button = (
            self.widgets["analysis"].widgets["preprocess"].widgets["buttons"].widgets["next"]
        )
        self.connect_next_button_to_analysis_widget(next_button, w_name)


# TODO: disable downstream toolbar buttons and delete data if load step data changed
