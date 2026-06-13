"""
Manager for exporting project data.
"""

from typing import Optional
from core.board_calculator import BoardCalculator

class ExportManager:
    """
    Handles the logic for exporting project data to a text file.
    """

    def __init__(self, board_repo, knot_repo):
        self.board_repo = board_repo
        self.knot_repo = knot_repo
        self.calculator = BoardCalculator()

    def _val_str(self, val, is_decimal=False) -> str:
        """Helper to format values as string. Returns empty string if None."""
        if val is None or val == "":
            return ""
        if is_decimal and isinstance(val, (int, float)):
            return f"{val:.2f}"
        return str(val)

    def export_project(self, project_id: str, file_path: str) -> bool:
        """
        Exports all boards and knots of a project to the specified text file.
        Returns True if successful.
        """
        boards = self.board_repo.get_all_boards(project_id)
        
        header = (
            "No_Board;No_Knot;X;tKnot;mKnot;tKAR;mKAR_L;mKAR_R;mKAR;DEB;DAB;DEK;EEB;EAB;"
            "x_tKAR;SplayKnot;B_Comment;Thick;Width;Length;Testpos;Pith;Pith_Y;Pith_Z;"
            "K_Comment;S1_Z1;S1_Z2;S1_Dmin;S2_Y1;S2_Y2;S2_Dmin;S3_Z1;S3_Z2;S3_Dmin;S4_Y1;S4_Y2;S4_Dmin;"
            "Pruned;Pruned_Y;Pruned_Z;"
        )

        lines = [header]

        for board in boards:
            knots = self.knot_repo.get_all_knots(board.board_no, project_id)
            
            # Formattazione per la tavola
            no_board = self._val_str(board.board_no)
            thick = self._val_str(board.base)
            width = self._val_str(board.height)
            length = self._val_str(board.length)
            testpos = self._val_str(board.test_position)
            b_comment = self._val_str(board.comment)

            if not knots:
                # Se non ci sono nodi, esporto solo i dati della tavola e lascio i campi del nodo vuoti
                line = (
                    f"{no_board};;;;;;;;;;;;;;;"  # No_Knot to x_tKAR, SplayKnot
                    f";{b_comment};{thick};{width};{length};{testpos};;;;"  # Pith, Pith_Y, Pith_Z
                    f";;;;;;;;;;;;;;;" # K_Comment, S1..S4
                    f";;;" # Pruned, Pruned_Y, Pruned_Z
                )
                lines.append(line)
                continue

            for knot in knots:
                # Ottengo i parametri calcolati
                # Nota: calculate_knot_results internamente converte i nodi in standard mode per i calcoli.
                # Ma restituisce solo i parametri (tKnot, DEB ecc). 
                # Per esportare i valori Z1/Z2 in standard mode, usiamo il metodo _to_standard_knot.
                std_knot = self.calculator._to_standard_knot(knot, board)
                res = self.calculator.calculate_knot_results(board, knots, knot)

                no_knot = self._val_str(knot.knot_no)
                x = self._val_str(std_knot.x)
                
                # Valori calcolati
                tknot = self._val_str(res.get("tKnot", ""), is_decimal=False)  # Già formattato
                mknot = self._val_str(res.get("mKnot", ""), is_decimal=False)
                tkar = self._val_str(res.get("tKAR", ""), is_decimal=False)
                mkar_l = self._val_str(res.get("mKAR_L", ""), is_decimal=False)
                mkar_r = self._val_str(res.get("mKAR_R", ""), is_decimal=False)
                mkar = self._val_str(res.get("mKAR", ""), is_decimal=False)
                deb = self._val_str(res.get("DEB", ""), is_decimal=False)
                dab = self._val_str(res.get("DAB", ""), is_decimal=False)
                dek = self._val_str(res.get("DEK", ""), is_decimal=False)
                eeb = self._val_str(res.get("EEB", ""), is_decimal=False)
                eab = self._val_str(res.get("EAB", ""), is_decimal=False)
                splayknot = self._val_str(res.get("SplayKnot", ""))
                x_tkar = ""  # Non implementato nel python

                # Proprietà del nodo
                pith = "1" if std_knot.pith_z is not None and std_knot.pith_y is not None else "0"
                pith_y = self._val_str(std_knot.pith_y)
                pith_z = self._val_str(std_knot.pith_z)
                k_comment = self._val_str(knot.comment)
                
                pruned = "1" if std_knot.is_pruned_knot else "0"
                pruned_y = self._val_str(std_knot.pruned_y)
                pruned_z = self._val_str(std_knot.pruned_z)

                s1_z1 = self._val_str(std_knot.side1_z1)
                s1_z2 = self._val_str(std_knot.side1_z2)
                s1_dmin = self._val_str(std_knot.side1_dmin)
                s2_y1 = self._val_str(std_knot.side2_z1)
                s2_y2 = self._val_str(std_knot.side2_z2)
                s2_dmin = self._val_str(std_knot.side2_dmin)
                s3_z1 = self._val_str(std_knot.side3_z1)
                s3_z2 = self._val_str(std_knot.side3_z2)
                s3_dmin = self._val_str(std_knot.side3_dmin)
                s4_y1 = self._val_str(std_knot.side4_z1)
                s4_y2 = self._val_str(std_knot.side4_z2)
                s4_dmin = self._val_str(std_knot.side4_dmin)

                line = (
                    f"{no_board};{no_knot};{x};{tknot};{mknot};{tkar};{mkar_l};{mkar_r};{mkar};{deb};{dab};{dek};{eeb};{eab};"
                    f"{x_tkar};{splayknot};{b_comment};{thick};{width};{length};{testpos};{pith};{pith_y};{pith_z};"
                    f"{k_comment};{s1_z1};{s1_z2};{s1_dmin};{s2_y1};{s2_y2};{s2_dmin};{s3_z1};{s3_z2};{s3_dmin};{s4_y1};{s4_y2};{s4_dmin};"
                    f"{pruned};{pruned_y};{pruned_z};"
                )
                
                # Sostituisco i N/A con stringa vuota per uniformità con java
                line = line.replace("N/A", "")
                lines.append(line)

        with open(file_path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")

        return True
