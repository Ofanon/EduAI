import yaml
import os
import hashlib
import streamlit as st
from datetime import datetime

# Charger le chemin du fichier YAML depuis `secrets.toml`
USERS_FILE = st.secrets["DATABASE"]["USERS_FILE"]

# Vérifier si le fichier existe, sinon le créer avec une structure vide
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        yaml.dump({"users": {}}, f)

def load_users():
    """ Charge les utilisateurs depuis le fichier YAML """
    with open(USERS_FILE, "r") as f:
        return yaml.safe_load(f)
    
def save_users(updated_users):
    """ Met à jour uniquement les valeurs nécessaires sans écraser les données existantes """
    existing_users = load_users()  # Charger l'état actuel des utilisateurs

    for username, new_data in updated_users["users"].items():
        if username in existing_users["users"]:
            # Mise à jour des données sans supprimer les valeurs existantes
            existing_users["users"][username].update(new_data)
        else:
            existing_users["users"][username] = new_data  # Ajouter un nouvel utilisateur

    # Sauvegarde des données mises à jour
    with open(USERS_FILE, "w") as f:
        yaml.dump(existing_users, f, default_flow_style=False)

def get_current_user():
    """ Récupère l'utilisateur actuellement connecté """
    return st.session_state.get("username", None)

def hash_password(password):
    """ Hash un mot de passe avec SHA-256 """
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_user(username, email, password):
    """ Initialise un utilisateur avec un mot de passe sécurisé """
    users = load_users()
    
    if username in users["users"]:
        return False, "❌ L'utilisateur existe déjà."

    users["users"][username] = {
        "email": email,
        "password": hash_password(password),
        "experience_points": 0,
        "requests": 5,
        "purchased_requests": 0,
        "last_request_date": None
    }
    save_users(users)
    return True, "✅ Compte créé avec succès !"

def authenticate(username, password):
    """ Vérifie si le nom d'utilisateur et le mot de passe sont corrects """
    users = load_users()
    user = users["users"].get(username)

    if not user:
        return False, "❌ Utilisateur introuvable."

    if user["password"] == hash_password(password):
        return True, "✅ Authentification réussie !"
    else:
        return False, "❌ Mot de passe incorrect."

def get_experience_points():
    """ Récupère les points d'expérience de l'utilisateur connecté """
    username = get_current_user()
    if not username:
        return 0
    users = load_users()
    return users["users"].get(username, {}).get("experience_points", 0)

def update_experience_points(points):
    """ Ajoute des points d'expérience à l'utilisateur connecté et sauvegarde correctement """
    username = get_current_user()
    if not username:
        return False, "❌ Aucun utilisateur connecté."

    users = load_users()
    user = users["users"].get(username)

    if not user:
        return False, "❌ Utilisateur introuvable."

    # Vérifier si la clé "experience_points" existe, sinon l'initialiser à 0
    if "experience_points" not in user:
        user["experience_points"] = 0

    user["experience_points"] += points  # Ajout des points d'expérience
    save_users({"users": {username: user}})  # Sauvegarde uniquement cet utilisateur
    return True, f"✅ {points} XP ajoutés avec succès !"


def get_requests_left():
    """ Récupère le nombre de requêtes restantes de l'utilisateur connecté """
    username = get_current_user()
    if not username:
        return 0
    users = load_users()
    return users["users"].get(username, {}).get("requests", 0) + users["users"].get(username, {}).get("purchased_requests", 0)

def consume_request():
    """ Décrémente le nombre de requêtes de l'utilisateur connecté et sauvegarde correctement """
    username = get_current_user()
    if not username:
        return False, "❌ Aucun utilisateur connecté."

    users = load_users()
    user = users["users"].get(username)

    if not user:
        return False, "❌ Utilisateur introuvable."

    if user["purchased_requests"] > 0:
        user["purchased_requests"] -= 1
    elif user["requests"] > 0:
        user["requests"] -= 1
    else:
        return False, "❌ Plus de requêtes disponibles."

    save_users({"users": {username: user}})  # Sauvegarde correctement l'utilisateur
    return True, "✅ Requête utilisée avec succès."


def can_user_make_request():
    """ Vérifie si l'utilisateur connecté peut encore faire une requête. """
    username = get_current_user()
    if not username:
        return False, "❌ Aucun utilisateur connecté."

    users = load_users()
    user = users["users"].get(username)

    if not user:
        return False, "❌ Utilisateur introuvable."

    today = datetime.now().strftime("%Y-%m-%d")

    # Réinitialiser les requêtes normales si la date a changé
    if user.get("last_request_date") != today:
        user["last_request_date"] = today
        if user["requests"] < 5:  # Ne met à 5 que si inférieur à 5 (évite la triche)
            user["requests"] = max(0, user["requests"])  # Ne jamais repasser à 5 si déjà utilisées
        save_users({"users": {username: user}})

    if user["requests"] > 0 or user["purchased_requests"] > 0:
        return True, "✅ Vous avez encore des requêtes disponibles."
    return False, "❌ Plus de requêtes disponibles. Achetez-en ou attendez demain."

def purchase_requests(cost_in_experience, requests_to_add):
    """ Permet à l'utilisateur connecté d'acheter des requêtes avec ses points d'expérience. """
    username = get_current_user()
    if not username:
        return False, "❌ Aucun utilisateur connecté."

    users = load_users()
    user = users["users"].get(username)

    if not user:
        return False, "❌ Utilisateur introuvable."

    if user["experience_points"] >= cost_in_experience:
        user["experience_points"] -= cost_in_experience  # Déduire les points d'expérience
        user["purchased_requests"] += requests_to_add  # Ajouter les requêtes achetées
        save_users(users)
        return True, f"✅ Achat réussi ! Vous avez {user['purchased_requests']} requêtes achetées."
    else:
        return False, "❌ Points d'expérience insuffisants pour cet achat."
