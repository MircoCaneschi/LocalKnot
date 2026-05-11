"""
QUICK REFERENCE - Risposte rapide alle domande comuni

Salva questo file come bookmark mentale!
"""

# ============================================================================
# 🎯 COSA FARE CON I VECCHI FILE
# ============================================================================

VECCHI FILE                          AZIONE              DOVE VA
───────────────────────────────────  ─────────────────   ──────────────────
controllers/                         ❌ Elimina           archive/
  data_panel_controller.py           (rimpiazzato)       

core/                                ✓ Mantieni          core/
  data_models.py                     (riutilizza)        

core/                                ✓ Estendi            core/
  database.py                        (aggiungi CRUD)     

gui/components/data_panel/           ✓ Aggiungi nuovo    gui/components/
  projects.py, boards.py, knots.py   📦 ARCHIVE old      data_panel/


# ============================================================================
# 📁 FILE CHE SERVONO - LA VERITÀ VERA
# ============================================================================

LAYER 1: DATABASE
├─ core/database.py              ✓ ESISTE, estendi
├─ core/repository.py            ✅ CREATO, implementa
└─ core/data_models.py           ✓ ESISTE, completa

LAYER 2: LOGIC
├─ mvvm/viewmodels/projects_viewmodel.py    ✅ CREATO, implementa
├─ mvvm/viewmodels/boards_viewmodel.py      ✅ CREATO, implementa
└─ mvvm/viewmodels/knots_viewmodel.py       ✅ CREATO, implementa

LAYER 3: UI
├─ gui/components/data_panel/projects_view_mvvm.py  ✅ CREATO, implementa
├─ gui/components/data_panel/boards_view_mvvm.py    ✅ CREATO, implementa
└─ gui/components/data_panel/knots_view_mvvm.py     ✅ CREATO, implementa

INTEGRATION
├─ gui/main_window.py            🔴 DA AGGIORNARE
└─ main.py                        ✅ OK


# ============================================================================
# 🔥 TOP 10 MISTAKES DA EVITARE
# ============================================================================

❌ 1. Mettere Qt import in ViewModel
     ✓ Fix: NO "from PySide6.QtWidgets import ..."

❌ 2. Manipolare widget nel ViewModel
     ✓ Fix: Emetti signal, let View aggiorna

❌ 3. Logica di business nel View
     ✓ Fix: Metti tutto nel ViewModel

❌ 4. Model che conosce ViewModel
     ✓ Fix: Model SOLO dati pure

❌ 5. View che accessa direttamente Model
     ✓ Fix: SOLO attraverso ViewModel

❌ 6. Dimenticare di connettere signal
     ✓ Fix: self.signal.connect(slot)

❌ 7. Signal non emesso quando state cambia
     ✓ Fix: Aggiungi self.signal.emit() in slot

❌ 8. ViewModel che non sa di existence
     ✓ Fix: ViewModel riceve via __init__

❌ 9. Dimenticare @Slot() decorator
     ✓ Fix: @Slot() def handle_something(self):

❌ 10. Property senza notify signal
      ✓ Fix: @Property(type, notify=signal_name)


# ============================================================================
# 📋 CHECKLIST PRIMA DI IMPLEMENTARE
# ============================================================================

[ ] Ho creato core/repository.py
[ ] Ho capito ProjectRepository, BoardRepository, KnotRepository
[ ] Ho elencato tutti i CRUD methods
[ ] Ho capito che ViewModel USERÀ repository
[ ] Ho capito che View NON chiamerà database direttamente
[ ] Ho capito che Model NON importa Qt
[ ] Ho capito che ViewModel importa Qt (per Signal/Property/Slot)
[ ] Ho capito che View importa ViewModel
[ ] Ho capito come funcionano i signals
[ ] Ho testato un semplice Signal/Slot in Python


# ============================================================================
# 💻 COMANDI PREFIX (copy-paste pronti)
# ============================================================================

# Vedi struttura
tree -I '__pycache__|*.pyc|.venv' LocalKnot/

# Testa database
python -c "from core.database import DatabaseManager; db = DatabaseManager(); print('DB OK')"

# Testa repository
python -c "from core.repository import ProjectRepository; print('Repo OK')"

# Testa viewmodel (dopo implementazione)
python -c "from mvvm.viewmodels import ProjectsViewModel; print('VM OK')"

# Esegui app
python main.py

# Vedi import
python -m py_compile mvvm/viewmodels/projects_viewmodel.py

# Rimetti su path Python
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Semplice test signal/slot (copia nella console)
from PySide6.QtCore import QObject, Signal, Slot

class TestVM(QObject):
    message = Signal(str)
    @Slot()
    def send_message(self):
        self.message.emit("Hello!")

vm = TestVM()
vm.message.connect(lambda msg: print(f"Received: {msg}"))
vm.send_message()  # Output: Received: Hello!


# ============================================================================
# 🎲 DOMANDE VELOCI - RISPOSTE VELOCI
# ============================================================================

Q1: Come emetto un signal nel ViewModel?
A1: self.signal_name.emit(value)

Q2: Come connetto un button al ViewModel?
A2: self.button.clicked.connect(self.view_model.handle_button_click)

Q3: Come ricevo il signal nel View?
A3: self.view_model.signal_name.connect(self._on_signal_received)

Q4: Come leggo una Property dalla ViewModel?
A4: value = self.view_model.property_name

Q5: Come scrivo un Property della ViewModel?
A5: self.view_model.property_name = new_value

Q6: Cosa va in @Property decorator?
A6: @Property(type, notify=signal_name)

Q7: Cosa va in @Slot decorator?
A7: @Slot() - se ha parametri: @Slot(str) o @Slot(str, int)

Q8: Quando chiamo il database in ViewModel?
A8: Nel __init__ per carica dati, negli Slot per save/delete

Q9: Che cosa ritorna il database?
A9: Dataclass instances: Project, Board, Knot

Q10: Che cosa passa il database al ViewModel?
A10: List[Project], List[Board], List[Knot] (oppure None/Exception)

Q11: Che cosa passa il ViewModel al View?
A11: Signals e Properties - NIENTE metodi diretti

Q12: View chiama mai il database?
A12: NO! SOLO through ViewModel


# ============================================================================
# 🏗️ STRUTTURA DI UN VIEWMODEL (TEMPLATE)
# ============================================================================

from PySide6.QtCore import QObject, Signal, Slot, Property
from core.repository import ProjectRepository
from core.data_models import Project

class ProjectsViewModel(QObject):
    # ===== SIGNALS =====
    projects_changed = Signal(list)
    project_error = Signal(str)
    project_saved = Signal(str)
    
    # ===== CONSTRUCTOR =====
    def __init__(self, repository: ProjectRepository):
        super().__init__()
        self.repo = repository
        self._projects = []
        self._current_project = ""
        self._load_projects()
    
    # ===== PROPERTIES =====
    @Property(list, notify=projects_changed)
    def project_list(self) -> list:
        return [p.id_project for p in self._projects]
    
    @Property(str)
    def current_project(self) -> str:
        return self._current_project
    
    @current_project.setter
    def current_project(self, value: str):
        self._current_project = value
    
    # ===== SLOTS (from View) =====
    @Slot()
    def handle_save_project(self):
        try:
            project = Project(self._current_project, "")
            self.repo.add_project(project)
            self._projects.append(project)
            self.projects_changed.emit([p.id_project for p in self._projects])
            self.project_saved.emit(self._current_project)
        except Exception as e:
            self.project_error.emit(str(e))
    
    # ===== PRIVATE METHODS =====
    def _load_projects(self):
        try:
            self._projects = self.repo.get_all_projects()
            self.projects_changed.emit([p.id_project for p in self._projects])
        except Exception as e:
            self.project_error.emit(str(e))


# ============================================================================
# 🎨 STRUTTURA DI UNA VIEW (TEMPLATE)
# ============================================================================

from PySide6.QtWidgets import QPushButton, QComboBox, QLabel, QVBoxLayout
from mvvm.viewmodels import ProjectsViewModel

class ProjectsView:
    def __init__(self, view_model: ProjectsViewModel):
        self.view_model = view_model
        
        # Create widgets
        self.new_btn = QPushButton("New")
        self.combo_box = QComboBox()
        self.error_label = QLabel()
        self.main_layout = QVBoxLayout()
        
        # Bind to ViewModel
        self._bind_to_view_model()
    
    def _bind_to_view_model(self):
        # View → ViewModel (user actions)
        self.new_btn.clicked.connect(self.view_model.handle_save_project)
        
        # ViewModel → View (state changes)
        self.view_model.projects_changed.connect(self._on_projects_changed)
        self.view_model.project_error.connect(self._on_project_error)
    
    def _on_projects_changed(self, projects: list):
        self.combo_box.clear()
        self.combo_box.addItems(projects)
    
    def _on_project_error(self, error_msg: str):
        self.error_label.setText(error_msg)
        self.error_label.show()


# ============================================================================
# 🗂️ STRUTTURA DI UN REPOSITORY (TEMPLATE)
# ============================================================================

from core.database import DatabaseManager
from core.data_models import Project

class ProjectRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_all_projects(self) -> list:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_project, species FROM project")
            rows = cursor.fetchall()
            return [Project(id_project=row[0], species=row[1]) for row in rows]
    
    def add_project(self, project: Project) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO project (id_project, species) VALUES (?, ?)",
                (project.id_project, project.species)
            )
            conn.commit()
        return True


# ============================================================================
# 📚 READING ORDER - LEGGI IN QUESTO ORDINE
# ============================================================================

1. QUESTO FILE (quick reference)       5 min
2. HOW_TO_ORGANIZE_FILES.md            20 min
3. CHECKLIST_IMPLEMENTATION.md         20 min
4. MVVM_SUMMARY.md                     10 min

POI IMPLEMENTA FASE PER FASE DALLA CHECKLIST


# ============================================================================
# 🚀 FASE 1 - PARTENZA (da fare adesso)
# ============================================================================

COSA: Estendi core/database.py con metodi CRUD

TEMPLATE:

def get_all_projects(self) -> list:
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id_project, species FROM project")
        rows = cursor.fetchall()
        from core.data_models import Project
        return [Project(**dict(zip(['id_project', 'species'], row))) 
                for row in rows]

METODI DA AGGIUNGERE:
├─ get_all_projects()
├─ get_project(id) 
├─ add_project(project)
├─ update_project(project)
├─ delete_project(id)
├─ get_all_boards(project_id)
├─ add_board(board)
├─ delete_board(board_id, project_id)
├─ get_all_knots(board_id, project_id)
├─ add_knot(knot)
└─ delete_knot(knot_id, board_id, project_id)

TEMPO: 3-4 ore
DIFFICOLTÀ: ⭐⭐


# ============================================================================
# ⚡ QUICK START - SUBITO DOPO LETTURA
# ============================================================================

1. Apri core/database.py
2. Aggiungi metodo: def get_all_projects(self) -> list
3. Test con: python -c "from core.database import DatabaseManager; db = DatabaseManager(); print(db.get_all_projects())"
4. Procedi al prossimo metodo

Se errore:
- Leggi messaggio
- Controlla sintassi SQL
- Controlla import
- Fai debug con print statements


========
FINE
========

Quando pronto: Apri HOW_TO_ORGANIZE_FILES.md ⭐
"""

