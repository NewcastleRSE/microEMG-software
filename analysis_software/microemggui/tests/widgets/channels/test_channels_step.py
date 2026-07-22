#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the channels step widget.
"""

import pytest
from pytest_check import check

from pymicroemg.emg_preproc_settings import EMGPreprocSettings
from pymicroemg.emg_files import EMGFiles
import pymicroemg.helper_config as cfg

from microemggui.models.emg import EMGDataRawModel, EMGDataPreprocModel
from microemggui.widgets.channels.channels_step import ChannelsWidget


pytestmark = pytest.mark.demo_data


# --- Fixture ---


# Fixture for raw and preprocessed EMG data models
# Currently only uses one EMG recording, but set up to add additional recordings
# Also only uses one preprocessing setting (= no preprocessing applied)
@pytest.fixture(params=[0], ids=["demo EMG recording #0"])
def emg_models(request, ensure_demo_data):
    # Load EMG data
    recording_num = request.param
    emg_dir, _ = cfg.get_recording_path_and_id(recording_num)
    emg_files = EMGFiles(emg_dir)
    emg_data = emg_files.load_emg_data()
    emg_data.trim_emg_ts(0, 10)  # shorten so tests run faster

    # Preprocessing settings (with no preprocessing applied)
    settings = EMGPreprocSettings()

    # "Preprocessed" EMG data (no preprocessing applied for speed)
    emg_data_preproc = emg_data.preprocess(settings)

    # GUI models of data
    emg_models = {
        "raw": EMGDataRawModel(emg_data),
        "preproc": EMGDataPreprocModel(emg_data_preproc),
    }

    return emg_models


# Colors for EMG viewer
@pytest.fixture
def emg_clrs():
    emg_clrs = ["#5F4690", "#1D6996"]

    return emg_clrs


# --- Functions for repeated tests ---


@check.check_func
def assert_check_state_of_all_channel_checkboxes(window, is_checked):
    checkboxes = window.widgets["channels"].widgets["checkboxes"].widgets["checkboxes"]
    for i in range(window.n_chan):
        with check:
            assert checkboxes[i].isChecked() == is_checked


# --- Tests ---


def test_select_all_and_all_channel_checkboxes_initially_checked(qtbot, emg_models, emg_clrs):
    # Set up window
    window = ChannelsWidget(emg_models["raw"], emg_models["preproc"], emg_clrs)
    window.show()
    qtbot.addWidget(window)

    # Confirm that select all checkbox is checked
    all_checkbox = window.widgets["channels"].widgets["all"]
    with check:
        assert all_checkbox.isChecked()

    # Confirm all channel checkboxes checked
    assert_check_state_of_all_channel_checkboxes(window, is_checked=True)


def test_clicking_select_all_updates_all_channel_checkboxes(qtbot, emg_models, emg_clrs):
    # Set up window
    window = ChannelsWidget(emg_models["raw"], emg_models["preproc"], emg_clrs)
    window.show()
    qtbot.addWidget(window)

    # Uncheck select all checkbox
    # (important - must click, not change state programmatically)
    all_checkbox = window.widgets["channels"].widgets["all"]
    all_checkbox.click()  # initially checked, so unchecks

    # Confirm that select all checkbox is unchecked
    with check:
        assert all_checkbox.isChecked() is False

    # Confirm all channel checkboxes unchecked
    assert_check_state_of_all_channel_checkboxes(window, is_checked=False)

    # Recheck select all
    all_checkbox.click()  # checks

    # Confirm that select all checkbox is checked
    with check:
        assert all_checkbox.isChecked()

    # Confirm all channel checkboxes checked
    assert_check_state_of_all_channel_checkboxes(window, is_checked=True)


@pytest.mark.parametrize("chan", [0, 15, 31, 63])
def test_toggling_one_channel_checkbox_updates_select_all(qtbot, emg_models, emg_clrs, chan):
    # Set up window
    window = ChannelsWidget(emg_models["raw"], emg_models["preproc"], emg_clrs)
    window.show()
    qtbot.addWidget(window)

    # Checkboxes
    all_checkbox = window.widgets["channels"].widgets["all"]
    checkboxes = window.widgets["channels"].widgets["checkboxes"].widgets["checkboxes"]

    if chan <= window.n_chan - 1:  # Only test if channel exists
        # Uncheck channel checkbox (must click - will uncheck)
        checkboxes[chan].click()

        # Confirm channel checkbox unchecked
        with check:
            assert checkboxes[chan].isChecked() is False

        # Confirm select all unchecked
        with check:
            assert all_checkbox.isChecked() is False

        # Confirm all other channels checked
        for i in range(window.n_chan):
            if i != chan:
                with check:
                    assert checkboxes[i].isChecked()

        # Click channel checkbox to recheck
        checkboxes[chan].click()

        # Confirm select all checked
        with check:
            assert all_checkbox.isChecked()

        # Confirm all channels checked
        assert_check_state_of_all_channel_checkboxes(window, is_checked=True)


@pytest.mark.parametrize("chan", [0, 15, 31, 63])
def test_select_all_checks_all_channel_checkboxes_after_one_channel_unchecked(
    qtbot, emg_models, emg_clrs, chan
):
    # Set up window
    window = ChannelsWidget(emg_models["raw"], emg_models["preproc"], emg_clrs)
    window.show()
    qtbot.addWidget(window)

    # Checkboxes
    all_checkbox = window.widgets["channels"].widgets["all"]
    checkboxes = window.widgets["channels"].widgets["checkboxes"].widgets["checkboxes"]

    if chan <= window.n_chan - 1:  # Only test if channel exists
        # Uncheck channel checkbox
        checkboxes[chan].click()

        # Confirm select all unchecked
        with check:
            assert all_checkbox.isChecked() is False

        # Click select all checkbox to recheck
        all_checkbox.click()

        # Confirm select all checked
        with check:
            assert all_checkbox.isChecked()

        # Confirm all channels checked
        assert_check_state_of_all_channel_checkboxes(window, is_checked=True)


@pytest.mark.parametrize("channels", [[0], [0, 15], [3, 5, 0, 10], [63, 30]])
def test_unchecking_channels_adds_channels_to_bad_chan_idx(qtbot, emg_models, emg_clrs, channels):
    # Set up window
    window = ChannelsWidget(emg_models["raw"], emg_models["preproc"], emg_clrs)
    window.show()
    qtbot.addWidget(window)

    # Checkboxes
    checkboxes = window.widgets["channels"].widgets["checkboxes"].widgets["checkboxes"]

    # List of channels that should be stored in bad channel indices
    should_be_in_bad_chan_idx = list()
    for chan in channels:
        if chan <= window.n_chan - 1:  # Only click if channel exists
            # Add to list
            should_be_in_bad_chan_idx.append(chan)
            print(should_be_in_bad_chan_idx)

            # Uncheck channel checkbox
            checkboxes[chan].click()

    should_be_in_bad_chan_idx.sort()
    assert window.bad_chan_idx == should_be_in_bad_chan_idx


@pytest.mark.parametrize("channels", [[0], [0, 15], [3, 5, 0, 10], [63, 30]])
def test_rechecking_channels_removes_from_bad_chan_idx(qtbot, emg_models, emg_clrs, channels):
    # Set up window
    window = ChannelsWidget(emg_models["raw"], emg_models["preproc"], emg_clrs)
    window.show()
    qtbot.addWidget(window)

    # Checkboxes
    checkboxes = window.widgets["channels"].widgets["checkboxes"].widgets["checkboxes"]

    for chan in channels:
        if chan <= window.n_chan - 1:  # Only click if channel exists
            # Uncheck channel checkbox
            checkboxes[chan].click()

            # Recheck channel checkbox
            checkboxes[chan].click()

    assert window.bad_chan_idx == []


def test_unchecking_select_all_adds_all_channels_to_bad_chan_idx(qtbot, emg_models, emg_clrs):
    # Set up window
    window = ChannelsWidget(emg_models["raw"], emg_models["preproc"], emg_clrs)
    window.show()
    qtbot.addWidget(window)

    # Uncheck select all checkbox
    # (important - must click, not change state programmatically)
    all_checkbox = window.widgets["channels"].widgets["all"]
    all_checkbox.click()  # initially checked, so unchecks

    # Confirm all channels stored in bad chan indices
    should_be_in_bad_chan_idx = [i for i in range(window.n_chan)]
    assert window.bad_chan_idx == should_be_in_bad_chan_idx


def test_checking_select_all_removes_all_channels_from_bad_chan_idx(qtbot, emg_models, emg_clrs):
    # Set up window
    window = ChannelsWidget(emg_models["raw"], emg_models["preproc"], emg_clrs)
    window.show()
    qtbot.addWidget(window)

    # Uncheck select all checkbox (important - must click, not change state programmatically)
    all_checkbox = window.widgets["channels"].widgets["all"]
    all_checkbox.click()  # initially checked, so unchecks

    # Recheck
    all_checkbox.click()

    # Confirm no channels stored in bad chan indices
    assert window.bad_chan_idx == []


def test_unchecking_select_all_disables_next_button(qtbot, emg_models, emg_clrs):
    # Set up window
    window = ChannelsWidget(emg_models["raw"], emg_models["preproc"], emg_clrs)
    window.show()
    qtbot.addWidget(window)

    # Uncheck select all checkbox
    # (important - must click, not change state programmatically)
    all_checkbox = window.widgets["channels"].widgets["all"]
    all_checkbox.click()  # initially checked, so unchecks

    # Confirm next button is disabled
    assert window.widgets["next"].isEnabled() is False


def test_rechecking_select_all_enables_next_button(qtbot, emg_models, emg_clrs):
    # Set up window
    window = ChannelsWidget(emg_models["raw"], emg_models["preproc"], emg_clrs)
    window.show()
    qtbot.addWidget(window)

    # Uncheck and check select all checkbox
    # (important - must click, not change state programmatically)
    all_checkbox = window.widgets["channels"].widgets["all"]
    all_checkbox.click()  # initially checked, so unchecks
    all_checkbox.click()  # rechecks

    # Confirm next button is enabled
    assert window.widgets["next"].isEnabled()
