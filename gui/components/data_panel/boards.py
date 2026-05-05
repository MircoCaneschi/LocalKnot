from PySide6.QtWidgets import QVBoxLayout, QFormLayout, QHBoxLayout, QGridLayout, QPushButton, QComboBox, QLineEdit, \
    QCompleter
from PySide6.QtCore import Qt

from gui.components.common_widgets import create_shift_buttons


class BoardsGui:
    def __init__(self):
        self._setup_main_layout()
        self.setup_hidden_layout()

    def _setup_main_layout(self):
        # main grid layout
        self.main_layout = QGridLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # sub-layouts in the grid
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(5, 0, 0, 0)
        top_layout.setSpacing(0)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(5, 0, 0, 0)
        bottom_layout.setSpacing(0)

        crud_layout = QVBoxLayout()
        crud_layout.setContentsMargins(0, 0, 0, 0)
        crud_layout.setSpacing(0)

        data_layout = QFormLayout()
        data_layout.setContentsMargins(0, 0, 5, 5)
        data_layout.setSpacing(0)
        # -

        # bottom layout
            #combo box
        board_no_combo = QComboBox()
        board_no_combo.setEditable(True)    #todo attach proper data
        temporary_list=["1", "2", "3","4672", "3234", "3445", "4325", "1438", "4382", "9999"]  # example items, replace with actual board numbers
        board_no_combo.addItems(temporary_list)  # example items, replace with actual board numbers

            #combo box autocomplete
        completer=QCompleter(temporary_list)    # example items, replace with actual board numbers
        completer.setFilterMode(Qt.MatchFlag.MatchStartsWith)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        board_no_combo.setCompleter(completer)

        bottom_layout.addWidget(board_no_combo,1)

        # top layout
        self.board_no = board_no_combo.count()
        # shifts
        right_shift_btn, left_shift_btn = create_shift_buttons()  # todo get these close together

        top_layout.addWidget(right_shift_btn)
        top_layout.addWidget(left_shift_btn)
        top_layout.addStretch(1)
        top_layout.setContentsMargins(0, 0, 0, 0)
        # -

        # crud layout
        crud_layout.addLayout(top_layout)
        new_btn = QPushButton("New+")
        save_btn = QPushButton("Save")
        delete_btn = QPushButton("Del-")
        new_btn.setMinimumWidth(50)
        save_btn.setMinimumWidth(50)
        delete_btn.setMinimumWidth(50)
        crud_layout.addWidget(new_btn)
        crud_layout.addWidget(save_btn)
        crud_layout.addWidget(delete_btn)

        # data layout
        # no_line = QLineEdit()      #as below
        height_line = QLineEdit()
        base_line = QLineEdit()
        length_line = QLineEdit()
        testpos_line = QLineEdit()
        comment_line = QLineEdit()
        # data_layout.addRow("No.", no_line)     #only add if you cannot modify number from the comboBox
        data_layout.addRow("Height", height_line)
        data_layout.addRow("Base", base_line)
        data_layout.addRow("Length", length_line)
        data_layout.addRow("TestPos", testpos_line)
        data_layout.addRow("Comment", comment_line)

        # grid disposition
        self.main_layout.addLayout(bottom_layout, 1, 0, 1, 1)
        self.main_layout.addLayout(crud_layout, 1, 1, 3, 1)
        self.main_layout.addLayout(data_layout, 0, 2, 6, 1)  # row, column, row span, column span

    def setup_hidden_layout(self):
        # main grid layout
        self.hidden_main_layout = QGridLayout()
        self.hidden_main_layout.setContentsMargins(0, 7, 0, 0)
        self.hidden_main_layout.setSpacing(0)

        # sub-layouts in the grid
        hidden_top_layout = QHBoxLayout()
        hidden_top_layout.setContentsMargins(0, 0, 5, 0)
        hidden_top_layout.setSpacing(0)

        hidden_bottom_layout = QHBoxLayout()
        hidden_bottom_layout.setContentsMargins(5, 0, 0, 0)
        hidden_bottom_layout.setSpacing(0)

        hidden_data_layout = QHBoxLayout()
        hidden_data_layout.setContentsMargins(5, 5, 5, 5)
        hidden_data_layout.setSpacing(0)

        # bottom layout
        board_no_combo = QComboBox()
        hidden_bottom_layout.addWidget(board_no_combo)

        # top layout
        self.board_no = board_no_combo.count()
        # shifts
        right_shift_btn, left_shift_btn = create_shift_buttons()

        hidden_top_layout.addWidget(right_shift_btn)
        hidden_top_layout.addWidget(left_shift_btn)

        # -

        # data layout
        height_line = QLineEdit()
        base_line = QLineEdit()
        length_line = QLineEdit()
        # use form layout to represent data and add horizontally
        height = QFormLayout()
        height.setContentsMargins(0, 0, 0, 0)
        base = QFormLayout()
        base.setContentsMargins(5, 0, 0, 0)
        length = QFormLayout()
        length.setContentsMargins(5, 0, 0, 0)
        height.addRow("Height", height_line)
        base.addRow("Base", base_line)
        length.addRow("Length", length_line)
        hidden_data_layout.addLayout(height)
        hidden_data_layout.addLayout(base)
        hidden_data_layout.addLayout(length)

        # grid disposition
        self.hidden_main_layout.addLayout(hidden_top_layout, 0, 1, 1, 1)
        self.hidden_main_layout.addLayout(hidden_bottom_layout, 0, 0, 1, 1)
        self.hidden_main_layout.addLayout(hidden_data_layout, 1, 0, 3, 2)  # row, column, row span, column span
