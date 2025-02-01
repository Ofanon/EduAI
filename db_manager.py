import os
import json
import hashlib
import streamlit as st
from datetime import datetime
import platform
import socket

DATA_DIR = "data"
USER_DATA_FILE = os.path.join(DATA_DIR, "users.json")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "w") as f:
        json.dump({}, f, indent=4)

def load_users():
    """Charge les utilisateurs depuis le fichier JSON."""
    try:
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users):
    """Sauvegarde les utilisateurs dans le fichier JSON."""
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

def get_private_ip():
    """Récupère l'adresse IP privée réelle de l'appareil."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception:
        return "127.0.0.1"

def generate_unique_device_id():
    """Génère un ID unique basé sur l’appareil."""
    private_ip = get_private_ip()
    device_name = platform.node()
    os_name = platform.system()
    processor = platform.processor()
    unique_id = hashlib.sha256(f"{private_ip}_{device_name}_{os_name}_{processor}".encode()).hexdigest()
    return unique_id

def get_user_id():
    """Récupère ou génère un identifiant utilisateur unique."""
    if "user_id" in st.session_state:
        return st.session_state["user_id"]
    
    user_id = generate_unique_device_id()
    users = load_users()
    
    if user_id not in users:
        users[user_id] = {
            "date": None,
            "requests": 5,
            "experience_points": 0,
            "purchased_requests": 0
        }
        save_users(users)
    
    st.session_state["user_id"] = user_id
    return user_id

def can_user_make_request():
    """Vérifie si l'utilisateur peut encore faire des requêtes aujourd'hui."""
    user_id = get_user_id()
    users = load_users()
    today = datetime.now().strftime("%Y-%m-%d")
    
    user_data = users.get(user_id, {})
    if user_data.get("date") != today:
        user_data["date"] = today
        user_data["requests"] = 5
        save_users(users)
        return True
    
    return user_data["requests"] > 0 or user_data["purchased_requests"] > 0

def consume_request():
    """Décrémente le nombre de requêtes disponibles pour l'utilisateur."""
    user_id = get_user_id()
    users = load_users()
    user_data = users.get(user_id, {})
    
    if user_data.get("purchased_requests", 0) > 0:
        user_data["purchased_requests"] -= 1
    elif user_data.get("requests", 0) > 0:
        user_data["requests"] -= 1
    else:
        return False
    
    save_users(users)
    return True

def purchase_requests(cost_in_experience, requests_to_add):
    """Ajoute des requêtes à l'utilisateur en échange de points d'expérience."""
    user_id = get_user_id()
    users = load_users()
    user_data = users.get(user_id, {})
    
    if user_data.get("experience_points", 0) >= cost_in_experience:
        user_data["experience_points"] -= cost_in_experience
        user_data["purchased_requests"] += requests_to_add
        save_users(users)
        return True
    return False

def update_experience_points(points):
    """Ajoute des points d'expérience à l'utilisateur."""
    user_id = get_user_id()
    users = load_users()
    users[user_id]["experience_points"] += points
    save_users(users)

def get_experience_points():
    """Retourne le nombre de points d'expérience de l'utilisateur."""
    user_id = get_user_id()
    users = load_users()
    return users[user_id].get("experience_points", 0)

def get_requests_left():
    """Retourne le nombre de requêtes restantes pour l'utilisateur."""
    user_id = get_user_id()
    users = load_users()
    user_data = users.get(user_id, {})
    return user_data.get("requests", 0) + user_data.get("purchased_requests", 0)

# Initialisation
get_user_id()