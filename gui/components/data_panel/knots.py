from PySide6.QtWidgets import QVBoxLayout, QFormLayout, QHBoxLayout, QGridLayout, QPushButton, QComboBox, QLineEdit, \
    QCheckBox

from gui.components.common_widgets import create_shift_buttons


class KnotsGui:
    def __init__(self):
        self.main_layout = None
        self.hidden_main_layout = None
        self.knot_no = 0



        self._setup_main_layout()
        self.setup_hidden_layout()

    def _setup_main_layout(self):
        # main grid layout
        self.main_layout = QGridLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # sub-layouts in the grid
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(5, 0, 0, 0)
        bottom_layout.setSpacing(0)

        crud_layout = QVBoxLayout()
        crud_layout.setContentsMargins(0, 0, 0, 0)
        crud_layout.setSpacing(0)

        data_layout = QFormLayout()
        data_layout.setContentsMargins(0, 0, 5, 0)
        data_layout.setSpacing(0)
        # -

        # bottom layout
        knot_no_combo = QComboBox()
        bottom_layout.addWidget(knot_no_combo)

        # top layout
        self.knot_no = knot_no_combo.count()
        # shifts
        right_shift_btn, left_shift_btn = create_shift_buttons()  # todo get these close together

        top_layout.addWidget(right_shift_btn)
        top_layout.addWidget(left_shift_btn)
        top_layout.setContentsMargins(0, 0, 0, 0)
        # -

        # crud layout
        crud_layout.addLayout(top_layout)
        new_btn = QPushButton("New+")
        save_btn = QPushButton("Save")
        delete_btn = QPushButton("Del-")
        crud_layout.addWidget(new_btn)
        crud_layout.addWidget(save_btn)
        crud_layout.addWidget(delete_btn)

        # data layout
        # no_line = QLineEdit()      #as below
        x_line = QLineEdit()
        pith_z_line = QLineEdit()
        pith_y_line = QLineEdit()
        comment_line = QLineEdit()
        # data_layout.addRow("No.", no_line)     #only add if you cannot modify number from the comboBox
        data_layout.addRow("X", x_line)
        data_layout.addRow("Pith Z", pith_z_line)
        data_layout.addRow("Pith Y", pith_y_line)
        data_layout.addRow("Comment", comment_line)
        fake_pith = QCheckBox()
        fake_pith.setChecked(False)
        data_layout.addRow("Fake pith:",fake_pith)

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
        knot_no_combo = QComboBox()
        hidden_bottom_layout.addWidget(knot_no_combo)

        # top layout
        self.knot_no = knot_no_combo.count()
        # shifts
        right_shift_btn, left_shift_btn = create_shift_buttons()  # todo get these close together

        hidden_top_layout.addWidget(right_shift_btn)
        hidden_top_layout.addWidget(left_shift_btn)

        # -

        # data layout
        x_line = QLineEdit()
        pith_z_line = QLineEdit()
        pith_y_line = QLineEdit()
        # use form layout to represent data and add horizontally
        x = QFormLayout()
        x.setContentsMargins(0, 0, 0, 0)
        pith_z = QFormLayout()
        pith_z.setContentsMargins(5, 0, 0, 0)
        pith_y = QFormLayout()
        pith_y.setContentsMargins(5, 0, 0, 0)
        comment = QFormLayout()
        comment.setContentsMargins(5, 0, 0, 0)
        x.addRow("X", x_line)
        pith_z.addRow("Pith Z", pith_z_line)
        pith_y.addRow("Length Y", pith_y_line)
        comment.addRow("Comment", comment)
        hidden_data_layout.addLayout(x)
        hidden_data_layout.addLayout(pith_z)
        hidden_data_layout.addLayout(pith_y)
        hidden_data_layout.addLayout(comment)
        #check box for the fake pith
        fake_pith = QCheckBox()
        fake_pith.setChecked(False)
        hidden_data_layout.addWidget(fake_pith)


        # grid disposition
        self.hidden_main_layout.addLayout(hidden_top_layout, 0, 1, 1, 1)
        self.hidden_main_layout.addLayout(hidden_bottom_layout, 0, 0, 1, 1)
        self.hidden_main_layout.addLayout(hidden_data_layout, 1, 0, 3, 2)  # row, column, row span, column span
