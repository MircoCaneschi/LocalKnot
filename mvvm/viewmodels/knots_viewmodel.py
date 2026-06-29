"""
View Model for Knots.

Manages all knot-related presentation state.
"""

from PySide6.QtCore import QObject, Signal, Slot, Property
from typing import List
from core.repository import KnotRepository, BoardRepository
from mvvm.models import Knot
from core.exceptions import LocalKnotError


class KnotsViewModel(QObject):
    """
    ViewModel for Knots management.

    Exposes:
    - Properties: knot_list, current_knot, x, pith_z, pith_y, is_pruned_knot, etc.
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

    validation_failed = Signal(list)
    virtual_board_error = Signal(str)
    knot_editable_changed = Signal(bool)
    current_knot_changed = Signal(str)
    hide_messages = Signal()
    save_enabled_changed = Signal(bool)

    # ==================== CONSTRUCTOR ====================

    def __init__(self, repository: KnotRepository, board_repo: BoardRepository = None):
        """Initialize the KnotsViewModel with repositories."""
        super().__init__()
        self.repo = repository
        self.board_repo = board_repo

        # Internal state
        self._knots = []
        self._current_knot_no = ""
        self._x = 0
        self._pith_z = None
        self._pith_y = None
        self._is_pruned_knot = False
        self._pruned_z1 = None
        self._pruned_y1 = None
        self._pruned_z2 = None
        self._pruned_y2 = None
        self._comment = ""
        self._side1_z1 = None
        self._side1_z2 = None
        self._side1_dmin = None
        self._side2_z1 = None
        self._side2_z2 = None
        self._side2_dmin = None
        self._side3_z1 = None
        self._side3_z2 = None
        self._side3_dmin = None
        self._side4_z1 = None
        self._side4_z2 = None
        self._side4_dmin = None
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

    @Property(object)
    def x(self):
        """Get the X coordinate."""
        return self._x

    @x.setter
    def x(self, value):
        """Set the X coordinate."""
        if not value and value != 0:
            val = None
        else:
            try:
                val = int(value)
            except (ValueError, TypeError):
                return
        if self._x != val:
            self._x = val
            self._mark_dirty()
            
            if self._knot_editable:
                self._autofill_pith_coordinates()

    @Property(object)
    def pith_z(self):
        """Get the Pith Z coordinate."""
        return self._pith_z

    @pith_z.setter
    def pith_z(self, value):
        """Set the Pith Z coordinate."""
        try:
            val = None if not value and value != 0 else int(value)
            if self._pith_z != val:
                self._pith_z = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(object)
    def pith_y(self):
        """Get the Pith Y coordinate."""
        return self._pith_y

    @pith_y.setter
    def pith_y(self, value):
        """Set the Pith Y coordinate."""
        try:
            val = None if not value and value != 0 else int(value)
            if self._pith_y != val:
                self._pith_y = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(bool)
    def is_pruned_knot(self) -> bool:
        """Get whether this knot has a pruned knot."""
        return self._is_pruned_knot

    @is_pruned_knot.setter
    def is_pruned_knot(self, value: bool):
        """Set whether knot is pruned."""
        if self._is_pruned_knot != value:
            if not self._current_knot_no and not self._knot_editable:
                # Discard the change visually and don't save
                self.knot_error.emit("Nessun nodo selezionato!")
                self.knot_data_changed.emit()
                return

            self._is_pruned_knot = value
            self.knot_data_changed.emit()
            self._mark_dirty()

    @Property(object)
    def pruned_z1(self):
        return self._pruned_z1

    @pruned_z1.setter
    def pruned_z1(self, value):
        try:
            val = None if not value and value != 0 else int(value)
            if self._pruned_z1 != val:
                self._pruned_z1 = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(object)
    def pruned_y1(self):
        return self._pruned_y1

    @pruned_y1.setter
    def pruned_y1(self, value):
        try:
            val = None if not value and value != 0 else int(value)
            if self._pruned_y1 != val:
                self._pruned_y1 = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(object)
    def pruned_z2(self):
        return self._pruned_z2

    @pruned_z2.setter
    def pruned_z2(self, value):
        try:
            val = None if not value and value != 0 else int(value)
            if self._pruned_z2 != val:
                self._pruned_z2 = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(object)
    def pruned_y2(self):
        return self._pruned_y2

    @pruned_y2.setter
    def pruned_y2(self, value):
        try:
            val = None if not value and value != 0 else int(value)
            if self._pruned_y2 != val:
                self._pruned_y2 = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

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

    @Property(object)
    def side1_z1(self):
        return self._side1_z1

    @side1_z1.setter
    def side1_z1(self, value):
        try:
            val = None if value == "" or value is None else int(value)
            if self._side1_z1 != val:
                self._side1_z1 = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(object)
    def side1_z2(self):
        return self._side1_z2

    @side1_z2.setter
    def side1_z2(self, value):
        try:
            val = None if value == "" or value is None else int(value)
            if self._side1_z2 != val:
                self._side1_z2 = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(object)
    def side1_dmin(self):
        return self._side1_dmin

    @side1_dmin.setter
    def side1_dmin(self, value):
        try:
            val = None if value == "" or value is None else int(value)
            if self._side1_dmin != val:
                self._side1_dmin = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(object)
    def side2_z1(self):
        return self._side2_z1

    @side2_z1.setter
    def side2_z1(self, value):
        try:
            val = None if value == "" or value is None else int(value)
            if self._side2_z1 != val:
                self._side2_z1 = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(object)
    def side2_z2(self):
        return self._side2_z2

    @side2_z2.setter
    def side2_z2(self, value):
        try:
            val = None if value == "" or value is None else int(value)
            if self._side2_z2 != val:
                self._side2_z2 = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(object)
    def side2_dmin(self):
        return self._side2_dmin

    @side2_dmin.setter
    def side2_dmin(self, value):
        try:
            val = None if value == "" or value is None else int(value)
            if self._side2_dmin != val:
                self._side2_dmin = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(object)
    def side3_z1(self):
        return self._side3_z1

    @side3_z1.setter
    def side3_z1(self, value):
        try:
            val = None if value == "" or value is None else int(value)
            if self._side3_z1 != val:
                self._side3_z1 = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(object)
    def side3_z2(self):
        return self._side3_z2

    @side3_z2.setter
    def side3_z2(self, value):
        try:
            val = None if value == "" or value is None else int(value)
            if self._side3_z2 != val:
                self._side3_z2 = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(object)
    def side3_dmin(self):
        return self._side3_dmin

    @side3_dmin.setter
    def side3_dmin(self, value):
        try:
            val = None if value == "" or value is None else int(value)
            if self._side3_dmin != val:
                self._side3_dmin = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(object)
    def side4_z1(self):
        return self._side4_z1

    @side4_z1.setter
    def side4_z1(self, value):
        try:
            val = None if value == "" or value is None else int(value)
            if self._side4_z1 != val:
                self._side4_z1 = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(object)
    def side4_z2(self):
        return self._side4_z2

    @side4_z2.setter
    def side4_z2(self, value):
        try:
            val = None if value == "" or value is None else int(value)
            if self._side4_z2 != val:
                self._side4_z2 = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    @Property(object)
    def side4_dmin(self):
        return self._side4_dmin

    @side4_dmin.setter
    def side4_dmin(self, value):
        try:
            val = None if value == "" or value is None else int(value)
            if self._side4_dmin != val:
                self._side4_dmin = val
                self._mark_dirty()
        except (ValueError, TypeError):
            pass

    # ==================== SLOTS ====================

    @Slot(str)
    def handle_project_changed(self, project_name: str):
        """Track current project."""
        self._current_project = project_name
        self._current_board = ""
        self._knots = []
        self.knots_changed.emit(self.knot_list)
        
        self._current_knot_no = ""
        self._clear_fields()
        self.current_knot_changed.emit("")

    @Slot(str)
    def handle_board_changed(self, board_no: str):
        """Update current board and load its knots."""
        board_exists = False
        if board_no and self._current_project and self.board_repo:
            try:
                board = self.board_repo.get_board_by_id(board_no, self._current_project)
                board_exists = board is not None
            except Exception:
                pass
                
        if not board_exists:
            board_no = ""
            
        self._current_board = board_no
        self._knot_editable = False
        self._current_knot_no = ""  # Force setter to trigger
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
                self._current_knot_no = ""
                self._clear_fields()
                self.current_knot_changed.emit("")
        except LocalKnotError as e:
            self.knot_error.emit(str(e))
        except Exception as e:
            self.knot_error.emit(f"Failed to load knots: {str(e)}")

    @Slot()
    def reload_knots(self):
        """Reload knots for the current board without losing current selection."""
        if not self._current_board or not self._current_project:
            return
            
        try:
            self._knots = self.repo.get_all_knots(self._current_board, self._current_project)
            self.knots_changed.emit(self.knot_list)
            
            # Reload currently selected knot data
            if self._current_knot_no:
                # We save it because handle_knot_selected might otherwise think it's the same and skip
                knot_to_load = self._current_knot_no
                self._current_knot_no = ""
                self.handle_knot_selected(knot_to_load)
        except Exception as e:
            self.knot_error.emit(f"Failed to reload knots: {str(e)}")

    @Slot()
    def handle_new_knot(self):
        """Prepare UI for new knot creation with auto-assigned ID."""
        self.hide_messages.emit()
        self._knot_editable = True
        self.knot_editable_changed.emit(True)

        # Auto-assign next sequential ID
        if self._knots:
            valid_ids = [int(k.knot_no) for k in self._knots if k.knot_no and str(k.knot_no).isdigit()]
            next_id = max(valid_ids) + 1 if valid_ids else 1
        else:
            next_id = 1
        self._current_knot_no = str(next_id)
        self.current_knot_changed.emit(self._current_knot_no)

        self._clear_fields()

    def _clear_fields(self):
        """Helper to reset all data fields to default."""

        self._x = None
        self._pith_z = None
        self._pith_y = None
        self._is_pruned_knot = False
        self._pruned_z1 = None
        self._pruned_y1 = None
        self._pruned_z2 = None
        self._pruned_y2 = None
        self._comment = ""
        self._side1_z1 = None
        self._side1_z2 = None
        self._side1_dmin = None
        self._side2_z1 = None
        self._side2_z2 = None
        self._side2_dmin = None
        self._side3_z1 = None
        self._side3_z2 = None
        self._side3_dmin = None
        self._side4_z1 = None
        self._side4_z2 = None
        self._side4_dmin = None
        self.knot_data_changed.emit()

    @Slot()
    def handle_save_knot(self):
        """Validate and save knot data."""
        self.hide_messages.emit()

        if not self._current_project or not self._current_board:
            self.knot_error.emit("No project or board selected!")
            return

        knot_text = str(self._current_knot_no).strip()
        if not knot_text:
            self.knot_error.emit("Please press 'New' before saving a knot!")
            return

        # Check > 0 condition for new knots
        invalid_fields_local = []
        error_messages_local = []
        
        if self._knot_editable:
            if self._x is None or self._x <= 0: 
                invalid_fields_local.append("X")
                error_messages_local.append("Field X must be greater than 0.")
                
        # Ensure at least 2 sides, or 1 side + pith/pruned
        compiled_sides = 0
        empty_side_fields = []
        for side in range(1, 5):
            z1 = getattr(self, f'_side{side}_z1')
            z2 = getattr(self, f'_side{side}_z2')
            dmin = getattr(self, f'_side{side}_dmin')
            if z1 is not None or z2 is not None or dmin is not None:
                compiled_sides += 1
            else:
                empty_side_fields.extend([f'side{side}_z1', f'side{side}_z2', f'side{side}_dmin'])

        has_pith_pruned = False
        if self._is_pruned_knot:
            if self._pruned_z1 is not None or self._pruned_y1 is not None or self._pruned_z2 is not None or self._pruned_y2 is not None:
                has_pith_pruned = True
        else:
            if self._pith_z is not None or self._pith_y is not None:
                has_pith_pruned = True

        valid_sides = (compiled_sides >= 2) or (compiled_sides >= 1 and has_pith_pruned)
        if not valid_sides:
            invalid_fields_local.extend(empty_side_fields)
            error_messages_local.append("Insert knot's coordinates first.")

        if self._is_pruned_knot:
            if (self._pruned_z1 is None and self._pruned_y1 is not None) or (self._pruned_z1 is not None and self._pruned_y1 is None):
                if self._pruned_z1 is None and "pith_z" not in invalid_fields_local: invalid_fields_local.append("pith_z")
                if self._pruned_y1 is None and "pith_y" not in invalid_fields_local: invalid_fields_local.append("pith_y")
                error_messages_local.append("Both Pruned Z1 and Pruned Y1 must be compiled if one is provided.")
                
            if (self._pruned_z2 is None and self._pruned_y2 is not None) or (self._pruned_z2 is not None and self._pruned_y2 is None):
                if self._pruned_z2 is None and "pruned_z2" not in invalid_fields_local: invalid_fields_local.append("pruned_z2")
                if self._pruned_y2 is None and "pruned_y2" not in invalid_fields_local: invalid_fields_local.append("pruned_y2")
                error_messages_local.append("Both Pruned Z2 and Pruned Y2 must be compiled if one is provided.")
        else:
            if (self._pith_z is None and self._pith_y is not None) or (self._pith_z is not None and self._pith_y is None):
                if self._pith_z is None and "pith_z" not in invalid_fields_local: invalid_fields_local.append("pith_z")
                if self._pith_y is None and "pith_y" not in invalid_fields_local: invalid_fields_local.append("pith_y")
                error_messages_local.append("Both Pith Z and Pith Y must be compiled if one is provided.")

        if invalid_fields_local:
            self.knot_error.emit("\n".join(error_messages_local))
            self.validation_failed.emit(invalid_fields_local)
            
            vb_fields = [f for f in invalid_fields_local if f.startswith('side')]
            if vb_fields:
                self.virtual_board_error.emit("Insert knot's coordinates first.")
            return

        board = None
        if self.board_repo:
            try:
                board = self.board_repo.get_board_by_id(self._current_board, self._current_project)
            except Exception:
                pass
                
        board_height = board.height if board else float('inf')
        board_base = board.base if board else float('inf')
        board_length = board.length if board else float('inf')

        # Check pith/pruned is inside the board
        if self._is_pruned_knot:
            check_z, check_y, name = self._pruned_z1, self._pruned_y1, "Pruned Z1/Y1"
            if self._pruned_z2 is not None and self._pruned_z2 >= board_height:
                self.knot_error.emit(f"Pruned Z2 ({self._pruned_z2}) must be less than board height ({board_height}).")
                self.validation_failed.emit(["pruned_z2"])
                return
            if self._pruned_y2 is not None and self._pruned_y2 >= board_base:
                self.knot_error.emit(f"Pruned Y2 ({self._pruned_y2}) must be less than board base ({board_base}).")
                self.validation_failed.emit(["pruned_y2"])
                return
        else:
            check_z, check_y, name = self._pith_z, self._pith_y, "Pith"

        if check_z is not None and check_z >= board_height:
            self.knot_error.emit(f"{name} Z ({check_z}) must be less than board height ({board_height}).")
            self.validation_failed.emit(["pith_z"])
            return
        if check_y is not None and check_y >= board_base:
            self.knot_error.emit(f"{name} Y ({check_y}) must be less than board base ({board_base}).")
            self.validation_failed.emit(["pith_y"])
            return

        # Check X <= length for all knots
        if self._x > board_length:
            self.knot_error.emit(f"Position X ({self._x}) cannot exceed board length ({board_length}).")
            self.validation_failed.emit(["X"])
            return
        
        invalid_fields = []
        error_msgs = []
        for side in range(1, 5):
            side_name = str(side)
            z1 = getattr(self, f'_side{side}_z1')
            z2 = getattr(self, f'_side{side}_z2')
            dmin = getattr(self, f'_side{side}_dmin')
            
            if z1 is not None or z2 is not None or dmin is not None:
                # If any field is compiled, all must be compiled for that side
                if z1 is None or z2 is None or dmin is None:
                    if z1 is None and f'side{side}_z1' not in invalid_fields: invalid_fields.append(f'side{side}_z1')
                    if z2 is None and f'side{side}_z2' not in invalid_fields: invalid_fields.append(f'side{side}_z2')
                    if dmin is None and f'side{side}_dmin' not in invalid_fields: invalid_fields.append(f'side{side}_dmin')
                    error_msgs.append(f"Side {side_name}: incomplete data. All 3 fields must be filled.")
                    continue
                
                if z1 < 0:
                    if f'side{side}_z1' not in invalid_fields: invalid_fields.append(f'side{side}_z1')
                    error_msgs.append(f"Side {side_name}: z1 must be >= 0")

                if z1 >= z2:
                    if f'side{side}_z1' not in invalid_fields: invalid_fields.append(f'side{side}_z1')
                    if f'side{side}_z2' not in invalid_fields: invalid_fields.append(f'side{side}_z2')
                    error_msgs.append(f"Side {side_name}: z1 must be < z2 (got z1={z1}, z2={z2})")
                    continue  # dmin and bounds checks depend on a valid interval, skip them
                
                if dmin <= 0:
                    if f'side{side}_dmin' not in invalid_fields: invalid_fields.append(f'side{side}_dmin')
                    error_msgs.append(f"Side {side_name}: dmin must be > 0")
                        
                if dmin > (z2 - z1):
                    if f'side{side}_dmin' not in invalid_fields: invalid_fields.append(f'side{side}_dmin')
                    error_msgs.append(f"Side {side_name}: dmin must be <= (z2 - z1)")
                    
                if side in (1, 3) and z2 > board_height:
                    if f'side{side}_z2' not in invalid_fields: invalid_fields.append(f'side{side}_z2')
                    error_msgs.append(f"Side {side_name}: z2 ({z2}) exceeds board height ({board_height})")
                elif side in (2, 4) and z2 > board_base:
                    if f'side{side}_z2' not in invalid_fields: invalid_fields.append(f'side{side}_z2')
                    error_msgs.append(f"Side {side_name}: z2 ({z2}) exceeds board base ({board_base})")
                    
        # Corner validation rules
        if self._side1_z2 == board_height and self._side4_z1 is not None and self._side4_z1 != 0:
            if 'side4_z1' not in invalid_fields: invalid_fields.append('side4_z1')
            error_msgs.append("Corner Rule (Top-Left): If Side 1 reaches the corner (z2=height), Side 4 must start at 0.")
        if self._side4_z1 == 0 and self._side1_z2 is not None and self._side1_z2 != board_height:
            if 'side1_z2' not in invalid_fields: invalid_fields.append('side1_z2')
            error_msgs.append("Corner Rule (Top-Left): If Side 4 starts at 0, Side 1 must reach the corner (z2=height).")
            
        if self._side4_z2 == board_base and self._side3_z1 is not None and self._side3_z1 != 0:
            if 'side3_z1' not in invalid_fields: invalid_fields.append('side3_z1')
            error_msgs.append("Corner Rule (Bottom-Left): If Side 4 reaches the corner (z2=base), Side 3 must start at 0.")
        if self._side3_z1 == 0 and self._side4_z2 is not None and self._side4_z2 != board_base:
            if 'side4_z2' not in invalid_fields: invalid_fields.append('side4_z2')
            error_msgs.append("Corner Rule (Bottom-Left): If Side 3 starts at 0, Side 4 must reach the corner (z2=base).")
            
        if self._side3_z2 == board_height and self._side2_z1 is not None and self._side2_z1 != 0:
            if 'side2_z1' not in invalid_fields: invalid_fields.append('side2_z1')
            error_msgs.append("Corner Rule (Bottom-Right): If Side 3 reaches the corner (z2=height), Side 2 must start at 0.")
        if self._side2_z1 == 0 and self._side3_z2 is not None and self._side3_z2 != board_height:
            if 'side3_z2' not in invalid_fields: invalid_fields.append('side3_z2')
            error_msgs.append("Corner Rule (Bottom-Right): If Side 2 starts at 0, Side 3 must reach the corner (z2=height).")
            
        if self._side2_z2 == board_base and self._side1_z1 is not None and self._side1_z1 != 0:
            if 'side1_z1' not in invalid_fields: invalid_fields.append('side1_z1')
            error_msgs.append("Corner Rule (Top-Right): If Side 2 reaches the corner (z2=base), Side 1 must start at 0.")
        if self._side1_z1 == 0 and self._side2_z2 is not None and self._side2_z2 != board_base:
            if 'side2_z2' not in invalid_fields: invalid_fields.append('side2_z2')
            error_msgs.append("Corner Rule (Top-Right): If Side 1 starts at 0, Side 2 must reach the corner (z2=base).")
                    
        if invalid_fields:
            self.validation_failed.emit(invalid_fields)
            
            panel_fields = [f for f in invalid_fields if not f.startswith('side')]
            vb_fields = [f for f in invalid_fields if f.startswith('side')]
            
            if panel_fields:
                self.knot_error.emit('Field X must be greater than 0.')
            if vb_fields:
                # Limit to 3 messages to avoid UI breaking, add "..." if more
                if len(error_msgs) > 3:
                    error_text = '\n'.join(error_msgs[:3]) + '\n... and other errors.'
                else:
                    error_text = '\n'.join(error_msgs)
                self.virtual_board_error.emit(error_text)
            return

        try:
            # Overwrite the unselected coordinate pair to None
            if self._is_pruned_knot:
                self._pith_z = None
                self._pith_y = None
            else:
                self._pruned_z1 = None
                self._pruned_y1 = None
                self._pruned_z2 = None
                self._pruned_y2 = None
            knot = Knot(
                knot_no=knot_text,
                x=self._x,
                pith_z=self._pith_z,
                pith_y=self._pith_y,
                is_pruned_knot=self._is_pruned_knot,
                pruned_z1=self._pruned_z1,
                pruned_y1=self._pruned_y1,
                pruned_z2=self._pruned_z2,
                pruned_y2=self._pruned_y2,
                comment=self._comment,
                side1_z1=self._side1_z1, side1_z2=self._side1_z2, side1_dmin=self._side1_dmin,
                side2_z1=self._side2_z1, side2_z2=self._side2_z2, side2_dmin=self._side2_dmin,
                side3_z1=self._side3_z1, side3_z2=self._side3_z2, side3_dmin=self._side3_dmin,
                side4_z1=self._side4_z1, side4_z2=self._side4_z2, side4_dmin=self._side4_dmin
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
                if self.repo.update_knot(knot, self._current_board, self._current_project):
                    for idx, k in enumerate(self._knots):
                        if str(k.knot_no) == knot_text:
                            self._knots[idx] = knot
                            break
                    self.knot_saved.emit(f"Knot {self._current_knot_no} updated!")
                    self.save_enabled_changed.emit(False)
        except LocalKnotError as e:
            self.knot_error.emit(str(e))
        except Exception as e:
            self.knot_error.emit(f"Failed to save: {str(e)}")

    @Slot()
    def handle_delete_knot(self):
        """Delete the currently selected knot and renumber higher IDs."""
        self.hide_messages.emit()
        
        if not self._current_project or not self._current_board:
            self.knot_error.emit("No project or board selected!")
            return

        if not self._current_knot_no:
            self.knot_error.emit("No knot selected!")
            return

        try:
            deleted_id = int(self._current_knot_no)
            if self.repo.delete_knot(self._current_knot_no, self._current_board, self._current_project):
                # Remove from in-memory list
                self._knots = [k for k in self._knots if str(k.knot_no) != self._current_knot_no]

                # Decrement IDs of all knots that had a higher ID than the deleted one.
                # Must process in ascending order to avoid ID collisions during rename.
                knots_to_renumber = sorted(
                    [k for k in self._knots if int(k.knot_no) > deleted_id],
                    key=lambda k: int(k.knot_no)
                )
                for k in knots_to_renumber:
                    old_id = str(k.knot_no)
                    new_id = str(int(k.knot_no) - 1)
                    self.repo.rename_knot_id(old_id, new_id, self._current_board, self._current_project)
                    k.knot_no = new_id

                self.knots_changed.emit(self.knot_list)

                if self._knots:
                    self.current_knot_no = str(self._knots[0].knot_no)
                else:
                    self._current_knot_no = ""
                    self._clear_fields()
                    self.current_knot_changed.emit("")
        except LocalKnotError as e:
            self.knot_error.emit(str(e))
        except Exception as e:
            self.knot_error.emit(f"Failed to delete: {str(e)}")

    @Slot(str)
    def handle_knot_selected(self, knot_no: str):
        """Load knot data when selected."""
        if not knot_no:
            self._current_knot_no = ""
            self._clear_fields()
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
                self._is_pruned_knot = knot.is_pruned_knot
                self._pruned_z1 = knot.pruned_z1
                self._pruned_y1 = knot.pruned_y1
                self._pruned_z2 = knot.pruned_z2
                self._pruned_y2 = knot.pruned_y2
                self._comment = knot.comment
                self._side1_z1 = knot.side1_z1
                self._side1_z2 = knot.side1_z2
                self._side1_dmin = knot.side1_dmin
                self._side2_z1 = knot.side2_z1
                self._side2_z2 = knot.side2_z2
                self._side2_dmin = knot.side2_dmin
                self._side3_z1 = knot.side3_z1
                self._side3_z2 = knot.side3_z2
                self._side3_dmin = knot.side3_dmin
                self._side4_z1 = knot.side4_z1
                self._side4_z2 = knot.side4_z2
                self._side4_dmin = knot.side4_dmin
                self.knot_data_changed.emit()
                self.knot_selected.emit(knot_no)
                self.save_enabled_changed.emit(False)
        except LocalKnotError as e:
            self.knot_error.emit(str(e))
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
                self._is_pruned_knot = knot.is_pruned_knot
                self._pruned_z1 = knot.pruned_z1
                self._pruned_y1 = knot.pruned_y1
                self._pruned_z2 = knot.pruned_z2
                self._pruned_y2 = knot.pruned_y2
                self._comment = knot.comment
                self._side1_z1 = knot.side1_z1
                self._side1_z2 = knot.side1_z2
                self._side1_dmin = knot.side1_dmin
                self._side2_z1 = knot.side2_z1
                self._side2_z2 = knot.side2_z2
                self._side2_dmin = knot.side2_dmin
                self._side3_z1 = knot.side3_z1
                self._side3_z2 = knot.side3_z2
                self._side3_dmin = knot.side3_dmin
                self._side4_z1 = knot.side4_z1
                self._side4_z2 = knot.side4_z2
                self._side4_dmin = knot.side4_dmin
                return True
            return False
        except Exception:
            return False

    def _autofill_pith_coordinates(self):
        """Auto-fill pith_z and pith_y based on nearest knot within +-150mm."""
        if not self._knots:
            return

        closest_knot = None
        min_dist = float('inf')

        for k in self._knots:
            if k.pith_z is None or k.pith_y is None:
                continue
                
            dist = abs(k.x - self._x)
            if dist <= 150:
                if dist < min_dist:
                    min_dist = dist
                    closest_knot = k

        if closest_knot:
            self._pith_z = closest_knot.pith_z
            self._pith_y = closest_knot.pith_y
        else:
            self._pith_z = None
            self._pith_y = None
            
        self.knot_data_changed.emit()
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
