"""
Repository Pattern for Data Access.

Provides a clean interface between ViewModels and the database layer.
This abstraction allows ViewModels to NOT know about SQLite directly.

Pattern: Repository
├─ ProjectRepository: Handles Project CRUD operations
├─ BoardRepository: Handles Board CRUD operations
└─ KnotRepository: Handles Knot CRUD operations

Dependencies:
├─ core.database.DatabaseManager
└─ core.data_models (Project, Board, Knot dataclasses)
"""

from typing import List, Optional
from core.database import DatabaseManager
from core.data_models import Project, Board, Knot


class ProjectRepository:
    """
    Repository for Project data operations.

    Provides CRUD interface for Project entities.
    Abstracts SQLite operations away from ViewModel.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize repository with database manager.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager

    def get_all_projects(self) -> List[Project]:
        """
        Get all projects from database.

        Returns:
            List[Project]: List of all projects
        """
        pass

    def get_project_by_id(self, project_id: str) -> Optional[Project]:
        """
        Get a specific project by ID.

        Args:
            project_id: Project ID to retrieve

        Returns:
            Optional[Project]: Project if found, None otherwise
        """
        pass

    def add_project(self, project: Project) -> bool:
        """
        Add a new project to database.

        Args:
            project: Project instance to add

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    def update_project(self, project: Project) -> bool:
        """
        Update an existing project.

        Args:
            project: Project instance with updated data

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project (cascades to boards and knots).

        Args:
            project_id: Project ID to delete

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    def project_exists(self, project_id: str) -> bool:
        """
        Check if a project exists.

        Args:
            project_id: Project ID to check

        Returns:
            bool: True if exists, False otherwise
        """
        pass


class BoardRepository:
    """
    Repository for Board data operations.

    Provides CRUD interface for Board entities within a Project.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize repository with database manager.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager

    def get_all_boards(self, project_id: str) -> List[Board]:
        """
        Get all boards for a specific project.

        Args:
            project_id: Project ID to get boards for

        Returns:
            List[Board]: List of boards in project
        """
        pass

    def get_board_by_id(self, board_id: int, project_id: str) -> Optional[Board]:
        """
        Get a specific board by ID.

        Args:
            board_id: Board ID to retrieve
            project_id: Project ID (composite key)

        Returns:
            Optional[Board]: Board if found, None otherwise
        """
        pass

    def add_board(self, board: Board) -> bool:
        """
        Add a new board to database.

        Args:
            board: Board instance to add

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    def update_board(self, board: Board) -> bool:
        """
        Update an existing board.

        Args:
            board: Board instance with updated data

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    def delete_board(self, board_id: int, project_id: str) -> bool:
        """
        Delete a board (cascades to knots).

        Args:
            board_id: Board ID to delete
            project_id: Project ID (composite key)

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    def board_exists(self, board_id: int, project_id: str) -> bool:
        """
        Check if a board exists.

        Args:
            board_id: Board ID to check
            project_id: Project ID (composite key)

        Returns:
            bool: True if exists, False otherwise
        """
        pass


class KnotRepository:
    """
    Repository for Knot data operations.

    Provides CRUD interface for Knot entities within a Board.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize repository with database manager.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager

    def get_all_knots(self, board_id: int, project_id: str) -> List[Knot]:
        """
        Get all knots for a specific board.

        Args:
            board_id: Board ID to get knots for
            project_id: Project ID (parent of board)

        Returns:
            List[Knot]: List of knots in board
        """
        pass

    def get_knot_by_id(self, knot_id: int, board_id: int,
                      project_id: str) -> Optional[Knot]:
        """
        Get a specific knot by ID.

        Args:
            knot_id: Knot ID to retrieve
            board_id: Board ID (composite key)
            project_id: Project ID (composite key)

        Returns:
            Optional[Knot]: Knot if found, None otherwise
        """
        pass

    def add_knot(self, knot: Knot) -> bool:
        """
        Add a new knot to database.

        Args:
            knot: Knot instance to add

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    def update_knot(self, knot: Knot) -> bool:
        """
        Update an existing knot.

        Args:
            knot: Knot instance with updated data

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    def delete_knot(self, knot_id: int, board_id: int,
                   project_id: str) -> bool:
        """
        Delete a knot.

        Args:
            knot_id: Knot ID to delete
            board_id: Board ID (composite key)
            project_id: Project ID (composite key)

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    def knot_exists(self, knot_id: int, board_id: int,
                   project_id: str) -> bool:
        """
        Check if a knot exists.

        Args:
            knot_id: Knot ID to check
            board_id: Board ID (composite key)
            project_id: Project ID (composite key)

        Returns:
            bool: True if exists, False otherwise
        """
        pass


# ==================== USAGE EXAMPLE ====================
#
# In a ViewModel:
#
#     from core.database import DatabaseManager
#     from core.repository import ProjectRepository
#
#     class ProjectsViewModel(QObject):
#         def __init__(self, db_manager: DatabaseManager):
#             super().__init__()
#             self.project_repo = ProjectRepository(db_manager)
#             self._load_projects()
#
#         def _load_projects(self):
#             try:
#                 projects = self.project_repo.get_all_projects()
#                 # Update UI
#             except Exception as e:
#                 # Emit error signal
#                 pass
#
#         @Slot()
#         def handle_save_project(self):
#             project = Project(id_project=name, species=species)
#             if self.project_repo.add_project(project):
#                 self.project_saved.emit(name)
#             else:
#                 self.project_error.emit("Failed to save")

