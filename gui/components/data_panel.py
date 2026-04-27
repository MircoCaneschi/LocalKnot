from PySide6.QtWidgets import QWidget, QHBoxLayout, QGroupBox


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

        # 2. Board Group
        self.board_group = QGroupBox("Board")

        # 3. Knots Group
        self.knots_group = QGroupBox("Knots")

        layout.addWidget(self.projects_group)
        layout.addWidget(self.board_group)
        layout.addWidget(self.knots_group)