"""
SQLite database operations
Developer: @gotweeds | Owner: Syed Rehan
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Any

DB_FILE = 'usernames.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usernames (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            claimed_at TIMESTAMP,
            last_checked TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_username(username: str, user_id: int) -> bool:
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('INSERT INTO usernames (username, user_id) VALUES (?, ?)',
                  (username.lower(), user_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def remove_username(username: str, user_id: int) -> bool:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM usernames WHERE username = ? AND user_id = ? AND status = "pending"',
              (username.lower(), user_id))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_pending_usernames() -> List[Dict[str, Any]]:
    """Return list of pending usernames with user_id"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT username, user_id FROM usernames WHERE status = "pending"')
    rows = c.fetchall()
    conn.close()
    return [{'username': r[0], 'user_id': r[1]} for r in rows]

def mark_claimed(username: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        UPDATE usernames 
        SET status = 'claimed', claimed_at = CURRENT_TIMESTAMP 
        WHERE username = ?
    ''', (username.lower(),))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def update_last_checked(username: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        UPDATE usernames 
        SET last_checked = CURRENT_TIMESTAMP 
        WHERE username = ?
    ''', (username.lower(),))
    conn.commit()
    conn.close()

def get_all_usernames(user_id: int) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT username, status, added_at, claimed_at 
        FROM usernames 
        WHERE user_id = ?
        ORDER BY added_at DESC
    ''', (user_id,))
    rows = c.fetchall()
    conn.close()
    return [
        {
            'username': r[0],
            'status': r[1],
            'added_at': r[2],
            'claimed_at': r[3]
        }
        for r in rows
    ]

def get_stats(user_id: int) -> Dict[str, int]:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM usernames WHERE user_id = ?', (user_id,))
    total = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM usernames WHERE user_id = ? AND status = "pending"', (user_id,))
    pending = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM usernames WHERE user_id = ? AND status = "claimed"', (user_id,))
    claimed = c.fetchone()[0]
    conn.close()
    return {'total': total, 'pending': pending, 'claimed': claimed}

def clear_pending(user_id: int) -> int:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM usernames WHERE user_id = ? AND status = "pending"', (user_id,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected
