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

    # Insérer l'utilisateur dans la base
    cursor.execute("INSERT INTO users (user_id, email, password) VALUES (?, ?, ?)", (user_id, email, hashed_password))
    conn.commit()
    conn.close()

    return True  # Inscription réussie

# ✅ Fonction de connexion
def login_user(email, password):
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    # Vérifier si l'utilisateur existe
    cursor.execute("SELECT user_id, password FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode(), user[1]):  # Vérifier le mot de passe
        return user[0]  # Retourner l'`user_id`
    
    return None  # Connexion échouée

# ✅ Fonction pour récupérer les infos utilisateur
def get_user_info(user_id):
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("SELECT email, experience_points, requests FROM users WHERE user_id = ?", (user_id,))
    user_info = cursor.fetchone()
    conn.close()

    return user_info if user_info else None

# ✅ Fonction pour mettre à jour les points d'expérience
def update_experience_points(user_id, points):
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET experience_points = experience_points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()
    conn.close()

# ✅ Fonction pour diminuer les requêtes disponibles
def consume_request(user_id):
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET requests = requests - 1 WHERE user_id = ? AND requests > 0", (user_id,))
    conn.commit()
    conn.close()
