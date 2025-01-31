import sqlite3
from datetime import datetime
import os
import hashlib
import uuid
import socket

DB_FILE = "data/request_logs.db"
UUID_FILE = "data/device_uuid.txt"
if not os.path.exists("data"):
    os.makedirs("data")

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

# Vérifier si la table users existe, sinon la créer
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
if not cursor.fetchone():
    cursor.execute('''
        CREATE TABLE users (
            user_id TEXT PRIMARY KEY,
            device_uuid TEXT UNIQUE,
            date TEXT,
            requests INTEGER DEFAULT 5,
            experience_points INTEGER DEFAULT 0,
            purchased_requests INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    print("✅ Table users créée avec succès")

conn.execute("VACUUM")
conn.commit()

if os.path.exists(DB_FILE):
    print(f"✅ Base de données créée avec succès : {DB_FILE}")
else:
    print("❌ Erreur : le fichier de base de données n'a pas été créé.")

def get_stored_uuid():
    if os.path.exists(UUID_FILE):
        with open(UUID_FILE, "r") as f:
            return f.read().strip()
    new_uuid = str(uuid.uuid4())
    with open(UUID_FILE, "w") as f:
        f.write(new_uuid)
    return new_uuid

def get_device_uuid():
    return hashlib.sha256(get_stored_uuid().encode()).hexdigest()

def get_user_id():
    device_uuid = get_device_uuid()
    cursor.execute("SELECT user_id FROM users WHERE device_uuid = ?", (device_uuid,))
    row = cursor.fetchone()
    
    if row:
        return row[0]
    
    new_user_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    cursor.execute("INSERT INTO users (user_id, device_uuid, date, requests, experience_points, purchased_requests) VALUES (?, ?, ?, 5, 0, 0)",
                   (new_user_id, device_uuid, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    return new_user_id

def initialize_user():
    get_user_id()

def can_user_make_request():
    user_id = get_user_id()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT date, requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        initialize_user()
        return True

    date_last_request, normal_requests, purchased_requests = row

    if date_last_request != today:
        cursor.execute("UPDATE users SET date = ?, requests = 5 WHERE user_id = ?", (today, user_id))
        conn.commit()
        return True

    return normal_requests > 0 or purchased_requests > 0

def consume_request():
    user_id = get_user_id()
    cursor.execute("SELECT requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        return False

    normal_requests, purchased_requests = row
    if purchased_requests > 0:
        cursor.execute("UPDATE users SET purchased_requests = purchased_requests - 1 WHERE user_id = ?", (user_id,))
    elif normal_requests > 0:
        cursor.execute("UPDATE users SET requests = requests - 1 WHERE user_id = ?", (user_id,))
    else:
        return False

    conn.commit()
    return True

def purchase_requests(cost_in_experience, requests_to_add):
    user_id = get_user_id()
    cursor.execute("SELECT experience_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row and row[0] >= cost_in_experience:
        cursor.execute("UPDATE users SET experience_points = experience_points - ?, purchased_requests = purchased_requests + ? WHERE user_id = ?", (cost_in_experience, requests_to_add, user_id))
        conn.commit()
        return True
    return False

def update_experience_points(points):
    user_id = get_user_id()
    cursor.execute("UPDATE users SET experience_points = experience_points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()

def get_experience_points():
    user_id = get_user_id()
    cursor.execute("SELECT experience_points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

def get_requests_left():
    user_id = get_user_id()
    cursor.execute("SELECT requests, purchased_requests FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] + row[1] if row else 5

initialize_user()
