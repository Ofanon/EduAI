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

def generate_device_id():
    """Génère un ID unique et le stocke en base SQLite pour éviter qu'il change."""
    
    # ✅ Vérifier si un `device_id` est stocké dans les cookies
    if "device_id" in st.query_params:
        return st.query_params["device_id"]

    # ✅ Générer un `device_id` unique basé sur un UUID aléatoire
    device_id = str(uuid.uuid4())

    # ✅ Stocker `device_id` dans l'URL pour persistance
    st.query_params["device_id"] = device_id

    return device_id

def get_or_create_user_id():
    """Récupère ou génère un `user_id` unique et permanent basé sur le `device_id`."""

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    # ✅ Générer ou récupérer un `device_id` unique basé sur l’utilisateur
    device_id = generate_device_id()
    print(f"🔍 [DEBUG] Device ID détecté : {device_id}")

    # ✅ Vérifier si ce `device_id` existe déjà en base
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
    return user_id

def get_requests_left():
    """Récupère le nombre de requêtes restantes pour l'utilisateur."""
    user_id = get_or_create_user_id()

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    return row[0] if row else 5

def consume_request():
    """Diminue le nombre de requêtes disponibles pour l'utilisateur."""
    user_id = get_or_create_user_id()

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET requests = requests - 1 WHERE user_id = ? AND requests > 0", (user_id,))
    conn.commit()
    conn.close()

    return cursor.rowcount > 0
