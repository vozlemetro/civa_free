import sqlite3

def init_db():
    conn = sqlite3.connect("accounts.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            password TEXT,
            proxy TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confirmed INTEGER DEFAULT 0,
            claimed INTEGER DEFAULT 0,
            issued INTEGER DEFAULT 0
        );
    """)
    conn.commit()
    conn.close()