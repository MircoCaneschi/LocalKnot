from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QGroupBox, QLabel
)

from mvvm.viewmodels.virtual_board_vm import VirtualBoardViewModel

class KnotResultsView(QWidget):
    """
    View component to display the calculated parameters of the knot.
    Can be expanded/collapsed.
    """
    def __init__(self, view_model: VirtualBoardViewModel):
        super().__init__()
        self.view_model = view_model
        
        self.setup_ui()
        self.bind_view_model()
        
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 10, 0, 0)
        
        # Button to show/hide results
        self.toggle_results_btn = QPushButton("Show/Hide Calculated Parameters")
        self.toggle_results_btn.clicked.connect(self._toggle_results)
        main_layout.addWidget(self.toggle_results_btn)
        
        # Group with data (initially hidden)
        self.results_group = QGroupBox("Knot Parameters")
        group_layout = QGridLayout(self.results_group)
        
        # Create placeholder labels for results
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
            if col > 5:  # 6 columns to not make it too tall
                col = 0
                row += 1
                
        main_layout.addWidget(self.results_group)
        self.results_group.hide()  # Hide at startup

    def _toggle_results(self):
        """Shows or hides the results panel."""
        if self.results_group.isVisible():
            self.results_group.hide()
        else:
            self.results_group.show()

    def bind_view_model(self):
        # Connect the view_model signal to update the labels
        # self.view_model.results_updated.connect(self._update_results)
        pass
        
    def _update_results(self, results_dict):
        """Updates the labels with calculated results."""
        for param, val in results_dict.items():
            if param in self.result_labels:
                self.result_labels[param].setText(str(val))
