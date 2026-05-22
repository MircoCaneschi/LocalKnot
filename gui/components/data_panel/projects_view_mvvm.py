"""
Refactored Projects View - MVVM Pattern.

This View layer receives a ProjectsViewModel and binds UI widgets
to its Properties and Signals. The View has NO business logic,
only UI presentation and event propagation.

Data Flow:
- User clicks button → emit signal from View
- Button signal connects to ViewModel Slot
- ViewModel Slot processes logic, modifies Properties
- ViewModel emits Signals
- View listens to Signals and updates UI
"""

from PySide6.QtWidgets import (
    QHBoxLayout, QPushButton, QLabel, QComboBox, QVBoxLayout,
    QSizePolicy, QSpacerItem, QFormLayout, QMessageBox, QStyle, QLineEdit,
    QWidget
)
from PySide6.QtCore import Qt, QObject, QEvent
from pyside6helpers import icons

from gui.components.common_widgets import create_shift_buttons
from mvvm.viewmodels import ProjectsViewModel


class SpeciesInteractionFilter(QObject):
    """Filters events to prevent opening the combo box while keeping it visually enabled."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_enabled = False
        self.is_editing_inline = False

    def eventFilter(self, obj, event):
        # 1. In-Line Editing Mode: Allow typing, block dropdown popup
        if self.is_editing_inline:
            if event.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonRelease, QEvent.MouseButtonDblClick]:
                if isinstance(obj, QComboBox) and obj.isEditable():
                    # Allow clicks ONLY if they are inside the lineEdit area (for cursor/focus)
                    if obj.lineEdit().geometry().contains(event.pos()):
                        return False
                # Block clicks on the arrow/button area
                return True
            
            if event.type() == QEvent.KeyPress:
                # Block keys that navigate or open the popup
                if event.key() in [Qt.Key_Up, Qt.Key_Down, Qt.Key_F4]:
                    return True
                # Allow all other keys (character input, backspace, enter, etc.)
                return False
            return False

        # 2. Locked Mode (Navigation): Block all interactions
        if not self.is_enabled:
            if event.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonRelease, 
                               QEvent.MouseButtonDblClick, QEvent.KeyPress]:
                return True
        
        # 3. Enabled Mode: Normal behavior
        return super().eventFilter(obj, event)


class ProjectsView:
    """
    Projects View Component (MVVM).

    Responsibilities:
    - Create UI widgets (buttons, combo boxes, labels)
    - Bind widgets to ViewModel Properties
    - Connect widget signals to ViewModel Slots
    - Update UI when ViewModel Signals are emitted
    - NO direct business logic
    """

    def __init__(self, view_model: ProjectsViewModel):
        """
        Initialize the Projects View with a ViewModel.

        Args:
            view_model: ProjectsViewModel instance to bind to
        """
        self.view_model = view_model

        # UI Components (initialized in setup methods)
        self.main_layout = None
        self.hidden_main_layout = None

        # Action buttons
        self.new_btn = None
        self.delete_btn = None
        self.change_name_btn = None
        self.save_btn = None

        # Combo boxes
        self.combo_box_projects = None
        self.combo_box_species = None
        self.species_line_edit = None
        self.add_species_btn = None
        self.modify_species_btn = None
        self.delete_species_btn = None
        self.save_species_btn = None
        self.cancel_species_btn = None
        self.species_btns_container = None
        self.species_edit_btns_container = None

        # Navigation buttons
        self.right_shift_btn = None
        self.left_shift_btn = None

        # Message labels
        self.project_msg = None
        self.species_msg = None

        # Hidden panel components
        self.hidden_combo_box_projects = None
        self.hidden_combo_box_species = None
        self.hidden_right_shift_btn = None
        self.hidden_left_shift_btn = None
        
        # State tracking
        self._species_menu_open = False

        # Setup UI
        self._setup_main_layout()
        self._setup_hidden_layout()

        # Event Filters for Species ComboBoxes (to keep them sharp when disabled)
        self.species_filter = SpeciesInteractionFilter()
        self.hidden_species_filter = SpeciesInteractionFilter()
        self.combo_box_species.installEventFilter(self.species_filter)
        self.hidden_combo_box_species.installEventFilter(self.hidden_species_filter)

        # Bind ViewModel
        self._bind_to_view_model()

    # ==================== SETUP UI ====================

    def _setup_main_layout(self):
        """
        Create and layout all main panel UI components.

        This is pure UI construction with NO logic.
        """
        new_del_layout = QHBoxLayout()
        self.new_btn = QPushButton("New+")
        self.delete_btn = QPushButton("Del-")
        self.change_name_btn = QPushButton("Modify")
        self.save_btn = QPushButton("Save")

        # Set sizes
        for btn in [self.new_btn, self.delete_btn, self.change_name_btn, self.save_btn]:
            btn.setMinimumWidth(50)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        new_del_layout.addWidget(self.new_btn, 1)
        new_del_layout.addWidget(self.delete_btn, 1)
        new_del_layout.addWidget(self.change_name_btn, 1)
        new_del_layout.addWidget(self.save_btn, 1)
        new_del_layout.setSpacing(2)
        spacer_nd = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        new_del_layout.addItem(spacer_nd)

        # Project combo
        project_layout = QHBoxLayout()
        self.combo_box_projects = QComboBox()
        self.combo_box_projects.setEditable(False)
        self.combo_box_projects.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        project_layout.addWidget(self.combo_box_projects)

        self.right_shift_btn, self.left_shift_btn = create_shift_buttons()
        project_layout.addWidget(self.right_shift_btn)
        project_layout.addWidget(self.left_shift_btn)
        project_layout.setSpacing(2)

        # Species combo
        species_layout = QHBoxLayout()
        self.combo_box_species = QComboBox()
        self.combo_box_species.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Connect returnPressed of the internal lineEdit to save action
        self.combo_box_species.setEditable(True)
        self.combo_box_species.lineEdit().returnPressed.connect(self.view_model.handle_save_species_edit)
        self.combo_box_species.setEditable(False)
        
        # Toggle button for species actions (Normal Mode)
        self.toggle_species_btns_btn = QPushButton()
        self.toggle_species_btns_btn.setMaximumWidth(20)
        self.toggle_species_btns_btn.setMinimumWidth(20)
        self.toggle_species_btns_btn.setIcon(icons.menu())

        # Species buttons container (Normal Mode)
        self.species_btns_container = QWidget()
        self.species_btns_container.hide()
        species_btns_layout = QHBoxLayout(self.species_btns_container)
        species_btns_layout.setContentsMargins(0, 0, 0, 0)
        species_btns_layout.setSpacing(2)
        
        self.add_species_btn = QPushButton()
        self.modify_species_btn = QPushButton()
        self.delete_species_btn = QPushButton()
        
        self.add_species_btn.setIcon(icons.plus())
        self.modify_species_btn.setIcon(icons.pencil())
        self.delete_species_btn.setIcon(icons.trash())
        
        for btn in [self.add_species_btn, self.modify_species_btn, self.delete_species_btn]:
            btn.setMaximumWidth(30)
            btn.setMinimumWidth(30)
            species_btns_layout.addWidget(btn)

        # Species edit buttons container (In-Line Mode)
        self.species_edit_btns_container = QWidget()
        self.species_edit_btns_container.hide()
        species_edit_btns_layout = QHBoxLayout(self.species_edit_btns_container)
        species_edit_btns_layout.setContentsMargins(0, 0, 0, 0)
        species_edit_btns_layout.setSpacing(2)

        self.save_species_btn = QPushButton()
        self.cancel_species_btn = QPushButton()
        
        self.save_species_btn.setIcon(icons.check())
        self.cancel_species_btn.setIcon(icons.cancel())
        
        self.save_species_btn.setStyleSheet("QPushButton { color: green; }")
        self.cancel_species_btn.setStyleSheet("QPushButton { color: red; }")

        for btn in [self.save_species_btn, self.cancel_species_btn]:
            btn.setMaximumWidth(30)
            btn.setMinimumWidth(30)
            species_edit_btns_layout.addWidget(btn)
        
        species_layout.addWidget(self.combo_box_species)
        species_layout.addWidget(self.toggle_species_btns_btn)
        species_layout.addWidget(self.species_btns_container)
        species_layout.addWidget(self.species_edit_btns_container)
        species_layout.setSpacing(2)

        # Messages
        self.project_msg = QLabel()
        self.species_msg = QLabel()
        self.project_msg.hide()
        self.species_msg.hide()

        # Form layout
        form = QFormLayout()
        form.addRow("Project", project_layout)
        form.addRow("", self.project_msg)
        form.addRow("Species", species_layout)
        form.addRow("", self.species_msg)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(new_del_layout)
        self.main_layout.addLayout(form)

    def _setup_hidden_layout(self):
        """
        Create and layout all hidden panel UI components.

        This is pure UI construction with NO logic.
        """
        hidden_project_layout = QHBoxLayout()
        hidden_project_no_label = QLabel("Project")
        self.hidden_combo_box_projects = QComboBox()
        self.hidden_combo_box_projects.setEditable(False)
        hidden_project_no_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.hidden_combo_box_projects.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        hidden_project_layout.addWidget(hidden_project_no_label)
        hidden_project_layout.addWidget(self.hidden_combo_box_projects)

        self.hidden_right_shift_btn, self.hidden_left_shift_btn = create_shift_buttons()
        hidden_project_layout.addWidget(self.hidden_right_shift_btn)
        hidden_project_layout.addWidget(self.hidden_left_shift_btn)
        hidden_project_layout.setSpacing(2)

        hidden_species_layout = QHBoxLayout()
        hidden_label_species = QLabel("Species")
        hidden_label_species.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.hidden_combo_box_species = QComboBox()
        self.hidden_combo_box_species.setEditable(False)
        self.hidden_combo_box_species.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        hidden_species_layout.addWidget(hidden_label_species)
        hidden_species_layout.addWidget(self.hidden_combo_box_species)
        hidden_species_layout.setSpacing(2)

        self.hidden_main_layout = QVBoxLayout()
        self.hidden_main_layout.addLayout(hidden_project_layout)
        self.hidden_main_layout.addLayout(hidden_species_layout)

    # ==================== BINDING ====================

    def _bind_to_view_model(self):
        """
        Establish all connections between View and ViewModel.

        Connects:
        - Widget signals → ViewModel Slots (for user actions)
        - ViewModel Signals → View methods (for state changes)
        """
        # Button clicks → ViewModel Slots
        self.new_btn.clicked.connect(self.view_model.handle_new_project)
        self.save_btn.clicked.connect(self.view_model.handle_save_project)
        
        # Species management clicks
        self.add_species_btn.clicked.connect(self.view_model.handle_add_species)
        self.modify_species_btn.clicked.connect(self.view_model.handle_modify_species)
        self.delete_species_btn.clicked.connect(self._on_delete_species_clicked)
        self.save_species_btn.clicked.connect(self.view_model.handle_save_species_edit)
        self.cancel_species_btn.clicked.connect(self.view_model.handle_cancel_species_edit)
        self.toggle_species_btns_btn.clicked.connect(self._toggle_species_btns)

        self.change_name_btn.clicked.connect(self.view_model.handle_modify_project)
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        
        # Shift buttons
        self.right_shift_btn.clicked.connect(self.view_model.handle_previous_project)
        self.left_shift_btn.clicked.connect(self.view_model.handle_next_project)
        self.hidden_right_shift_btn.clicked.connect(self.view_model.handle_previous_project)
        self.hidden_left_shift_btn.clicked.connect(self.view_model.handle_next_project)
        
        # Focus handling
        self.new_btn.clicked.connect(lambda: self.combo_box_projects.setFocus())
        self.add_species_btn.clicked.connect(lambda: self.combo_box_species.setFocus())
        self.modify_species_btn.clicked.connect(lambda: self.combo_box_species.setFocus())
        self.change_name_btn.clicked.connect(lambda: self.combo_box_projects.setFocus())

        # Combo boxes text changes → Update ViewModel properties (Main and Hidden)
        for combo in [self.combo_box_projects, self.hidden_combo_box_projects]:
            combo.currentTextChanged.connect(
                lambda text: setattr(self.view_model, 'current_project', text)
            )
        
        self.combo_box_species.currentTextChanged.connect(self._on_species_combo_text_changed)
        self.hidden_combo_box_species.currentTextChanged.connect(
            lambda text: setattr(self.view_model, 'current_species', text)
        )

        # ViewModel Signals → View update methods
        self.view_model.hide_messages.connect(lambda: (self.project_msg.hide(), self.species_msg.hide()))
        
        # Sync Project List (Main and Hidden)
        self.view_model.projects_changed.connect(self._on_projects_changed)
        self.view_model.projects_changed.connect(self._on_hidden_projects_changed)
        
        self.view_model.project_editable_changed.connect(self.set_project_editable)
        self.view_model.project_modify_mode.connect(self._on_project_modify_mode)
        self.view_model.project_error.connect(self._on_project_error)
        self.view_model.project_saved.connect(self._on_project_saved)
        
        # Sync Species List (Main and Hidden)
        self.view_model.species_changed.connect(self._on_species_changed)
        self.view_model.species_changed.connect(self._on_hidden_species_changed)
        
        self.view_model.species_editable_changed.connect(self.set_species_editable)
        self.view_model.species_enabled_changed.connect(self.set_species_enabled)
        self.view_model.save_enabled_changed.connect(self.save_btn.setEnabled)
        self.view_model.navigation_enabled_changed.connect(self._on_navigation_enabled_changed)
        self.view_model.species_error.connect(self._on_species_error)
        self.view_model.species_added.connect(self._on_species_added)
        
        # Species Mode and Action States
        self.view_model.species_normal_mode_changed.connect(self._on_species_mode_changed)
        
        # Granular Species Actions Binding
        self.view_model.species_add_enabled.connect(self.add_species_btn.setEnabled)
        self.view_model.species_modify_enabled.connect(self.modify_species_btn.setEnabled)
        self.view_model.species_delete_enabled.connect(self.delete_species_btn.setEnabled)
        
        # Sync Current Text (Main and Hidden)
        self.view_model.current_species_changed.connect(self._on_current_species_changed)
        
        self.view_model.current_project_changed.connect(self.combo_box_projects.setCurrentText)
        self.view_model.current_project_changed.connect(self.hidden_combo_box_projects.setCurrentText)

        # Force initial UI update from ViewModel state
        self._on_projects_changed(self.view_model.project_list)
        self._on_hidden_projects_changed(self.view_model.project_list)
        self._on_species_changed(self.view_model.species_list)
        self._on_hidden_species_changed(self.view_model.species_list)
        
        # Sync initial selection
        self.combo_box_projects.setCurrentText(self.view_model.current_project)
        self.hidden_combo_box_projects.setCurrentText(self.view_model.current_project)
        self.combo_box_species.setCurrentText(self.view_model.current_species)
        self.hidden_combo_box_species.setCurrentText(self.view_model.current_species)
        
        # Initial UI constraints
        self.save_btn.setEnabled(False)
        self._on_species_mode_changed(True)
        # Force initial interaction state (should be disabled by default as per requirement)
        is_project_editable = self.view_model.project_editable if hasattr(self.view_model, 'project_editable') else self.view_model._project_editable
        has_species = bool(self.view_model.current_species)
        
        self.set_species_enabled(is_project_editable) 
        self.add_species_btn.setEnabled(is_project_editable)
        self.modify_species_btn.setEnabled(has_species)
        self.delete_species_btn.setEnabled(is_project_editable and has_species)
        self._update_shift_buttons_state()

    # ==================== SIGNAL HANDLERS (from ViewModel) ====================

    def _on_projects_changed(self, projects: list):
        """Intelligently updates main combo box without clearing if possible."""
        self.combo_box_projects.blockSignals(True)
        
        # Get current items
        existing_items = [self.combo_box_projects.itemText(i) for i in range(self.combo_box_projects.count())]
        
        if existing_items != projects:
            self.combo_box_projects.clear()
            self.combo_box_projects.addItems(projects)
        
        # Always sync with current selection from ViewModel
        self.combo_box_projects.setCurrentText(self.view_model.current_project)
        self.combo_box_projects.blockSignals(False)

    def _on_hidden_projects_changed(self, projects: list):
        """Intelligently updates hidden combo box without clearing."""
        self.hidden_combo_box_projects.blockSignals(True)
        
        existing_items = [self.hidden_combo_box_projects.itemText(i) for i in range(self.hidden_combo_box_projects.count())]
        
        if existing_items != projects:
            self.hidden_combo_box_projects.clear()
            self.hidden_combo_box_projects.addItems(projects)
            
        self.hidden_combo_box_projects.setCurrentText(self.view_model.current_project)
        self.hidden_combo_box_projects.blockSignals(False)

    def _on_species_changed(self, species: list):
        """Updates main combo box with new species list."""
        current = self.view_model.current_species
        self.combo_box_species.blockSignals(True)
        self.combo_box_species.clear()
        self.combo_box_species.addItems(species)
        self.combo_box_species.setCurrentText(current)
        self.combo_box_species.blockSignals(False)

    def _on_hidden_species_changed(self, species: list):
        """Updates hidden combo box with new species list."""
        current = self.view_model.current_species
        self.hidden_combo_box_species.blockSignals(True)
        self.hidden_combo_box_species.clear()
        self.hidden_combo_box_species.addItems(species)
        self.hidden_combo_box_species.setCurrentText(current)
        self.hidden_combo_box_species.blockSignals(False)

    def _on_project_modify_mode(self, is_modifying: bool):
        """Handle UI restrictions when modifying a project."""
        if is_modifying:
            for combo in [self.combo_box_projects, self.hidden_combo_box_projects]:
                text = combo.currentText()
                combo.blockSignals(True)
                combo.clear()
                combo.addItem(text)
                combo.blockSignals(False)

    def _on_project_error(self, error_message: str):
        """
        Slot called when ViewModel emits project_error signal.

        Displays error message to user.

        Args:
            error_message: Error message from ViewModel
        """
        self.project_msg.setText(error_message)
        self.project_msg.show()

    def _on_species_error(self, error_message: str):
        """
        Slot called when ViewModel emits species_error signal.

        Args:
            error_message: Error message from ViewModel
        """
        self.species_msg.setText(error_message)
        self.species_msg.show()

    def _on_project_saved(self, project_name: str):
        """
        Slot called when ViewModel emits project_saved signal.

        Displays success message and clears inputs.

        Args:
            project_name: Name of saved project
        """
        self.project_msg.setText(f"{project_name} registered!")
        self.project_msg.show()

    def _on_species_added(self, species_name: str):
        """
        Slot called when ViewModel emits species_added signal.

        Args:
            species_name: Name of added species
        """
        self.species_msg.setText(f"{species_name} registered!")
        self.species_msg.show()

    # ==================== PROPERTY BINDING (read from ViewModel) ====================

    def get_current_project(self) -> str:
        """
        Read project name from ViewModel Property.

        Returns:
            str: Current project from ViewModel
        """
        return self.view_model.current_project

    def get_current_species(self) -> str:
        """
        Read species name from ViewModel Property.

        Returns:
            str: Current species from ViewModel
        """
        return self.view_model.current_species

    def set_project_editable(self, state: bool):
        """Check if project combo is editable."""
        self.combo_box_projects.blockSignals(True)
        self.hidden_combo_box_projects.blockSignals(True)
        
        self.hidden_combo_box_projects.setEditable(state)
        self.combo_box_projects.setEditable(state)
        
        # When returning to non-editable, Qt resets the index. Force it back.
        if not state:
            self.combo_box_projects.setCurrentText(self.view_model.current_project)
            self.hidden_combo_box_projects.setCurrentText(self.view_model.current_project)
            
        self.combo_box_projects.blockSignals(False)
        self.hidden_combo_box_projects.blockSignals(False)
        self._update_shift_buttons_state()

    def set_species_editable(self, state: bool):
        """Check if species combo is editable."""
        self.combo_box_species.blockSignals(True)
        self.hidden_combo_box_species.blockSignals(True)
        
        self.hidden_combo_box_species.setEditable(state)
        self.combo_box_species.setEditable(state)
        
        # When returning to non-editable, Qt resets the index. Force it back.
        if not state:
            self.combo_box_species.setCurrentText(self.view_model.current_species)
            self.hidden_combo_box_species.setCurrentText(self.view_model.current_species)
            
        self.combo_box_species.blockSignals(False)
        self.hidden_combo_box_species.blockSignals(False)
        self._update_shift_buttons_state()

    def _update_shift_buttons_state(self):
        """Update the enabled state of the shift buttons based on editing state."""
        is_editing = self.combo_box_projects.isEditable() or self.combo_box_species.isEditable()
        self.right_shift_btn.setEnabled(not is_editing)
        self.left_shift_btn.setEnabled(not is_editing)
        self.hidden_right_shift_btn.setEnabled(not is_editing)
        self.hidden_left_shift_btn.setEnabled(not is_editing)

    def set_species_enabled(self, state: bool):
        """
        Enable or disable the species selection interaction.
        Instead of setEnabled(False) which fades the widget, we use an event filter
        to block interaction while keeping the visual state sharp.
        """
        self.species_filter.is_enabled = state
        self.hidden_species_filter.is_enabled = state

    def _on_navigation_enabled_changed(self, enabled: bool):
        """Enable or disable navigation buttons (New, Modify, Delete)."""
        self.new_btn.setEnabled(enabled)
        self.change_name_btn.setEnabled(enabled)
        self.delete_btn.setEnabled(enabled)

    def _on_project_selection_changed(self, text: str):
        # Update the ViewModel
        self.view_model.current_project = text
        # read the species and update the UI
        nuova_specie = self.view_model.current_species
        self.combo_box_species.setCurrentText(nuova_specie)

    def _on_delete_clicked(self):
        """Handle delete button click with confirmation."""
        project_name = self.view_model.current_project
        if not project_name:
            return

        reply = QMessageBox.question(
            self.delete_btn.window(), 'Delete Project',
            f"Are you sure you want to delete project '{project_name}'?\n"
            "This will also delete all associated boards and knots.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.view_model.handle_delete_project()

    def _on_delete_species_clicked(self):
        """Handle delete species button click with confirmation."""
        species_name = self.view_model.current_species
        if not species_name:
            return

        reply = QMessageBox.question(
            self.delete_species_btn.window(), 'Delete Species',
            f"Are you sure you want to delete species '{species_name}'?\n"
            "This will only succeed if the species is not used by any project.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.view_model.handle_delete_species()

    def _on_current_species_changed(self, text: str):
        """Update species combo boxes. If text is empty, clear selection."""
        if not text:
            self.combo_box_species.setCurrentIndex(-1)
            self.hidden_combo_box_species.setCurrentIndex(-1)
        else:
            self.combo_box_species.setCurrentText(text)
            self.hidden_combo_box_species.setCurrentText(text)

    def _toggle_species_btns(self):
        """Toggle the visibility of species action buttons."""
        is_visible = self.species_btns_container.isVisible()
        self.species_btns_container.setVisible(not is_visible)

    def _on_species_mode_changed(self, is_normal: bool):
        """Switch UI between Normal and In-Line modes."""
        self.toggle_species_btns_btn.setVisible(is_normal)
        self.species_btns_container.setVisible(False) # Always start hidden in normal mode
        self.species_edit_btns_container.setVisible(not is_normal)
        
        # In In-Line mode, the combo box becomes editable but stays visible
        self.combo_box_species.setEditable(not is_normal)
        
        # Update filter flags
        self.species_filter.is_editing_inline = not is_normal
        self.hidden_species_filter.is_editing_inline = not is_normal
        
        if not is_normal:
            # Focus and select text for immediate typing
            self.combo_box_species.setFocus()
            if self.combo_box_species.lineEdit():
                self.combo_box_species.lineEdit().selectAll()
        else:
            # Revert to project-based interaction state when returning to normal mode
            self.set_species_enabled(self.view_model._project_editable)

    def _on_species_combo_text_changed(self, text: str):
        """Update ViewModel when combo box selection changes."""
        self.view_model.current_species = text
