"""
MVVM Refactoring Guide: LocalKnot Application

This guide shows the new MVVM structure and how it replaces the old code.

================================================================================
NEW DIRECTORY STRUCTURE
================================================================================

LocalKnot/
│
├── mvvm/                          # NEW MVVM Architecture
│   ├── __init__.py
│   ├── ARCHITECTURE.md            # Documentation (this file explains patterns)
│   │
│   ├── models/
│   │   ├── __init__.py            # Project, Species, Board, Knot (DATA MODELS)
│   │   │                          # Pure business logic - NO GUI dependencies
│   │
│   └── viewmodels/
│       ├── __init__.py
│       ├── projects_viewmodel.py  # ProjectsViewModel (PRESENTATION STATE)
│       ├── boards_viewmodel.py    # BoardsViewModel
│       └── knots_viewmodel.py     # KnotsViewModel
│
├── gui/
│   ├── main_window.py             # (Updated to use MVVM ViewModels)
│   │
│   └── components/
│       └── data_panel/
│           ├── projects.py        # OLD - Keep for reference
│           ├── projects_view_mvvm.py  # NEW - MVVM Pattern
│           │
│           ├── boards.py          # OLD - Keep for reference
│           ├── boards_view_mvvm.py    # NEW - MVVM Pattern
│           │
│           ├── knots.py           # OLD - Keep for reference
│           └── knots_view_mvvm.py     # NEW - MVVM Pattern
│
├── controllers/                   # OLD - Will be replaced by ViewModels
│   └── data_panel_controller.py   # (Keep as reference during transition)
│
└── core/                          # Existing (database, models)
    ├── database.py
    └── data_models.py


================================================================================
FILE PURPOSES
================================================================================

MODEL LAYER (mvvm/models/__init__.py)
────────────────────────────────────

Contains basic data classes representing domain entities:

    class Project:
        """Represents a project with name and species"""
        name: str
        species: str
        def validate_name(name: str) -> bool: ...

    class Species:
        """Represents a species entity"""
        name: str  
        def validate_name(name: str) -> bool: ...

    class Board:
        """Represents board measurements within a project"""
        board_no: int | str
        height: float
        base: float
        length: float
        def validate_measurements() -> bool: ...

    class Knot:
        """Represents knot data within a board"""
        knot_no: int | str
        x: float
        pith_z: float
        pith_y: float
        is_fake_pith: bool
        def validate_coordinates() -> bool: ...

KEY POINTS:
- Pure Python classes
- NO PySide6 imports
- NO Qt signals or properties
- Only data storage and simple validation
- Can exist independently of GUI


VIEWMODEL LAYER (mvvm/viewmodels/*.py)
──────────────────────────────────────

Contains presentation state management:

    class ProjectsViewModel(QObject):
        # Signals notify View of state changes
        projects_changed = Signal(list)
        project_error = Signal(str)
        project_saved = Signal(str)
        
        # Properties expose state to View
        @Property(list, notify=projects_changed)
        def project_list(self) -> List[str]: ...
        
        # Slots receive user actions from View
        @Slot()
        def handle_new_project(self): ...
        
        @Slot()
        def handle_save_project(self): ...

KEY POINTS:
- Inherits from QObject (for signals/properties/slots)
- NO QtWidgets imports (no buttons, combo boxes, etc.)
- Contains NO UI code
- Transforms Model data for presentation
- Implements business logic (validation)
- Communicates with View via Qt signals/properties
- Can be tested without GUI


VIEW LAYER (gui/components/data_panel/*_view_mvvm.py)
─────────────────────────────────────────────────────

Contains UI and bindings to ViewModel:

    class ProjectsView:
        def __init__(self, view_model: ProjectsViewModel):
            self.view_model = view_model
            # Create UI widgets
            self.new_btn = QPushButton("New")
            self.combo_box_projects = QComboBox()
            # ... create other widgets ...
            
            # Connect View to ViewModel
            self._bind_to_view_model()
        
        def _bind_to_view_model(self):
            # Button click → ViewModel Slot
            self.new_btn.clicked.connect(self.view_model.handle_new_project)
            
            # ViewModel Signal → View update
            self.view_model.project_error.connect(self._on_project_error)
        
        def _on_project_error(self, error_message: str):
            self.error_label.setText(error_message)

KEY POINTS:
- Pure UI code (buttons, combo boxes, layouts)
- Contains NO business logic
- Binds to ViewModel Properties
- Connects to ViewModel Slots
- Listens to ViewModel Signals
- NO direct data access


================================================================================
MIGRATION PATH: OLD → NEW
================================================================================

OLD ARCHITECTURE
────────────────

    View (projects.py)
          │
          ├─→ Controller (data_panel_controller.py)
          │   └─→ Directly manipulates View widgets
          │
          └─→ Model data (core/data_models.py)
               └─→ Direct access from Controller

PROBLEMS:
- Controller tightly coupled to View widgets
- Hard to test without GUI
- Business logic mixed with UI manipulation
- Difficult to reuse logic with different UI


NEW ARCHITECTURE (MVVM)
──────────────────────

    View (projects_view_mvvm.py)
         │
         ├─ Binds to ──→ ViewModel (projects_viewmodel.py)
         │               └─ Uses ──→ Model (models/__init__.py)
         │
         └─ Signals/Properties ──→ Loose coupling
                                  Unit testable


BENEFITS:
- View and ViewModel are independently testable
- ViewModel has zero GUI dependencies
- Easy to swap implementations
- Reusable presentation logic
- Clear data flow


================================================================================
CONVERSION EXAMPLE: Projects
================================================================================

OLD CODE (Controller-based)
────────────────────────────

FILE: controllers/data_panel_controller.py

    class ProjectsController:
        def __init__(self, data_panel_obj, hidden_panel_obj):
            self.data_panel = data_panel_obj.projects_gui
            self.data_panel.new_btn.clicked.connect(self.handle_new_project)
            self.data_panel.save_btn.clicked.connect(self.handle_save_project)
        
        def handle_new_project(self):
            self.data_panel.combo_box_projects.setEditable(True)
            self.data_panel.combo_box_projects.clearEditText()
            # PROBLEM: Controller directly manipulates View widgets!
        
        def handle_save_project(self):
            project_text = self.data_panel.combo_box_projects.currentText()
            # Complex validation logic mixed with UI code
            if project_text == '' or self.data_panel.combo_box_projects.findText(...) != -1:
                self.data_panel.project_msg.setText("Invalid project name!")
                self.data_panel.project_msg.show()
                return
            # Save logic


NEW CODE (MVVM-based)
────────────────────

FILE: mvvm/viewmodels/projects_viewmodel.py

    class ProjectsViewModel(QObject):
        # Declare state change signals
        projects_changed = Signal(list)
        project_error = Signal(str)
        project_saved = Signal(str)
        
        # Expose data via Properties
        @Property(list, notify=projects_changed)
        def project_list(self) -> List[str]:
            return self._projects
        
        # Handle user actions via Slots
        @Slot()
        def handle_new_project(self):
            self._current_project = ""
            self._species_editable = True
            # NO direct widget manipulation!
        
        @Slot()
        def handle_save_project(self):
            name = self._current_project
            is_valid, error_msg = self._validate_project_name(name)
            if not is_valid:
                self.project_error.emit(error_msg)
                return
            self._projects.append(name)
            self.projects_changed.emit(self._projects)
            self.project_saved.emit(name)


FILE: gui/components/data_panel/projects_view_mvvm.py

    class ProjectsView:
        def __init__(self, view_model: ProjectsViewModel):
            self.view_model = view_model
            
            # Create UI widgets
            self.new_btn = QPushButton("New+")
            self.combo_box_projects = QComboBox()
            self.project_msg = QLabel()
            # ... more widgets ...
            
            # Establish bindings
            self._bind_to_view_model()
        
        def _bind_to_view_model(self):
            # Connect View → ViewModel (user actions)
            self.new_btn.clicked.connect(self.view_model.handle_new_project)
            
            # Connect ViewModel → View (state changes)
            self.view_model.project_error.connect(self._on_project_error)
            self.view_model.projects_changed.connect(self._on_projects_changed)
        
        def _on_project_error(self, error_message: str):
            self.project_msg.setText(error_message)
            self.project_msg.show()
        
        def _on_projects_changed(self, projects: list):
            self.combo_box_projects.clear()
            self.combo_box_projects.addItems(projects)


DIFFERENCE SUMMARY:

    └─ Controller directly manipulated widgets
        └─ ViewModel emits signals that View listens to
            └─ Clean separation: no widget knowledge in ViewModel


================================================================================
KEY PATTERNS IN ACTION
================================================================================

PATTERN 1: User Click → Validation → UI Update
────────────────────────────────────────────

User clicks Save button
    │
    ├─→ View code: self.save_btn.clicked.connect(self.view_model.handle_save_project)
    │
    ├─→ ViewModel Slot: @Slot() def handle_save_project(self):
    │                       if not self._validate():
    │                           self.project_error.emit(error)
    │
    ├─→ View listens: self.view_model.project_error.connect(self._on_error)
    │
    └─→ View updates: def _on_error(self, msg): self.error_label.setText(msg)


PATTERN 2: Property Binding (Bidirectional)
────────────────────────────────────────────

ViewModel Property:
    @Property(str)
    def current_project(self) -> str:
        return self._current_project
    
    @current_project.setter
    def current_project(self, value: str):
        self._current_project = value

View Read:
    project_name = self.view_model.current_project

View Write:
    self.view_model.current_project = self.combo_box.currentText()


PATTERN 3: Dynamic List Updates
──────────────────────────────

ViewModel modifies list:
    self._projects.append(new_project)
    self.projects_changed.emit(self._projects)  # Signal that list changed

View listens:
    self.view_model.projects_changed.connect(self._on_projects_changed)

View updates UI:
    def _on_projects_changed(self, projects: list):
        self.combo_box.clear()
        self.combo_box.addItems(projects)


================================================================================
TESTING MVVM COMPONENTS
================================================================================

TEST 1: Model (Pure unit testing)
────────────────────────────────

    def test_project_validation():
        project = Project("Test Project", "Oak")
        assert project.validate_name("Test Project")
        assert not project.validate_name("")
        assert not project.validate_name("   ")


TEST 2: ViewModel (No GUI required)
──────────────────────────────────

    def test_projects_viewmodel():
        viewmodel = ProjectsViewModel()
        
        # Test that signals are emitted
        signal_spy = SignalSpy(viewmodel.project_saved)
        
        viewmodel.handle_save_project()  # Should emit signal
        assert signal_spy.count() > 0


TEST 3: View (With Mock ViewModel)
─────────────────────────────────

    def test_projects_view_error_display():
        mock_vm = MockProjectsViewModel()
        view = ProjectsView(mock_vm)
        
        # Simulate error from ViewModel
        mock_vm.project_error.emit("Invalid name")
        
        # Check View updated
        assert view.project_msg.isVisible()
        assert "Invalid name" in view.project_msg.text()


================================================================================
NEXT STEPS FOR IMPLEMENTATION
================================================================================

1. Complete Model classes (mvvm/models/__init__.py)
   - Implement data attributes
   - Implement validation methods
   - Add to_dict() / from_dict() if persistence needed

2. Complete ViewModel classes
   - Implement Properties with backing fields
   - Implement Slots with business logic
   - Connect to database/repository layer

3. Complete View classes
   - Implement _setup_main_layout() - create widgets
   - Implement _setup_hidden_layout() - create widgets
   - Implement signal handlers - update UI

4. Update main_window.py
   - Instantiate ViewModels
   - Pass ViewModels to View constructors
   - Connect Views to main layout

5. Update main.py
   - Create ViewModels as application singletons or per-view
   - Pass to main window

6. Remove/Archive old code
   - Move controllers/data_panel_controller.py to archive
   - Keep old GUI components as reference during transition

7. Add unit tests
   - Test Models independently
   - Test ViewModels without GUI
   - Test View bindings with mock ViewModels

================================================================================
"""

