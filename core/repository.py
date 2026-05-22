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
from mvvm.models import Project, Board, Knot


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
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id_project, species FROM project")
                rows = cursor.fetchall()
                return [Project(name=row[0], species=row[1]) for row in rows]
        except Exception as e:
            raise Exception(f"Failed to get projects: {str(e)}")

    def get_project_by_id(self, project_id: str) -> Optional[Project]:
        """
        Get a specific project by ID.

        Args:
            project_id: Project ID to retrieve

        Returns:
            Optional[Project]: Project if found, None otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id_project, species FROM project WHERE id_project = ?", (project_id,))
                row = cursor.fetchone()
                if row:
                    return Project(name=row[0], species=row[1])
                return None
        except Exception as e:
            raise Exception(f"Failed to get project: {str(e)}")

    def add_project(self, project: Project) -> bool:
        """
        Add a new project to database.
        Ensures species exists in the species table first.

        Args:
            project: Project instance to add

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                # Ensure species exists
                cursor.execute("INSERT OR IGNORE INTO species (name) VALUES (?)", (project.species,))
                
                cursor.execute(
                    "INSERT INTO project (id_project, species) VALUES (?, ?)",
                    (project.name, project.species)
                )
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Failed to add project: {str(e)}")

    def update_project(self, old_project_name: str, project: Project) -> bool:
        """
        Update an existing project and cascade renaming if necessary.
        Ensures species exists in the species table first.

        Args:
            old_project_name: The original name of the project
            project: Project instance with updated data

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                # Ensure species exists
                cursor.execute("INSERT OR IGNORE INTO species (name) VALUES (?)", (project.species,))

                if old_project_name != project.name:
                    # Rename project and manually cascade to boards and knots
                    cursor.execute(
                        "UPDATE project SET id_project = ?, species = ? WHERE id_project = ?",
                        (project.name, project.species, old_project_name)
                    )
                    cursor.execute(
                        "UPDATE board SET id_project = ? WHERE id_project = ?",
                        (project.name, old_project_name)
                    )
                    cursor.execute(
                        "UPDATE knot SET id_project = ? WHERE id_project = ?",
                        (project.name, old_project_name)
                    )
                else:
                    # Just update species
                    cursor.execute(
                        "UPDATE project SET species = ? WHERE id_project = ?",
                        (project.species, old_project_name)
                    )
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Failed to update project: {str(e)}")

    def get_all_species(self) -> List[str]:
        """Get all species names from the species table."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM species ORDER BY name ASC")
                rows = cursor.fetchall()
                return [row[0] for row in rows]
        except Exception as e:
            raise Exception(f"Failed to get species: {str(e)}")

    def add_species(self, species_name: str) -> bool:
        """Add a new species to the species table."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO species (name) VALUES (?)", (species_name,))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Failed to add species: {str(e)}")

    def update_species(self, old_name: str, new_name: str) -> bool:
        """
        Rename a species and update all projects using it.
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                # 1. Update species table
                cursor.execute("UPDATE species SET name = ? WHERE name = ?", (new_name, old_name))
                # 2. Update project table (manual cascade if not in schema)
                cursor.execute("UPDATE project SET species = ? WHERE species = ?", (new_name, old_name))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Failed to update species: {str(e)}")

    def delete_species(self, species_name: str) -> bool:
        """
        Delete a species. 
        Note: foreign key constraints might prevent this if projects still use it.
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM species WHERE name = ?", (species_name,))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Failed to delete species: {str(e)}")

    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project (cascades to boards and knots).

        Args:
            project_id: Project ID to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM project WHERE id_project = ?", (project_id,))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Failed to delete project: {str(e)}")

    def project_exists(self, project_id: str) -> bool:
        """
        Check if a project exists.

        Args:
            project_id: Project ID to check

        Returns:
            bool: True if exists, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM project WHERE id_project = ? LIMIT 1", (project_id,))
                return cursor.fetchone() is not None
        except:
            return False


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
        """Get all boards for a specific project."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id_board, id_project, height, base, length, testpos, comment FROM board WHERE id_project = ?", (project_id,))
                rows = cursor.fetchall()
                return [Board(board_no=row[0], height=row[2], base=row[3], length=row[4], test_position=row[5], comment=row[6]) for row in rows]
        except Exception as e:
            raise Exception(f"Failed to get boards: {str(e)}")

    def get_board_by_id(self, board_id: str, project_id: str) -> Optional[Board]:
        """Get a specific board by ID."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id_board, id_project, height, base, length, testpos, comment FROM board WHERE id_board = ? AND id_project = ?", (board_id, project_id))
                row = cursor.fetchone()
                if row:
                    return Board(board_no=row[0], height=row[2], base=row[3], length=row[4], test_position=row[5], comment=row[6])
                return None
        except Exception as e:
            raise Exception(f"Failed to get board: {str(e)}")

    def add_board(self, board: Board, project_id: str) -> bool:
        """Add a new board to database."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO board (id_board, id_project, height, base, length, testpos, comment) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (board.board_no, project_id, board.height, board.base, board.length, board.test_position, board.comment)
                )
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Failed to add board: {str(e)}")

    def update_board(self, board: Board, project_id: str) -> bool:
        """Update an existing board."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE board SET height = ?, base = ?, length = ?, testpos = ?, comment = ? WHERE id_board = ? AND id_project = ?",
                    (board.height, board.base, board.length, board.test_position, board.comment, board.board_no, project_id)
                )
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Failed to update board: {str(e)}")

    def delete_board(self, board_id: str, project_id: str) -> bool:
        """Delete a board (cascades to knots)."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM board WHERE id_board = ? AND id_project = ?", (board_id, project_id))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Failed to delete board: {str(e)}")

    def board_exists(self, board_id: str, project_id: str) -> bool:
        """Check if a board exists."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM board WHERE id_board = ? LIMIT 1", (board_id,))
                return cursor.fetchone() is not None
        except:
            return False


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

    def get_all_knots(self, board_id: str, project_id: str) -> List[Knot]:
        """Get all knots for a specific board."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id_nodo, id_board, x, pith_z, pith_y, comment, fake_pith FROM knot WHERE id_board = ?", (board_id,))
                rows = cursor.fetchall()
                return [Knot(knot_no=row[0], x=row[2], pith_z=row[3], pith_y=row[4], comment=row[5], is_fake_pith=row[6]) for row in rows]
        except Exception as e:
            raise Exception(f"Failed to get knots: {str(e)}")

    def get_knot_by_id(self, knot_id: str, board_id: str, project_id: str) -> Optional[Knot]:
        """Get a specific knot by ID."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id_nodo, id_board, x, pith_z, pith_y, comment, fake_pith FROM knot WHERE id_nodo = ? AND id_board = ?", (knot_id, board_id))
                row = cursor.fetchone()
                if row:
                    return Knot(knot_no=row[0], x=row[2], pith_z=row[3], pith_y=row[4], comment=row[5], is_fake_pith=row[6])
                return None
        except Exception as e:
            raise Exception(f"Failed to get knot: {str(e)}")

    def add_knot(self, knot: Knot) -> bool:
        """Add a new knot to database."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO knot (id_nodo, id_board, id_project, x, pith_z, pith_y, comment, fake_pith, side1_z1, side1_z2, side1_dmin, side2_z1, side2_z2, side2_dmin, side3_z1, side3_z2, side3_dmin, side4_z1, side4_z2, side4_dmin) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)",
                    (knot.knot_no, "", "", knot.x, knot.pith_z, knot.pith_y, knot.comment, knot.is_fake_pith)
                )
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Failed to add knot: {str(e)}")

    def update_knot(self, knot: Knot) -> bool:
        """Update an existing knot."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE knot SET x = ?, pith_z = ?, pith_y = ?, comment = ?, fake_pith = ? WHERE id_nodo = ?",
                    (knot.x, knot.pith_z, knot.pith_y, knot.comment, knot.is_fake_pith, knot.knot_no)
                )
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Failed to update knot: {str(e)}")

    def delete_knot(self, knot_id: str, board_id: str, project_id: str) -> bool:
        """Delete a knot."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM knot WHERE id_nodo = ?", (knot_id,))
                conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Failed to delete knot: {str(e)}")

    def knot_exists(self, knot_id: str, board_id: str, project_id: str) -> bool:
        """Check if a knot exists."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM knot WHERE id_nodo = ? LIMIT 1", (knot_id,))
                return cursor.fetchone() is not None
        except:
            return False




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

