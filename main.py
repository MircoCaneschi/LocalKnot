import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """Application entry point."""
    app = QApplication(sys.argv)

    # esperimento, fa cagare non considerare
    stile_globale = """
        QMainWindow {
            background-color: #E39998;
        }
        QPushButton {
            background-color: #F25050;
            color: white;
            padding: 5px;
            border-radius: 10px;
        }
        QLabel {
            color: #7D2727;
            font-size: 12px;
        }
    """
    app.setStyleSheet(stile_globale)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()