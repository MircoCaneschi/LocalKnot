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
import os
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream, QIODevice
from gui.main_window import MainWindow
import resources_rc

def main():
    """Application entry point - MVVM Architecture."""
    app = QApplication(sys.argv)

    # Apply global stylesheet from resources
    qss_file = QFile(":/styles/style.qss")
    if qss_file.open(QIODevice.ReadOnly | QIODevice.Text):
        stream = QTextStream(qss_file)
        app.setStyleSheet(stream.readAll())
        qss_file.close()

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()