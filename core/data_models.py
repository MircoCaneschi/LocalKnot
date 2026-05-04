from dataclasses import dataclass
from typing import Optional

@dataclass
class Project:
    id_project: str     # PK (es. "QRC-001")
    species: str        # species of wood

@dataclass
class Board:
    id_board: int       # PK
    id_project: str     # FK to Project.id_project
    height: float       # millimeters with decimals
    Base: float        # millimeters with decimals
    length: int
    testpos: int
    comment: str
    image_path: Optional[str] = None  # path to the image of the board, optional

@dataclass
class Knot:
    id_knot: int        # PK
    id_board: int       # FK to Board.id_board
    x: int
    pith_z: int
    pitch_y: int
    comment: str
    fake_pith: bool
    #side1
    side1_z1: int
    side1_z2: int
    side1_dmin: int
    #side2
    side2_z1: int
    side2_z2: int
    side2_dmin: int
    #side 3
    side3_z1: int
    side3_z2: int
    side3_dmin: int
    #sode 4
    side4_z1: int
    side4_z2: int
    side4_dmin: int