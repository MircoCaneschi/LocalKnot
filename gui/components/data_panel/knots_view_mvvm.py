"""
Refactored Knots View - MVVM Pattern.

This View layer receives a KnotsViewModel and binds UI widgets to its Properties and Signals.
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QFormLayout, QHBoxLayout, QGridLayout, QPushButton,
    QComboBox, QLineEdit, QCheckBox, QLabel, QMessageBox, QSizePolicy
)
from PySide6.QtGui import QIntValidator

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
        self.pruned_knot = None
        self.knot_msg = None

        # Hidden panel components
        self.hidden_main_layout = None
        self.hidden_knot_no_combo = None
        self.hidden_right_shift_btn = None
        self.hidden_left_shift_btn = None
        self.hidden_x_line = None
        self.hidden_pith_z_line = None
        self.hidden_pith_y_line = None
        self.hidden_pruned_knot = None
        
        self._last_pruned_state = False
        self._fade_in_anim = None
        
        # Label references for animation
        self.x_label = None
        self.hidden_x_label = None
        self.pith_z_label = None
        self.pith_y_label = None
        self.hidden_pith_z_label = None
        self.hidden_pith_y_label = None
        self._animations = []

        # Setup UI
        self._setup_main_layout()
        self._setup_hidden_layout()

        # Bind ViewModel
        self._bind_to_view_model()
        
        # Initial states
        self.save_btn.setEnabled(False)
        self.set_knot_editable(False)

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
        self.knot_no_combo.setEditable(False)
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
        
        validator = QIntValidator()
        self.x_line.setValidator(validator)
        self.pith_z_line.setValidator(validator)
        self.pith_y_line.setValidator(validator)
        
        self.comment_line = QLineEdit()
        self.pruned_knot = QCheckBox()
        self.pruned_knot.setChecked(False)

        self.x_label = QLabel("X")
        self.pith_z_label = QLabel("Pith Z")
        self.pith_y_label = QLabel("Pith Y")
        data_layout.addRow(self.x_label, self.x_line)
        data_layout.addRow(self.pith_z_label, self.pith_z_line)
        data_layout.addRow(self.pith_y_label, self.pith_y_line)
        data_layout.addRow("Comment", self.comment_line)
        data_layout.addRow("Pruned knot", self.pruned_knot)

        # Message label
        self.knot_msg = QLabel()
        sp = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        sp.setRetainSizeWhenHidden(True)
        self.knot_msg.setSizePolicy(sp)
        self.knot_msg.hide()

        # grid disposition
        self.main_layout.addLayout(bottom_layout, 1, 0, 1, 1)
        self.main_layout.addLayout(crud_layout, 1, 1, 3, 1)
        self.main_layout.addLayout(data_layout, 0, 2, 6, 1)
        self.main_layout.addWidget(self.knot_msg, 4, 0, 1, 2)

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
        self.hidden_knot_no_combo.setEditable(False)
        hidden_bottom_layout.addWidget(self.hidden_knot_no_combo)

        # top layout
        self.hidden_right_shift_btn, self.hidden_left_shift_btn = create_shift_buttons()
        hidden_top_layout.addWidget(self.hidden_right_shift_btn)
        hidden_top_layout.addWidget(self.hidden_left_shift_btn)

        # data layout
        self.hidden_x_line = QLineEdit()
        self.hidden_pith_z_line = QLineEdit()
        self.hidden_pith_y_line = QLineEdit()
        
        validator = QIntValidator()
        self.hidden_x_line.setValidator(validator)
        self.hidden_pith_z_line.setValidator(validator)
        self.hidden_pith_y_line.setValidator(validator)

        x = QFormLayout()
        x.setContentsMargins(0, 0, 0, 0)
        pith_z = QFormLayout()
        pith_z.setContentsMargins(5, 0, 0, 0)
        pith_y = QFormLayout()
        pith_y.setContentsMargins(5, 0, 0, 0)
        
        self.hidden_x_label = QLabel("X")
        self.hidden_pith_z_label = QLabel("Pith Z")
        self.hidden_pith_y_label = QLabel("Pith Y")
        x.addRow(self.hidden_x_label, self.hidden_x_line)
        pith_z.addRow(self.hidden_pith_z_label, self.hidden_pith_z_line)
        pith_y.addRow(self.hidden_pith_y_label, self.hidden_pith_y_line)
        hidden_data_layout.addLayout(x)
        hidden_data_layout.addLayout(pith_z)
        hidden_data_layout.addLayout(pith_y)

        self.hidden_pruned_knot = QCheckBox()
        self.hidden_pruned_knot.setChecked(False)
        hidden_data_layout.addWidget(self.hidden_pruned_knot)

        # grid disposition
        self.hidden_main_layout.addLayout(hidden_top_layout, 0, 1, 1, 1)
        self.hidden_main_layout.addLayout(hidden_bottom_layout, 0, 0, 1, 1)
        self.hidden_main_layout.addLayout(hidden_data_layout, 1, 0, 3, 2)

    # ==================== BINDING ====================

    def _bind_to_view_model(self):
        """Establish all connections between View and ViewModel."""
        # Hide messages on interaction (Connect FIRST so it runs before other slots)
        for combo in [self.knot_no_combo, self.hidden_knot_no_combo]:
            combo.activated.connect(self._hide_messages)
        
        for le in [self.x_line, self.pith_z_line, self.pith_y_line, self.comment_line,
                   self.hidden_x_line, self.hidden_pith_z_line, self.hidden_pith_y_line]:
            le.textEdited.connect(self._hide_messages)

        for cb in [self.pruned_knot, self.hidden_pruned_knot]:
            cb.clicked.connect(self._hide_messages)

        for btn in [self.new_btn, self.delete_btn, self.right_shift_btn, self.left_shift_btn,
                    self.hidden_right_shift_btn, self.hidden_left_shift_btn]:
            btn.clicked.connect(self._hide_messages)

        # Widget signals → ViewModel Slots
        self.new_btn.clicked.connect(self.view_model.handle_new_knot)
        self.save_btn.clicked.connect(self.view_model.handle_save_knot)
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        self.knot_no_combo.currentTextChanged.connect(lambda text: setattr(self.view_model, 'current_knot_no', text))
        self.hidden_knot_no_combo.currentTextChanged.connect(lambda text: setattr(self.view_model, 'current_knot_no', text))
        
        self.right_shift_btn.clicked.connect(self.view_model.handle_previous_knot)
        self.left_shift_btn.clicked.connect(self.view_model.handle_next_knot)
        self.hidden_right_shift_btn.clicked.connect(self.view_model.handle_previous_knot)
        self.hidden_left_shift_btn.clicked.connect(self.view_model.handle_next_knot)

        # Line edits sync with ViewModel
        self.x_line.textChanged.connect(lambda: setattr(self.view_model, 'x', self.x_line.text() or 0))
        self.pith_z_line.textChanged.connect(self._update_z)
        self.pith_y_line.textChanged.connect(self._update_y)
        self.comment_line.textChanged.connect(lambda: setattr(self.view_model, 'comment', self.comment_line.text()))
        self.pruned_knot.stateChanged.connect(lambda: setattr(self.view_model, 'is_pruned_knot', self.pruned_knot.isChecked()))

        # Also sync hidden components with ViewModel
        self.hidden_x_line.textChanged.connect(lambda: setattr(self.view_model, 'x', self.hidden_x_line.text() or 0))
        self.hidden_pith_z_line.textChanged.connect(self._update_z)
        self.hidden_pith_y_line.textChanged.connect(self._update_y)
        self.hidden_pruned_knot.stateChanged.connect(lambda: setattr(self.view_model, 'is_pruned_knot', self.hidden_pruned_knot.isChecked()))

        # Sync main and hidden components directly
        self.x_line.textEdited.connect(self.hidden_x_line.setText)
        self.hidden_x_line.textEdited.connect(self.x_line.setText)
        
        self.pith_z_line.textEdited.connect(self.hidden_pith_z_line.setText)
        self.hidden_pith_z_line.textEdited.connect(self.pith_z_line.setText)
        
        self.pith_y_line.textEdited.connect(self.hidden_pith_y_line.setText)
        self.hidden_pith_y_line.textEdited.connect(self.pith_y_line.setText)
        
        self.pruned_knot.toggled.connect(self.hidden_pruned_knot.setChecked)
        self.hidden_pruned_knot.toggled.connect(self.pruned_knot.setChecked)

        # ViewModel Signals → View update methods
        self.view_model.knots_changed.connect(self._on_knots_changed)
        self.view_model.knot_data_changed.connect(self._on_knot_data_changed)
        self.view_model.knot_error.connect(self._on_knot_error)
        self.view_model.knot_saved.connect(self._on_knot_saved)
        self.view_model.knot_editable_changed.connect(self.set_knot_editable)
        self.view_model.current_knot_changed.connect(self._on_current_knot_changed)
        self.view_model.hide_messages.connect(self.knot_msg.hide)
        self.view_model.save_enabled_changed.connect(self.save_btn.setEnabled)
        self.view_model.validation_failed.connect(self._on_validation_failed)

    def _update_z(self, text):
        if self.pruned_knot.isChecked():
            setattr(self.view_model, 'pruned_z', text)
        else:
            setattr(self.view_model, 'pith_z', text)
            
    def _update_y(self, text):
        if self.pruned_knot.isChecked():
            setattr(self.view_model, 'pruned_y', text)
        else:
            setattr(self.view_model, 'pith_y', text)

    # ==================== SIGNAL HANDLERS ====================

    def _hide_messages(self, *args):
        """Hide all messages in this view."""
        self.knot_msg.hide()

    def _on_knots_changed(self, knots: list):
        """Update knot combo box when knots list changes."""
        self.knot_no_combo.blockSignals(True)
        self.hidden_knot_no_combo.blockSignals(True)
        
        self.knot_no_combo.clear()
        self.knot_no_combo.addItems(knots)
        
        self.hidden_knot_no_combo.clear()
        self.hidden_knot_no_combo.addItems(knots)
        
        self.knot_no_combo.blockSignals(False)
        self.hidden_knot_no_combo.blockSignals(False)

    def _on_knot_data_changed(self):
        """Update UI when ViewModel knot data changes."""
        line_edits = [
            self.x_line, self.pith_z_line, self.pith_y_line, self.comment_line,
            self.hidden_x_line, self.hidden_pith_z_line, self.hidden_pith_y_line
        ]
        
        for le in line_edits:
            le.blockSignals(True)
        self.pruned_knot.blockSignals(True)
        self.hidden_pruned_knot.blockSignals(True)

        self.x_line.setText(str(self.view_model.x))
        self.comment_line.setText(self.view_model.comment)
        self.pruned_knot.setChecked(self.view_model.is_pruned_knot)
        self.hidden_x_line.setText(str(self.view_model.x))
        self.hidden_pruned_knot.setChecked(self.view_model.is_pruned_knot)
        
        is_pruned = self.view_model.is_pruned_knot
        if is_pruned:
            self.pith_z_label.setText("Pruned Z")
            self.pith_y_label.setText("Pruned Y")
            self.hidden_pith_z_label.setText("Pruned Z")
            self.hidden_pith_y_label.setText("Pruned Y")
            z_val = self.view_model.pruned_z
            y_val = self.view_model.pruned_y
        else:
            self.pith_z_label.setText("Pith Z")
            self.pith_y_label.setText("Pith Y")
            self.hidden_pith_z_label.setText("Pith Z")
            self.hidden_pith_y_label.setText("Pith Y")
            z_val = self.view_model.pith_z
            y_val = self.view_model.pith_y

        self.pith_z_line.setText("" if z_val is None else str(z_val))
        self.pith_y_line.setText("" if y_val is None else str(y_val))
        self.hidden_pith_z_line.setText("" if z_val is None else str(z_val))
        self.hidden_pith_y_line.setText("" if y_val is None else str(y_val))
        
        if getattr(self, '_last_pruned_state', None) is not None and self._last_pruned_state != is_pruned:
            self._last_pruned_state = is_pruned
            self._trigger_pruned_animation()
        elif getattr(self, '_last_pruned_state', None) is None:
            self._last_pruned_state = is_pruned
        
        for le in line_edits:
            le.blockSignals(False)
        self.pruned_knot.blockSignals(False)
        self.hidden_pruned_knot.blockSignals(False)

    def _on_knot_error(self, error_message: str):
        """Display error message on validation failure."""
        self.knot_msg.setText(error_message)
        self.knot_msg.show()

    def _on_knot_saved(self, message: str):
        """Show success message when knot is saved."""
        self.knot_msg.setText(message)
        self.knot_msg.show()

    def _on_delete_clicked(self):
        """Handle delete button click with confirmation."""
        knot_no = self.view_model.current_knot_no
        if not knot_no:
            return

        reply = QMessageBox.question(
            self.delete_btn.window(), 'Delete Knot',
            f"Are you sure you want to delete knot '{knot_no}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.view_model.handle_delete_knot()

    def _on_current_knot_changed(self, text: str):
        """Sync combo boxes when current knot changes programmatically."""
        self.knot_no_combo.blockSignals(True)
        self.hidden_knot_no_combo.blockSignals(True)
        self.knot_no_combo.setCurrentText(text)
        self.hidden_knot_no_combo.setCurrentText(text)
        self.knot_no_combo.blockSignals(False)
        self.hidden_knot_no_combo.blockSignals(False)
        # Restart any hidden animations so they map correctly to the hidden state.
        self._on_validation_failed([])

    def _trigger_pruned_animation(self):
        """Play a smooth fade-in animation on the fields when toggling pruned knot."""
        from PySide6.QtCore import QVariantAnimation
        from PySide6.QtWidgets import QGraphicsOpacityEffect
        
        self._fade_in_anim = QVariantAnimation()
        self._fade_in_anim.setDuration(400)
        self._fade_in_anim.setStartValue(0.0)
        self._fade_in_anim.setEndValue(1.0)
        
        widgets = [
            self.pith_z_label, self.pith_z_line, self.pith_y_label, self.pith_y_line,
            self.hidden_pith_z_label, self.hidden_pith_z_line, self.hidden_pith_y_label, self.hidden_pith_y_line
        ]
        
        def update_op(val):
            for w in widgets:
                if not w: continue
                eff = w.graphicsEffect()
                if not eff:
                    eff = QGraphicsOpacityEffect(w)
                    w.setGraphicsEffect(eff)
                eff.setOpacity(val)
                
        def remove_effects():
            for w in widgets:
                if not w: continue
                w.setGraphicsEffect(None)
                
        self._fade_in_anim.valueChanged.connect(update_op)
        self._fade_in_anim.finished.connect(remove_effects)
        self._fade_in_anim.start()

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

        if "X" in invalid_fields:
            _flash_label(self.x_label)
            _flash_label(self.hidden_x_label)
            _flash_label(self.knot_msg)
        if "pith_z" in invalid_fields:
            _flash_label(self.pith_z_label)
            _flash_label(self.hidden_pith_z_label)
            _flash_label(self.knot_msg)
        if "pith_y" in invalid_fields:
            _flash_label(self.pith_y_label)
            _flash_label(self.hidden_pith_y_label)
            _flash_label(self.knot_msg)

    def set_knot_editable(self, state: bool):
        """Enable or disable the save/delete/shift buttons based on editing state.
        The knot combo is always non-editable (IDs are auto-assigned)."""
        self.knot_no_combo.blockSignals(True)
        self.hidden_knot_no_combo.blockSignals(True)

        if not state:
            self.knot_no_combo.setCurrentText(self.view_model.current_knot_no)
            self.hidden_knot_no_combo.setCurrentText(self.view_model.current_knot_no)

        self.knot_no_combo.blockSignals(False)
        self.hidden_knot_no_combo.blockSignals(False)

        self.save_btn.setEnabled(state)
        self.delete_btn.setEnabled(not state)

        self.left_shift_btn.setEnabled(not state)
        self.right_shift_btn.setEnabled(not state)
        self.hidden_left_shift_btn.setEnabled(not state)
        self.hidden_right_shift_btn.setEnabled(not state)

