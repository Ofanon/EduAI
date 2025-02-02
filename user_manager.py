import yaml
import hashlib
import os
import streamlit as st  # Pour accéder à la session utilisateur

USERS_FILE = "users.yaml"

# Charger les utilisateurs
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    return {}

# Sauvegarder les utilisateurs
def save_users(users):
    with open(USERS_FILE, "w") as f:
        yaml.dump(users, f, default_flow_style=False)

# Hachage du mot de passe
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Récupérer l'utilisateur connecté
def get_current_user():
    return st.session_state.get("username")

# Création d'un utilisateur
def register_user(username, password, email):
    users = load_users()
    if username in users:
        return False, "L'utilisateur existe déjà."

    users[username] = {
        "password": hash_password(password),
        "email": email,
        "requests": 5,
        "purchase_requests": 0,
        "experience_points": 0
    }
    save_users(users)
    return True, "Compte créé avec succès !"

# Authentification
def authenticate(username, password):
    users = load_users()
    if username in users and users[username]["password"] == hash_password(password):
        st.session_state["username"] = username  # Stocke l'utilisateur en session
        return True, users[username]
    return False, None

# Vérifier si l'utilisateur peut faire une requête
def can_user_make_request():
    username = get_current_user()
    if not username:
        return False, "Utilisateur non connecté."

    users = load_users()
    user = users.get(username, {})

    if user.get("requests", 0) > 0:
        return True, "Requête autorisée (quota normal)."
    elif user.get("purchase_requests", 0) > 0:
        return True, "Requête autorisée (requêtes achetées)."
    else:
        return False, "Quota épuisé. Achetez des requêtes ou attendez demain."

# Consommer une requête
def consume_request():
    username = get_current_user()
    if not username:
        return False, "Utilisateur non connecté."

    users = load_users()
    user = users.get(username, {})

    if user.get("requests", 0) > 0:
        user["requests"] -= 1
    elif user.get("purchase_requests", 0) > 0:
        user["purchase_requests"] -= 1
    else:
        return False, "Pas de requêtes disponibles."

    save_users(users)
    return True, "Requête consommée avec succès."

# Acheter des requêtes avec XP
def purchase_requests(cost_in_experience, requests_to_add):
    username = get_current_user()
    if not username:
        return False, "Utilisateur non connecté."

    users = load_users()
    user = users.get(username, {})

    if user.get("experience_points", 0) >= cost_in_experience:
        user["experience_points"] -= cost_in_experience
        user["purchase_requests"] += requests_to_add
        save_users(users)
        return True, f"{requests_to_add} requêtes achetées avec succès !"
    else:
        return False, "Pas assez de points d'expérience."

# Ajouter des points d'expérience
def update_experience_points(points):
    username = get_current_user()
    if not username:
        return False, "Utilisateur non connecté."

    users = load_users()
    users[username]["experience_points"] += points
    save_users(users)
    return True, f"{points} points d'expérience ajoutés."

# Obtenir les points d'expérience
def get_experience_points():
    username = get_current_user()
    if not username:
        return 0  # Retourne 0 si aucun utilisateur connecté

    users = load_users()
    return users.get(username, {}).get("experience_points", 0)

# Obtenir le nombre de requêtes restantes
def get_requests_left():
    username = get_current_user()
    if not username:
        return 0, 0  # Retourne 0 si aucun utilisateur connecté

    users = load_users()
    user = users.get(username, {})
    return user.get("requests", 0), user.get("purchase_requests", 0)
