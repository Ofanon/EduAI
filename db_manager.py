import sqlite3
from datetime import datetime
import os
import hashlib
import uuid

DB_FILE = "data/request_logs.db"
if not os.path.exists("data"):
    os.makedirs("data")


def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


conn = get_connection()
cursor = conn.cursor()

# Vérifier si la table users existe, sinon la créer
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
if not cursor.fetchone():
    cursor.execute('''
        CREATE TABLE users (
            user_id TEXT PRIMARY KEY,
            user_token TEXT UNIQUE,
            date TEXT,
            requests INTEGER DEFAULT 5,
            experience_points INTEGER DEFAULT 0,
            purchased_requests INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    print("✅ Table users créée avec succès")
conn.close()


def generate_user_token():
    return str(uuid.uuid4())


def get_user_id():
    conn = get_connection()
    cursor = conn.cursor()

    # Vérifier si un token utilisateur existe déjà
    cursor.execute("SELECT user_id FROM users WHERE user_token IS NOT NULL LIMIT 1")
    row = cursor.fetchone()
    if row:
        conn.close()
        return row[0]

    # Générer un nouvel identifiant utilisateur et token
    new_user_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    new_token = generate_user_token()
    cursor.execute("INSERT INTO users (user_id, user_token, date, requests, experience_points, purchased_requests) VALUES (?, ?, ?, 5, 0, 0)",
                   (new_user_id, new_token, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()
    return new_user_id


def initialize_user():
    get_user_id()


def can_user_make_request():
    user_id = get_user_id()
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT date, requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        initialize_user()
        conn.close()
        return True

    date_last_request, normal_requests, purchased_requests = row
    if date_last_request != today:
        cursor.execute("UPDATE users SET date = ?, requests = 5 WHERE user_id = ?", (today, user_id))
        conn.commit()
        conn.close()
        return True

    conn.close()
    return normal_requests > 0 or purchased_requests > 0


def consume_request():
    user_id = get_user_id()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    normal_requests, purchased_requests = row
    if purchased_requests > 0:
        cursor.execute("UPDATE users SET purchased_requests = purchased_requests - 1 WHERE user_id = ?", (user_id,))
    elif normal_requests > 0:
        cursor.execute("UPDATE users SET requests = requests - 1 WHERE user_id = ?", (user_id,))
    else:
        conn.close()
        return False

    conn.commit()
    conn.close()
    return True


def purchase_requests(cost_in_experience, requests_to_add):
    user_id = get_user_id()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT experience_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row and row[0] >= cost_in_experience:
        cursor.execute("UPDATE users SET experience_points = experience_points - ?, purchased_requests = purchased_requests + ? WHERE user_id = ?", (cost_in_experience, requests_to_add, user_id))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False


def update_experience_points(points):
    user_id = get_user_id()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET experience_points = experience_points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()
    conn.close()


def get_experience_points():
    user_id = get_user_id()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT experience_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0


def get_requests_left():
    user_id = get_user_id()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] + row[1] if row else 5


initialize_user()