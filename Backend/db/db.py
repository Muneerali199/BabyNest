import sqlite3
import os
import fcntl
from flask import g

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(BASE_DIR, "db", "database.db")
SCHEMA_FILE = os.path.join(BASE_DIR, "schema.sql")
SETUP_LOCK_FILE = os.path.join(BASE_DIR, "db", ".setup.lock")

def open_db():
    if "db" not in g:
        first_time_setup()
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None) 
    if db is not None:
        db.close()

def first_time_setup():
    if not os.path.exists(DATABASE) or os.stat(DATABASE).st_size == 0:
        # Use file lock to prevent race condition during setup
        os.makedirs(os.path.dirname(SETUP_LOCK_FILE), exist_ok=True)
        with open(SETUP_LOCK_FILE, 'w') as lock_file:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                # Double-check after acquiring lock
                if not os.path.exists(DATABASE) or os.stat(DATABASE).st_size == 0:
                    with sqlite3.connect(DATABASE) as db:
                        with open(SCHEMA_FILE,"r") as f:
                            db.executescript(f.read())
                        db.commit()
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
