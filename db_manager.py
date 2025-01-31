import sqlite3
from datetime import datetime
import os
import hashlib
import streamlit as st
import requests
import uuid

DB_FILE = os.path.join("data", "request_logs.db")
if not os.path.exists("data"):
    os.makedirs("data")
    
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

def get_user_id():
    """Génère un ID unique basé sur l'adresse MAC + IP + Type d'appareil."""
    if "user_id" not in st.session_state:
        try:
            # 🔹 Récupération de l'adresse MAC (unique par appareil)
            mac_address = str(uuid.getnode())

            # 🔹 Récupération de l'IP publique
            response = requests.get("https://api64.ipify.org?format=json", timeout=5)
            public_ip = response.json().get("ip", "Unknown")

            # 🔹 Récupération du type d'appareil (Windows, iOS, Android...)
            device_info = platform.system() + "_" + platform.release()

            # 🔹 Création d'un ID unique basé sur MAC + IP + Type d'appareil
            unique_id = f"{mac_address}_{public_ip}_{device_info}"
            hashed_id = hashlib.sha256(unique_id.encode()).hexdigest()

            # 🔹 Stocke l'ID utilisateur dans la session
            st.session_state["user_id"] = hashed_id
        except Exception:
            # 🔹 Si erreur, utilise seulement la MAC (toujours unique par appareil)
            st.session_state["user_id"] = hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()

    return st.session_state["user_id"]

# 🔄 Vérification si l'utilisateur existe et création si nécessaire
def initialize_user():
    """Ajoute l'utilisateur s'il n'existe pas déjà."""
    user_id = get_user_id()
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO users (user_id, date, requests, experience_points, purchased_requests)
            VALUES (?, ?, 5, 0, 0)
        """, (user_id, None))
        conn.commit()

# 🔍 Vérification des requêtes disponibles
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

# 🔄 Consommer une requête
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

# 🌟 Mise à jour des points d'expérience
def update_experience_points(points):
    """Ajoute des XP à l'utilisateur."""
    user_id = get_user_id()
    cursor.execute("UPDATE users SET experience_points = experience_points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()

# 🎯 Récupération des XP
def get_experience_points():
    """Retourne les XP de l'utilisateur."""
    user_id = get_user_id()
    cursor.execute("SELECT experience_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

# 🔄 Récupération des requêtes restantes
def get_requests_left():
    """Retourne le nombre total de requêtes disponibles."""
    user_id = get_user_id()
    cursor.execute("SELECT requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] + row[1] if row else 5

def purchase_requests(cost_in_experience, requests_to_add):
    """Ajoute des requêtes supplémentaires à l'utilisateur en échange d'XP."""
    user_id = get_user_id()
    
    # 🔍 Vérifier le solde XP actuel
    cursor.execute("SELECT experience_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row and row[0] >= cost_in_experience:
        # ✅ Déduction des XP et ajout des requêtes achetées
        cursor.execute("""
            UPDATE users
            SET experience_points = experience_points - ?, purchased_requests = purchased_requests + ?
            WHERE user_id = ?
        """, (cost_in_experience, requests_to_add, user_id))
        conn.commit()
        return True  # ✅ Achat réussi
    return False  # ❌ Achat refusé (pas assez d'XP)
    
# 🔍 Debug : Afficher l'ID utilisateur
def debug_show_user():
    """Affiche l'ID utilisateur pour s'assurer qu'il est unique."""
    user_id = get_user_id()
    print(f"✅ [DEBUG] Utilisateur actuel : {user_id}")

initialize_user()
