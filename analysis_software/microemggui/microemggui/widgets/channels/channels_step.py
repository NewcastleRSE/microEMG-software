#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for selecting channels to use for analysis.
"""

from pymicroemg.emg_channels import EMGChannels

from PySide6.QtWidgets import QWidget, QCheckBox, QGridLayout, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Signal

from microemggui.widgets.preproc.preproc_step import EMGViewerTabbedWidget
from microemggui.models.emg import EMGDataRawModel, EMGDataPreprocModel
from microemggui.widgets.base import (
    CheckBoxChannel,
    CheckBoxChannelLabel,
    HighlightedLabel,
    SectionTitle,
    LargePushButton,
)

# --- Component widgets ---


class ColourfulChannelCheckBox(QWidget):
    # Option for adding checkbox text that is not coloured to match emg viewer
    # TODO: remove if not used
    def __init__(self, chan_name: str, chan_clr: str, parent=None):
        super().__init__(parent)

        self.checkbox = CheckBoxChannel("channel", parent=self)
        label = CheckBoxChannelLabel(chan_name, parent=self)
        label.setStyleSheet("color: " + chan_clr)

        layout = QHBoxLayout()
        layout.addWidget(self.checkbox)
        layout.addWidget(label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def setChecked(self, is_checked):
        self.checkbox.setChecked(is_checked)


class ChannelsCheckBoxes(QWidget):
    # Checkboxes for each channel

    # Signal to emit indicating if each channel is checked
    # Sends bool for check state (bool) and channel index, counting from 0 (int)
    chan_toggled = Signal(bool, int)

    def __init__(self, chan: EMGChannels, chan_clrs: list[str], max_chan: int = 32, parent=None):
        # max_chan = maximum number of channels to put in one column
        # chan_clrs should be the same length as the number of channels

        super().__init__(parent)

        # All channel names (+ "channel")
        chan_names = chan.chan_names
        n_chan = len(chan_names)

        # Make checkbox for each channel
        self.widgets = {"checkboxes": dict()}
        for i in range(n_chan):
            w = CheckBoxChannel(chan_names[i], parent=self)
            w.setStyleSheet("color: " + chan_clrs[i])

            # Use channel index i as the label so easy to determine which channels are
            # checked/unchecked
            self.widgets["checkboxes"][i] = w

        # Add checkboxes to layout
        # Max number of channels per column is max_chan
        row = 0
        col = 0
        layout = QGridLayout()
        for w in self.widgets["checkboxes"].values():
            layout.addWidget(w, row, col)  # layout
            row += 1
            if row == max_chan:  # reset row number
                row = 0
                col += 1
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(75)
        self.setLayout(layout)

        # Connections

        # Send index of channel with check state when channel is toggled
        for idx, w in self.widgets["checkboxes"].items():
            w.toggled.connect(lambda checked, idx=idx: self.chan_toggled.emit(checked, idx))


class SelectChannels(QWidget):
    # Widget for selecting channels to include in the analysis
    # Channel checkboxes with related widgets (select all/none and label for channels
    # that will be excluded from the analysis)

    def __init__(self, chan: EMGChannels, chan_clrs: list[str], parent=None):
        # chan_clrs should be the same length as the number of channels

        super().__init__(parent)

        # Create widgets
        self.widgets = {
            "all": QCheckBox("Select all", parent=self),
            "checkboxes": ChannelsCheckBoxes(chan, chan_clrs, parent=self),
        }

        # Add to layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Connections
        self.connect_channel_checkboxes_to_select_all_checkbox()

    def connect_channel_checkboxes_to_select_all_checkbox(self):
        # Connect select all checkbox to all channel checkboxes
        # Select all checkbox can check/uncheck all channel checkboxes
        # TODO: Check state of select all also determined by state of channel checkboxes

        # Connect select all checkbox to all channel checkboxes
        self.widgets["all"].toggled.connect(self.check_or_uncheck_all)
        self.widgets["all"].setChecked(True)  # initial state: all checked

        # TODO: If any one checkbox unchecked, uncheck select all; otherwise, checked

    def check_or_uncheck_all(self, checked: bool):
        # Check or uncheck all channel checkboxes
        # Slot for self.widgets["all"] checkbox (select all/none)

        for w in self.widgets["checkboxes"].widgets["checkboxes"].values():
            w.setChecked(checked)


class NextButton(LargePushButton):
    # Button for proceeding to the next step

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Next")
        self.setToolTip("Proceed to next step")


# --- Channels selection widget ----


class ChannelsWidget(QWidget):
    # Widgets for channels to include in the analysis

    # Signal for sending updated indices of bad channels
    # TODO: remove if not needed
    bad_chan_updated = Signal(list[int])

    def __init__(
        self,
        raw_emg_model: EMGDataRawModel,
        preproc_emg_model: EMGDataPreprocModel,
        emg_clrs: list[str],
        parent=None,
    ):
        super().__init__(parent)

        # Boolean list to store whether each channel is checked (all initially selected)
        self.chan_checked = [True for i in range(raw_emg_model.emg_data.n_chan)]
        self.bad_chan_idx = []  # Indices of bad channels

        # Create widgets
        # Make viewer first so its full colour array (with repeated colours) can be
        # passed to the channel checkboxes
        viewer = EMGViewerTabbedWidget(raw_emg_model, emg_clrs)  # make viewer first
        self.widgets = {
            "title": SectionTitle("Select channels to analyse", parent=self),
            "channels": SelectChannels(
                chan=raw_emg_model.emg_data.chan, chan_clrs=viewer.emg_clrs, parent=self
            ),
            "viewer": viewer,
            "exclude": HighlightedLabel("", parent=self),
            "next": NextButton(parent=self),
        }
        self.widgets["exclude"].setWordWrap(True)
        self.update_exclude_message()

        # Add preprocessed data to EMG viewer
        self.widgets["viewer"].add_preproc_emg_model(preproc_emg_model)

        # Add widgets to layout
        # TODO: remove if keep current layout
        # layout = QGridLayout()
        # layout.addWidget(self.widgets["title"], 0, 0, 1, 2)  # span 2 columns
        # layout.addWidget(self.widgets["channels"], 1, 0)
        # layout.addWidget(self.widgets["viewer"], 1, 1, 2, 1)  # span 2 rows
        # layout.addWidget(self.widgets["next"], 2, 0)

        layout = QGridLayout()
        layout.addWidget(self.widgets["title"], 0, 0, 1, 2)  # span 2 columns
        layout.addWidget(self.widgets["channels"], 1, 0)
        layout.addWidget(self.widgets["viewer"], 1, 1)  # span 2 rows
        layout.addWidget(self.widgets["exclude"], 2, 0, 1, 2)
        layout.addWidget(self.widgets["next"], 3, 0)

        self.setLayout(layout)

        # Connections

        # For updating chan_checked based on checkbox state
        self.widgets["channels"].widgets["checkboxes"].chan_toggled.connect(
            self.update_chan_checked
        )

    def update_chan_checked(self, checked: bool, idx: int):
        # Update check status of a channel; slot for chan_toggled

        self.chan_checked[idx] = checked
        print(self.chan_checked)

        # Update bad channels
        self.update_bad_chan_idx()

    def update_bad_chan_idx(self):
        # Updates indices of channels that are unchecked (i.e., "bad" channels)
        # Also updates corresponding message for channels that will be excluded

        self.bad_chan_idx = [i for i in range(len(self.chan_checked)) if not self.chan_checked[i]]
        print(self.bad_chan_idx)
        self.update_exclude_message()

    def update_exclude_message(self):
        # Update exclude message to list bad channels that will be excluded from the
        # analysis

        # Channel  names - need to add one to go from indices to labels
        bad_chan_names = [str(i + 1) for i in self.bad_chan_idx]

        # Text depends on the number of bad channels
        if len(self.bad_chan_idx) == 1:
            text = "Will exclude channel " + bad_chan_names[0]
        elif len(self.bad_chan_idx) > 1:
            text = "Will exclude channels " + ", ".join(bad_chan_names)
        else:
            text = "All channels will be included in the analysis"

        # Set text
        self.widgets["exclude"].setText(text)


# TODO:
# get list of bad channels from chan_checked
# add list of bad channels to preprocessed data (probably in main window)
