import sqlite3
import os
import uuid
import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime, timedelta
import shutil

DB_FILE = os.path.join("data", "request_logs.db")
BACKUP_FILE = DB_FILE + ".backup"

# ✅ Vérifier si le dossier "data" et la base existent
if not os.path.exists("data"):
    os.makedirs("data")

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

# ✅ Création de la table des utilisateurs si elle n'existe pas
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

def backup_database():
    """Crée une sauvegarde automatique de la base pour éviter toute perte."""
    if os.path.exists(DB_FILE):
        shutil.copy(DB_FILE, BACKUP_FILE)
        print(f"✅ [DEBUG] Sauvegarde effectuée : {BACKUP_FILE}")

backup_database()

# ✅ Gérer une seule instance de CookieManager
cookie_manager_instance = None

def get_cookie_manager():
    """Retourne une instance unique de CookieManager pour éviter les doublons."""
    global cookie_manager_instance
    if cookie_manager_instance is None:
        cookie_manager_instance = stx.CookieManager()
    return cookie_manager_instance

def get_or_create_user_id():
    """Récupère ou génère un `user_id` unique pour chaque appareil et le stocke dans un cookie."""
    
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    cookie_manager = get_cookie_manager()

    # ✅ Vérifier si un `device_id` unique est déjà stocké dans les cookies
    device_id = cookie_manager.get("device_id")

    if not device_id:
        device_id = str(uuid.uuid4())  # Génère un identifiant unique pour cet appareil
        cookie_manager.set("device_id", device_id, expires_at=datetime.now() + timedelta(days=365 * 20))

    # ✅ Vérifier si ce `device_id` existe déjà en base
    cursor.execute("SELECT user_id FROM users WHERE device_id = ?", (device_id,))
    row = cursor.fetchone()

    if row:
        user_id = row[0]  # L'utilisateur existant garde son ID
    else:
        user_id = str(uuid.uuid4())  # Générer un nouvel ID unique pour cet appareil
        cursor.execute("INSERT INTO users (user_id, device_id, date, requests, experience_points, purchased_requests) VALUES (?, ?, ?, 5, 0, 0)", 
                       (user_id, device_id, None))
        conn.commit()
        print(f"✅ [DEBUG] Nouvel ID enregistré pour l'appareil : {device_id} → {user_id}")

    conn.close()

    # ✅ Stocker l'`user_id` dans un cookie de longue durée (20 ans)
    expires_at = datetime.now() + timedelta(days=365 * 20)
    cookie_manager.set("user_id", user_id, expires_at=expires_at)

    # ✅ Stocker en session pour éviter les requêtes répétées
    st.session_state["user_id"] = user_id

    return user_id

def can_user_make_request():
    user_id = get_or_create_user_id()
    today = datetime.now().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("SELECT date, requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        return True

    date_last_request, normal_requests, purchased_requests = row

    if date_last_request != today:
        cursor.execute("UPDATE users SET date = ?, requests = 5 WHERE user_id = ?", (today, user_id))
        conn.commit()
        return True

    return normal_requests > 0 or purchased_requests > 0

def consume_request():
    user_id = get_or_create_user_id()
    
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

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

def get_requests_left():
    user_id = get_or_create_user_id()

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("SELECT requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] + row[1] if row else 5
