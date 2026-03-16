"""
auth.py — MySQL based user authentication
"""

import hashlib
import mysql.connector

# ── MySQL Config — apna credentials yahan daalo ──────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "200633",  
    "database": "deepguard_db"
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_credentials(username: str, password: str) -> bool:
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND is_active = 1",
            (username.strip().lower(),)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and user["password_hash"] == hash_password(password):
            return True
        return False
    except Exception as e:
        print(f"DB Error: {e}")
        return False

def register_user(username: str, password: str, role: str = "user") -> tuple:
    if len(username.strip()) < 3:
        return False, "Username must be at least 3 characters"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
            (username.strip().lower(), hash_password(password), role)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Registration successful!"
    except mysql.connector.IntegrityError:
        return False, "Username already exists"
    except Exception as e:
        return False, str(e)

def get_user_role(username: str) -> str:
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT role FROM users WHERE username = %s", (username.lower(),))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user["role"] if user else "user"
    except:
        return "user"

def get_all_users() -> list:
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, role, created_at, is_active FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return users
    except:
        return []

def toggle_user_status(username: str):
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT is_active FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            new_status = 0 if user["is_active"] else 1
            cursor.execute("UPDATE users SET is_active = %s WHERE username = %s", (new_status, username))
            conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Toggle error: {e}")

def delete_user(username: str):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = %s AND role != 'admin'", (username,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Delete error: {e}")

def change_password(username: str, old_password: str, new_password: str) -> tuple:
    if not check_credentials(username, old_password):
        return False, "Current password is incorrect"
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters"
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE username = %s",
            (hash_password(new_password), username)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Password changed successfully!"
    except Exception as e:
        return False, str(e)