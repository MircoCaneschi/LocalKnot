from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QGraphicsView, QGraphicsScene, QLineEdit, QLabel, QFormLayout,
    QGroupBox, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator

from mvvm.viewmodels.virtual_board_vm import VirtualBoardViewModel
from mvvm.viewmodels.knots_viewmodel import KnotsViewModel

class VirtualBoardView(QWidget):
    """
    Interactive graphical interface for viewing and inputting
    data for the board and the current knot.
    Contains a QGraphicsView in the center and 12 LineEdits on the sides.
    """
    def __init__(self, view_model: VirtualBoardViewModel, knots_vm: KnotsViewModel = None):
        super().__init__()
        self.view_model = view_model
        self.knots_vm = knots_vm
        
        self.setup_ui()
        self.bind_view_model()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'scene') and hasattr(self, 'graphics_view'):
            if self.scene.sceneRect().isValid():
                self.graphics_view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # --- GRAPHICS GRID AND INPUT ---
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Validator to accept only integers
        validator = QIntValidator()
        self.inputs = {}

        # Helper function to create a group of 3 line edits (z1, z2, dmin)
        def create_side_inputs(side_name, orientation="horizontal"):
            container = QWidget()
            container.setObjectName("SideInputContainer")
            
            group_inputs = {}
            
            # Extract side number from name e.g. "side1_top" -> "Side 1:"
            side_num = side_name.split("_")[0].replace("side", "")
            side_label = QLabel(f"<b>Side {side_num}:</b>")
            side_label.setObjectName("VirtualBoardSideLabel")
            
            if orientation == "horizontal":
                outer = QHBoxLayout(container)
                outer.setContentsMargins(5, 3, 5, 3)
                outer.setSpacing(2)
                outer.addWidget(side_label, alignment=Qt.AlignmentFlag.AlignHCenter)
                
                layout = QHBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                for field in ["z1", "z2", "dmin"]:
                    form = QFormLayout()
                    form.setContentsMargins(0, 0, 0, 0)
                    line_edit = QLineEdit()
                    line_edit.setValidator(validator)
                    line_edit.setMaximumWidth(60)
                    form.addRow(f"{field}:", line_edit)
                    layout.addLayout(form)
                    group_inputs[field] = line_edit
                outer.addLayout(layout)
            else:
                outer = QVBoxLayout(container)
                outer.setContentsMargins(5, 3, 5, 3)
                outer.setSpacing(2)
                outer.addWidget(side_label, alignment=Qt.AlignmentFlag.AlignHCenter)
                
                layout = QFormLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
                for field in ["z1", "z2", "dmin"]:
                    line_edit = QLineEdit()
                    line_edit.setValidator(validator)
                    line_edit.setMaximumWidth(60)
                    layout.addRow(f"{field}:", line_edit)
                    group_inputs[field] = line_edit
                outer.addLayout(layout)
                    
            self.inputs[side_name] = group_inputs
            return container


        # Creation of the 4 sides
        top_widget = create_side_inputs("side1_top", "horizontal")
        right_widget = create_side_inputs("side2_right", "vertical")
        bottom_widget = create_side_inputs("side3_bottom", "horizontal")
        left_widget = create_side_inputs("side4_left", "vertical")

        # Center: QGraphicsView
        self.scene = QGraphicsScene()
        self.graphics_view = QGraphicsView(self.scene)
        self.graphics_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.graphics_view.setMinimumSize(400, 400)

        # Positioning in the grid
        # row 0: empty, top, empty
        # row 1: left, center, right
        # row 2: empty, bottom, empty
        grid_layout.addWidget(top_widget, 0, 1, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        grid_layout.addWidget(left_widget, 1, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid_layout.addWidget(self.graphics_view, 1, 1)
        grid_layout.addWidget(right_widget, 1, 2, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        grid_layout.addWidget(bottom_widget, 2, 1, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Set stretches to ensure the graphics view gets all available extra space
        grid_layout.setRowStretch(0, 0)
        grid_layout.setRowStretch(1, 1)
        grid_layout.setRowStretch(2, 0)
        
        grid_layout.setColumnStretch(0, 0)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(2, 0)

        # Error Message Label (Prominent Banner at the top)
        self.error_msg = QLabel()
        self.error_msg.setObjectName("VirtualBoardErrorMsg")
        self.error_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_msg.setWordWrap(True)
        self.error_msg.hide()
        
        main_layout.addWidget(self.error_msg)
        main_layout.addLayout(grid_layout, stretch=1)


    def bind_view_model(self):
        # We will connect the view_model signals to the line edits and graphics here
        if not self.knots_vm:
            return

        # 1. View -> ViewModel: When user types, update ViewModel property
        def connect_input_to_vm(field_name: str, line_edit: QLineEdit):
            line_edit.textEdited.connect(lambda text: setattr(self.knots_vm, field_name, text))

        for side, group in self.inputs.items():
            # side e.g. "side1_top" -> prefix "side1"
            prefix = side.split("_")[0] 
            for field, le in group.items():
                prop_name = f"{prefix}_{field}" # e.g. "side1_z1"
                connect_input_to_vm(prop_name, le)

        # 2. ViewModel -> View: When node data loads, update UI
        def update_ui_from_vm():
            for side, group in self.inputs.items():
                prefix = side.split("_")[0]
                for field, le in group.items():
                    prop_name = f"{prefix}_{field}"
                    val = getattr(self.knots_vm, prop_name, None)
                    
                    # Block signals so setting text doesn't trigger textEdited -> _mark_dirty
                    le.blockSignals(True)
                    le.setText(str(val) if val is not None else "")
                    le.blockSignals(False)

        self.knots_vm.knot_data_changed.connect(update_ui_from_vm)
        self.knots_vm.knot_data_changed.connect(self._redraw_board)
        self.knots_vm.validation_failed.connect(self._on_validation_failed)
        self.knots_vm.virtual_board_error.connect(self._on_virtual_board_error)
        self.knots_vm.hide_messages.connect(self.error_msg.hide)

        # Initial sync
        update_ui_from_vm()
        self._redraw_board()

    def _redraw_board(self):
        from PySide6.QtGui import QPen, QBrush, QColor, QPolygonF, QFont
        from PySide6.QtCore import QPointF, Qt
        
        self.scene.clear()
        
        if not self.knots_vm or not self.knots_vm._current_board or not self.knots_vm.board_repo:
            return
            
        try:
            board = self.knots_vm.board_repo.get_board_by_id(
                self.knots_vm._current_board, 
                self.knots_vm._current_project
            )
        except Exception:
            return
            
        if not board:
            return
            
        base = getattr(board, 'base', 0)
        hight = getattr(board, 'height', 0)
        
        if base <= 0 or hight <= 0:
            return
            
        # The sceneRect is now dynamically calculated at the end of the drawing
        # to include the board and all arrows.
        
        # Cosmetic pen for borders (remains thin at any zoom level)
        board_pen = QPen(Qt.black, 1.5)
        board_pen.setCosmetic(True)
        
        # Drawing the board section
        board_rect = self.scene.addRect(0, 0, hight, base, board_pen, QBrush(QColor(240, 230, 210)))

        # Vertical dashed lines at quarters (1/4 and 3/4 of the width, which represents the board's height)
        quarter_pen = QPen(QColor(0, 0, 0, 60), 2)
        quarter_pen.setStyle(Qt.DashLine)
        quarter_pen.setCosmetic(True)
        
        self.scene.addLine(hight / 4, 0, hight / 4, base, quarter_pen)
        self.scene.addLine(3 * hight / 4, 0, 3 * hight / 4, base, quarter_pen)

        # ── Coordinate-convention arrows ──────────────────────────────────────
        # Drawn always (when a board exists), outside the board rect, parallel
        # to each side, pointing in the direction of increasing z.
        #
        # Side 1 (top,    y=0):     z grows right→left  (hight → 0)
        # Side 2 (right,  x=hight): z grows bottom→top  (base  → 0)
        # Side 3 (bottom, y=base):  z grows left→right  (0     → hight)
        # Side 4 (left,   x=0):     z grows top→bottom  (0     → base)

        _arrow_pen = QPen(QColor(50, 100, 200), 3)
        _arrow_pen.setCosmetic(True)
        _arrow_color = QColor(50, 100, 200)
        _gap = min(hight, base) * 0.06  # proportional distance to avoid overlaps at different zoom levels

        # Fixed arrowhead size regardless of which side / arrow length
        _head_len = min(hight, base) * 0.035
        _head_wide = _head_len * 0.50

        def _draw_arrow(x1, y1, x2, y2):
            import math
            dx, dy = x2 - x1, y2 - y1
            length = math.hypot(dx, dy)
            if length == 0:
                return
            ux, uy = dx / length, dy / length   # unit vector (tail → tip)
            px, py = -uy, ux                    # perpendicular

            tip = QPointF(x2, y2)
            # Tail ends just before the arrowhead base
            tail_end = QPointF(x2 - ux * _head_len, y2 - uy * _head_len)
            self.scene.addLine(x1, y1, tail_end.x(), tail_end.y(), _arrow_pen)

            bm = tail_end
            lp = QPointF(bm.x() + px * _head_wide, bm.y() + py * _head_wide)
            rp = QPointF(bm.x() - px * _head_wide, bm.y() - py * _head_wide)
            self.scene.addPolygon(QPolygonF([tip, lp, rp]), _arrow_pen, QBrush(_arrow_color))

        _al = min(hight, base) * 0.20   # fixed length for all blue arrows (20% of min side)

        # Side 1 – above top edge (y=0), arrow points left
        _draw_arrow(hight, -_gap, hight - _al, -_gap)

        # Side 2 – right edge (x=hight), arrow points up
        _draw_arrow(hight + _gap, base, hight + _gap, base - _al)

        # Side 3 – below bottom edge (y=base), arrow points right
        _draw_arrow(0, base + _gap, _al, base + _gap)

        # Side 4 – left edge (x=0), arrow points down
        _draw_arrow(-_gap, 0, -_gap, _al)

        # ── Side Numbers (1, 2, 3, 4) ─────────────────────────────────────────
        _num_gap = min(hight, base) * 0.09
        
        def _draw_side_number(cx, cy, text):
            r = min(hight, base) * 0.055
            pen = QPen(QColor(50, 50, 50), 1.5)
            pen.setCosmetic(True)
            circle = self.scene.addEllipse(cx - r, cy - r, 2 * r, 2 * r, pen, QBrush(QColor(245, 245, 245)))
            circle.setZValue(8)
            
            lbl = self.scene.addSimpleText(text)
            font = QFont("Arial", 100)
            font.setBold(True)
            lbl.setFont(font)
            lbl.setBrush(QBrush(QColor(30, 30, 30)))
            lbl.setZValue(9)
            
            br = lbl.boundingRect()
            target_h = r * 1.45
            scale = target_h / br.height() if br.height() > 0 else 1
            lbl.setScale(scale)
            lbl.setPos(cx - (br.width() * scale) / 2, cy - (br.height() * scale) / 2)

        _draw_side_number(hight / 2, -_num_gap, "1")
        _draw_side_number(hight + _num_gap, base / 2, "2")
        _draw_side_number(hight / 2, base + _num_gap, "3")
        _draw_side_number(-_num_gap, base / 2, "4")

        # ── Pith coordinate system indicator ──────────────────────────────────
        # Two red arrows anchored at the bottom-right corner of the board:
        #   horizontal (← left)  → pith_z is measured from the right edge
        #   vertical   (↑ up)    → pith_y is measured from the bottom edge
        _pith_ax_len   = min(hight, base) * 0.20
        _pith_head_len = _pith_ax_len * 0.18
        _pith_head_w   = _pith_head_len * 0.5
        _pith_pen      = QPen(QColor(200, 0, 0), 2)
        _pith_pen.setCosmetic(True)
        _pith_color    = QColor(200, 0, 0)

        def _draw_pith_axis(x1, y1, x2, y2, label, lbl_x, lbl_y, rotation=0):
            import math
            dx, dy = x2 - x1, y2 - y1
            length = math.hypot(dx, dy)
            if length == 0:
                return
            ux, uy = dx / length, dy / length
            px, py = -uy, ux
            tip      = QPointF(x2, y2)
            tail_end = QPointF(x2 - ux * _pith_head_len, y2 - uy * _pith_head_len)
            line = self.scene.addLine(x1, y1, tail_end.x(), tail_end.y(), _pith_pen)
            line.setZValue(7)
            bm = tail_end
            lp   = QPointF(bm.x() + px * _pith_head_w, bm.y() + py * _pith_head_w)
            rp   = QPointF(bm.x() - px * _pith_head_w, bm.y() - py * _pith_head_w)
            head = self.scene.addPolygon(QPolygonF([tip, lp, rp]), _pith_pen, QBrush(_pith_color))
            head.setZValue(7)
            lbl = self.scene.addSimpleText(label)
            lbl.setBrush(QBrush(_pith_color))
            font = QFont()
            font.setPixelSize(12)
            lbl.setFont(font)
            lbl.setFlag(lbl.GraphicsItemFlag.ItemIgnoresTransformations, True)
            lbl.setPos(lbl_x, lbl_y)
            lbl.setRotation(rotation)
            lbl.setZValue(9)

        # offset the pith origin outward along the bisector to avoid overlapping blue arrows
        _ox = hight + _gap * 2.5
        _oy = base + _gap * 2.5
        _dist = 1  # Distanza ridotta per tenere il testo più vicino alla freccia
        
        # Horizontal arrow → left (pith_z); label just below midpoint
        _draw_pith_axis(
            _ox, _oy,
            _ox - _pith_ax_len, _oy,
            "pith_z",
            _ox - _pith_ax_len * 0.75, _oy + _dist,
        )
        # Vertical arrow → up (pith_y); label to the right of the arrow, rotated -90
        _draw_pith_axis(
            _ox, _oy,
            _ox, _oy - _pith_ax_len,
            "pith_y",
            _ox + _dist, _oy - _pith_ax_len * 0.25,
            rotation=-90
        )

        vm = self.knots_vm


        # Coordinate conversion: X = hight - z, Y = base - y
        def map_x(z): return hight - z
        def map_y(y): return base - y

        def build_knot_shape(knot_obj):
            """Compute (border_points, pith_point) for any object with sideX_z1/z2 attributes."""
            faces_data = [
                (1, knot_obj.side1_z1, knot_obj.side1_z2),
                (2, knot_obj.side2_z1, knot_obj.side2_z2),
                (3, knot_obj.side3_z1, knot_obj.side3_z2),
                (4, knot_obj.side4_z1, knot_obj.side4_z2),
            ]
            points_on_faces = []
            for face, z1, z2 in faces_data:
                if z1 is not None and z2 is not None:
                    p1 = p2 = None
                    if face == 1:
                        p1 = QPointF(map_x(z1), 0)
                        p2 = QPointF(map_x(z2), 0)
                    elif face == 2:
                        p1 = QPointF(hight, map_y(z1))
                        p2 = QPointF(hight, map_y(z2))
                    elif face == 3:
                        p1 = QPointF(z1, base)
                        p2 = QPointF(z2, base)
                    elif face == 4:
                        p1 = QPointF(0, z1)
                        p2 = QPointF(0, z2)
                    if p1 is not None and p2 is not None:
                        points_on_faces.append((face, p1, p2))

            if not points_on_faces:
                return None, None

            def get_perimeter_param(pt):
                x, y = pt.x(), pt.y()
                if abs(y - 0) < 0.1:       return x
                elif abs(x - hight) < 0.1: return hight + y
                elif abs(y - base) < 0.1:  return hight + base + (hight - x)
                elif abs(x - 0) < 0.1:     return hight + base + hight + (base - y)
                return 0

            all_border_pts = []
            for _, p1, p2 in points_on_faces:
                all_border_pts.extend([p1, p2])
            all_border_pts.sort(key=get_perimeter_param)

            unique_border_pts = []
            for pt in all_border_pts:
                if not unique_border_pts or (
                    abs(unique_border_pts[-1].x() - pt.x()) > 0.1
                    or abs(unique_border_pts[-1].y() - pt.y()) > 0.1
                ):
                    unique_border_pts.append(pt)

            is_pruned = getattr(knot_obj, 'is_pruned_knot', False)
            pith_points = []
            if is_pruned:
                z1 = getattr(knot_obj, 'pruned_z1', None)
                y1 = getattr(knot_obj, 'pruned_y1', None)
                z2 = getattr(knot_obj, 'pruned_z2', None)
                y2 = getattr(knot_obj, 'pruned_y2', None)
                if z1 is not None and y1 is not None and z1 > 0 and y1 > 0:
                    pith_points.append(QPointF(map_x(z1), map_y(y1)))
                if z2 is not None and y2 is not None and z2 > 0 and y2 > 0:
                    pith_points.append(QPointF(map_x(z2), map_y(y2)))
            else:
                pith_z = getattr(knot_obj, 'pith_z', None)
                pith_y = getattr(knot_obj, 'pith_y', None)
                if pith_z is not None and pith_y is not None and pith_z > 0 and pith_y > 0:
                    pith_points.append(QPointF(map_x(pith_z), map_y(pith_y)))

            return unique_border_pts, pith_points

        def draw_knot_shape(knot_obj, brush, pen, pith_pen, pith_brush, z_value,
                            label=None, label_color=None):
            """Draw a knot cross-section on the scene with the given styling."""
            border_pts, pith_points = build_knot_shape(knot_obj)
            if border_pts is None:
                return

            if pith_points:
                if len(border_pts) >= 2:
                    poly = QPolygonF(pith_points + border_pts)
                    item = self.scene.addPolygon(poly, pen, brush)
                    item.setZValue(z_value)
                    
                if len(pith_points) == 2:
                    p_line = self.scene.addLine(
                        pith_points[0].x(), pith_points[0].y(),
                        pith_points[1].x(), pith_points[1].y(),
                        pith_pen
                    )
                    p_line.setZValue(z_value + 1)

                for pt in pith_points:
                    pith_item = self.scene.addEllipse(-3, -3, 6, 6, pith_pen, pith_brush)
                    pith_item.setPos(pt)
                    pith_item.setFlag(pith_item.GraphicsItemFlag.ItemIgnoresTransformations, True)
                    pith_item.setZValue(z_value + 2)
            else:
                if len(border_pts) >= 3:
                    poly = QPolygonF(border_pts)
                    item = self.scene.addPolygon(poly, pen, brush)
                    item.setZValue(z_value)

            # Knot number label — fixed pixel size so it's always legible at any zoom
            if label and border_pts:
                cx = sum(p.x() for p in border_pts) / len(border_pts)
                cy = sum(p.y() for p in border_pts) / len(border_pts)
                text_item = self.scene.addSimpleText(label)
                if label_color:
                    text_item.setBrush(QBrush(label_color))
                font = QFont()
                font.setPixelSize(12)
                font.setBold(True)
                text_item.setFont(font)
                text_item.setFlag(text_item.GraphicsItemFlag.ItemIgnoresTransformations, True)
                text_item.setPos(cx, cy)
                text_item.setZValue(z_value + 2)

        # ── Neighboring knots (within ±150 mm along X) ───────────────────────
        current_knot_no = vm._current_knot_no
        try:
            current_x = int(vm._x) if vm._x is not None else None
        except (TypeError, ValueError):
            current_x = None

        neighbor_brush      = QBrush(QColor(139, 69, 19, 60))
        neighbor_pen        = QPen(QColor(101, 67, 33, 130), 1.0)
        neighbor_pen.setCosmetic(True)
        neighbor_pith_pen   = QPen(QColor(200, 0, 0, 130), 1)
        neighbor_pith_pen.setCosmetic(True)
        neighbor_pith_brush = QBrush(QColor(255, 0, 0, 100))

        if current_x is not None:
            for knot in vm._knots:
                if str(knot.knot_no) == str(current_knot_no):
                    continue
                try:
                    kx = int(knot.x) if knot.x is not None else None
                except (TypeError, ValueError):
                    kx = None
                if kx is not None and abs(kx - current_x) <= 150:
                    draw_knot_shape(
                        knot,
                        brush=neighbor_brush,
                        pen=neighbor_pen,
                        pith_pen=neighbor_pith_pen,
                        pith_brush=neighbor_pith_brush,
                        z_value=1,
                        label=f"#{knot.knot_no}",
                        label_color=QColor(80, 40, 10, 180),
                    )

        # ── Selected knot (prominent, drawn on top) ────────────────────────
        has_knot_data = any(z2 is not None for z2 in [
            vm.side1_z2, vm.side2_z2, vm.side3_z2, vm.side4_z2
        ])

        if has_knot_data:
            # Lightweight proxy to reuse draw_knot_shape with VM properties
            class _KnotProxy:
                pass
            proxy = _KnotProxy()
            proxy.side1_z1 = vm.side1_z1; proxy.side1_z2 = vm.side1_z2
            proxy.side2_z1 = vm.side2_z1; proxy.side2_z2 = vm.side2_z2
            proxy.side3_z1 = vm.side3_z1; proxy.side3_z2 = vm.side3_z2
            proxy.side4_z1 = vm.side4_z1; proxy.side4_z2 = vm.side4_z2
            proxy.pith_z   = vm.pith_z
            proxy.pith_y   = vm.pith_y
            proxy.is_pruned_knot = vm.is_pruned_knot
            proxy.pruned_z1 = vm.pruned_z1
            proxy.pruned_y1 = vm.pruned_y1
            proxy.pruned_z2 = vm.pruned_z2
            proxy.pruned_y2 = vm.pruned_y2

            selected_brush      = QBrush(QColor(139, 69, 19, 210))
            selected_pen        = QPen(QColor(80, 40, 10), 2.0)
            selected_pen.setCosmetic(True)
            selected_pith_pen   = QPen(Qt.red, 1)
            selected_pith_pen.setCosmetic(True)
            selected_pith_brush = QBrush(Qt.red)

            draw_knot_shape(
                proxy,
                brush=selected_brush,
                pen=selected_pen,
                pith_pen=selected_pith_pen,
                pith_brush=selected_pith_brush,
                z_value=5,
                label=f"#{current_knot_no}",
                label_color=QColor(40, 10, 0),
            )

        # Calculate the total bounding rectangle (blue arrows at -_gap, red arrows at _ox, _oy)
        # Add a proportional margin of 10% to comfortably include text
        pad = max(hight, base) * 0.10
        min_x = -_gap - pad
        min_y = -_gap - pad
        max_x = _ox + pad
        max_y = _oy + pad
        self.scene.setSceneRect(min_x, min_y, max_x - min_x, max_y - min_y)
        
        # Force the view to resize to fit the available space
        self.graphics_view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def _on_virtual_board_error(self, msg: str):
        """Show error message and flash it."""
        from PySide6.QtCore import QVariantAnimation, QAbstractAnimation
        from PySide6.QtGui import QColor

        self.error_msg.setText(msg)
        self.error_msg.show()

        anim = QVariantAnimation(self.error_msg)
        anim.setDuration(300)
        anim.setStartValue(QColor("red"))
        # we interpolate to a transparent color to simulate blinking
        anim.setEndValue(QColor(0, 0, 0, 0)) 
        anim.setLoopCount(3)
        
        if not hasattr(self, '_animations'):
            self._animations = []
        self._animations.append(anim)
        anim.finished.connect(lambda a=anim: self._animations.remove(a) if a in self._animations else None)
        anim.finished.connect(lambda: self.error_msg.setStyleSheet(""))
        anim.valueChanged.connect(lambda color: self.error_msg.setStyleSheet(
            f"color: {color.name()}; border-color: {color.name()};"
        ))
        anim.start(QAbstractAnimation.DeleteWhenStopped)

    def _on_validation_failed(self, invalid_fields: list):
        """Flash the specific line edits if they failed validation."""
        from PySide6.QtCore import QVariantAnimation, QAbstractAnimation
        from PySide6.QtGui import QColor

        def _flash_widget(widget):
            if not widget: return
            anim = QVariantAnimation(widget)
            anim.setDuration(300)
            anim.setStartValue(QColor("red"))
            anim.setEndValue(widget.palette().color(widget.foregroundRole()))
            anim.setLoopCount(3)
            
            if not hasattr(self, '_animations'):
                self._animations = []
            self._animations.append(anim)
            anim.finished.connect(lambda a=anim: self._animations.remove(a) if a in self._animations else None)
            anim.finished.connect(lambda w=widget: w.setStyleSheet(""))
            anim.valueChanged.connect(lambda color, w=widget: w.setStyleSheet(f"color: {color.name()};"))
            anim.start(QAbstractAnimation.DeleteWhenStopped)

        for side, group in self.inputs.items():
            prefix = side.split("_")[0]
            for field, le in group.items():
                prop_name = f"{prefix}_{field}"
