import json

data_file = "request_logs.json"

def load_user_data():
    try:
        with open(data_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_data(user_ip, experience_points):
    data = load_user_data()
    data[user_ip] = {"experience_points": experience_points}
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)

def get_experience_points(user_ip):
    data = load_user_data()
    return data.get(user_ip, {}).get("experience_points", 0)

def update_experience_points(user_ip, points):
    current_points = get_experience_points(user_ip)
    new_points = current_points + points
    save_user_data(user_ip, new_points)
    return new_points
