import sqlite3
from datetime import datetime
import os
import hashlib
import uuid
import platform
import http.cookies as Cookie

DB_FILE = "data/request_logs.db"
TOKEN_FILE = "data/device_token_{}.txt".format(platform.node())
if not os.path.exists("data"):
    os.makedirs("data")

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

conn = get_connection()
cursor = conn.cursor()

# Vérifier si la colonne user_token existe
cursor.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cursor.fetchall()]

if "user_token" not in columns:
    print("🔄 Migration : Création d'une nouvelle table users avec user_token")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_new (
            user_id TEXT PRIMARY KEY,
            user_token TEXT UNIQUE,
            date TEXT,
            requests INTEGER DEFAULT 5,
            experience_points INTEGER DEFAULT 0,
            purchased_requests INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        INSERT INTO users_new (user_id, date, requests, experience_points, purchased_requests)
        SELECT user_id, date, requests, experience_points, purchased_requests FROM users
    ''')
    cursor.execute("DROP TABLE users")
    cursor.execute("ALTER TABLE users_new RENAME TO users")
    conn.commit()
    print("✅ Migration terminée : table users mise à jour avec user_token")
conn.close()

def get_local_token():
    if os.environ.get("HTTP_COOKIE"):
        cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
        if "device_token" in cookie:
            return cookie["device_token"].value
    
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    new_token = str(uuid.uuid4())
    with open(TOKEN_FILE, "w") as f:
        f.write(new_token)
    return new_token

def get_user_id():
    user_token = get_local_token()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_token = ?", (user_token,))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row[0]
    new_user_id = hashlib.sha256(user_token.encode()).hexdigest()
    cursor.execute("INSERT INTO users (user_id, user_token, date, requests, experience_points, purchased_requests) VALUES (?, ?, ?, 5, 0, 0)",
                   (new_user_id, user_token, datetime.now().strftime("%Y-%m-%d")))
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