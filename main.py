import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from controllers.data_panel_controller import ProjectsController, BoardsController, KnotsController
from gui.main_window import MainWindow


def main():
    """Application entry point."""
    app = QApplication(sys.argv)

    # esperimento, fa cagare non considerare
    stile_globale = """
        QMainWindow {
            background-color: #734F28;
        }
        QGroupBox {
            background-color: #BD8142;
            color: #663F18;
            border-radius: 10px;
            padding: 10px, 0;
            
        }
        QPushButton {
            background-color: #824300;
            color: white;
            padding: 5px;
            border-radius: 10px;
        }
         QPushButton:hover {
            color: yellow;
        }
        QPushButton:pressed {
                background-color: #A85C0A;
                padding-left: 7px; /* Slight movement effect */
                padding-top: 7px;
        }
        QLabel {
            color: #663F18;
        }
    """
    app.setStyleSheet(stile_globale)

    window = MainWindow()

    # Instantiate the controllers
    projects_controller = ProjectsController(window.data_panel, window.hidden_data_panel)
    boards_controller = BoardsController(window.data_panel, window.hidden_data_panel)
    knots_controller = KnotsController(window.data_panel, window.hidden_data_panel)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()