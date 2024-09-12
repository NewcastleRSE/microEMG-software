#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for home page. Includes information about the GUI (e.g., license, attributions)
"""

from typing import Any

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

from microemggui.widgets.base import (
    SectionTitle,
    SubsectionTitle,
    MessageLabel,
    ExpandingVSpacer,
)

# --- Helper function for making hyperlink strings ---


def make_hyperlink(text: str, link: str) -> str:
    """
    Create string with HTML for a text hyperlink.

    Parameters
    ----------
    text : str
        Link text.
    link : str
        Link that is opened by the text.

    Returns
    -------
    str
        String of the HTML for the hyperlink.

    """

    hyperlink_str = f'<a href="{link}">{text}</a>'

    return hyperlink_str


# --- Widgets to add to home page ---


class HomePageSectionWidget(QWidget):
    """
    Generic class for section with a title and text. Will use to add different text
    sections to HomeWidget.
    """

    def __init__(self, title: str, text: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create widgets - title and corresponding text underneath
        self.widgets: dict[str, Any] = {
            "title": SubsectionTitle(title, parent=self),
            "text": MessageLabel(text, parent=self),
        }

        # Set to open hyperlinks
        self.widgets["text"].setOpenExternalLinks(True)

        # Add to layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


# --- Home page widget ---


class HomeWidget(QWidget):
    """
    Widget for home (welcome) page.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create dictionary for info to add to home page widget.
        # Keys will become section titles, and values will be used for the
        # corresponding text.
        # Can use some HTML for formatting (e.g., <b></b> for bold, <br> for line breaks,
        # <a href=\"http://example.com/\">Example Link</a> for links (see helper function
        # make_hyperlink)

        about_text = (
            "<b>MicroEMG:</b> Analyse multi-channel EMG recordings to identify motor units, "
            + "localise muscle fibres, and compute fibre pair jitter."
            + "<br><br>"
            + "<b>Code:</b> "
            + make_hyperlink(
                "https://github.com/NewcastleRSE/microEMG-software/",
                "https://github.com/NewcastleRSE/microEMG-software/",
            )
            + "<br><br>"
            + "<b>Version:</b> <b>TBA</b>"
            + "<br><br>"
            + "This research software was developed at Newcastle University's "
            + "Translational and Clinical Research Institute in collaboration with the "
            + make_hyperlink(
                "Research Software Engineering (RSE) team", "https://rse.ncldata.dev/"
            )
            + "."
            + "<br><br>"
            + "<b>Developers:</b><br>"
            + "Dr Stuart Maitland (stu.maitland@newcastle.ac.uk)<br>"
            + "Dr Roger Whittaker<br>"
            + "Dr Gabrielle Schroeder (RSE)<br>"
            + "Dr Richard Howey (RSE)<br>"
            + "Dr Frances Turner (RSE)<br>"
        )

        legal_text = (
            "The MicroEMG software is licensed under <b>TBA</b>"
            + "<br><br>"
            + "The GUI uses "
            + make_hyperlink("Bootstrap Icons", "https://icons.getbootstrap.com/")
            + " (license: The MIT License) and "
            + make_hyperlink("CartoColors", "https://carto.com/carto-colors/")
            + " (license: CC-BY 4.0) for data visualisations."
        )

        home_info = {"About": about_text, "Legal": legal_text}

        # Names for corresponding widgets
        home_info_names = [k.lower().replace(" ", "_") for k in home_info.keys()]
        print(home_info_names)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "title": SectionTitle("Welcome to the MicroEMG GUI", parent=self)
        }

        # Add section widget for each item in home_info
        for (k, v), name in zip(home_info.items(), home_info_names):
            self.widgets[name] = HomePageSectionWidget(title=k, text=v, parent=self)

        # Add to layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.addItem(ExpandingVSpacer())  # spacer
        layout.setContentsMargins(20, 5, 20, 20)
        self.setLayout(layout)
