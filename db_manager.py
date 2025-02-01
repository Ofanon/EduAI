import sqlite3
import os
import uuid
import hashlib
import platform
import socket
import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime, timedelta

# 📌 Chemin de la base SQLite
DB_FILE = os.path.join("data", "request_logs.db")

# ✅ Assurer que le dossier `data/` existe
if not os.path.exists("data"):
    os.makedirs("data")

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

# ✅ Gestion unique des cookies
cookie_manager_instance = None

def get_cookie_manager():
    """Retourne une instance unique de CookieManager."""
    global cookie_manager_instance
    if cookie_manager_instance is None:
        cookie_manager_instance = stx.CookieManager()
    return cookie_manager_instance

def generate_device_id():
    """Génère un ID unique basé sur l’appareil."""
    try:
        private_ip = socket.gethostbyname(socket.gethostname())  # IP locale
        device_name = platform.node()  # Nom de l'appareil
        os_name = platform.system()  # OS (Windows, Linux, Mac, Android, iOS)
        processor = platform.processor()  # Type de processeur

        raw_id = f"{private_ip}_{device_name}_{os_name}_{processor}"
        hashed_id = hashlib.sha256(raw_id.encode()).hexdigest()

        return hashed_id
    except Exception as e:
        print(f"❌ [ERROR] Impossible de récupérer les infos système : {e}")
        return str(uuid.uuid4())

def get_or_create_user_id():
    """Récupère ou génère un `user_id` unique par appareil."""

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    cookie_manager = get_cookie_manager()

    # ✅ Générer un `device_id` unique
    device_id = generate_device_id()
    print(f"🔍 [DEBUG] Device ID détecté : {device_id}")

    # ✅ Vérifier si le `device_id` existe déjà en base
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

    # ✅ Stocker l'`user_id` en session et cookie (si pas déjà défini)
    if not cookie_manager.get("user_id"):
        expires_at = datetime.now() + timedelta(days=365 * 20)
        cookie_manager.set("user_id", user_id, expires_at=expires_at)

    st.session_state["user_id"] = user_id
    return user_id
