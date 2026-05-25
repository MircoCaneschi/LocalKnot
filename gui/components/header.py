from PySide6.QtWidgets import QWidget, QLabel, QGridLayout
from PySide6.QtGui import QPixmap
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
        layout = QGridLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)
        
        logo_label = QLabel()
        # Load from Qt Resources system
        logo_pixmap = QPixmap(":/imgs/Blu.png")
        if not logo_pixmap.isNull():
            # Scale it to a larger header height
            logo_label.setPixmap(logo_pixmap.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation))
        
        title_label = QLabel("LocalKnot")
        # Assign ObjectName to be styled via QSS
        title_label.setObjectName("HeaderTitle")
        
        # Center the title perfectly and keep logo on the left
        layout.addWidget(logo_label, 0, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(title_label, 0, 0, alignment=Qt.AlignCenter)
