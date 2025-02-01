import os
import uuid
import bcrypt
import streamlit as st
import extra_streamlit_components as stx
from tinydb import TinyDB, Query

# 📌 Base de données TinyDB (stockée en JSON)
DB_FILE = "data/users.json"
db = TinyDB(DB_FILE)
Users = Query()

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

    # ✅ Stocker dans un cookie
    cookie_manager.set("device_id", device_id)

    return device_id

# ✅ Fonction d'inscription
def register_user(email, password):
    """Enregistre un nouvel utilisateur avec un `user_id` unique."""
    if db.search(Users.email == email):
        return False  # Utilisateur déjà existant

    # Hacher le mot de passe
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # Générer un `user_id` unique
    user_id = str(uuid.uuid4())

    # Associer un `device_id` unique
    device_id = generate_device_id()

    # Insérer l'utilisateur dans la base
    db.insert({
        "user_id": user_id,
        "email": email,
        "password": hashed_password.decode(),
        "device_id": device_id,
        "experience_points": 0,
        "requests": 5
    })

    return True  # Inscription réussie

# ✅ Fonction de connexion
def login_user(email, password):
    """Connecte un utilisateur en vérifiant son `device_id`."""
    user = db.search(Users.email == email)

    if user and bcrypt.checkpw(password.encode(), user[0]["password"].encode()):  # Vérifier le mot de passe
        device_id = generate_device_id()  # Générer un `device_id` unique

        # ✅ Vérifier si l'appareil correspond à celui enregistré
        if user[0]["device_id"] and user[0]["device_id"] != device_id:
            return None  # Refuser la connexion si l’appareil ne correspond pas

        # ✅ Mettre à jour l'appareil associé à l'utilisateur
        db.update({"device_id": device_id}, Users.email == email)
        return user[0]["user_id"]  # Retourner l'`user_id`

    return None  # Connexion échouée

# ✅ Fonction pour récupérer les infos utilisateur
def get_user_info(user_id):
    """Récupère les informations d'un utilisateur."""
    user = db.search(Users.user_id == user_id)
    return user[0] if user else None
