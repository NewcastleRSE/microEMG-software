"""
Tests for widget that loads microEMG recording.
"""

import pytest

from microemggui.models.emg import EMGDataRawModel
from microemggui.widgets.load.load_step import LoadWidget


# --- Fixtures ---


# --- Tests ---


def test_load_button_initially_disabled(qtbot):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Get widget for loading recording
    w_load = window.widgets["recording"]

    # Check that load button is disabled
    assert not w_load.widgets["load"].isEnabled()


# Current just one demo recording, but test set up to add additional ones
@pytest.mark.parametrize("recording_num", [0])
def test_load_button_enabled_when_select_demo_recording(qtbot, recording_num):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Get widgets for loading recording and selecting recording
    w_load = window.widgets["recording"]
    w_select = w_load.widgets["selectrecording"]

    # Change combobox to demo recording
    idx = w_select.demo_recording_num.index(recording_num)
    w_select.widgets["combobox"].setCurrentIndex(idx)

    # Check that load button is enabled
    assert w_load.widgets["load"].isEnabled()


@pytest.mark.parametrize("recording_num", [0])
def test_load_button_disabled_when_remove_demo_recording_selection(qtbot, recording_num):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Get widgets for loading recording and selecting recording
    w_load = window.widgets["recording"]
    w_select = w_load.widgets["selectrecording"]

    # Change combobox to demo recording
    idx = w_select.demo_recording_num.index(recording_num)
    w_select.widgets["combobox"].setCurrentIndex(idx)

    # Check that load button is enabled
    assert w_load.widgets["load"].isEnabled()

    # Change combobox back to empty (first index)
    w_select.widgets["combobox"].setCurrentIndex(0)

    # Check that load button is disabled
    assert not w_load.widgets["load"].isEnabled()


@pytest.mark.parametrize("recording_num", [0])
def test_can_load_demo_recording(qtbot, recording_num):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Get widgets for loading recording and selecting recording
    w_load = window.widgets["recording"]
    w_select = w_load.widgets["selectrecording"]

    # Check that no EMG files present initially
    assert not w_load.emg_model  # EMG model is None
    assert not w_load.emg_label  # No label

    # Change combobox to demo recording
    idx = w_select.demo_recording_num.index(recording_num)
    w_select.widgets["combobox"].setCurrentIndex(idx)

    # Click load button
    w_load.widgets["load"].click()

    # Check that EMG files are added
    assert w_load.emg_model  # EMG model is not None
    assert isinstance(w_load.emg_model, EMGDataRawModel)  # Check type
    assert w_load.emg_label  # Check that label exists


@pytest.mark.parametrize("recording_num", [0])
def test_that_changing_recording_selection_deletes_loaded_recording(qtbot, recording_num):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Get widgets for loading recording and selecting recording
    w_load = window.widgets["recording"]
    w_select = w_load.widgets["selectrecording"]

    # Change combobox to demo recording
    idx = w_select.demo_recording_num.index(recording_num)
    w_select.widgets["combobox"].setCurrentIndex(idx)

    # Click load button
    w_load.widgets["load"].click()

    # Change recording selection
    w_select.widgets["combobox"].setCurrentIndex(0)

    # Check that no EMG files are present
    assert not w_load.emg_model  # EMG model is not None
    assert not w_load.emg_label  # Check that no label


@pytest.mark.parametrize("recording_num", [0])
def test_that_changing_recording_path_to_empty_disables_load_button(qtbot, recording_num):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Get widgets for loading recording and selecting recording
    w_load = window.widgets["recording"]
    w_select = w_load.widgets["selectrecording"]

    # Change combobox to demo recording
    idx = w_select.demo_recording_num.index(recording_num)
    w_select.widgets["combobox"].setCurrentIndex(idx)

    # Check that load button is enabled
    assert w_load.widgets["load"].isEnabled()

    # Change recording path to empty
    w_select.recording_path_changed.emit("")

    # Check that load button is disabled
    assert not w_load.widgets["load"].isEnabled()


@pytest.mark.parametrize("recording_label", ["testlabel", "test label", "Test_Label", ""])
def test_that_changing_recording_label_updates_attribute_and_label_text(qtbot, recording_label):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Get widgets for loading recording, selecting recording, and displaying recording label
    w_load = window.widgets["recording"]
    w_select = w_load.widgets["selectrecording"]
    w_label = w_load.widgets["label"]

    # Change recording label
    w_select.recording_label_changed.emit(recording_label)

    # Check that label is updated (attribute and label text)
    assert w_load.emg_label == recording_label
    assert w_label.widgets["recording"].text() == recording_label
