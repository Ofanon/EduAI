import sqlite3
from datetime import datetime
import socket

DB_FILE = "data/request_logs.db"

# Connexion à la base SQLite
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

# Création de la table si elle n'existe pas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        date TEXT,
        requests INTEGER DEFAULT 0,
        experience_points INTEGER DEFAULT 0,
        purchased_requests INTEGER DEFAULT 0
    )
''')
conn.commit()

# Obtenir l'ID utilisateur
hostname = socket.gethostname()
user_id = socket.gethostbyname(hostname)

def initialize_user():
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, date, requests, experience_points, purchased_requests)
        VALUES (?, ?, 0, 0, 0)
    """, (user_id, None))
    conn.commit()

def can_user_make_request():
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT date, requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        initialize_user()
        cursor.execute("SELECT date, requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

    date_last_request, normal_requests, purchased_requests = row

    # Réinitialiser les requêtes si la date a changé
    if date_last_request != today:
        cursor.execute("UPDATE users SET date = ?, requests = 5 WHERE user_id = ?", (today, user_id))
        conn.commit()
        return True

    # Vérifier si des requêtes normales sont disponibles
    if normal_requests > 0:
        return True

    # Vérifier si des requêtes achetées sont disponibles
    if purchased_requests > 0:
        return True

    return False

def consume_request():
    cursor.execute("SELECT requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row[1] > 0:  # Consommer une requête achetée
        cursor.execute("UPDATE users SET purchased_requests = purchased_requests - 1 WHERE user_id = ?", (user_id,))
    elif row[0] > 0:  # Consommer une requête normale
        cursor.execute("UPDATE users SET requests = requests - 1 WHERE user_id = ?", (user_id,))
    else:
        return False

    conn.commit()
    return True

def purchase_requests(cost_in_experience, requests_to_add):
    cursor.execute("SELECT experience_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row and row[0] >= cost_in_experience:  # Vérifier si suffisamment de points d'expérience
        cursor.execute("""
            UPDATE users
            SET experience_points = experience_points - ?, purchased_requests = purchased_requests + ?
            WHERE user_id = ?
        """, (cost_in_experience, requests_to_add, user_id))
        conn.commit()
        return True
    return False

def update_experience_points(points):
    cursor.execute("UPDATE users SET experience_points = experience_points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()

def get_experience_points():
    cursor.execute("SELECT experience_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

initialize_user()
