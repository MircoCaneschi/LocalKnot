import sqlite3
import os
import platform
from pathlib import Path


class DatabaseManager:
    def __init__(self, db_name="LocalKnotData.db"):
        self.db_path = self._get_db_path(db_name)
        self.create_tables()

    @staticmethod
    def _get_db_path(db_name):
        app_name = "KnotCalc"

        # Determine the standard user data directory based on the OS
        if platform.system() == 'Windows':
            base_dir = Path(os.getenv('LOCALAPPDATA', os.path.expanduser('~')))
        elif platform.system() == 'Darwin':  # macOS
            base_dir = Path(os.path.expanduser('~/Library/Application Support'))
        else:  # Linux/Unix
            base_dir = Path(os.path.expanduser('~/.local/share'))

        # Create the full path
        app_dir = base_dir / app_name

        # Create the folder if it does not exist
        app_dir.mkdir(parents=True, exist_ok=True)

        return app_dir / db_name

    def get_connection(self):
        # Use the dynamic path
        conn = sqlite3.connect(str(self.db_path))
        # # CRITICAL: Enable foreign keys, otherwise ON DELETE CASCADE will not work
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def create_tables(self):
        # with the "with" block, the code automatically commits or rollback the transaction, even if an error occurs
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # project table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS project (
                    id_project TEXT PRIMARY KEY,
                    species TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # BOARD table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS board (
                    id_board INTEGER NOT NULL,
                    id_project TEXT NOT NULL,
                    height REAL NOT NULL, 
                    base REAL NOT NULL,
                    length INTEGER NOT NULL,
                    testpos INTEGER ,
                    image_path TEXT,
                    PRIMARY KEY (id_board, id_project),
                    FOREIGN KEY (id_project) REFERENCES project (id_project) ON DELETE CASCADE
                )
            ''')

            # KNOT table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knot (
                    id_nodo INTEGER NOT NULL,
                    id_board INTEGER NOT NULL,
                    id_project TEXT NOT NULL,
                    x INTEGER NOT NULL,
                    pith_z INTEGER,
                    pith_y INTEGER,
                    comment TEXT,
                    fake_pith BOOLEAN,
                    
                    side1_z1 INTEGER NOT NULL,
                    side1_z2 INTEGER NOT NULL,
                    side1_dmin INTEGER NOT NULL,
                    
                    side2_z1 INTEGER NOT NULL,
                    side2_z2 INTEGER NOT NULL,
                    side2_dmin INTEGER NOT NULL,
                    
                    side3_z1 INTEGER NOT NULL,
                    side3_z2 INTEGER NOT NULL,
                    side3_dmin INTEGER NOT NULL,
                    
                    side4_z1 INTEGER NOT NULL,
                    side4_z2 INTEGER NOT NULL,
                    side4_dmin INTEGER NOT NULL,
                    PRIMARY KEY (id_nodo, id_board, id_project),
                    FOREIGN KEY (id_board, id_project) REFERENCES board (id_board, id_project) ON DELETE CASCADE
                )
            ''')
            conn.commit()

    #--------TRANSACTIONS---------

    def add_project_db(self, id_project, species, db_name):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO project (id_project, species) VALUES (?, ?)
            ''', (id_project, species))
            conn.commit()