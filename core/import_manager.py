"""
Manager for importing project data from CSV/TXT files.
Supports both legacy and new export formats.
"""

import os
from typing import Dict, List, Any, Optional
from mvvm.models import Project, Board, Knot

class ImportManager:
    """
    Handles the logic for parsing text files and creating entities.
    """

    def __init__(self, project_repo, board_repo, knot_repo):
        self.project_repo = project_repo
        self.board_repo = board_repo
        self.knot_repo = knot_repo

    def parse_and_import(self, file_path: str, project_name: str, species: str) -> bool:
        """
        Parses the given file and saves the project, boards, and knots to the database.
        Returns True if successful.
        """
        # 1. Read file
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        if not lines:
            raise ValueError("The file is empty.")

        # 2. Parse headers
        header_line = lines[0]
        headers = [h.strip() for h in header_line.split(";")]
        header_map = {h: i for i, h in enumerate(headers) if h}

        # 3. Create Project
        project = Project(name=project_name, species=species)
        self.project_repo.add_project(project)

        # 4. Parse rows
        boards_data: Dict[str, Board] = {}
        knots_data: Dict[str, List[Knot]] = {}

        for line_idx in range(1, len(lines)):
            line = lines[line_idx].strip()
            if not line:
                continue
            
            row = line.split(";")
            
            def get_val(col_name: str) -> str:
                if col_name in header_map:
                    idx = header_map[col_name]
                    if idx < len(row):
                        return row[idx].strip()
                return ""
                
            def get_int(col_name: str) -> Optional[int]:
                val = get_val(col_name)
                if val:
                    try:
                        return int(float(val)) # float() handles "3.0" -> 3 cases if any
                    except ValueError:
                        return None
                return None

            no_board = get_val("No_Board")
            if not no_board:
                continue

            # Parse Board
            if no_board not in boards_data:
                b_height = get_int("Width") or 0
                b_base = get_int("Thick") or 0
                b_length = get_val("Length")
                b_testpos = get_val("Testpos")
                b_comment = get_val("B_Comment")
                
                board = Board(
                    board_no=no_board,
                    height=b_height,
                    base=b_base,
                    length=b_length,
                    test_position=b_testpos,
                    comment=b_comment
                )
                boards_data[no_board] = board
                self.board_repo.add_board(board, project.name)
                knots_data[no_board] = []

            # Parse Knot (if present)
            no_knot = get_val("No_Knot")
            if no_knot:
                k_x = get_int("X")
                if k_x is None: k_x = 0
                
                # Check pith
                pith_z = get_int("Pith_Z")
                pith_y = get_int("Pith_Y")
                
                # Pruned fields (missing in legacy, so they will be None/0)
                is_pruned = 1 if get_val("Pruned") == "1" else 0
                pruned_y1 = get_int("Pruned_Y1")
                pruned_z1 = get_int("Pruned_Z1")
                pruned_y2 = get_int("Pruned_Y2")
                pruned_z2 = get_int("Pruned_Z2")
                
                knot = Knot(
                    knot_no=no_knot,
                    x=k_x,
                    pith_z=pith_z,
                    pith_y=pith_y,
                    comment=get_val("K_Comment"),
                    is_pruned_knot=is_pruned,
                    pruned_z1=pruned_z1,
                    pruned_y1=pruned_y1,
                    pruned_z2=pruned_z2,
                    pruned_y2=pruned_y2,
                    side1_z1=get_int("S1_Z1"),
                    side1_z2=get_int("S1_Z2"),
                    side1_dmin=get_int("S1_Dmin"),
                    side2_z1=get_int("S2_Y1"), # Note: Header says S2_Y1 for side2_z1 in export
                    side2_z2=get_int("S2_Y2"),
                    side2_dmin=get_int("S2_Dmin"),
                    side3_z1=get_int("S3_Z1"),
                    side3_z2=get_int("S3_Z2"),
                    side3_dmin=get_int("S3_Dmin"),
                    side4_z1=get_int("S4_Y1"), # S4_Y1 mapped to side4_z1
                    side4_z2=get_int("S4_Y2"),
                    side4_dmin=get_int("S4_Dmin")
                )
                self.knot_repo.add_knot(knot, no_board, project.name)
                knots_data[no_board].append(knot)
                
        return True
