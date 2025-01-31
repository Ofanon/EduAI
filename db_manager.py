import sqlite3
from datetime import datetime
import os
import hashlib
import streamlit as st
import uuid
import shutil
import requests
import platform

DB_FILE = os.path.join("data", "request_logs.db")

USER_ID_FILE = "data/user_id.txt"

if not os.path.exists("data"):
    os.makedirs("data")

db_exists = os.path.exists(DB_FILE)

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

def backup_database():
    backup_path = DB_FILE + ".backup"
    if os.path.exists(DB_FILE):
        shutil.copy(DB_FILE, backup_path)
        print(f"✅ [DEBUG] Sauvegarde effectuée : {backup_path}")

backup_database()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        date TEXT,
        requests INTEGER DEFAULT 5,
        experience_points INTEGER DEFAULT 0,
        purchased_requests INTEGER DEFAULT 0
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS revision_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        title TEXT,
        content TEXT,
        date TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        date TEXT,
        xp_earned INTEGER DEFAULT 0,
        quizzes_completed INTEGER DEFAULT 0,
        correct_answers INTEGER DEFAULT 0,
        wrong_answers INTEGER DEFAULT 0
    )
''')

conn.commit()

def get_user_id():
    
    if "user_id" not in st.session_state:
        try:
            if os.path.exists(USER_ID_FILE):
                with open(USER_ID_FILE, "r") as file:
                    stored_id = file.read().strip()
                st.session_state["user_id"] = stored_id
                return stored_id

            try:
                response = requests.get("https://api64.ipify.org?format=json", timeout=5)
                public_ip = response.json().get("ip", "Unknown")
            except Exception:
                public_ip = "NoIP"

            device_id = str(uuid.getnode())

            os_info = platform.system() + "_" + platform.release()

            unique_id = f"{public_ip}_{device_id}_{os_info}"
            hashed_id = hashlib.sha256(unique_id.encode()).hexdigest()

            with open(USER_ID_FILE, "w") as file:
                file.write(hashed_id)

            st.session_state["user_id"] = hashed_id
            return hashed_id

        except Exception:
            temp_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
            st.session_state["user_id"] = temp_id
            return temp_id

    return st.session_state["user_id"]


def initialize_user():
    user_id = get_user_id()
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO users (user_id, date, requests, experience_points, purchased_requests)
            VALUES (?, ?, 5, 0, 0)
        """, (user_id, None))
        conn.commit()

def can_user_make_request():
    user_id = get_user_id()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT date, requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        initialize_user()
        return True

    date_last_request, normal_requests, purchased_requests = row

    if date_last_request != today:
        cursor.execute("UPDATE users SET date = ?, requests = 5 WHERE user_id = ?", (today, user_id))
        conn.commit()
        return True

    return normal_requests > 0 or purchased_requests > 0

def consume_request():
    user_id = get_user_id()
    cursor.execute("SELECT requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        return False

    normal_requests, purchased_requests = row

    if purchased_requests > 0:
        cursor.execute("UPDATE users SET purchased_requests = purchased_requests - 1 WHERE user_id = ?", (user_id,))
    elif normal_requests > 0:
        cursor.execute("UPDATE users SET requests = requests - 1 WHERE user_id = ?", (user_id,))
    else:
        return False

    conn.commit()

def update_experience_points(points):
    user_id = get_user_id()
    cursor.execute("UPDATE users SET experience_points = experience_points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()

def get_experience_points():
    user_id = get_user_id()
    cursor.execute("SELECT experience_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

def purchase_requests(cost_in_experience, requests_to_add):
    user_id = get_user_id()
    cursor.execute("SELECT experience_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row and row[0] >= cost_in_experience:
        cursor.execute("""
            UPDATE users
            SET experience_points = experience_points - ?, purchased_requests = purchased_requests + ?
            WHERE user_id = ?
        """, (cost_in_experience, requests_to_add, user_id))
        conn.commit()
        return True
    return False

def get_requests_left():
    user_id = get_user_id()
    cursor.execute("SELECT requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] + row[1] if row else 5

initialize_user()
