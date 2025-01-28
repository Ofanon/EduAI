import sqlite3
from datetime import datetime
import socket

DB_FILE = "data/request_logs.db"

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

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

hostname = socket.gethostname()
user_id = socket.gethostbyname(hostname)

def initialize_user():
    cursor.execute("INSERT INTO users (user_id, date, requests, experience_points, purchased_requests) VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_id) DO NOTHING", 
                   (user_id, None, 0, 0, 0))
    conn.commit()

def get_requests_left():
    cursor.execute("SELECT requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        requests_left = max(0, 10 - row[0]) + row[1]
        return requests_left
    return 10

def purchase_requests(cost_in_experience, requests_to_add):
    cursor.execute("SELECT experience_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row and row[0] >= cost_in_experience:
        cursor.execute("UPDATE users SET experience_points = experience_points - ?, purchased_requests = purchased_requests + ? WHERE user_id = ?", 
                       (cost_in_experience, requests_to_add, user_id))
        conn.commit()
        return True
    return False

def can_user_make_request():
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Récupérer les informations actuelles de l'utilisateur
    cursor.execute("SELECT date, requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row:
        last_date, daily_requests, purchased_requests = row

        # Vérifier si c'est un nouveau jour
        if last_date != today:
            # Réinitialiser les requêtes quotidiennes à 5
            cursor.execute(
                "UPDATE users SET date = ?, requests = ?, purchased_requests = ? WHERE user_id = ?",
                (today, 5, purchased_requests, user_id)
            )
            conn.commit()
            return True

        # Consommer une requête achetée si disponible
        if purchased_requests > 0:
            cursor.execute(
                "UPDATE users SET purchased_requests = purchased_requests - 1 WHERE user_id = ?",
                (user_id,)
            )
            conn.commit()
            return True

        # Consommer une requête quotidienne si disponible
        if daily_requests > 0:
            cursor.execute(
                "UPDATE users SET requests = requests - 1 WHERE user_id = ?",
                (user_id,)
            )
            conn.commit()
            return True

        # Pas de requêtes disponibles
        return False

    # Si l'utilisateur n'existe pas, l'initialiser
    cursor.execute(
        "INSERT INTO users (user_id, date, requests, purchased_requests) VALUES (?, ?, ?, ?)",
        (user_id, today, 5, 0)
    )
    conn.commit()
    return True

def get_experience_points():
    cursor.execute("SELECT experience_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

def update_experience_points(points):
    cursor.execute("UPDATE users SET experience_points = experience_points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()
    return get_experience_points()

initialize_user()
