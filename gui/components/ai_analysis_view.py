from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QGraphicsView, QGraphicsScene, QFileDialog, QFrame, 
                               QInputDialog, QMessageBox, QDialog, QTabWidget, QFormLayout, QLineEdit, QDialogButtonBox,
                               QProgressBar)
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QColor, QPolygonF, QBrush, QPainter, QPixmap, QImage
import os
import cv2
import numpy as np

from mvvm.viewmodels.ai_analysis_vm import AiAnalysisViewModel

from PySide6.QtGui import QIntValidator

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, scene=None, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        
    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            zoom_in_factor = 1.15
            zoom_out_factor = 1 / zoom_in_factor
            if event.angleDelta().y() > 0:
                self.scale(zoom_in_factor, zoom_in_factor)
            else:
                self.scale(zoom_out_factor, zoom_out_factor)
        else:
            super().wheelEvent(event)

class SingleFaceKnotDialog(QDialog):
    def __init__(self, board=None, knot_data=None, face_id=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Single Face Knot")
        
        layout = QVBoxLayout(self)
        
        # Board dimensions info
        info_text = "Unknown Board Data"
        if board:
            info_text = f"Reference values - Base: {board.base} | Height: {board.height}"
            
        if knot_data and face_id is not None:
            k_x = knot_data.get('x', '?')
            z1 = knot_data.get(f'side{face_id}_z1', '?')
            z2 = knot_data.get(f'side{face_id}_z2', '?')
            dmin = knot_data.get(f'side{face_id}_dmin', '?')
            info_text += f"\nDetected segment - X: {k_x} | Z1: {z1} | Z2: {z2} | Dmin: {dmin}"
            
        info_label = QLabel(info_text)
        info_label.setStyleSheet("font-weight: bold; color: #555;")
        layout.addWidget(info_label)
        
        self.tabs = QTabWidget()
        
        # Setup integer validator
        int_validator = QIntValidator(0, 99999)
        
        # Tab Pruned
        self.tab_pruned = QWidget()
        pruned_layout = QFormLayout(self.tab_pruned)
        self.pruned_z1 = QLineEdit(); self.pruned_z1.setValidator(int_validator)
        self.pruned_y1 = QLineEdit(); self.pruned_y1.setValidator(int_validator)
        self.pruned_z2 = QLineEdit(); self.pruned_z2.setValidator(int_validator)
        self.pruned_y2 = QLineEdit(); self.pruned_y2.setValidator(int_validator)
        pruned_layout.addRow("Z1:", self.pruned_z1)
        pruned_layout.addRow("Y1:", self.pruned_y1)
        pruned_layout.addRow("Z2:", self.pruned_z2)
        pruned_layout.addRow("Y2:", self.pruned_y2)
        self.tabs.addTab(self.tab_pruned, "Pruned")
        
        # Tab Pith
        self.tab_pith = QWidget()
        pith_layout = QFormLayout(self.tab_pith)
        self.pith_z = QLineEdit(); self.pith_z.setValidator(int_validator)
        self.pith_y = QLineEdit(); self.pith_y.setValidator(int_validator)
        pith_layout.addRow("Z:", self.pith_z)
        pith_layout.addRow("Y:", self.pith_y)
        self.tabs.addTab(self.tab_pith, "Pith")
        
        layout.addWidget(self.tabs)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_data(self):
        def parse_int(text):
            try: return int(text) if text else 0
            except: return 0
            
        if self.tabs.currentIndex() == 0:
            return {
                'type': 'pruned',
                'pruned_z1': parse_int(self.pruned_z1.text()),
                'pruned_y1': parse_int(self.pruned_y1.text()),
                'pruned_z2': parse_int(self.pruned_z2.text()),
                'pruned_y2': parse_int(self.pruned_y2.text())
            }
        else:
            return {
                'type': 'pith',
                'pith_z': parse_int(self.pith_z.text()),
                'pith_y': parse_int(self.pith_y.text())
            }

class LoadingOverlay(QWidget):
    """Semi-transparent overlay displayed over the canvas during AI analysis."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel("Analyzing image, please wait...")
        self.label.setStyleSheet(
            "color: white; font-size: 16px; font-weight: bold; background: transparent;"
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate mode
        self.progress.setFixedWidth(300)
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 3px;
                background-color: rgba(255, 255, 255, 20);
            }
            QProgressBar::chunk {
                border-radius: 3px;
                background-color: #5C9DFF;
            }
        """)

        layout.addWidget(self.label)
        layout.addSpacing(8)
        layout.addWidget(self.progress, 0, Qt.AlignmentFlag.AlignCenter)

        self.btn_cancel = QPushButton("CANCEL DETECTION")
        self.btn_cancel.setFixedWidth(180)
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        layout.addSpacing(15)
        layout.addWidget(self.btn_cancel, 0, Qt.AlignmentFlag.AlignCenter)

        self.hide()

    def paintEvent(self, event):
        """Paint a semi-transparent dark background."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(20, 30, 50, 180))
        painter.end()
        super().paintEvent(event)


class AiAnalysisView(QWidget):
    def __init__(self, view_model: AiAnalysisViewModel):
        super().__init__()
        self.view_model = view_model
        
        self.is_grouping_mode = False
        self.is_remove_mode = False
        self.is_add_mode = False
        self.drawing_points = []
        self.drawing_poly_item = None
        self.scale_x = 1.0
        self.scale_y = 1.0
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 30)
        
        # Divider with Title
        header_layout = QHBoxLayout()
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        line1.setLineWidth(2)
        title = QLabel("AI DETECTION MODE")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #283863;")
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        line2.setLineWidth(2)
        
        header_layout.addWidget(line1, 1)
        header_layout.addWidget(title, 0, Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(line2, 5)
        
        main_layout.addLayout(header_layout)
        
        # Content Layout
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(28, 0, 28, 0)
        
        # Left Panel (Buttons and Label)
        left_panel = QHBoxLayout()
        
        self.btn_import = QPushButton("IMPORT IMAGE")
        self.btn_start = QPushButton("START DETECTION")
        self.btn_group = QPushButton("GROUP KNOTS")
        self.btn_add = QPushButton("ADD SEGMENT")
        self.btn_remove = QPushButton("REMOVE SEGMENT")
        self.btn_hide_segments = QPushButton("HIDE SEGMENTS")
        self.hide_segments = False
        
        self.msg_label = QLabel("")
        self.msg_label.setWordWrap(True)
        self.msg_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        
        # Style buttons - disabled by default where appropriate
        self.btn_start.setEnabled(False)
        self.btn_group.setEnabled(False)
        self.btn_add.setEnabled(False)
        self.btn_remove.setEnabled(False)
        self.btn_hide_segments.setEnabled(False)
        
        left_panel.addWidget(self.btn_import)
        left_panel.addWidget(self.btn_start)
        left_panel.addWidget(self.btn_group)
        left_panel.addWidget(self.btn_add)
        left_panel.addWidget(self.btn_remove)
        left_panel.addWidget(self.btn_hide_segments)
        left_panel.addWidget(self.msg_label)
        left_panel.addStretch()
        
        content_layout.addLayout(left_panel, 1) # 1 part for controls
        
        # Right Panel (Graphics View)
        self.scene = QGraphicsScene(self)
        self.view = ZoomableGraphicsView(self.scene, self)
        self.view.setMinimumHeight(400)
        # Mouse click handling on view
        self.view.mousePressEvent = self._on_canvas_clicked
        
        content_layout.addWidget(self.view, 5) # 5 parts for image

        # Loading overlay (shown during AI analysis)
        self.loading_overlay = LoadingOverlay(self.view)
        self.loading_overlay.hide()
        
        main_layout.addLayout(content_layout)

    def _connect_signals(self):
        self.btn_import.clicked.connect(self._import_image)
        self.btn_start.clicked.connect(self._start_detection)
        self.btn_group.clicked.connect(self._toggle_group_mode)
        self.btn_add.clicked.connect(self._toggle_add_mode)
        self.btn_remove.clicked.connect(self._toggle_remove_mode)
        self.btn_hide_segments.clicked.connect(self._toggle_hide_segments)
        self.loading_overlay.btn_cancel.clicked.connect(self._cancel_detection)
        
        # VM Signals
        self.view_model.analysis_started.connect(self._on_analysis_started)
        self.view_model.analysis_finished.connect(self._on_analysis_finished)
        self.view_model.error_occurred.connect(self._on_error)
        self.view_model.segments_updated.connect(self._redraw_segments)
        self.view_model.selection_changed.connect(self._redraw_segments)
        self.view_model.state_reset.connect(self._on_state_reset)

    def _cancel_detection(self):
        """Cancel ongoing AI analysis and restore pre-detection state."""
        self.view_model.cancel_analysis()
        self._hide_loading_overlay()
        self.btn_start.setText("START DETECTION")
        self.btn_start.setStyleSheet("")
        self.btn_start.setEnabled(True)
        self.btn_import.setEnabled(True)
        self.btn_group.setEnabled(False)
        self.btn_add.setEnabled(False)
        self.btn_remove.setEnabled(False)
        self.btn_hide_segments.setEnabled(False)
        self.msg_label.setText("Detection cancelled. Ready to start detection.")
        self.msg_label.setStyleSheet("color: black;")
        self._redraw_segments()

    def _toggle_hide_segments(self):
        """Toggle showing/hiding of knot segments over raw board."""
        self.hide_segments = not getattr(self, 'hide_segments', False)
        if self.hide_segments:
            self.btn_hide_segments.setText("SHOW SEGMENTS")
            self.btn_hide_segments.setStyleSheet("background-color: #E65100; color: white; font-weight: bold;")
        else:
            self.btn_hide_segments.setText("HIDE SEGMENTS")
            self.btn_hide_segments.setStyleSheet("")
        self._redraw_segments()
        
    def _on_state_reset(self):
        """Reset UI canvas, interaction modes, and buttons when board/project changes or state is cleared."""
        self.is_grouping_mode = False
        self.is_add_mode = False
        self.is_remove_mode = False
        self.hide_segments = False
        self.btn_hide_segments.setText("HIDE SEGMENTS")
        self.btn_hide_segments.setStyleSheet("")
        self.btn_start.setText("START DETECTION")
        self.btn_start.setStyleSheet("")
        self.drawing_points = []
        self.drawing_poly_item = None
        self.drawn_items = []
        
        self.scene.clear()
        
        board = self.view_model._get_current_board()
        if board:
            self.btn_import.setEnabled(True)
            self.btn_start.setEnabled(False)
            self.btn_group.setEnabled(False)
            self.btn_add.setEnabled(False)
            self.btn_remove.setEnabled(False)
            self.btn_hide_segments.setEnabled(False)
            self.msg_label.setText(f"Ready to import image for Board {board.board_no}.")
            self.msg_label.setStyleSheet("color: black;")
        else:
            self.btn_import.setEnabled(False)
            self.btn_start.setEnabled(False)
            self.btn_group.setEnabled(False)
            self.btn_add.setEnabled(False)
            self.btn_remove.setEnabled(False)
            self.btn_hide_segments.setEnabled(False)
            self.msg_label.setText("No board selected. Please select a board from the top Data Panel.")
            self.msg_label.setStyleSheet("color: #777;")

    def _import_image(self):
        # Validate that a board is selected first
        board = self.view_model._get_current_board()
        if not board:
            QMessageBox.warning(self, "Warning", "Please select a board from the top Data Panel first.")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Select Board Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            # Reset modes and canvas before loading new image
            self.is_grouping_mode = False
            self.is_add_mode = False
            self.is_remove_mode = False
            self.btn_group.setText("GROUP KNOTS")
            self.btn_group.setStyleSheet("")
            self.btn_add.setText("ADD SEGMENT")
            self.btn_add.setStyleSheet("")
            self.btn_remove.setText("REMOVE SEGMENT")
            self.btn_remove.setStyleSheet("")
            self.btn_start.setText("START DETECTION")
            self.btn_start.setStyleSheet("")
            
            self.view_model.load_image(file_path)
            self.msg_label.setText("Image loaded. Ready for detection.")
            self.msg_label.setStyleSheet("color: black;")
            self.btn_start.setEnabled(True)
            self.btn_group.setEnabled(False)
            self.btn_add.setEnabled(False)
            self.btn_remove.setEnabled(False)
            self._draw_image(file_path)

    def _start_detection(self):
        # If worker is currently running, clicking button cancels detection
        if self.view_model._worker is not None and self.view_model._worker.isRunning():
            self._cancel_detection()
            return

        board = self.view_model._get_current_board()
        if not board:
            QMessageBox.warning(self, "Warning", "Please select a board from the top Data Panel first.")
            return
        self.view_model.run_analysis()

    def _on_analysis_started(self):
        self.msg_label.setText("Analyzing image...")
        self.msg_label.setStyleSheet("color: blue;")
        self.btn_start.setText("STOP DETECTION")
        self.btn_start.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        self.btn_start.setEnabled(True)
        self.btn_import.setEnabled(False)
        self._show_loading_overlay()

    def _on_analysis_finished(self, result):
        self._hide_loading_overlay()
        self.btn_start.setText("START DETECTION")
        self.btn_start.setStyleSheet("")
        has_segs = bool(self.view_model.unassigned_segments)
        self.btn_hide_segments.setEnabled(has_segs)
        if has_segs:
            self.msg_label.setText("Please, group the knots")
            self.msg_label.setStyleSheet("color: green; font-weight: bold;")
            self.btn_group.setEnabled(True)
            self.btn_add.setEnabled(True)
            self.btn_remove.setEnabled(True)
        else:
            self.msg_label.setText("No valid knots found in the test area.")
            self.msg_label.setStyleSheet("color: orange; font-weight: bold;")
            self.btn_add.setEnabled(True)
            
        self.btn_import.setEnabled(True)
        self.btn_start.setEnabled(True)
        self._redraw_segments()

    def _on_error(self, err_msg):
        self._hide_loading_overlay()
        self.btn_start.setText("START DETECTION")
        self.btn_start.setStyleSheet("")
        self.msg_label.setText(f"Error: {err_msg}")
        self.msg_label.setStyleSheet("color: red; font-weight: bold;")
        self.btn_start.setEnabled(True)
        self.btn_import.setEnabled(True)

    def _show_loading_overlay(self):
        """Show the loading overlay on top of the graphics view."""
        self.loading_overlay.setGeometry(self.view.rect())
        self.loading_overlay.raise_()
        self.loading_overlay.show()

    def _hide_loading_overlay(self):
        """Hide the loading overlay."""
        self.loading_overlay.hide()

    def _toggle_group_mode(self):
        if not self.is_grouping_mode:
            # Enter grouping mode
            self.is_grouping_mode = True
            self.btn_group.setText("SAVE GROUP")
            self.btn_group.setStyleSheet("background-color: #4CAF50;") # Green button
            self.msg_label.setText("Click segments to group them, then press SAVE GROUP.")
            self.msg_label.setStyleSheet("color: black;")
            self.btn_add.setEnabled(False)
            self.btn_start.setEnabled(False)
            self.btn_import.setEnabled(False)
        else:
            # Save group
            if not self.view_model.selected_segment_ids:
                QMessageBox.warning(self, "Warning", "No segment selected!")
                return
                
            # If only 1 segment is selected, ask for Single Face details
            single_face_data = None
            if len(self.view_model.selected_segment_ids) == 1:
                board = self.view_model._get_current_board()
                selected_segs = [s for s in self.view_model.unassigned_segments if s.segment_id in self.view_model.selected_segment_ids]
                temp_knot_data = self.view_model._calculate_knot_data(selected_segs, None)
                face_id = selected_segs[0].face_id
                
                dialog = SingleFaceKnotDialog(board, temp_knot_data, face_id, self)
                if dialog.exec():
                    single_face_data = dialog.get_data()
                else:
                    return # User cancelled grouping
            
            success = self.view_model.group_and_save_knot(single_face_data=single_face_data)
            
            if not success:
                # The ViewModel already emitted an error which was caught by _on_error,
                # but we shouldn't exit grouping mode or clear the selection.
                return
                
            # Check if we are done
            if not self.view_model.unassigned_segments:
                self.is_grouping_mode = False
                self.btn_group.setText("GROUP KNOTS")
                self.btn_group.setStyleSheet("")
                self.btn_group.setEnabled(False)
                self.msg_label.setText("All knots grouped successfully!")
                self.msg_label.setStyleSheet("color: green; font-weight: bold;")
                self.btn_add.setEnabled(True)
                self.btn_remove.setEnabled(True)
                self.btn_start.setEnabled(True)
                self.btn_import.setEnabled(True)
            else:
                self.msg_label.setText("Knot saved! Select segments for the next group.")
                self.msg_label.setStyleSheet("color: black;")

    def _finalize_manual_segment(self):
        """Automatically determine Face ID from polygon Y coordinates and save manual segment."""
        if len(self.drawing_points) < 3:
            return
        from core.ai.ai_models import Point2D
        poly_points = [Point2D(x=pt.x(), y=pt.y()) for pt in self.drawing_points]
        cy_px = float(np.mean([pt.y() for pt in self.drawing_points]))
        
        assigned_face = self.view_model.auto_detect_face(cy_px)
        
        self.view_model.add_manual_segment(poly_points, face_id=assigned_face)
        
        self.drawing_points = []
        if self.drawing_poly_item:
            self.scene.removeItem(self.drawing_poly_item)
            self.drawing_poly_item = None
            
        self.btn_add.setText("ADD SEGMENT")
        self.btn_add.setStyleSheet("")
        self.is_add_mode = False
        self.msg_label.setText("Manual segment added.")
        self.msg_label.setStyleSheet("color: green;")

    def _toggle_add_mode(self):
        if not self.is_add_mode:
            self.is_add_mode = True
            self.btn_add.setText("FINISH ADDING")
            self.btn_add.setStyleSheet("background-color: #4CAF50;") # Green button
            self.msg_label.setText("Click points on canvas to draw segment. Click FINISH ADDING when done.")
            self.msg_label.setStyleSheet("color: black;")
            
            # Disable other modes
            self.is_grouping_mode = False
            self.btn_group.setText("GROUP KNOTS")
            self.btn_group.setStyleSheet("")
            self.is_remove_mode = False
            self.btn_remove.setText("REMOVE SEGMENT")
            self.btn_remove.setStyleSheet("")
        else:
            self._finalize_manual_segment()

    def _toggle_remove_mode(self):
        if not self.is_remove_mode:
            self.is_remove_mode = True
            self.btn_remove.setText("FINISH REMOVING")
            self.btn_remove.setStyleSheet("background-color: #f44336;") # Red button
            self.msg_label.setText("Click segments to delete them. Press FINISH REMOVING when done.")
            self.msg_label.setStyleSheet("color: black;")
            
            # Disable other modes
            self.is_add_mode = False
            self.btn_add.setText("ADD SEGMENT")
            self.btn_add.setStyleSheet("")
            self.is_grouping_mode = False
            self.btn_group.setText("GROUP KNOTS")
            self.btn_group.setStyleSheet("")
        else:
            self.is_remove_mode = False
            self.btn_remove.setText("REMOVE SEGMENT")
            self.btn_remove.setStyleSheet("")
            if self.view_model.unassigned_segments:
                self.msg_label.setText("Please, group the knots")
                self.msg_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.msg_label.setText("No segments remaining.")
                self.msg_label.setStyleSheet("color: black;")
        
    def _draw_image(self, image_path: str):
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            return
            
        # Safely reset canvas state
        self.drawn_items = []
        self.drawing_poly_item = None
        self.scene.clear()
        
        # Crop out bottom non-wood grey calibration strip if present
        img_bgr = cv2.imread(image_path)
        if img_bgr is not None:
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            top_y, bottom_y = self.view_model.analyzer._detect_wood_crop_bounds(img_rgb)
            if bottom_y < img_bgr.shape[0]:
                wood_bgr = img_bgr[top_y:bottom_y, :]
                wood_rgb = cv2.cvtColor(wood_bgr, cv2.COLOR_BGR2RGB)
                h, w, ch = wood_rgb.shape
                bytes_per_line = ch * w
                qimg = QImage(wood_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
        
        self.scale_x = 1.0
        self.scale_y = 1.0
                
        self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def _redraw_segments(self, unused=None):
        if not self.view_model.current_image_path:
            return

        has_segments = bool(self.view_model.unassigned_segments)
        self.btn_hide_segments.setEnabled(has_segments)
        if not has_segments:
            self.hide_segments = False
            self.btn_hide_segments.setText("HIDE SEGMENTS")
            self.btn_hide_segments.setStyleSheet("")
            
        # Safely remove previously drawn dynamic items without crashing if scene was cleared
        if hasattr(self, 'drawn_items'):
            for item in self.drawn_items:
                try:
                    self.scene.removeItem(item)
                except Exception:
                    pass
        self.drawn_items = []
        
        # Draw faces separators
        if self.view_model.analysis_result:
            for face in self.view_model.analysis_result.faces:
                scaled_y = face.max_y
                scaled_max_x = self.view_model.analysis_result.image_width
                line = self.scene.addLine(0, scaled_y, scaled_max_x, scaled_y, QPen(QColor(0, 0, 255, 150), 2))
                self.drawn_items.append(line)

            # Draw testpos lines if available
            board = self.view_model._get_current_board()
            if board and getattr(board, 'test_position', None) is not None and board.test_position > 0:
                testpos = board.test_position
                h = board.height
                
                px_per_mm_x = self.view_model.analysis_result.image_width / float(board.length) if board.length > 0 else 1.0
                testpos_px = testpos * px_per_mm_x
                h_px = 3 * h * px_per_mm_x

                line_y1 = 0
                line_y2 = self.scene.sceneRect().height()
                
                testpos_pen = QPen(QColor(50, 50, 200, 200), 2, Qt.PenStyle.DashLine)
                bound_pen = QPen(QColor(200, 50, 50, 200), 2, Qt.PenStyle.DashLine)
                
                l1 = self.scene.addLine(testpos_px, line_y1, testpos_px, line_y2, testpos_pen)
                l2 = self.scene.addLine(testpos_px - h_px, line_y1, testpos_px - h_px, line_y2, bound_pen)
                l3 = self.scene.addLine(testpos_px + h_px, line_y1, testpos_px + h_px, line_y2, bound_pen)
                self.drawn_items.extend([l1, l2, l3])

        # Draw segments (only if not hidden by user toggle)
        if not getattr(self, 'hide_segments', False):
            for seg in self.view_model.unassigned_segments:
                is_selected = seg.segment_id in self.view_model.selected_segment_ids
                
                poly = QPolygonF([QPointF(p.x, p.y) for p in seg.polygon])
                
                brush_color = QColor(0, 255, 0, 100) if is_selected else QColor(255, 255, 0, 100)
                pen_color = QColor(0, 255, 0, 255) if is_selected else QColor(255, 255, 0, 255)
                
                poly_item = self.scene.addPolygon(poly, QPen(pen_color, 2), QBrush(brush_color))
                poly_item.setData(0, seg.segment_id)
                self.drawn_items.append(poly_item)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.scene.sceneRect().width() > 0:
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        # Keep loading overlay sized to the view
        self.loading_overlay.setGeometry(self.view.rect())

    def _on_canvas_clicked(self, event):
        QGraphicsView.mousePressEvent(self.view, event)
        
        pos = self.view.mapToScene(event.pos())
        
        if self.is_add_mode:
            if event.button() == Qt.MouseButton.LeftButton:
                # Add point to drawing
                self.drawing_points.append(pos)
                if self.drawing_poly_item:
                    self.scene.removeItem(self.drawing_poly_item)
                self.drawing_poly_item = self.scene.addPolygon(QPolygonF(self.drawing_points), QPen(QColor(255, 0, 0), 2))
            elif event.button() == Qt.MouseButton.RightButton and len(self.drawing_points) >= 3:
                # Finish drawing and save manual segment
                self._finalize_manual_segment()
            return

        # Normal interaction (select or remove)
        item = self.scene.itemAt(pos, self.view.transform())
        
        if item and item.data(0):
            segment_id = item.data(0)
            if self.is_remove_mode and event.button() == Qt.MouseButton.LeftButton:
                # Delete segment (priority over grouping selection)
                self.view_model.delete_segment(segment_id)
            elif self.is_grouping_mode and event.button() == Qt.MouseButton.LeftButton:
                self.view_model.toggle_segment_selection(segment_id)
