"""
View Model for Boards.

Manages all board-related presentation state.
"""

from PySide6.QtCore import QObject, Signal, Slot, Property
from typing import List
from core.repository import BoardRepository
from mvvm.models import Board


class BoardsViewModel(QObject):
    """
    ViewModel for Boards management.

    Manages board presentation state.
    """

    # ==================== SIGNALS ====================
    boards_changed = Signal(list)
    board_selected = Signal(str)
    board_data_changed = Signal()
    board_error = Signal(str)
    board_saved = Signal(str)
    board_editable_changed = Signal(bool)
    current_board_changed = Signal(str)
    hide_messages = Signal()
    save_enabled_changed = Signal(bool)

    # ==================== CONSTRUCTOR ====================

    def __init__(self, repository: BoardRepository):
        """Initialize the BoardsViewModel with repository."""
        super().__init__()
        self.repo = repository

        # Internal state
        self._boards = []
        self._current_board_no = ""
        self._height = 0.0
        self._base = 0.0
        self._length = 0.0
        self._test_position = ""
        self._comment = ""
        self._board_editable = False
        self._current_project = ""

    # ==================== PROPERTIES ====================

    @Property(list, notify=boards_changed)
    def board_list(self) -> List[str]:
        """Get list of board numbers, sorted numerically if possible."""
        try:
            return sorted([str(b.board_no) for b in self._boards], key=int)
        except ValueError:
            return sorted([str(b.board_no) for b in self._boards])

    @Property(str)
    def current_board_no(self) -> str:
        """Get currently selected board number."""
        return self._current_board_no

    @current_board_no.setter
    def current_board_no(self, value: str):
        """Set the current board number."""
        if self._current_board_no != value:
            self._current_board_no = value
            self.current_board_changed.emit(value)
            if not self._board_editable:
                self.handle_board_selected(value)

    @Property(float)
    def height(self) -> float:
        """Get the height value."""
        return self._height

    @height.setter
    def height(self, value: float):
        """Set the height value."""
        try:
            val = float(value)
            if self._height != val:
                self._height = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(float)
    def base(self) -> float:
        """Get the base value."""
        return self._base

    @base.setter
    def base(self, value: float):
        """Set the base value."""
        try:
            val = float(value)
            if self._base != val:
                self._base = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(float)
    def length(self) -> float:
        """Get the length value."""
        return self._length

    @length.setter
    def length(self, value: float):
        """Set the length value."""
        try:
            val = float(value)
            if self._length != val:
                self._length = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(int)
    def test_position(self) -> int:
        """Get the test position reference."""
        return self._test_position

    @test_position.setter
    def test_position(self, value: int):
        """Set the test position reference."""
        try:
            val = int(value)
            if self._test_position != val:
                self._test_position = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(str)
    def comment(self) -> str:
        """Get the board comment."""
        return self._comment

    @comment.setter
    def comment(self, value: str):
        """Set the board comment."""
        if self._comment != value:
            self._comment = value
            self._mark_dirty()

    # ==================== SLOTS ====================

    def _mark_dirty(self):
        if not self._board_editable and self._current_board_no:
            self.save_enabled_changed.emit(True)

    @Slot(str)
    def handle_project_changed(self, project_name: str):
        """Update current project and load its boards."""
        self._current_project = project_name
        self._board_editable = False
        self._current_board_no = ""  # Force setter to trigger
        self.board_editable_changed.emit(False)
        try:
            if project_name:
                self._boards = self.repo.get_all_boards(project_name)
            else:
                self._boards = []
            
            self.boards_changed.emit(self.board_list)
            
            if self._boards:
                self.current_board_no = str(self._boards[0].board_no)
            else:
                self.handle_new_board()
        except Exception as e:
            self.board_error.emit(f"Failed to load boards: {str(e)}")

    @Slot()
    def handle_new_board(self):
        """Prepare UI for new board creation."""
        self.hide_messages.emit()
        self._board_editable = True
        self.board_editable_changed.emit(True)
        
        self.current_board_no = ""
        self._height = 0.0
        self._base = 0.0
        self._length = 0.0
        self._test_position = 0
        self._comment = ""
        self.board_data_changed.emit()

    @Slot()
    def handle_save_board(self):
        """Validate and save board data."""
        self.hide_messages.emit()
        
        if not self._current_project:
            self.board_error.emit("No project selected!")
            return

        if not self._current_board_no:
            self.board_error.emit("Board number cannot be empty!")
            return
            
        board_text = str(self._current_board_no).strip()
        
        # Check duplicate if creating
        if self._board_editable and any(str(b.board_no) == board_text for b in self._boards):
            self.board_error.emit("Board already exists!")
            return

        try:
            board = Board(
                board_no=board_text,
                height=self._height,
                base=self._base,
                length=self._length,
                test_position=self._test_position,
                comment=self._comment
            )

            if not board.validate_measurements():
                self.board_error.emit("Invalid measurements! Height, base, and length must be numbers >= 0.")
                return

            if self._board_editable:
                # Creating a new board
                if self.repo.add_board(board, self._current_project):
                    self._boards.append(board)
                    self.boards_changed.emit(self.board_list)
                    self.board_saved.emit(f"Board {self._current_board_no} saved!")
                    
                    self._board_editable = False
                    self.board_editable_changed.emit(False)
                    self.handle_board_selected(self._current_board_no)
            else:
                # Modifying an existing board
                if self.repo.update_board(board, self._current_project):
                    # Update local list
                    for idx, b in enumerate(self._boards):
                        if str(b.board_no) == board_text:
                            self._boards[idx] = board
                            break
                    self.board_saved.emit(f"Board {self._current_board_no} updated!")
                    self.save_enabled_changed.emit(False)
                    
        except Exception as e:
            self.board_error.emit(f"Failed to save: {str(e)}")

    @Slot()
    def handle_delete_board(self):
        """Delete the currently selected board."""
        self.hide_messages.emit()
        
        if not self._current_project:
            self.board_error.emit("No project selected!")
            return

        if not self._current_board_no:
            self.board_error.emit("No board selected!")
            return

        try:
            if self.repo.delete_board(self._current_board_no, self._current_project):
                self._boards = [b for b in self._boards if str(b.board_no) != self._current_board_no]
                self.boards_changed.emit(self.board_list)
                
                if self._boards:
                    self.current_board_no = str(self._boards[0].board_no)
                else:
                    self.handle_new_board()
        except Exception as e:
            self.board_error.emit(f"Failed to delete: {str(e)}")

    @Slot(str)
    def handle_board_selected(self, board_no: str):
        """Load board data when selected."""
        if not board_no:
            self.handle_new_board()
            return

        if not self._current_project:
            return

        try:
            board = self.repo.get_board_by_id(board_no, self._current_project)
            if board:
                self._current_board_no = str(board.board_no)
                self._height = board.height
                self._base = board.base
                self._length = board.length
                self._test_position = board.test_position
                self._comment = board.comment
                self.board_data_changed.emit()
                self.board_selected.emit(board_no)
                self.save_enabled_changed.emit(False)
        except Exception as e:
            self.board_error.emit(f"Failed to load: {str(e)}")

    @Slot()
    def handle_previous_board(self):
        """Navigate to previous board in combobox order."""
        if not self._boards or not self._current_board_no:
            return
            
        sorted_boards = self.board_list
        try:
            current_index = sorted_boards.index(self._current_board_no)
            if current_index > 0:
                self.current_board_no = sorted_boards[current_index - 1]
        except ValueError:
            pass

    @Slot()
    def handle_next_board(self):
        """Navigate to next board in combobox order."""
        if not self._boards or not self._current_board_no:
            return
            
        sorted_boards = self.board_list
        try:
            current_index = sorted_boards.index(self._current_board_no)
            if current_index >= 0 and current_index < len(sorted_boards) - 1:
                self.current_board_no = sorted_boards[current_index + 1]
        except ValueError:
            pass


