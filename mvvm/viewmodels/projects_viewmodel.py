"""
View Models for Projects.

ViewModels manage presentation state and expose Qt Properties and Signals
to the View layer. They have ZERO dependencies on QtWidgets.

This module transforms data from Models into presentation-ready state
and handles user interactions via Slots.
"""

from PySide6.QtCore import QObject, Signal, Slot, Property
from typing import List


class ProjectsViewModel(QObject):
    """
    ViewModel for Projects management.

    Exposes:
    - Properties: project_list, species_list, current_project_message, etc.
    - Signals: projectsChanged, speciesChanged, etc.
    - Slots: handleNewProject, handleSaveProject, handleAddSpecies, etc.
    """

    # ==================== SIGNALS ====================
    # Emitted when the projects list changes
    projects_changed = Signal(list)

    # Emitted when the species list changes
    species_changed = Signal(list)

    # Emitted when project validation error occurs
    project_error = Signal(str)

    # Emitted when species validation error occurs
    species_error = Signal(str)

    # Emitted when project is successfully saved
    project_saved = Signal(str)

    # Emitted when species is successfully added
    species_added = Signal(str)

    # ==================== CONSTRUCTOR ====================

    def __init__(self):
        """
        Initialize the ProjectsViewModel.

        Sets up internal state for projects and species management.
        """
        super().__init__()
        pass

    # ==================== PROPERTIES ====================

    @Property(list, notify=projects_changed)
    def project_list(self) -> List[str]:
        """
        Get the current list of projects (read-only property).

        Returns:
            List[str]: List of project names
        """
        pass

    @Property(list, notify=species_changed)
    def species_list(self) -> List[str]:
        """
        Get the current list of species (read-only property).

        Returns:
            List[str]: List of species names
        """
        pass

    @Property(str)
    def current_project(self) -> str:
        """
        Get the currently selected project name.

        Returns:
            str: Current project name or empty string
        """
        pass

    @current_project.setter
    def current_project(self, value: str):
        """
        Set the current project (property setter).

        Args:
            value: Project name to select
        """
        pass

    @Property(str)
    def current_species(self) -> str:
        """
        Get the currently selected species name.

        Returns:
            str: Current species name or empty string
        """
        pass

    @current_species.setter
    def current_species(self, value: str):
        """
        Set the current species (property setter).

        Args:
            value: Species name to select
        """
        pass

    @Property(bool)
    def species_editable(self) -> bool:
        """
        Get whether the species field should be editable.

        Returns:
            bool: True if editable, False otherwise
        """
        pass

    # ==================== SLOTS (User Actions) ====================

    @Slot()
    def handle_new_project(self):
        """
        Slot called when user clicks 'New Project' button.

        Prepares UI for new project creation:
        - Clears input fields
        - Makes project combo editable
        - Hides previous messages
        """
        pass

    @Slot()
    def handle_save_project(self):
        """
        Slot called when user clicks 'Save Project' button.

        Validates and saves the project:
        - Validates project name (not empty, not duplicate)
        - Validates species (selected or new)
        - Emits signals: project_error, species_error, project_saved
        - Clears input fields on success
        """
        pass

    @Slot()
    def handle_add_species(self):
        """
        Slot called when user clicks 'Add Species' button.

        Prepares UI for adding a new species:
        - Makes species combo editable
        - Focuses on species field
        """
        pass

    @Slot(str)
    def handle_delete_project(self, project_name: str):
        """
        Slot called when user clicks 'Delete Project' button.

        Args:
            project_name: Name of project to delete
        """
        pass

    @Slot(str)
    def handle_modify_project(self, project_name: str):
        """
        Slot called when user clicks 'Modify Project' button.

        Args:
            project_name: Name of project to modify
        """
        pass

    # ==================== PRIVATE METHODS ====================

    def _validate_project_name(self, name: str) -> tuple[bool, str]:
        """
        Validate project name according to business rules.

        Args:
            name: Project name to validate

        Returns:
            tuple: (is_valid, error_message)
        """
        pass

    def _validate_species_name(self, name: str, is_new: bool) -> tuple[bool, str]:
        """
        Validate species name according to business rules.

        Args:
            name: Species name to validate
            is_new: Whether this is a new species

        Returns:
            tuple: (is_valid, error_message)
        """
        pass

    def _clear_inputs(self):
        """Reset all input fields to empty state."""
        pass

