#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for selecting channels to use for analysis.
"""

from pymicroemg.emg_channels import EMGChannels

from PySide6.QtWidgets import QWidget, QCheckBox, QGridLayout, QHBoxLayout, QVBoxLayout

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

    def __init__(self, chan: EMGChannels, chan_clrs: list[str], max_chan: int = 32, parent=None):
        # max_chan = maximum number of channels to put in one column
        # chan_clrs should be the same length as the number of channels

        super().__init__(parent)

        # All channel names (+ "channel")
        chan_names = chan.chan_names
        # chan_names = ["channel " + i for i in chan_names]

        # Make checkbox for each channel
        self.widgets = {"checkboxes": list()}
        for chan, clr in zip(chan_names, chan_clrs):
            # w = ColourfulChannelCheckBox(chan, clr, parent=self)
            w = CheckBoxChannel(chan, parent=self)
            w.setStyleSheet("color: " + clr)

            self.widgets["checkboxes"].append(w)
            print(chan)

        # Add checkboxes to layout
        # Max number of channels per column is max_chan
        row = 0
        col = 0
        layout = QGridLayout()
        for w in self.widgets["checkboxes"]:
            layout.addWidget(w, row, col)  # layout
            row += 1
            if row == max_chan:  # reset row number
                row = 0
                col += 1
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(75)
        self.setLayout(layout)


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
            "exclude": HighlightedLabel("Excluded channels:", parent=self),
        }
        self.widgets["exclude"].setFixedWidth(150)
        self.widgets["exclude"].setWordWrap(True)

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

        for w in self.widgets["checkboxes"].widgets["checkboxes"]:
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

    def __init__(
        self,
        raw_emg_model: EMGDataRawModel,
        preproc_emg_model: EMGDataPreprocModel,
        emg_clrs: list[str],
        parent=None,
    ):
        super().__init__(parent)

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
            "next": NextButton(parent=self),
        }

        # Add preprocessed data to EMG viewer
        self.widgets["viewer"].add_preproc_emg_model(preproc_emg_model)

        # Add widgets to layout
        layout = QGridLayout()
        layout.addWidget(self.widgets["title"], 0, 0, 1, 2)  # span 2 columns
        layout.addWidget(self.widgets["channels"], 1, 0)
        layout.addWidget(self.widgets["viewer"], 1, 1, 2, 1)  # span 2 rows
        layout.addWidget(self.widgets["next"], 2, 0)

        self.setLayout(layout)
