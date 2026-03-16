"""
auth.py — SQLite based auth for Streamlit Cloud deployment
"""
import sqlite3
import hashlib
import os

DB_PATH = "deepguard_users.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    if not get_user("admin"):
        register_user("admin", "admin@123", role="admin")
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_credentials(username: str, password: str) -> bool:
    user = get_user(username.strip().lower())
    if user and user["is_active"] and user["password_hash"] == hash_password(password):
        return True
    return False

def register_user(username: str, password: str, role: str = "user") -> tuple:
    if len(username.strip()) < 3:
        return False, "Username must be at least 3 characters"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username.strip().lower(), hash_password(password), role)
        )
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    except Exception as e:
        return False, str(e)

def get_user(username: str):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username.lower(),)).fetchone()
    conn.close()
    return user

def get_user_role(username: str) -> str:
    user = get_user(username)
    return user["role"] if user else "user"

def get_all_users():
    conn = get_db()
    users = conn.execute("SELECT id, username, role, created_at, is_active FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return users

def toggle_user_status(username: str):
    conn = get_db()
    user = conn.execute("SELECT is_active FROM users WHERE username = ?", (username,)).fetchone()
    if user:
        new_status = 0 if user["is_active"] else 1
        conn.execute("UPDATE users SET is_active = ? WHERE username = ?", (new_status, username))
        conn.commit()
    conn.close()

def delete_user(username: str):
    conn = get_db()
    conn.execute("DELETE FROM users WHERE username = ? AND role != 'admin'", (username,))
    conn.commit()
    conn.close()

def change_password(username: str, old_password: str, new_password: str) -> tuple:
    if not check_credentials(username, old_password):
        return False, "Current password is incorrect"
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters"
    conn = get_db()
    conn.execute("UPDATE users SET password_hash = ? WHERE username = ?",
                 (hash_password(new_password), username))
    conn.commit()
    conn.close()
    return True, "Password changed successfully!"

init_db()