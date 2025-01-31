import sqlite3
from datetime import datetime
import os
import hashlib
import streamlit as st
import uuid
import shutil

# 📂 Chemin sécurisé pour la base de données
DB_FILE = os.path.join("data", "request_logs.db")

# 🔒 Vérification et création du dossier "data" si nécessaire
if not os.path.exists("data"):
    os.makedirs("data")

# 🔍 Vérification si la base existe déjà AVANT d'ouvrir la connexion
db_exists = os.path.exists(DB_FILE)

# 🔄 Connexion à SQLite
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

BACKUP_FILE = DB_FILE + ".backup"

def restore_database():
    if os.path.exists(BACKUP_FILE):
        shutil.copy(BACKUP_FILE, DB_FILE)
        print("✅ Base de données restaurée depuis la sauvegarde !")
    else:
        print("❌ Aucune sauvegarde trouvée, restauration impossible.")

if not os.path.exists(DB_FILE) and os.path.exists(BACKUP_FILE):
    print("⚠️ [WARNING] Base manquante ! Restauration en cours...")
    restore_database()
    
def backup_database():
    backup_path = DB_FILE + ".backup"
    if os.path.exists(DB_FILE):
        shutil.copy(DB_FILE, backup_path)
        print(f"✅ [DEBUG] Sauvegarde effectuée : {backup_path}")

backup_database()

if not db_exists:
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

def get_user_id():
    """Génère un ID unique et stable pour chaque appareil."""
    if "user_id" not in st.session_state:
        try:
            # 🔹 Vérifier si un ID existe déjà dans `st.secrets`
            if "user_id" in st.secrets:
                st.session_state["user_id"] = st.secrets["user_id"]
            else:
                # 🔹 Générer un ID basé sur l’adresse MAC + UUID aléatoire
                unique_device_id = str(uuid.uuid4())
                hashed_id = hashlib.sha256(unique_device_id.encode()).hexdigest()

                # 🔒 Sauvegarder l’ID dans les secrets pour le rendre persistant
                with open(".streamlit/secrets.toml", "w") as f:
                    f.write(f'user_id = "{hashed_id}"')

                st.session_state["user_id"] = hashed_id
        except Exception:
            # 🔹 En cas d’erreur, générer un ID aléatoire unique
            st.session_state["user_id"] = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

    return st.session_state["user_id"]


def initialize_user():
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

