from datetime import datetime, timedelta
from tinydb import TinyDB, Query
import socket

def get_user_id():
    return socket.gethostbyname(socket.gethostname())

user_id = get_user_id()

db = TinyDB("request_logs.json")
User = Query()
max_requests= 20
def can_user_make_request():

    today = datetime.now().strftime("%Y-%m-%d")
    user_data = db.get((User.user_id == user_id) & (User.date == today))

    if user_data:
        if user_data["requests"] >= max_requests:
            return False
        else:
            
            db.update({"requests": user_data["requests"] + 1}, (User.user_id == user_id) & (User.date == today))
    else:
        db.insert({"user_id": user_id, "date": today, "requests": 1})

    return True, max_requests - 1

def get_user_requests_left():
    today = datetime.now().strftime("%Y-%m-%d")
    user_data = db.get((User.user_id == user_id) & (User.date == today))

    if user_data:
        requests_made = user_data["requests"]
        requests_left = max_requests - requests_made
        return max(0, requests_left)
    else:
        return max_requests
