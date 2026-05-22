"""
View Model for Knots.

Manages all knot-related presentation state.
"""

from PySide6.QtCore import QObject, Signal, Slot, Property
from typing import List
from core.repository import KnotRepository
from mvvm.models import Knot


class KnotsViewModel(QObject):
    """
    ViewModel for Knots management.

    Exposes:
    - Properties: knot_list, current_knot, x, pith_z, pith_y, is_fake_pith, etc.
    - Signals: knots_changed, knot_selected, etc.
    - Slots: handleNewKnot, handleSaveKnot, handleDeleteKnot, etc.
    """

    # ==================== SIGNALS ====================

    # Emitted when the knots list changes
    knots_changed = Signal(list)

    # Emitted when a knot is selected
    knot_selected = Signal(str)

    # Emitted when knot data changes
    knot_data_changed = Signal()

    # Emitted on validation error
    knot_error = Signal(str)

    # Emitted on successful save
    knot_saved = Signal(str)

    knot_editable_changed = Signal(bool)
    current_knot_changed = Signal(str)
    hide_messages = Signal()
    save_enabled_changed = Signal(bool)

    # ==================== CONSTRUCTOR ====================

    def __init__(self, repository: KnotRepository):
        """Initialize the KnotsViewModel with repository."""
        super().__init__()
        self.repo = repository

        # Internal state
        self._knots = []
        self._current_knot_no = ""
        self._x = 0
        self._pith_z = 0
        self._pith_y = 0
        self._is_fake_pith = False
        self._comment = ""
        self._knot_editable = False
        self._current_project = ""
        self._current_board = ""

    # ==================== PROPERTIES ====================

    @Property(list, notify=knots_changed)
    def knot_list(self) -> List[str]:
        """Get list of knot numbers."""
        return [str(k.knot_no) for k in self._knots]

    @Property(str)
    def current_knot_no(self) -> str:
        """Get currently selected knot number."""
        return self._current_knot_no

    @current_knot_no.setter
    def current_knot_no(self, value: str):
        """Set the current knot number."""
        if self._current_knot_no != value:
            self._current_knot_no = value
            self.current_knot_changed.emit(value)
            if not self._knot_editable:
                self.handle_knot_selected(value)

    def _mark_dirty(self):
        if not self._knot_editable and self._current_knot_no:
            self.save_enabled_changed.emit(True)

    @Property(int)
    def x(self) -> int:
        """Get the X coordinate."""
        return self._x

    @x.setter
    def x(self, value: int):
        """Set the X coordinate."""
        try:
            val = int(value)
            if self._x != val:
                self._x = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(int)
    def pith_z(self) -> int:
        """Get the Pith Z coordinate."""
        return self._pith_z

    @pith_z.setter
    def pith_z(self, value: int):
        """Set the Pith Z coordinate."""
        try:
            val = int(value)
            if self._pith_z != val:
                self._pith_z = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(int)
    def pith_y(self) -> int:
        """Get the Pith Y coordinate."""
        return self._pith_y

    @pith_y.setter
    def pith_y(self, value: int):
        """Set the Pith Y coordinate."""
        try:
            val = int(value)
            if self._pith_y != val:
                self._pith_y = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(bool)
    def is_fake_pith(self) -> bool:
        """Get whether this knot has a fake pith."""
        return self._is_fake_pith

    @is_fake_pith.setter
    def is_fake_pith(self, value: bool):
        """Set whether pith is fake."""
        if self._is_fake_pith != value:
            if not self._current_knot_no and not self._knot_editable:
                # Discard the change visually and don't save
                self.knot_error.emit("Nessun nodo selezionato!")
                self.knot_data_changed.emit()
                return

            self._is_fake_pith = value
            self.knot_data_changed.emit()
            self._mark_dirty()
            # Save automatically on toggle if it's an existing knot
            if not self._knot_editable and self._current_knot_no:
                self.handle_save_knot()

    @Property(str)
    def comment(self) -> str:
        """Get the knot comment."""
        return self._comment

    @comment.setter
    def comment(self, value: str):
        """Set the knot comment."""
        if self._comment != value:
            self._comment = value
            self._mark_dirty()

    # ==================== SLOTS ====================

    @Slot(str)
    def handle_project_changed(self, project_name: str):
        """Track current project."""
        self._current_project = project_name
        self._current_board = ""
        self._knots = []
        self.knots_changed.emit(self.knot_list)
        self.handle_new_knot()

    @Slot(str)
    def handle_board_changed(self, board_no: str):
        """Update current board and load its knots."""
        self._current_board = board_no
        self._knot_editable = False
        self.knot_editable_changed.emit(False)
        try:
            if board_no and self._current_project:
                self._knots = self.repo.get_all_knots(board_no, self._current_project)
            else:
                self._knots = []
            
            self.knots_changed.emit(self.knot_list)
            
            if self._knots:
                self.current_knot_no = str(self._knots[0].knot_no)
            else:
                self.handle_new_knot()
        except Exception as e:
            self.knot_error.emit(f"Failed to load knots: {str(e)}")

    @Slot()
    def handle_new_knot(self):
        """Prepare UI for new knot creation."""
        self.hide_messages.emit()
        self._knot_editable = True
        self.knot_editable_changed.emit(True)
        
        self.current_knot_no = ""
        self._x = 0
        self._pith_z = 0
        self._pith_y = 0
        self._is_fake_pith = False
        self._comment = ""
        self.knot_data_changed.emit()

    @Slot()
    def handle_save_knot(self):
        """Validate and save knot data."""
        self.hide_messages.emit()
        
        if not self._current_project or not self._current_board:
            self.knot_error.emit("No project or board selected!")
            return
            
        if not self._current_knot_no:
            self.knot_error.emit("Knot number cannot be empty!")
            return
            
        knot_text = str(self._current_knot_no).strip()
        
        # Check duplicate if creating
        if self._knot_editable and any(str(k.knot_no) == knot_text for k in self._knots):
            self.knot_error.emit("Knot already exists!")
            return

        try:
            knot = Knot(
                knot_no=knot_text,
                x=self._x,
                pith_z=self._pith_z,
                pith_y=self._pith_y,
                is_fake_pith=self._is_fake_pith,
                comment=self._comment
            )

            if not knot.validate_coordinates():
                self.knot_error.emit("Invalid coordinates! Must be integers.")
                return

            if self._knot_editable:
                if self.repo.add_knot(knot, self._current_board, self._current_project):
                    self._knots.append(knot)
                    self.knots_changed.emit(self.knot_list)
                    self.knot_saved.emit(f"Knot {self._current_knot_no} saved!")
                    
                    self._knot_editable = False
                    self.knot_editable_changed.emit(False)
                    self.handle_knot_selected(self._current_knot_no)
            else:
                if self.repo.update_knot(knot):
                    for idx, k in enumerate(self._knots):
                        if str(k.knot_no) == knot_text:
                            self._knots[idx] = knot
                            break
                    self.knot_saved.emit(f"Knot {self._current_knot_no} updated!")
                    self.save_enabled_changed.emit(False)
        except Exception as e:
            self.knot_error.emit(f"Failed to save: {str(e)}")

    @Slot()
    def handle_delete_knot(self):
        """Delete the currently selected knot."""
        self.hide_messages.emit()
        
        if not self._current_project or not self._current_board:
            self.knot_error.emit("No project or board selected!")
            return

        if not self._current_knot_no:
            self.knot_error.emit("No knot selected!")
            return

        try:
            if self.repo.delete_knot(self._current_knot_no, self._current_board, self._current_project):
                self._knots = [k for k in self._knots if str(k.knot_no) != self._current_knot_no]
                self.knots_changed.emit(self.knot_list)
                
                if self._knots:
                    self.current_knot_no = str(self._knots[0].knot_no)
                else:
                    self.handle_new_knot()
        except Exception as e:
            self.knot_error.emit(f"Failed to delete: {str(e)}")

    @Slot(str)
    def handle_knot_selected(self, knot_no: str):
        """Load knot data when selected."""
        if not knot_no:
            self.handle_new_knot()
            return

        if not self._current_board or not self._current_project:
            return

        try:
            knot = self.repo.get_knot_by_id(knot_no, self._current_board, self._current_project)
            if knot:
                self._current_knot_no = str(knot.knot_no)
                self._x = knot.x
                self._pith_z = knot.pith_z
                self._pith_y = knot.pith_y
                self._is_fake_pith = knot.is_fake_pith
                self._comment = knot.comment
                self.knot_data_changed.emit()
                self.knot_selected.emit(knot_no)
                self.save_enabled_changed.emit(False)
        except Exception as e:
            self.knot_error.emit(f"Failed to load: {str(e)}")

    @Slot()
    def handle_previous_knot(self):
        """Navigate to previous knot in combobox order."""
        if not self._knots or not self._current_knot_no:
            return
            
        sorted_knots = self.knot_list
        try:
            current_index = sorted_knots.index(self._current_knot_no)
            if current_index > 0:
                self.current_knot_no = sorted_knots[current_index - 1]
        except ValueError:
            pass

    @Slot()
    def handle_next_knot(self):
        """Navigate to next knot in combobox order."""
        if not self._knots or not self._current_knot_no:
            return
            
        sorted_knots = self.knot_list
        try:
            current_index = sorted_knots.index(self._current_knot_no)
            if current_index >= 0 and current_index < len(sorted_knots) - 1:
                self.current_knot_no = sorted_knots[current_index + 1]
        except ValueError:
            pass

    # ==================== PRIVATE METHODS ====================

    def _load_knot_data(self, knot_no: str) -> bool:
        """Load knot data from model by knot number."""
        try:
            knot = self.repo.get_knot_by_id(knot_no, self._current_board, self._current_project)
            if knot:
                self._current_knot_no = str(knot.knot_no)
                self._x = knot.x
                self._pith_z = knot.pith_z
                self._pith_y = knot.pith_y
                self._is_fake_pith = knot.is_fake_pith
                self._comment = knot.comment
                return True
            return False
        except:
            return False

    def _validate_knot_data(self) -> tuple:
        """Validate current knot data."""
        if not self._current_knot_no:
            return False, "Knot number cannot be empty"
        knot = Knot(knot_no=self._current_knot_no, x=self._x, pith_z=self._pith_z, pith_y=self._pith_y)
        if not knot.validate_coordinates():
            return False, "Invalid coordinates"
        return True, "Valid"

    def _clear_knot_data(self):
        """Reset all knot fields to empty/default state."""
        self.handle_new_knot()
