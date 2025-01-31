import sqlite3
from datetime import datetime
import os
import hashlib
import streamlit as st
import uuid
import shutil
import platform
import socket

DB_FILE = "data/request_logs.db"

# 📂 Vérifie et crée le dossier "data" s'il n'existe pas
if not os.path.exists("data"):
    os.makedirs("data")

def create_database():
    """Crée la base de données SQLite si elle n'existe pas."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

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
    conn.close()
    print("✅ Base de données créée avec succès !")

# 🔄 Vérifier si `request_logs.db` existe, sinon la créer
if not os.path.exists(DB_FILE):
    print("⚠️ [WARNING] Base de données absente, création en cours...")
    create_database()
else:
    print("✅ [DEBUG] Base de données existante.")


def get_private_ip():
    """Récupère l'adresse IP privée réelle de l'appareil."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connexion temporaire pour obtenir l’IP locale
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        print(f"❌ [ERROR] Impossible de récupérer l'adresse IP privée : {e}")
        return "127.0.0.1"  # Adresse de secours

def generate_unique_device_id():
    """Génère un ID unique basé sur l’appareil pour assurer son unicité."""
    private_ip = get_private_ip()  # 🔍 Adresse IP locale unique
    device_name = platform.node()  # 🔹 Nom de l'appareil
    os_name = platform.system()  # 🔹 Type de système (Windows, Mac, Linux, Android, iOS)
    processor = platform.processor()  # 🔹 Type de processeur
    unique_id = hashlib.sha256(f"{private_ip}_{device_name}_{os_name}_{processor}".encode()).hexdigest()

    return unique_id

def get_user_id():
    """Récupère un ID unique en base ou le génère si inexistant."""
    
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    # 🔹 1️⃣ Vérifier si l'ID est déjà stocké en session (utile pour éviter les recalculs)
    if "user_id" in st.session_state:
        return st.session_state["user_id"]

    user_id = generate_unique_device_id()  # Génération basée sur l’appareil

    # 🔹 2️⃣ Vérifier si cet ID existe déjà en base
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row:
        user_id = row[0]  # 🔄 Récupérer l’ID existant en base
        print(f"✅ [DEBUG] ID récupéré depuis SQLite : {user_id}")
    else:
        # 🔹 Insérer l’ID si c’est un nouvel utilisateur
        cursor.execute("INSERT INTO users (user_id, date, requests, experience_points, purchased_requests) VALUES (?, ?, 5, 0, 0)", (user_id, None))
        conn.commit()
        print(f"✅ [DEBUG] Nouvel ID enregistré en base : {user_id}")

    conn.close()

    st.session_state["user_id"] = user_id  # 🔄 Stocker en session pour éviter de recalculer à chaque appel

    return user_id

def initialize_user():
    user_id = get_user_id()

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone()[0]

    if not exists:
        print(f"✅ [DEBUG] Nouvel utilisateur ajouté en base : {user_id}")
        cursor.execute("""
            INSERT INTO users (user_id, date, requests, experience_points, purchased_requests)
            VALUES (?, ?, 5, 0, 0)
        """, (user_id, None))
        conn.commit()
    else:
        print(f"✅ [DEBUG] Utilisateur déjà existant en base : {user_id}")

    conn.close()


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
    return row[0] + row[1] if row else 5

initialize_user()
