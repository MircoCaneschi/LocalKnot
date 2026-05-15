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

    # ==================== CONSTRUCTOR ====================

    def __init__(self, repository: KnotRepository):
        """Initialize the KnotsViewModel with repository."""
        super().__init__()
        self.repo = repository

        # Internal state
        self._knots = []
        self._current_knot_no = ""
        self._x = 0.0
        self._pith_z = 0.0
        self._pith_y = 0.0
        self._is_fake_pith = False
        self._comment = ""

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
            self.handle_knot_selected(value)

    @Property(float)
    def x(self) -> float:
        """Get the X coordinate."""
        return self._x

    @x.setter
    def x(self, value: float):
        """Set the X coordinate."""
        try:
            self._x = float(value)
            self.knot_data_changed.emit()
        except (ValueError, TypeError):
            self._x = 0.0

    @Property(float)
    def pith_z(self) -> float:
        """Get the Pith Z coordinate."""
        return self._pith_z

    @pith_z.setter
    def pith_z(self, value: float):
        """Set the Pith Z coordinate."""
        try:
            self._pith_z = float(value)
            self.knot_data_changed.emit()
        except (ValueError, TypeError):
            self._pith_z = 0.0

    @Property(float)
    def pith_y(self) -> float:
        """Get the Pith Y coordinate."""
        return self._pith_y

    @pith_y.setter
    def pith_y(self, value: float):
        """Set the Pith Y coordinate."""
        try:
            self._pith_y = float(value)
            self.knot_data_changed.emit()
        except (ValueError, TypeError):
            self._pith_y = 0.0

    @Property(bool)
    def is_fake_pith(self) -> bool:
        """Get whether this knot has a fake pith."""
        return self._is_fake_pith

    @is_fake_pith.setter
    def is_fake_pith(self, value: bool):
        """Set whether pith is fake."""
        if self._is_fake_pith != value:
            self._is_fake_pith = value
            self.knot_data_changed.emit()

    @Property(str)
    def comment(self) -> str:
        """Get the knot comment."""
        return self._comment

    @comment.setter
    def comment(self, value: str):
        """Set the knot comment."""
        if self._comment != value:
            self._comment = value
            self.knot_data_changed.emit()

    # ==================== SLOTS ====================

    @Slot()
    def handle_new_knot(self):
        """Prepare UI for new knot creation."""
        self._current_knot_no = ""
        self._x = 0.0
        self._pith_z = 0.0
        self._pith_y = 0.0
        self._is_fake_pith = False
        self._comment = ""
        self.knot_data_changed.emit()

    @Slot()
    def handle_save_knot(self):
        """Validate and save knot data."""
        if not self._current_knot_no:
            self.knot_error.emit("Knot number cannot be empty!")
            return

        try:
            knot = Knot(
                knot_no=self._current_knot_no,
                x=self._x,
                pith_z=self._pith_z,
                pith_y=self._pith_y,
                is_fake_pith=self._is_fake_pith,
                comment=self._comment
            )

            if not knot.validate_coordinates():
                self.knot_error.emit("Invalid coordinates!")
                return

            if self.repo.add_knot(knot):
                self._knots.append(knot)
                self.knots_changed.emit(self.knot_list)
                self.knot_saved.emit(f"Knot {self._current_knot_no} saved!")
                self.handle_new_knot()
        except Exception as e:
            self.knot_error.emit(f"Failed to save: {str(e)}")

    @Slot()
    def handle_delete_knot(self):
        """Delete the currently selected knot."""
        if not self._current_knot_no:
            self.knot_error.emit("No knot selected!")
            return

        try:
            if self.repo.delete_knot(self._current_knot_no, "", ""):
                self._knots = [k for k in self._knots if str(k.knot_no) != self._current_knot_no]
                self.knots_changed.emit(self.knot_list)
                self.handle_new_knot()
        except Exception as e:
            self.knot_error.emit(f"Failed to delete: {str(e)}")

    @Slot(str)
    def handle_knot_selected(self, knot_no: str):
        """Load knot data when selected."""
        if not knot_no:
            self.handle_new_knot()
            return

        try:
            knot = self.repo.get_knot_by_id(knot_no, "", "")
            if knot:
                self._current_knot_no = str(knot.knot_no)
                self._x = knot.x
                self._pith_z = knot.pith_z
                self._pith_y = knot.pith_y
                self._is_fake_pith = knot.is_fake_pith
                self._comment = knot.comment
                self.knot_data_changed.emit()
                self.knot_selected.emit(knot_no)
        except Exception as e:
            self.knot_error.emit(f"Failed to load: {str(e)}")

    # ==================== PRIVATE METHODS ====================

    def _load_knot_data(self, knot_no: str) -> bool:
        """Load knot data from model by knot number."""
        try:
            knot = self.repo.get_knot_by_id(knot_no, "", "")
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
