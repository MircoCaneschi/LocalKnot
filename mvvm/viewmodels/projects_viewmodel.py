"""
View Model for Projects management.

Manages presentation state and handles user interactions.
"""

from PySide6.QtCore import QObject, Signal, Slot, Property
from typing import List
from core.repository import ProjectRepository
from mvvm.models import Project


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

    # Emitted when project editability changes
    project_editable_changed = Signal(bool)

    # Emitted when species editability changes
    species_editable_changed = Signal(bool)

    # Emitted every time I click save project. Overridden if an actual error is sent
    hide_messages = Signal(bool)

    # Emitted when project validation error occurs
    project_error = Signal(str)

    # Emitted when species validation error occurs
    species_error = Signal(str)

    # Emitted when project is successfully saved
    project_saved = Signal(str)

    # Emitted when species is successfully added
    species_added = Signal(str)

    # Emitted when current species changes
    current_species_changed = Signal(str)

    # Emitted when current project changes
    current_project_changed = Signal(str)

    # Emitted when entering or leaving project modification mode
    project_modify_mode = Signal(bool)

    # Emitted to enable or disable the species combo box
    species_enabled_changed = Signal(bool)

    # ==================== CONSTRUCTOR ====================

    def __init__(self, repository: ProjectRepository):
        """
        Initialize the ProjectsViewModel.

        Sets up internal state for projects and species management.
        """
        super().__init__()
        self.repo = repository

        # Internal state
        self._projects = []
        self._species = []
        self._current_project = ""
        self._current_species = ""
        self._species_editable = False
        self._project_editable = False
        
        self._is_modifying = False
        self._original_project_name = ""

        # Load initial data
        self._load_projects_from_db()
        self._load_species_from_db()

    # ==================== PROPERTIES ====================

    @Property(list, notify=projects_changed)
    def project_list(self) -> List[str]:
        """
        Get the current list of projects (read-only property).

        Returns:
            List[str]: List of project names
        """
        return [p.name for p in self._projects]

    @Property(list, notify=species_changed)
    def species_list(self) -> List[str]:
        """
        Get the current list of species (read-only property).

        Returns:
            List[str]: List of species names
        """
        return self._species

    @Property(str)
    def current_project(self) -> str:
        """Get the currently selected project name."""
        return self._current_project

    @current_project.setter
    def current_project(self, value: str):
        """Set the current project (property setter)."""
        if self._current_project != value:
            self._current_project = value

            #changing the species associated with the project
            matching_project = next((p for p in self._projects if p.name == value), None)

            if matching_project:
                self._current_species = matching_project.species
                self.current_species_changed.emit(self._current_species)

    @Property(str, notify=current_species_changed)
    def current_species(self) -> str:
        """Get the currently selected species name."""
        return self._current_species

    @current_species.setter
    def current_species(self, value: str):
        """Set the current species (property setter)."""
        if self._current_species != value:
            self._current_species = value
            self.current_species_changed.emit(value)

    @Property(bool)
    def species_editable(self) -> bool:
        """Get whether the species field should be editable."""
        return self._species_editable

    # ==================== SLOTS (User Actions) ====================

    @Slot()
    def handle_new_project(self):
        print("handling new project")
        """
        Slot called when user clicks 'New Project' button.

        Prepares UI for new project creation:
        - Clears input fields
        - Makes project combo editable
        - Hides previous messages
        """
        self._is_modifying = False
        self.project_modify_mode.emit(False)

        # 1. Make editable FIRST so the UI accepts custom/empty text
        self._project_editable = True
        self.project_editable_changed.emit(self._project_editable)

        # Enable species selection
        self.species_enabled_changed.emit(True)

        # 2. Set internal state and emit changes to clear UI
        self._current_project = ""
        self.current_project_changed.emit("")

        self._current_species = ""
        self.current_species_changed.emit("")

    @Slot()
    def handle_save_project(self):
        print("handling save project")
        """
        Slot called when user clicks 'Save Project' button.
        """
        project_text = self._current_project.strip()
        species_text = self._current_species.strip()

        self.hide_messages.emit(True)

        # Validate project name
        if not project_text:
            self.project_error.emit("Project name cannot be empty!")
            return
            
        # Check duplicate name
        if self._is_modifying:
            if project_text != self._original_project_name and any(p.name == project_text for p in self._projects):
                self.project_error.emit("Project name already exists!")
                return
        else:
            if any(p.name == project_text for p in self._projects):
                self.project_error.emit("Project already exists!")
                return
                
        # Validate species
        if not species_text:
            self.species_error.emit("Species cannot be empty!")
            return

        if not self._species_editable and species_text not in self._species:
            self.species_error.emit("Please select a valid species!")
            return

        try:
            # Create and save project
            project = Project(name=project_text, species=species_text)
            
            if self._is_modifying:
                if self.repo.update_project(self._original_project_name, project):
                    for p in self._projects:
                        if p.name == self._original_project_name:
                            p.name = project.name
                            p.species = project.species
                            break
                    self.project_saved.emit("Project modified successfully!")
            else:
                if self.repo.add_project(project):
                    self._projects.append(project)
                    self.project_saved.emit(f"{project_text} registered!")

            # Add species if it's new
            if species_text not in self._species:
                self._species.append(species_text)
                self._species.sort()
                self.species_changed.emit(self._species)
                self.species_added.emit(f"{species_text} registered!")

            # Emit signals
            self.projects_changed.emit(self.project_list)

            # Reset state
            self._is_modifying = False
            self.project_modify_mode.emit(False)
            
            self._project_editable = False
            self._species_editable = False
            self.project_editable_changed.emit(False)
            self.species_editable_changed.emit(False)
            
            self.species_enabled_changed.emit(False)
            
            # Re-select the saved project
            self.current_project = project.name

        except Exception as e:
            self.project_error.emit(f"Failed to save project: {str(e)}")

    @Slot()
    def handle_add_species(self):
        """
        Slot called when user clicks 'Add Species' button.

        Prepares UI for adding a new species:
        - Makes species combo editable
        - Focuses on species field
        """
        # 1. Make editable FIRST
        self._species_editable = True
        self.species_editable_changed.emit(self._species_editable)
        
        # 2. Clear text
        self._current_species = ""
        self.current_species_changed.emit("")

    @Slot(str)
    def handle_delete_project(self, project_name: str):
        """
        Slot called when user clicks 'Delete Project' button.

        Args:
            project_name: Name of project to delete
        """
        try:
            if self.repo.delete_project(project_name):
                self._projects = [p for p in self._projects if p.name != project_name]
                self.projects_changed.emit(self.project_list)
        except Exception as e:
            self.project_error.emit(f"Failed to delete project: {str(e)}")

    @Slot()
    def handle_modify_project(self):
        """
        Slot called when user clicks 'Modify Project' button.
        """
        if not self._current_project:
            self.project_error.emit("Please select a project to modify.")
            return

        self._is_modifying = True
        self._original_project_name = self._current_project

        # Trigger modify mode in view to restrict combo box dropdown
        self.project_modify_mode.emit(True)

        self._project_editable = True
        self.project_editable_changed.emit(True)

        self.species_enabled_changed.emit(True)

    # ==================== PRIVATE METHODS ====================

    def _load_projects_from_db(self):
        """Load projects from database."""
        try:
            self._projects = self.repo.get_all_projects()
            print(f"DEBUG: Loaded {len(self._projects)} projects from DB")
            for p in self._projects:
                print(f"DEBUG: Project: {p.name} ({p.species})")
            self.projects_changed.emit(self.project_list)
        except Exception as e:
            print(f"DEBUG: Failed to load projects: {str(e)}")
            self.project_error.emit(f"Failed to load projects: {str(e)}")

    def _load_species_from_db(self):
        """Load species from all projects in database."""
        try:
            species_set = set()
            for project in self._projects:
                if project.species:
                    species_set.add(project.species)
            self._species = sorted(list(species_set))
            self.species_changed.emit(self._species)
        except Exception as e:
            self.species_error.emit(f"Failed to load species: {str(e)}")
