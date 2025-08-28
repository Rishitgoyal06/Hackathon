import sqlite3
import os
from flask import current_app, g

# -- DATABASE CONNECTION --

def get_db():
    """Gets a connection to the SQLite database. Creates one if it doesn't exist."""
    # 'g' is a special Flask object unique for each request.
    if 'db' not in g:
        # Create the path to the database file inside the 'instance' folder
        db_path = os.path.join(current_app.instance_path, 'school_attendance.db')
        # Connect to the SQLite database at that path
        g.db = sqlite3.connect(db_path)
        # This makes sqlite3 return rows that behave like dictionaries
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Closes the database connection at the end of a request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database by running the schema from models.py"""
    db = get_db()
    # Import the SQL string from models.py
    from app import models
    # Execute the SQL commands to create tables
    db.executescript(models.SQL_SCHEMA)
    db.commit()

# -- HELPER FUNCTIONS FOR QUERIES --

def query_db(query, args=(), one=False):
    """
    Helper function to run a SELECT query and get results.
    Usage:
        user = query_db('SELECT * FROM users WHERE id = ?', [1], one=True)
        all_users = query_db('SELECT * FROM users')
    """
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def modify_db(query, args=()):
    """
    Helper function to run INSERT, UPDATE, or DELETE queries.
    Usage:
        modify_db('INSERT INTO users (name, role) VALUES (?, ?)', ['Alice', 'Student'])
    """
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    cur.close()
    # Return the ID of the last row that was modified (useful for INSERTs)
    return cur.lastrowid