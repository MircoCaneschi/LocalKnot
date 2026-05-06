from PySide6.QtWidgets import QHBoxLayout, QPushButton, QLabel, QComboBox, QVBoxLayout, QSizePolicy, QSpacerItem, \
    QFormLayout

from gui.components.common_widgets import create_shift_buttons


# this is the messiest class because it's the first I did

class ProjectsGui:
    def __init__(self):
        self.main_layout = None
        self.hidden_main_layout = None

        # interactive widgets
        self.new_btn = None
        self.delete_btn = None
        self.change_name_btn = None
        self.save_btn = None
        self.combo_box_projects = None
        self.combo_box_species = None
        self.add_species_btn = None
        self.right_shift_btn = None
        self.left_shift_btn = None
        #----------------------------
        self.hidden_combo_box_projects = None
        self.hidden_combo_box_species = None
        self.hidden_right_shift_btn = None
        self.hidden_left_shift_btn = None
        #-

        self._setup_main_layout()
        self._setup_hidden_layout()

    def _setup_main_layout(self):
        new_del_layout = QHBoxLayout()
        self.new_btn = QPushButton("New+")
        self.delete_btn = QPushButton("Del-")
        self.change_name_btn = QPushButton("Modify")
        self.save_btn = QPushButton("Save")
        # gives dimension
        self.new_btn.setMinimumWidth(50)
        self.delete_btn.setMinimumWidth(50)
        self.change_name_btn.setMinimumWidth(60)
        self.save_btn.setMinimumWidth(50)
        self.new_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.delete_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.change_name_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.save_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # -
        new_del_layout.addWidget(self.new_btn, 1)
        new_del_layout.addWidget(self.delete_btn, 1)
        new_del_layout.addWidget(self.change_name_btn, 1)
        new_del_layout.addWidget(self.save_btn, 1)
        # brings the button closer
        new_del_layout.setSpacing(2)
        # spacer to align left the widgets
        spacer_nd = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        new_del_layout.addItem(spacer_nd)

        # horizontal layout for project label and combo box
        project_layout = QHBoxLayout()
        self.combo_box_projects = QComboBox()
        self.combo_box_projects.InsertPolicy(QComboBox.InsertPolicy.InsertAtBottom)
        self.combo_box_projects.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        project_layout.addWidget(self.combo_box_projects)

        # shifts
        self.right_shift_btn, self.left_shift_btn = create_shift_buttons()
        project_layout.addWidget(self.right_shift_btn)
        project_layout.addWidget(self.left_shift_btn)
        # brings the button closer
        project_layout.setSpacing(2)

        # species
        species_layout = QHBoxLayout()
        self.combo_box_species = QComboBox()
        self.combo_box_species.InsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        self.add_species_btn = QPushButton("+")
        self.combo_box_species.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.add_species_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.add_species_btn.setMaximumWidth(30)
        self.add_species_btn.setMinimumWidth(30)
        species_layout.addWidget(self.combo_box_species)
        species_layout.addWidget(self.add_species_btn)
        # brings the button closer
        species_layout.setSpacing(2)

        #messages
        self.project_msg = QLabel()
        self.species_msg = QLabel()
        self.project_msg.hide()
        self.species_msg.hide()

        # form for bottom widgets
        form = QFormLayout()
        form.addRow("Project.", project_layout)
        form.addRow("", self.project_msg)
        form.addRow("Species", species_layout)
        form.addRow("", self.species_msg)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(new_del_layout)
        self.main_layout.addLayout(form)

    #############---layout for the hidden version---###################

    def _setup_hidden_layout(self):
        # horizontal layout for project label and combo box
        hidden_project_layout = QHBoxLayout()
        hidden_project_no_label = QLabel("Project")
        self.hidden_combo_box_projects = QComboBox()
        self.hidden_combo_box_projects.setEditable(True)
        self.hidden_combo_box_projects.InsertPolicy(QComboBox.InsertPolicy.InsertAtBottom)
        hidden_project_no_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.hidden_combo_box_projects.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        hidden_project_layout.addWidget(hidden_project_no_label)
        hidden_project_layout.addWidget(self.hidden_combo_box_projects)
        # shifts
        self.hidden_right_shift_btn, self.hidden_left_shift_btn = create_shift_buttons()
        hidden_project_layout.addWidget(self.hidden_right_shift_btn)
        hidden_project_layout.addWidget(self.hidden_left_shift_btn)
        # species
        hidden_species_layout = QHBoxLayout()
        hidden_label_species = QLabel("Species")
        hidden_label_species.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        # comboBox species
        self.hidden_combo_box_species = QComboBox()
        self.hidden_combo_box_species.setEditable(True)
        self.hidden_combo_box_species.InsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        self.hidden_combo_box_species.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        hidden_species_layout.addWidget(hidden_label_species)
        hidden_species_layout.addWidget(self.hidden_combo_box_species)

        # brings the button closer
        hidden_project_layout.setSpacing(2)

        self.hidden_main_layout = QVBoxLayout()
        self.hidden_main_layout.addLayout(hidden_project_layout)
        self.hidden_main_layout.addLayout(hidden_species_layout)
