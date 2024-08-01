#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for selecting channels to use for analysis.
"""
from typing import Any
from pymicroemg.emg_channels import EMGChannels

from PySide6.QtWidgets import (
    QWidget,
    QCheckBox,
    QGridLayout,
    QVBoxLayout,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal

from microemggui.widgets.preproc.preproc_step import EMGViewerTabbedWidget
from microemggui.models.emg import EMGDataRawModel, EMGDataPreprocModel
from microemggui.widgets.base import (
    CheckBoxChannel,
    HighlightedLabel,
    SectionTitle,
    LargePushButton,
)

# --- Component widgets ---


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
        self.widgets: dict[str, dict[int, Any]] = {"checkboxes": dict()}
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
        layout.setContentsMargins(0, 0, 50, 0)
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(50)
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
        self.widgets: dict[str, Any] = {
            "all": QCheckBox("Select all", parent=self),
            "checkboxes": ChannelsCheckBoxes(chan, chan_clrs, parent=self),
        }

        # Add to layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignLeft)
        self.setLayout(layout)

        # Connections
        self.connect_channel_checkboxes_to_select_all_checkbox()

    def connect_channel_checkboxes_to_select_all_checkbox(self):
        # Connect select all checkbox to all channel checkboxes
        # Select all checkbox can check/uncheck all channel checkboxes

        # Connect select all checkbox to all channel checkboxes
        # Use "clicked" signal so not emitted if change checkbox state programmatically
        self.widgets["all"].clicked.connect(self.check_or_uncheck_all)
        self.widgets["all"].click()  # click so initial state is all checked

        # Note: in ChannelsWidget, the check state of the select all checkbox is also
        # updated if all channels are checked/unchecked by checking individual checkboxes.
        # This update is performed in ChannelsWidget so that the bad_chan_idx
        # attribute can be used to determine the check state of the select all checkbox.

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

    def change_enabled(self, enabled: bool):
        # Method for enable/disabling button based on whether sufficient channels are
        # selected

        self.setEnabled(enabled)


# --- Channels selection widget ----


class ChannelsWidget(QWidget):
    # Widgets for channels to include in the analysis

    # Signal for sending updated indices of bad channels
    bad_chan_updated = Signal(list)

    # Signal for indicating whether minimum number of channels have been selected
    min_chan_selected = Signal(bool)

    def __init__(
        self,
        raw_emg_model: EMGDataRawModel,
        preproc_emg_model: EMGDataPreprocModel,
        emg_clrs: list[str],
        min_chan: int = 1,
        parent=None,
    ):
        # min_chan = minimum number of channels needed to proceed with the analysis

        super().__init__(parent)

        # Total number of channels for easy reference
        self.n_chan = raw_emg_model.emg_data.n_chan
        self.min_chan = min_chan  # Number of selected channels needed to proceed with analysis

        # Boolean list to store whether each channel is checked (all initially selected)
        self.chan_checked = [True for i in range(self.n_chan)]
        self.bad_chan_idx: list[int] = []  # Indices of bad channels

        # Create widgets
        # Make viewer first so its full colour array (with repeated colours) can be
        # passed to the channel checkboxes
        viewer = EMGViewerTabbedWidget(raw_emg_model, emg_clrs)  # make viewer first
        self.widgets: dict[str, Any] = {
            "title": SectionTitle("Select channels", parent=self),
            "channels": SelectChannels(
                chan=raw_emg_model.emg_data.chan, chan_clrs=viewer.emg_clrs, parent=self
            ),
            "viewer": viewer,
            "exclude": HighlightedLabel("", parent=self),
            "next": NextButton(parent=self),
        }

        # Properties of exclude message - word wrap, fixed height
        self.widgets["exclude"].setWordWrap(True)
        self.widgets["exclude"].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.widgets["exclude"].setObjectName("channels_widget_exclude")
        self.update_exclude_message()

        # Add preprocessed data to EMG viewer
        self.widgets["viewer"].add_preproc_emg_model(preproc_emg_model)

        # Layout
        layout = QGridLayout()
        layout.addWidget(self.widgets["title"], 0, 0)
        layout.addWidget(self.widgets["channels"], 1, 0)
        layout.addWidget(self.widgets["viewer"], 0, 1, 4, 1)  # span 2 rows
        layout.addWidget(self.widgets["exclude"], 2, 0)  # span 2 columns
        layout.addWidget(self.widgets["next"], 3, 0)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        # Connections

        # For updating chan_checked based on checkbox state
        self.widgets["channels"].widgets["checkboxes"].chan_toggled.connect(
            self.update_chan_checked
        )

        # Emit channels when next button is clicked
        self.widgets["next"].clicked.connect(self.next_clicked)

    def selected_min_channels(self) -> bool:
        # Compute whether min number of channels are selected
        # Also emit signal indicating whether min number of channels have been selected
        # to disable/enable downstream steps in GUI.

        min_selected = self.n_chan - len(self.bad_chan_idx) >= self.min_chan
        self.min_chan_selected.emit(min_selected)
        return min_selected

    def update_chan_checked(self, checked: bool, idx: int):
        # Update check status of a channel; slot for chan_toggled

        self.chan_checked[idx] = checked

        # Update bad channels
        self.update_bad_chan_idx()

        # Uncheck select all checkbox if any bad channels
        self.update_select_all_checkbox()

    def update_bad_chan_idx(self):
        # Updates indices of channels that are unchecked (i.e., "bad" channels)
        # Also triggers downstream changes:
        #   1) Updates corresponding message for channels that will be excluded
        #   2) Enables/disables Next button based on whether enough channels selected

        self.bad_chan_idx = [i for i in range(len(self.chan_checked)) if not self.chan_checked[i]]
        self.update_exclude_message()
        self.widgets["next"].change_enabled(self.selected_min_channels())

    def update_select_all_checkbox(self):
        # Unchecks select all checkbox if any channels unchecked
        # Checks select all checkbox if all channels checked

        # Use self.bad_chan_idx as a quick way to see if any channels unchecked
        # (if not empty, channels are unchecked)
        if self.bad_chan_idx:
            self.widgets["channels"].widgets["all"].setChecked(False)
        else:
            self.widgets["channels"].widgets["all"].setChecked(True)

    def update_exclude_message(self):
        # Update exclude message to list bad channels that will be excluded from the
        # analysis

        # Channel  names - need to add one to go from indices to labels
        bad_chan_names = [str(i + 1) for i in self.bad_chan_idx]

        # Text depends on the number of bad channels
        # First check if sufficient number of channels are selected
        min_selected = self.selected_min_channels()

        if min_selected:  # Display info about excluded channels
            if len(self.bad_chan_idx) == 1:
                text = "Will exclude channel " + bad_chan_names[0] + "."
            elif len(self.bad_chan_idx) > 1:
                text = "Will exclude channels " + ", ".join(bad_chan_names) + "."
            else:
                text = "All channels will be included in the analysis."
        else:  # Indicate that more channels need to be selected
            if self.min_chan == 1:
                text = f"Select at least {self.min_chan} channel."
            else:
                text = f"Select at least {self.min_chan} channels."

        # Set text
        self.widgets["exclude"].setText(text)

    def next_clicked(self):
        # Slot for next button
        # Emits bad channel indices when next button clicked
        print("channels widget next clicked")
        self.bad_chan_updated.emit(self.bad_chan_idx)
