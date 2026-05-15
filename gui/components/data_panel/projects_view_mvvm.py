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
    QSizePolicy, QSpacerItem, QFormLayout
)
from PySide6.QtCore import Qt

from gui.components.common_widgets import create_shift_buttons
from mvvm.viewmodels import ProjectsViewModel


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
        self.add_species_btn = None

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

        # Setup UI
        self._setup_main_layout()
        self._setup_hidden_layout()

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
        self.combo_box_species.setEditable(False)
        self.add_species_btn = QPushButton("+")
        self.add_species_btn.setMaximumWidth(30)
        self.add_species_btn.setMinimumWidth(30)
        self.combo_box_species.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        species_layout.addWidget(self.combo_box_species)
        species_layout.addWidget(self.add_species_btn)
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
        self.add_species_btn.clicked.connect(self.view_model.handle_add_species)
        self.change_name_btn.clicked.connect(self.view_model.handle_modify_project)
        
        # Focus handling
        self.new_btn.clicked.connect(lambda: self.combo_box_projects.setFocus())
        self.add_species_btn.clicked.connect(lambda: self.combo_box_species.setFocus())
        self.change_name_btn.clicked.connect(lambda: self.combo_box_projects.setFocus())

        # Combo boxes text changes → Update ViewModel properties (Main and Hidden)
        for combo in [self.combo_box_projects, self.hidden_combo_box_projects]:
            combo.currentTextChanged.connect(
                lambda text: setattr(self.view_model, 'current_project', text)
            )
        
        for combo in [self.combo_box_species, self.hidden_combo_box_species]:
            combo.currentTextChanged.connect(
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
        self.view_model.species_error.connect(self._on_species_error)
        self.view_model.species_added.connect(self._on_species_added)
        
        # Sync Current Text (Main and Hidden)
        self.view_model.current_species_changed.connect(self.combo_box_species.setCurrentText)
        self.view_model.current_species_changed.connect(self.hidden_combo_box_species.setCurrentText)
        
        self.view_model.current_project_changed.connect(self.combo_box_projects.setCurrentText)
        self.view_model.current_project_changed.connect(self.hidden_combo_box_projects.setCurrentText)

        # Force initial UI update from ViewModel state
        self._on_projects_changed(self.view_model.project_list)
        self._on_hidden_projects_changed(self.view_model.project_list)
        self._on_species_changed(self.view_model.species_list)
        self._on_hidden_species_changed(self.view_model.species_list)
        
        # Initial UI constraints
        self.set_species_enabled(False)

    # ==================== SIGNAL HANDLERS (from ViewModel) ====================

    def _on_projects_changed(self, projects: list):
        """Updates main combo box with new projects list."""
        current = self.view_model.current_project
        self.combo_box_projects.blockSignals(True)
        self.combo_box_projects.clear()
        self.combo_box_projects.addItems(projects)
        self.combo_box_projects.setCurrentText(current)
        self.combo_box_projects.blockSignals(False)

    def _on_hidden_projects_changed(self, projects: list):
        """Updates hidden combo box with new projects list."""
        current = self.view_model.current_project
        self.hidden_combo_box_projects.blockSignals(True)
        self.hidden_combo_box_projects.clear()
        self.hidden_combo_box_projects.addItems(projects)
        self.hidden_combo_box_projects.setCurrentText(current)
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
        self.hidden_combo_box_projects.setEditable(state)
        self.combo_box_projects.setEditable(state)

    def set_species_editable(self, state: bool):
        """Check if species combo is editable."""
        self.hidden_combo_box_species.setEditable(state)
        self.combo_box_species.setEditable(state)

    def set_species_enabled(self, state: bool):
        """Enable or disable the species combo box and add button."""
        self.combo_box_species.setEnabled(state)
        self.hidden_combo_box_species.setEnabled(state)
        self.add_species_btn.setEnabled(state)

    def _on_project_selection_changed(self, text: str):
        # Update the ViewModel
        self.view_model.current_project = text
        # read the species and update the UI
        nuova_specie = self.view_model.current_species
        self.combo_box_species.setCurrentText(nuova_specie)
