from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QGraphicsView, QGraphicsScene,
                               QSizePolicy, QGroupBox, QScrollArea)
from PySide6.QtCore import Qt

from core.database import DatabaseManager
from core.repository import ProjectRepository, BoardRepository, KnotRepository
from mvvm.viewmodels import ProjectsViewModel, BoardsViewModel, KnotsViewModel
from gui.components.data_panel.projects_view_mvvm import ProjectsView
from gui.components.data_panel.boards_view_mvvm import BoardsView
from gui.components.data_panel.knots_view_mvvm import KnotsView
from gui.components.header import HeaderWidget

from core.board_calculator import BoardCalculator
from mvvm.viewmodels.virtual_board_vm import VirtualBoardViewModel
from gui.components.virtual_board_view import VirtualBoardView
from gui.components.knot_results_view import KnotResultsView

class MainWindow(QMainWindow):
    """Main application window with MVVM architecture."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LocalKnot - MVVM Architecture")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        
        central_widget = QWidget()
        self.scroll_area.setWidget(central_widget)
        self.setCentralWidget(self.scroll_area)

        # Main vertical layout
        self.main_layout = QVBoxLayout(central_widget)

        # ==================== Setup MVVM Components ====================

        # Setup Database and Repositories
        self.db = DatabaseManager()
        self.project_repo = ProjectRepository(self.db)
        self.board_repo = BoardRepository(self.db)
        self.knot_repo = KnotRepository(self.db)

        # Create ViewModels
        self.projects_vm = ProjectsViewModel(self.project_repo)
        self.boards_vm = BoardsViewModel(self.board_repo)
        self.knots_vm = KnotsViewModel(self.knot_repo)

        # Create Views
        self.projects_view = ProjectsView(self.projects_vm)
        self.boards_view = BoardsView(self.boards_vm)
        self.knots_view = KnotsView(self.knots_vm)

        # ==================== Add to Layout ====================
        
        # Header Layout
        self.header = HeaderWidget()
        self.main_layout.addWidget(self.header)

        # Toolbar with toggle button
        toolbar_layout = QHBoxLayout()
        self.toggle_panel_btn = QPushButton("Toggle Data Panel")
        self.toggle_panel_btn.clicked.connect(self._toggle_data_panel)
        toolbar_layout.addWidget(self.toggle_panel_btn)
        self.main_layout.addLayout(toolbar_layout)

        # Data panel container
        self.data_panel_container = QWidget()
        self.data_panel_layout = QHBoxLayout(self.data_panel_container)

        # Add all views to their QGroupBox
        self.project_group = QGroupBox(f"Projects[{self.projects_view.combo_box_projects.count()}]")
        self.board_group = QGroupBox(f"Boards[{self.boards_view.board_no_combo.count()}]")
        self.knot_group = QGroupBox(f"Knots[{self.knots_view.knot_no_combo.count()}]")

        self.project_group.setLayout(self.projects_view.main_layout)
        self.board_group.setLayout(self.boards_view.main_layout)
        self.knot_group.setLayout(self.knots_view.main_layout)

        # Add groups to the layout
        self.data_panel_layout.addWidget(self.project_group)
        self.data_panel_layout.addWidget(self.board_group)
        self.data_panel_layout.addWidget(self.knot_group)

        self.main_layout.addWidget(self.data_panel_container)

        # Connect signals for cross-viewModel communication and UI updates
        self.projects_vm.projects_changed.connect(self._update_project_counter)
        self.boards_vm.boards_changed.connect(self._update_board_counter)
        self.projects_vm.current_project_changed.connect(self.boards_vm.handle_project_changed)
        
        self.knots_vm.knots_changed.connect(self._update_knot_counter)
        self.projects_vm.current_project_changed.connect(self.knots_vm.handle_project_changed)
        self.boards_vm.current_board_changed.connect(self.knots_vm.handle_board_changed)

        # Hidden panel (compact view)
        self.hidden_data_panel_container = QWidget()
        self.hidden_data_panel_layout = QHBoxLayout(self.hidden_data_panel_container)

        # Hidden groupBox
        self.hidden_project_group = QGroupBox(f"Projects[{self.projects_view.combo_box_projects.count()}]")
        self.hidden_board_group = QGroupBox(f"Boards[{self.boards_view.board_no_combo.count()}]")
        self.hidden_knot_group = QGroupBox(f"Knots[{self.knots_view.knot_no_combo.count()}]")

        self.hidden_project_group.setLayout(self.projects_view.hidden_main_layout)
        self.hidden_board_group.setLayout(self.boards_view.hidden_main_layout)
        self.hidden_knot_group.setLayout(self.knots_view.hidden_main_layout)

        # Add hidden views
        if hasattr(self.projects_view, 'hidden_main_layout') and self.projects_view.hidden_main_layout:
            self.hidden_data_panel_layout.addWidget(self.hidden_project_group, 1)
        if hasattr(self.boards_view, 'hidden_main_layout') and self.boards_view.hidden_main_layout:
            self.hidden_data_panel_layout.addWidget(self.hidden_board_group, 1)
        if hasattr(self.knots_view, 'hidden_main_layout') and self.knots_view.hidden_main_layout:
            self.hidden_data_panel_layout.addWidget(self.hidden_knot_group, 1)

        #self.hidden_data_panel_layout.addStretch()
        self.main_layout.addWidget(self.hidden_data_panel_container)
        self.hidden_data_panel_container.hide()

        # Virtual Board area
        self.board_calculator = BoardCalculator()
        self.virtual_board_vm = VirtualBoardViewModel(self.board_calculator, self.knot_repo)
        
        # Results panel (between data panel and virtual board)
        self.knot_results_view = KnotResultsView(self.virtual_board_vm)
        self.main_layout.addWidget(self.knot_results_view)
        
        self.virtual_board_view = VirtualBoardView(self.virtual_board_vm)
        self.main_layout.addWidget(self.virtual_board_view)

        # Trigger initial data load now that UI is fully initialized
        self.knots_vm.handle_project_changed(self.projects_vm.current_project)
        self.boards_vm.handle_project_changed(self.projects_vm.current_project)

        self.showMaximized()


    def _toggle_data_panel(self):
        """Manages the visibility of the top data panel."""
        if self.data_panel_container.isVisible():
            self.data_panel_container.hide()
            self.hidden_data_panel_container.show()
        else:
            self.hidden_data_panel_container.hide()
            self.data_panel_container.show()

    def _update_project_counter(self, projects: list):
        """Update the counter in the project group box title."""
        count = len(projects)
        self.project_group.setTitle(f"Projects[{count}]")
        self.hidden_project_group.setTitle(f"Projects[{count}]")

    def _update_board_counter(self, boards: list):
        """Update the counter in the board group box title."""
        count = len(boards)
        self.board_group.setTitle(f"Boards[{count}]")
        self.hidden_board_group.setTitle(f"Boards[{count}]")

    def _update_knot_counter(self, knots: list):
        """Update the counter in the knot group box title."""
        count = len(knots)
        self.knot_group.setTitle(f"Knots[{count}]")
        self.hidden_knot_group.setTitle(f"Knots[{count}]")
