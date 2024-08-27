#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for main window with toolbars and other navigation elements.

"""
from typing import Any

from copy import deepcopy

from palettable.cartocolors.qualitative import Prism_10

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QStackedLayout,
)
from PySide6.QtCore import Qt

from pymicroemg.emg_reconstruct import EMGAnalysisReconstruct

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
from microemggui.widgets.findmu.find_mu_step import FindMUWidget
from microemggui.widgets.selectmu.select_mu_step import SelectMUWidget
from microemggui.widgets.localise.localise_step import LocaliseWidget
from microemggui.widgets.jitter.jitter_step import JitterWidget

# Models
from microemggui.models.settings import EMGSettingsModel, EMGPreprocSettingsModel
from microemggui.models.emg import (
    EMGDataRawModel,
    EMGDataPreprocModel,
    EMGAnalysisReconstructModel,
)


# --- Widgets to put within main window ---


class WelcomeWidget(QWidget):
    """
    Widget for welcome (home) page.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "title": SectionTitle("Welcome to the microEMG analysis GUI", parent=self)
        }

        # Add to layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.addItem(ExpandingVSpacer())  # spacer
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)


class AnalysisStepsWidget(QWidget):
    """
    Stacked widgets for the different steps of the analysis.
    Also includes the Welcome (home) page.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make iniital widgets
        # Will use same names as AnalysisToolbar so easy to link buttons to corresponding pages:
        # "home", "load", "preprocess", "channels", "motorunits", "fibres", "jitter","export"
        self.widgets: dict[str, Any] = {
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


class MicroEMGMain(QMainWindow):
    """
    Main window for microEMG GUI

    Types of methods:
        - resetting the analysis
        - adding connections
        - updating data/settings
        - adding widget for each analysis step

    """

    def __init__(self):
        super().__init__()

        # Initialise attributes for storing data needed for analysis
        self.emg_model = {}
        self.settings_model = None
        self.bad_chan_idx = []  # List of indices of bad channels
        self.reconstruct_model = None
        self.motor_units_to_analyse = []  # List of motor units to analyse

        # Colours for EMG recordings
        # TODO: make configurable?
        self.emg_clrs = Prism_10.hex_colors

        # Make widgets and toolbars
        self.widgets: dict[str, Any] = {
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

    def reset_downstream_steps_of_gui(self, last_w_name: str):
        """
        Reset steps and data that occur after analysis step last_w_name.
        """

        print(f"Resetting part of GUI analysis (downstream of {last_w_name})")

        # All analysis steps that have been added
        analysis_w_names = list(self.widgets["analysis"].widgets.keys())

        # Delete widgets for steps after w_name
        # Also delete data added by later steps and reset settings modified by later steps
        delete_w = False
        for w_name in analysis_w_names:
            if delete_w:
                w = self.widgets["analysis"].widgets.pop(w_name, None)  # also removes from dict
                w.deleteLater()  # delete
                print(f"Deleted {w_name} widget")

                # Disable toolbar buttons
                self.widgets["analysistoolbar"].widgets[w_name].setEnabled(False)

                # Remove data if delete certain points of the analysis
                if w_name == "preprocess":
                    print("Deleting EMG model and settings model")
                    self.emg_model = {}
                    self.settings_model = None

                if w_name == "channels":
                    print("Removing bad channels")
                    self.bad_chan_idx = []  # bad channels
                    if self.emg_model:  # also remove bad channels from EMG model if still present
                        print("Also removing bad channels from EMG model")
                        self.emg_model["preproc"].emg_data.set_bad_chan(self.bad_chan_idx)
                    print("Removing reconstruct model")
                    self.reconstruct_model = None

                if w_name == "findmu":
                    print("Removing motor units")
                    if self.reconstruct_model:
                        self.reconstruct_model.found_motor_units = None

                    # Reset motor unit settings (modified in this widget)
                    print("Resetting motor unit settings")
                    print(
                        f"current spike thresh: {self.settings_model.mu_settings.tk_filt_thres_spike}"
                    )
                    self.settings_model.mu_settings = deepcopy(
                        self.settings_model_original.mu_settings
                    )
                    print(
                        f"new spike thresh: {self.settings_model.mu_settings.tk_filt_thres_spike}"
                    )

                if w_name == "selectmu":
                    print("Removing list of motor units to analyse")
                    self.motor_units_to_analyse = []

                if w_name == "localise":
                    # Delete fibre reconstruction and clustering results
                    if self.reconstruct_model:
                        self.reconstruct_model.reconstruct.delete_all_mu_fibre_localisation()

                    # Reset motor unit clustering settings (modified in this widget)
                    print("Removing cluster settings")
                    print(
                        f"current time weight: {self.settings_model.mu_cluster_settings.time_scale}"
                    )
                    self.settings_model.mu_cluster_settings = deepcopy(
                        self.settings_model_original.mu_cluster_settings
                    )
                    print(f"new time weight: {self.settings_model.mu_cluster_settings.time_scale}")

                if w_name == "jitter":
                    if self.reconstruct_model:
                        self.reconstruct_model.reconstruct.delete_all_mu_fibre_jitter()
                    print("Reset jitter widget: deleted jitter results")

            # Change delete_w to True after pass last_w_name; will delete downstream widgets
            if w_name == last_w_name:
                delete_w = True

    def add_load_connections(self):
        """
        Connections to add for the load step widget.
        Connections enable/disable the preprocess toolbar button and update the data
        stored in the main window.
        """

        # Load widget
        load_w = self.widgets["analysis"].widgets["load"]

        # Connection for enabling/disabling next step (preprocessing)
        load_w.load_finished.connect(
            lambda load_finished, w_name="preprocess": self.enable_analysis_toolbar_button(
                load_finished, w_name
            )
        )

        # When load buttons are interacted with, reset GUI (regardless of whether
        # load was successful)
        load_w.widgets["recording"].recording_loaded.connect(
            lambda recording_loaded, last_w_name="load": self.reset_downstream_steps_of_gui(
                last_w_name
            )
        )

        # When settings are interacted with, reset GUI after preprocessing step
        load_w.widgets["settings"].widgets["load"].widgets["combobox"].currentTextChanged.connect(
            lambda text, last_w_name="preprocess": self.reset_downstream_steps_of_gui(last_w_name)
        )

        # Connection for updating raw EMG and settings data in main window
        load_w.load_data_changed.connect(self.update_raw_emg_model_and_settings_model)

        # Link recording label to top toolbar
        # TODO: consider storing in main window (e.g., for saving/exports)
        select_recording_w = load_w.widgets["recording"].widgets["selectrecording"]
        select_recording_w.recording_label_changed.connect(
            self.widgets["toptoolbar"].change_recording_label
        )

    def add_preprocess_connections(self):
        """
        Add connections for the preprocess widget.
        Connection updates the preprocessed EMG data and preprocessing settings that are
        stored in the main window.
        """

        # Preprocess widget
        preprocess_w = self.widgets["analysis"].widgets["preprocess"]

        # Connection for updating preprocessed EMG and preprocessing settings in main window
        preprocess_w.preproc_data_changed.connect(
            self.update_preproc_emg_model_and_preprocess_settings
        )

    def add_channels_connections(self):
        """
        Add connections for channels widget:
          - Update list of bad channels when click next. (If channels have changed,
          update_bad_chan_idx will also trigger the re-creation of the findmu widget.)
          - Disable/enable toolbar button for next step depending on whether min number
          of channels have been selected.
        """

        channels_w = self.widgets["analysis"].widgets["channels"]
        channels_w.bad_chan_updated.connect(self.update_bad_chan_idx)

        # Also connect next step in toolbar to next_clicked method of channels widget
        # so same signal is emitted when navigate via toolbar instead of the next button
        self.widgets["analysistoolbar"].widgets["findmu"].clicked.connect(channels_w.next_clicked)

        # Disable/enable toolbar button for next step depending on whether min number
        # of channels have been selected.
        self.widgets["analysis"].widgets["channels"].min_chan_selected.connect(
            lambda min_selected, w_name="findmu": self.enable_analysis_toolbar_button(
                min_selected, w_name
            )
        )

    def add_findmu_connections(self):
        """
        Add connections for find motor units (findmu) widget.
        Adds/deletes the selectmu widget and enables/disables buttons for the next step
        depending on whether motor units have been found.
        """

        # Find motor units widget
        findmu_w = self.widgets["analysis"].widgets["findmu"]

        # Connection for adding/deleting next step (select motor units widget)
        next_w_name = "selectmu"
        findmu_w.motor_units_found.connect(self.add_selectmu_widget)

        # Connection for enabling/disabling next step (select motor units)
        findmu_w.motor_units_found.connect(
            lambda motor_units_found, w_name=next_w_name: self.enable_analysis_toolbar_button(
                motor_units_found, w_name
            )
        )

        # TODO: connect motor_units_found to resetting GUI
        # need to reset before add next widget

    def add_selectmu_connections(self):
        """
        Add connections for select motor units (selectmu) widget:
            - Update list of motor units to analyse when selection changes.

        """

        selectmu_w = self.widgets["analysis"].widgets["selectmu"]
        selectmu_w.motor_units_updated.connect(self.update_motor_units_to_analyse)

    def add_localise_connections(self):
        """
        Add connections for localise fibres (localise) widget:
            - Add/update jitter widget when perform localisation by clicking apply button
        """

        localise_w = self.widgets["analysis"].widgets["localise"]
        localise_w.widgets["buttons"].widgets["apply"].clicked.connect(self.add_jitter_widget)

    def update_toolbar_connections(self):
        """
        Connects toolbar buttons to analysis widgets
        This method is called repeatedly as more analysis widgets are added.
        """

        print("Updating toolbar connections")
        for w_name in self.widgets["analysis"].widgets.keys():
            self.widgets["analysistoolbar"].widgets[w_name].clicked.connect(
                lambda checked=None, w_name=w_name: self.widgets["analysis"].show_widget(w_name)
            )
            print(w_name)

    def update_raw_emg_model_and_settings_model(
        self, raw_emg_model: EMGDataRawModel, settings_model: EMGSettingsModel
    ):
        """
        Slot for updating raw EMG model and settings model.
        Also updates the preprocess widget with this data.
        """

        self.emg_model["raw"] = raw_emg_model
        self.settings_model = settings_model

        # Also save original settings model as a separate variable that will not be
        # changed (deep copy) - allows resetting of the downstream settings if partially
        # re-do the analysis
        self.settings_model_original = deepcopy(settings_model)

        # Use data to make preprocessing widget
        self.add_preprocess_widget()

    def update_preproc_emg_model_and_preprocess_settings(
        self,
        preproc_emg_model: EMGDataPreprocModel,
        preprocess_settings_model: EMGPreprocSettingsModel,
    ):
        """
        Slot for updating preprocessed EMG model and the applied preprocessing settings.
        Also updates channel selection widget with the preprocessed data.
        Resets any downstream steps.
        """

        self.emg_model["preproc"] = preproc_emg_model
        if self.settings_model:
            self.settings_model.preprocess_settings = preprocess_settings_model.settings
        else:
            raise ValueError("settings_model must be added to main window before preprocessing")

        # Remove any downstream widgets
        self.reset_downstream_steps_of_gui("preprocess")

        # Use data to make channels widget
        self.add_channels_widget()

    def update_bad_chan_idx(self, bad_chan_idx):
        """
        Updates the list of bad channels that should not be included in the analysis.
        Unlike most other widgets, these changes do not need to be applied before
        proceeding to next step of the analysis - the next step (find motor units) is
        already enabled. As such, this method also updates the findmu widget that uses
        this data.
        """

        # If indices are the same, do not update and do not make new find MU widget
        if self.bad_chan_idx == bad_chan_idx:
            return
        else:
            # Reset downstream steps of GUI
            self.reset_downstream_steps_of_gui("channels")

            # Update bad channels
            self.bad_chan_idx = bad_chan_idx
            print(self.bad_chan_idx)

            # Update in preprocessed data and reconstruction analysis object
            self.emg_model["preproc"].emg_data.set_bad_chan(self.bad_chan_idx)
            if self.settings_model:
                reconstruct = EMGAnalysisReconstruct(
                    emg_data_preproc=self.emg_model["preproc"].emg_data,
                    mu_settings=self.settings_model.mu_settings,
                    recon_settings=self.settings_model.recon_settings,
                    mu_cluster_settings=self.settings_model.mu_cluster_settings,
                    mu_jitter_settings=self.settings_model.mu_jitter_settings,
                )
                self.reconstruct_model = EMGAnalysisReconstructModel(reconstruct)
            else:
                raise ValueError(
                    "settings_model must be added to main window before"
                    + " fibre reconstruction analysis."
                )

            # Update find MU widget
            self.add_findmu_widget()

    def update_motor_units_to_analyse(self, motor_units_idx):
        """
        Updates the list of motor units that should be further analysed in the localise
        fibres and jitter analyse widgets.
        """

        # If indices are the same, do not need to update
        if self.motor_units_to_analyse == motor_units_idx:
            return
        else:
            # Reset downstream steps since motor units changed
            self.reset_downstream_steps_of_gui("selectmu")

            # Update list of motor units
            self.motor_units_to_analyse = motor_units_idx
            print(f"Motor units to analyse updated: {self.motor_units_to_analyse}")

            # Create localise widget
            self.add_localise_widget()

        # Enable/disable localise fibre button on toolbar depepnding on if motor units
        # have been selected
        if self.motor_units_to_analyse:
            self.widgets["analysistoolbar"].widgets["localise"].setEnabled(True)
        else:
            self.widgets["analysistoolbar"].widgets["localise"].setEnabled(False)

    def connect_next_button_to_analysis_widget(self, next_button, w_name: str):
        """
        Connect the "next" button on an analysis step to the corresponding widget for
        the next analysis step.
        Also creates the connection to update the active button on the analysis toolbar
        so the toolbar state matches the currently displayed widget even if navigate
        using the "next" buttons.
        """

        next_button.clicked.connect(
            lambda checked=None, w_name=w_name: self.widgets["analysis"].show_widget(w_name)
        )
        next_button.clicked.connect(
            lambda checked=None, w_name=w_name: self.click_analysis_toolbar_button(w_name)
        )

    def click_analysis_toolbar_button(self, w_name: str):
        """
        Clicks on the w_name button in the analysis toolbar to make it the active
        button.
        Used as a slot for clicking the "next" buttons on the analysis step widgets
        (as an alternative to using the toolbar to navigate).
        """

        self.widgets["analysistoolbar"].widgets[w_name].toggle()

    def enable_analysis_toolbar_button(self, previous_step_finished: bool, w_name: str):
        """
        Enable/disable button in analysis toolbar based on whether the previous step is
        finished
        """
        self.widgets["analysistoolbar"].widgets[w_name].setEnabled(previous_step_finished)

    def add_widget_to_analysis_steps(self, w, w_name: str):
        """
        Add new widget w with name w_name to the stack of analysis step widgets.
        Update the toolbar connections to include this new widget.
        """

        # Add widget to layout and dictionary of analysis widgets
        analysis_w = self.widgets["analysis"]
        analysis_w.widgets[w_name] = w
        analysis_w.layout.addWidget(analysis_w.widgets[w_name])

        # Update toolbar connections
        self.update_toolbar_connections()

    def add_preprocess_widget(self):
        """
        Add preprocessing widget using data stored in the main window.
        """

        # Extract preprocessing settings
        if self.settings_model:
            preprocess_settings_model = EMGPreprocSettingsModel(
                self.settings_model.preprocess_settings
            )
        else:
            raise ValueError("settings_model must be added to main window before preprocessing")

        # Create widget and add to stack of analysis step widgets
        w_name = "preprocess"
        w = PreprocWidget(self.emg_model["raw"], preprocess_settings_model, self.emg_clrs)
        self.add_widget_to_analysis_steps(w, w_name)

        # Add connection to load step next button of previous step
        next_button = self.widgets["analysis"].widgets["load"].widgets["run"].widgets["next"]
        self.connect_next_button_to_analysis_widget(next_button, w_name)

        # Add connections to signals from preprocessing widget
        self.add_preprocess_connections()

    def add_channels_widget(self):
        """
        Add widget for channel selection once preprocessing is finished/updated.
        Also triggers initial creation of the findmu widget since there is no analysis
        that needs to be applied in the channels widget.
        """

        # Create widget and add to stack of analysis step widgets
        w_name = "channels"
        w = ChannelsWidget(self.emg_model["raw"], self.emg_model["preproc"], self.emg_clrs)
        self.add_widget_to_analysis_steps(w, w_name)

        # Enable toolbar button
        self.enable_analysis_toolbar_button(True, "channels")

        # Add connection to next button of previous step
        next_button = (
            self.widgets["analysis"].widgets["preprocess"].widgets["buttons"].widgets["next"]
        )
        self.connect_next_button_to_analysis_widget(next_button, w_name)

        # Add connection for next button (to update bad channels)
        self.add_channels_connections()

        # Create reconstruction analysis data
        if self.settings_model:
            reconstruct = EMGAnalysisReconstruct(
                emg_data_preproc=self.emg_model["preproc"].emg_data,
                mu_settings=self.settings_model.mu_settings,
                recon_settings=self.settings_model.recon_settings,
                mu_cluster_settings=self.settings_model.mu_cluster_settings,
                mu_jitter_settings=self.settings_model.mu_jitter_settings,
            )
            self.reconstruct_model = EMGAnalysisReconstructModel(reconstruct)
        else:
            raise ValueError(
                "settings_model must be added to main window before"
                + " fibre reconstruction analysis."
            )

        # Add find MU widget
        self.add_findmu_widget()

    def add_findmu_widget(self):
        """
        Add widget for finding motor units.
        """

        # Create widget and add to stack of analysis step widgets
        w_name = "findmu"
        if self.reconstruct_model:
            w = FindMUWidget(self.reconstruct_model)
        else:
            raise ValueError(
                "GUI model for fibre reconstruction analysis must be created before "
                + "creating widgets for this analysis."
            )
        self.add_widget_to_analysis_steps(w, w_name)

        print("Channels to analyse: ")
        reconstruct = w.reconstruct_model.reconstruct
        print(reconstruct.emg_data_preproc.chan.analyse_chan)

        # Enable toolbar button
        self.enable_analysis_toolbar_button(True, w_name)

        # Add connection to next button of previous step
        next_button = self.widgets["analysis"].widgets["channels"].widgets["next"]
        self.connect_next_button_to_analysis_widget(next_button, w_name)

        # Connections to next widget
        self.add_findmu_connections()

    def add_selectmu_widget(self, motor_units_found: bool):
        """
        Add widget for selecting motor units for downstream analysis if motor units
        have been found (i.e., motor_units_found = True). Otherwise, delete the widget
        if it exists.
        Slot for found_motor_units signal of findmu widget.
        """

        w_name = "selectmu"

        if motor_units_found:  # if motor units found, create widget
            print("creating selectmu widget")
            # Create widget and add to stack of analysis step widgets with toolbar connections
            if self.reconstruct_model:
                w = SelectMUWidget(self.reconstruct_model, parent=self)
            else:
                raise ValueError(
                    "GUI model for fibre reconstruction analysis must be created before "
                    + "creating widgets for this analysis."
                )
            self.add_widget_to_analysis_steps(w, w_name)

            # Enable toolbar button
            self.enable_analysis_toolbar_button(True, w_name)

            # Add connection to next button of previous step
            next_button = (
                self.widgets["analysis"].widgets["findmu"].widgets["buttons"].widgets["next"]
            )
            self.connect_next_button_to_analysis_widget(next_button, w_name)

            # Add connections
            self.add_selectmu_connections()

        else:  # Otherwise, delete widget if it exists
            print("deleting select mu widget")
            w = self.widgets["analysis"].widgets.pop(w_name, None)
            if w:
                w.deleteLater()
                print(f"Deleted {w_name} widget")

    def add_localise_widget(self):
        """
        Add widget for localising fibres in selected motor units.

        """

        w_name = "localise"

        if self.reconstruct_model:
            # Create widget and add to stack of analysis step widgets with toolbar connections
            w = LocaliseWidget(self.reconstruct_model, self.motor_units_to_analyse, parent=self)
        else:
            raise ValueError(
                "GUI model for fibre reconstruction analysis must be created before "
                + "creating widgets for this analysis."
            )
        self.add_widget_to_analysis_steps(w, w_name)

        # Enable toolbar button
        self.enable_analysis_toolbar_button(True, w_name)

        # Add connection to next button of previous step
        next_button = self.widgets["analysis"].widgets["selectmu"].widgets["next"]
        self.connect_next_button_to_analysis_widget(next_button, w_name)

        # Add connections
        self.add_localise_connections()

    def add_jitter_widget(self):
        """
        Add widget for jitter analysis results in selected motor units.

        """
        w_name = "jitter"

        if self.reconstruct_model:
            # Perform jitter analysis (no apply button in this widget since settings are fixed)
            for mu_idx in self.motor_units_to_analyse:
                self.reconstruct_model.reconstruct.mu_jitter_analysis(mu_idx)

            # Create widget and add to stack of analysis step widgets with toolbar connections
            w = JitterWidget(self.reconstruct_model, self.motor_units_to_analyse, parent=self)
            print("Added jitter widget")
        else:
            raise ValueError(
                "GUI model for fibre reconstruction analysis must be created before "
                + "creating widgets for this analysis."
            )
        self.add_widget_to_analysis_steps(w, w_name)

        # Enable toolbar button
        self.enable_analysis_toolbar_button(True, w_name)

        # Add connection to next button of previous step
        next_button = (
            self.widgets["analysis"].widgets["localise"].widgets["buttons"].widgets["next"]
        )
        self.connect_next_button_to_analysis_widget(next_button, w_name)
