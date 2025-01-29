import sqlite3
from datetime import datetime
import os
import streamlit as st

DB_FILE = "request_logs.db"  # Met le fichier à la racine du projet

# Vérifier si la base de données existe
db_exists = os.path.exists(DB_FILE)

st.write(f"[DEBUG] 📂 Le fichier SQLite devrait être ici : {os.path.abspath(DB_FILE)}")

if not os.path.exists(DB_FILE):
    st.write("[ERROR] 🚨 La base de données n'existe pas, elle va être recréée !")
else:
    st.write("[DEBUG] ✅ La base de données existe bien et ne sera pas recréée.")
# Connexion à SQLite
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()


# Créer la table uniquement si la base est nouvelle
if not db_exists:
    print("[DEBUG] Création de la base de données.")
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
    """Récupère un ID unique pour chaque utilisateur en utilisant `st.session_state`."""
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = str(os.getlogin())  # Utilise le nom de l'utilisateur du PC
    return st.session_state["user_id"]

def initialize_user():
    """Crée un utilisateur seulement s'il n'existe pas."""
    user_id = get_user_id()
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone()[0] == 0:
        print(f"[DEBUG] Nouvel utilisateur ajouté : {user_id}")
        cursor.execute("""
            INSERT INTO users (user_id, date, requests, experience_points, purchased_requests)
            VALUES (?, ?, 5, 0, 0)
        """, (user_id, None))
        conn.commit()

def can_user_make_request():
    """Vérifie si l'utilisateur peut faire une requête."""
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
    """Consomme une requête normale ou achetée."""
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
    return True

def purchase_requests(cost_in_experience, requests_to_add):
    """Achète des requêtes avec les points d'expérience."""
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
    """Ajoute des points d'expérience à l'utilisateur."""
    user_id = get_user_id()
    cursor.execute("UPDATE users SET experience_points = experience_points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()

def get_experience_points():
    """Récupère les points d'expérience de l'utilisateur."""
    user_id = get_user_id()
    cursor.execute("SELECT experience_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

def get_requests_left():
    """Retourne le nombre total de requêtes restantes (normales + achetées)."""
    user_id = get_user_id()
    cursor.execute("SELECT requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        return row[0] + row[1]
    return 5  # Valeur par défaut

def debug_show_users():
    """Affiche tous les utilisateurs de la base pour vérifier."""
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    print("[DEBUG] Liste des utilisateurs enregistrés :")
    for row in rows:
        print(row)

# Initialisation de l'utilisateur
initialize_user()
