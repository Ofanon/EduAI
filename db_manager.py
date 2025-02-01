import sqlite3
import os
import hashlib
import socket
import uuid

DB_FILE = "users_data.db"

# Création et connexion à la base de données
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

# Table principale pour stocker les utilisateurs
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        points INTEGER DEFAULT 0,
        requests INTEGER DEFAULT 5
    )
''')
conn.commit()

def generate_user_id():
    """Génère un identifiant unique basé sur l'adresse IP et l'adresse MAC."""
    ip_address = socket.gethostbyname(socket.gethostname())
    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 8)][::-1])
    unique_id = hashlib.sha256(f"{ip_address}_{mac_address}".encode()).hexdigest()
    return unique_id

def get_user_id():
    """Récupère un ID unique en base ou le génère si inexistant."""
    user_id = generate_user_id()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users (user_id, points, requests) VALUES (?, 0, 5)", (user_id,))
        conn.commit()
    return user_id

def update_experience_points(user_id, points):
    """Met à jour les points de l'utilisateur."""
    cursor.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()

def update_requests(user_id, count):
    """Met à jour le nombre de requêtes restantes."""
    cursor.execute("UPDATE users SET requests = requests + ? WHERE user_id = ?", (count, user_id))
    conn.commit()

def get_experience_points(user_id):
    """Récupère les points actuels de l'utilisateur."""
    cursor.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else None

def get_requests_left(user_id):
    """Récupère le nombre de requêtes restantes de l'utilisateur."""
    cursor.execute("SELECT requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else None