import sqlite3
import os
import uuid
import bcrypt
import streamlit as st
import extra_streamlit_components as stx

# 📌 Base SQLite
DB_FILE = os.path.join("data", "users.db")

# ✅ Initialisation de la base de données
def initialize_database():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            password TEXT,
            device_id TEXT UNIQUE,
            experience_points INTEGER DEFAULT 0,
            requests INTEGER DEFAULT 5
        )
    ''')
    conn.commit()
    conn.close()

initialize_database()

# ✅ Gestion des cookies pour stocker les sessions utilisateur
cookie_manager_instance = None

def get_cookie_manager():
    global cookie_manager_instance
    if cookie_manager_instance is None:
        cookie_manager_instance = stx.CookieManager()
    return cookie_manager_instance

def generate_device_id():
    """Génère un `device_id` unique basé sur l’appareil et le stocke en cookie."""
    cookie_manager = get_cookie_manager()

    # ✅ Vérifier si un `device_id` est déjà stocké dans les cookies
    stored_device_id = cookie_manager.get("device_id")
    if stored_device_id:
        return stored_device_id  # ✅ Réutiliser l'ID existant

    # 🎯 Générer un `device_id` unique basé sur un UUID aléatoire
    device_id = str(uuid.uuid4())

    # ✅ Stocker dans un cookie spécifique à l’appareil
    cookie_manager.set("device_id", device_id)

    return device_id

# ✅ Fonction d'inscription
def register_user(email, password):
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    # Vérifier si l'email est déjà utilisé
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return False  # Utilisateur déjà existant

    # Hacher le mot de passe
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # Générer un `user_id` unique
    user_id = str(uuid.uuid4())

    # Associer un `device_id` unique
    device_id = generate_device_id()

    # Insérer l'utilisateur dans la base
    cursor.execute("INSERT INTO users (user_id, email, password, device_id) VALUES (?, ?, ?, ?)", 
                   (user_id, email, hashed_password, device_id))
    conn.commit()
    conn.close()

    return True  # Inscription réussie

# ✅ Fonction de connexion
def login_user(email, password):
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    # Vérifier si l'utilisateur existe
    cursor.execute("SELECT user_id, password, device_id FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode(), user[1]):  # Vérifier le mot de passe
        device_id = generate_device_id()  # Générer un `device_id` unique

        # ✅ Vérifier si l'appareil correspond à celui enregistré
        if user[2] and user[2] != device_id:
            conn.close()
            return None  # Refuser la connexion si l’appareil ne correspond pas

        # ✅ Mettre à jour l'appareil associé à l'utilisateur
        cursor.execute("UPDATE users SET device_id = ? WHERE user_id = ?", (device_id, user[0]))
        conn.commit()
        conn.close()
        return user[0]  # Retourner l'`user_id`
    
    conn.close()
    return None  # Connexion échouée

# ✅ Fonction pour récupérer les infos utilisateur
def get_user_info(user_id):
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("SELECT email, experience_points, requests FROM users WHERE user_id = ?", (user_id,))
    user_info = cursor.fetchone()
    conn.close()

    return user_info if user_info else None
