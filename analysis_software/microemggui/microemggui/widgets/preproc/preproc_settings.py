"""
Widgets for specifying preprocessing settings
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy

from PySide6.QtCore import Signal

from PySide6.QtGui import QDoubleValidator

from microemggui.widgets.base import (
    CheckBoxMain,
    InputLabel,
    InputWarningLabel,
    InputComboBox,
    InputSpinBox,
    InputLineEdit,
    InputInlineText,
    ExpandingVSpacer,
    SubsectionTitle,
)

from microemggui.models.settings import EMGPreprocSettingsModel

# --- Widgets for filter specification ---


class FilterTypeWidget(QWidget):
    # Widget for specifying filter type from labelled combobox
    def __init__(
        self,
        settings_model: EMGPreprocSettingsModel,
        filter_types: list[str],
        parent=None,
    ):
        super().__init__(parent)

        # Label for filter type
        self.type_label = InputLabel("Type", self)

        # Input for filter type
        self.type_combobox = InputComboBox(self)

        self.type_combobox.addItems(filter_types)

        # Add to layout
        layout = QVBoxLayout()
        layout.addWidget(self.type_label)
        layout.addWidget(self.type_combobox)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Set initial text using provided settings
        self.match_input_to_settings(settings_model)

        # Connect to filter settigns interface
        self.connect_to_settings(settings_model)

    def match_input_to_settings(self, settings_model):
        # Set combobox text to corresponding text in preprocessing settings

        self.type_combobox.setCurrentText(
            settings_model.settings.butterworth_filter_settings["filter_type"]
        )

    def connect_to_settings(self, settings_model):
        # Connect combobox value to corresponding values in preprocessing settings.
        # Changes filter type and also sets cutoff2 frequency to none if filter type
        # only requires one frequency

        self.type_combobox.currentTextChanged.connect(
            settings_model.filter_type_text_changed
        )


class FilterOrderWidget(QWidget):
    # Widget for specifying the filter order from a spinbox

    def __init__(self, settings_model: EMGPreprocSettingsModel, parent=None):
        super().__init__(parent)

        # Label
        self.order_label = InputLabel("Order", self)

        # Spinbox with range from 2 to 8, in steps of 2
        self.order_spinbox = InputSpinBox(self)
        self.order_spinbox.setRange(2, 8)
        self.order_spinbox.setSingleStep(2)

        # Set to ready only so cannot edit to odd number
        self.order_spinbox.lineEdit().setReadOnly(True)

        # Add to layout
        layout = QVBoxLayout()
        layout.addWidget(self.order_label)
        layout.addWidget(self.order_spinbox)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Set initial value using provided settings
        self.match_input_to_settings(settings_model)

        # Connect to filter settings interface
        self.connect_to_settings(settings_model)

    def match_input_to_settings(self, settings_model):
        # Set spinbox value to corresponding value in preprocessing settings

        self.order_spinbox.setValue(
            settings_model.settings.butterworth_filter_settings["order"]
        )

    def connect_to_settings(self, settings_model):
        # Connect spinbox value to corresponding value in preprocessing settings

        self.order_spinbox.valueChanged.connect(settings_model.filter_order_changed)


class FilterFreqWidget(QWidget):
    # Widget for specifying the filter frequencies from input boxes
    def __init__(self, settings_model: EMGPreprocSettingsModel, parent=None):
        super().__init__(parent)

        # TODO: block preprocessing from being applied if freq are not valid
        # TODO: set validator based on data sampling frequency
        # TODO: check upper allowed range for filter frequencies
        # TODO: ensure upper cutoff is greater than lower cutoff

        # Settings
        self.settings_model = settings_model

        # Label
        self.freq_label = InputLabel("Cutoff frequencies", self)

        # Widgets for specifying frequencies

        # Keep frequency input line edits separate so easy to loop through
        # Keys match the keys for specifying the filter cutoff frequency in settings
        self.freq_lineedit = {
            "cutoff1": InputLineEdit(self),
            "cutoff2": InputLineEdit(self),
        }
        self.freq_inlinelabel = {
            "to": InputInlineText("to", self),
            "hz": InputInlineText("Hz", self),
        }

        # Horizontal layout for frequency input
        layout_input = QHBoxLayout()
        layout_input.addWidget(self.freq_lineedit["cutoff1"])
        layout_input.addWidget(self.freq_inlinelabel["to"])
        layout_input.addWidget(self.freq_lineedit["cutoff2"])
        layout_input.addWidget(self.freq_inlinelabel["hz"])
        layout_input.setContentsMargins(0, 0, 0, 0)

        self.freq_input = QWidget(self)
        self.freq_input.setLayout(layout_input)

        # Valid range for frequencies
        self.freq_val_low = 0
        self.freq_val_high = 10000  # Nyquist frequency for 20k Hz sampling frequency
        freq_val = QDoubleValidator(self.freq_val_low, self.freq_val_high, 2)
        for _, w in self.freq_lineedit.items():
            w.setValidator(freq_val)

        # Warning label for each frequency input if not valid
        self.warning_labels = {}
        w_count = ["First", "Second"]
        for k, c in zip(self.freq_lineedit.keys(), w_count):
            self.warning_labels[k] = InputWarningLabel(
                (
                    f"{c} frequency must be between {self.freq_val_low} and "
                    f"{self.freq_val_high} Hz"
                ),
                self,
            )
            self.warning_labels[k].hide()  # Initially hidden since settings validated

        # Add label and input to overall layout
        layout = QVBoxLayout()
        layout.addWidget(self.freq_label)
        layout.addWidget(self.freq_input)
        for _, w in self.warning_labels.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Set initial values and widget visibility using provided settings
        self.match_input_to_settings()

        # Connections
        self.connect_to_settings()  # To filter settings interface
        self.connect_input_to_warning()  # To warning labels

    def set_n_freq(self, filter_type):
        # Set frequency input to match the number of frequencies needed (determined
        # by filter type)
        # Note that setting cutoff2 frequency to None is handled by FilterTypeWidget
        # signal.

        filter_n_freq = self.settings_model.settings._get_n_freq_per_filter_type()
        n_freq = filter_n_freq[filter_type]

        if n_freq == 1:
            # Change cutoff2 input to empty string
            self.freq_lineedit["cutoff2"].setText("")

            # Hide widgets
            self.freq_lineedit["cutoff2"].hide()
            self.freq_inlinelabel["to"].hide()
            self.warning_labels["cutoff2"].hide()

            # Change labels to singular
            self.freq_label.setText("Cutoff frequency")
            self.warning_labels["cutoff1"].setText(
                (
                    f"Frequency must be between {self.freq_val_low} and "
                    f"{self.freq_val_high} Hz"
                )
            )

        elif n_freq == 2:
            # TODO: store that cutoff2 input is not valid since still empty

            # Show widgets
            self.freq_lineedit["cutoff2"].show()
            self.freq_inlinelabel["to"].show()

            # Change labels to plural
            self.freq_label.setText("Cutoff frequencies")
            self.warning_labels["cutoff1"].setText(
                (
                    f"First frequency must be between {self.freq_val_low} and "
                    f"{self.freq_val_high} Hz"
                )
            )

    def match_input_to_settings(self):
        # Set line edit box text to the corresponding values in the preprocessing
        # settings

        # Match lineedit inputs to frequencies
        # If cutoff2 is None, will be replaced by empty string by self.set_n_freq
        for k, w in self.freq_lineedit.items():
            w.setText(str(self.settings_model.settings.butterworth_filter_settings[k]))

        # Match widgets to filter type
        self.set_n_freq(
            self.settings_model.settings.butterworth_filter_settings["filter_type"]
        )

    def connect_to_settings(self):
        # Connect line edit values to corresponding values in preprocessing settings

        for k, w in self.freq_lineedit.items():
            w.editingFinished.connect(
                lambda w=w, cutoff_type=k: self.settings_model.filter_cutoff_changed(
                    float(w.displayText()), cutoff_type
                )
            )

    def change_warning_visibility(self, has_acceptable_input: bool, cutoff_type: str):
        if has_acceptable_input:
            self.warning_labels[cutoff_type].hide()
        else:
            self.warning_labels[cutoff_type].show()

    def connect_input_to_warning(self):
        # Connect line edit values to visibility of warning messages

        for k, w in self.freq_lineedit.items():
            w.textChanged.connect(
                lambda text, w=w, cutoff_type=k: self.change_warning_visibility(
                    w.hasAcceptableInput(), cutoff_type
                )
            )


class FilterSpecWidget(QWidget):
    # Widget for all filter specifications
    def __init__(
        self,
        settings_model: EMGPreprocSettingsModel,
        filter_types: list[str],
        parent=None,
    ):
        super().__init__(parent)

        # Widgets for filter specifications
        self.widgets = {
            "filter_type": FilterTypeWidget(
                settings_model=settings_model, filter_types=filter_types, parent=self
            ),  # type
            "filter_freq": FilterFreqWidget(settings_model, self),  # frequencies
            "filter_order": FilterOrderWidget(settings_model, parent=self),  # order
        }

        # Add to filter specifications to vertical layout
        layout = QVBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(35, 0, 0, 0)  # add padding to left
        self.setLayout(layout)
        size_policy = self.sizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Maximum)
        size_policy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(size_policy)


# --- Widget for all preprocessing settings ---


class PreprocSettingsWidget(QWidget):
    # Widget for all preprocessing settings

    # Custom signal to emit when data is updated - using to check data in main window
    # TODO: potentially modify or remove
    settings_changed = Signal()

    def __init__(self, settings_model: EMGPreprocSettingsModel, parent=None):
        super().__init__(parent)

        # Settings interface
        self.settings_model = settings_model

        # Create widget

        # Checkbox for selecting mains noise removal
        mains_checkbox = CheckBoxMain("Remove mains noise (50 Hz)", self)

        # Checkbox for selecting filter
        filter_checkbox = CheckBoxMain("Filter", self)

        # Filter settings
        filter_spec = FilterSpecWidget(
            settings_model=self.settings_model,
            filter_types=settings_model.settings._get_filter_types_allowed(),
            parent=self,
        )

        # All widgets
        self.widgets = {
            "title": SubsectionTitle("Settings", self),
            "mains_checkbox": mains_checkbox,
            "filter_checkbox": filter_checkbox,
            "filter_spec": filter_spec,
        }

        # Create layout and add widgets
        layout = QVBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)

        # Spacer at end so extra space is added below other widgets if window resized
        end_space = ExpandingVSpacer()
        layout.addItem(end_space)

        self.setLayout(layout)

        # Connect checkboxes to data
        self.match_input_to_settings()  # match initial settings
        mains_checkbox.toggled.connect(self.settings_model.mains_checkbox_toggled)
        filter_checkbox.toggled.connect(self.settings_model.filter_checkbox_toggled)

        # Connect visability of filter specifications to filter checkbox
        filter_checkbox.toggled.connect(self.change_filter_spec_visibility)
        self.change_filter_spec_visibility(filter_checkbox.isChecked())

        # Connect filter type to filter frequency widget
        filter_spec.widgets["filter_type"].type_combobox.currentTextChanged.connect(
            filter_spec.widgets["filter_freq"].set_n_freq
        )

        # Temporary checks (whether settings data is updated in main window)
        # TODO: remove or incorporate in logger
        mains_checkbox.toggled.connect(self.settings_changed_func)
        filter_checkbox.toggled.connect(self.settings_changed_func)
        filter_spec.widgets["filter_type"].type_combobox.currentTextChanged.connect(
            self.settings_changed_func
        )
        filter_spec.widgets["filter_order"].order_spinbox.valueChanged.connect(
            self.settings_changed_func
        )
        freq_widgets = filter_spec.widgets["filter_freq"].freq_lineedit
        for _, w in freq_widgets.items():
            w.editingFinished.connect(self.settings_changed_func)

    def match_input_to_settings(self):
        # Set checkboxes to match provided preprocessing settings
        settings = self.settings_model.settings

        # Mains noise removal checkbox
        self.widgets["mains_checkbox"].setChecked(settings.remove_mains)

        # Filter checkbox
        self.widgets["filter_checkbox"].setChecked(settings.butterworth_filter)

    def change_filter_spec_visibility(self, checked):
        # Show or hide filter specification widgets based on filter checkbox state
        # Note that filter specification settings are retained so they are available
        # if the filtering option is added back to the preprocessing steps.

        if checked:
            self.show_filter_spec()
        else:
            self.hide_filter_spec()

    def hide_filter_spec(self):
        # Hides filter specification widgets
        # Values do not change, but will not be used if filter checkbox is not checked
        for _, w in self.widgets["filter_spec"].widgets.items():
            w.hide()

    def show_filter_spec(self):
        # Shows filter specification widgets
        for _, w in self.widgets["filter_spec"].widgets.items():
            w.show()

    def settings_changed_func(self):
        # Currently used to check data in main window
        # TODO: potentially modify or remove
        self.settings_changed.emit()
