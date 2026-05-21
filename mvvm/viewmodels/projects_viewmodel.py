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

    # Emitted when a species is updated (old_name, new_name)
    species_updated = Signal(str, str)

    # Emitted when current project changes
    current_project_changed = Signal(str)

    # Emitted when entering or leaving project modification mode
    project_modify_mode = Signal(bool)

    # Emitted to enable or disable the species combo box (interaction)
    species_enabled_changed = Signal(bool)

    # Emitted to enable or disable the save button
    save_enabled_changed = Signal(bool)

    # Emitted to enable or disable navigation buttons (New, Modify, Delete)
    navigation_enabled_changed = Signal(bool)

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
        self._original_species_name = ""

        # Load initial data
        self._load_projects_from_db()
        self._load_species_from_db()
        
        # Initial states
        self.save_enabled_changed.emit(False)
        self.navigation_enabled_changed.emit(True)
        self.species_enabled_changed.emit(False)

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

    @Property(str, notify=current_project_changed)
    def current_project(self) -> str:
        """Get the currently selected project name."""
        return self._current_project

    @current_project.setter
    def current_project(self, value: str):
        """Set the current project (property setter)."""
        if self._current_project != value:
            self._current_project = value
            self.current_project_changed.emit(value)

            # Only auto-change the associated species if we are navigating (not editing/creating)
            if not self._project_editable:
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
        self.navigation_enabled_changed.emit(False)

        # 1. Make editable FIRST so the UI accepts custom/empty text
        self._project_editable = True
        self.project_editable_changed.emit(self._project_editable)

        # Enable species selection
        self.species_enabled_changed.emit(True)
        self.save_enabled_changed.emit(True)

        # 2. Set internal state and emit changes to clear UI
        self._current_project = ""
        self.current_project_changed.emit("")

        self._current_species = ""
        self.current_species_changed.emit("")

        # 3. Trigger modify mode to restrict combo box dropdown
        self.project_modify_mode.emit(True)

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
            self.save_enabled_changed.emit(False)
            self.navigation_enabled_changed.emit(True)
            
            # Re-select the saved project
            self.current_project = project.name

        except Exception as e:
            self.project_error.emit(f"Failed to save project: {str(e)}")

    @Slot()
    def handle_modify_species(self):
        """
        Slot called when user clicks 'Modify Species' button.
        This prepares the UI for renaming a species.
        Actual renaming logic is handled in handle_save_project or a dedicated slot.
        """
        if not self._current_species:
            return

        # Store the original name to know what we are renaming
        self._original_species_name = self._current_species

        # Prepare for modification
        self._species_editable = True
        self.species_editable_changed.emit(True)
        # We don't clear the field because we want to edit the existing name

    @Slot()
    def handle_add_species(self):
        """
        Slot called when user clicks 'Add Species' button.
        Prepares UI for adding a new species.
        """
        self._original_species_name = ""  # New species mode
        self._species_editable = True
        self.species_editable_changed.emit(True)
        self.current_species = ""

    @Slot(str, str)
    def handle_confirm_modify_species(self, old_name: str, new_name: str):
        """
        Actually perform the species renaming in the database.
        Called after user confirms the QMessageBox in the View.
        """
        if not new_name or old_name == new_name:
            self._species_editable = False
            self.species_editable_changed.emit(False)
            return

        try:
            if self.repo.update_species(old_name, new_name):
                # Update internal species list
                self._species = [new_name if s == old_name else s for s in self._species]
                self._species.sort()
                self.species_changed.emit(self._species)
                
                # Update current species if it was the one modified
                if self._current_species == old_name:
                    self._current_species = new_name
                    self.current_species_changed.emit(new_name)

                # Update internal projects list (species name changed)
                for p in self._projects:
                    if p.species == old_name:
                        p.species = new_name
                
                self.species_added.emit(f"Species renamed to {new_name}!")
                
                # Exit edit mode
                self._species_editable = False
                self.species_editable_changed.emit(False)
            else:
                self.species_error.emit("Failed to update species in database.")
        except Exception as e:
            self.species_error.emit(f"Error updating species: {str(e)}")

    @Slot()
    def handle_delete_project(self):
        """
        Slot called when user clicks 'Delete Project' button.
        Deletes the currently selected project.
        """
        project_to_delete = self._current_project
        if not project_to_delete:
            return

        try:
            if self.repo.delete_project(project_to_delete):
                # Update internal list
                self._projects = [p for p in self._projects if p.name != project_to_delete]
                self.projects_changed.emit(self.project_list)
                
                # Update current project selection
                if self._projects:
                    # Select the first available project
                    new_project = self._projects[0]
                    self.current_project = new_project.name
                    self.current_species = new_project.species
                else:
                    # No projects left
                    self.current_project = ""
                    self.current_species = ""
                
                self.project_saved.emit(f"Project {project_to_delete} deleted.")
        except Exception as e:
            self.project_error.emit(f"Failed to delete project: {str(e)}")

    @Slot()
    def handle_delete_species(self):
        """
        Slot called when user clicks 'Delete Species' button.
        Deletes the currently selected species if it's not used by any project.
        """
        species_to_delete = self._current_species
        if not species_to_delete:
            return

        # Check if used by any project
        if any(p.species == species_to_delete for p in self._projects):
            self.species_error.emit(f"Cannot delete {species_to_delete}: it is used by some projects.")
            return

        try:
            if self.repo.delete_species(species_to_delete):
                if species_to_delete in self._species:
                    self._species.remove(species_to_delete)
                    self.species_changed.emit(self._species)
                
                # Update selection
                if self._species:
                    self.current_species = self._species[0]
                else:
                    self.current_species = ""
                
                self.species_added.emit(f"Species {species_to_delete} deleted.")
        except Exception as e:
            self.species_error.emit(f"Failed to delete species: {str(e)}")

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
        self.save_enabled_changed.emit(True)
        self.navigation_enabled_changed.emit(False)

    # ==================== PRIVATE METHODS ====================

    def _load_projects_from_db(self):
        """Load projects from database."""
        try:
            self._projects = self.repo.get_all_projects()
            print(f"DEBUG: Loaded {len(self._projects)} projects from DB")
            for p in self._projects:
                print(f"DEBUG: Project: {p.name} ({p.species})")
            self.projects_changed.emit(self.project_list)
            
            # Synchronize initial state: select first project if none selected
            if self._projects and not self._current_project:
                first_project = self._projects[0].name
                self._current_project = first_project
                self.current_project_changed.emit(first_project)
                
                self._current_species = self._projects[0].species
                self.current_species_changed.emit(self._current_species)
                
        except Exception as e:
            print(f"DEBUG: Failed to load projects: {str(e)}")
            self.project_error.emit(f"Failed to load projects: {str(e)}")

    def _load_species_from_db(self):
        """Load species from the dedicated species table."""
        try:
            self._species = self.repo.get_all_species()
            self.species_changed.emit(self._species)
        except Exception as e:
            self.species_error.emit(f"Failed to load species: {str(e)}")

    @Slot(str)
    def handle_add_species_direct(self, species_name: str):
        """
        Actually add a species to the database (called after validation).
        """
        try:
            if self.repo.add_species(species_name):
                if species_name not in self._species:
                    self._species.append(species_name)
                    self._species.sort()
                    self.species_changed.emit(self._species)
                    self.species_added.emit(f"Species {species_name} added!")
        except Exception as e:
            self.species_error.emit(f"Failed to add species: {str(e)}")
