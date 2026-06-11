from PySide6.QtCore import QObject, Signal

class VirtualBoardViewModel(QObject):
    """
    ViewModel that acts as a bridge between the VirtualBoardView (user interface)
    and the BoardCalculator (core logic) / Repository (database).
    """
    
    # Signals to notify the UI of changes
    results_updated = Signal(dict)
    
    def __init__(self, calculator, knot_repo):
        super().__init__()
        self.calculator = calculator
        self.knot_repo = knot_repo
        
        # Property to hold the current knot data
        self.current_knot_data = {}

    def update_results(self, current_board, all_knots, current_knot):
        """
        Calculates knot results and emits the results_updated signal.
        Args:
            current_board: The active Board object.
            all_knots: List of Knot objects on the active board.
            current_knot: The currently selected Knot object.
        """
        if not current_board or not current_knot or not all_knots:
            self.results_updated.emit(self.calculator._empty_results())
            return
            
        # Perform the calculation
        results = self.calculator.calculate_knot_results(current_board, all_knots, current_knot)
        
        # Emit the new results to the UI
        self.results_updated.emit(results)
