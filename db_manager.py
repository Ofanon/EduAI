import sqlite3
import os
import uuid
import hashlib
import platform
import socket
import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime, timedelta

# 📌 Chemin de la base de données SQLite
DB_FILE = os.path.join("data", "request_logs.db")

# ✅ Assurer que le dossier `data/` existe
if not os.path.exists("data"):
    os.makedirs("data")

# ✅ Création automatique de la base SQLite si elle n'existe pas
def initialize_database():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    # ✅ Vérifier si la table `users` existe, sinon la créer
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

# ✅ Gestion d'une seule instance de CookieManager
cookie_manager_instance = None

def get_cookie_manager():
    """Retourne une instance unique de CookieManager."""
    global cookie_manager_instance
    if cookie_manager_instance is None:
        cookie_manager_instance = stx.CookieManager()
    return cookie_manager_instance

def generate_device_id():
    """Génère un ID 100% unique basé sur l’appareil et le navigateur."""
    cookie_manager = get_cookie_manager()

    # ✅ Vérifier si un `device_id` aléatoire est déjà stocké dans les cookies
    stored_device_id = cookie_manager.get("device_id")

    if stored_device_id:
        return stored_device_id  # ✅ Réutiliser l'ID unique de l'appareil

    # 📌 Récupérer des infos système
    try:
        private_ip = socket.gethostbyname(socket.gethostname())  # IP locale
        device_name = platform.node()  # Nom de l'appareil
        os_name = platform.system()  # OS (Windows, Linux, Mac, Android, iOS)
        processor = platform.processor()  # Type de processeur

        # 🔍 Générer un identifiant unique basé sur ces infos
        raw_id = f"{private_ip}_{device_name}_{os_name}_{processor}"
        hashed_id = hashlib.sha256(raw_id.encode()).hexdigest()  # Hash pour anonymisation

    except Exception as e:
        print(f"❌ [ERROR] Impossible de récupérer les infos système : {e}")
        hashed_id = str(uuid.uuid4())  # 🎯 Générer un ID aléatoire en secours

    # ✅ Ajouter un identifiant aléatoire pour garantir l'unicité
    final_device_id = f"{hashed_id}_{uuid.uuid4()}"

    # ✅ Stocker l'ID dans un cookie pour être sûr qu'il reste unique
    cookie_manager.set("device_id", final_device_id, expires_at="2034-01-01T00:00:00Z")

    return final_device_id

def get_or_create_user_id():
    """Récupère ou génère un `user_id` unique et le stocke en base + cookies."""

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    cookie_manager = get_cookie_manager()

    # ✅ Générer un `device_id` vraiment unique
    device_id = generate_device_id()
    print(f"🔍 [DEBUG] Device ID détecté : {device_id}")

    # ✅ Vérifier si cet appareil existe déjà en base
    cursor.execute("SELECT user_id FROM users WHERE device_id = ?", (device_id,))
    row = cursor.fetchone()

    if row:
        user_id = row[0]
    else:
        user_id = str(uuid.uuid4())  # Générer un nouvel ID unique
        cursor.execute("""
            INSERT INTO users (user_id, device_id, date, requests, experience_points, purchased_requests)
            VALUES (?, ?, ?, 5, 0, 0)
        """, (user_id, device_id, None))
        conn.commit()
        print(f"✅ [DEBUG] Nouvel ID enregistré pour l'appareil : {device_id} → {user_id}")

    conn.close()

    # ✅ Stocker l'`user_id` en session et cookie (si pas déjà défini)
    if not cookie_manager.get("user_id"):
        cookie_manager.set("user_id", user_id, expires_at="2034-01-01T00:00:00Z")

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
