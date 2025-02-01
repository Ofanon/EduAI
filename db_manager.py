import sqlite3
import os
import uuid
import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime, timedelta
import hashlib

# 📌 Chemin de la base SQLite
DB_FILE = os.path.join("data", "request_logs.db")

# ✅ Vérifier que le dossier `data/` existe
if not os.path.exists("data"):
    os.makedirs("data")

# ✅ Initialiser la base de données SQLite
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

# ✅ Gestion unique des cookies
cookie_manager_instance = None

def get_cookie_manager():
    """Retourne une instance unique de CookieManager."""
    global cookie_manager_instance
    if cookie_manager_instance is None:
        cookie_manager_instance = stx.CookieManager()
    return cookie_manager_instance

def generate_device_id():
    """Génère un ID unique basé sur un UUID et le navigateur de l’utilisateur."""
    cookie_manager = get_cookie_manager()

    # ✅ Vérifier si un `device_id` est déjà stocké dans les cookies
    stored_device_id = cookie_manager.get("device_id")
    if stored_device_id:
        return stored_device_id  # ✅ Réutiliser l'ID stocké

    # 🔍 Récupérer un identifiant basé sur l'empreinte navigateur
    user_agent = st.session_state.get("user_agent", str(uuid.uuid4()))

    # 🎯 Générer un `device_id` unique
    final_device_id = hashlib.sha256(user_agent.encode()).hexdigest()

    # ✅ Stocker dans un cookie pour persistance
    expires_at = datetime.now() + timedelta(days=365 * 20)
    cookie_manager.set("device_id", final_device_id, expires_at=expires_at)

    return final_device_id

def get_or_create_user_id():
    """Récupère ou génère un `user_id` unique par appareil et navigateur."""

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    cookie_manager = get_cookie_manager()

    # ✅ Générer un `device_id` unique
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

    # ✅ Stocker `user_id` en cookie si non défini
    if not cookie_manager.get("user_id"):
        expires_at = datetime.now() + timedelta(days=365 * 20)
        cookie_manager.set("user_id", user_id, expires_at=expires_at)

    st.session_state["user_id"] = user_id
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
