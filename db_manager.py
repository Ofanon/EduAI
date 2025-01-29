import sqlite3
from datetime import datetime
import os
import streamlit as st
import requests
import hashlib
import uuid
DB_FILE = "data/request_logs.db"

db_exists = os.path.exists(DB_FILE)

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

if not db_exists:
    print("[DEBUG] Création de la base de données.")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            date TEXT,
            requests INTEGER DEFAULT 5,
            experience_points INTEGER DEFAULT 0,
            purchased_requests INTEGER DEFAULT 0
        )
    ''')
    conn.commit()

try:
    print(f"[DEBUG] Votre utilisateur système est : {os.getlogin()}")
except Exception as e:
    print(f"[ERROR] os.getlogin() a échoué : {e}")

def get_user_id():
    """Génère un ID stable sans utiliser os.getlogin()."""
    if "user_id" not in st.session_state:
        try:
            response = requests.get("https://api64.ipify.org?format=json", timeout=5)
            public_ip = response.json().get("ip", "Unknown")

            unique_id = f"{public_ip}_{uuid.uuid4()}"
            hashed_id = hashlib.sha256(unique_id.encode()).hexdigest()

            st.session_state["user_id"] = hashed_id
        except Exception:
            st.session_state["user_id"] = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

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
    else:
        print(f"[DEBUG] L'utilisateur {user_id} existe déjà, pas de création.")

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
    return True

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

def update_experience_points(points):
    user_id = get_user_id()
    cursor.execute("UPDATE users SET experience_points = experience_points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()

def get_experience_points():
    user_id = get_user_id()
    cursor.execute("SELECT experience_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

def get_requests_left():
    user_id = get_user_id()
    cursor.execute("SELECT requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        return row[0] + row[1]
    return 5

def debug_show_users():
    """Affiche tous les utilisateurs de la base pour vérifier."""
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    print("[DEBUG] Liste des utilisateurs enregistrés :")
    for row in rows:
        print(row)

initialize_user()
