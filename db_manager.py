from datetime import datetime
from tinydb import TinyDB, Query
import socket
import os
import json

QUOTAS_FILE = "data/request_logs.json"

MAX_REQUESTS = 10

def load_quotas():
    if os.path.exists(QUOTAS_FILE):
        with open(QUOTAS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_quotas(quotas):
    with open(QUOTAS_FILE, "w") as f:
        json.dump(quotas, f)

def get_user_id():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

def get_requests_left():
    quotas = load_quotas()
    user_id = get_user_id()
    today = datetime.now().strftime("%Y-%m-%d")

    if user_id in quotas and quotas[user_id]["date"] == today:
        requests_made = quotas[user_id]["requests"]
        return max(0, MAX_REQUESTS - requests_made)
    else:
        quotas[user_id] = {"date": today, "requests": 0}
        save_quotas(quotas)
        return MAX_REQUESTS

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
