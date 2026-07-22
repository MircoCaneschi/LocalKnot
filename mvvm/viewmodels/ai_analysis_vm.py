from PySide6.QtCore import QObject, Signal, QThread
from core.ai.ai_analyzer_base import BaseAIAnalyzer
from core.ai.ai_models import AIAnalysisResult, AiKnotSegment, Point2D
from typing import List, Optional

class AnalysisWorker(QThread):
    """Worker thread for running SAM2 analysis without blocking the UI."""
    analysis_complete = Signal(object)  # Emits AIAnalysisResult
    analysis_error = Signal(str)

    def __init__(self, analyzer, image_path, board_length, board_base, board_height):
        super().__init__()
        self.analyzer = analyzer
        self.image_path = image_path
        self.board_length = board_length
        self.board_base = board_base
        self.board_height = board_height

    def run(self):
        try:
            self.analyzer.load_model()
            result = self.analyzer.analyze(
                image_path=self.image_path,
                board_length=self.board_length,
                board_base=self.board_base,
                board_height=self.board_height
            )
            self.analysis_complete.emit(result)
        except Exception as e:
            self.analysis_error.emit(str(e))


class AiAnalysisViewModel(QObject):
    # Signals for the View
    analysis_started = Signal()
    analysis_finished = Signal(object) # Passes AIAnalysisResult
    error_occurred = Signal(str)
    selection_changed = Signal(list) # Passes list of selected segment_ids
    segments_updated = Signal(list) # Passes list of unassigned segments

    def __init__(self, analyzer: BaseAIAnalyzer, boards_vm, knots_vm):
        super().__init__()
        self.analyzer = analyzer
        self.boards_vm = boards_vm
        self.knots_vm = knots_vm

        self.current_image_path: Optional[str] = None
        self.analysis_result: Optional[AIAnalysisResult] = None
        
        self.unassigned_segments: List[AiKnotSegment] = []
        self.selected_segment_ids: List[str] = []
        
        self.knots_vm.knot_saved.connect(self._on_knot_saved_sync)
        self.knots_vm.knot_error.connect(self._on_knot_error_sync)
        self.knots_vm.validation_failed.connect(self._on_knot_error_sync)
        self._save_success = False
        self._worker = None

    def _on_knot_saved_sync(self, msg):
        self._save_success = True

    def _on_knot_error_sync(self, msg=None):
        self._save_success = False

    def load_image(self, image_path: str):
        self.current_image_path = image_path
        # Reset state
        self.analysis_result = None
        self.unassigned_segments = []
        self.selected_segment_ids = []

    def run_analysis(self):
        if not self.current_image_path:
            self.error_occurred.emit("No image loaded.")
            return

        board = self._get_current_board()
        if not board:
            self.error_occurred.emit("Please select a board from the top Data Panel first.")
            return

        # Prevent running multiple analyses simultaneously
        if self._worker is not None and self._worker.isRunning():
            self.error_occurred.emit("Analysis is already in progress.")
            return

        self.analysis_started.emit()

        # Store board reference for post-processing in the main thread
        self._analysis_board = board

        self._worker = AnalysisWorker(
            self.analyzer,
            self.current_image_path,
            board.length,
            board.base,
            board.height
        )
        self._worker.analysis_complete.connect(self._on_analysis_complete)
        self._worker.analysis_error.connect(self._on_analysis_error)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.start()

    def _on_analysis_complete(self, result):
        """Handle successful analysis result from the worker thread."""
        self._worker = None
        self.analysis_result = result
        self.unassigned_segments = list(result.segments)

        # Filter for TestPos (Central Third Region)
        # Validity area: from testpos - 3*height to testpos + 3*height
        board = self._analysis_board
        testpos = getattr(board, 'test_position', 0)
        if testpos and testpos > 0:
            h = board.height
            min_valid_x_mm = testpos - (3 * h)
            max_valid_x_mm = testpos + (3 * h)

            px_per_mm_x = result.image_width / board.length if board.length > 0 else 1.0

            filtered_segments = []
            for seg in self.unassigned_segments:
                min_px = min(p.x for p in seg.polygon)
                max_px = max(p.x for p in seg.polygon)
                seg_x_mm = ((min_px + max_px) / 2) / px_per_mm_x

                if min_valid_x_mm <= seg_x_mm <= max_valid_x_mm:
                    filtered_segments.append(seg)

            # If testpos filtering yields 0 segments but raw segments were found, retain all segments
            if filtered_segments:
                self.unassigned_segments = filtered_segments
            else:
                print("AiAnalysisViewModel: TestPos filter matched 0 segments; displaying all detected segments.")

        self.selected_segment_ids = []

        self.analysis_finished.emit(self.analysis_result)
        self.segments_updated.emit(self.unassigned_segments)

    def _on_analysis_error(self, error_msg):
        """Handle analysis error from the worker thread."""
        self._worker = None
        self.error_occurred.emit(f"Error during analysis: {error_msg}")

    def toggle_segment_selection(self, segment_id: str):
        if segment_id in self.selected_segment_ids:
            self.selected_segment_ids.remove(segment_id)
        else:
            # Check if face is already selected
            seg = next((s for s in self.unassigned_segments if s.segment_id == segment_id), None)
            if seg:
                selected_faces = [s.face_id for s in self.unassigned_segments if s.segment_id in self.selected_segment_ids]
                if seg.face_id in selected_faces:
                    self.error_occurred.emit(f"You cannot select more than one segment on Face {seg.face_id}.")
                    return
            self.selected_segment_ids.append(segment_id)
        self.selection_changed.emit(self.selected_segment_ids)

    def delete_segment(self, segment_id: str):
        self.unassigned_segments = [s for s in self.unassigned_segments if s.segment_id != segment_id]
        if segment_id in self.selected_segment_ids:
            self.selected_segment_ids.remove(segment_id)
        self.selection_changed.emit(self.selected_segment_ids)
        self.segments_updated.emit(self.unassigned_segments)
        
    def add_manual_segment(self, points: List[Point2D], face_id: int):
        new_seg = AiKnotSegment(polygon=points, face_id=face_id, confidence=1.0)
        self.unassigned_segments.append(new_seg)
        self.segments_updated.emit(self.unassigned_segments)

    def auto_detect_face(self, cy_px: float) -> int:
        """Automatically determines which face (1-4) a Y coordinate belongs to based on face boundaries."""
        if self.analysis_result and self.analysis_result.faces:
            for f in self.analysis_result.faces:
                if f.min_y <= cy_px <= f.max_y:
                    return f.face_id
            return 1

        # Fallback using current board physical dimensions if AI analysis hasn't run yet
        board = self._get_current_board()
        if board:
            img_h = self.analysis_result.image_height if self.analysis_result else 1000.0
            h, b = board.height, board.base
            if h > 0 and b > 0:
                total = 2 * h + 2 * b
                y1 = img_h * (h / total)
                y2 = img_h * ((h + b) / total)
                y3 = img_h * ((2 * h + b) / total)
                if cy_px < y1: return 1
                elif cy_px < y2: return 2
                elif cy_px < y3: return 3
                else: return 4

        return 1

    def delete_selected_segments(self):
        if not self.selected_segment_ids:
            return
        self.unassigned_segments = [s for s in self.unassigned_segments if s.segment_id not in self.selected_segment_ids]
        self.selected_segment_ids = []
        self.selection_changed.emit(self.selected_segment_ids)
        self.segments_updated.emit(self.unassigned_segments)

    def _calculate_knot_data(self, selected_segs, _unused=None):
        """Calculate knot dimensions from selected segments for preview purposes."""
        board = self._get_current_board()
        if not board or not self.analysis_result:
            return {}

        px_per_mm_x = self.analysis_result.image_width / board.length if board.length > 0 else 1.0

        # Calculate center X of all selected segments
        min_x = min(p.x for s in selected_segs for p in s.polygon)
        max_x = max(p.x for s in selected_segs for p in s.polygon)
        knot_x_mm = int(((min_x + max_x) / 2) / px_per_mm_x)

        knot_data = {'x': knot_x_mm}

        for seg in selected_segs:
            face_info = next((f for f in self.analysis_result.faces if f.face_id == seg.face_id), None)
            if not face_info:
                continue

            is_height_face = seg.face_id in [1, 3]
            physical_width_of_face = board.height if is_height_face else board.base

            face_px_height = face_info.max_y - face_info.min_y
            px_per_mm_z = face_px_height / physical_width_of_face if physical_width_of_face > 0 else 1.0

            seg_min_y = min(p.y for p in seg.polygon)
            seg_max_y = max(p.y for p in seg.polygon)

            z1_mm = int((seg_min_y - face_info.min_y) / px_per_mm_z)
            z2_mm = int((seg_max_y - face_info.min_y) / px_per_mm_z)

            import numpy as np
            import cv2
            pts_mm = np.array([[p.x / px_per_mm_x, p.y / px_per_mm_z] for p in seg.polygon], dtype=np.float32)
            dmin_mm = 1
            if len(pts_mm) >= 3:
                rect_mm = cv2.minAreaRect(pts_mm)
                w_mm, h_mm = rect_mm[1]
                dmin_mm = max(1, int(min(w_mm, h_mm)))

            side_prefix = f"side{seg.face_id}"
            knot_data[f"{side_prefix}_z1"] = z1_mm
            knot_data[f"{side_prefix}_z2"] = z2_mm
            knot_data[f"{side_prefix}_dmin"] = dmin_mm

        return knot_data

    def group_and_save_knot(self, single_face_data: dict = None) -> bool:
        if not self.selected_segment_ids:
            self.error_occurred.emit("No segment selected.")
            return False

        board = self._get_current_board()
        if not board:
            self.error_occurred.emit("No board selected.")
            return False

        # Get the selected segments
        selected_segs = [s for s in self.unassigned_segments if s.segment_id in self.selected_segment_ids]
        
        # 1. Calculate X
        # Image width = board_length
        px_per_mm_x = self.analysis_result.image_width / board.length if board.length > 0 else 1.0
        
        # Find the center X of the bounding box of all selected segments
        min_x = min(p.x for s in selected_segs for p in s.polygon)
        max_x = max(p.x for s in selected_segs for p in s.polygon)
        center_x_px = (min_x + max_x) / 2
        knot_x_mm = int(center_x_px / px_per_mm_x)

        # 2. Prepare Knot Data Dictionary
        knot_data = {
            'x': knot_x_mm,
            'comment': "AI Generated",
        }
        
        if single_face_data:
            knot_data['type'] = single_face_data.get('type')
            if knot_data['type'] == 'pruned':
                knot_data['pruned_z1'] = single_face_data.get('pruned_z1')
                knot_data['pruned_y1'] = single_face_data.get('pruned_y1')
                knot_data['pruned_z2'] = single_face_data.get('pruned_z2')
                knot_data['pruned_y2'] = single_face_data.get('pruned_y2')
            elif knot_data['type'] == 'pith':
                knot_data['pith_z'] = single_face_data.get('pith_z')
                knot_data['pith_y'] = single_face_data.get('pith_y')

        # 3. Calculate z1, z2, dmin for each face
        # We assume faces 1, 3 correspond to the board's 'height' (edges) 
        # and faces 2, 4 correspond to the board's 'base' (flats). 
        # This mapping can be adjusted if the image layout is different.
        for seg in selected_segs:
            face_info = next((f for f in self.analysis_result.faces if f.face_id == seg.face_id), None)
            if not face_info: continue

            # Determine physical height of this face
            is_height_face = seg.face_id in [1, 3]
            physical_width_of_face = board.height if is_height_face else board.base
            
            face_px_height = face_info.max_y - face_info.min_y
            px_per_mm_z = face_px_height / physical_width_of_face if physical_width_of_face > 0 else 1.0

            # Find min_y and max_y relative to the face
            seg_min_y = min(p.y for p in seg.polygon)
            seg_max_y = max(p.y for p in seg.polygon)
            
            # Convert to Z (distance from the top edge of the face)
            z1_mm = int((seg_min_y - face_info.min_y) / px_per_mm_z)
            z2_mm = int((seg_max_y - face_info.min_y) / px_per_mm_z)

            # dmin calculation: Minimum Area Rectangle
            import numpy as np
            import cv2
            
            pts_mm = np.array([[p.x / px_per_mm_x, p.y / px_per_mm_z] for p in seg.polygon], dtype=np.float32)
            if len(pts_mm) >= 3:
                rect_mm = cv2.minAreaRect(pts_mm)
                width_mm, height_mm = rect_mm[1]
                dmin_mm = int(min(width_mm, height_mm))
            else:
                dmin_mm = 1

            # Ensure we don't exceed the board limits logically
            dmin_mm = max(1, dmin_mm) # At least 1mm

            # Map to the corresponding side in the database (side1 to side4)
            side_prefix = f"side{seg.face_id}"
            knot_data[f"{side_prefix}_z1"] = z1_mm
            knot_data[f"{side_prefix}_z2"] = z2_mm
            knot_data[f"{side_prefix}_dmin"] = dmin_mm

        # 4. Save using KnotsViewModel
        return self._save_knot_to_vm(knot_data)

    def _get_current_board(self):
        board_no = self.boards_vm.current_board_no
        if not board_no: return None
        return next((b for b in self.boards_vm._boards if str(b.board_no) == str(board_no)), None)

    def _save_knot_to_vm(self, knot_data: dict) -> bool:
        self._save_success = False
        
        # Map knot_data to knots_vm properties and trigger a save
        self.knots_vm.handle_new_knot()
        
        self.knots_vm.x = knot_data.get('x', 0)
        self.knots_vm.comment = knot_data.get('comment', "")
        
        # Reset specific fields
        self.knots_vm.is_pruned_knot = False
        self.knots_vm.pith_z = None
        self.knots_vm.pith_y = None
        
        if knot_data.get('type') == 'pruned':
            self.knots_vm.is_pruned_knot = True
            setattr(self.knots_vm, 'pruned_z1', knot_data.get('pruned_z1'))
            setattr(self.knots_vm, 'pruned_y1', knot_data.get('pruned_y1'))
            setattr(self.knots_vm, 'pruned_z2', knot_data.get('pruned_z2'))
            setattr(self.knots_vm, 'pruned_y2', knot_data.get('pruned_y2'))
        elif knot_data.get('type') == 'pith':
            self.knots_vm.pith_z = knot_data.get('pith_z')
            self.knots_vm.pith_y = knot_data.get('pith_y')

        # Apply sides data
        for side in range(1, 5):
            setattr(self.knots_vm, f"side{side}_z1", knot_data.get(f"side{side}_z1"))
            setattr(self.knots_vm, f"side{side}_z2", knot_data.get(f"side{side}_z2"))
            setattr(self.knots_vm, f"side{side}_dmin", knot_data.get(f"side{side}_dmin"))

        # Save to database
        self.knots_vm.handle_save_knot()
        
        if self._save_success:
            self.unassigned_segments = [s for s in self.unassigned_segments if s.segment_id not in self.selected_segment_ids]
            self.selected_segment_ids = []
            self.selection_changed.emit(self.selected_segment_ids)
            return True
        return False
