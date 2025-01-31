import sqlite3
from datetime import datetime
import os
import hashlib
import streamlit as st
import uuid
import shutil
import platform

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

USER_ID_FILE = "data/user_id.txt"

def get_user_id():
    """Génère un ID unique pour chaque appareil et le rend persistant."""
    if "user_id" not in st.session_state:
        user_id = None

        # 🔹 1️⃣ Vérifier si un ID est déjà stocké localement
        if os.path.exists(USER_ID_FILE):
            with open(USER_ID_FILE, "r") as f:
                stored_id = f.read().strip()
                if stored_id:
                    user_id = stored_id
                    print(f"✅ [DEBUG] ID récupéré depuis user_id.txt : {user_id}")

        # 🔹 2️⃣ Si aucun ID trouvé localement, chercher en base SQLite
        if not user_id:
            conn = sqlite3.connect(DB_FILE, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users ORDER BY rowid DESC LIMIT 1")
            row = cursor.fetchone()

            if row:
                user_id = row[0]  # Récupérer l'ID existant en base
                print(f"✅ [DEBUG] ID récupéré depuis la base SQLite : {user_id}")

        # 🔹 3️⃣ Si toujours aucun ID trouvé, générer un nouvel ID unique
        if not user_id:
            device_name = platform.node()  # Nom de l'appareil
            os_name = platform.system()  # Windows, Linux, Android, iOS, etc.
            unique_device_id = str(uuid.uuid4())  # Généré une seule fois par appareil

            # Générer un hash unique
            user_id = hashlib.sha256(f"{device_name}_{os_name}_{unique_device_id}".encode()).hexdigest()

            # 🔒 Sauvegarder cet ID en local pour qu'il soit stable même après fermeture
            with open(USER_ID_FILE, "w") as f:
                f.write(user_id)

            # 🔍 Vérifier si l’ID est déjà en base, sinon l’ajouter
            cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (user_id,))
            exists = cursor.fetchone()[0]

            if not exists:
                cursor.execute("INSERT INTO users (user_id, date, requests, experience_points, purchased_requests) VALUES (?, ?, 5, 0, 0)", (user_id, None))
                conn.commit()
                print(f"✅ [DEBUG] Nouvel ID enregistré en base : {user_id}")

            conn.close()

        # 🔄 Stocker en session pour éviter de le recalculer à chaque appel
        st.session_state["user_id"] = user_id

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
