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
            
            if orientation == "horizontal":
                layout = QHBoxLayout(container)
                layout.setContentsMargins(5, 5, 5, 5)
                for field in ["z1", "z2", "dmin"]:
                    form = QFormLayout()
                    form.setContentsMargins(0, 0, 0, 0)
                    line_edit = QLineEdit()
                    line_edit.setValidator(validator)
                    line_edit.setMaximumWidth(60)
                    form.addRow(f"{field}:", line_edit)
                    layout.addLayout(form)
                    group_inputs[field] = line_edit
            else:
                layout = QFormLayout(container)
                layout.setContentsMargins(5, 5, 5, 5)
                # Align labels to the right so they stick close to the line edits
                layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
                for field in ["z1", "z2", "dmin"]:
                    line_edit = QLineEdit()
                    line_edit.setValidator(validator)
                    line_edit.setMaximumWidth(60)
                    layout.addRow(f"{field}:", line_edit)
                    group_inputs[field] = line_edit
                    
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

        # Error Message Label (Prominent Banner at the top)
        self.error_msg = QLabel()
        self.error_msg.setStyleSheet(
            "color: #d32f2f; "
            "font-weight: bold; "
            "font-size: 13px; "
            "background-color: #ffebee; "
            "padding: 8px; "
            "border-radius: 4px; "
            "border: 1px solid #ffcdd2;"
        )
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
        from PySide6.QtGui import QPen, QBrush, QColor, QPolygonF
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
            
        margin = 5
        # Lasciamo spazio verticale per il disegno longitudinale (es. 1.3x base invece di 2.5x)
        self.scene.setSceneRect(-margin, -margin, hight + 2*margin, base * 1.3 + 2*margin)
        
        # Penna cosmetica per i bordi (rimane sottile a qualsiasi livello di zoom)
        board_pen = QPen(Qt.black, 1.5)
        board_pen.setCosmetic(True)
        
        # Disegno della sezione della tavola
        board_rect = self.scene.addRect(0, 0, hight, base, board_pen, QBrush(QColor(240, 230, 210)))
        
        vm = self.knots_vm
        pith_z = vm.pith_z
        pith_y = vm.pith_y
        
        # Conversione coordinate: X = hight - z, Y = base - y
        def map_x(z): return hight - z
        def map_y(y): return base - y
        
        faces_data = [
            (1, vm.side1_z1, vm.side1_z2),
            (2, vm.side2_z1, vm.side2_z2),
            (3, vm.side3_z1, vm.side3_z2),
            (4, vm.side4_z1, vm.side4_z2),
        ]
        
        has_knot_data = any(z2 is not None for _, z1, z2 in faces_data)
        if not has_knot_data:
            return
            
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
                
                if p1 and p2:
                    points_on_faces.append((face, p1, p2))
                
        if not points_on_faces:
            return
            
        knot_brush = QBrush(QColor(139, 69, 19, 180)) # Colore legno scuro semitrasparente
        knot_pen = QPen(QColor(101, 67, 33), 1.5)
        knot_pen.setCosmetic(True) # Evita che i bordi del nodo diventino giganti con lo zoom
        
        has_pith = (pith_z is not None and pith_z > 0) or (pith_y is not None and pith_y > 0)
        
        if has_pith and pith_z is not None and pith_y is not None:
            pith_point = QPointF(map_x(pith_z), map_y(pith_y))
            # Disegna il punto del midollo in modo che mantenga dimensione fissa su schermo
            pith_pen = QPen(Qt.red, 1)
            pith_pen.setCosmetic(True)
            pith_item = self.scene.addEllipse(-3, -3, 6, 6, pith_pen, QBrush(Qt.red))
            pith_item.setPos(pith_point)
            pith_item.setFlag(pith_item.GraphicsItemFlag.ItemIgnoresTransformations, True)
            pith_item.setZValue(10) # Assicuriamoci che stia sempre sopra ai poligoni
            
            # Genera i poligoni che uniscono le facce al midollo
            for face, p1, p2 in points_on_faces:
                poly = QPolygonF([pith_point, p1, p2])
                self.scene.addPolygon(poly, knot_pen, knot_brush)
        else:
            # Senza midollo: Uniamo i punti delle facce calcolando il loro ordinamento sul perimetro
            def get_perimeter_param(pt):
                x, y = pt.x(), pt.y()
                if abs(y - 0) < 0.1: return x
                elif abs(x - hight) < 0.1: return hight + y
                elif abs(y - base) < 0.1: return hight + base + (hight - x)
                elif abs(x - 0) < 0.1: return hight + base + hight + (base - y)
                return 0

            all_points = []
            for _, p1, p2 in points_on_faces:
                all_points.extend([p1, p2])
                
            all_points.sort(key=get_perimeter_param)
            
            unique_points = []
            for pt in all_points:
                if not unique_points or (abs(unique_points[-1].x() - pt.x()) > 0.1 or abs(unique_points[-1].y() - pt.y()) > 0.1):
                    unique_points.append(pt)
                    
            if len(unique_points) >= 3:
                poly = QPolygonF(unique_points)
                self.scene.addPolygon(poly, knot_pen, knot_brush)
                
        # Forza il ridimensionamento della vista per farla fittare nello spazio a disposizione
        if self.scene.sceneRect().isValid():
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
        anim.finished.connect(lambda: self.error_msg.setStyleSheet(
            "color: #d32f2f; font-weight: bold; font-size: 13px; "
            "background-color: #ffebee; padding: 8px; border-radius: 4px; border: 1px solid #ffcdd2;"
        ))
        anim.valueChanged.connect(lambda color: self.error_msg.setStyleSheet(
            f"color: {color.name()}; font-weight: bold; font-size: 13px; "
            f"background-color: #ffebee; padding: 8px; border-radius: 4px; border: 1px solid {color.name()};"
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
                if prop_name in invalid_fields:
                    _flash_widget(le)
