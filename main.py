"""
MVVM Architecture Application Entry Point.

This is the main entry point for the LocalKnot application.
It creates a QApplication, applies styling, and launches MainWindow.

MainWindow handles all MVVM component initialization:
- Database setup (DatabaseManager)
- Repository creation (ProjectRepository, BoardRepository, KnotRepository)
- ViewModel instantiation (ProjectsViewModel, BoardsViewModel, KnotsViewModel)
- View creation and Signal/Slot binding (ProjectsView, BoardsView, KnotsView)
"""

import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Application entry point - MVVM Architecture."""
    app = QApplication(sys.argv)

    # Apply global stylesheet
    stylesheet = """
        QMainWindow {
            background-color: #F59D67;
        }
        QGroupBox {
            background-color: #BD8142;
            color: #824300;
            border-radius: 10px;
            padding: 10px;
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
            padding-left: 7px;
            padding-top: 7px;
        }
        QPushButton:disabled {
            background-color: #A06A33;
            color: #D3A87C;
        }
        QLabel {
            color: #824300;
        }
    """
    app.setStyleSheet(stylesheet)

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()