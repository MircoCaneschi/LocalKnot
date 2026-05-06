import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """Application entry point."""
    app = QApplication(sys.argv)

    # esperimento, fa cagare non considerare
    stile_globale = """
        QMainWindow {
            background-color: #301E96;
        }
        QGroupBox {
            background-color: #42AAC2;
            color: #7D2727;
            border-radius: 10px;
            padding: 10px, 0;
            
        }
        QPushButton {
            background-color: #9D63E0;
            color: white;
            padding: 5px;
            border-radius: 10px;
        }
         QPushButton:hover {
            color: yellow;
        }
        QPushButton:pressed {
                background-color: #21618c;
                padding-left: 7px; /* Slight movement effect */
                padding-top: 7px;
        }
        QLabel {
            color: #7D2727;
        }
    """
    app.setStyleSheet(stile_globale)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()