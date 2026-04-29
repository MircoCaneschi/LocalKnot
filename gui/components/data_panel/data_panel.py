from PySide6.QtWidgets import QWidget, QHBoxLayout, QGroupBox, QSizePolicy
from gui.components import data_panel
from gui.components.data_panel.boards import BoardsGui
from gui.components.data_panel.knots import KnotsGui
from gui.components.data_panel.projects import ProjectsGui


class DataPanelWidget(QWidget):
    """Top panel containing input controls."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        # Horizontal layout to align the three groups
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 1. Projects Group
        projects_gui = ProjectsGui()
        self.projects_group = QGroupBox("Projects")
        self.projects_group.setLayout(projects_gui.main_layout)

        # 2. Board Group
        boards_gui = BoardsGui()
        self.board_group = QGroupBox(f"Boards[{boards_gui.board_no}]")
        self.board_group.setLayout(boards_gui.main_layout)

        # 3. Knots Group
        knots_gui = KnotsGui()
        self.knots_group = QGroupBox("Knots")
        self.knots_group.setLayout(knots_gui.main_layout)

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
            projects_gui = ProjectsGui()
            self.hidden_projects_group = QGroupBox("Projects")
            self.hidden_projects_group.setLayout(projects_gui.hidden_main_layout)

            # 2. Board Group
            boards_gui = BoardsGui()
            self.hidden_board_group = QGroupBox(f"Boards[{boards_gui.board_no}]")
            self.hidden_board_group.setLayout(boards_gui.hidden_main_layout)

            # 3. Knots Group
            knots_gui = KnotsGui()
            self.hidden_knots_group = QGroupBox("Knots")
            self.hidden_knots_group.setLayout(knots_gui.hidden_main_layout)

            hidden_layout.addWidget(self.hidden_projects_group, 1)
            hidden_layout.addWidget(self.hidden_board_group, 1)
            hidden_layout.addWidget(self.hidden_knots_group, 1)