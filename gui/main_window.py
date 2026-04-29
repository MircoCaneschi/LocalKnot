from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                               QPushButton, QGraphicsView, QGraphicsScene,
                               QSizePolicy)
from gui.components.data_panel.data_panel import DataPanelWidget, HiddenDataPanelWidget


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LocalKnot")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout
        self.main_layout = QVBoxLayout(central_widget)

        # Button to toggle the data panel visibility
        self.toggle_panel_btn = QPushButton("Toggle Data Panel")
        self.toggle_panel_btn.clicked.connect(self._toggle_data_panel)
        self.main_layout.addWidget(self.toggle_panel_btn)

        # Instantiate and insert the data panel
        self.data_panel = DataPanelWidget()
        self.main_layout.addWidget(self.data_panel)

        #Instantiate and insert the hidden data panel
        self.hidden_data_panel = HiddenDataPanelWidget()
        self.main_layout.addWidget(self.hidden_data_panel)
        self.hidden_data_panel.hide()

        # Instantiate and insert the graphics area
        self.scene = QGraphicsScene()
        self.graphics_view = QGraphicsView(self.scene)

        # Force the view to expand
        self.graphics_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.main_layout.addWidget(self.graphics_view)

        self.showMaximized()


    def _toggle_data_panel(self):
        """Manages the visibility of the top data panel."""
        if self.data_panel.isVisible():
            self.data_panel.hide()
            self.hidden_data_panel.show()
        else:
            self.hidden_data_panel.hide()
            self.data_panel.show()
