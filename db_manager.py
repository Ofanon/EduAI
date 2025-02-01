import sqlite3
import os
import uuid
import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime, timedelta
import shutil

DB_FILE = os.path.join("data", "request_logs.db")

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

# ✅ Vérifier si la colonne `device_id` existe déjà
cursor.execute("PRAGMA table_info(users)")
columns = [column[1] for column in cursor.fetchall()]

if "device_id" not in columns:
    print("⚠️ [WARNING] `device_id` est absent. Migration de la base...")

    # ✅ Étape 1 : Créer une nouvelle table temporaire avec `device_id`
    cursor.execute('''
        CREATE TABLE users_new (
            user_id TEXT PRIMARY KEY,
            device_id TEXT UNIQUE,
            date TEXT,
            requests INTEGER DEFAULT 5,
            experience_points INTEGER DEFAULT 0,
            purchased_requests INTEGER DEFAULT 0
        )
    ''')
    
    # ✅ Étape 2 : Copier les anciennes données dans la nouvelle table
    cursor.execute('''
        INSERT INTO users_new (user_id, date, requests, experience_points, purchased_requests)
        SELECT user_id, date, requests, experience_points, purchased_requests FROM users
    ''')

    # ✅ Étape 3 : Supprimer l'ancienne table et renommer la nouvelle
    cursor.execute("DROP TABLE users")
    cursor.execute("ALTER TABLE users_new RENAME TO users")

    conn.commit()
    print("✅ [DEBUG] Migration terminée, `device_id` ajouté.")

conn.close()


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
