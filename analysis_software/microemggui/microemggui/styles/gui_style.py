#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions for defining style settings (e.g., colours) and getting style sheet.
"""

import os
from PySide6.QtCore import QFile
import microemggui


def get_gui_style_sheet() -> str:
    """
    Load GUI style sheet as string.

    Returns
    -------
    str
        GUI style sheet.

    """

    # Get path to style sheet
    style_dir = microemggui.__file__
    style_dir = style_dir[:-11]  # remove init
    style_path = os.path.join(style_dir, "styles", "style.qss")

    # Load style sheet
    gui_style_file = QFile(style_path)
    gui_style_file.open(QFile.OpenModeFlag.ReadOnly)
    gui_style_sheet = gui_style_file.readAll().toStdString()

    return gui_style_sheet


def get_formatted_gui_style_sheet() -> str:
    """
    Get and format style sheet (replaces variables defined in style sheet with
    corresponding values).

    Also defines values for variables in the style sheet.

    Returns
    -------
    str
        Formatted style sheet.

    """

    # Get style sheet
    gui_style_sheet = get_gui_style_sheet()

    # Dictionary of terms to replace (all marked with {} ) in style sheet
    # Note on MacOS, background by default is #ececec -
    # should have good contrast with that colour

    # Primary colour, with variations for different states
    clr_primary = "#30819C"
    clr_primary_disabled = "#A4C1CB"
    clr_primary_hover = "#276A7E"
    clr_primary_pressed = "#1E5362"

    # Secondary colour (will set to same colour as primary, but use separate
    # variable for flexibility; using purple to test)
    clr_secondary = "purple"

    # Dictionary for defining different variables in style sheet
    style_var = {
        # theme colors
        "{clr_primary}": clr_primary,  # should have high contrast with white
        "{clr_primary_dark}": "#276A7E",  # darker version for text on light background
        "{clr_primary_disabled}": clr_primary_disabled,
        "{clr_primary_hover}": clr_primary_hover,
        "{clr_primary_pressed}": clr_primary_pressed,
        "{clr_secondary}": clr_secondary,
        "{clr_warning}": "#A33221",  # should be a shade of red/orange
        # text colors
        "{clr_text_dark}": "#0D0D0D",
        "{clr_text_medium}": "#404040",
        "{clr_text_light}": "#656565",
        # large buttons - will use primary colors directly
        "{clr_large_button_text}": "white",  # light text
        # small buttons - will use primary colors directly as outline and text
        "{clr_small_button}": "white",
        # icon buttons
        # all buttons
        "{radius_button}": "4",
        # borders
        "{clr_border}": "#808080",
        "{clr_border_light}": "#D9D9D9",
        # background color (for when do not use default)
        "{clr_background}": "white",
    }

    # Replace variables in style sheet with corresponding values
    for k, v in style_var.items():
        gui_style_sheet = gui_style_sheet.replace(k, v)

    # Return formatted style sheet
    return gui_style_sheet
