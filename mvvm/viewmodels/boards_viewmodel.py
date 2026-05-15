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

    # ==================== PROPERTIES ====================

    @Property(list, notify=boards_changed)
    def board_list(self) -> List[str]:
        """Get list of board numbers."""
        return [str(b.board_no) for b in self._boards]

    @Property(str)
    def current_board_no(self) -> str:
        """Get currently selected board number."""
        return self._current_board_no

    @current_board_no.setter
    def current_board_no(self, value: str):
        """Set the current board number."""
        if self._current_board_no != value:
            self._current_board_no = value
            self.handle_board_selected(value)

    @Property(float)
    def height(self) -> float:
        """Get the height value."""
        return self._height

    @height.setter
    def height(self, value: float):
        """Set the height value."""
        try:
            self._height = float(value)
            self.board_data_changed.emit()
        except (ValueError, TypeError):
            self._height = 0.0

    @Property(float)
    def base(self) -> float:
        """Get the base value."""
        return self._base

    @base.setter
    def base(self, value: float):
        """Set the base value."""
        try:
            self._base = float(value)
            self.board_data_changed.emit()
        except (ValueError, TypeError):
            self._base = 0.0

    @Property(float)
    def length(self) -> float:
        """Get the length value."""
        return self._length

    @length.setter
    def length(self, value: float):
        """Set the length value."""
        try:
            self._length = float(value)
            self.board_data_changed.emit()
        except (ValueError, TypeError):
            self._length = 0.0

    @Property(str)
    def test_position(self) -> str:
        """Get the test position reference."""
        return self._test_position

    @test_position.setter
    def test_position(self, value: str):
        """Set the test position reference."""
        if self._test_position != value:
            self._test_position = value
            self.board_data_changed.emit()

    @Property(str)
    def comment(self) -> str:
        """Get the board comment."""
        return self._comment

    @comment.setter
    def comment(self, value: str):
        """Set the board comment."""
        if self._comment != value:
            self._comment = value
            self.board_data_changed.emit()

    # ==================== SLOTS ====================

    @Slot()
    def handle_new_board(self):
        """Prepare UI for new board creation."""
        self._current_board_no = ""
        self._height = 0.0
        self._base = 0.0
        self._length = 0.0
        self._test_position = ""
        self._comment = ""
        self.board_data_changed.emit()

    @Slot()
    def handle_save_board(self):
        """Validate and save board data."""
        if not self._current_board_no:
            self.board_error.emit("Board number cannot be empty!")
            return

        try:
            board = Board(
                board_no=self._current_board_no,
                height=self._height,
                base=self._base,
                length=self._length,
                test_position=self._test_position,
                comment=self._comment
            )

            if not board.validate_measurements():
                self.board_error.emit("Invalid measurements!")
                return

            if self.repo.add_board(board):
                self._boards.append(board)
                self.boards_changed.emit(self.board_list)
                self.board_saved.emit(f"Board {self._current_board_no} saved!")
                self.handle_new_board()
        except Exception as e:
            self.board_error.emit(f"Failed to save: {str(e)}")

    @Slot()
    def handle_delete_board(self):
        """Delete the currently selected board."""
        if not self._current_board_no:
            self.board_error.emit("No board selected!")
            return

        try:
            if self.repo.delete_board(self._current_board_no, ""):
                self._boards = [b for b in self._boards if str(b.board_no) != self._current_board_no]
                self.boards_changed.emit(self.board_list)
                self.handle_new_board()
        except Exception as e:
            self.board_error.emit(f"Failed to delete: {str(e)}")

    @Slot(str)
    def handle_board_selected(self, board_no: str):
        """Load board data when selected."""
        if not board_no:
            self.handle_new_board()
            return

        try:
            board = self.repo.get_board_by_id(board_no, "")
            if board:
                self._current_board_no = str(board.board_no)
                self._height = board.height
                self._base = board.base
                self._length = board.length
                self._test_position = board.test_position
                self._comment = board.comment
                self.board_data_changed.emit()
                self.board_selected.emit(board_no)
        except Exception as e:
            self.board_error.emit(f"Failed to load: {str(e)}")


