import sqlite3
import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import hashlib
import platform
import socket
from datetime import datetime

DB_FILE = "data/request_logs.db"

def get_private_ip():
    """Récupère l'adresse IP locale unique."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except:
        return "127.0.0.1"

def generate_unique_device_id():
    """Génère un identifiant unique basé sur l'appareil."""
    private_ip = get_private_ip()
    device_name = platform.node()
    os_name = platform.system()
    processor = platform.processor()
    return hashlib.sha256(f"{private_ip}_{device_name}_{os_name}_{processor}".encode()).hexdigest()

def get_user_id():
    """Récupère ou génère un ID utilisateur unique et le stocke dans localStorage."""

    # Vérifier si l'ID utilisateur existe déjà dans le localStorage
    user_id = streamlit_js_eval(js_code="localStorage.getItem('user_id')")

    if user_id:
        st.session_state["user_id"] = user_id
        return user_id

    # Si non, générer un nouvel ID
    user_id = generate_unique_device_id()

    # Vérifier si cet ID existe en base
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        cursor.execute("INSERT INTO users (user_id, date, requests, experience_points, purchased_requests) VALUES (?, ?, 5, 0, 0)", (user_id, None))
        conn.commit()

    conn.close()

    # Stocker l'ID dans localStorage
    streamlit_js_eval(js_code=f"localStorage.setItem('user_id', '{user_id}')")

    st.session_state["user_id"] = user_id
    return user_id
