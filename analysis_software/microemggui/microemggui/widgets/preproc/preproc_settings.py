"""
Widgets for specifying preprocessing settings
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from PySide6.QtCore import Signal

from microemggui.widgets.base import (
    CheckBoxMain,
    InputLabel,
    InputComboBox,
    InputSpinBox,
    InputLineEdit,
    InputInlineLabel,
    ExpandingSpacer,
)

from microemggui.models.settings import EMGPreprocSettingsModel

# --- Widgets for filter specification ---


class FilterTypeWidget(QWidget):
    # Widget for specifying filter type from labelled combobox
    def __init__(self, filter_types, parent=None):
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


class FilterOrderWidget(QWidget):
    # Widget for specifying the filter order from a spinbox
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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


class FilterFreqWidget(QWidget):
    # Widget for specifying the filter frequencies from input boxes
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO: add input validator (QDoubleValidator?)

        # Label
        self.freq_label = InputLabel("Cutoff frequencies", self)

        # Widgets for specifying frequencies
        self.freq_input_widgets = [
            InputLineEdit(self),
            InputInlineLabel("to", self),
            InputLineEdit(self),
            InputInlineLabel("Hz", self),
        ]

        # Horizontal layout for frequency input
        layout_input = QHBoxLayout()
        for w in self.freq_input_widgets:
            layout_input.addWidget(w)
        layout_input.setContentsMargins(0, 0, 0, 0)
        self.freq_input = QWidget(self)
        self.freq_input.setLayout(layout_input)

        # Add label and input to overall layout
        layout = QVBoxLayout()
        layout.addWidget(self.freq_label)
        layout.addWidget(self.freq_input)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class FilterSpecWidget(QWidget):
    # Widget for all filter specifications
    def __init__(self, filter_types, parent=None):
        super().__init__(parent)

        # Widgets for filter specifications
        self.widgets = {
            "filter_type": FilterTypeWidget(filter_types, parent=self),  # type
            "filter_freq": FilterFreqWidget(self),  # frequencies
            "filter_order": FilterOrderWidget(self),  # order
        }

        # Add to filter specifications to vertical layout
        layout = QVBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(50, 0, 0, 0)  # add padding to left
        self.setLayout(layout)


# --- Widget for all settings ---


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
            settings_model.settings._get_filter_types_allowed(), parent=self
        )

        # All widgets
        self.widgets = {
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
        end_space = ExpandingSpacer()
        layout.addItem(end_space)

        self.setLayout(layout)

        # Connect to data

        # Set inputs to match provided preprocessing settings
        self.match_input_to_settings()

        # Connections to interface
        mains_checkbox.toggled.connect(self.settings_model.mains_checkbox_toggled)
        filter_checkbox.toggled.connect(self.settings_model.filter_checkbox_toggled)
        filter_spec.widgets["filter_type"].type_combobox.currentTextChanged.connect(
            self.settings_model.filter_type_text_changed
        )

        # TODO: ...
        # Connect remaining filter  (cutoff freq and order)
        # Move connections to corresponding widget classes where possible
        # Hide 2nd cutoff freq if filter type is not bandpass

        # Temporary checks (whether settings data is updated in main window)
        # TODO: remove or incorporate in logger
        mains_checkbox.toggled.connect(self.settings_changed_func)
        filter_checkbox.toggled.connect(self.settings_changed_func)
        filter_spec.widgets["filter_type"].type_combobox.currentTextChanged.connect(
            self.settings_changed_func
        )
        # Connect editable property of filter specifications to filter checkbox
        filter_checkbox.toggled.connect(self.change_filter_spec_visibility)

    def match_input_to_settings(self):
        # Set widgets to match provided preprocessing settings
        settings = self.settings_model.settings

        # Mains noise removal checkbox
        self.widgets["mains_checkbox"].setChecked(settings.remove_mains)

        # Filter checkbox
        self.widgets["filter_checkbox"].setChecked(settings.butterworth_filter)

        # Filter specifications checkbox
        filter_spec_w = self.widgets["filter_spec"].widgets
        filter_spec_w["filter_type"].type_combobox.setCurrentText(
            settings.butterworth_filter_settings["filter_type"]
        )

    def change_filter_spec_visibility(self, checked):
        # Show or hide filter specification widgets based on filter checkbox state

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
