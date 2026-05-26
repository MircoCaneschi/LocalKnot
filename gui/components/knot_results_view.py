from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QGroupBox, QLabel, QFrame, QStyle
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPixmap

class FlaredTabButton(QPushButton):
    """A custom button that draws an outward-flared tab shape at the top."""
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        w = self.width()
        h = self.height()
        r = 10  # bottom inward radius
        f = 12  # top outward flare radius
        
        path.moveTo(0, 0)
        # Top-left outward curve
        path.quadTo(f, 0, f, f)
        # Left straight edge
        path.lineTo(f, h - r)
        # Bottom-left inward curve
        path.quadTo(f, h, f + r, h)
        # Bottom straight edge
        path.lineTo(w - f - r, h)
        # Bottom-right inward curve
        path.quadTo(w - f, h, w - f, h - r)
        # Right straight edge
        path.lineTo(w - f, f)
        # Top-right outward curve
        path.quadTo(w - f, 0, w, 0)
        # Close path
        path.lineTo(0, 0)
        
        if self.isDown():
            color = QColor("#A85C0A")
        elif self.underMouse():
            color = QColor("#A85C0A")
        else:
            color = QColor("#824300")
            
        painter.fillPath(path, color)
        
        # Draw the text and icon vertically stacked
        painter.setPen(QColor(Qt.GlobalColor.white))
        font_metrics = painter.fontMetrics()
        text_rect = font_metrics.boundingRect(self.text())
        
        icon = self.icon()
        icon_size = self.iconSize()
        if not icon_size.isValid() or icon_size.width() == 0:
            icon_size = QSize(16, 16)
            
        spacing = 4
        total_height = text_rect.height() + icon_size.height() + spacing
        start_y = (h - total_height) // 2
        
        icon_x = (w - icon_size.width()) // 2
        text_x = (w - text_rect.width()) // 2
        
        # Tint icon to pure white
        pixmap = icon.pixmap(icon_size)
        if not pixmap.isNull():
            tinted = QPixmap(pixmap.size())
            tinted.fill(Qt.GlobalColor.transparent)
            p2 = QPainter(tinted)
            p2.drawPixmap(0, 0, pixmap)
            p2.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            p2.fillRect(tinted.rect(), QColor(Qt.GlobalColor.white))
            p2.end()
            pixmap = tinted
            
        if "Show" in self.text():
            # Text above, icon below
            text_y = start_y + font_metrics.ascent()
            painter.drawText(text_x, text_y, self.text())
            icon_y = start_y + text_rect.height() + spacing
            if not pixmap.isNull():
                painter.drawPixmap(icon_x, icon_y, pixmap)
        else:
            # Icon above, text below
            icon_y = start_y
            if not pixmap.isNull():
                painter.drawPixmap(icon_x, icon_y, pixmap)
            text_y = start_y + icon_size.height() + spacing + font_metrics.ascent()
            painter.drawText(text_x, text_y, self.text())

    def sizeHint(self):
        # Provide a reasonable default size for the vertical layout
        return QSize(160, 45)

from mvvm.viewmodels.virtual_board_vm import VirtualBoardViewModel

class KnotResultsView(QWidget):
    """
    View component to display the calculated parameters of the knot.
    Can be expanded/collapsed.
    """
    def __init__(self, view_model: VirtualBoardViewModel):
        super().__init__()
        self.view_model = view_model
        
        self.setup_ui()
        self.bind_view_model()
        
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0) # No spacing between divider and button
        
        # Horizontal divider line
        self.divider = QFrame()
        self.divider.setObjectName("ResultsDivider")
        main_layout.addWidget(self.divider)
        
        # Group with data (initially hidden)
        self.results_group = QGroupBox("Knot Parameters")
        group_layout = QGridLayout(self.results_group)
        
        # Create placeholder labels for results
        self.result_labels = {}
        parameters = ["tKnot", "mKnot", "tKAR", "mKAR_L", "mKAR_R", "mKAR", "DEB", "DAB", "DEK", "EEB", "EAB"]
        
        row, col = 0, 0
        for param in parameters:
            name_lbl = QLabel(f"<b>{param}:</b>")
            val_lbl = QLabel("-")
            
            form = QHBoxLayout()
            form.addWidget(name_lbl)
            form.addWidget(val_lbl)
            form.addStretch()
            
            group_layout.addLayout(form, row, col)
            self.result_labels[param] = val_lbl
            
            col += 1
            if col > 5:  # 6 columns to not make it too tall
                col = 0
                row += 1
                
        main_layout.addWidget(self.results_group)
        self.results_group.hide()  # Hide at startup
        
        # Button layout to center it and make it narrow
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.addStretch()
        
        # Button to show/hide results
        self.toggle_results_btn = FlaredTabButton("Show parameters\n")
        self.toggle_results_btn.setObjectName("ResultsToggleBtn")
        self.toggle_results_btn.setFixedWidth(160)
        icon_down = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarUnshadeButton)
        self.toggle_results_btn.setIcon(icon_down)
        self.toggle_results_btn.clicked.connect(self._toggle_results)
        
        btn_layout.addWidget(self.toggle_results_btn)
        btn_layout.addStretch()
        
        main_layout.addLayout(btn_layout)
        


    def _toggle_results(self):
        """Shows or hides the results panel."""
        if self.results_group.isVisible():
            self.results_group.hide()
            self.toggle_results_btn.setText("Show parameters")
            icon_down = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarUnshadeButton)
            self.toggle_results_btn.setIcon(icon_down)
        else:
            self.results_group.show()
            self.toggle_results_btn.setText("Hide parameters")
            icon_up = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarShadeButton)
            self.toggle_results_btn.setIcon(icon_up)

    def bind_view_model(self):
        # Connect the view_model signal to update the labels
        # self.view_model.results_updated.connect(self._update_results)
        pass
        
    def _update_results(self, results_dict):
        """Updates the labels with calculated results."""
        for param, val in results_dict.items():
            if param in self.result_labels:
                self.result_labels[param].setText(str(val))
