from PySide6.QtWidgets import QSizePolicy


def fix_widget_size(my_widget, w, h):
    # Set widget min size and set size policy to Fixed

    # set size properties
    w_sz = my_widget.sizeHint()
    if w is not None:
        w_sz.setWidth(w)
    if h is not None:
        w_sz.setHeight(h)
    my_widget.setMinimumSize(w_sz)
    my_widget.setMaximumSize(w_sz)

    # size policy = fixed so does not expand if widget size changes
    my_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
