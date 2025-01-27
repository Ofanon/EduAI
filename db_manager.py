from datetime import datetime, timedelta
from tinydb import TinyDB, Query
import socket

def get_user_id():
    return socket.gethostbyname(socket.gethostname())

user_id = get_user_id()

db = TinyDB("request_logs.json")
User = Query()

def can_user_make_request(max_requests=10):

    today = datetime.now().strftime("%Y-%m-%d")
    user_data = db.get((User.user_id == user_id) & (User.date == today))

    if user_data:
        if user_data["requests"] >= max_requests:
            return False
        else:
            
            db.update({"requests": user_data["requests"] + 1}, (User.user_id == user_id) & (User.date == today))
    else:
        db.insert({"user_id": user_id, "date": today, "requests": 1})

    return True
