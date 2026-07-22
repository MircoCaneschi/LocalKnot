from dataclasses import dataclass, field
from typing import List
import uuid

@dataclass
class Point2D:
    x: float
    y: float

@dataclass
class BoardFaceInfo:
    face_id: int  # 1 to 4
    min_y: float  # Top boundary of the face in pixels
    max_y: float  # Bottom boundary of the face in pixels

@dataclass
class AiKnotSegment:
    segment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    polygon: List[Point2D] = field(default_factory=list)
    face_id: int = 1  # The face this segment primarily belongs to
    confidence: float = 1.0

@dataclass
class AIAnalysisResult:
    image_width: int
    image_height: int
    faces: List[BoardFaceInfo]
    segments: List[AiKnotSegment]
