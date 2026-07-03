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
    QWidget, QFileDialog, QInputDialog
)
from PySide6.QtCore import Qt, QObject, QEvent
import os
# pyrefly: ignore [missing-import]
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
        
        # Export and Import components
        self.export_btn = None
        self.export_msg = None
        self.import_btn = None

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
        new_del_layout.setContentsMargins(0, 6, 0, 0)
        
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
        self.project_msg.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.species_msg.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.project_msg.hide()
        self.species_msg.hide()

        # Form layout
        form = QFormLayout()
        form.addRow("Project", project_layout)
        form.addRow("", self.project_msg)
        form.addRow("Species", species_layout)
        form.addRow("", self.species_msg)
        
        # Export / Import Layout
        export_layout = QHBoxLayout()
        self.export_btn = QPushButton("Export Data")
        self.export_btn.setIcon(icons.upload())
        self.export_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.export_msg = QLabel()
        self.export_msg.hide()
        
        self.import_btn = QPushButton("Import Data")
        self.import_btn.setIcon(icons.download())
        self.import_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        export_layout.addWidget(self.export_btn)
        export_layout.addWidget(self.import_btn)
        export_layout.addWidget(self.export_msg)
        export_layout.addStretch()

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(new_del_layout)
        self.main_layout.addLayout(form)
        self.main_layout.addLayout(export_layout)

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
        # Hide messages on interaction (Connect FIRST so it runs before other slots)
        for combo in [self.combo_box_projects, self.hidden_combo_box_projects, 
                      self.combo_box_species, self.hidden_combo_box_species]:
            combo.activated.connect(self._hide_messages)
            if combo.lineEdit():
                combo.lineEdit().textEdited.connect(self._hide_messages)
                
        for btn in [self.new_btn, self.change_name_btn, self.delete_btn, 
                    self.add_species_btn, self.modify_species_btn, self.delete_species_btn,
                    self.right_shift_btn, self.left_shift_btn,
                    self.hidden_right_shift_btn, self.hidden_left_shift_btn,
                    self.export_btn, self.import_btn]:
            btn.clicked.connect(self._hide_messages)

        # Button clicks → ViewModel Slots
        self.new_btn.clicked.connect(self.view_model.handle_new_project)
        self.save_btn.clicked.connect(self.view_model.handle_save_project)
        self.export_btn.clicked.connect(self.view_model.handle_export_project)
        self.import_btn.clicked.connect(self._on_import_clicked)
        
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
        self.view_model.export_error.connect(self._on_export_error)
        self.view_model.export_success.connect(self._on_export_success)
        self.view_model.import_error.connect(self._on_import_error)
        self.view_model.import_success.connect(self._on_export_success)
        
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
        
        self.view_model.current_project_changed.connect(self._on_current_project_changed)

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

    def _hide_messages(self, *args):
        """Hide all messages in this view."""
        self.project_msg.hide()
        self.species_msg.hide()
        self.export_msg.hide()

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
        self._update_shift_buttons_state()

    def _on_hidden_projects_changed(self, projects: list):
        """Intelligently updates hidden combo box without clearing."""
        self.hidden_combo_box_projects.blockSignals(True)
        
        existing_items = [self.hidden_combo_box_projects.itemText(i) for i in range(self.hidden_combo_box_projects.count())]
        
        if existing_items != projects:
            self.hidden_combo_box_projects.clear()
            self.hidden_combo_box_projects.addItems(projects)
            
        self.hidden_combo_box_projects.setCurrentText(self.view_model.current_project)
        self.hidden_combo_box_projects.blockSignals(False)
        self._update_shift_buttons_state()

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

    def _on_export_error(self, error_message: str):
        """
        Slot called when ViewModel emits export_error signal.
        Displays error message to user next to export button.
        """
        self.export_msg.setText(error_message)
        self.export_msg.show()

    def _on_export_success(self, message: str):
        """
        Slot called when ViewModel emits export_success or import_success signal.
        Displays success message to user next to export/import buttons.
        """
        self.export_msg.setText(message)
        self.export_msg.show()

    def _on_import_error(self, error_message: str):
        """
        Slot called when ViewModel emits import_error signal.
        Displays error message in a styled popup.
        """
        from gui.theme_utils import set_custom_titlebar_color
        msg = QMessageBox(self.import_btn.window())
        msg.setWindowTitle("Errore di importazione")
        msg.setText(error_message)
        msg.setIcon(QMessageBox.Icon.Critical)
        set_custom_titlebar_color(msg)
        msg.exec()

    def _on_import_clicked(self):
        """
        Handle import button click: open file dialog, process files, and handle user inputs
        for naming collisions and missing species.
        """
        # Open file dialog
        file_paths, _ = QFileDialog.getOpenFileNames(
            self.import_btn.window(),
            "Import Project Data",
            "",
            "Text/CSV Files (*.txt *.csv);;All Files (*)"
        )

        if not file_paths:
            return  # User cancelled

        for file_path in file_paths:
            if not self.view_model.is_valid_export_file(file_path):
                self._on_import_error("Il file non è valido.")
                continue

            # Extract base name without extension
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            project_name = base_name

            # Handle duplicate project names
            while self.view_model.project_exists(project_name):
                from gui.theme_utils import set_custom_titlebar_color
                dialog = QInputDialog(self.import_btn.window())
                dialog.setWindowTitle("Duplicate Project Name")
                dialog.setLabelText(f"A project named '{project_name}' already exists.\nPlease enter a new name:")
                dialog.setTextValue(project_name + " (1)")
                set_custom_titlebar_color(dialog)
                ok = dialog.exec() == QInputDialog.DialogCode.Accepted
                new_name = dialog.textValue()
                if not ok or not new_name.strip():
                    return # User cancelled the import for this and subsequent files (or we could just continue to the next)
                project_name = new_name.strip()

            # Handle missing species
            species = self.view_model.guess_species(file_path, project_name)
            if not species:
                from gui.theme_utils import set_custom_titlebar_color
                dialog = QInputDialog(self.import_btn.window())
                dialog.setWindowTitle("Unknown Species")
                dialog.setLabelText(f"Cannot determine species for project '{project_name}'.\nPlease enter the species name:")
                dialog.setTextValue("Placeholder")
                set_custom_titlebar_color(dialog)
                ok = dialog.exec() == QInputDialog.DialogCode.Accepted
                species_input = dialog.textValue()
                if not ok or not species_input.strip():
                    return # User cancelled
                species = species_input.strip()

            # Execute import via ViewModel
            self.view_model.execute_import(file_path, project_name, species)

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
        """Update the enabled state of the shift buttons based on editing state and list limits."""
        is_editing = self.combo_box_projects.isEditable() or self.combo_box_species.isEditable()
        
        count = self.combo_box_projects.count()
        current_index = self.combo_box_projects.currentIndex()
        
        prev_enabled = not is_editing and count > 1 and current_index > 0
        next_enabled = not is_editing and count > 1 and current_index < count - 1

        self.right_shift_btn.setEnabled(prev_enabled)
        self.left_shift_btn.setEnabled(next_enabled)
        self.hidden_right_shift_btn.setEnabled(prev_enabled)
        self.hidden_left_shift_btn.setEnabled(next_enabled)

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

    def _on_current_project_changed(self, text: str):
        """Update combo boxes and button states when current project changes."""
        self.combo_box_projects.blockSignals(True)
        self.hidden_combo_box_projects.blockSignals(True)
        self.combo_box_projects.setCurrentText(text)
        self.hidden_combo_box_projects.setCurrentText(text)
        self.combo_box_projects.blockSignals(False)
        self.hidden_combo_box_projects.blockSignals(False)
        self._update_shift_buttons_state()

    def _on_project_selection_changed(self, text: str):
        # Update the ViewModel
        self.view_model.current_project = text
        # read the species and update the UI
        new_species = self.view_model.current_species
        self.combo_box_species.setCurrentText(new_species)
        self._update_shift_buttons_state()

    def _on_delete_clicked(self):
        """Handle delete button click with confirmation."""
        project_name = self.view_model.current_project
        if not project_name:
            return

        from gui.theme_utils import set_custom_titlebar_color
        msg = QMessageBox(self.delete_btn.window())
        msg.setWindowTitle('Delete Project')
        msg.setText(f"Are you sure you want to delete project '{project_name}'?\nThis will also delete all associated boards and knots.")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        msg.setIcon(QMessageBox.Icon.Question)
        set_custom_titlebar_color(msg)
        reply = msg.exec()

        if reply == QMessageBox.StandardButton.Yes:
            self.view_model.handle_delete_project()

    def _on_delete_species_clicked(self):
        """Handle delete species button click with confirmation."""
        species_name = self.view_model.current_species
        if not species_name:
            return

        from gui.theme_utils import set_custom_titlebar_color
        msg = QMessageBox(self.delete_species_btn.window())
        msg.setWindowTitle('Delete Species')
        msg.setText(f"Are you sure you want to delete species '{species_name}'?\nThis will only succeed if the species is not used by any project.")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        msg.setIcon(QMessageBox.Icon.Question)
        set_custom_titlebar_color(msg)
        reply = msg.exec()

        if reply == QMessageBox.StandardButton.Yes:
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
