import sqlite3
from datetime import datetime
import os
import hashlib
import streamlit as st
import uuid
import shutil

DB_FILE = os.path.join("data", "request_logs.db")
BACKUP_FILE = DB_FILE + ".backup"

if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(DB_FILE) and os.path.exists(BACKUP_FILE):
    print("⚠️ [WARNING] Base de données manquante ! Restauration automatique...")
    shutil.copy(BACKUP_FILE, DB_FILE)
    print("✅ Base de données restaurée depuis la sauvegarde.")

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

# 🛠 Création des tables UNIQUEMENT si la base est nouvelle
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

# 🔒 Sauvegarde automatique avant toute mise à jour
def backup_database():
    """Crée une sauvegarde automatique de la base pour éviter toute perte."""
    if os.path.exists(DB_FILE):
        shutil.copy(DB_FILE, BACKUP_FILE)
        print(f"✅ [DEBUG] Sauvegarde effectuée : {BACKUP_FILE}")

backup_database()

def get_user_id():
    """Génère un ID unique par appareil et le stocke dans SQLite pour assurer qu'il soit persistant."""
    if "user_id" not in st.session_state:
        user_id = None

        # Vérifier si un ID est déjà enregistré pour cet appareil dans SQLite
        cursor.execute("SELECT user_id FROM users WHERE user_id LIKE 'device_%' ORDER BY rowid DESC LIMIT 1")
        row = cursor.fetchone()

        if row:
            user_id = row[0]  # Récupérer l'ID existant
        else:
            # Générer un ID basé sur UUID (évite les conflits d’IP ou MAC)
            unique_device_id = str(uuid.uuid4())  
            user_id = f"device_{hashlib.sha256(unique_device_id.encode()).hexdigest()}"

            # Stocker cet ID unique en base de données
            cursor.execute("INSERT INTO users (user_id, date, requests, experience_points, purchased_requests) VALUES (?, ?, 5, 0, 0)", (user_id, None))
            conn.commit()

        st.session_state["user_id"] = user_id  # Sauvegarde dans la session
    return st.session_state["user_id"]



def initialize_user():
    """Ajoute l'utilisateur s'il n'existe pas encore."""
    user_id = get_user_id()
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone()[0] == 0:
        print(f"✅ [DEBUG] Nouvel utilisateur ajouté : {user_id}")
        cursor.execute("""
            INSERT INTO users (user_id, date, requests, experience_points, purchased_requests)
            VALUES (?, ?, 5, 0, 0)
        """, (user_id, None))
        conn.commit()

def can_user_make_request():
    """Vérifie si l'utilisateur peut faire une requête aujourd'hui."""
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
    """Diminue le nombre de requêtes disponibles pour l'utilisateur."""
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
    """Ajoute des requêtes en échange d'XP."""
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
    """Ajoute des XP à l'utilisateur."""
    user_id = get_user_id()
    cursor.execute("UPDATE users SET experience_points = experience_points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()

def get_experience_points():
    """Retourne les XP de l'utilisateur."""
    user_id = get_user_id()
    cursor.execute("SELECT experience_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

def get_requests_left():
    """Retourne le nombre total de requêtes disponibles."""
    user_id = get_user_id()
    cursor.execute("SELECT requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] + row[1] if row else 5

initialize_user()
