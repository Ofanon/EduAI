from datetime import datetime
import socket
import os
import json

QUOTAS_FILE = "data/request_logs.json"

MAX_REQUESTS = 10

def get_user_requests():
    MAX_REQUESTS = (QUOTAS_FILE)

def load_quotas():
    if os.path.exists(QUOTAS_FILE):
        with open(QUOTAS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_quotas(quotas):
    with open(QUOTAS_FILE, "w") as f:
        json.dump(quotas, f, indent=4)

def get_user_id():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip
user_id = get_user_id()

def initialize_user():
    quotas = load_quotas()
    if user_id not in quotas:
        quotas[user_id] = {
            "date": None,
            "requests": 0,
            "experience_points": 0
        }
    save_quotas(quotas)

def get_requests_left():
    quotas = load_quotas()
    today = datetime.now().strftime("%Y-%m-%d")
    if user_id in quotas:
        user_data = quotas[user_id]
        requests_left = MAX_REQUESTS - user_data.get("requests", 0)
        purchased_requests = user_data.get("purchased_requests", 0)
        return max(0, requests_left) + purchased_requests
    return MAX_REQUESTS


def purchase_requests(cost_in_experience, requests_to_add):
    quotas = load_quotas()
    if user_id in quotas:
        user_data = quotas[user_id]
        current_experience = user_data.get("experience_points", 0)

        if current_experience >= cost_in_experience:
            user_data["experience_points"] -= cost_in_experience
            user_data["purchased_requests"] = user_data.get("purchased_requests", 0) + requests_to_add
            save_quotas(quotas)
            return True
        else:
            return False


def can_user_make_request():
    quotas = load_quotas()
    user_id = get_user_id()
    today = datetime.now().strftime("%Y-%m-%d")

    if user_id in quotas and quotas[user_id]["date"] == today:
        if quotas[user_id]["requests"] >= MAX_REQUESTS:
            return False
        else:
            quotas[user_id]["requests"] += 1
            save_quotas(quotas)
            return True
    else:
        quotas[user_id] = {"date": today, "requests": 1}
        save_quotas(quotas)
        return True

def get_experience_points():
    quotas = load_quotas()
    return quotas.get(user_id, {}).get("experience_points", 0)

def update_experience_points(points):
    quotas = load_quotas()
    if user_id in quotas:
        quotas[user_id]["experience_points"] = quotas[user_id].get("experience_points", 0) + points
        save_quotas(quotas)
        return quotas[user_id]["experience_points"]
    else:
        raise ValueError("Utilisateur non trouvé.")

