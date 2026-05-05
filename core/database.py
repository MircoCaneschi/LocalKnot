import sqlite3

class DatabaseManager:
    def __init__(self, db_name="LocalKnotData.db"):
        self.db_name = db_name
        self.create_tables()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        # activates the foreign keyes, otherwise ON DELETE CASCADE would not work
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
                    species TEXT NOT NULL
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