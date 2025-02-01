import os
import uuid
import hashlib
import platform
import socket
import json
import streamlit as st
import extra_streamlit_components as stx
from tinydb import TinyDB, Query
from datetime import datetime, timedelta

# 📌 Chemin du fichier de base de données (TinyDB)
DB_FILE = "data/db.json"

# ✅ Charger TinyDB en évitant les erreurs JSON
def load_tinydb():
    """Charge TinyDB et corrige les erreurs JSON si besoin."""
    try:
        return TinyDB(DB_FILE)
    except json.JSONDecodeError:
        print("⚠️ [WARNING] Fichier JSON corrompu. Réinitialisation...")
        os.remove(DB_FILE)  # Supprime le fichier corrompu
        return TinyDB(DB_FILE)  # Recrée un fichier propre

db = load_tinydb()
Users = Query()

# ✅ Gestion d'une seule instance de CookieManager
cookie_manager_instance = None

def get_cookie_manager():
    """Retourne une instance unique de CookieManager pour éviter les doublons."""
    global cookie_manager_instance
    if cookie_manager_instance is None:
        cookie_manager_instance = stx.CookieManager()
    return cookie_manager_instance

def generate_device_id():
    """Génère un ID unique basé sur plusieurs caractéristiques de l’appareil."""
    try:
        private_ip = socket.gethostbyname(socket.gethostname())  # IP locale
        device_name = platform.node()  # Nom de l'appareil
        os_name = platform.system()  # OS (Windows, Linux, Mac, Android, iOS)
        processor = platform.processor()  # Type de processeur

        raw_id = f"{private_ip}_{device_name}_{os_name}_{processor}"
        hashed_id = hashlib.sha256(raw_id.encode()).hexdigest()  # Hash pour anonymisation

        return hashed_id
    except Exception as e:
        print(f"❌ [ERROR] Impossible de générer un device_id : {e}")
        return str(uuid.uuid4())  # En secours, générer un UUID aléatoire

def get_or_create_user_id():
    """Récupère ou génère un `user_id` unique et le stocke en base + cookies."""

    cookie_manager = get_cookie_manager()

    # ✅ Vérifier si un `device_id` est déjà stocké dans les cookies
    device_id = cookie_manager.get("device_id")

    if not device_id:
        device_id = generate_device_id()  # Génère un ID unique
        print(f"🔍 [DEBUG] Génération d'un nouveau device_id : {device_id}")
        cookie_manager.set("device_id", device_id, expires_at=datetime.now() + timedelta(days=365 * 20), key="device_id")

    # ✅ Vérifier si cet appareil existe déjà en base
    user = db.search(Users.device_id == device_id)
    if user:
        user_id = user[0]["user_id"]
    else:
        user_id = str(uuid.uuid4())  # Générer un nouvel ID unique
        db.insert({"user_id": user_id, "device_id": device_id, "requests": 5, "experience_points": 0, "purchased_requests": 0})
        print(f"✅ [DEBUG] Nouvel ID enregistré pour l'appareil : {device_id} → {user_id}")

    # ✅ Stocker l'`user_id` en session et cookie (si pas déjà défini)
    if not cookie_manager.get("user_id"):
        cookie_manager.set("user_id", user_id, expires_at=datetime.now() + timedelta(days=365 * 20), key="user_id")

    st.session_state["user_id"] = user_id
    return user_id

def get_requests_left():
    """Récupère le nombre de requêtes restantes pour l'utilisateur."""
    user_id = get_or_create_user_id()

    user = db.search(Users.user_id == user_id)
    return user[0]["requests"] if user else 5

def consume_request():
    """Diminue le nombre de requêtes disponibles pour l'utilisateur."""
    user_id = get_or_create_user_id()

    user = db.search(Users.user_id == user_id)
    if user and user[0]["requests"] > 0:
        db.update({"requests": user[0]["requests"] - 1}, Users.user_id == user_id)
        return True
    return False
