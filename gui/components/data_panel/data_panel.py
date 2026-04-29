from PySide6.QtWidgets import QWidget, QHBoxLayout, QGroupBox, QSizePolicy
from gui.components import data_panel
from gui.components.data_panel.projects import MainWidgetProjects


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
        self.projects_group = QGroupBox("Projects")
        self.projects_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.projects_group.setLayout(MainWidgetProjects().main_layout)

        # 2. Board Group
        self.board_group = QGroupBox("Board")
        self.board_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.board_group.setLayout(MainWidgetProjects().main_layout)

        # 3. Knots Group
        self.knots_group = QGroupBox("Knots")
        self.knots_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.knots_group.setLayout(MainWidgetProjects().main_layout)

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
            self.hidden_projects_group = QGroupBox("Projects")
            self.hidden_projects_group.setLayout(MainWidgetProjects().hidden_main_layout)

            # 2. Board Group
            self.hidden_board_group = QGroupBox("Board")
            self.hidden_board_group.setLayout(MainWidgetProjects().hidden_main_layout)

            # 3. Knots Group
            self.hidden_knots_group = QGroupBox("Knots")
            self.hidden_knots_group.setLayout(MainWidgetProjects().hidden_main_layout)

            hidden_layout.addWidget(self.hidden_projects_group, 1)
            hidden_layout.addWidget(self.hidden_board_group, 1)
            hidden_layout.addWidget(self.hidden_knots_group, 1)