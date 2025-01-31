import sqlite3
from datetime import datetime
import os
import hashlib
import streamlit as st
import uuid
import shutil
import platform
import socket
from streamlit_js_eval import streamlit_js_eval


# 📌 Chemin de la base de données et de sa sauvegarde
DB_FILE = os.path.join("data", "request_logs.db")
BACKUP_FILE = DB_FILE + ".backup"

# 📌 Création du dossier 'data' s'il n'existe pas
if not os.path.exists("data"):
    os.makedirs("data")

# 📌 Restauration de la base si elle est manquante
if not os.path.exists(DB_FILE) and os.path.exists(BACKUP_FILE):
    print("⚠️ [WARNING] Base de données manquante ! Restauration automatique...")
    shutil.copy(BACKUP_FILE, DB_FILE)
    print("✅ Base de données restaurée depuis la sauvegarde.")

# 📌 Connexion à SQLite
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

# 📌 Fonction pour sauvegarder la base de données
def backup_database():
    """Crée une sauvegarde automatique pour éviter toute perte de données."""
    if os.path.exists(DB_FILE):
        shutil.copy(DB_FILE, BACKUP_FILE)
        print(f"✅ [DEBUG] Sauvegarde effectuée : {BACKUP_FILE}")

backup_database()

# 📌 Fonction pour récupérer l'IP locale de l'utilisateur
def get_private_ip():
    """Récupère l'adresse IP privée réelle de l'appareil."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        print(f"❌ [ERROR] Impossible de récupérer l'adresse IP privée : {e}")
        return "127.0.0.1"

# 📌 Fonction pour générer un identifiant unique basé sur l’appareil
def generate_unique_device_id():
    """Génère un ID unique basé sur l’appareil pour assurer son unicité."""
    private_ip = get_private_ip()
    device_name = platform.node()
    os_name = platform.system()
    processor = platform.processor()
    unique_id = hashlib.sha256(f"{private_ip}_{device_name}_{os_name}_{processor}".encode()).hexdigest()
    return unique_id

# 📌 Fonction pour récupérer ou générer un identifiant unique avec stockage local
def get_user_id():
    """Récupère un ID unique depuis le stockage local ou le génère si inexistant."""

    # 🔍 Vérifier dans le stockage local du navigateur
    user_id = streamlit_js_eval(js_code="localStorage.getItem('user_id')")

    if user_id:
        st.session_state["user_id"] = user_id
        return user_id

    # 🔹 Si aucun ID trouvé, générer un nouvel ID unique
    user_id = generate_unique_device_id()

    # 🔍 Vérifier si cet ID existe déjà dans la base
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        cursor.execute("INSERT INTO users (user_id, date, requests, experience_points, purchased_requests) VALUES (?, ?, 5, 0, 0)", (user_id, None))
        conn.commit()

    conn.close()

    # ✅ Stocker l'ID utilisateur dans le stockage local du navigateur
    streamlit_js_eval(js_code=f"localStorage.setItem('user_id', '{user_id}')")

    st.session_state["user_id"] = user_id
    return user_id

# 📌 Initialisation de l'utilisateur en base de données
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

# 📌 Vérification du quota de requêtes de l'utilisateur
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

# 📌 Consommer une requête utilisateur
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

# 📌 Acheter des requêtes avec des points d'expérience
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

# 📌 Mettre à jour les points d'expérience
def update_experience_points(points):
    user_id = get_user_id()
    cursor.execute("UPDATE users SET experience_points = experience_points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()

# 📌 Récupérer les points d'expérience
def get_experience_points():
    user_id = get_user_id()
    cursor.execute("SELECT experience_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

# 📌 Récupérer le nombre de requêtes restantes
def get_requests_left():
    user_id = get_user_id()
    cursor.execute("SELECT requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] + row[1] if row else 5

initialize_user()
