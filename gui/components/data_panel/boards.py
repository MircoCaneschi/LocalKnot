from PySide6.QtWidgets import QVBoxLayout, QFormLayout, QHBoxLayout, QGridLayout, QPushButton, QComboBox, QLineEdit, \
    QCompleter
from PySide6.QtCore import Qt

from gui.components.common_widgets import create_shift_buttons


class BoardsGui:
    def __init__(self):
        self.board_no = 0

        self.board_no_combo = None
        self.right_shift_btn = None
        self.left_shift_btn = None
        self.new_btn = None
        self.save_btn = None
        self.delete_btn = None
        self.height_line = None
        self.base_line = None
        self.length_line = None
        self.testpos_line = None
        self.comment_line = None
        #------------------------
        self.hidden_board_no_combo = None
        self.hidden_right_shift_btn = None
        self.hidden_left_shift_btn = None
        self.hidden_height_line = None
        self.hidden_base_line = None
        self.hidden_length_line = None


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
        top_layout.setSpacing(2)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(5, 0, 0, 0)
        bottom_layout.setSpacing(2)

        crud_layout = QVBoxLayout()
        crud_layout.setContentsMargins(0, 0, 0, 0)
        crud_layout.setSpacing(2)

        data_layout = QFormLayout()
        data_layout.setContentsMargins(5, 0, 5, 5)
        data_layout.setSpacing(2)
        # -

        # bottom layout
            #combo box
        self.board_no_combo = QComboBox()
        self.board_no_combo.InsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        self.board_no_combo.setEditable(True)    #todo attach proper data
        temporary_list=["1", "2", "3","4672", "3234", "3445", "4325", "1438", "4382", "9999"]  # example items, replace with actual board numbers
        self.board_no_combo.addItems(temporary_list)  # example items, replace with actual board numbers
        self.board_no = self.board_no_combo.count()

            #combo box autocomplete
        completer=QCompleter(temporary_list)    # example items, replace with actual board numbers
        completer.setFilterMode(Qt.MatchFlag.MatchStartsWith)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.board_no_combo.setCompleter(completer)

        bottom_layout.addWidget(self.board_no_combo,1)

        # shifts
        self.right_shift_btn, self.left_shift_btn = create_shift_buttons()

        top_layout.addWidget(self.right_shift_btn)
        top_layout.addWidget(self.left_shift_btn)
        top_layout.addStretch(1)
        top_layout.setContentsMargins(0, 0, 0, 0)
        # -

        # crud layout
        crud_layout.addLayout(top_layout)
        self.new_btn = QPushButton("New+")
        self.save_btn = QPushButton("Save")
        self.delete_btn = QPushButton("Del-")
        self.new_btn.setMinimumWidth(50)
        self.save_btn.setMinimumWidth(50)
        self.delete_btn.setMinimumWidth(50)
        crud_layout.addWidget(self.new_btn)
        crud_layout.addWidget(self.save_btn)
        crud_layout.addWidget(self.delete_btn)

        # data layout
        # no_line = QLineEdit()      #as below
        self.height_line = QLineEdit()
        self.base_line = QLineEdit()
        self.length_line = QLineEdit()
        self.testpos_line = QLineEdit()
        self.comment_line = QLineEdit()
        # data_layout.addRow("No.", no_line)     #only add if you cannot modify number from the comboBox
        data_layout.addRow("Height", self.height_line)
        data_layout.addRow("Base", self.base_line)
        data_layout.addRow("Length", self.length_line)
        data_layout.addRow("TestPos", self.testpos_line)
        data_layout.addRow("Comment", self.comment_line)

        # grid disposition
        self.main_layout.addLayout(bottom_layout, 1, 0, 1, 1)
        self.main_layout.addLayout(crud_layout, 1, 1, 3, 1)
        self.main_layout.addLayout(data_layout, 0, 2, 6, 1)  # row, column, row span, column span

    def setup_hidden_layout(self):
        # main grid layout
        self.hidden_main_layout = QGridLayout()
        self.hidden_main_layout.setContentsMargins(0, 7, 0, 0)
        self.hidden_main_layout.setSpacing(2)

        # sub-layouts in the grid
        hidden_top_layout = QHBoxLayout()
        hidden_top_layout.setContentsMargins(0, 0, 5, 0)
        hidden_top_layout.setSpacing(2)

        hidden_bottom_layout = QHBoxLayout()
        hidden_bottom_layout.setContentsMargins(5, 0, 0, 0)
        hidden_bottom_layout.setSpacing(2)

        hidden_data_layout = QHBoxLayout()
        hidden_data_layout.setContentsMargins(5, 5, 5, 5)
        hidden_data_layout.setSpacing(2)

        # bottom layout
        self.hidden_board_no_combo = QComboBox()
        self.hidden_board_no_combo.setEditable(True)
        self.hidden_board_no_combo.InsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        hidden_bottom_layout.addWidget(self.hidden_board_no_combo)

        # top layout

        # shifts
        self.hidden_right_shift_btn, self.hidden_left_shift_btn = create_shift_buttons()

        hidden_top_layout.addWidget(self.hidden_right_shift_btn)
        hidden_top_layout.addWidget(self.hidden_left_shift_btn)

        # -

        # data layout
        self.hidden_height_line = QLineEdit()
        self.hidden_base_line = QLineEdit()
        self.hidden_length_line = QLineEdit()
        # use form layout to represent data and add horizontally
        height = QFormLayout()
        height.setContentsMargins(0, 0, 0, 0)
        base = QFormLayout()
        base.setContentsMargins(5, 0, 0, 0)
        length = QFormLayout()
        length.setContentsMargins(5, 0, 0, 0)
        height.addRow("Height", self.hidden_height_line)
        base.addRow("Base", self.hidden_base_line)
        length.addRow("Length", self.hidden_length_line)
        hidden_data_layout.addLayout(height)
        hidden_data_layout.addLayout(base)
        hidden_data_layout.addLayout(length)

        # grid disposition
        self.hidden_main_layout.addLayout(hidden_top_layout, 0, 1, 1, 1)
        self.hidden_main_layout.addLayout(hidden_bottom_layout, 0, 0, 1, 1)
        self.hidden_main_layout.addLayout(hidden_data_layout, 1, 0, 3, 2)  # row, column, row span, column span
