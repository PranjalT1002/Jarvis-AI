import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "memory.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Notes Table
    c.execute("""CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, timestamp TEXT)""")
    # Reminders Table
    c.execute("""CREATE TABLE IF NOT EXISTS reminders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, trigger_time TEXT, is_active INTEGER)""")
    # Chat History Table for long term memory
    c.execute("""CREATE TABLE IF NOT EXISTS chat_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT, timestamp TEXT)""")
    conn.commit()
    conn.close()


def add_note(content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO notes (content, timestamp) VALUES (?, ?)",
        (content, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_notes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, content FROM notes")
    notes = c.fetchall()
    conn.close()
    return notes


def delete_note(note_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()


def add_reminder(content, trigger_time):
    # trigger_time should be a string in ISO format (e.g. 2023-10-27T14:30:00)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO reminders (content, trigger_time, is_active) VALUES (?, ?, 1)",
        (content, trigger_time),
    )
    conn.commit()
    conn.close()


def get_active_reminders():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, content, trigger_time FROM reminders WHERE is_active=1")
    reminders = c.fetchall()
    conn.close()
    return reminders


def mark_reminder_done(reminder_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE reminders SET is_active=0 WHERE id=?", (reminder_id,))
    conn.commit()
    conn.close()


def log_chat(role, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO chat_history (role, content, timestamp) VALUES (?, ?, ?)",
        (role, content, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_recent_chat_context(limit=10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT role, content FROM chat_history ORDER BY id DESC LIMIT ?", (limit,)
    )
    history = c.fetchall()
    conn.close()
    return list(reversed([{"role": row[0], "content": row[1]} for row in history]))


# Initialize the db when the module is imported
init_db()
