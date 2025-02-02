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

def save_users(users):
    """ Sauvegarde correctement toutes les données des utilisateurs """
    with open(USERS_FILE, "w") as f:
        yaml.dump(users, f, default_flow_style=False)

def get_current_user():
    """ Récupère l'utilisateur actuellement connecté """
    return st.session_state.get("username", None)

def hash_password(password):
    """ Hash un mot de passe avec SHA-256 """
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_user(email, password):
    """ Initialise un utilisateur avec un mot de passe sécurisé """
    users = load_users()
    username = get_current_user()
    
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

def update_user_data(key, value):
    username= get_current_user()
    users = load_users()

    if username not in users["users"]:
        return False, "❌ Utilisateur introuvable."

    users["users"][username][key] = value  # Mise à jour de la donnée spécifique
    save_users(users)  # Sauvegarde des changements
    return True, f"✅ {key} mis à jour avec succès : {value}."


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
    """ Ajoute directement des points d'expérience à l'utilisateur connecté et enregistre immédiatement dans users.yaml """
    username = get_current_user()
    if not username:
        return False, "❌ Aucun utilisateur connecté."

    users = load_users()

    # Vérifier si l'utilisateur existe
    if username not in users["users"]:
        return False, "❌ Utilisateur introuvable."

    # Vérifier et initialiser "experience_points" si nécessaire
    if "experience_points" not in users["users"][username]:
        users["users"][username]["experience_points"] = 0

    # Ajouter les points d'expérience
    users["users"][username]["experience_points"] += points

    # Sauvegarder immédiatement dans users.yaml
    try:
        with open(USERS_FILE, "w") as f:
            yaml.dump(users, f, default_flow_style=False)

        print(f"DEBUG: XP mis à jour pour {username} -> {users['users'][username]['experience_points']}")
        return True, f"✅ {points} XP ajoutés avec succès et enregistrés !"

    except Exception as e:
        return False, f"❌ Erreur lors de la sauvegarde de users.yaml : {str(e)}"

def test_yaml_write():
    """ Teste si users.yaml peut être modifié """
    try:
        test_data = {"test": "écriture réussie"}
        
        # Test d'écriture
        with open(USERS_FILE, "w") as f:
            yaml.dump(test_data, f, default_flow_style=False)
        
        # Test de lecture
        with open(USERS_FILE, "r") as f:
            read_data = yaml.safe_load(f)

        st.write(f"DEBUG: Test d'écriture réussi, contenu du fichier : {read_data}")
        return True
    except Exception as e:
        st.write(f"❌ Erreur lors du test d'écriture : {str(e)}")
        return False

def get_requests_left():
    username = get_current_user()
    if not username:
        return 0
    users = load_users()
    return users["users"].get(username, {}).get("requests", 0) + users["users"].get(username, {}).get("purchased_requests", 0)

def consume_request():
    """ Décrémente directement le nombre de requêtes de l'utilisateur connecté et enregistre immédiatement dans users.yaml """
    username = get_current_user()
    if not username:
        return False, "❌ Aucun utilisateur connecté."

    users = load_users()

    # Vérifier si l'utilisateur existe
    if username not in users["users"]:
        return False, "❌ Utilisateur introuvable."

    # Vérifier et initialiser "requests" si nécessaire
    if "requests" not in users["users"][username]:
        users["users"][username]["requests"] = 5  # Valeur par défaut

    # Vérifier et initialiser "purchased_requests" si nécessaire
    if "purchased_requests" not in users["users"][username]:
        users["users"][username]["purchased_requests"] = 0

    # Consommer une requête
    if users["users"][username]["purchased_requests"] > 0:
        users["users"][username]["purchased_requests"] -= 1
    elif users["users"][username]["requests"] > 0:
        users["users"][username]["requests"] -= 1
    else:
        return False, "❌ Plus de requêtes disponibles."

    # Sauvegarder immédiatement dans users.yaml
    try:
        with open(USERS_FILE, "w") as f:
            yaml.dump(users, f, default_flow_style=False)

        print(f"DEBUG: Requests mis à jour pour {username} -> {users['users'][username]['requests']}")
        return True, "✅ Requête utilisée avec succès."

    except Exception as e:
        return False, f"❌ Erreur lors de la sauvegarde de users.yaml : {str(e)}"


def can_user_make_request():
    """ Vérifie si l'utilisateur connecté peut encore faire une requête sans triche. """
    username = get_current_user()
    if not username:
        return False, "❌ Aucun utilisateur connecté."

    users = load_users()
    user = users["users"].get(username, {})

    if not user:
        return False, "❌ Utilisateur introuvable."

    today = datetime.now().strftime("%Y-%m-%d")

    if user.get("last_request_date") != today:
        user["last_request_date"] = today
        if user["requests"] < 5:  # Ne pas réinitialiser si l'utilisateur a encore des requêtes restantes
            user["requests"] = max(user["requests"], 5)  # S'assure que ça ne dépasse jamais 5
        save_users(users)

    if user["requests"] > 0 or user["purchased_requests"] > 0:
        return True, "✅ Vous avez encore des requêtes disponibles."
    return False, "❌ Plus de requêtes disponibles. Achetez-en ou attendez demain."

def purchase_requests(cost_in_experience, requests_to_add):
    """ Permet à l'utilisateur connecté d'acheter des requêtes avec ses points d'expérience. """
    username = get_current_user()
    if not username:
        return False, "❌ Aucun utilisateur connecté."

    users = load_users()
    user = users["users"].get(username, {})

    if not user:
        return False, "❌ Utilisateur introuvable."

    if user["experience_points"] >= cost_in_experience:
        user["experience_points"] -= cost_in_experience  # Déduire les points d'expérience
        user["purchased_requests"] += requests_to_add  # Ajouter les requêtes achetées
        users["users"][username] = user  # Mise à jour des données
        save_users(users)  # Sauvegarde correctement l'utilisateur
        return True, f"✅ Achat réussi ! Vous avez {user['purchased_requests']} requêtes achetées."
    else:
        return False, "❌ Points d'expérience insuffisants pour cet achat."
