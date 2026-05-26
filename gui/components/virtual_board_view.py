from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QGraphicsView, QGraphicsScene, QLineEdit, QLabel, QFormLayout,
    QGroupBox, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator

from mvvm.viewmodels.virtual_board_vm import VirtualBoardViewModel

class VirtualBoardView(QWidget):
    """
    Interactive graphical interface for viewing and inputting
    data for the board and the current knot.
    Contains a QGraphicsView in the center and 12 LineEdits on the sides.
    """
    def __init__(self, view_model: VirtualBoardViewModel):
        super().__init__()
        self.view_model = view_model
        
        self.setup_ui()
        self.bind_view_model()
        
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
            layout = QHBoxLayout(container) if orientation == "horizontal" else QVBoxLayout(container)
            layout.setContentsMargins(5, 5, 5, 5)
            
            group_inputs = {}
            for field in ["z1", "z2", "dmin"]:
                form = QFormLayout()
                form.setContentsMargins(0, 0, 0, 0)
                line_edit = QLineEdit()
                line_edit.setValidator(validator)
                line_edit.setMaximumWidth(60)
                form.addRow(f"{field}:", line_edit)
                layout.addLayout(form)
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
        grid_layout.addWidget(top_widget, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        grid_layout.addWidget(left_widget, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        grid_layout.addWidget(self.graphics_view, 1, 1)
        grid_layout.addWidget(right_widget, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        grid_layout.addWidget(bottom_widget, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addLayout(grid_layout, stretch=1)


    def bind_view_model(self):
        # We will connect the view_model signals to the line edits and graphics here
        pass
