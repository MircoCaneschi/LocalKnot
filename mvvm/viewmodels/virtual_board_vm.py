from PySide6.QtCore import QObject, Signal

class VirtualBoardViewModel(QObject):
    """
    ViewModel che fa da ponte tra la VirtualBoardView (interfaccia utente) 
    e il BoardCalculator (logica core) / Repository (database).
    """
    
    # Segnali per notificare la UI dei cambiamenti
    results_updated = Signal(dict)
    
    def __init__(self, calculator, knot_repo):
        super().__init__()
        self.calculator = calculator
        self.knot_repo = knot_repo
        
        # Proprietà per contenere i dati correnti del nodo
        self.current_knot_data = {}

    # Qui implementeremo le funzioni per aggiornare i dati e calcolare i risultati
