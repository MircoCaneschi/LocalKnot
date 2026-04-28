from PySide6.QtGraphs import QVector3DList
from PySide6.QtWidgets import QWidget, QHBoxLayout, QGroupBox, QPushButton, QGridLayout, QLabel, QComboBox, QVBoxLayout, QSizePolicy, QSpacerItem


class MainWidgetProjects:
    def __init__(self):

        #todo reduce space between buttons


        #'''

        new_del_layout = QHBoxLayout()
        new_btn = QPushButton("New+")
        delete_btn = QPushButton("Del-")
        # - sto cercando di dargli una dimensione adeguata. il problema attuale è che stanno troppo distanti
        new_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        delete_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        new_btn.setMaximumWidth(60)
        delete_btn.setMaximumWidth(60)
        # -
        new_del_layout.addWidget(new_btn)
        new_del_layout.addWidget(delete_btn)
        # spacer to align left the widgets
        spacer_nd = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        new_del_layout.addItem(spacer_nd)

        # horizontal layout for project label and combo box
        project_layout = QHBoxLayout()
        project_no_label = QLabel("No. project")
        combo_box_projects = QComboBox()
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
        # spacer to align left the widgets
        spacer_project = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        project_layout.addItem(spacer_project)  #spacer

        #species
        species_layout = QHBoxLayout()
        label_species = QLabel("Species")
        combo_box_species = QComboBox()
        add_species_btn = QPushButton("+")
        add_species_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        add_species_btn.setMaximumWidth(30)
        species_layout.addWidget(label_species)
        species_layout.addWidget(combo_box_species)
        species_layout.addWidget(add_species_btn)
        # spacer to align left the widgets
        spacer_species = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        species_layout.addItem(spacer_species)


        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(new_del_layout)
        self.main_layout.addLayout(project_layout)
        self.main_layout.addLayout(species_layout)
        #'''