"""Common reusable widgets for the GUI."""

from PySide6.QtWidgets import QPushButton, QSizePolicy


def create_shift_buttons():
    """
    Creates and configures shift buttons (< and >).

    Returns:
        tuple: (right_button, left_button) - QPushButton instances ready to use
    """
    right_btn = QPushButton("<")
    left_btn = QPushButton(">")

    # Configure size policy
    right_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    left_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    # Set fixed dimensions
    right_btn.setMaximumWidth(30)
    right_btn.setMinimumWidth(30)
    left_btn.setMaximumWidth(30)
    left_btn.setMinimumWidth(30)



    return right_btn, left_btn

