"""
Tests for widget that loads microEMG recording and performs other analysis set ups.
"""

import pytest

from microemggui.models.emg import EMGDataRawModel
from microemggui.models.settings import EMGSettingsModel
from microemggui.widgets.load.load_step import LoadWidget


# --- Fixtures ---


# --- Reusable functions ---


def load_demo_recording(window, recording_num):
    # Get widgets for loading recording and selecting recording
    w_recording = window.widgets["recording"]
    w_select = w_recording.widgets["selectrecording"]

    # Change combobox to demo recording
    idx = w_select.demo_recording_num.index(recording_num)
    w_select.widgets["combobox"].setCurrentIndex(idx)

    # Click load button
    w_recording.widgets["load"].click()


# --- Tests for loading EMG recording ---


def test_load_button_initially_disabled(qtbot):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Get widget for loading recording
    w_recording = window.widgets["recording"]

    # Check that load button is disabled
    assert not w_recording.widgets["load"].isEnabled()


# Current just one demo recording, but test set up to add additional ones
@pytest.mark.parametrize("recording_num", [0])
def test_load_button_enabled_when_select_demo_recording(qtbot, recording_num):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Get widgets for loading recording and selecting recording
    w_recording = window.widgets["recording"]
    w_select = w_recording.widgets["selectrecording"]

    # Change combobox to demo recording
    idx = w_select.demo_recording_num.index(recording_num)
    w_select.widgets["combobox"].setCurrentIndex(idx)

    # Check that load button is enabled
    assert w_recording.widgets["load"].isEnabled()


@pytest.mark.parametrize("recording_num", [0])
def test_load_button_disabled_when_remove_demo_recording_selection(qtbot, recording_num):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Get widgets for loading recording and selecting recording
    w_recording = window.widgets["recording"]
    w_select = w_recording.widgets["selectrecording"]

    # Change combobox to demo recording
    idx = w_select.demo_recording_num.index(recording_num)
    w_select.widgets["combobox"].setCurrentIndex(idx)

    # Check that load button is enabled
    assert w_recording.widgets["load"].isEnabled()

    # Change combobox back to empty (first index)
    w_select.widgets["combobox"].setCurrentIndex(0)

    # Check that load button is disabled
    assert not w_recording.widgets["load"].isEnabled()


@pytest.mark.parametrize("recording_num", [0])
def test_can_load_demo_recording(qtbot, recording_num):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Get widget for loading recording
    w_recording = window.widgets["recording"]

    # Check that no EMG files present initially
    assert not w_recording.emg_model  # EMG model is None
    assert not w_recording.emg_label  # No label

    # Load demo recording
    load_demo_recording(window, recording_num)

    # Check that EMG files are added
    assert w_recording.emg_model  # EMG model is not None
    assert isinstance(w_recording.emg_model, EMGDataRawModel)  # Check type
    assert w_recording.emg_label  # Check that label exists


@pytest.mark.parametrize("recording_num", [0])
def test_that_loading_demo_recording_sends_emg_data_to_load_widget(qtbot, recording_num):
    # Set up window
    window = LoadWidget()  # Load step widget
    window.show()
    qtbot.addWidget(window)

    # Get widget for loading recording
    w_recording = window.widgets["recording"]

    # Check that no EMG data present initially in load widget
    assert not window.emg_model  # EMG model is None

    # Load demo recording
    load_demo_recording(window, recording_num)

    # Check that EMG files are added to load widget and matches data in recording widget
    assert window.emg_model  # EMG model is not None
    assert isinstance(window.emg_model, EMGDataRawModel)  # Check type
    assert window.emg_model == w_recording.emg_model  # Data matches in different widgets


@pytest.mark.parametrize("recording_num", [0])
def test_that_changing_recording_selection_deletes_loaded_recording_in_recording_widget(
    qtbot, recording_num
):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Get widgets for loading recording and selecting recording
    w_recording = window.widgets["recording"]
    w_select = w_recording.widgets["selectrecording"]

    # Load demo recording
    load_demo_recording(window, recording_num)

    # Change recording selection
    w_select.widgets["combobox"].setCurrentIndex(0)

    # Check that no EMG files are present
    assert not w_recording.emg_model  # EMG model is None
    assert not w_recording.emg_label  # Check that no label


@pytest.mark.parametrize("recording_num", [0])
def test_that_changing_recording_selection_deletes_loaded_recording_in_load_widget(
    qtbot, recording_num
):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Get widgets for loading recording and selecting recording
    w_recording = window.widgets["recording"]
    w_select = w_recording.widgets["selectrecording"]

    # Load demo recording
    load_demo_recording(window, recording_num)

    # Change recording selection
    w_select.widgets["combobox"].setCurrentIndex(0)

    # Check that no EMG data is present in load widget
    assert not window.emg_model  # EMG model is None


@pytest.mark.parametrize("recording_num", [0])
def test_that_changing_recording_path_to_empty_disables_load_button(qtbot, recording_num):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Get widgets for loading recording and selecting recording
    w_recording = window.widgets["recording"]
    w_select = w_recording.widgets["selectrecording"]

    # Change combobox to demo recording
    idx = w_select.demo_recording_num.index(recording_num)
    w_select.widgets["combobox"].setCurrentIndex(idx)

    # Check that load button is enabled
    assert w_recording.widgets["load"].isEnabled()

    # Change recording path to empty
    w_select.recording_path_changed.emit("")

    # Check that load button is disabled
    assert not w_recording.widgets["load"].isEnabled()


@pytest.mark.parametrize("recording_label", ["testlabel", "test label", "Test_Label", ""])
def test_that_changing_recording_label_updates_attribute_and_label_text_in_recording_widget(
    qtbot, recording_label
):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Get widgets for loading recording, selecting recording, and displaying recording label
    w_recording = window.widgets["recording"]
    w_select = w_recording.widgets["selectrecording"]
    w_label = w_recording.widgets["label"]

    # Change recording label
    w_select.recording_label_changed.emit(recording_label)

    # Check that label is updated (attribute and label text)
    assert w_recording.emg_label == recording_label
    assert w_label.widgets["recording"].text() == recording_label


# --- Tests for loading EMG settings ---


@pytest.mark.parametrize("recording_num", [0])
def test_that_settings_model_is_initially_none_in_settings_and_load_widgets(qtbot, recording_num):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Load demo recording
    load_demo_recording(window, recording_num)

    # Get widget for loading settings
    w_settings = window.widgets["settings"]

    # Check that no settings are stored in widgets
    assert w_settings.settings_model is None
    assert window.settings_model is None


@pytest.mark.parametrize("recording_num", [0])
def test_that_selecting_default_settings_changes_settings_model_in_settings_and_load_widgets(
    qtbot, recording_num
):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Load demo recording
    load_demo_recording(window, recording_num)

    # Get widget for loading settings
    w_settings = window.widgets["settings"]

    # Change settings to default
    w_settings.widgets["load"].widgets["combobox"].setCurrentText("Default")

    # Check that settings are stored in widgets
    assert w_settings.settings_model
    assert window.settings_model
    assert isinstance(w_settings.settings_model, EMGSettingsModel)  # Check type
    assert isinstance(window.settings_model, EMGSettingsModel)  # Check type
    assert w_settings.settings_model == window.settings_model  # Check settings are the same


@pytest.mark.parametrize("recording_num", [0])
def test_that_removing_settings_selection_removes_settings_model_in_settings_and_load_widgets(
    qtbot, recording_num
):
    # Set up window
    window = LoadWidget()
    window.show()
    qtbot.addWidget(window)

    # Load demo recording
    load_demo_recording(window, recording_num)

    # Get widget for loading settings
    w_settings = window.widgets["settings"]

    # Change settings to default
    w_settings.widgets["load"].widgets["combobox"].setCurrentText("Default")

    # Change settings back to empty (first index)
    w_settings.widgets["load"].widgets["combobox"].setCurrentIndex(0)

    # Check that no settings are stored in widgets
    assert w_settings.settings_model is None
    assert window.settings_model is None
