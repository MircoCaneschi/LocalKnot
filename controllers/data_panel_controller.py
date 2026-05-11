from PySide6.QtWidgets import QWidget

from gui.components.data_panel.data_panel import *


class ProjectsController:
    def __init__(self, data_panel_obj: DataPanelWidget, hidden_panel_obj: HiddenDataPanelWidget):
        self.data_panel = data_panel_obj.projects_gui
        self.hidden_panel = hidden_panel_obj

        # SIGNALS CONNECTIONS
        self.data_panel.new_btn.clicked.connect(self.handle_new_project)
        self.data_panel.save_btn.clicked.connect(self.handle_save_project)
        self.data_panel.add_species_btn.clicked.connect(self.handle_add_species)

    def handle_new_project(self):
        self.data_panel.combo_box_projects.setEditable(True)
        self.data_panel.combo_box_projects.clearEditText()
        self.data_panel.combo_box_species.clearEditText()
        self.data_panel.project_msg.hide()
        self.data_panel.species_msg.hide()

    def handle_save_project(self):
        project_text = self.data_panel.combo_box_projects.currentText()
        species_text = self.data_panel.combo_box_species.currentText()

        # --------PROJECT CHECKS--------
        # checks if the project_text is valid -> no empty str or already existing
        if project_text == '' or self.data_panel.combo_box_projects.findText(project_text) != -1:
            self.data_panel.project_msg.setText("Invalid project name!")
            self.data_panel.project_msg.show()
            return
        # hide message if it was previously shown
        self.data_panel.project_msg.hide()

        # --------SPECIES CHECKS--------
        if species_text == '' and not self.data_panel.combo_box_species.isEditable():
            self.data_panel.species_msg.setText("Select a species first!")
            self.data_panel.species_msg.show()
            return
        # checks if the species name is valid -> no empty str or already existing | ONLY WHEN A NEW SPECIES WAS ADDED
        if ((species_text == '' or self.data_panel.combo_box_species.findText(species_text) != -1) and
                self.data_panel.combo_box_species.isEditable()):
            self.data_panel.species_msg.setText("Invalid species name!")
            self.data_panel.species_msg.show()
            return
        # hide message if it was previously shown
        self.data_panel.species_msg.hide()

        # register the project
        self.data_panel.combo_box_projects.addItem(project_text)
        # register the species if it was a new one
        if self.data_panel.combo_box_species.findText(species_text) == -1:
            self.data_panel.combo_box_species.addItem(species_text)
            self.data_panel.species_msg.setText(f"{species_text} registered!")
            self.data_panel.species_msg.show()

        # confirmation message
        self.data_panel.project_msg.setText(f"{project_text} registered!")
        self.data_panel.project_msg.show()

        # reset editable of combo boxes to False
        self.data_panel.combo_box_projects.setEditable(False)
        self.data_panel.combo_box_species.setEditable(False)


        # todo implement the db part

    def handle_add_species(self):
        self.data_panel.combo_box_species.setEditable(True)


class BoardsController:
    def __init__(self, data_panel_obj: DataPanelWidget, hidden_panel_obj: HiddenDataPanelWidget):
        data_panel_obj.boards_gui.board_no_combo.maxVisibleItems = 5  # todo does nothing


class KnotsController:
    def __init__(self, data_panel_obj: DataPanelWidget, hidden_panel_obj: HiddenDataPanelWidget):
        None
