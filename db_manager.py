import sqlite3
import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import uuid
from datetime import datetime
import os
import shutil

DB_FILE = os.path.join("data", "request_logs.db")
BACKUP_FILE = DB_FILE + ".backup"

# 📌 Vérifier si la base de données existe, sinon la restaurer
if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(DB_FILE) and os.path.exists(BACKUP_FILE):
    print("⚠️ [WARNING] Base de données manquante ! Restauration automatique...")
    shutil.copy(BACKUP_FILE, DB_FILE)
    print("✅ Base de données restaurée depuis la sauvegarde.")

# 📌 Connexion SQLite
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

# 📌 Création de la table des utilisateurs
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

# 📌 Sauvegarde automatique de la base de données
def backup_database():
    if os.path.exists(DB_FILE):
        shutil.copy(DB_FILE, BACKUP_FILE)
        print(f"✅ [DEBUG] Sauvegarde effectuée : {BACKUP_FILE}")

backup_database()

# 📌 Générer un identifiant unique
def generate_unique_device_id():
    """Génère un identifiant totalement unique pour chaque utilisateur."""
    return str(uuid.uuid4())  # Génère un UUID aléatoire

# 📌 Récupérer ou créer un ID utilisateur en utilisant `localStorage`
def get_user_id():
    """Récupère l'ID utilisateur depuis localStorage ou en crée un nouveau."""

    # 🔍 1️⃣ Vérifier si l'ID existe déjà dans le navigateur (`localStorage`)
    user_id = streamlit_js_eval(js_code="localStorage.getItem('user_id')")

    if user_id:
        st.session_state["user_id"] = user_id
        return user_id

    # 🔹 2️⃣ Si non, générer un nouvel ID
    user_id = generate_unique_device_id()

    # 🔹 3️⃣ Vérifier si cet ID existe déjà en base
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        cursor.execute("INSERT INTO users (user_id, date, requests, experience_points, purchased_requests) VALUES (?, ?, 5, 0, 0)", (user_id, None))
        conn.commit()
        print(f"✅ [DEBUG] Nouvel ID enregistré : {user_id}")

    conn.close()

    # 🔹 4️⃣ Stocker l'ID dans le `localStorage` pour le conserver après un refresh
    streamlit_js_eval(js_code=f"localStorage.setItem('user_id', '{user_id}')")

    st.session_state["user_id"] = user_id
    return user_id

# 📌 Initialisation de l'utilisateur dans la base de données
def initialize_user():
    user_id = get_user_id()

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone()[0]

    if not exists:
        cursor.execute("""
            INSERT INTO users (user_id, date, requests, experience_points, purchased_requests)
            VALUES (?, ?, 5, 0, 0)
        """, (user_id, None))
        conn.commit()

    conn.close()

# 📌 Vérifier si l'utilisateur peut faire une requête
def can_user_make_request():
    user_id = get_user_id()
    today = datetime.now().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

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

# 📌 Consommer une requête utilisateur
def consume_request():
    user_id = get_user_id()
    
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

# 📌 Ajouter des points d'expérience
def update_experience_points(points):
    user_id = get_user_id()
    
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("UPDATE users SET experience_points = experience_points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()

# 📌 Récupérer les points d'expérience
def get_experience_points():
    user_id = get_user_id()
    
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("SELECT experience_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    return row[0] if row else 0

# 📌 Récupérer le nombre de requêtes restantes
def get_requests_left():
    user_id = get_user_id()
    
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("SELECT requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    return row[0] + row[1] if row else 5

initialize_user()
