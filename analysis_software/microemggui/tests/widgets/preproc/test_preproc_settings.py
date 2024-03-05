"""
Tests for preprocessing settings widgets.
TODO:
    - Tests for warning labels
    - Tests for checkbox toggles
    - Tests for widget visibility
"""
import pytest

from pymicroemg.emg_preproc_settings import EMGPreprocSettings

# from microemggui.widgets.preproc import preprocessing_settings as preproc_set
import microemggui.widgets.preproc.preproc_settings as preproc_set
from microemggui.models.settings import EMGPreprocSettingsModel


# --- Fixtures for preprocessing settings ---

# TODO: addfixture w/o initial filter (once behaviour is implemented)


# Settings model fixture, parametrised to have different initial settings
@pytest.fixture(
    params=[
        ("bandpass", False),
        ("bandpass", True),
        ("lowpass", False),
        ("lowpass", True),
        ("highpass", False),
        ("highpass", True),
    ],
    ids=[
        "bandpass filter",
        "bandpass filter and remove mains",
        "lowpass filter",
        "lowpass filter and remove mains",
        "highpass filter",
        "highpass filter and remove mains",
    ],
)
def settings_model_with_filter(request):
    settings = EMGPreprocSettings()
    if request.param[1]:
        settings.add_remove_mains()
    if (
        request.param[0] == "bandpass"
    ):  # Bandpass filter requires two cutoff frequencies
        cutoff_freq = [100, 400]
    else:
        cutoff_freq = 100
    settings.add_butterworth_filter(
        filter_type=request.param[0], cutoff_freq=cutoff_freq, order=4
    )
    settings_model = EMGPreprocSettingsModel(settings)

    return settings_model


# --- Functions for repeated assertions ----


def assert_settings_match(window, settings, is_initial=False):
    # Function for checking that stored settings match GUI input fields.
    # Use for checking consistency in different scenarios.

    # Checkboxes
    assert settings.remove_mains == window.widgets["mains_checkbox"].isChecked()
    assert settings.butterworth_filter == window.widgets["filter_checkbox"].isChecked()

    # Filter specifications
    spec_w = window.widgets["filter_spec"].widgets
    assert (
        settings.butterworth_filter_settings["filter_type"]
        == spec_w["filter_type"].type_combobox.currentText()
    )
    assert (
        settings.butterworth_filter_settings["order"]
        == spec_w["filter_order"].order_spinbox.value()
    )
    assert (
        str(settings.butterworth_filter_settings["cutoff1"])
        == spec_w["filter_freq"].freq_lineedit["cutoff1"].text()
    )
    # Can only guarantee cutoff2 frequency for bandpass filter if initial settings
    if is_initial:
        if settings.butterworth_filter_settings["filter_type"] == "bandpass":
            assert (
                str(settings.butterworth_filter_settings["cutoff2"])
                == spec_w["filter_freq"].freq_lineedit["cutoff2"].text()
            )
        # If not a bandpass filter, cutoff2 line edit is empty string and setting is None
        else:
            assert spec_w["filter_freq"].freq_lineedit["cutoff2"].text() == ""
            assert settings.butterworth_filter_settings["cutoff2"] is None
    else:
        if settings.butterworth_filter_settings["cutoff2"] is not None:
            assert (
                str(settings.butterworth_filter_settings["cutoff2"])
                == spec_w["filter_freq"].freq_lineedit["cutoff2"].text()
            )
        else:
            assert spec_w["filter_freq"].freq_lineedit["cutoff2"].text() == ""
            assert settings.butterworth_filter_settings["cutoff2"] is None


# --- Tests ---


def test_preproc_widget_matches_initial_settings(qtbot, settings_model_with_filter):
    # Set up window
    window = preproc_set.PreprocSettingsWidget(settings_model_with_filter)
    window.show()
    qtbot.addWidget(window)

    # Check that all settings match
    assert_settings_match(window, window.settings_model.settings, is_initial=True)


def test_preproc_widget_modifying_filter_order(qtbot, settings_model_with_filter):
    # Set up window
    window = preproc_set.PreprocSettingsWidget(settings_model_with_filter)
    window.show()
    qtbot.addWidget(window)

    # Order spinbox widget
    w = window.widgets["filter_spec"].widgets["filter_order"].order_spinbox

    # Change filter order
    order_original = w.value()
    w.setValue(order_original + 2)
    assert w.value() == order_original + 2

    # Check all settings match
    assert_settings_match(window, window.settings_model.settings)


@pytest.mark.parametrize("filter_type", ["bandpass", "lowpass", "highpass"])
def test_preproc_widget_modifying_filter_type(
    qtbot, settings_model_with_filter, filter_type
):
    # Note: changing filter type also modifies cutoff frequencies

    # Set up window
    window = preproc_set.PreprocSettingsWidget(settings_model_with_filter)
    window.show()
    qtbot.addWidget(window)

    # Filter combobox widget
    w = window.widgets["filter_spec"].widgets["filter_type"].type_combobox

    # Change filter type
    w.setCurrentText(filter_type)
    assert w.currentText() == filter_type

    # Check all settings match
    assert_settings_match(window, window.settings_model.settings)


@pytest.mark.parametrize("freq", [500, 500.01, 500.1])
def test_preproc_widget_modifying_filter_cutoff1(
    qtbot, settings_model_with_filter, freq
):
    # Set up window
    window = preproc_set.PreprocSettingsWidget(settings_model_with_filter)
    window.show()
    qtbot.addWidget(window)

    # Filter frequency line edit (first cutoff frequency)
    w = window.widgets["filter_spec"].widgets["filter_freq"].freq_lineedit["cutoff1"]

    # Change frequency
    freq_str = str(float(freq))
    w.setText(freq_str)
    # Change focus to another widget so text is stored
    window.widgets["filter_spec"].widgets["filter_order"].order_spinbox.setFocus()
    assert w.text() == freq_str

    # Check all settings match
    assert_settings_match(window, window.settings_model.settings)


@pytest.mark.parametrize("freq", ["None", "ten", -1, 999999999999])
def test_preproc_widget_modifying_filter_cutoff1_fails_when_input_invalid(
    qtbot, settings_model_with_filter, freq
):
    # Set up window
    window = preproc_set.PreprocSettingsWidget(settings_model_with_filter)
    window.show()
    qtbot.addWidget(window)

    # Filter frequency line edit (first cutoff frequency)
    w = window.widgets["filter_spec"].widgets["filter_freq"].freq_lineedit["cutoff1"]

    # Original frequency
    freq_str_original = w.text()

    # Change frequency
    if isinstance(freq, float) or isinstance(freq, int):
        freq_str = str(freq)
    else:
        freq_str = freq
    w.setText(freq_str)
    # Change focus to another widget so text is stored
    window.widgets["filter_spec"].widgets["filter_order"].order_spinbox.setFocus()
    assert w.text() == freq_str

    # Check that cutoff1 setting has not changed
    settings = settings_model_with_filter.settings
    assert str(settings.butterworth_filter_settings["cutoff1"]) != w.text()
    assert str(settings.butterworth_filter_settings["cutoff1"]) == freq_str_original
