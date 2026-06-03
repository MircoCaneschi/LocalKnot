"""
Refactored Boards View - MVVM Pattern.

This View layer receives a BoardsViewModel and binds UI widgets to its Properties and Signals.
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QFormLayout, QHBoxLayout, QGridLayout, QPushButton,
    QComboBox, QLineEdit, QLabel, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QIntValidator, QRegularExpressionValidator

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
        self.board_msg = None

        # Hidden panel components
        self.hidden_main_layout = None
        self.hidden_board_no_combo = None
        self.hidden_right_shift_btn = None
        self.hidden_left_shift_btn = None
        self.hidden_height_line = None
        self.hidden_base_line = None
        self.hidden_length_line = None
        
        # Label references for animation
        self.height_label = None
        self.base_label = None
        self.length_label = None
        self.hidden_height_label = None
        self.hidden_base_label = None
        self.hidden_length_label = None
        self._animations = []

        # Setup UI
        self._setup_main_layout()
        self._setup_hidden_layout()

        # Bind ViewModel
        self._bind_to_view_model()
        
        # Initial states
        self.save_btn.setEnabled(False)
        self.set_board_editable(False)

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
        self.board_no_combo.setEditable(False)
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
        
        float_regex = QRegularExpression(r"^[0-9]*([.,][0-9]{0,2})?$")
        
        self.height_line.setValidator(QRegularExpressionValidator(float_regex))
        self.base_line.setValidator(QRegularExpressionValidator(float_regex))
        self.length_line.setValidator(QRegularExpressionValidator(float_regex))
        self.testpos_line.setValidator(QIntValidator(0, 999999))
        
        self.height_label = QLabel("Height")
        self.base_label = QLabel("Base")
        self.length_label = QLabel("Length")
        
        data_layout.addRow(self.height_label, self.height_line)
        data_layout.addRow(self.base_label, self.base_line)
        data_layout.addRow(self.length_label, self.length_line)
        data_layout.addRow("TestPos", self.testpos_line)
        data_layout.addRow("Comment", self.comment_line)

        # Message label
        self.board_msg = QLabel()
        self.board_msg.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.board_msg.hide()

        # grid disposition
        self.main_layout.addLayout(bottom_layout, 1, 0, 1, 1)
        self.main_layout.addLayout(crud_layout, 1, 1, 3, 1)
        self.main_layout.addLayout(data_layout, 0, 2, 6, 1)
        self.main_layout.addWidget(self.board_msg, 4, 0, 1, 2)

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
        self.hidden_board_no_combo.setEditable(False)
        hidden_bottom_layout.addWidget(self.hidden_board_no_combo)

        # shifts
        self.hidden_right_shift_btn, self.hidden_left_shift_btn = create_shift_buttons()
        hidden_top_layout.addWidget(self.hidden_right_shift_btn)
        hidden_top_layout.addWidget(self.hidden_left_shift_btn)

        # data layout
        self.hidden_height_line = QLineEdit()
        self.hidden_base_line = QLineEdit()
        self.hidden_length_line = QLineEdit()
        
        float_regex = QRegularExpression(r"^[0-9]*([.,][0-9]{0,2})?$")
        
        self.hidden_height_line.setValidator(QRegularExpressionValidator(float_regex))
        self.hidden_base_line.setValidator(QRegularExpressionValidator(float_regex))
        self.hidden_length_line.setValidator(QRegularExpressionValidator(float_regex))

        height = QFormLayout()
        height.setContentsMargins(0, 0, 0, 0)
        base = QFormLayout()
        base.setContentsMargins(5, 0, 0, 0)
        length = QFormLayout()
        length.setContentsMargins(5, 0, 0, 0)
        self.hidden_height_label = QLabel("Height")
        self.hidden_base_label = QLabel("Base")
        self.hidden_length_label = QLabel("Length")
        
        height.addRow(self.hidden_height_label, self.hidden_height_line)
        base.addRow(self.hidden_base_label, self.hidden_base_line)
        length.addRow(self.hidden_length_label, self.hidden_length_line)
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
        # Hide messages on interaction (Connect FIRST so it runs before other slots)
        for combo in [self.board_no_combo, self.hidden_board_no_combo]:
            combo.activated.connect(self._hide_messages)
            if combo.lineEdit():
                combo.lineEdit().textEdited.connect(self._hide_messages)
        
        for le in [self.height_line, self.base_line, self.length_line, self.testpos_line, self.comment_line,
                   self.hidden_height_line, self.hidden_base_line, self.hidden_length_line]:
            le.textEdited.connect(self._hide_messages)

        for btn in [self.new_btn, self.delete_btn, self.right_shift_btn, self.left_shift_btn,
                    self.hidden_right_shift_btn, self.hidden_left_shift_btn]:
            btn.clicked.connect(self._hide_messages)

        # Widget signals → ViewModel Slots
        self.new_btn.clicked.connect(self.view_model.handle_new_board)
        self.save_btn.clicked.connect(self.view_model.handle_save_board)
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        
        self.right_shift_btn.clicked.connect(self.view_model.handle_previous_board)
        self.left_shift_btn.clicked.connect(self.view_model.handle_next_board)
        self.hidden_right_shift_btn.clicked.connect(self.view_model.handle_previous_board)
        self.hidden_left_shift_btn.clicked.connect(self.view_model.handle_next_board)
        
        self.board_no_combo.currentTextChanged.connect(lambda text: setattr(self.view_model, 'current_board_no', text))
        self.hidden_board_no_combo.currentTextChanged.connect(lambda text: setattr(self.view_model, 'current_board_no', text))

        # Line edits sync with ViewModel
        self.height_line.textChanged.connect(lambda: setattr(self.view_model, 'height', self.height_line.text() or 0))
        self.base_line.textChanged.connect(lambda: setattr(self.view_model, 'base', self.base_line.text() or 0))
        self.length_line.textChanged.connect(lambda: setattr(self.view_model, 'length', self.length_line.text() or 0))
        self.testpos_line.textChanged.connect(lambda: setattr(self.view_model, 'test_position', self.testpos_line.text()))
        self.comment_line.textChanged.connect(lambda: setattr(self.view_model, 'comment', self.comment_line.text()))
        
        self.hidden_height_line.textChanged.connect(lambda: setattr(self.view_model, 'height', self.hidden_height_line.text() or 0))
        self.hidden_base_line.textChanged.connect(lambda: setattr(self.view_model, 'base', self.hidden_base_line.text() or 0))
        self.hidden_length_line.textChanged.connect(lambda: setattr(self.view_model, 'length', self.hidden_length_line.text() or 0))

        # Sync main and hidden line edits directly
        self.height_line.textEdited.connect(self.hidden_height_line.setText)
        self.hidden_height_line.textEdited.connect(self.height_line.setText)
        
        self.base_line.textEdited.connect(self.hidden_base_line.setText)
        self.hidden_base_line.textEdited.connect(self.base_line.setText)
        
        self.length_line.textEdited.connect(self.hidden_length_line.setText)
        self.hidden_length_line.textEdited.connect(self.length_line.setText)

        # ViewModel Signals → View update methods
        self.view_model.boards_changed.connect(self._on_boards_changed)
        self.view_model.board_data_changed.connect(self._on_board_data_changed)
        self.view_model.board_error.connect(self._on_board_error)
        self.view_model.board_saved.connect(self._on_board_saved)
        self.view_model.board_editable_changed.connect(self.set_board_editable)
        self.view_model.current_board_changed.connect(self._on_current_board_changed)
        self.view_model.hide_messages.connect(self.board_msg.hide)
        self.view_model.save_enabled_changed.connect(self.save_btn.setEnabled)
        self.view_model.validation_failed.connect(self._on_validation_failed)

    # ==================== SIGNAL HANDLERS ====================

    def _hide_messages(self, *args):
        """Hide all messages in this view."""
        self.board_msg.hide()

    def _on_boards_changed(self, boards: list):
        """Update board combo box when boards list changes."""
        self.board_no_combo.blockSignals(True)
        self.hidden_board_no_combo.blockSignals(True)
        
        self.board_no_combo.clear()
        self.board_no_combo.addItems(boards)
        
        self.hidden_board_no_combo.clear()
        self.hidden_board_no_combo.addItems(boards)
        
        self.board_no_combo.blockSignals(False)
        self.hidden_board_no_combo.blockSignals(False)

    def _on_board_data_changed(self):
        """Update UI when ViewModel board data changes."""
        line_edits = [
            self.height_line, self.base_line, self.length_line,
            self.testpos_line, self.comment_line,
            self.hidden_height_line, self.hidden_base_line, self.hidden_length_line
        ]
        
        for le in line_edits:
            if le: le.blockSignals(True)
            
        def format_float(val: float) -> str:
            s = f"{val:.2f}".rstrip('0').rstrip('.')
            return s if s else "0"
            
        self.height_line.setText(format_float(self.view_model.height))
        self.base_line.setText(format_float(self.view_model.base))
        self.length_line.setText(format_float(self.view_model.length))
        self.testpos_line.setText(str(self.view_model.test_position))
        self.comment_line.setText(str(self.view_model.comment))
        
        if self.hidden_height_line:
            self.hidden_height_line.setText(format_float(self.view_model.height))
        if self.hidden_base_line:
            self.hidden_base_line.setText(format_float(self.view_model.base))
        if self.hidden_length_line:
            self.hidden_length_line.setText(format_float(self.view_model.length))
            
        for le in line_edits:
            if le: le.blockSignals(False)

    def _on_board_error(self, error_message: str):
        """Display error message on validation failure."""
        self.board_msg.setText(error_message)
        self.board_msg.show()

    def _on_board_saved(self, message: str):
        """Show success message when board is saved."""
        self.board_msg.setText(message)
        self.board_msg.show()

    def _on_delete_clicked(self):
        """Handle delete button click with confirmation."""
        board_no = self.view_model.current_board_no
        if not board_no:
            return

        reply = QMessageBox.question(
            self.delete_btn.window(), 'Delete Board',
            f"Are you sure you want to delete board '{board_no}'?\n"
            "This will also delete all associated knots.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.view_model.handle_delete_board()

    def _on_current_board_changed(self, text: str):
        """Sync combo boxes when current board changes programmatically."""
        self.board_no_combo.blockSignals(True)
        self.hidden_board_no_combo.blockSignals(True)
        self.board_no_combo.setCurrentText(text)
        self.hidden_board_no_combo.setCurrentText(text)
        self.board_no_combo.blockSignals(False)
        self.hidden_board_no_combo.blockSignals(False)

    def _on_validation_failed(self, invalid_fields: list):
        """Flash the labels of the invalid fields."""
        from PySide6.QtCore import QVariantAnimation, QAbstractAnimation
        from PySide6.QtGui import QColor

        def _flash_label(label: QLabel):
            if not label: return
            anim = QVariantAnimation(label)
            anim.setDuration(300)
            anim.setStartValue(QColor("red"))
            anim.setEndValue(label.palette().color(label.foregroundRole()))
            anim.setLoopCount(3)
            
            self._animations.append(anim)
            anim.finished.connect(lambda a=anim: self._animations.remove(a) if a in self._animations else None)
            anim.finished.connect(lambda l=label: l.setStyleSheet(""))
            anim.valueChanged.connect(lambda color, l=label: l.setStyleSheet(f"color: {color.name()};"))
            anim.start(QAbstractAnimation.DeleteWhenStopped)

        if "Height" in invalid_fields:
            _flash_label(self.height_label)
            _flash_label(self.hidden_height_label)
        if "Base" in invalid_fields:
            _flash_label(self.base_label)
            _flash_label(self.hidden_base_label)
        if "Length" in invalid_fields:
            _flash_label(self.length_label)
            _flash_label(self.hidden_length_label)

    def set_board_editable(self, state: bool):
        """Enable or disable editing for board combobox and buttons."""
        self.board_no_combo.blockSignals(True)
        self.hidden_board_no_combo.blockSignals(True)
        
        self.board_no_combo.setEditable(state)
        self.hidden_board_no_combo.setEditable(state)
        
        if state:
            self.board_no_combo.setValidator(QIntValidator(1, 999999))
            self.hidden_board_no_combo.setValidator(QIntValidator(1, 999999))
        
        if not state:
            self.board_no_combo.setCurrentText(self.view_model.current_board_no)
            self.hidden_board_no_combo.setCurrentText(self.view_model.current_board_no)
            
        self.board_no_combo.blockSignals(False)
        self.hidden_board_no_combo.blockSignals(False)
        
        self.save_btn.setEnabled(state)
        self.delete_btn.setEnabled(not state)
        
        self.left_shift_btn.setEnabled(not state)
        self.right_shift_btn.setEnabled(not state)
        self.hidden_left_shift_btn.setEnabled(not state)
        self.hidden_right_shift_btn.setEnabled(not state)

