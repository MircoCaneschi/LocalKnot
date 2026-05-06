from PySide6.QtWidgets import QWidget, QHBoxLayout, QGroupBox, QSizePolicy
from gui.components.data_panel.boards import BoardsGui
from gui.components.data_panel.knots import KnotsGui
from gui.components.data_panel.projects import ProjectsGui


class DataPanelWidget(QWidget):
    """Top panel containing input controls."""

    def __init__(self):
        super().__init__()
        self.projects_gui=None
        self.boards_gui=None
        self.knots_gui=None
        self._setup_ui()

    def _setup_ui(self):
        # Horizontal layout to align the three groups
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 1. Projects Group
        self.projects_gui = ProjectsGui()
        self.projects_group = QGroupBox("Projects")
        self.projects_group.setLayout(self.projects_gui.main_layout)

        # 2. Board Group
        self.boards_gui = BoardsGui()
        self.board_group = QGroupBox(f"Boards[{self.boards_gui.board_no}]")
        self.board_group.setLayout(self.boards_gui.main_layout)

        # 3. Knots Group
        self.knots_gui = KnotsGui()
        self.knots_group = QGroupBox(f"Knots[{self.knots_gui.knot_no}]")
        self.knots_group.setLayout(self.knots_gui.main_layout)

        layout.addWidget(self.projects_group, 1)
        layout.addWidget(self.board_group, 1)
        layout.addWidget(self.knots_group, 1)


class HiddenDataPanelWidget(QWidget):
    #this class is used when the data panel is collapsed, to show a minimalistic version of it

    def __init__(self):
        super().__init__()
        self._setup_hidden_ui()

    def _setup_hidden_ui(self):
            # Horizontal layout to align the three groups
            hidden_layout = QHBoxLayout(self)
            hidden_layout.setContentsMargins(0, 0, 0, 0)

            # 1. Projects Group
            self.projects_gui = ProjectsGui()
            self.hidden_projects_group = QGroupBox("Projects")
            self.hidden_projects_group.setLayout(self.projects_gui.hidden_main_layout)

            # 2. Board Group
            self.boards_gui = BoardsGui()
            self.hidden_board_group = QGroupBox(f"Boards[{self.boards_gui.board_no}]")
            self.hidden_board_group.setLayout(self.boards_gui.hidden_main_layout)

            # 3. Knots Group
            self.knots_gui = KnotsGui()
            self.hidden_knots_group = QGroupBox(f"Knots[{self.knots_gui.knot_no}]")
            self.hidden_knots_group.setLayout(self.knots_gui.hidden_main_layout)

            hidden_layout.addWidget(self.hidden_projects_group, 1)
            hidden_layout.addWidget(self.hidden_board_group, 1)
            hidden_layout.addWidget(self.hidden_knots_group, 1)