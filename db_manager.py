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

    # ✅ Vérifier si la colonne `device_id` existe déjà
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    if "device_id" not in columns:
        print("⚠️ [WARNING] `device_id` absent. Migration de la base...")

        # ✅ Étape 1 : Créer une nouvelle table avec `device_id`
        cursor.execute('''
            CREATE TABLE users_new (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                password TEXT,
                device_id TEXT UNIQUE,
                experience_points INTEGER DEFAULT 0,
                requests INTEGER DEFAULT 5
            )
        ''')
        
        # ✅ Étape 2 : Copier les anciennes données dans la nouvelle table
        cursor.execute('''
            INSERT INTO users_new (user_id, email, password, experience_points, requests)
            SELECT user_id, email, password, experience_points, requests FROM users
        ''')

        # ✅ Étape 3 : Supprimer l'ancienne table et renommer la nouvelle
        cursor.execute("DROP TABLE users")
        cursor.execute("ALTER TABLE users_new RENAME TO users")

        conn.commit()
        print("✅ [DEBUG] Migration terminée, `device_id` ajouté.")

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
    """Génère un ID unique basé sur l’appareil et le stocke en cookie."""
    cookie_manager = get_cookie_manager()

    # ✅ Vérifier si un `device_id` est déjà stocké dans les cookies
    stored_device_id = cookie_manager.get("device_id")
    if stored_device_id:
        return stored_device_id  # ✅ Réutiliser l'ID existant

    # 🎯 Générer un `device_id` unique basé sur un UUID aléatoire
    device_id = str(uuid.uuid4())

    # ✅ Stocker dans un cookie
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
    cursor.execute("SELECT user_id, password FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode(), user[1]):  # Vérifier le mot de passe
        device_id = generate_device_id()  # Générer un `device_id` unique

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
