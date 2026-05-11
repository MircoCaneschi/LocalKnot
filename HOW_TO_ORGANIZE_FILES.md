"""
INTEGRAZIONE DEI FILE VECCHI CON MVVM - GUIDA COMPLETA

Analisi di cosa fare con:
- controllers/data_panel_controller.py  (OLD - da rimpiazzare)
- core/data_models.py                   (USE - riutilizzare)
- core/database.py                      (USE - riutilizzare)

================================================================================
SITUAZIONE ATTUALE
================================================================================

controllers/data_panel_controller.py
───────────────────────────────────

✗ PROBLEMI con questo file:
  - ProjectsController manipola direttamente i widget della View
  - Handle_new_project(), handle_save_project() fanno UI manipulation
  - Tightly coupled: Controller conosce i widget specifici
  - Difficile da testare
  - Logica di business mescolata con UI code

Linea 17: self.data_panel.combo_box_projects.setEditable(True)
Linea 24: project_text = self.data_panel.combo_box_projects.currentText()
Linea 30: self.data_panel.project_msg.setText("Invalid project name!")

QUESTO È ESATTAMENTE CIÒ CHE MPVM RISOLVE!


core/data_models.py (DATACLASS)
───────────────────────────────

✓ BUONO - Strutture dati pure:

@dataclass
class Project:
    id_project: str      # PK
    species: str         # species of wood

@dataclass
class Board:
    id_board: int        # PK
    id_project: str      # FK
    height: float
    Base: float
    length: int
    ...

@dataclass
class Knot:
    id_knot: int         # PK
    id_board: int        # FK
    id_project: str      # FK
    x: int
    pith_z: int
    ...

QUESTO VA USATO NEL LAYER MODEL!


core/database.py (DATABASE MANAGER)
───────────────────────────────────

✓ BUONO - Gestione SQLite:

class DatabaseManager:
    def __init__(self, db_name="LocalKnotData.db")
    def get_connection()
    def create_tables()
    def add_project_db(id_project, species)
    ...

QUESTO VA USATO DAL VIEWMODEL!

================================================================================
ARCHITETTURA MVVM CORRETTA CON QUESTI FILE
================================================================================

                    DATA FLOW NUOVO MVVM

┌─────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION TIER                         │
│  gui/components/data_panel/                                        │
│  ├─ projects_view_mvvm.py                                          │
│  ├─ boards_view_mvvm.py                                            │
│  └─ knots_view_mvvm.py                                             │
│                                                                     │
│  View layer: UI widgets + binding                                  │
│  NO business logic                                                 │
└─────────────────────────────────────────────────────────────────────┘
         ↕ (Signals, Properties, Slots)
┌─────────────────────────────────────────────────────────────────────┐
│                        APPLICATION TIER                            │
│  mvvm/viewmodels/                                                  │
│  ├─ projects_viewmodel.py         (ProjectsViewModel)             │
│  ├─ boards_viewmodel.py           (BoardsViewModel)               │
│  └─ knots_viewmodel.py            (KnotsViewModel)                │
│                                                                    │
│  ViewModel layer: State management, Signals/Properties/Slots      │
│  Uses: core/database.py + core/data_models.py                    │
│  Uses: Presentation logic only                                   │
└─────────────────────────────────────────────────────────────────────┘
         ↕ (read/write data, transactions)
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA/PERSISTENCE TIER                       │
│  core/                                                             │
│  ├─ data_models.py                (Dataclass: Project/Board/Knot)│
│  ├─ database.py                   (DatabaseManager + SQL)         │
│  └─ [NEW] repository.py           (Repository Pattern)           │
│                                                                   │
│  Data layer: Pure data, persistence, business validation         │
│  NO UI knowledge, NO ViewModel knowledge                          │
└─────────────────────────────────────────────────────────────────────┘


================================================================================
COSA FARE CON OGNI FILE
================================================================================

1. controllers/data_panel_controller.py
   ════════════════════════════════════

   AZIONE: ❌ ELIMINARE (rimpiazzato da ViewModels)
   
   Il codice logico va trasferito a:
   - mvvm/viewmodels/projects_viewmodel.py   (le validazioni e logica)
   - mvvm/viewmodels/boards_viewmodel.py
   - mvvm/viewmodels/knots_viewmodel.py
   
   Esempio di migrazione:
   
   OLD (controllers/data_panel_controller.py):
   ───────────────────────────────────────────
   def handle_save_project(self):
       project_text = self.data_panel.combo_box_projects.currentText()
       if project_text == '':
           self.data_panel.project_msg.setText("Invalid!")
           self.data_panel.project_msg.show()
   
   
   NEW (mvvm/viewmodels/projects_viewmodel.py):
   ──────────────────────────────────────────
   @Slot()
   def handle_save_project(self):
       project_text = self._current_project
       if not project_text:
           self.project_error.emit("Invalid project name!")
           return
       # ...further logic...
       self.project_saved.emit(project_name)
   
   
   TIMELINE:
   ├─ Tieni il file come riferimento per ora
   └─ Elimina quando ViewModel è pronto


2. core/data_models.py
   ═══════════════════

   AZIONE: ✓ RIUTILIZZARE (NO MODIFICHE per ora)
   
   Questi dataclass vanno bene come sono:
   - @dataclass Project(id_project, species)
   - @dataclass Board(id_board, id_project, height, base, length, ...)
   - @dataclass Knot(id_knot, id_board, x, pith_z, pith_y, ...)
   
   PROBLEMA MINORE:
   - Board ha "Base" (maiuscolo) - usare "base" (minuscolo)
   - Knot ha "pitch_y" - usare "pith_y" (typo?)
   
   MIGLIORAMENTI FUTURI:
   ├─ Aggiungere __post_init__() per validazione
   ├─ Aggiungere to_dict() per serializzazione
   └─ Aggiungere from_dict() per deserializzazione
   
   COME USARE NEL MVVM:
   ├─ ViewModel importa da core.data_models
   ├─ ViewModel crea/modifica istanze di Project, Board, Knot
   ├─ ViewModel passa al DatabaseManager
   └─ ViewModel riceve indietro dal DatabaseManager


3. core/database.py
   ═════════════════

   AZIONE: ✓ RIUTILIZZARE + ESTENDERE
   
   Mantenere DatabaseManager.py come è:
   - __init__(): Connessione DB
   - get_connection(): Restituisce connessione
   - create_tables(): Schema SQLite
   - add_project_db(): Insert project
   
   AGGIUNGERE METODI:
   ├─ get_all_projects() -> List[Project]
   ├─ get_project(id) -> Project
   ├─ update_project(project: Project) -> bool
   ├─ delete_project(id) -> bool
   ├─ get_all_boards(project_id) -> List[Board]
   ├─ add_board(board: Board) -> bool
   ├─ get_all_knots(board_id) -> List[Knot]
   ├─ add_knot(knot: Knot) -> bool
   └─ ... (operazioni CRUD per tutte le entità)
   
   PATTERN REPOSITORY (NUOVO FILE):
   ┌─ Creare: core/repository.py
   ├─ Classe: ProjectRepository(DatabaseManager)
   ├─ Classe: BoardRepository(DatabaseManager)
   ├─ Classe: KnotRepository(DatabaseManager)
   └─ Interfaccia: IRepository (astratto)
   
   VANTAGGI Repository Pattern:
   - ViewModel non conosce SQL direttamente
   - Facile cambiare DB backend
   - Testabile con mock repository
   
   COME USARE NEL MVVM:
   ├─ ViewModel __init__: project_repo = ProjectRepository(db_manager)
   ├─ ViewModel slot: self.project_repo.save_project(project)
   └─ ViewModel riceve Exception se errore


================================================================================
STRUTTURA DIRECTORY FINALE
================================================================================

LocalKnot/
│
├── core/                              [DATA/PERSISTENCE TIER]
│   ├── __init__.py
│   ├── data_models.py                 ✓ MANTIENI (Dataclass)
│   ├── database.py                    ✓ MANTIENI + Estendi
│   └── repository.py                  ➕ CREA (Repository Pattern)
│
├── mvvm/                              [APPLICATION TIER]
│   ├── models/
│   │   └── __init__.py                ✓ MANTIENI (Domain Models)
│   │
│   └── viewmodels/
│       ├── projects_viewmodel.py      ✓ USA core/database.py + core/repository.py
│       ├── boards_viewmodel.py
│       └── knots_viewmodel.py
│
├── gui/                               [PRESENTATION TIER]
│   └── components/
│       └── data_panel/
│           ├── projects_view_mvvm.py  ✓ Bind a ProjectsViewModel
│           ├── boards_view_mvvm.py    ✓ Bind a BoardsViewModel
│           └── knots_view_mvvm.py     ✓ Bind a KnotsViewModel
│
├── controllers/                       [DEPRECATED]
│   └── data_panel_controller.py       ❌ ELIMINA quando MVVM pronto
│
└── MVVM_SUMMARY.md


================================================================================
ROADMAP DI IMPLEMENTAZIONE
================================================================================

PHASE 1: SETUP REPOSITORY PATTERN
──────────────────────────────────

1. Estendi core/database.py
   ├─ Aggiungi get_all_projects()
   ├─ Aggiungi get_all_boards(project_id)
   ├─ Aggiungi get_all_knots(board_id)
   ├─ Aggiungi add_project(project: Project)
   ├─ Aggiungi add_board(board: Board)
   ├─ Aggiungi add_knot(knot: Knot)
   └─ Aggiungi update/delete per ogni entità

2. Crea core/repository.py
   ├─ class ProjectRepository
   ├─ class BoardRepository
   ├─ class KnotRepository
   └─ Wrappa DatabaseManager con interfaccia pulita

3. Test database layer
   └─ Testa: adding/getting/updating/deleting project


PHASE 2: IMPLEMENT VIEWMODELS
──────────────────────────────

1. mvvm/viewmodels/projects_viewmodel.py
   ├─ __init__: Initialize repo = ProjectRepository(db_manager)
   ├─ Load initial data: self.projects = repo.get_all_projects()
   ├─ Implement slots: handle_new_project(), handle_save_project(), ...
   ├─ Emit signals: project_error, project_saved, ...
   └─ Test WITHOUT GUI

2. Stesso per boards_viewmodel.py e knots_viewmodel.py


PHASE 3: IMPLEMENT VIEWS
────────────────────────

1. gui/components/data_panel/projects_view_mvvm.py
   ├─ __init__(viewmodel: ProjectsViewModel)
   ├─ _setup_main_layout()
   ├─ _setup_hidden_layout()
   ├─ _bind_to_view_model()
   └─ Test WITH ViewModel


PHASE 4: INTEGRATE
───────────────────

1. main_window.py
   ├─ Create DatabaseManager
   ├─ Create ProjectRepository, BoardRepository, KnotRepository
   ├─ Create ViewModels (pass repos)
   ├─ Create Views (pass viewmodels)
   └─ Add views to layouts


PHASE 5: CLEANUP
─────────────────

1. Testa l'app completa
2. Elimina: controllers/data_panel_controller.py
3. Tieni old GUI files come reference (projects.py, boards.py, knots.py)
4. Archive/Delete quando sicuro


================================================================================
ESEMPIO DI INTEGRAZIONE: ProjectsViewModel + Repository
================================================================================

mvvm/viewmodels/projects_viewmodel.py:

    from core.repository import ProjectRepository
    from core.data_models import Project
    
    class ProjectsViewModel(QObject):
        project_error = Signal(str)
        project_saved = Signal(str)
        projects_changed = Signal(list)
        
        def __init__(self, repository: ProjectRepository):
            super().__init__()
            self.repo = repository
            self._projects = []
            self._load_projects_from_db()
        
        def _load_projects_from_db(self):
            """Load projects from database and cache them"""
            try:
                self._projects = self.repo.get_all_projects()
                self.projects_changed.emit(
                    [p.id_project for p in self._projects]
                )
            except Exception as e:
                self.project_error.emit(f"Failed to load projects: {str(e)}")
        
        @Slot()
        def handle_save_project(self):
            """Handle save project action"""
            # Get from View via properties
            project_name = self._current_project
            species_name = self._current_species
            
            # Validate
            if not project_name or not species_name:
                self.project_error.emit("Project and species are required")
                return
            
            # Create model
            project = Project(id_project=project_name, species=species_name)
            
            # Save to database via repository
            try:
                self.repo.add_project(project)
                self._projects.append(project)
                self.projects_changed.emit(
                    [p.id_project for p in self._projects]
                )
                self.project_saved.emit(project_name)
            except Exception as e:
                self.project_error.emit(f"Failed to save project: {str(e)}")


core/repository.py:

    from core.database import DatabaseManager
    from core.data_models import Project
    
    class ProjectRepository:
        """Interface to Project data operations"""
        
        def __init__(self, db_manager: DatabaseManager):
            self.db = db_manager
        
        def get_all_projects(self) -> list[Project]:
            """Fetch all projects from database"""
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id_project, species FROM project")
                rows = cursor.fetchall()
                return [Project(id_project=row[0], species=row[1]) 
                        for row in rows]
        
        def add_project(self, project: Project) -> bool:
            """Insert a new project into database"""
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO project (id_project, species) VALUES (?, ?)",
                    (project.id_project, project.species)
                )
                conn.commit()
                return True
        
        def delete_project(self, project_id: str) -> bool:
            """Delete a project"""
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM project WHERE id_project = ?", 
                              (project_id,))
                conn.commit()
                return True


gui/components/data_panel/projects_view_mvvm.py:

    from mvvm.viewmodels import ProjectsViewModel
    
    class ProjectsView:
        def __init__(self, view_model: ProjectsViewModel):
            self.view_model = view_model
            self.new_btn = QPushButton("New")
            self.combo_box_projects = QComboBox()
            # ... create widgets ...
            self._bind_to_view_model()
        
        def _bind_to_view_model(self):
            # View → ViewModel
            self.new_btn.clicked.connect(self.view_model.handle_new_project)
            
            # ViewModel → View
            self.view_model.project_error.connect(self._on_project_error)
            self.view_model.projects_changed.connect(self._on_projects_changed)
        
        def _on_projects_changed(self, projects: list):
            self.combo_box_projects.clear()
            self.combo_box_projects.addItems(projects)


main_window.py:

    from core.database import DatabaseManager
    from core.repository import ProjectRepository, BoardRepository, KnotRepository
    from mvvm.viewmodels import ProjectsViewModel, BoardsViewModel, KnotsViewModel
    from gui.components.data_panel import ProjectsView, BoardsView, KnotsView
    
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            
            # Setup database and repositories
            db = DatabaseManager()
            project_repo = ProjectRepository(db)
            board_repo = BoardRepository(db)
            knot_repo = KnotRepository(db)
            
            # Create ViewModels
            projects_vm = ProjectsViewModel(project_repo)
            boards_vm = BoardsViewModel(board_repo)
            knots_vm = KnotsViewModel(knot_repo)
            
            # Create Views
            projects_view = ProjectsView(projects_vm)
            boards_view = BoardsView(boards_vm)
            knots_view = KnotsView(knots_vm)
            
            # Add to UI
            self.main_layout.addWidget(projects_view.main_layout)
            self.main_layout.addWidget(boards_view.main_layout)
            self.main_layout.addWidget(knots_view.main_layout)


================================================================================
SUMMARY
================================================================================

FILE                          AZIONE          NOTE
────────────────────────────  ──────────────  ──────────────────────────
controllers/                  ❌ ELIMINA      Rimpiazzato da ViewModel
  data_panel_controller.py

core/                         ✓ MANTIENI      Riutilizza come M layer
  data_models.py              ✓ ESTENDI       Aggiungi CRUD methods
  database.py                 ➕ CREA         Repository pattern

mvvm/                         ✓ COMPLETA      Implementa bodies
  models/
  viewmodels/

gui/                          ✓ COMPLETA      Implementa UI + binding
  components/
    data_panel/


================================================================================
NEXT STEPS - LEGGI QUESTO
================================================================================

1. ✅ Hai già la struttura MVVM base

2. Devi creare core/repository.py
   └─ ProjectRepository, BoardRepository, KnotRepository

3. Devi estendere core/database.py
   └─ Aggiungi CRUD methods

4. Implementa bodies di:
   └─ mvvm/viewmodels/*.py
   └─ gui/components/data_panel/*_view_mvvm.py

5. Aggiorna main_window.py e main.py per usare MVVM

6. Testa e elimina file vecchi


La struttura è logica e scalabile! 🎉
"""

