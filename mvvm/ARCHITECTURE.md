"""
MVVM Architecture Documentation

This document explains the Model-View-ViewModel (MVVM) pattern implemented
in the LocalKnot application, demonstrating strict separation of concerns
and one-way data flow.

================================================================================
ARCHITECTURE OVERVIEW
================================================================================

The application is organized into three distinct layers:

    ┌─────────────────────────────────────────────────────────────────┐
    │                        VIEW LAYER (GUI)                         │
    │  - ProjectsView, BoardsView, KnotsView                          │
    │  - UI widgets only (buttons, combo boxes, line edits)           │
    │  - Binds to ViewModel Properties: @Property decorator           │
    │  - Connects to ViewModel Slots: .clicked.connect()             │
    │  - Listens to ViewModel Signals: project_error.connect()       │
    │  - NO business logic, NO direct data access                    │
    └─────────────────────────────────────────────────────────────────┘
                              ↕ (binding)
    ┌─────────────────────────────────────────────────────────────────┐
    │                      VIEWMODEL LAYER                            │
    │  - ProjectsViewModel, BoardsViewModel, KnotsViewModel           │
    │  - Qt Properties: read/write state exposed to View              │
    │  - Qt Signals: notify View of state changes                     │
    │  - Qt Slots: receive user actions from View                     │
    │  - NO QtWidgets dependencies                                    │
    │  - Transforms Model data for presentation                       │
    │  - Implements presentation logic (validation, formatting)       │
    └─────────────────────────────────────────────────────────────────┘
                              ↕ (data flow)
    ┌─────────────────────────────────────────────────────────────────┐
    │                       MODEL LAYER                              │
    │  - Project, Species, Board, Knot (data classes)                │
    │  - Pure business logic and data validation                     │
    │  - NO UI dependencies                                          │
    │  - Can be tested independently                                 │
    └─────────────────────────────────────────────────────────────────┘


================================================================================
DATA FLOW PATTERNS
================================================================================

1. USER CLICKS BUTTON (View → ViewModel → Model)
   ────────────────────────────────────────────

   User clicks "Save Project" button
         │
         ↓
   View emits signal: self.save_btn.clicked
         │
         ↓
   Connects to ViewModel Slot: @Slot() handle_save_project()
         │
         ↓
   ViewModel validates using Model.validate_name()
         │
         ↓
   If valid: ViewModel updates internal state
   If invalid: ViewModel emits error signal
         │
         ↓
   ViewModel emits Signal: project_saved or project_error
         │
         ↓
   View listens and updates UI accordingly


2. PROPERTY BINDING (View ↔ ViewModel)
   ──────────────────────────────────

   View reads property:
        current_project = self.view_model.current_project
   
   View writes property:
        self.view_model.current_project = user_input
   
   ViewModel defines property:
        @Property(str)
        def current_project(self) -> str:
            return self._current_project
        
        @current_project.setter
        def current_project(self, value: str):
            self._current_project = value
            self.project_changed.emit()


3. SIGNAL COMMUNICATION (ViewModel → View)
   ──────────────────────────────────────

   ViewModel state changes:
        def handle_save_project(self):
            # ... validation logic ...
            self.project_saved.emit(project_name)
   
   View listens:
        self.view_model.project_saved.connect(self._on_project_saved)
   
   View slot handles update:
        def _on_project_saved(self, project_name: str):
            self.project_msg.setText(f"{project_name} registered!")
            self.project_msg.show()


================================================================================
LAYER RESPONSIBILITIES
================================================================================

MODEL LAYER (mvvm/models/__init__.py)
────────────────────────────────────

Responsibilities:
- Store data
- Validate business rules
- Provide data contracts

Classes:
- Project: Represents a project with name and species
- Species: Represents a species
- Board: Board measurements and metadata
- Knot: Knot coordinates and properties

No Dependencies:
- NO PySide6 imports
- NO GUI knowledge
- NO ViewModel knowledge

Example:
    class Project:
        def __init__(self, name: str, species: str):
            self.name = name
            self.species = species
        
        def validate_name(self, name: str) -> bool:
            return bool(name) and len(name) > 0


VIEWMODEL LAYER (mvvm/viewmodels/)
──────────────────────────────────

Responsibilities:
- Manage presentation state
- Transform Model data for display
- Handle user interactions
- Validate user input
- Emit state changes

Components:
- QtCore.Property: Expose read/write state to View
- QtCore.Signal: Notify View of changes
- QtCore.Slot: Receive user actions from View

Features:
- ProjectsViewModel: Manage projects and species
- BoardsViewModel: Manage board measurements
- KnotsViewModel: Manage knot data
- NO QtWidgets imports (no combo boxes, buttons, etc.)
- Pure business/presentation logic

Example:
    class ProjectsViewModel(QObject):
        # Signal tells View state changed
        projects_changed = Signal(list)
        
        # Property exposes data
        @Property(list, notify=projects_changed)
        def project_list(self) -> List[str]:
            return self._projects
        
        # Slot receives user action
        @Slot()
        def handle_save_project(self):
            # Validation
            if not self._validate_project():
                self.project_error.emit("Invalid project")
                return
            
            # State change triggers signal
            self._projects.append(new_project)
            self.projects_changed.emit(self._projects)


VIEW LAYER (gui/components/data_panel/)
──────────────────────────────────────

Responsibilities:
- Present UI widgets
- Bind to ViewModel Properties
- Connect user interactions to ViewModel Slots
- Update UI when ViewModel Signals fire
- NO business logic

Components:
- ProjectsView: Projects UI and binding
- BoardsView: Boards UI and binding
- KnotsView: Knots UI and binding

Features:
- Pure presentation logic
- Declarative binding
- Event propagation
- Signal/Slot connections

Example:
    class ProjectsView:
        def __init__(self, view_model: ProjectsViewModel):
            self.view_model = view_model
            self.new_btn = QPushButton("New")
            # ... create other widgets ...
            self._bind_to_view_model()
        
        def _bind_to_view_model(self):
            # Connect button to ViewModel slot
            self.new_btn.clicked.connect(self.view_model.handle_new_project)
            
            # Connect ViewModel signal to view method
            self.view_model.project_error.connect(self._on_project_error)
        
        def _on_project_error(self, error_message: str):
            self.project_msg.setText(error_message)
            self.project_msg.show()


================================================================================
KEY ADVANTAGES OF MVVM
================================================================================

1. SEPARATION OF CONCERNS
   ──────────────────────
   - Model: Pure data/business logic
   - ViewModel: Presentation state
   - View: UI only
   - Each layer has single responsibility

2. TESTABILITY
   ──────────
   - Model can be tested without GUI
   - ViewModel can be tested without GUI
   - Mock ViewModel can test View bindings

3. REUSABILITY
   ──────────
   - Same ViewModel can be used by different Views
   - Model is independent of GUI framework
   - ViewModel logic is GUI-framework agnostic

4. MAINTAINABILITY
   ──────────────
   - Changes in business logic don't affect UI
   - UI changes don't affect business logic
   - Clear dependencies and data flow

5. DECOUPLING
   ────────
   - View has NO reference to Model
   - Model has NO reference to View or ViewModel
   - Only ViewModel knows about both layers
   - Qt Signal/Slot mechanism handles communication

6. TWO-WAY BINDING
   ──────────────
   - Properties automatically sync between View and ViewModel
   - No manual property synchronization needed
   - Qt handles the binding mechanism


================================================================================
BINDING PATTERNS IN DETAIL
================================================================================

1. SIGNAL BINDING (Action → State Change)
   ──────────────────────────────────────

   Button Click → Signal → ViewModel Slot → ViewModel Signal → View Update

   View code:
        self.new_btn.clicked.connect(self.view_model.handle_new_project)

   ViewModel code:
        @Slot()
        def handle_new_project(self):
            # Reset state
            self._current_project = ""
            self._projects_editable = True
            # Notify listeners
            self.projects_changed.emit(self._projects)

   View code:
        self.view_model.projects_changed.connect(self._on_projects_changed)

   View slot:
        def _on_projects_changed(self, projects: list):
            self.combo_box_projects.clear()
            self.combo_box_projects.addItems(projects)


2. PROPERTY BINDING (Bidirectional Data)
   ────────────────────────────────────

   ViewModel Property:
        @Property(str)
        def current_project(self) -> str:
            return self._current_project
        
        @current_project.setter
        def current_project(self, value: str):
            self._current_project = value
            self.current_changed.emit()

   View Write:
        self.view_model.current_project = self.combo_box_projects.currentText()

   View Read:
        project_name = self.view_model.current_project


3. ERROR/SUCCESS SIGNALS (Validation Feedback)
   ───────────────────────────────────────────

   ViewModel Signals:
        project_error = Signal(str)
        project_saved = Signal(str)

   ViewModel Slot:
        @Slot()
        def handle_save_project(self):
            is_valid, error_msg = self._validate_project_name(name)
            if not is_valid:
                self.project_error.emit(error_msg)
                return
            # Save logic
            self.project_saved.emit(name)

   View Listeners:
        self.view_model.project_error.connect(self._on_project_error)
        self.view_model.project_saved.connect(self._on_project_saved)

   View Handlers:
        def _on_project_error(self, msg: str):
            self.error_label.setText(msg)
            self.error_label.show()

        def _on_project_saved(self, name: str):
            self.success_label.setText(f"Saved: {name}")
            self.success_label.show()


================================================================================
DEPENDENCY GRAPH
================================================================================

        ┌─────────┐
        │  Model  │ (Pure data, no dependencies)
        └────┬────┘
             │ (imports to read/modify data)
             │
        ┌────▼─────────┐
        │  ViewModel   │ (Qt-aware, but NO QtWidgets)
        │              │
        │ Properties ──┬──→ View (read-only access)
        │ Signals    ──┼──→ View (notifications)
        │ Slots      ←─┘ View (user actions)
        └────┬─────────┘
             │
        ┌────▼───────────┐
        │  View (GUI)    │ (QtWidgets)
        │                │
        │ Binds to ──────→ ViewModel Properties
        │ Connects to ──→ ViewModel Slots
        │ Listens to ──→ ViewModel Signals
        └────────────────┘

Dependencies allowed:
    View → ViewModel ✓ (View knows about ViewModel)
    View → Model ✗ (View NEVER imports Model directly)
    ViewModel → Model ✓ (ViewModel uses Model)
    Model → anything ✗ (Model is independent)


================================================================================
COMMON MISTAKES TO AVOID
================================================================================

1. Putting business logic in View
   ──────────────────────────────
   ✗ BAD:
        def on_save_clicked(self):
            if not self.text.strip():
                return
            # Business logic in View!
            self.projects.append(self.text)

   ✓ GOOD:
        def on_save_clicked(self):
            self.view_model.handle_save_project()

2. Putting UI code in ViewModel
   ───────────────────────────
   ✗ BAD:
        class ProjectsViewModel:
            def handle_save(self):
                combo_box.addItem(name)  # QtWidgets in ViewModel!

   ✓ GOOD:
        class ProjectsViewModel:
            projects_changed = Signal(list)
            
            def handle_save(self):
                self.projects.append(name)
                self.projects_changed.emit(self.projects)

3. Two-way coupling between View and ViewModel
   ──────────────────────────────────────────
   ✗ BAD:
        view.ui_element = viewmodel.create_widget()

   ✓ GOOD:
        view._bind_to_view_model()  # Loose coupling via signals

4. Model knowing about ViewModel or View
   ───────────────────────────────────
   ✗ BAD:
        class Project:
            def __init__(self):
                self.ui_label = QLabel()  # Qt import in Model!

   ✓ GOOD:
        class Project:
            def __init__(self):
                self.name = ""
                self.species = ""


================================================================================
TESTING STRATEGY
================================================================================

Because of MVVM separation:

1. Test Model independently
   ─────────────────────────
   model = Project("Test", "Oak")
   assert model.validate_name("Test")
   assert not model.validate_name("")

2. Test ViewModel logic without GUI
   ────────────────────────────────
   viewmodel = ProjectsViewModel()
   viewmodel.handle_new_project()
   assert viewmodel.current_project == ""

3. Mock ViewModel and test View bindings
   ────────────────────────────────────
   mock_vm = MockProjectsViewModel()
   view = ProjectsView(mock_vm)
   mock_vm.projects_changed.emit(["Project1"])
   assert view.combo_box.itemText(0) == "Project1"

This structure makes the codebase highly testable and maintainable!
"""

