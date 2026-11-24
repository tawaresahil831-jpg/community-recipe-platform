import os
import sqlite3
from typing import Optional, Any
from flask import g, current_app


def get_db_path() -> str:
    """Return configured database path."""
    if current_app:
        return current_app.config.get("DATABASE_PATH", "recipes.db")
    return os.getenv("DATABASE_PATH", "recipes.db")


def get_db() -> sqlite3.Connection:
    """
    Open and return a database connection for current request context.
    Configures row factory to sqlite3.Row and enables foreign key constraints.
    """
    if "db" not in g:
        db_path = get_db_path()
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db


def close_db(e: Optional[BaseException] = None) -> None:
    """Close the current database connection if open."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(db_path: Optional[str] = None) -> None:
    """
    Execute schema.sql script to initialize tables and indexes.
    Works standalone and inside application context.
    """
    schema_file = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    target_path = db_path or get_db_path()
    conn = sqlite3.connect(target_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()
