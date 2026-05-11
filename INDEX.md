"""
📑 INDEX - TUTTI I FILE MESSI A PUNTO

Questo è il file MAN-PAGE del progetto. Spiega tutto in una pagina.
"""

# ============================================================================
# ⭐ SCEGLI DA DOVE INIZIARE
# ============================================================================

SEI IN FRETTA? (5 min)
├─ Leggi: QUICK_REFERENCE.md
└─ Inizia subito: Fase 1, estendi core/database.py

HAI 30 MIN? (30 min)
├─ Leggi: QUICK_REFERENCE.md
├─ Leggi: HOW_TO_ORGANIZE_FILES.md
└─ Capito? Procedi a implementare

HAI 2 ORE? (2 ore)
├─ Leggi: ROADMAP_START_HERE.md
├─ Leggi: QUICK_REFERENCE.md
├─ Leggi: HOW_TO_ORGANIZE_FILES.md
├─ Leggi: CHECKLIST_IMPLEMENTATION.md
└─ Pronto a iniziare

VUOI CAPIRE TUTTO? (4+ ore)
├─ Leggi tutto in sequenza (vedi under)
└─ Perfetto per capire architettura profondamente


# ============================================================================
# 📚 LETTURA CONSIGLIATA - Ordine perfetto
# ============================================================================

👉 1. QUICK_REFERENCE.md
   └─ Top 10 mistakes, templates, quick answers
   └─ ⏱️ 5-10 min
   └─ Output: Sai i pattern MVVM

👉 2. ROADMAP_START_HERE.md
   └─ Panoramica completa, cosa fare, timeline
   └─ ⏱️ 10-15 min
   └─ Output: Sai il piano completo

👉 3. HOW_TO_ORGANIZE_FILES.md
   └─ Cosa fare con OGNI file, integrazioni, repository pattern
   └─ ⏱️ 20-30 min
   └─ Output: Sai esattamente cosa implementare

👉 4. CHECKLIST_IMPLEMENTATION.md
   └─ Step-by-step per 6 fasi, comandi, troubleshooting
   └─ ⏱️ 20 min (leggi ora, usa dopo)
   └─ Output: Hai checklist di controllo

[ OPZIONALE - Approfondimento ]

5. MVVM_SUMMARY.md
   └─ Overview completissimo dei file creati
   └─ ⏱️ 10 min

6. mvvm/README.md (in mvvm/ folder)
   └─ Riepilogo struttura MVVM
   └─ ⏱️ 10 min

7. mvvm/ARCHITECTURE.md (in mvvm/ folder)
   └─ PROFONDITÀ massima, 800+ righe
   └─ ⏱️ 30-40 min

8. mvvm/IMPLEMENTATION_GUIDE.md (in mvvm/ folder)
   └─ Esempi di migrazione da old code
   └─ ⏱️ 20 min

TOTALE LETTERA ESSENZIALE: 50-70 min
TOTALE CON APPROFONDIMENTO: 2-3 ore


# ============================================================================
# 📁 FILE STRUCTURE - DOVE TROVARLI
# ============================================================================

DOCUMENTATION FILES (leggi questi):
│
├─ QUICK_REFERENCE.md              ⭐ Top tips, mistakes, templates
├─ ROADMAP_START_HERE.md           ⭐ Mappa completa, ordine lettura
├─ HOW_TO_ORGANIZE_FILES.md        ⭐ Cosa fa ogni file, come organizzare
├─ CHECKLIST_IMPLEMENTATION.md     ⭐ Step-by-step fasi 1-6
│
└─ MVVM_SUMMARY.md                 📚 Overview file creati

MVVM DOCUMENTATION (per approfondimento):
│
└─ mvvm/
   ├─ README.md                    📚 Overview MVVM
   ├─ ARCHITECTURE.md              📚 Spiegazione profonda
   └─ IMPLEMENTATION_GUIDE.md       📚 Esempi pratici

SOURCE CODE (implementa questi):
│
├─ core/
│  ├─ database.py                   🔴 Estendi (CRUD methods)
│  ├─ repository.py                 🟡 Implementa (bodies)
│  └─ data_models.py                🟡 Completa (bodies)
│
├─ mvvm/
│  ├─ models/
│  │  └─ __init__.py                🟡 Completa (Project, Species, Board, Knot)
│  │
│  └─ viewmodels/
│     ├─ projects_viewmodel.py      🟡 Implementa bodies
│     ├─ boards_viewmodel.py        🟡 Implementa bodies
│     └─ knots_viewmodel.py         🟡 Implementa bodies
│
└─ gui/
   └─ components/
      └─ data_panel/
         ├─ projects_view_mvvm.py   🟡 Implementa UI + binding
         ├─ boards_view_mvvm.py     🟡 Implementa UI + binding
         └─ knots_view_mvvm.py      🟡 Implementa UI + binding


LEGEND:
🟢 ✅ Done (OK così)
🟡 🔴 TODO (devi implementare)
📚 Documentazione
⭐ Leggi per primo


# ============================================================================
# 🎯 COSA FARE ADESSO
# ============================================================================

STEP 1 (5 min): Leggi QUICK_REFERENCE.md
└─ Capisce patterns, mistakes, templates

STEP 2 (30 min): Leggi HOW_TO_ORGANIZE_FILES.md
└─ Capisce struttura e cosa fare con file

STEP 3 (20 min): Leggi CHECKLIST_IMPLEMENTATION.md
└─ Capisce sequenza di implementazione

STEP 4 (15 min): Apri CHECKLIST novamente
└─ Segui Fase 1 passo per passo

STEP 5 (3-4 ore): Implementa Fase 1
├─ Estendi core/database.py
├─ Aggiungi CRUD methods
├─ Testa con print statements
└─ Quando finito: Vai a Fase 2

[REPEAT PER FASI 2-6]

...

STEP N: Done! 🎉


# ============================================================================
# 🔥 MOST IMPORTANT PATTERNS
# ============================================================================

PATTERN 1: Signal da ViewModel a View
─────────────────────────────────────
ViewModel:
    project_error = Signal(str)  # Dichiara signal

    @Slot()
    def handle_save(self):
        if not valid:
            self.project_error.emit(error_msg)  # Emetti

View:
    self.view_model.project_error.connect(self._on_error)  # Connetti

    def _on_error(self, msg: str):
        self.label.setText(msg)  # Aggiorna UI


PATTERN 2: Property da ViewModel a View
────────────────────────────────────────
ViewModel:
    @Property(str)
    def current_name(self) -> str:
        return self._name

    @current_name.setter
    def current_name(self, value: str):
        self._name = value
        self.name_changed.emit()

View:
    text = self.view_model.current_name  # Leggi
    self.view_model.current_name = user_input  # Scrivi


PATTERN 3: Slot da View a ViewModel
────────────────────────────────────
View:
    self.save_btn.clicked.connect(self.view_model.handle_save_project)

ViewModel:
    @Slot()
    def handle_save_project(self):
        # Logica qui
        pass


PATTERN 4: Repository per Data Access
──────────────────────────────────────
ViewModel:
    def __init__(self, repository):
        self.repo = repository

    @Slot()
    def handle_save(self):
        project = Project(name, species)
        self.repo.add_project(project)  # ← Use repository

Repository:
    def add_project(self, project: Project) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO project...")
            conn.commit()
        return True


# ============================================================================
# ⚠️ TOP 5 COSE DA RICORDARE
# ============================================================================

1️⃣  Model = PURE DATI (NO Qt)
    └─ core/data_models.py (Project, Board, Knot dataclass)

2️⃣  ViewModel = LOGICA APP (USE Qt signals/properties but NO QtWidgets)
    └─ mvvm/viewmodels/ (ProjectsViewModel, BoardsViewModel, KnotsViewModel)

3️⃣  View = SOLO UI (QtWidgets + binding)
    └─ gui/components/data_panel/ (ProjectsView, BoardsView, KnotsView)

4️⃣  Repository = INTERFACE a DB (ViewModel NON conosce SQL)
    └─ core/repository.py (ProjectRepository, BoardRepository, KnotRepository)

5️⃣  Signal/Slot/Property = Comunicazione lecitamente (NO tight coupling)
    └─ View signals ← → ViewModel slots
    └─ View properties ← → ViewModel properties


# ============================================================================
# 🏁 FINE DEL VIAGGIO
# ============================================================================

Quando finito tutto:

✅ core/database.py          → Ha CRUD methods
✅ core/repository.py        → Ha ProjectRepository, boardRepository, KnotRepository
✅ core/data_models.py       → Completo
✅ mvvm/models/              → Completo
✅ mvvm/viewmodels/          → Completo con logica
✅ gui/components/data_panel/ → Completo con UI + binding
✅ gui/main_window.py        → Aggiornato per MVVM
✅ controllers/              → Eliminato
✅ Vecchi file              → Archiviati

Result: UN'APP MVVM COMPLETA E TESTABILE! 🎉


# ============================================================================
# 📞 AIUTO RAPIDO
# ============================================================================

Ho errore ImportError
├─ Verifica che PYTHONPATH include il progetto
├─ $ export PYTHONPATH="${PYTHONPATH}:$(pwd)"
└─ Leggi: HOW_TO_ORGANIZE_FILES.md - TROUBLESHOOTING

Non capisco dove mettere il codice
├─ Guarda il TEMPLATE in QUICK_REFERENCE.md
└─ Segui il CHECKLIST in CHECKLIST_IMPLEMENTATION.md

Non funziona il binding
├─ Verifica signal.connect() è chiamato
├─ Verifica @Slot() decora il metodo ricevente
└─ Leggi: mvvm/ARCHITECTURE.md - BINDING PATTERNS

Database non funziona
├─ Test repository direttamente
├─ Verifica SQL syntax
└─ Aggiungi print statements

Confuso sulla struttura
├─ Leggi HOW_TO_ORGANIZE_FILES.md - ARCHITECTURE DIAGRAM
└─ Leggi MVVM_SUMMARY.md - FILE PURPOSES


# ============================================================================
# 🚀 BUON DIVERTIMENTO!
# ============================================================================

Inizia qui:
1. Leggi QUICK_REFERENCE.md (5 min)
2. Poi HOW_TO_ORGANIZE_FILES.md (30 min)
3. Poi CHECKLIST_IMPLEMENTATION.md (20 min)
4. Poi? → Apperatura in editor, inizia Fase 1!

Il journey di MVVM starts now! 🎯

Questions? Le risposte sono nei file. 😎
"""

