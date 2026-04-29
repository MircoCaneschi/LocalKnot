from PySide6.QtGraphs import QVector3DList
from PySide6.QtWidgets import QWidget, QHBoxLayout, QGroupBox, QPushButton, QGridLayout, QLabel, QComboBox, QVBoxLayout, QSizePolicy, QSpacerItem


class MainWidgetProjects:
    def __init__(self):

        #'''

        new_del_layout = QHBoxLayout()
        new_btn = QPushButton("New+")
        delete_btn = QPushButton("Del-")
        change_name_btn = QPushButton("Modify")
        #gives dimension
        new_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        delete_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        change_name_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        #-
        new_del_layout.addWidget(new_btn, 1)
        new_del_layout.addWidget(delete_btn, 1)
        new_del_layout.addWidget(change_name_btn, 1)
        # brings the button closer
        new_del_layout.setSpacing(0)
        # spacer to align left the widgets
        spacer_nd = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        new_del_layout.addItem(spacer_nd)

        # horizontal layout for project label and combo box
        project_layout = QHBoxLayout()
        project_no_label = QLabel("No. project")
        combo_box_projects = QComboBox()
        project_no_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        combo_box_projects.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        project_layout.addWidget(project_no_label)
        project_layout.addWidget(combo_box_projects)
        #shifts
        right_shift_btn = QPushButton("<")
        left_shift_btn = QPushButton(">")
        right_shift_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        left_shift_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        right_shift_btn.setMaximumWidth(30)
        right_shift_btn.setMinimumWidth(30)
        left_shift_btn.setMaximumWidth(30)
        left_shift_btn.setMinimumWidth(30)
        project_layout.addWidget(right_shift_btn)
        project_layout.addWidget(left_shift_btn)
        # brings the button closer
        project_layout.setSpacing(0)
        # spacer to align left the widgets
        spacer_project = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        project_layout.addItem(spacer_project)  #spacer

        #species
        species_layout = QHBoxLayout()
        label_species = QLabel("Species")
        combo_box_species = QComboBox()
        add_species_btn = QPushButton("+")
        label_species.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        combo_box_species.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        add_species_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        add_species_btn.setMaximumWidth(30)
        add_species_btn.setMinimumWidth(30)
        species_layout.addWidget(label_species)
        species_layout.addWidget(combo_box_species)
        species_layout.addWidget(add_species_btn)
        # brings the button closer
        species_layout.setSpacing(0)
        # spacer to align left the widgets
        spacer_species = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        species_layout.addItem(spacer_species)


        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(new_del_layout)
        self.main_layout.addLayout(project_layout)
        self.main_layout.addLayout(species_layout)
        #'''


        #############---layout for the hidden version---###################


        # horizontal layout for project label and combo box
        hidden_project_layout = QHBoxLayout()
        hidden_project_no_label = QLabel("No. project")
        hidden_combo_box_projects = QComboBox()
        hidden_project_no_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        hidden_combo_box_projects.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        hidden_project_layout.addWidget(hidden_project_no_label)
        hidden_project_layout.addWidget(hidden_combo_box_projects)
        #shifts
        hidden_right_shift_btn = QPushButton("<")
        hidden_left_shift_btn = QPushButton(">")
        hidden_right_shift_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        hidden_left_shift_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        hidden_right_shift_btn.setMaximumWidth(30)
        hidden_right_shift_btn.setMinimumWidth(30)
        hidden_left_shift_btn.setMaximumWidth(30)
        hidden_left_shift_btn.setMinimumWidth(30)
        hidden_project_layout.addWidget(hidden_right_shift_btn)
        hidden_project_layout.addWidget(hidden_left_shift_btn)
        #species
        hidden_label_species = QLabel("Species")
        hidden_combo_box_species = QComboBox()
        hidden_label_species.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        hidden_combo_box_species.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        hidden_project_layout.addWidget(hidden_label_species)
        hidden_project_layout.addWidget(hidden_combo_box_species)
        # brings the button closer
        hidden_project_layout.setSpacing(0)
        # spacer to align left the widgets
        hidden_spacer_project = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        hidden_project_layout.addItem(hidden_spacer_project)  #spacer



        self.hidden_main_layout = QVBoxLayout()
        self.hidden_main_layout.addLayout(hidden_project_layout)
