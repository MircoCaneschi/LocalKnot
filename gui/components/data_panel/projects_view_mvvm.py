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
        pass

    def _setup_hidden_layout(self):
        """
        Create and layout all hidden panel UI components.

        This is pure UI construction with NO logic.
        """
        pass

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

        # ViewModel Signals → View update methods
        self.view_model.projects_changed.connect(self._on_projects_changed)
        self.view_model.species_changed.connect(self._on_species_changed)
        self.view_model.project_error.connect(self._on_project_error)
        self.view_model.species_error.connect(self._on_species_error)
        self.view_model.project_saved.connect(self._on_project_saved)
        self.view_model.species_added.connect(self._on_species_added)

    # ==================== SIGNAL HANDLERS (from ViewModel) ====================

    def _on_projects_changed(self, projects: list):
        """
        Slot called when ViewModel emits projects_changed signal.

        Updates combo box with new projects list.

        Args:
            projects: List of project names from ViewModel
        """
        pass

    def _on_species_changed(self, species: list):
        """
        Slot called when ViewModel emits species_changed signal.

        Updates combo box with new species list.

        Args:
            species: List of species names from ViewModel
        """
        pass

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

    def is_project_editable(self) -> bool:
        """Check if project combo is editable."""
        return self.combo_box_projects.isEditable()

    def is_species_editable(self) -> bool:
        """Check if species combo is editable."""
        return self.combo_box_species.isEditable()

