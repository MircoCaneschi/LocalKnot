"""
Refactored Boards View - MVVM Pattern.

This View layer receives a BoardsViewModel and binds UI widgets to its Properties and Signals.
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QFormLayout, QHBoxLayout, QGridLayout, QPushButton,
    QComboBox, QLineEdit, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt

from gui.components.common_widgets import create_shift_buttons
from mvvm.viewmodels import BoardsViewModel


class BoardsView:
    """Boards View Component (MVVM)."""

    def __init__(self, view_model: BoardsViewModel):
        """Initialize the Boards View with a ViewModel."""
        self.view_model = view_model

        # Main panel components
        self.main_layout = None
        self.board_no_combo = None
        self.right_shift_btn = None
        self.left_shift_btn = None
        self.new_btn = None
        self.save_btn = None
        self.delete_btn = None
        self.height_line = None
        self.base_line = None
        self.length_line = None
        self.testpos_line = None
        self.comment_line = None

        # Hidden panel components
        self.hidden_main_layout = None
        self.hidden_board_no_combo = None
        self.hidden_right_shift_btn = None
        self.hidden_left_shift_btn = None
        self.hidden_height_line = None
        self.hidden_base_line = None
        self.hidden_length_line = None

        # Setup UI
        self._setup_main_layout()
        self._setup_hidden_layout()

        # Bind ViewModel
        self._bind_to_view_model()

    # ==================== SETUP UI ====================

    def _setup_main_layout(self):
        """Create and layout all main panel UI components."""
        # main grid layout
        self.main_layout = QGridLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # sub-layouts in the grid
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(5, 0, 0, 0)
        top_layout.setSpacing(2)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(5, 0, 0, 0)
        bottom_layout.setSpacing(2)

        crud_layout = QVBoxLayout()
        crud_layout.setContentsMargins(0, 0, 0, 0)
        crud_layout.setSpacing(2)

        data_layout = QFormLayout()
        data_layout.setContentsMargins(5, 0, 5, 5)
        data_layout.setSpacing(2)

        # bottom layout - combo box
        self.board_no_combo = QComboBox()
        self.board_no_combo.setEditable(True)
        bottom_layout.addWidget(self.board_no_combo, 1)

        # shifts
        self.right_shift_btn, self.left_shift_btn = create_shift_buttons()
        top_layout.addWidget(self.right_shift_btn)
        top_layout.addWidget(self.left_shift_btn)
        top_layout.addStretch(1)

        # crud layout
        crud_layout.addLayout(top_layout)
        self.new_btn = QPushButton("New+")
        self.save_btn = QPushButton("Save")
        self.delete_btn = QPushButton("Del-")
        for btn in [self.new_btn, self.save_btn, self.delete_btn]:
            btn.setMinimumWidth(50)
        crud_layout.addWidget(self.new_btn)
        crud_layout.addWidget(self.save_btn)
        crud_layout.addWidget(self.delete_btn)

        # data layout
        self.height_line = QLineEdit()
        self.base_line = QLineEdit()
        self.length_line = QLineEdit()
        self.testpos_line = QLineEdit()
        self.comment_line = QLineEdit()
        data_layout.addRow("Height", self.height_line)
        data_layout.addRow("Base", self.base_line)
        data_layout.addRow("Length", self.length_line)
        data_layout.addRow("TestPos", self.testpos_line)
        data_layout.addRow("Comment", self.comment_line)

        # grid disposition
        self.main_layout.addLayout(bottom_layout, 1, 0, 1, 1)
        self.main_layout.addLayout(crud_layout, 1, 1, 3, 1)
        self.main_layout.addLayout(data_layout, 0, 2, 6, 1)

    def _setup_hidden_layout(self):
        """Create and layout all hidden panel UI components."""
        # main grid layout
        self.hidden_main_layout = QGridLayout()
        self.hidden_main_layout.setContentsMargins(0, 7, 0, 0)
        self.hidden_main_layout.setSpacing(2)

        # sub-layouts in the grid
        hidden_top_layout = QHBoxLayout()
        hidden_top_layout.setContentsMargins(0, 0, 5, 0)
        hidden_top_layout.setSpacing(2)

        hidden_bottom_layout = QHBoxLayout()
        hidden_bottom_layout.setContentsMargins(5, 0, 0, 0)
        hidden_bottom_layout.setSpacing(2)

        hidden_data_layout = QHBoxLayout()
        hidden_data_layout.setContentsMargins(5, 5, 5, 5)
        hidden_data_layout.setSpacing(2)

        # bottom layout
        self.hidden_board_no_combo = QComboBox()
        self.hidden_board_no_combo.setEditable(True)
        hidden_bottom_layout.addWidget(self.hidden_board_no_combo)

        # shifts
        self.hidden_right_shift_btn, self.hidden_left_shift_btn = create_shift_buttons()
        hidden_top_layout.addWidget(self.hidden_right_shift_btn)
        hidden_top_layout.addWidget(self.hidden_left_shift_btn)

        # data layout
        self.hidden_height_line = QLineEdit()
        self.hidden_base_line = QLineEdit()
        self.hidden_length_line = QLineEdit()

        height = QFormLayout()
        height.setContentsMargins(0, 0, 0, 0)
        base = QFormLayout()
        base.setContentsMargins(5, 0, 0, 0)
        length = QFormLayout()
        length.setContentsMargins(5, 0, 0, 0)
        height.addRow("Height", self.hidden_height_line)
        base.addRow("Base", self.hidden_base_line)
        length.addRow("Length", self.hidden_length_line)
        hidden_data_layout.addLayout(height)
        hidden_data_layout.addLayout(base)
        hidden_data_layout.addLayout(length)

        # grid disposition
        self.hidden_main_layout.addLayout(hidden_top_layout, 0, 1, 1, 1)
        self.hidden_main_layout.addLayout(hidden_bottom_layout, 0, 0, 1, 1)
        self.hidden_main_layout.addLayout(hidden_data_layout, 1, 0, 3, 2)

    # ==================== BINDING ====================

    def _bind_to_view_model(self):
        """Establish all connections between View and ViewModel."""
        # Widget signals → ViewModel Slots
        self.new_btn.clicked.connect(self.view_model.handle_new_board)
        self.save_btn.clicked.connect(self.view_model.handle_save_board)
        self.delete_btn.clicked.connect(self.view_model.handle_delete_board)
        self.board_no_combo.currentTextChanged.connect(self.view_model.handle_board_selected)

        # Line edits sync with ViewModel
        self.height_line.textChanged.connect(lambda: setattr(self.view_model, 'height', self.height_line.text() or 0))
        self.base_line.textChanged.connect(lambda: setattr(self.view_model, 'base', self.base_line.text() or 0))
        self.length_line.textChanged.connect(lambda: setattr(self.view_model, 'length', self.length_line.text() or 0))
        self.testpos_line.textChanged.connect(lambda: setattr(self.view_model, 'test_position', self.testpos_line.text()))
        self.comment_line.textChanged.connect(lambda: setattr(self.view_model, 'comment', self.comment_line.text()))

        # ViewModel Signals → View update methods
        self.view_model.boards_changed.connect(self._on_boards_changed)
        self.view_model.board_data_changed.connect(self._on_board_data_changed)
        self.view_model.board_error.connect(self._on_board_error)
        self.view_model.board_saved.connect(self._on_board_saved)

    # ==================== SIGNAL HANDLERS ====================

    def _on_boards_changed(self, boards: list):
        """Update board combo box when boards list changes."""
        self.board_no_combo.clear()
        self.board_no_combo.addItems(boards)

    def _on_board_data_changed(self):
        """Update UI when ViewModel board data changes."""
        self.height_line.setText(str(self.view_model.height))
        self.base_line.setText(str(self.view_model.base))
        self.length_line.setText(str(self.view_model.length))
        self.testpos_line.setText(self.view_model.test_position)
        self.comment_line.setText(self.view_model.comment)

    def _on_board_error(self, error_message: str):
        """Display error message on validation failure."""
        pass

    def _on_board_saved(self, board_no: str):
        """Show success message when board is saved."""
        pass

