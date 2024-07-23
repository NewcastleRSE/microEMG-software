"""
Generic functions for creating and modifying widgets.
"""


def set_retain_size(widget, retain_size: bool):
    """
    Set whether a widget's size should be retained when hidden.
    Parameters
    ----------
    widget : QWidget
        Qt Widget.
    retain_size : bool
        Whether to retain the widget's size when hidden.

    Returns
    -------
    None.

    """
    size_policy = widget.sizePolicy()
    size_policy.setRetainSizeWhenHidden(retain_size)
    widget.setSizePolicy(size_policy)
