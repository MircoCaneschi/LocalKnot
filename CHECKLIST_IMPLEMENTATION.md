"""
CHECKLIST PRATICA - MIGRAZIONE MVVM

Segui questi passaggi nell'ordine per un'integrazione senza problemi.

===============================================================================
FASE 1: PREPARA CORE LAYER (Data Persistence)
===============================================================================

[ ] 1.1 Rivedi core/data_models.py
    └─ Esistono già @dataclass Project, Board, Knot
    └─ Nota: "Base" dovrebbe essere "base", "pitch_y" dovrebbe essere "pith_y"

[ ] 1.2 Estendi core/database.py con metodi CRUD
    
    Aggiungi a DatabaseManager:
    ├─ get_all_projects() -> List[Project]           (righe ~110)
    ├─ get_project(id) -> Optional[Project]
    ├─ update_project(project) -> bool
    ├─ delete_project(id) -> bool
    ├─ get_all_boards(project_id) -> List[Board]
    ├─ get_board(board_id, project_id) -> Optional[Board]
    ├─ add_board(board: Board) -> bool
    ├─ update_board(board) -> bool
    ├─ delete_board(board_id, project_id) -> bool
    ├─ get_all_knots(board_id, project_id) -> List[Knot]
    ├─ get_knot(knot_id, board_id, project_id) -> Optional[Knot]
    ├─ add_knot(knot: Knot) -> bool
    ├─ update_knot(knot) -> bool
    └─ delete_knot(knot_id, board_id, project_id) -> bool

[ ] 1.3 Implementa core/repository.py
    
    Implementa bodies di:
    ├─ ProjectRepository (6 metodi)
    │   ├─ get_all_projects()
    │   ├─ get_project_by_id(project_id)
    │   ├─ add_project(project)
    │   ├─ update_project(project)
    │   ├─ delete_project(project_id)
    │   └─ project_exists(project_id)
    │
    ├─ BoardRepository (6 metodi)
    │   ├─ get_all_boards(project_id)
    │   ├─ get_board_by_id(board_id, project_id)
    │   ├─ add_board(board)
    │   ├─ update_board(board)
    │   ├─ delete_board(board_id, project_id)
    │   └─ board_exists(board_id, project_id)
    │
    └─ KnotRepository (6 metodi)
        ├─ get_all_knots(board_id, project_id)
        ├─ get_knot_by_id(knot_id, board_id, project_id)
        ├─ add_knot(knot)
        ├─ update_knot(knot)
        ├─ delete_knot(knot_id, board_id, project_id)
        └─ knot_exists(knot_id, board_id, project_id)

[ ] 1.4 TEST: Testa core layer
    
    Crea test/test_repository.py:
    ├─ test_project_crud()
    ├─ test_board_crud()
    └─ test_knot_crud()
    
    $ python -m pytest test/test_repository.py -v


===============================================================================
FASE 2: IMPLEMENTA MODELS LAYER (mvvm/models)
===============================================================================

[ ] 2.1 Rivedi mvvm/models/__init__.py
    
    Qui definiamo i domain models SENZA Qt:
    ├─ Project
    ├─ Species
    ├─ Board
    └─ Knot

[ ] 2.2 Completa i bodies di Project
    
    In mvvm/models/__init__.py:
    ├─ Project.__init__(name, species)
    ├─ Project.validate_name(name) -> bool
    ├─ Project.__eq__(other)
    ├─ Project.__repr__()

[ ] 2.3 Completa gli altri models
    
    ├─ Species.__init__, validate_name, __eq__
    ├─ Board.__init__, validate_measurements, ...
    └─ Knot.__init__, validate_coordinates, ...

[ ] 2.4 TEST: Testa models layer
    
    $ python -c "from mvvm.models import Project; p = Project('Test', 'Oak'); print(p)"


===============================================================================
FASE 3: IMPLEMENTA VIEWMODELS LAYER (mvvm/viewmodels)
===============================================================================

[ ] 3.1 Completa ProjectsViewModel (mvvm/viewmodels/projects_viewmodel.py)
    
    Pattern da seguire:
    
    ├─ __init__(repository: ProjectRepository)
    │   ├─ super().__init__()
    │   ├─ self.repo = repository
    │   ├─ self._projects = []
    │   ├─ self._current_project = ""
    │   ├─ self._current_species = ""
    │   ├─ self._species_editable = False
    │   └─ self._load_projects_from_db()
    │
    ├─ Properties: @Property definizioni
    │   ├─ project_list (getter) -> List[str]
    │   ├─ species_list (getter) -> List[str]
    │   ├─ current_project (getter/setter)
    │   ├─ current_species (getter/setter)
    │   └─ species_editable (getter)
    │
    ├─ Slots: @Slot definizioni
    │   ├─ handle_new_project()
    │   ├─ handle_save_project()
    │   ├─ handle_add_species()
    │   ├─ handle_delete_project(name: str)
    │   └─ handle_modify_project(name: str)
    │
    └─ Private methods:
        ├─ _load_projects_from_db()
        ├─ _validate_project_name(name) -> (bool, str)
        ├─ _validate_species_name(name, is_new) -> (bool, str)
        └─ _clear_inputs()

[ ] 3.2 Implementa handle_new_project()
    
    @Slot()
    def handle_new_project(self):
        """Reset state for creating new project"""
        self._current_project = ""
        self._current_species = ""
        self._species_editable = True
        self.projects_changed.emit(...)  # notify view

[ ] 3.3 Implementa handle_save_project()
    
    @Slot()
    def handle_save_project(self):
        """Validate and save project"""
        # 1. Validate project name
        is_valid, error = self._validate_project_name(self._current_project)
        if not is_valid:
            self.project_error.emit(error)
            return
        
        # 2. Validate species
        is_valid, error = self._validate_species_name(
            self._current_species, self._species_editable
        )
        if not is_valid:
            self.species_error.emit(error)
            return
        
        # 3. Create and save project
        project = Project(self._current_project, self._current_species)
        try:
            if self.repo.add_project(project):
                self._projects.append(project)
                self.projects_changed.emit(
                    [p.id_project for p in self._projects]
                )
                self.project_saved.emit(self._current_project)
        except Exception as e:
            self.project_error.emit(str(e))

[ ] 3.4 Implementa gli altri slot
    
    ├─ handle_add_species(): Just set _species_editable = True
    ├─ handle_delete_project(name): repo.delete_project, emit signal
    └─ handle_modify_project(name): repo.update_project, emit signal

[ ] 3.5 Ripeti per BoardsViewModel e KnotsViewModel
    
    Stesso pattern, ma per Board e Knot


[ ] 3.6 TEST: Testa ViewModels senza GUI
    
    Crea test/test_viewmodels.py:
    ├─ Mock ProjectRepository
    ├─ Test ProjectsViewModel.handle_save_project()
    ├─ Verify signals emitted
    └─ $ python -m pytest test/test_viewmodels.py -v


===============================================================================
FASE 4: IMPLEMENTA VIEWS LAYER (gui/components/data_panel)
===============================================================================

[ ] 4.1 Completa ProjectsView (gui/components/data_panel/projects_view_mvvm.py)
    
    ├─ __init__(view_model: ProjectsViewModel)
    │   ├─ self.view_model = view_model
    │   ├─ Create all widgets
    │   ├─ _setup_main_layout()
    │   ├─ _setup_hidden_layout()
    │   └─ _bind_to_view_model()
    │
    ├─ _setup_main_layout()
    │   ├─ Create: new_btn, delete_btn, change_name_btn, save_btn
    │   ├─ Create: combo_box_projects, combo_box_species
    │   ├─ Create: add_species_btn
    │   ├─ Create: project_msg, species_msg labels
    │   ├─ Create: shift buttons
    │   └─ Arrange in layouts
    │
    ├─ _setup_hidden_layout()
    │   ├─ Similar to main layout, but minimized
    │
    ├─ _bind_to_view_model()
    │   ├─ Button clicks → ViewModel slots:
    │   │   self.new_btn.clicked.connect(vm.handle_new_project)
    │   │   self.save_btn.clicked.connect(vm.handle_save_project)
    │   │
    │   └─ ViewModel signals → View methods:
    │       vm.project_error.connect(self._on_project_error)
    │       vm.project_saved.connect(self._on_project_saved)
    │
    ├─ Signal handlers:
    │   ├─ _on_projects_changed(projects: list)
    │   ├─ _on_species_changed(species: list)
    │   ├─ _on_project_error(error_msg: str)
    │   ├─ _on_species_error(error_msg: str)
    │   ├─ _on_project_saved(name: str)
    │   └─ _on_species_added(name: str)
    │
    └─ Property readers:
        ├─ get_current_project() -> str
        ├─ get_current_species() -> str
        ├─ is_project_editable() -> bool
        └─ is_species_editable() -> bool

[ ] 4.2 Ripeti per BoardsView e KnotsView
    
    ├─ Stesso pattern
    ├─ Ma con campi diversi
    └─ (board_no, height, base, length, etc.)

[ ] 4.3 TEST: Testa Views con ViewModel
    
    Crea test/test_views.py:
    ├─ Create mock ViewModel
    ├─ Create View with mock
    ├─ Emit signal from mock
    ├─ Verify UI updated
    └─ $ python -m pytest test/test_views.py -v


===============================================================================
FASE 5: INTEGRAZIONE (main_window.py e main.py)
===============================================================================

[ ] 5.1 Aggiorna main_window.py
    
    In MainWindow.__init__():
    
    ├─ Import repositories e viewmodels
    ├─ Create: db = DatabaseManager()
    ├─ Create: project_repo = ProjectRepository(db)
    ├─ Create: board_repo = BoardRepository(db)
    ├─ Create: knot_repo = KnotRepository(db)
    ├─ Create: projects_vm = ProjectsViewModel(project_repo)
    ├─ Create: boards_vm = BoardsViewModel(board_repo)
    ├─ Create: knots_vm = KnotsViewModel(knot_repo)
    ├─ Create: projects_view = ProjectsView(projects_vm)
    ├─ Create: boards_view = BoardsView(boards_vm)
    ├─ Create: knots_view = KnotsView(knots_vm)
    └─ Add to layouts: self.main_layout.addWidget(...)

[ ] 5.2 Rimuovi dal main_window.py:
    
    ├─ Vecchia importazione di controllers
    ├─ Vecchie GUI components (projects.py, boards.py, knots.py)
    └─ Old code from MainWindow no longer needed

[ ] 5.3 Aggiorna main.py
    
    └─ main() rimane praticamente uguale
        └─ window = MainWindow()  (che ora usa MVVM internamente)

[ ] 5.4 TEST: Testa l'app completa
    
    $ python main.py
    └─ Test tutti i flussi:
        ├─ Creare nuovo progetto
        ├─ Selezionare progetto
        ├─ Aggiungere specie
        ├─ Salvare progetto
        ├─ Stessi per board e knot
        └─ Verificare database


===============================================================================
FASE 6: CLEANUP E ARCHIVIO
===============================================================================

[ ] 6.1 Testa tutto funziona
    
    ├─ $ python main.py
    ├─ Crea un progetto
    ├─ Verifica nel DB
    ├─ Chiudi app e riapri
    ├─ Progetto caricato? ✓
    └─ All good? Proceed to cleanup

[ ] 6.2 Archiva file vecchi
    
    mkdir archive/
    ├─ mv controllers/data_panel_controller.py archive/
    ├─ mv gui/components/data_panel/projects.py archive/
    ├─ mv gui/components/data_panel/boards.py archive/
    └─ mv gui/components/data_panel/knots.py archive/

[ ] 6.3 Elimina cartella controllers/ se vuota
    
    ├─ Check che nulla dipende da essa
    └─ rm -r controllers/

[ ] 6.4 Aggiorna README del progetto
    
    └─ Documenta la nuova architettura MVVM

[ ] 6.5 Commit finale
    
    git add -A
    git commit -m "Refactor: Complete MVVM migration from controller pattern"


===============================================================================
TEMPO STIMATO
===============================================================================

Fase 1 (Core Layer):        3-4 ore
Fase 2 (Models):            1 ora
Fase 3 (ViewModels):        4-6 ore
Fase 4 (Views):             3-4 ore
Fase 5 (Integration):       2-3 ore
Fase 6 (Cleanup):           30 min
─────────────────────────────────────
TOTALE:                     14-19 ore

Suggerimento: Procedi una fase al giorno, testiamo step by step.


===============================================================================
COMANDI UTILI
===============================================================================

Testa database layer:
    $ python -m pytest core/repository.py -v

Testa viewmodels:
    $ python -m pytest mvvm/viewmodels/ -v

Testa views:
    $ python -m pytest gui/components/data_panel/ -v

Esegui app:
    $ python main.py

Vedi struttura:
    $ tree -I '__pycache__|.venv'


===============================================================================
TROUBLESHOOTING
===============================================================================

Q: ImportError: No module named 'mvvm'
A: Assicurati che mvvm/ sia nel PYTHONPATH, o fai:
   $ export PYTHONPATH="${PYTHONPATH}:$(pwd)"

Q: Signal non emesso
A: Verifica che @Slot() decori i metodi nella View
   Q: E che signal.connect() sia corretto

Q: Database locked
A: Verifica che get_connection() con "with" block
   A: E che conn.commit() sia chiamato

Q: Vecchio controller ancora caricato
A: Eliminalo o muovilo in archive/
   A: Riavvia Python interpreter


===============================================================================
PROSSIMA AZIONE
===============================================================================

Leggi in questo ordine:

1. HOW_TO_ORGANIZE_FILES.md (questo spiega il layout)
2. MVVM_SUMMARY.md (overview del progetto)
3. mvvm/README.md (dettagli MVVM)
4. mvvm/ARCHITECTURE.md (approfondimento architettura)

POI INIZIA DA FASE 1 ✅

Buona implementazione! 🚀
"""

