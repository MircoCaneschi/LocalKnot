from PySide6.QtWidgets import QHBoxLayout, QPushButton, QLabel, QComboBox, QVBoxLayout, QSizePolicy, QSpacerItem, \
    QFormLayout

from gui.components.common_widgets import create_shift_buttons


# this is the messiest class because it's the first I did

class ProjectsGui:
    def __init__(self):
        self.main_layout = None
        self.hidden_main_layout = None

        self._setup_main_layout()
        self._setup_hidden_layout()

    def _setup_main_layout(self):
        new_del_layout = QHBoxLayout()
        new_btn = QPushButton("New+")
        delete_btn = QPushButton("Del-")
        change_name_btn = QPushButton("Modify")
        save_btn = QPushButton("Save")
        # gives dimension
        new_btn.setMinimumWidth(50)
        delete_btn.setMinimumWidth(50)
        change_name_btn.setMinimumWidth(60)
        save_btn.setMinimumWidth(50)
        new_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        delete_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        change_name_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        save_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # -
        new_del_layout.addWidget(new_btn, 1)
        new_del_layout.addWidget(delete_btn, 1)
        new_del_layout.addWidget(change_name_btn, 1)
        new_del_layout.addWidget(save_btn, 1)
        # brings the button closer
        new_del_layout.setSpacing(0)
        # spacer to align left the widgets
        spacer_nd = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        new_del_layout.addItem(spacer_nd)

        # horizontal layout for project label and combo box
        project_layout = QHBoxLayout()
        combo_box_projects = QComboBox()
        combo_box_projects.setEditable(True)
        combo_box_projects.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        project_layout.addWidget(combo_box_projects)
        # shifts
        right_shift_btn, left_shift_btn = create_shift_buttons()
        project_layout.addWidget(right_shift_btn)
        project_layout.addWidget(left_shift_btn)
        # brings the button closer
        project_layout.setSpacing(0)

        # species
        species_layout = QHBoxLayout()
        combo_box_species = QComboBox()
        add_species_btn = QPushButton("+")
        combo_box_species.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        add_species_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        add_species_btn.setMaximumWidth(30)
        add_species_btn.setMinimumWidth(30)
        species_layout.addWidget(combo_box_species)
        species_layout.addWidget(add_species_btn)
        # brings the button closer
        species_layout.setSpacing(0)

        # form for bottom widgets
        form = QFormLayout()
        form.addRow("Project.", project_layout)
        form.addRow("Species", species_layout)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(new_del_layout)
        self.main_layout.addLayout(form)

    #############---layout for the hidden version---###################

    def _setup_hidden_layout(self):
        # horizontal layout for project label and combo box
        hidden_project_layout = QHBoxLayout()
        hidden_project_no_label = QLabel("Project")
        hidden_combo_box_projects = QComboBox()
        hidden_project_no_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        hidden_combo_box_projects.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        hidden_project_layout.addWidget(hidden_project_no_label)
        hidden_project_layout.addWidget(hidden_combo_box_projects)
        # shifts
        hidden_right_shift_btn, hidden_left_shift_btn = create_shift_buttons()
        hidden_project_layout.addWidget(hidden_right_shift_btn)
        hidden_project_layout.addWidget(hidden_left_shift_btn)
        # species
        hidden_species_layout = QHBoxLayout()
        hidden_label_species = QLabel("Species")
        hidden_combo_box_species = QComboBox()
        hidden_label_species.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        hidden_combo_box_species.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        hidden_species_layout.addWidget(hidden_label_species)
        hidden_species_layout.addWidget(hidden_combo_box_species)
        # brings the button closer
        hidden_project_layout.setSpacing(0)

        self.hidden_main_layout = QVBoxLayout()
        self.hidden_main_layout.addLayout(hidden_project_layout)
        self.hidden_main_layout.addLayout(hidden_species_layout)
