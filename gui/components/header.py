import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt

class HeaderWidget(QWidget):
    """
    Main application header.
    Contains the logo, application name, and space for future elements.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        logo_label = QLabel()
        # Resolve the absolute path to the imgs directory 
        # (components is inside gui, which is inside root)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        img_path = os.path.join(project_root, "imgs", "Blu.png")
        
        logo_pixmap = QPixmap(img_path)
        if not logo_pixmap.isNull():
            # Scale it to a larger header height
            logo_label.setPixmap(logo_pixmap.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation))
        
        title_label = QLabel("LocalKnot")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Center the title and keep logo on the left
        layout.addWidget(logo_label)
        layout.addStretch(1)
        layout.addWidget(title_label, alignment=Qt.AlignCenter)
        layout.addStretch(1)
