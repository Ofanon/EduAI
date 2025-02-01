import os
import uuid
import hashlib
import platform
import socket
import streamlit as st
import extra_streamlit_components as stx
from tinydb import TinyDB, Query
from datetime import datetime, timedelta

# ✅ Sélectionner le type de base (options : "tinydb", "mysql", "postgresql")
DB_TYPE = "tinydb"

# 📌 Configuration des bases de données (TinyDB / MySQL / PostgreSQL)
if DB_TYPE == "tinydb":
    DB_FILE = "data/db.json"
    db = TinyDB(DB_FILE)

elif DB_TYPE == "mysql":
    import mysql.connector
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="eduai"
    )
    cursor = db.cursor()

elif DB_TYPE == "postgresql":
    import psycopg2
    db = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="password",
        database="eduai"
    )
    cursor = db.cursor()

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
        os_name = platform.system()  # OS (Windows, Mac, Linux, Android, iOS)
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

    # ✅ Récupérer ou créer l'utilisateur en fonction du type de base
    if DB_TYPE == "tinydb":
        Users = Query()
        user = db.search(Users.device_id == device_id)
        if user:
            user_id = user[0]["user_id"]
        else:
            user_id = str(uuid.uuid4())
            db.insert({"user_id": user_id, "device_id": device_id, "requests": 5, "experience_points": 0, "purchased_requests": 0})
            print(f"✅ [DEBUG] Nouvel ID enregistré pour l'appareil : {device_id} → {user_id}")

    elif DB_TYPE in ["mysql", "postgresql"]:
        cursor.execute("SELECT user_id FROM users WHERE device_id = %s", (device_id,))
        row = cursor.fetchone()
        if row:
            user_id = row[0]
        else:
            user_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO users (user_id, device_id, requests, experience_points, purchased_requests) VALUES (%s, %s, 5, 0, 0)", 
                           (user_id, device_id))
            db.commit()
            print(f"✅ [DEBUG] Nouvel ID enregistré en SQL pour : {device_id} → {user_id}")

    # ✅ Stocker l'`user_id` en session et cookie (si pas déjà défini)
    if not cookie_manager.get("user_id"):
        cookie_manager.set("user_id", user_id, expires_at=datetime.now() + timedelta(days=365 * 20), key="user_id")

    st.session_state["user_id"] = user_id
    return user_id

def get_requests_left():
    """Récupère le nombre de requêtes restantes pour l'utilisateur."""
    user_id = get_or_create_user_id()

    if DB_TYPE == "tinydb":
        Users = Query()
        user = db.search(Users.user_id == user_id)
        return user[0]["requests"] if user else 5

    elif DB_TYPE in ["mysql", "postgresql"]:
        cursor.execute("SELECT requests FROM users WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        return row[0] if row else 5

def consume_request():
    """Diminue le nombre de requêtes disponibles pour l'utilisateur."""
    user_id = get_or_create_user_id()

    if DB_TYPE == "tinydb":
        Users = Query()
        user = db.search(Users.user_id == user_id)
        if user and user[0]["requests"] > 0:
            db.update({"requests": user[0]["requests"] - 1}, Users.user_id == user_id)
            return True
        return False

    elif DB_TYPE in ["mysql", "postgresql"]:
        cursor.execute("UPDATE users SET requests = requests - 1 WHERE user_id = %s AND requests > 0", (user_id,))
        db.commit()
        return cursor.rowcount > 0
