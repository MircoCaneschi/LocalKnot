from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QGraphicsView, QGraphicsScene, QLineEdit, QLabel, QFormLayout,
    QGroupBox, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator

from mvvm.viewmodels.virtual_board_vm import VirtualBoardViewModel

class VirtualBoardView(QWidget):
    """
    Interfaccia grafica interattiva per la visualizzazione e l'inserimento
    dei dati della tavola e del nodo corrente. 
    Contiene un QGraphicsView al centro e le 12 LineEdit ai lati.
    """
    def __init__(self, view_model: VirtualBoardViewModel):
        super().__init__()
        self.view_model = view_model
        
        self.setup_ui()
        self.bind_view_model()
        
    def setup_ui(self):
        # Layout principale
        main_layout = QVBoxLayout(self)
        
        # --- GRIGLIA GRAFICA E INPUT ---
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Validatore per accettare solo numeri interi
        validator = QIntValidator()
        self.inputs = {}

        # Funzione helper per creare un gruppo di 3 line edit (z1, z2, dmin)
        def create_side_inputs(side_name, orientation="horizontal"):
            container = QWidget()
            layout = QHBoxLayout(container) if orientation == "horizontal" else QVBoxLayout(container)
            layout.setContentsMargins(5, 5, 5, 5)
            
            group_inputs = {}
            for field in ["z1", "z2", "dmin"]:
                form = QFormLayout()
                form.setContentsMargins(0, 0, 0, 0)
                line_edit = QLineEdit()
                line_edit.setValidator(validator)
                line_edit.setMaximumWidth(60)
                form.addRow(f"{field}:", line_edit)
                layout.addLayout(form)
                group_inputs[field] = line_edit
                
            self.inputs[side_name] = group_inputs
            return container

        # Creazione dei 4 lati
        top_widget = create_side_inputs("side1_top", "horizontal")
        right_widget = create_side_inputs("side2_right", "vertical")
        bottom_widget = create_side_inputs("side3_bottom", "horizontal")
        left_widget = create_side_inputs("side4_left", "vertical")

        # Centro: QGraphicsView
        self.scene = QGraphicsScene()
        self.graphics_view = QGraphicsView(self.scene)
        self.graphics_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.graphics_view.setMinimumSize(400, 400)

        # Posizionamento nella griglia
        # riga 0: vuoto, top, vuoto
        # riga 1: left, centro, right
        # riga 2: vuoto, bottom, vuoto
        grid_layout.addWidget(top_widget, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        grid_layout.addWidget(left_widget, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        grid_layout.addWidget(self.graphics_view, 1, 1)
        grid_layout.addWidget(right_widget, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        grid_layout.addWidget(bottom_widget, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addLayout(grid_layout, stretch=1)
        
        # --- TENDINA RISULTATI ---
        self.results_container = QWidget()
        results_layout = QVBoxLayout(self.results_container)
        results_layout.setContentsMargins(0, 10, 0, 0)
        
        # Pulsante per mostrare/nascondere i risultati
        self.toggle_results_btn = QPushButton("Mostra/Nascondi Parametri Calcolati")
        self.toggle_results_btn.clicked.connect(self._toggle_results)
        results_layout.addWidget(self.toggle_results_btn)
        
        # Gruppo con i dati (inizialmente nascosto)
        self.results_group = QGroupBox("Parametri del Nodo")
        group_layout = QGridLayout(self.results_group)
        
        # Creiamo label placeholder per i risultati
        self.result_labels = {}
        parameters = ["tKnot", "mKnot", "tKAR", "mKAR_L", "mKAR_R", "mKAR", "DEB", "DAB", "DEK", "EEB", "EAB"]
        
        row, col = 0, 0
        for param in parameters:
            name_lbl = QLabel(f"<b>{param}:</b>")
            val_lbl = QLabel("-")
            
            form = QHBoxLayout()
            form.addWidget(name_lbl)
            form.addWidget(val_lbl)
            form.addStretch()
            
            group_layout.addLayout(form, row, col)
            self.result_labels[param] = val_lbl
            
            col += 1
            if col > 3:  # 4 colonne per non renderlo troppo alto
                col = 0
                row += 1
                
        results_layout.addWidget(self.results_group)
        self.results_group.hide()  # Nascondi all'avvio
        
        main_layout.addWidget(self.results_container)

    def _toggle_results(self):
        """Mostra o nasconde il pannello dei risultati."""
        if self.results_group.isVisible():
            self.results_group.hide()
        else:
            self.results_group.show()

    def bind_view_model(self):
        # Collegheremo qui i segnali del view_model alle line edit e alla grafica
        pass
