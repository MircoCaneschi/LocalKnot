from core.ai.ai_analyzer_base import BaseAIAnalyzer
from core.ai.ai_models import AIAnalysisResult, BoardFaceInfo, AiKnotSegment, Point2D
import random
import os
# pyrefly: ignore [missing-import]
import cv2

class DummyAnalyzer(BaseAIAnalyzer):
    def load_model(self) -> None:
        print("DummyAnalyzer: Model 'loaded' successfully.")

    def analyze(self, image_path: str, board_length: int, board_base: int, board_height: int) -> AIAnalysisResult:
        print(f"DummyAnalyzer: Analyzing {image_path}...")
        
        # We try to use cv2 if available, otherwise just mock dimensions
        width, height = 1000, 400
        if os.path.exists(image_path):
            img = cv2.imread(image_path)
            if img is not None:
                height, width = img.shape[:2]
            
        # Mock 4 faces by dividing height evenly
        face_height = height / 4.0
        faces = []
        for i in range(1, 5):
            faces.append(BoardFaceInfo(
                face_id=i,
                min_y=(i-1)*face_height,
                max_y=i*face_height
            ))
            
        # Create some fake polygons (knots)
        segments = []
        for i in range(1, 6):
            # Pick a random face
            face_id = random.randint(1, 4)
            face = faces[face_id - 1]
            
            # Center of the fake knot
            cx = random.uniform(width * 0.1, width * 0.9)
            cy = random.uniform(face.min_y + 10, face.max_y - 10)
            radius = random.uniform(10, 40)
            
            # Make a simple diamond/octagon polygon
            poly = [
                Point2D(cx, cy - radius),
                Point2D(cx + radius, cy),
                Point2D(cx, cy + radius),
                Point2D(cx - radius, cy)
            ]
            
            segments.append(AiKnotSegment(
                polygon=poly,
                face_id=face_id,
                confidence=round(random.uniform(0.7, 0.99), 2)
            ))
            
        return AIAnalysisResult(
            image_width=width,
            image_height=height,
            faces=faces,
            segments=segments
        )
