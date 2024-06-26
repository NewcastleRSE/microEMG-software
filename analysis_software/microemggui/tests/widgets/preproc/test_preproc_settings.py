"""
Tests for preprocessing settings widgets.
TODO: Tests for warning labels
TODO: Tests for widget visibility
"""

import pytest
from pytest_check import check, equal, is_none

from pymicroemg.emg_preproc_settings import EMGPreprocSettings
import microemggui.widgets.preproc.preproc_settings as preproc_set
from microemggui.models.settings import EMGPreprocSettingsModel


# --- Fixtures for preprocessing settings ---


# Settings model fixture, parametrised to have different initial settings
# Parameters are (whether to apply mains removal, whether to apply filter, filter type)
@pytest.fixture(
    params=[
        (False, True, "bandpass"),
        (True, True, "bandpass"),
        (False, True, "lowpass"),
        (True, True, "lowpass"),
        (False, True, "highpass"),
        (True, True, "highpass"),
        (False, False, "bandpass"),
        (True, False, "bandpass"),
        (False, False, "lowpass"),
        (True, False, "lowpass"),
        (False, False, "highpass"),
        (True, False, "highpass"),
    ],
    ids=[
        "bandpass filter",
        "bandpass filter and remove mains",
        "lowpass filter",
        "lowpass filter and remove mains",
        "highpass filter",
        "highpass filter and remove mains",
        "no preprocessing, bandpass filter settings stored",
        "remove mains only, bandpass filter settings stored",
        "no preprocessing, lowpass filter settings stored",
        "remove mains only, lowpass filter settings stored",
        "no preprocessing, highpass filter settings stored",
        "remove mains only, highpass filter settings stored",
    ],
)
def settings_model(request):
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


# Settings model fixture, only parameterised to have bandpass filter
# Parameters are (whether to apply mains removal, filter type)
@pytest.fixture(
    params=[(False, "bandpass"), (True, "bandpass")],
    ids=["bandpass filter", "bandpass filter and remove mains"],
)
def settings_model_with_bandpass_filter(request):
    settings = EMGPreprocSettings()
    if request.param[0]:
        settings.add_remove_mains()
    cutoff_freq = [100.0, 400]  # Test initial value as both float and int
    settings.add_butterworth_filter(filter_type=request.param[1], cutoff_freq=cutoff_freq, order=4)
    settings_model = EMGPreprocSettingsModel(settings)

    return settings_model


# --- Functions for repeated assertions ----


@check.check_func
def assert_settings_match(window, settings, is_initial=False):
    # Function for checking that stored settings match GUI input fields.
    # Use for checking consistency in different scenarios.

    # Checkboxes
    equal(settings.remove_mains, window.widgets["mains_checkbox"].isChecked())
    equal(settings.butterworth_filter, window.widgets["filter_checkbox"].isChecked())

    # Filter specifications
    spec_w = window.widgets["filter_spec"].widgets
    equal(
        settings.butterworth_filter_settings["filter_type"],
        spec_w["filter_type"].type_combobox.currentText(),
    )
    equal(
        settings.butterworth_filter_settings["order"], spec_w["filter_order"].order_spinbox.value()
    )
    equal(
        settings.butterworth_filter_settings["cutoff1"],
        float(spec_w["filter_freq"].freq_lineedit["cutoff1"].text()),
    )
    # Can only guarantee cutoff2 frequency for bandpass filter if initial settings
    if is_initial:
        if settings.butterworth_filter_settings["filter_type"] == "bandpass":
            equal(
                settings.butterworth_filter_settings["cutoff2"],
                float(spec_w["filter_freq"].freq_lineedit["cutoff2"].text()),
            )
        # If not a bandpass filter, cutoff2 line edit is empty string, setting is None
        else:
            equal(spec_w["filter_freq"].freq_lineedit["cutoff2"].text(), "")
            is_none(settings.butterworth_filter_settings["cutoff2"])
    else:
        if settings.butterworth_filter_settings["cutoff2"] is not None:
            equal(
                settings.butterworth_filter_settings["cutoff2"],
                float(spec_w["filter_freq"].freq_lineedit["cutoff2"].text()),
            )
        else:
            equal(spec_w["filter_freq"].freq_lineedit["cutoff2"].text(), "")
            is_none(settings.butterworth_filter_settings["cutoff2"])


# --- Tests ---


def test_preproc_widget_matches_initial_settings(qtbot, settings_model):
    # Set up window
    window = preproc_set.PreprocSettingsWidget(settings_model)
    window.show()
    qtbot.addWidget(window)

    # Check that all settings match
    assert_settings_match(window, window.settings_model.settings, is_initial=True)


def test_preproc_widget_modifying_filter_order(qtbot, settings_model):
    # Set up window
    window = preproc_set.PreprocSettingsWidget(settings_model)
    window.show()
    qtbot.addWidget(window)

    # Order spinbox widget
    w = window.widgets["filter_spec"].widgets["filter_order"].order_spinbox

    # Change filter order
    order_original = w.value()
    w.setValue(order_original + 2)
    with check:
        assert w.value() == order_original + 2

    # Check all settings match
    assert_settings_match(window, window.settings_model.settings)


@pytest.mark.parametrize("filter_type", ["bandpass", "lowpass", "highpass"])
def test_preproc_widget_modifying_filter_type(qtbot, settings_model, filter_type):
    # Note: changing filter type also modifies cutoff frequencies

    # Set up window
    window = preproc_set.PreprocSettingsWidget(settings_model)
    window.show()
    qtbot.addWidget(window)

    # Filter combobox widget
    w = window.widgets["filter_spec"].widgets["filter_type"].type_combobox

    # Change filter type
    w.setCurrentText(filter_type)
    with check:
        assert w.currentText() == filter_type

    # Check all settings match
    assert_settings_match(window, window.settings_model.settings)


@pytest.mark.parametrize("freq", [150, 150.01, 150.1])  # keep below fixture's cutoff2
def test_preproc_widget_modifying_filter_cutoff1(qtbot, settings_model, freq):
    # Set up window
    window = preproc_set.PreprocSettingsWidget(settings_model)
    window.show()
    qtbot.addWidget(window)

    # Filter frequency line edit (first cutoff frequency)
    w = window.widgets["filter_spec"].widgets["filter_freq"].freq_lineedit["cutoff1"]

    # Change frequency
    freq_str = str(freq)
    w.setText(freq_str)
    with check:
        assert w.text() == freq_str

    # Check all settings match
    assert_settings_match(window, window.settings_model.settings)


@pytest.mark.parametrize("freq", ["None", "ten", -1, 999999999999])
def test_preproc_widget_modifying_filter_cutoff1_fails_when_input_invalid(
    qtbot, settings_model, freq
):
    # Set up window
    window = preproc_set.PreprocSettingsWidget(settings_model)
    window.show()
    qtbot.addWidget(window)

    # Filter frequency line edit (first cutoff frequency)
    w = window.widgets["filter_spec"].widgets["filter_freq"].freq_lineedit["cutoff1"]

    # Original frequency
    freq_original = float(w.text())

    # Change frequency
    if isinstance(freq, float) or isinstance(freq, int):
        freq_str = str(freq)
    else:
        freq_str = freq
    w.setText(freq_str)
    with check:
        assert w.text() == freq_str

    # Check that cutoff1 setting has not changed
    settings = settings_model.settings
    with check:
        assert settings.butterworth_filter_settings["cutoff1"] == freq_original


@pytest.mark.parametrize("freq", [550, 550.01, 550.1])  # keep above fixture's cutoff1
def test_preproc_widget_modifying_filter_cutoff2(qtbot, settings_model_with_bandpass_filter, freq):
    # Set up window
    window = preproc_set.PreprocSettingsWidget(settings_model_with_bandpass_filter)
    window.show()
    qtbot.addWidget(window)

    # Filter frequency line edit (first cutoff frequency)
    w = window.widgets["filter_spec"].widgets["filter_freq"].freq_lineedit["cutoff2"]

    # Change frequency
    freq_str = str(freq)
    w.setText(freq_str)
    with check:
        assert w.text() == freq_str

    # Check all settings match
    assert_settings_match(window, window.settings_model.settings)


@pytest.mark.parametrize("freq", ["None", "ten", -1, 999999999999])
def test_preproc_widget_modifying_filter_cutoff2_fails_when_input_invalid(
    qtbot, settings_model_with_bandpass_filter, freq
):
    # Set up window
    window = preproc_set.PreprocSettingsWidget(settings_model_with_bandpass_filter)
    window.show()
    qtbot.addWidget(window)

    # Filter frequency line edit (first cutoff frequency)
    w = window.widgets["filter_spec"].widgets["filter_freq"].freq_lineedit["cutoff2"]

    # Original frequency
    freq_original = float(w.text())

    # Change frequency
    if isinstance(freq, float) or isinstance(freq, int):
        freq_str = str(freq)
    else:
        freq_str = freq
    w.setText(freq_str)
    with check:
        assert w.text() == freq_str

    # Check that cutoff1 setting has not changed
    settings = settings_model_with_bandpass_filter.settings
    with check:
        assert settings.butterworth_filter_settings["cutoff2"] == freq_original


# Parameterise with checkbox and corresponding attribute
@pytest.mark.parametrize(
    "setting",
    [("filter_checkbox", "butterworth_filter"), ("mains_checkbox", "remove_mains")],
)
def test_toggle_checkbox_changes_settings_bool_and_checkbox_state(qtbot, settings_model, setting):
    # Set up window
    window = preproc_set.PreprocSettingsWidget(settings_model)
    window.show()
    qtbot.addWidget(window)

    # Filter checkbox
    w = window.widgets[setting[0]]

    # Original checkbox state and filter bool
    original_checkbox_state = w.isChecked()
    original_filter_bool = getattr(window.settings_model.settings, setting[1])

    # Toggle checkbox
    w.toggle()

    # Check that state and bool have changed
    # use "x== (not y)" to confirm swap, not just inequality
    with check:
        assert original_checkbox_state == (not w.isChecked())
    with check:
        assert original_filter_bool == (not getattr(window.settings_model.settings, setting[1]))

    # Check all settings match
    assert_settings_match(window, window.settings_model.settings)


# Parameterise how much to change frequency above/below valid range
@pytest.mark.parametrize("delta", [0.1, 1, 1000])
def test_invalid_cutoff1_freq_changes_freq_values_valid_attribute_to_false(
    qtbot, settings_model, delta
):
    # Set up window
    window = preproc_set.PreprocSettingsWidget(settings_model)
    window.show()
    qtbot.addWidget(window)

    # Frequency widget - has freq_values_valid attribute
    w = window.widgets["filter_spec"].widgets["filter_freq"]

    # Get valid range for frequency from widget
    freq_val_low = w.freq_val_low
    freq_val_high = w.freq_val_high

    # Frequency input line edit
    w_lineedit = w.freq_lineedit["cutoff1"]
    freq_original_str = w_lineedit.text()

    # Confirm original values are valid
    with check:
        assert w.freq_values_valid is True

    # Change frequency to below range and check freq_values_valid is False
    w_lineedit.setText(str(freq_val_low - delta))
    with check:
        assert w.freq_values_valid is False

    # Change frequency back to original
    w_lineedit.setText(freq_original_str)
    with check:
        assert w.freq_values_valid is True

    # Change frequency to above range and check freq_values_valid is False
    w_lineedit.setText(str(freq_val_high + delta))
    with check:
        assert w.freq_values_valid is False


# Parameterise how much to change frequency above/below valid range
@pytest.mark.parametrize("delta", [0.1, 1, 1000])
def test_invalid_cutoff2_freq_changes_freq_values_valid_attribute_to_false(
    qtbot, settings_model_with_bandpass_filter, delta
):
    # Set up window
    window = preproc_set.PreprocSettingsWidget(settings_model_with_bandpass_filter)
    window.show()
    qtbot.addWidget(window)

    # Frequency widget - has freq_values_valid attribute
    w = window.widgets["filter_spec"].widgets["filter_freq"]

    # Get valid range for frequency from widget
    freq_val_low = w.freq_val_low
    freq_val_high = w.freq_val_high

    # Frequency input line edit
    w_lineedit = w.freq_lineedit["cutoff2"]
    freq_original_str = w_lineedit.text()

    # Confirm original values are valid
    with check:
        assert w.freq_values_valid is True

    # Change frequency to below range and check freq_values_valid is False
    w_lineedit.setText(str(freq_val_low - delta))
    with check:
        assert w.freq_values_valid is False

    # Change frequency back to original
    w_lineedit.setText(freq_original_str)
    with check:
        assert w.freq_values_valid is True

    # Change frequency to above range and check freq_values_valid is False
    w_lineedit.setText(str(freq_val_high + delta))
    with check:
        assert w.freq_values_valid is False


# Parameterise how much to change frequency above/below valid range
@pytest.mark.parametrize("freqs", [(10, 0.1), (100, 100), (1000, 10)])
def test_cutoff2_less_than_or_equal_tocutoff1_changes_freq_values_attribute_to_false(
    qtbot, settings_model_with_bandpass_filter, freqs
):
    # Set up window
    window = preproc_set.PreprocSettingsWidget(settings_model_with_bandpass_filter)
    window.show()
    qtbot.addWidget(window)

    # Frequency widget - has freq_values_valid attribute
    w = window.widgets["filter_spec"].widgets["filter_freq"]

    # Frequency input line edit for each frequency
    w_lineedit1 = w.freq_lineedit["cutoff1"]
    w_lineedit2 = w.freq_lineedit["cutoff2"]

    # Confirm original values are valid
    with check:
        assert w.freq_values_valid is True

    # Change frequencies so cutoff2 is less than or equal to cutoff1
    w_lineedit1.setText(str(freqs[0]))
    w_lineedit2.setText(str(freqs[1]))
    with check:
        assert w.freq_values_valid is False
