import sqlite3
import os
import uuid
import streamlit as st

# 📌 Base SQLite
DB_FILE = os.path.join("data", "request_logs.db")

# ✅ Vérifier et créer la base SQLite
def initialize_database():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            device_id TEXT UNIQUE,
            date TEXT,
            requests INTEGER DEFAULT 5,
            experience_points INTEGER DEFAULT 0,
            purchased_requests INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

initialize_database()

def get_or_create_user_id(device_id):
    """Récupère ou génère un `user_id` unique basé sur `device_id`."""

    if not device_id:
        device_id = str(uuid.uuid4())  # 🎯 Générer un `device_id` aléatoire si aucun n'est trouvé
        st.session_state["device_id"] = device_id

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    # ✅ Vérifier si ce `device_id` existe en base
    cursor.execute("SELECT user_id FROM users WHERE device_id = ?", (device_id,))
    row = cursor.fetchone()

    if row:
        user_id = row[0]
        print(f"✅ [DEBUG] User ID récupéré depuis SQLite : {user_id}")
    else:
        user_id = str(uuid.uuid4())  # Générer un nouvel ID unique
        cursor.execute("""
            INSERT INTO users (user_id, device_id, date, requests, experience_points, purchased_requests)
            VALUES (?, ?, ?, 5, 0, 0)
        """, (user_id, device_id, None))
        conn.commit()
        print(f"✅ [DEBUG] Nouvel ID enregistré : {device_id} → {user_id}")

    conn.close()
    st.session_state["user_id"] = user_id
    return user_id
