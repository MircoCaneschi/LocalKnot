"""
Refactored Knots View - MVVM Pattern.

This View layer receives a KnotsViewModel and binds UI widgets to its Properties and Signals.
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QFormLayout, QHBoxLayout, QGridLayout, QPushButton,
    QComboBox, QLineEdit, QCheckBox, QLabel
)

from gui.components.common_widgets import create_shift_buttons
from mvvm.viewmodels import KnotsViewModel


class KnotsView:
    """Knots View Component (MVVM)."""

    def __init__(self, view_model: KnotsViewModel):
        """Initialize the Knots View with a ViewModel."""
        self.view_model = view_model

        # Main panel components
        self.main_layout = None
        self.knot_no_combo = None
        self.right_shift_btn = None
        self.left_shift_btn = None
        self.new_btn = None
        self.save_btn = None
        self.delete_btn = None
        self.x_line = None
        self.pith_z_line = None
        self.pith_y_line = None
        self.comment_line = None
        self.fake_pith = None

        # Hidden panel components
        self.hidden_main_layout = None
        self.hidden_knot_no_combo = None
        self.hidden_right_shift_btn = None
        self.hidden_left_shift_btn = None
        self.hidden_x_line = None
        self.hidden_pith_z_line = None
        self.hidden_pith_y_line = None
        self.hidden_fake_pith = None

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
        self.main_layout.setSpacing(2)

        # sub-layouts in the grid
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(2)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(5, 0, 0, 0)
        bottom_layout.setSpacing(2)

        crud_layout = QVBoxLayout()
        crud_layout.setContentsMargins(0, 0, 0, 0)
        crud_layout.setSpacing(2)

        data_layout = QFormLayout()
        data_layout.setContentsMargins(5, 0, 5, 0)
        data_layout.setSpacing(2)

        # bottom layout
        self.knot_no_combo = QComboBox()
        self.knot_no_combo.setEditable(True)
        bottom_layout.addWidget(self.knot_no_combo, 1)

        # top layout - shifts
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
        self.x_line = QLineEdit()
        self.pith_z_line = QLineEdit()
        self.pith_y_line = QLineEdit()
        self.comment_line = QLineEdit()
        self.fake_pith = QCheckBox()
        self.fake_pith.setChecked(False)

        data_layout.addRow("X", self.x_line)
        data_layout.addRow("Pith Z", self.pith_z_line)
        data_layout.addRow("Pith Y", self.pith_y_line)
        data_layout.addRow("Comment", self.comment_line)
        data_layout.addRow("Fake pith", self.fake_pith)

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
        self.hidden_knot_no_combo = QComboBox()
        self.hidden_knot_no_combo.setEditable(True)
        hidden_bottom_layout.addWidget(self.hidden_knot_no_combo)

        # top layout
        self.hidden_right_shift_btn, self.hidden_left_shift_btn = create_shift_buttons()
        hidden_top_layout.addWidget(self.hidden_right_shift_btn)
        hidden_top_layout.addWidget(self.hidden_left_shift_btn)

        # data layout
        self.hidden_x_line = QLineEdit()
        self.hidden_pith_z_line = QLineEdit()
        self.hidden_pith_y_line = QLineEdit()

        x = QFormLayout()
        x.setContentsMargins(0, 0, 0, 0)
        pith_z = QFormLayout()
        pith_z.setContentsMargins(5, 0, 0, 0)
        pith_y = QFormLayout()
        pith_y.setContentsMargins(5, 0, 0, 0)
        x.addRow("X", self.hidden_x_line)
        pith_z.addRow("Pith Z", self.hidden_pith_z_line)
        pith_y.addRow("Pith Y", self.hidden_pith_y_line)
        hidden_data_layout.addLayout(x)
        hidden_data_layout.addLayout(pith_z)
        hidden_data_layout.addLayout(pith_y)

        self.hidden_fake_pith = QCheckBox()
        self.hidden_fake_pith.setChecked(False)
        hidden_data_layout.addWidget(self.hidden_fake_pith)

        # grid disposition
        self.hidden_main_layout.addLayout(hidden_top_layout, 0, 1, 1, 1)
        self.hidden_main_layout.addLayout(hidden_bottom_layout, 0, 0, 1, 1)
        self.hidden_main_layout.addLayout(hidden_data_layout, 1, 0, 3, 2)

    # ==================== BINDING ====================

    def _bind_to_view_model(self):
        """Establish all connections between View and ViewModel."""
        # Widget signals → ViewModel Slots
        self.new_btn.clicked.connect(self.view_model.handle_new_knot)
        self.save_btn.clicked.connect(self.view_model.handle_save_knot)
        self.delete_btn.clicked.connect(self.view_model.handle_delete_knot)
        self.knot_no_combo.currentTextChanged.connect(self.view_model.handle_knot_selected)

        # Line edits sync with ViewModel
        self.x_line.textChanged.connect(lambda: setattr(self.view_model, 'x', self.x_line.text() or 0))
        self.pith_z_line.textChanged.connect(lambda: setattr(self.view_model, 'pith_z', self.pith_z_line.text() or 0))
        self.pith_y_line.textChanged.connect(lambda: setattr(self.view_model, 'pith_y', self.pith_y_line.text() or 0))
        self.comment_line.textChanged.connect(lambda: setattr(self.view_model, 'comment', self.comment_line.text()))
        self.fake_pith.stateChanged.connect(lambda: setattr(self.view_model, 'is_fake_pith', self.fake_pith.isChecked()))

        # ViewModel Signals → View update methods
        self.view_model.knots_changed.connect(self._on_knots_changed)
        self.view_model.knot_data_changed.connect(self._on_knot_data_changed)
        self.view_model.knot_error.connect(self._on_knot_error)
        self.view_model.knot_saved.connect(self._on_knot_saved)

    # ==================== SIGNAL HANDLERS ====================

    def _on_knots_changed(self, knots: list):
        """Update knot combo box when knots list changes."""
        self.knot_no_combo.clear()
        self.knot_no_combo.addItems(knots)

    def _on_knot_data_changed(self):
        """Update UI when ViewModel knot data changes."""
        self.x_line.setText(str(self.view_model.x))
        self.pith_z_line.setText(str(self.view_model.pith_z))
        self.pith_y_line.setText(str(self.view_model.pith_y))
        self.comment_line.setText(self.view_model.comment)
        self.fake_pith.setChecked(self.view_model.is_fake_pith)

    def _on_knot_error(self, error_message: str):
        """Display error message on validation failure."""
        pass

    def _on_knot_saved(self, knot_no: str):
        """Show success message when knot is saved."""
        pass

