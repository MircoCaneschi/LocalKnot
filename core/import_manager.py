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
        Includes strict validation. Returns True if successful.
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

        # Check if it's a valid KnotVision export by looking for essential columns
        if "No_Board" not in header_map:
            raise ValueError("This file does not appear to be a KnotVision export.")

        # 3. Parse and validate everything in memory FIRST
        boards_data: Dict[str, Board] = {}
        knots_data: Dict[str, List[Knot]] = {}
        
        # We need these to validate knot coordinates against board dimensions
        board_dimensions: Dict[str, dict] = {} 

        for line_idx in range(1, len(lines)):
            line = lines[line_idx].strip()
            if not line:
                continue
            
            row = line.split(";")
            row_context = f"Row {line_idx + 1}"
            
            def get_val(col_name: str, required: bool = False) -> str:
                if col_name in header_map:
                    idx = header_map[col_name]
                    if idx < len(row):
                        val = row[idx].strip()
                        if required and not val:
                            raise ValueError(f"{row_context}: Field '{col_name}' cannot be empty (NOT NULL).")
                        return val
                if required:
                    raise ValueError(f"{row_context}: Field '{col_name}' is missing but required.")
                return ""
                
            def get_int(col_name: str, required: bool = False) -> Optional[int]:
                val = get_val(col_name, required=required)
                if val:
                    try:
                        return int(float(val))
                    except ValueError:
                        raise ValueError(f"{row_context}: Field '{col_name}' must be an integer, got '{val}'.")
                return None

            try:
                no_board = get_val("No_Board", required=True)
                if not no_board.isdigit():
                    # Usually No_Board is an integer ID in DB, we validate it's numeric
                    raise ValueError(f"{row_context}: 'No_Board' must be numeric.")

                # Parse Board
                if no_board not in boards_data:
                    b_height = get_int("Width", required=True)
                    b_base = get_int("Thick", required=True)
                    b_length_val = get_val("Length", required=True)
                    try:
                        b_length = int(float(b_length_val))
                    except ValueError:
                        raise ValueError(f"{row_context}: 'Length' must be numeric.")
                    
                    b_testpos = get_int("Testpos", required=False)
                    b_comment = get_val("B_Comment")
                    
                    board = Board(
                        board_no=no_board,
                        height=b_height,
                        base=b_base,
                        length=b_length,
                        test_position=b_testpos if b_testpos is not None else 0,
                        comment=b_comment
                    )
                    boards_data[no_board] = board
                    knots_data[no_board] = []
                    board_dimensions[no_board] = {"height": b_height, "base": b_base, "length": b_length}

                # Parse Knot (if present)
                no_knot = get_val("No_Knot", required=False)
                if no_knot:
                    if not no_knot.isdigit():
                        raise ValueError(f"{row_context}: 'No_Knot' must be numeric.")
                    
                    k_x = get_int("X", required=True)
                    if k_x <= 0:
                        raise ValueError(f"{row_context}: Knot X coordinate must be > 0.")
                    b_len = board_dimensions[no_board]["length"]
                    if k_x > b_len:
                        raise ValueError(f"{row_context}: Knot X ({k_x}) exceeds board length ({b_len}).")
                    
                    # Pith / Pruned
                    pith_z = get_int("Pith_Z")
                    pith_y = get_int("Pith_Y")
                    
                    is_pruned = 1 if get_val("Pruned") == "1" else 0
                    pruned_y1 = get_int("Pruned_Y1")
                    pruned_z1 = get_int("Pruned_Z1")
                    pruned_y2 = get_int("Pruned_Y2")
                    pruned_z2 = get_int("Pruned_Z2")
                    
                    # Check pith / pruned completeness
                    if is_pruned:
                        if (pruned_z1 is None) != (pruned_y1 is None):
                            raise ValueError(f"{row_context}: Both Pruned Z1 and Y1 must be provided if one is.")
                        if (pruned_z2 is None) != (pruned_y2 is None):
                            raise ValueError(f"{row_context}: Both Pruned Z2 and Y2 must be provided if one is.")
                    else:
                        if (pith_z is None) != (pith_y is None):
                            raise ValueError(f"{row_context}: Both Pith Z and Y must be provided if one is.")

                    b_height = board_dimensions[no_board]["height"]
                    b_base = board_dimensions[no_board]["base"]

                    # Check pith bounds
                    if is_pruned:
                        if pruned_z2 is not None and pruned_z2 >= b_height:
                            raise ValueError(f"{row_context}: Pruned Z2 ({pruned_z2}) >= board height ({b_height}).")
                        if pruned_y2 is not None and pruned_y2 >= b_base:
                            raise ValueError(f"{row_context}: Pruned Y2 ({pruned_y2}) >= board base ({b_base}).")
                    else:
                        if pith_z is not None and pith_z >= b_height:
                            raise ValueError(f"{row_context}: Pith Z ({pith_z}) >= board height ({b_height}).")
                        if pith_y is not None and pith_y >= b_base:
                            raise ValueError(f"{row_context}: Pith Y ({pith_y}) >= board base ({b_base}).")

                    # Sides
                    sides = {}
                    compiled_sides = 0
                    for side, (z1_col, z2_col, dmin_col, max_val_name, max_val) in enumerate([
                        ("S1_Z1", "S1_Z2", "S1_Dmin", "height", b_height),
                        ("S2_Y1", "S2_Y2", "S2_Dmin", "base", b_base),
                        ("S3_Z1", "S3_Z2", "S3_Dmin", "height", b_height),
                        ("S4_Y1", "S4_Y2", "S4_Dmin", "base", b_base)
                    ], 1):
                        z1 = get_int(z1_col)
                        z2 = get_int(z2_col)
                        dmin = get_int(dmin_col)
                        
                        if z1 is not None or z2 is not None or dmin is not None:
                            if z1 is None or z2 is None or dmin is None:
                                raise ValueError(f"{row_context}: Side {side} has incomplete data. All 3 fields needed.")
                            
                            if z1 < 0:
                                raise ValueError(f"{row_context}: Side {side} start coord must be >= 0.")
                            if z1 >= z2:
                                raise ValueError(f"{row_context}: Side {side} start coord must be < end coord.")
                            if dmin <= 0:
                                raise ValueError(f"{row_context}: Side {side} dmin must be > 0.")
                            if dmin > (z2 - z1):
                                raise ValueError(f"{row_context}: Side {side} dmin > (end - start).")
                            if z2 > max_val:
                                raise ValueError(f"{row_context}: Side {side} end coord ({z2}) > board {max_val_name} ({max_val}).")
                            
                            compiled_sides += 1
                            
                        sides[side] = {"z1": z1, "z2": z2, "dmin": dmin}
                    
                    # Check valid sides count
                    has_pith = False
                    if is_pruned and (pruned_z1 is not None or pruned_z2 is not None): has_pith = True
                    if not is_pruned and (pith_z is not None): has_pith = True
                    
                    if not ((compiled_sides >= 2) or (compiled_sides >= 1 and has_pith)):
                        raise ValueError(f"{row_context}: Knot must have at least 2 sides, or 1 side + pith/pruned data.")

                    # Corner rules
                    s1, s2, s3, s4 = sides[1], sides[2], sides[3], sides[4]
                    
                    # Top-Left (S1 ends at height, S4 starts at 0)
                    if s1["z2"] == b_height and s4["z1"] is not None and s4["z1"] != 0:
                        raise ValueError(f"{row_context}: Corner Rule: Side 1 reaches height, so Side 4 must start at 0.")
                    if s4["z1"] == 0 and s1["z2"] is not None and s1["z2"] != b_height:
                        raise ValueError(f"{row_context}: Corner Rule: Side 4 starts at 0, so Side 1 must reach height.")
                    
                    # Bottom-Left (S4 ends at base, S3 starts at 0)
                    if s4["z2"] == b_base and s3["z1"] is not None and s3["z1"] != 0:
                        raise ValueError(f"{row_context}: Corner Rule: Side 4 reaches base, so Side 3 must start at 0.")
                    if s3["z1"] == 0 and s4["z2"] is not None and s4["z2"] != b_base:
                        raise ValueError(f"{row_context}: Corner Rule: Side 3 starts at 0, so Side 4 must reach base.")
                    
                    # Bottom-Right (S3 ends at height, S2 starts at 0)
                    if s3["z2"] == b_height and s2["z1"] is not None and s2["z1"] != 0:
                        raise ValueError(f"{row_context}: Corner Rule: Side 3 reaches height, so Side 2 must start at 0.")
                    if s2["z1"] == 0 and s3["z2"] is not None and s3["z2"] != b_height:
                        raise ValueError(f"{row_context}: Corner Rule: Side 2 starts at 0, so Side 3 must reach height.")
                    
                    # Top-Right (S2 ends at base, S1 starts at 0)
                    if s2["z2"] == b_base and s1["z1"] is not None and s1["z1"] != 0:
                        raise ValueError(f"{row_context}: Corner Rule: Side 2 reaches base, so Side 1 must start at 0.")
                    if s1["z1"] == 0 and s2["z2"] is not None and s2["z2"] != b_base:
                        raise ValueError(f"{row_context}: Corner Rule: Side 1 starts at 0, so Side 2 must reach base.")

                    knot = Knot(
                        knot_no=no_knot,
                        x=k_x,
                        pith_z=pith_z,
                        pith_y=pith_y,
                        comment=get_val("K_Comment"),
                        is_pruned_knot=is_pruned,
                        pruned_z1=pruned_z1, pruned_y1=pruned_y1,
                        pruned_z2=pruned_z2, pruned_y2=pruned_y2,
                        side1_z1=s1["z1"], side1_z2=s1["z2"], side1_dmin=s1["dmin"],
                        side2_z1=s2["z1"], side2_z2=s2["z2"], side2_dmin=s2["dmin"],
                        side3_z1=s3["z1"], side3_z2=s3["z2"], side3_dmin=s3["dmin"],
                        side4_z1=s4["z1"], side4_z2=s4["z2"], side4_dmin=s4["dmin"]
                    )
                    knots_data[no_board].append(knot)
            except ValueError:
                # Se c'è un errore proviamo a ricavare l'id, se fallisce diamo la riga nel file
                try:
                    no_board = get_val("No_Board", required=True)
                except ValueError:
                    no_board = str(line_idx + 1)
                raise ValueError(f"board {no_board} data are corrupted ")

        # 4. If all validations passed, insert into database
        project = Project(name=project_name, species=species)
        self.project_repo.add_project(project)
        
        for board_no, board in boards_data.items():
            self.board_repo.add_board(board, project.name)
            for knot in knots_data[board_no]:
                self.knot_repo.add_knot(knot, board_no, project.name)
                
        return True
