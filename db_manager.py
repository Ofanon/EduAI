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

def backup_database():
    """Crée une sauvegarde automatique de la base pour éviter toute perte."""
    if os.path.exists(DB_FILE):
        shutil.copy(DB_FILE, BACKUP_FILE)
        print(f"✅ [DEBUG] Sauvegarde effectuée : {BACKUP_FILE}")

backup_database()


USER_ID_FILE = "data/user_id.txt"

def get_user_id():
    """Génère un ID unique pour chaque appareil et assure sa stabilité sans utiliser le dernier enregistrement."""
    if "user_id" not in st.session_state:
        user_id = None

        # 1️⃣ Vérifier si un ID est déjà stocké localement
        if os.path.exists(USER_ID_FILE):
            with open(USER_ID_FILE, "r") as f:
                stored_id = f.read().strip()
                if stored_id:
                    user_id = stored_id
                    print(f"✅ [DEBUG] ID récupéré depuis user_id.txt : {user_id}")

        # 2️⃣ Si aucun ID trouvé localement, générer un ID propre à cet appareil
        if not user_id:
            try:
                device_name = platform.node()  # Nom de l'appareil
                os_name = platform.system()  # Type de système (Windows, MacOS, Linux, Android, iOS)
                processor = platform.processor()  # Type de processeur
                unique_device_id = str(uuid.uuid4())  # Généré une seule fois par appareil

                # 🔹 Générer un hash unique basé sur ces informations
                user_id = hashlib.sha256(f"{device_name}_{os_name}_{processor}_{unique_device_id}".encode()).hexdigest()

                # 🔒 Sauvegarder cet ID en local pour qu'il soit stable après fermeture
                with open(USER_ID_FILE, "w") as f:
                    f.write(user_id)

            except Exception as e:
                print(f"❌ [ERROR] Impossible de générer un ID unique : {e}")
                user_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()  # Solution de secours

        # 3️⃣ Vérifier si cet appareil a déjà un ID en base
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        if not row:
            # Insérer un nouvel ID en base uniquement si cet appareil est inconnu
            cursor.execute("INSERT INTO users (user_id, date, requests, experience_points, purchased_requests) VALUES (?, ?, 5, 0, 0)", (user_id, None))
            conn.commit()
            print(f"✅ [DEBUG] Nouvel ID enregistré en base : {user_id}")

        conn.close()
        st.session_state["user_id"] = user_id  # 🔄 Stocker en session pour éviter de le recalculer à chaque appel

    return st.session_state["user_id"]




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
