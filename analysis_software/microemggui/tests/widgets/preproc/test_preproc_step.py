"""
Tests for preprocessing step widget.

TODO: check tests fail
TODO: created shared file for fixtures
TODO: additional tests (e.g., for tabbed emg viewer)
TODO: cache fixtures for faster testing
"""

import pytest

from pymicroemg.emg_preproc_settings import EMGPreprocSettings
from pymicroemg.emg_files import EMGFiles
import pymicroemg.helper_config as cfg

from microemggui.models.settings import EMGPreprocSettingsModel
from microemggui.models.emg import EMGDataRawModel
from microemggui.widgets.preproc.preproc_step import PreprocWidget


# --- Fixtures for EMG data and preprocessing settings ---


# Concise settings model fixture for faster testing - does not cover all combinations
@pytest.fixture(
    params=[(True, True, "bandpass"), (False, True, "lowpass")],
    ids=[
        "bandpass filter and remove mains",
        "lowpass filter",
    ],
)
def settings_model_limited(request):
    settings = EMGPreprocSettings()

    # Add mains noise removal
    if request.param[0]:
        settings.add_remove_mains()

    # Add filter with specified filter type
    if request.param[2] == "bandpass":  # Bandpass requires two cutoff frequencies
        cutoff_freq = [100.0, 400]  # Test initial values as float and int
    else:
        cutoff_freq = 100.0
    settings.add_butterworth_filter(
        filter_type=request.param[2],
        cutoff_freq=cutoff_freq,
        order=4,
        apply_filter=request.param[1],
    )

    settings_model = EMGPreprocSettingsModel(settings)

    return settings_model


# Fixture for raw EMG data model
# Currently only uses one EMG recording, but set up to add additional recordings
@pytest.fixture(params=[0], ids=["demo EMG recording #0"])
def emg_data_raw_model(request):
    # Load EMG data
    recording_num = request.param
    emg_dir, _ = cfg.get_recording_path_and_id(recording_num)
    emg_files = EMGFiles(emg_dir)
    emg_data = emg_files.load_emg_data()
    emg_data_raw_model = EMGDataRawModel(emg_data)

    return emg_data_raw_model


# Colors for EMG viewer
@pytest.fixture
def emg_clrs():
    emg_clrs = ["#5F4690", "#1D6996"]

    return emg_clrs


# --- Tests ---


def test_apply_button_enabled_with_valid_initial_preprocessing_settings(
    qtbot, emg_data_raw_model, settings_model_limited, emg_clrs
):
    # Set up window
    window = PreprocWidget(
        emg_data_raw_model, settings_model_limited, emg_clrs=emg_clrs
    )
    window.show()
    qtbot.addWidget(window)

    # Get apply button
    w = window.widgets["buttons"].widgets["apply"]

    # Confirm that button is enabled with provided settings
    assert w.isEnabled()


def test_apply_button_disabled_if_freq_values_valid_manually_set_to_false(
    qtbot, emg_data_raw_model, settings_model_limited, emg_clrs
):
    # Set up window
    window = PreprocWidget(
        emg_data_raw_model, settings_model_limited, emg_clrs=emg_clrs
    )
    window.show()
    qtbot.addWidget(window)

    # Get apply button
    w_apply = window.widgets["buttons"].widgets["apply"]

    # Confirm that button is enabled with provided settings
    assert w_apply.isEnabled()

    # Frequency widget - has freq_values_valid attribute
    w_freq = window.widgets["settings"].widgets["filter_spec"].widgets["filter_freq"]

    # Manually set freq_values_valid to false and call function that triggers signal to
    # apply button
    w_freq.freq_values_valid = False
    window.widgets["settings"].settings_changed()

    # Confirm that apply button is disabled
    assert w_apply.isEnabled() is False


def test_apply_button_changed_to_reapply_and_disabled_after_preprocessing(
    qtbot, emg_data_raw_model, settings_model_limited, emg_clrs
):
    # Set up window
    window = PreprocWidget(
        emg_data_raw_model, settings_model_limited, emg_clrs=emg_clrs
    )
    window.show()
    qtbot.addWidget(window)

    # Get apply button
    w_apply = window.widgets["buttons"].widgets["apply"]

    # Click apply button to trigger preprocessing
    w_apply.clicked.emit()

    # Check text of apply button changed and button disabled
    assert w_apply.text() == "Re-apply"
    assert w_apply.isEnabled() is False


def test_next_button_becomes_visible_after_preprocessing(
    qtbot, emg_data_raw_model, settings_model_limited, emg_clrs
):
    # Set up window
    window = PreprocWidget(
        emg_data_raw_model, settings_model_limited, emg_clrs=emg_clrs
    )
    window.show()
    qtbot.addWidget(window)

    # Get apply button and next button
    w_apply = window.widgets["buttons"].widgets["apply"]
    w_next = window.widgets["buttons"].widgets["next"]

    # Confirm next button is hidden
    assert w_next.isVisible() is False

    # Click apply button to trigger preprocessing
    w_apply.clicked.emit()

    # Check next button becomes visible and enabled
    assert w_next.isVisible()
    assert w_next.isEnabled()


def test_emg_data_preprocessed_and_added_to_viewer_when_apply_button_clicked(
    qtbot, emg_data_raw_model, settings_model_limited, emg_clrs
):
    # Set up window
    window = PreprocWidget(
        emg_data_raw_model, settings_model_limited, emg_clrs=emg_clrs
    )
    window.show()
    qtbot.addWidget(window)

    # Get apply button
    w_apply = window.widgets["buttons"].widgets["apply"]

    # Click apply button to trigger preprocessing
    w_apply.clicked.emit()

    # Check that preprocessed data is added with settings that match settings_model
    assert window.emg_model.get("preproc")  # Confirm preprocessed data added
    assert (
        window.emg_model["preproc"].emg_data.preproc_settings
        == settings_model_limited.settings
    )

    # Confirm same preprocessed data added to tabbed EMG viewer
    viewer_emg_model_preproc = window.widgets["tabbedviewer"].emg_model["preproc"]
    assert viewer_emg_model_preproc == window.emg_model["preproc"]

    # Confirm that preprocessed data is data shown in viewer
    assert (
        viewer_emg_model_preproc
        == window.widgets["tabbedviewer"].widgets["viewer"].widgets["plot"].emg_model
    )
